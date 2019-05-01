#  StateMod_TS - class to read/write StateMod format time series

# NoticeStart
#
# CDSS Models Java Library
# CDSS Models Java Library is a part of Colorado's Decision Support Systems (CDSS)
# Copyright (C) 1994-2019 Colorado Department of Natural Resources
#
# CDSS Models Java Library is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     CDSS Models Java Library is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with CDSS Models Java Library.  If not, see <https://www.gnu.org/licenses/>.
#
# NoticeEnd

# ----------------------------------------------------------------------------
# StateMod_TS - class to read/write StateMod format time series
# ----------------------------------------------------------------------------
# History:
#
# 28 Nov 2000	Steven A. Malers, RTi	Copy and modify DateValueTS to include
#					getSample().  This class will eventually
#					combine the StateModMonthTS and
#					StateModDayTS code, as time allows.
# 28 Feb 2001	SAM, RTi		Add getFileInterval() to help
#					automatically determine whether data
#					are monthly or daily format.
# 2003-06-19	SAM, RTi		* Rename class from StateModTS to
#					  StateMod_TS and start to include code
#					  from legacy StateModMonthTS and
#					  StateModDayTS classes.
#					* Update to use new TS package (e.g.,
#					  use DateTime instead of TSDate and
#					  TimeInterval instead of TSInterval).
# 2003-07-08	SAM, RTI		Rename write methods from
#					writePersistent*() to
#					writeTimeSeries*().
# 2003-08-22	SAM, RTI		Enable daily time series read in
#					readTimeSeriesList().
# 2003-09-03	SAM, RTI		Fix a bug reading daily data.
# 2003-10-09	SAM, RTI		Fix a bug reading data other than
#					calendar year - the year was not
#					getting set correctly in the read.
# 2003-11-04	SAM, RTi		Add readTimeSeries() to take a TSID
#					and file name, to read a requested
#					time series.
# 2003-12-11	SAM, RTi		Add readPatternTimeSeriesList() -
#					from the old StateModMonthTS.
#					readPatternFile().
# 2004-01-15	SAM, RTi		* Remove revisits that were limiting
#					  previous functionality (precision
#					  formatting, calendar type).
#					* Change writeTimeSeriesList(,PropList)
#					  to return void.
# 2004-01-31	SAM, RTi		* Enable writing of daily files.
#					  Similar to readTimeSeries() both
#					  daily and monthly format is supported
#					  in writeTimeSeries().
#					* Optimize the writeTimeSeries() code
#					  some - remove extra loops and checks,
#					  and add a boolean array to help avoid
#					  repeated checks for null or bad time
#					  series.
# 2005-05-06	SAM, RTi		* Add writePatternTimeSeriesList().
#					  Copy and modify writeTimeSeriesList to
#					  implement.  Some additional features
#					  may be enabled later.
#					* Clean up some of the old messages that
#					  were still using "writePersistent".
# 2005-09-09	SAM, RTi		* Allow comments in the data part of
#					  monthly and daily files.
# 2006-01-23	SAM, RTi		* Fix bug where monthly average time
#					  series were not being read in properly
#					  for water year.
# 2007-03-01	SAM, RTi		Clean up code based on Eclipse feedback.
# 2007-04-10	SAM, RTi		Change default prevision from 2 to -2 as per
#						writeStateMod() command docs - this is a better default.
# ----------------------------------------------------------------------------
# EndHeader

import logging
import os
import time

from RTi.TS.DayTS import DayTS
from RTi.TS.MonthTS import MonthTS
from RTi.TS.TSIdent import TSIdent
from RTi.TS.TSUtil import TSUtil
from RTi.Util.IO.IOUtil import IOUtil
from RTi.Util.String.StringUtil import StringUtil
from RTi.Util.Time.DateTime import DateTime
from RTi.Util.Time.StopWatch import StopWatch
from RTi.Util.Time.TimeInterval import TimeInterval
from RTi.Util.Time.TimeUtil import TimeUtil
from RTi.Util.Time.YearType import YearType


class StateMod_TS(object):
    """
    The StateMod_TS class provides static input/output methods and general utilities
    for StateMod time series.  Methods are provided to read/write from daily and
    monthly StateMod time series.  This class replaces the legacy StateModMonthTS
    and StateModDayTS classes.  This class will ideally contain all StateMod time
    series related code.  However, this may not be possible - design decisions will
    be made as code is incorporated into this class.
    """

    # Use the following to specify that precision of output should be determined from the units file.
    PRECISION_USE_UNITS = 1000000

    # If the precision is divided by 1000, use the following to indicate from the
    # remainder special actions that should be taken for the precision.  For example,
    # specifying a -2001 precision is equivalent to -2 with NO decimal point for
    # large numbers.  THESE ARE BIT MASK VALUES!!!
    PRECISION_NO_DECIMAL_FOR_LARGE = 1

    # Offset used to shift requested precisions for special requests...
    PRECISION_SPECIAL_OFFSET = 1000

    # Default precision for output.
    PRECISION_DEFAULT = -2

    # Comment character for permanent comments
    PERMANENT_COMMENT = "#"

    # Comment character for non-permanent comments.
    NONPERMANENT_COMMENT = "#>"

    def __init__(self):
        pass

    @staticmethod
    def getFileDataInterval(filename):
        """
        Determine whether a StateMod file is daily or monthly format.  This is done
        by reading through the file until the first line of data.  If that line has
        more than 150 characters, it is assumed to be a daily file; otherwise it is assumed
        to be a monthly file.  Currently, this method does NOT verify that the file
        contents are actually for StateMod.
        The IOUtil.getPathUsingWorkingDir() method is applied to the filename.
        :param filename: Name of file to examine.
        :return: TimeInterval.DAY, TimeInterval.MONTH or -999
        """
        logger = logging.getLogger("StateMod")
        message = None
        routine = "StateMod_TS.getFileDataInterval"
        iline = None
        intervalUnknown = -999  # Return if can't figure out interval
        interval = intervalUnknown
        full_filename = IOUtil.getPathUsingWorkingDir(filename)
        try:
            f = open(full_filename)
        except Exception as e:
            msg = "Unable to open file \"{}\" to determine data interval.".format(full_filename)
            logger.warning(msg)
            return intervalUnknown
        try:
            if filename.upper().endswith("XOP"):
                # The *.xop file will have "Time Step: Monthly"
                with open(full_filename) as f:
                    for iline in f:
                        if iline is None:
                            break
                        if (iline.startswith("#")) and (iline.upper().index("TIME STEP:") > 0):
                            parts = iline.split(":")
                            if len(parts) > 1:
                                if parts[1].strip().upper() == "MONTHLY":
                                    interval = TimeInterval.MONTH
                                    break
                                elif parts[1].strip().upper() == "DAILY":
                                    interval = TimeInterval.DAY
                                    break
            else:
                with open(full_filename) as f:
                    lines = f.readlines()
                    # Read while a comment or blank line...
                    i = -1
                    while True:
                        i += 1
                        iline = lines[i]
                        if iline is None:
                            logger.warning("end of file")
                        iline = iline.strip()
                        if (len(iline) != 0) and (iline[0] != "#"):
                            break  # iline should be the header line
                    # Now should have the header. Read one more to get to a data line...
                    i += 1
                    iline = lines[i]
                    if iline is None:
                        logger.warning("end of file")
                    # Should be first data line. If no longer than the threshold, assume daily.
                    # Trim because some fixed-format write tools put extra spaces at the end.
                    if len(iline.strip()) > 150:
                        interval = TimeInterval.DAY
                    else:
                        interval = TimeInterval.MONTH
        except Exception as e:
            # Could not determine file interval
            return intervalUnknown
        return interval

    @staticmethod
    def readTimeSeriesList(fname, date1, date2, units, read_data):
        """
        Read all the time series from a StateMod format file.
        The IOUtil.getPathUsingWorkingDir() method is applied to the filename.
        :param fname: Name of file to read.
        :param date1: Starting date to initialize period (NULL to read the entire time series).
        :param date2: Ending date to initialize period (NULL to read the entire time series).
        :param units: Units to convert to.
        :param read_data: Indicates whether data should be read.
        :return: a pointer to a newly-allocated Vector of time series if successful, a NULL pointer
        if not.
        """
        logger = logging.getLogger("StateMod")
        tslist = None
        routine = "StateMod_TS.readTimeSeriesList"

        input_name = fname
        full_fname = IOUtil.getPathUsingWorkingDir(fname)
        data_interval = 0
        if( not os.path.isfile(full_fname)):
            logger.warning("File does not exist: \"{}\"".format(full_fname))
        try:
            data_interval = StateMod_TS.getFileDataInterval(full_fname)
            with open(full_fname) as f:
                tslist = StateMod_TS.readTimeSeriesList2(None, f, full_fname, data_interval,
                                                        date1, date2, units, read_data)
            nts = int()
            if tslist is not None:
                nts = len(tslist)
            for i in range(nts):
                ts = tslist[i]
                if ts is not None:
                    ts.setInputName(full_fname)
                    ts.getIdentifier().setInputName(input_name)
        except Exception as e:
            logger.warning("Could not read file: \"{]\"".format(full_fname))
        return tslist

    @staticmethod
    def readTimeSeriesList2(req_ts, f, fullFilename, fileInterval, reqDate1, reqDate2, reqUnits, readData):
        """
        Read one or more time series from a StateMod format file.
        :param req_ts: Pointer to time series to fill. If null, return all new time series
        in the list. All data are reset, except for the identifier, which is assumed to have
        been set in the calling code.
        :param f: reference to open filestream
        :param fullFilename: Full path to filename, used for messages.
        :param fileInterval: Indicates the file type (TimeInterval.DAY or TimeInterval.MONTH).
        :param reqDate1: Requested starting date to initialize period (or NULL to read the entire
        time series).
        :param reqDate2: Requested ending date to initialize period (or NULL to read the entire time series).
        :param reqUnits: Units to convert to (currently ignored).
        :param readData: Indicates whether data should be read.
        :return: a list of time series if successful, null if not. The calling code is responsible
        for freeing the memory for the time series.
        """
        #start = time.time()
        logger = logging.getLogger("StateMod")
        dl = 40
        i = int()
        line_count = 0
        m1 = int()
        m2 = int()
        y1 = int()
        y2 = int()
        currentTSindex = int()
        current_month = 1
        current_year = 0
        doffset = 2
        init_month = 1
        init_year = int()
        ndata_per_line = 12
        numts = 0

        chval = str()
        iline = ""
        routine = "StateMod_TS.readTimeSeriesList"

        v = []
        date = None
        if fullFilename.upper().endswith("XOP"):
            # XOP file is similar to the normal time series format but has some difference
            # in that the header is different, station identifier is provided in the header, and
            # time series are listed vertically one after another, not interwoven by interval like
            # *.stm
            return StateMod_TS.readXTimeSeriesList(req_ts, f, fullFilename, fileInterval,
                                                   reqDate1, reqDate2, reqUnits, readData)
        fileIntervalString = ""
        if fileInterval == TimeInterval.DAY:
            date = DateTime(DateTime.PRECISION_DAY)
            doffset = 3  # Used when setting data to skip the leading fields on the data line
            fileIntervalString = "Day"
        elif fileInterval == TimeInterval.MONTH:
            date = DateTime(DateTime.PRECISION_MONTH)
            fileIntervalString = "Month"
        else:
            logger.warning("Requested file interval is invalid.")

        req_id_found = False  # Indicates if we have found the requested TS in the file.
        standard_ts = True  # Non-standard indicates 12 monthly averages in file.

        tslist = None  # List of time series to return.
        req_id = None
        if req_ts is not None:
            req_id = req_ts.getLocation()
        # Declare here so are visible in final catch to provide feedback for bad format files
        date1_header = None
        date2_header = None
        units = ""
        yearType = YearType.YearType_CALENDAR()
        try:  # General error handler
            # Read first line of the file
            line_count += 1
            i = -1
            lines = f.readlines()
            while i < len(lines) - 1:
                i += 1
                iline = lines[i]
                if iline == None:
                    logger.warning("Zero length file.")
                    return None
                if len(iline.strip()) < 1:
                    logger.warning("Zero length file.")
                    return None

                # Read lines until no more comments are found. The last line read will
                # need to be processed as the main header line...

                while iline.startswith("#"):
                    line_count += 1
                    i += 1
                    iline = lines[i]

                # Process the main header line...
                # It looks like some of the replace() files for demandts have the
                # header line malformatted.  Rather than change all the files, check
                # for a '/' in the [3] position and adjust the format.  Print a warning at level 1.

                format_fileContents = None
                if iline[3] == '/':
                    logger.warning("Non-standard header for file \"" + fullFilename + "\" allowing with work-around.")
                    format_fileContents = "i3x1i4x5i5x1i4s5s5"
                else:
                    # Probably formatted correctly...
                    format_fileContents = "i5x1i4x5i5x1i4s5s5"

                v = StringUtil.fixedRead1(iline, format_fileContents)

                m1 = int(v[0])
                y1 = int(v[1])
                m2 = int(v[2])
                y2 = int(v[3])
                if fileInterval == TimeInterval.DAY:
                    date1_header = DateTime(DateTime.PRECISION_DAY)
                    date1_header.setYear(y1)
                    date1_header.setMonth(m1)
                    date1_header.setDay(1)
                else:
                    date1_header = DateTime(DateTime.PRECISION_MONTH)
                    date1_header.setYear(y1)
                    date1_header.setMonth(m1)
                if fileInterval == TimeInterval.DAY:
                    date2_header = DateTime(DateTime.PRECISION_DAY)
                    date2_header.setYear(y2)
                    date2_header.setMonth(m2)
                    date2_header.setDay(TimeUtil.numDaysInMonth(m2,y2))
                else:
                    date2_header = DateTime(DateTime.PRECISION_MONTH)
                    date2_header.setYear(y2)
                    date2_header.setMonth(m2)
                units = v[4].strip()
                yeartypes = v[5].strip()
                # Year type is used in one place to initialize the year when
                # transferring data. However, it is assumed that m1 is always correct for the year type.
                if yeartypes.upper() == "WYR":
                    yeartype = YearType.YearType_WATER()
                if yeartypes.upper() == "IYR":
                    yeartype = YearType.YearType_NOV_TO_OCT()
                # year that are specified are used to set the period.

                format = []
                format_w = []
                if fileInterval == TimeInterval.DAY:
                    format = [int()]*35
                    format_w = [int()]*35
                    format[0] = StringUtil.TYPE_INTEGER
                    format[1] = StringUtil.TYPE_INTEGER
                    format[2] = StringUtil.TYPE_SPACE
                    format[3] = StringUtil.TYPE_STRING
                    # TODO @jurentie 04/26/2019 - the following might need tested
                    iFormat = 4
                    for j in range(30):
                        format[iFormat] = StringUtil.TYPE_DOUBLE
                        iFormat += 1
                    format_w[0] = 4
                    format_w[1] = 4
                    format_w[2] = 1
                    format_w[3] = 12
                    iFormat = 4
                    for j in range(30):
                        format_w[iFormat] = 8
                        iFormat += 1
                else:
                    format = [int()] * 14
                    format[0] = StringUtil.TYPE_INTEGER
                    format[1] = StringUtil.TYPE_STRING
                    iFormat = 2
                    for j in range(12):
                        format[iFormat] = StringUtil.TYPE_DOUBLE
                        iFormat += 1
                    format_w = [int()] * 14
                    format_w[0] = 5
                    format_w[1] = 12
                    iFormat = 2
                    for j in range(12):
                        format_w[iFormat] = 8
                        iFormat += 1
                if y1 == 0:
                    # average monthly series
                    standard_ts = False
                    format[0] = StringUtil.TYPE_STRING  # Year not used
                    current_year = 0  # STart year will be calendar year 0
                    init_year = 0
                    if m2 < m1:
                        y2 = 1  # End year is calendar year 1
                else:
                    # Standard time series, includes a year on input lines
                    current_year = y1
                    if fileInterval == TimeInterval.MONTH and (m2 < m1):
                        # Monthly data and not calendar year - the first year
                        # shown in the data will be water or irrigation year
                        # and will not match the calendar dates shown in the header...
                        init_year = y1 + 1
                    else:
                        init_year = y1
                current_month = m1
                init_month = m1

                # Read remaining data lines. If in the first year, allocate memory
                # for each time series as a new station is encountered.
                currentTSindex = 0
                currentTS = None  # used to fill data
                ts = None  # used to fill data
                id = None  # Identifier for a row

                # Sometimes the time series files have empty lines at the bottom
                # checking it's length seemed to solve the problem.
                second_iline = None
                single_ts = False  # Indicates whether a single time series is in the file.
                have_second_line = False
                data_line_count = 0
                while True:
                    if data_line_count == 0:
                        i += 1
                        iline = lines[i]
                        if iline == None:
                            break
                        elif iline.startswith("#"):
                            # Comment line. Count the line but do not treat as data...
                            line_count += 1
                            continue
                        # To allow for the case where only one time series is in
                        # the file and a req_id is specified that may be different
                        # (but always return the file contents), read the second line...
                        i += 1
                        second_iline = lines[i]
                        have_second_line = True
                        if second_iline is not None:
                            # Check to see if the year from the first line is different
                            # from the second line, and the identifiers are the same.
                            # If so, assume one time series in the file...
                            if iline[0:5].strip() == "":
                                line1_year = 0
                            else:
                                line1_year = int(iline[0:5].strip())
                            if second_iline[0:5].strip() == "":
                                line2_year = 0
                            else:
                                line2_year = int(second_iline[0:5].strip())
                            if iline[5:17].strip() == "":
                                line1_id = 0
                            else:
                                line1_id = iline[5:17].strip()
                            if second_iline[5:17].strip == "":
                                line2_id = 0
                            else:
                                line2_id = second_iline[5:17].strip()
                            if (line1_id == line2_id) and (line1_year != line2_year):
                                single_ts = True
                                logger.info("Single TS detected - reading all.")
                                if (req_id is not None) and (line1_id.upper() != req_id):
                                    logger.info("reading StateMod file, the requested ID is \"" +
                                                req_id + "\" but the file contains only \"" +
                                                line1_id + "\".")
                                    logger.info("Will read the file's data but use the requested identifier.")
                    elif have_second_line:
                        # Special case where the 2nd line was read immediately after the first to check
                        # to see if only one time series is in the file. If here, set the line to what
                        # was read before...
                        have_second_line = False
                        iline = second_iline
                        second_iline = None
                    else:
                        # Read another line...
                        i += 1
                        # Check if at end of lines list
                        if i == len(lines):
                            break
                        iline = lines[i]
                    if iline is None:
                        # No more data...
                        break
                    line_count += 1
                    if iline.startswith("#"):
                        # Comment line. Count the line but do not treat as data...
                        continue
                    data_line_count += 1
                    if len(iline) == 0:
                        # Treat as a blank data line...
                        continue

                    # The first thing that we do is get the time series identifier
                    # so we can check against a requested identifier. If there is only
                    # one time series in the file, always use it.
                    if req_id is not None:
                        # Have a requested identifier and there are more than one time series.
                        # Get the ID from the input line. Don't parse out the remaining
                        # lines unless this line is a match...
                        if fileInterval == TimeInterval.MONTH:
                            chval = iline[5:17]
                        else:
                            # Daily offset for month...
                            chval = iline[9:21]
                        # Need this below...
                        id = chval.strip()

                        if not single_ts:
                            if id.upper() != req_id:
                                # We are not interested in this time series so don't process...
                                continue

                    # Parse the data line...
                    StringUtil.fixedRead2(iline, format, format_w, v)
                    if standard_ts:
                        # This is monthly and includes year
                        current_year = int(v[0])
                        if fileInterval == TimeInterval.DAY:
                            current_month = int(v[1])

                    # If we are reading the entire file, set id to current id
                    if req_id is None:
                        if fileInterval == TimeInterval.DAY:
                            # Have year, month, and then ID...
                            id = v[2].strip()
                        else:
                            # Have year and then ID...
                            id = v[1].strip()

                    # We are still establishing the list of stations in file
                    if ((fileInterval == TimeInterval.DAY) and (current_year == init_year) and (current_month == init_month)) or ((fileInterval == TimeInterval.MONTH) and (current_year == init_year)):
                        if req_id == None:
                            # Create a new time series...
                            if fileInterval == TimeInterval.DAY:
                                ts = DayTS()
                            else:
                                ts = MonthTS()
                        elif (id.upper() == req_id) or single_ts:
                            # We want the requested time series to get filled in...
                            ts = req_ts
                            req_id_found = True
                            numts = 1
                            # Save this index as that used for the requested time series...
                        if (reqDate1 is not None) and (reqDate2 is not None):
                            # Allocate memory for the time series based on the requested period.
                            ts.setDate1(reqDate1)
                            ts.setDate2(reqDate2)
                            ts.setDate1Original(date1_header)
                            ts.setDate2Original(date2_header)
                        else:
                            # Allocate memory for the time series based on the file header...
                            date.setMonth(m1)
                            date.setYear(y1)
                            if fileInterval == TimeInterval.DAY:
                                date.setDay(1)
                            ts.setDate1(date)
                            ts.setDate1Original(date1_header)

                            date.setMonth(m2)
                            date.setYear(y2)
                            if fileInterval == TimeInterval.DAY:
                                date.setDay(TimeUtil.numDaysInMonth(m2, y2))
                            ts.setDate2(date)
                            ts.setDate2Original(date2_header)

                        if readData:
                            ts.allocateDataSpace()

                        ts.setDataUnits(units)
                        ts.setDataUnitsOriginal(units)

                        # The input name is the full path to the input file...
                        ts.setInputName(fullFilename)
                        # Set other identifier information. The readTimeSeries() version that
                        # takes a full identifier will reset teh file information because it
                        # knows whether the original filename was from the scenario, etc.
                        ident = TSIdent()
                        ident.setLocation2(id)
                        if fileInterval == TimeInterval.DAY:
                            ident.setInterval_intervalString("DAY")
                        else:
                            ident.setInterval_intervalString("MONTH")
                        ident.setInputType("StateMod")
                        ident.setInputName(fullFilename)
                        ts.setDescription(id)
                        # May be forcing a read if only one time series but only reset the
                        # identifier if the file identifier does match the requested...
                        if ((req_id is not None) and req_id_found and (id.upper() == req_id)) or (req_id is None):
                            # Found the matching ID.
                            ts.setIdentifier(ident)
                            ts.addToGenesis("Read StateMod TS for " + str(ts.getDate1()) + " to " + str(ts.getDate2())
                                            + " from \"" + fullFilename + "\"")
                        if not req_id_found:
                            # Attach new time series to list. This is only done if we have not passed
                            # in a requested time series to fill.
                            if tslist is None:
                                tslist = []
                            tslist.append(ts)
                            numts += 1
                    else:
                        if not readData:
                            break

                    # If we are working through the first year, currentTSindex will
                    # be the last element index. On the other hand, if we have already
                    # established the list and are filling the rest of the rows, currentTSindex
                    # should be reset to 0. This assumes that the number and order of stations is
                    # consistent in the file from year to year.

                    if currentTSindex >= numts:
                        currentTSindex = 0
                    if not req_id_found:
                        # Filling a vector of TS...
                        currentTS = tslist[currentTSindex]
                    else:
                        # Filling a single time series...
                        currentTS = req_ts

                    if fileInterval == TimeInterval.DAY:
                        # Year from the file is always calendar year...
                        date.setYear(current_year)
                        # Month from the file is always calendar month...
                        date.setMonth(current_month)
                        # Day always starts at 1...
                        date.setDay(1)
                    else:
                        # Monthly data. The year is for calendar type and
                        # therefore the starting year may actually need to
                        # be set to the previous year. Don't do the shift
                        # for average monthly values.
                        if standard_ts and (yeartype != YearType.YearType_CALENDAR()):
                            date.setYear(current_year - 1)
                        else:
                            date.setYear(current_year)
                        # Month is assumed from calendar type - it is assumed that the header
                        # is correct...
                        date.setMonth(m1)
                    if reqDate2 is not None:
                        if date.greaterThan(reqDate2):
                            break

                    if readData:
                        if fileInterval == TimeInterval.DAY:
                            # Need to loop through the proper number of days for the month...
                            ndata_per_line = TimeUtil.numDaysInMonth(date.getMonth(), date.getYear())
                        for j in range(ndata_per_line):
                            currentTS.setDataValue(date, float(v[j+doffset]))
                            if fileInterval == TimeInterval.DAY:
                                date.addDay(1)
                            else:
                                date.addMonth(1)
                    currentTSindex+=1
                # print("time end: " + str(time.time() - start))
                break
        except Exception as e:
            message = ("Error reading file near line " + str(line_count) + " header indicates interval " +
                       fileIntervalString + ", period " + str(date1_header) + " to " + str(date2_header) +
                       ", units =\"" + units + "\" line: " + str(iline))
            logger.warning(message)
            logger.warning(e)
            return
        return tslist

    @staticmethod
    def readXTimeSeriesList(req_ts, f, fullFilename, fileInterval, reqDate1, reqDate2, reqUnits, readData):
        """
        Read a StateMod time series in an output format, for example the *xop.  This format has one
        time series listed after each other, with a main file header, time series header, and time series data.
        Currently only the monthly *xop file has been tested.
        """
        logger = logging.getLogger("StateMod")
        routine = "StateMod_TS.readXTimeSeriesList"
        tslist = []
        req_id = None
        if req_ts is not None:
            # Periods in identifiers are converted to underscores so as to not break period-delimited TSID
            req_id = req_ts.getLocation().replace('.', '_')
        iline = ""
        lineCount = 0
        try:
            # General error handler
            # Read lines until no more comments are found. The last line read will
            # need to be processed as the main header line...
            inTsHeader = False
            inTsData = False
            units = ""
            id = ""
            name = ""
            oprType = ""
            adminNum = ""
            source1 = ""
            dest = ""
            yearOn = ""
            yearOff = ""
            firstMonth = ""
            pos = int()
            v = []
            format = None
            format_w = None
            dataRowCount = 0  # Initialize for first iteration
            maxYears = 500  # Maximum years of data in a time series handled
            yearArray = [int()] * maxYears
            dataArray = [[float()]*13]*maxYears
            year = int()
            if fileInterval == TimeInterval.MONTH:
                if readData:
                    format = [int()] * 14
                    format_w = [int()] * 14
                else:
                    # Only year
                    format = [int()] * 1
                    format = [int()] * 1
                format[0] = StringUtil.TYPE_INTEGER
                format_w[0] = 4
                if readData:
                    for iFormat in range(14):
                        format[iFormat] = StringUtil.TYPE_DOUBLE
                    for iFormat in range(14):
                        format_w[iFormat] = 8
            else:
                logger.warning("Do not know how to read daily XOP file.")
            for iline in f:
                lineCount += 1
                # The first checks are expected at the top of the file but blank lines
                # and comments could be anywhere
                if len(iline) == 0:
                    continue
                elif iline[0] == "#":
                    continue
                elif (not inTsHeader) and iline.startswith(" Operational Right Summary"):
                    # Units are after this string - check below
                    inTsHeader = True
                elif (not inTsHeader) and iline.startswith(" ID ="):
                    # Second check to detect when in time series header, in case main header is not
                    # as expected
                    inTsHeader = True
                    # No continue because want to process the line
                if inTsHeader:
                    # Reading the time series header
                    if iline.startswith("_"):
                        # Last line in time series header section
                        inTsHeader = False
                        inTsData = True
                    elif iline.startswith(" Operational Right Summary"):
                        # Units are after this strong
                        units = iline[26].strip()
                    elif iline.startswith(" ID ="):
                        # Processing:   ID = 01038160.01        Name = Opr_Empire_Store         Opr Type =   45   Admin # =      20226.00000
                        pos = iline.find("ID =")
                        # Following may need to be +13 as per specification, but do 20 to allow flexibility
                        id = iline[pos+4:pos+4+20].strip()
                        # Identifier cannot contain periods so replace with underscore
                        id = id.replace('.','_')
                        pos = iline.find("Name =")
                        name = iline[pos+6:pos+6+24].strip()
                        pos = iline.find("Opr Type =")
                        oprType = iline[pos+10:pos+10+5].strip()
                        pos = iline.find("Admin # =")
                        adminNum = iline[pos+9:pos+9+17].strip()
                    elif iline.startswith(" Source 1 ="):
                        # Processing:    Source 1 = 0103816.01   Destination = 0103816           Year On =     0   Year Off =  9999
                        pos = iline.find("Source 1 =")
                        source1 = iline[pos+10:pos+10+12].strip()
                        pos = iline.find("Destination =")
                        dest = iline[pos+13:pos+13+12].strip()
                        pos = iline.find("Year On =")
                        yearOn = iline[pos+9:pos+9+6].strip()
                        pos = iline.find("Year Off =")
                        yearOff = iline[pos+10:pos+10+6].strip()
                    elif iline.startswith("YEAR"):
                        # Processing:  YEAR    JAN     FEB     MAR     APR     MAY     JUN     JUL     AUG     SEP     OCT     NOV     DEC     TOT
                        # Mainly interested in first month to know whether calendar
                        firstMonth = iline[6:14].strip()
                elif inTsData:
                    # Reading the time series data
                    if iline.startswith("AVG"):
                        # Last line in time series data section - create time series
                        tsid = (id + TSIdent.SEPARATOR + "" + TSIdent.SEPARATOR + "Operation" + TSIdent.SEPARATOR +
                        "Month" + TSIdent.INPUT_SEPARATOR + "StateMod" + TSIdent.INPUT_SEPARATOR + fullFilename)
                        ts = TSUtil.newTimeSeries(tsid, True)
                        ts.setIdentifier(tsid)
                        yearType = None
                        if firstMonth.upper() == "JAN":
                            yearType = YearType.YearType_CALENDAR()
                        if firstMonth.upper() == "OCT":
                            yearType = YearType.YearType_WATER()
                        if firstMonth.upper() == "NOV":
                            yearType = YearType.YearType_NOV_TO_OCT()
                        else:
                            logger.warning("Do not know how to handle year starting with month " + firstMonth)
                            return
                        # First set original period using file dates
                        date1 = DateTime(DateTime.PRECISION_MONTH)
                        date1.setYear(yearArray[0] + yearType.getStartYearOffset())
                        date1.setMonth(yearType.getStartMonth())
                        ts.setDate1Original(date1)
                        date2 = DateTime(DateTime.PRECISION_MONTH)
                        date2.setYear(yearArray[dataRowCount - 1])
                        date2.setMonth(yearType.getEndMonth())
                        ts.setDate2Original(date2)
                        # Set data period to requested if provided
                        if reqDate1 is not None:
                            ts.setDate1(reqDate1)
                        else:
                            ts.setDate1(ts.getDate1Original())
                        if reqDate2 is not None:
                            ts.setDate2(reqDate2)
                        else:
                            ts.setDate2(ts.getDate2Original())
                        ts.setDataUnits(units)
                        ts.setDataUnitsOriginal(units)
                        ts.setInputName(fullFilename)
                        ts.addToGenesis("Read StateMod TS for " + ts.getDate1() + " to " + ts.getDate2() +
                                        "from \"" + fullFilename + "\"")
                        # Be careful renaming the following because they show up in StateMod_TS_TableModel and
                        # possibly other classes
                        ts.setProperty("OprType", int(oprType))
                        ts.setProperty("AdminNum", adminNum)
                        ts.setProperty("Source1", source1)
                        ts.setProperty("Destination", dest)
                        ts.setProperty("YearOn", int(yearOn))
                        ts.setProperty("YearOff", int(yearOff))
                        if readData:
                            # Transfer the data that was read
                            ts.allocateDataSpace()
                        date = DateTime(DateTime.PRECISION_MONTH)
                        for iData in range(dataRowCount):
                            date.setYear(yearArray[iData] + yearType.getStartYearOffset())
                            date.setMonth(yearType.getStartMonth())
                            if readData:
                                for iMonth in range(12):
                                    date.addMonth(1)
                                    ts.setDataValue(date, dataArray[iData][iMonth])
                        if (req_id is not None) and (len(req_id) > 0):
                            if req_id.upper() == id:
                                # Found the requested time series so no need to keep reading
                                tslist.append(ts)
                                break
                        else:
                            tslist.append(ts)
                        # Set the flag to read another header and initialized header information
                        # to blanks so they can be populated by the next header
                        inTsHeader = True
                        inTsData = False
                        units = ""
                        dataRowCount = 0
                        id = ""
                        name = ""
                        oprType = ""
                        adminNum = ""
                        source1 = ""
                        dest = ""
                        yearOn = ""
                        yearOff = ""
                        firstMonth = ""
                    else:
                        # If first 4 characters are a number then it is a data line:
                        # 1950  12983.   3282.   8086.      0.      0.      0.      0.      0.      0.      0.      0.  15628.  39979.
                        # Fixed format read and numbers can be squished together
                        if not iline[0:4].isdigit():
                            # Don't know what to do with line
                            logger.warning("Don't know how to parse data line " + lineCount + ": " + iline.strip())
                        else:
                            # Always read the year so it can be used to set the period in time seires metadat
                            dataRowCount += 1
                            if dataRowCount <= maxYears:
                                StringUtil.fixedRead2(iline, format, format_w, v)
                                year = int(v[0])
                                yearArray[dataRowCount - 1] = year
                                if readData:
                                    for iv in range(14):
                                        dataArray[dataRowCount - 1][iv - 1] = float(v[iv])
        except Exception as e:
            logger.warning(e)
            return
        return tslist