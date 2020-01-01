#  StateMod_TS - class to read/write StateMod format time series

# NoticeStart
#
# CDSS Models Python Library
# CDSS Models Python Library is a part of Colorado's Decision Support Systems (CDSS)
# Copyright (C) 1994-2019 Colorado Department of Natural Resources
#
# CDSS Models Python Library is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     CDSS Models Python Library is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with CDSS Models Python Library.  If not, see <https://www.gnu.org/licenses/>.
#
# NoticeEnd

import logging
import os

from RTi.TS.DayTS import DayTS
from RTi.TS.MonthTS import MonthTS
from RTi.TS.TSIdent import TSIdent
from RTi.TS.TSUtil import TSUtil
from RTi.Util.IO.IOUtil import IOUtil
from RTi.Util.String.StringUtil import StringUtil
from RTi.Util.Time.DateTime import DateTime
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
    def get_file_data_interval(filename):
        """
        Determine whether a StateMod file is daily or monthly format.  This is done
        by reading through the file until the first line of data.  If that line has
        more than 150 characters, it is assumed to be a daily file; otherwise it is assumed
        to be a monthly file.  Currently, this method does NOT verify that the file
        contents are actually for StateMod.
        The IOUtil.get_path_using_working_dir() method is applied to the filename.
        :param filename: Name of file to examine.
        :return: TimeInterval.DAY, TimeInterval.MONTH or -999
        """
        logger = logging.getLogger(__name__)
        message = None
        iline = None
        interval_unknown = -999  # Return if can't figure out interval
        interval = interval_unknown
        full_filename = IOUtil.get_path_using_working_dir(filename)
        try:
            f = open(full_filename)
        except Exception as e:
            msg = "Unable to open file \"{}\" to determine data interval.".format(full_filename)
            logger.warning(msg)
            return interval_unknown
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
            return interval_unknown
        return interval

    @staticmethod
    def read_time_series_list(fname, date1, date2, units, read_data):
        """
        Read all the time series from a StateMod format file.
        The IOUtil.get_path_using_working_dir() method is applied to the filename.
        :param fname: Name of file to read.
        :param date1: Starting date to initialize period (NULL to read the entire time series).
        :param date2: Ending date to initialize period (NULL to read the entire time series).
        :param units: Units to convert to.
        :param read_data: Indicates whether data should be read.
        :return: a pointer to a newly-allocated Vector of time series if successful, a NULL pointer
        if not.
        """
        logger = logging.getLogger(__name__)
        tslist = None

        input_name = fname
        full_fname = IOUtil.get_path_using_working_dir(fname)
        data_interval = 0
        if(not os.path.isfile(full_fname)):
            logger.warning("File does not exist: \"{}\"".format(full_fname))
        try:
            data_interval = StateMod_TS.get_file_data_interval(full_fname)
            with open(full_fname) as f:
                tslist = StateMod_TS.read_time_series_list2(None, f, full_fname, data_interval,
                                                            date1, date2, units, read_data)
            nts = int()
            if tslist is not None:
                nts = len(tslist)
            for i in range(nts):
                ts = tslist[i]
                if ts is not None:
                    ts.set_input_name(full_fname)
                    ts.get_identifier().set_input_name(input_name)
        except Exception as e:
            logger.warning("Could not read file: \"{]\"".format(full_fname))
        return tslist

    @staticmethod
    def read_time_series_list2(req_ts, f, full_filename, file_interval, req_date1, req_date2, req_units, read_data):
        """
        Read one or more time series from a StateMod format file.
        :param req_ts: Pointer to time series to fill. If null, return all new time series
        in the list. All data are reset, except for the identifier, which is assumed to have
        been set in the calling code.
        :param f: reference to open filestream
        :param full_filename: Full path to filename, used for messages.
        :param file_interval: Indicates the file type (TimeInterval.DAY or TimeInterval.MONTH).
        :param req_date1: Requested starting date to initialize period (or NULL to read the entire
        time series).
        :param req_date2: Requested ending date to initialize period (or NULL to read the entire time series).
        :param req_units: Units to convert to (currently ignored).
        :param read_data: Indicates whether data should be read.
        :return: a list of time series if successful, null if not. The calling code is responsible
        for freeing the memory for the time series.
        """
        # start = time.time()
        logger = logging.getLogger(__name__)
        dl = 40
        i = int()
        line_count = 0
        m1 = int()
        m2 = int()
        y1 = int()
        y2 = int()
        current_ts_index = int()
        current_month = 1
        current_year = 0
        doffset = 2
        init_month = 1
        init_year = int()
        ndata_per_line = 12
        numts = 0

        chval = str()
        iline = ""

        v = []
        date = None
        if full_filename.upper().endswith("XOP"):
            # XOP file is similar to the normal time series format but has some difference
            # in that the header is different, station identifier is provided in the header, and
            # time series are listed vertically one after another, not interwoven by interval like
            # *.stm
            return StateMod_TS.read_x_time_series_list(req_ts, f, full_filename, file_interval,
                                                       req_date1, req_date2, req_units, read_data)
        file_interval_string = ""
        if file_interval == TimeInterval.DAY:
            date = DateTime(DateTime.PRECISION_DAY)
            doffset = 3  # Used when setting data to skip the leading fields on the data line
            file_interval_string = "Day"
        elif file_interval == TimeInterval.MONTH:
            date = DateTime(DateTime.PRECISION_MONTH)
            file_interval_string = "Month"
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
        year_type = YearType.YearType_CALENDAR()
        try:  # General error handler
            # Read first line of the file
            line_count += 1
            i = -1
            lines = f.readlines()
            while i < len(lines) - 1:
                i += 1
                iline = lines[i]
                if iline is None:
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

                format_file_contents = None
                if iline[3] == '/':
                    logger.warning("Non-standard header for file \"" + full_filename + "\" allowing with work-around.")
                    format_file_contents = "i3x1i4x5i5x1i4s5s5"
                else:
                    # Probably formatted correctly...
                    format_file_contents = "i5x1i4x5i5x1i4s5s5"

                v = StringUtil.fixed_read(iline, format_file_contents)

                m1 = int(v[0])
                y1 = int(v[1])
                m2 = int(v[2])
                y2 = int(v[3])
                if file_interval == TimeInterval.DAY:
                    date1_header = DateTime(DateTime.PRECISION_DAY)
                    date1_header.set_year(y1)
                    date1_header.set_month(m1)
                    date1_header.set_day(1)
                else:
                    date1_header = DateTime(DateTime.PRECISION_MONTH)
                    date1_header.set_year(y1)
                    date1_header.set_month(m1)
                if file_interval == TimeInterval.DAY:
                    date2_header = DateTime(DateTime.PRECISION_DAY)
                    date2_header.set_year(y2)
                    date2_header.set_month(m2)
                    date2_header.set_day(TimeUtil.num_days_in_month(m2, y2))
                else:
                    date2_header = DateTime(DateTime.PRECISION_MONTH)
                    date2_header.set_year(y2)
                    date2_header.set_month(m2)
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
                if file_interval == TimeInterval.DAY:
                    format = [int()]*35
                    format_w = [int()]*35
                    format[0] = StringUtil.TYPE_INTEGER
                    format[1] = StringUtil.TYPE_INTEGER
                    format[2] = StringUtil.TYPE_SPACE
                    format[3] = StringUtil.TYPE_STRING
                    # TODO @jurentie 04/26/2019 - the following might need tested
                    i_format = 4
                    for j in range(30):
                        format[i_format] = StringUtil.TYPE_DOUBLE
                        i_format += 1
                    format_w[0] = 4
                    format_w[1] = 4
                    format_w[2] = 1
                    format_w[3] = 12
                    i_format = 4
                    for j in range(30):
                        format_w[i_format] = 8
                        i_format += 1
                else:
                    format = [int()] * 14
                    format[0] = StringUtil.TYPE_INTEGER
                    format[1] = StringUtil.TYPE_STRING
                    i_format = 2
                    for j in range(12):
                        format[i_format] = StringUtil.TYPE_DOUBLE
                        i_format += 1
                    format_w = [int()] * 14
                    format_w[0] = 5
                    format_w[1] = 12
                    i_format = 2
                    for j in range(12):
                        format_w[i_format] = 8
                        i_format += 1
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
                    if file_interval == TimeInterval.MONTH and (m2 < m1):
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
                current_ts_index = 0
                current_ts = None  # used to fill data
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
                        if iline is None:
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
                        if file_interval == TimeInterval.MONTH:
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
                    StringUtil.fixed_read2(iline, format, format_w, v)
                    if standard_ts:
                        # This is monthly and includes year
                        current_year = int(v[0])
                        if file_interval == TimeInterval.DAY:
                            current_month = int(v[1])

                    # If we are reading the entire file, set id to current id
                    if req_id is None:
                        if file_interval == TimeInterval.DAY:
                            # Have year, month, and then ID...
                            id = v[2].strip()
                        else:
                            # Have year and then ID...
                            id = v[1].strip()

                    # We are still establishing the list of stations in file
                    if ((file_interval == TimeInterval.DAY) and (current_year == init_year) and
                        (current_month == init_month)) or ((file_interval == TimeInterval.MONTH) and
                                                           (current_year == init_year)):
                        if req_id is None:
                            # Create a new time series...
                            if file_interval == TimeInterval.DAY:
                                ts = DayTS()
                            else:
                                ts = MonthTS()
                        elif (id.upper() == req_id) or single_ts:
                            # We want the requested time series to get filled in...
                            ts = req_ts
                            req_id_found = True
                            numts = 1
                            # Save this index as that used for the requested time series...
                        if (req_date1 is not None) and (req_date2 is not None):
                            # Allocate memory for the time series based on the requested period.
                            ts.set_date1(req_date1)
                            ts.set_date2(req_date2)
                            ts.set_date1_original(date1_header)
                            ts.set_date2_original(date2_header)
                        else:
                            # Allocate memory for the time series based on the file header...
                            date.set_month(m1)
                            date.set_year(y1)
                            if file_interval == TimeInterval.DAY:
                                date.set_day(1)
                            ts.set_date1(date)
                            ts.set_date1_original(date1_header)

                            date.set_month(m2)
                            date.set_year(y2)
                            if file_interval == TimeInterval.DAY:
                                date.set_day(TimeUtil.num_days_in_month(m2, y2))
                            ts.set_date2(date)
                            ts.set_date2_original(date2_header)

                        if read_data:
                            ts.allocate_data_space()

                        ts.set_data_units(units)
                        ts.set_data_units_original(units)

                        # The input name is the full path to the input file...
                        ts.set_input_name(full_filename)
                        # Set other identifier information. The readTimeSeries() version that
                        # takes a full identifier will reset teh file information because it
                        # knows whether the original filename was from the scenario, etc.
                        ident = TSIdent()
                        ident.set_location2(id)
                        if file_interval == TimeInterval.DAY:
                            ident.set_interval_interval_string("DAY")
                        else:
                            ident.set_interval_interval_string("MONTH")
                        ident.set_input_type("StateMod")
                        ident.set_input_name(full_filename)
                        ts.set_description(id)
                        # May be forcing a read if only one time series but only reset the
                        # identifier if the file identifier does match the requested...
                        if ((req_id is not None) and req_id_found and (id.upper() == req_id)) or (req_id is None):
                            # Found the matching ID.
                            ts.set_identifier(ident)
                            ts.add_to_genesis("Read StateMod TS for " + str(ts.get_date1()) + " to " +
                                              str(ts.get_date2()) + " from \"" + full_filename + "\"")
                        if not req_id_found:
                            # Attach new time series to list. This is only done if we have not passed
                            # in a requested time series to fill.
                            if tslist is None:
                                tslist = []
                            tslist.append(ts)
                            numts += 1
                    else:
                        if not read_data:
                            break

                    # If we are working through the first year, current_ts_index will
                    # be the last element index. On the other hand, if we have already
                    # established the list and are filling the rest of the rows, current_ts_index
                    # should be reset to 0. This assumes that the number and order of stations is
                    # consistent in the file from year to year.

                    if current_ts_index >= numts:
                        current_ts_index = 0
                    if not req_id_found:
                        # Filling a vector of TS...
                        current_ts = tslist[current_ts_index]
                    else:
                        # Filling a single time series...
                        current_ts = req_ts

                    if file_interval == TimeInterval.DAY:
                        # Year from the file is always calendar year...
                        date.set_year(current_year)
                        # Month from the file is always calendar month...
                        date.set_month(current_month)
                        # Day always starts at 1...
                        date.set_day(1)
                    else:
                        # Monthly data. The year is for calendar type and
                        # therefore the starting year may actually need to
                        # be set to the previous year. Don't do the shift
                        # for average monthly values.
                        if standard_ts and (yeartype != YearType.YearType_CALENDAR()):
                            date.set_year(current_year - 1)
                        else:
                            date.set_year(current_year)
                        # Month is assumed from calendar type - it is assumed that the header
                        # is correct...
                        date.set_month(m1)
                    if req_date2 is not None:
                        if date.greater_than(req_date2):
                            break

                    if read_data:
                        if file_interval == TimeInterval.DAY:
                            # Need to loop through the proper number of days for the month...
                            ndata_per_line = TimeUtil.num_days_in_month(date.getMonth(), date.getYear())
                        for j in range(ndata_per_line):
                            current_ts.set_data_value(date, float(v[j+doffset]))
                            if file_interval == TimeInterval.DAY:
                                date.addDay(1)
                            else:
                                date.add_month(1)
                    current_ts_index += 1
                # print("time end: " + str(time.time() - start))
                break
        except Exception as e:
            message = ("Error reading file near line " + str(line_count) + " header indicates interval " +
                       file_interval_string + ", period " + str(date1_header) + " to " + str(date2_header) +
                       ", units =\"" + units + "\" line: " + str(iline))
            logger.warning(message)
            logger.warning(e)
            return
        return tslist

    @staticmethod
    def read_x_time_series_list(req_ts, f, full_filename, file_interval, req_date1, req_date2, req_units, read_data):
        """
        Read a StateMod time series in an output format, for example the *xop.  This format has one
        time series listed after each other, with a main file header, time series header, and time series data.
        Currently only the monthly *xop file has been tested.
        """
        logger = logging.getLogger(__name__)
        tslist = []
        req_id = None
        if req_ts is not None:
            # Periods in identifiers are converted to underscores so as to not break period-delimited TSID
            req_id = req_ts.getLocation().replace('.', '_')
        iline = ""
        line_count = 0
        try:
            # General error handler
            # Read lines until no more comments are found. The last line read will
            # need to be processed as the main header line...
            in_ts_header = False
            in_ts_data = False
            units = ""
            id = ""
            name = ""
            opr_type = ""
            admin_num = ""
            source1 = ""
            dest = ""
            year_on = ""
            year_off = ""
            first_month = ""
            pos = int()
            v = []
            format = None
            format_w = None
            data_row_count = 0  # Initialize for first iteration
            maxYears = 500  # Maximum years of data in a time series handled
            year_array = [int()] * maxYears
            data_array = [[float()]*13]*maxYears
            year = int()
            if file_interval == TimeInterval.MONTH:
                if read_data:
                    format = [int()] * 14
                    format_w = [int()] * 14
                else:
                    # Only year
                    format = [int()] * 1
                    format = [int()] * 1
                format[0] = StringUtil.TYPE_INTEGER
                format_w[0] = 4
                if read_data:
                    for i_format in range(14):
                        format[i_format] = StringUtil.TYPE_DOUBLE
                    for i_format in range(14):
                        format_w[i_format] = 8
            else:
                logger.warning("Do not know how to read daily XOP file.")
            for iline in f:
                line_count += 1
                # The first checks are expected at the top of the file but blank lines
                # and comments could be anywhere
                if len(iline) == 0:
                    continue
                elif iline[0] == "#":
                    continue
                elif (not in_ts_header) and iline.startswith(" Operational Right Summary"):
                    # Units are after this string - check below
                    in_ts_header = True
                elif (not in_ts_header) and iline.startswith(" ID ="):
                    # Second check to detect when in time series header, in case main header is not
                    # as expected
                    in_ts_header = True
                    # No continue because want to process the line
                if in_ts_header:
                    # Reading the time series header
                    if iline.startswith("_"):
                        # Last line in time series header section
                        in_ts_header = False
                        in_ts_data = True
                    elif iline.startswith(" Operational Right Summary"):
                        # Units are after this strong
                        units = iline[26].strip()
                    elif iline.startswith(" ID ="):
                        # Processing:   ID = 01038160.01        Name = Opr_Empire_Store         Opr Type =   45   Admin # =      20226.00000
                        pos = iline.find("ID =")
                        # Following may need to be +13 as per specification, but do 20 to allow flexibility
                        id = iline[pos+4:pos+4+20].strip()
                        # Identifier cannot contain periods so replace with underscore
                        id = id.replace('.', '_')
                        pos = iline.find("Name =")
                        name = iline[pos+6:pos+6+24].strip()
                        pos = iline.find("Opr Type =")
                        opr_type = iline[pos+10:pos+10+5].strip()
                        pos = iline.find("Admin # =")
                        admin_num = iline[pos+9:pos+9+17].strip()
                    elif iline.startswith(" Source 1 ="):
                        # Processing:    Source 1 = 0103816.01   Destination = 0103816           Year On =     0   Year Off =  9999
                        pos = iline.find("Source 1 =")
                        source1 = iline[pos+10:pos+10+12].strip()
                        pos = iline.find("Destination =")
                        dest = iline[pos+13:pos+13+12].strip()
                        pos = iline.find("Year On =")
                        year_on = iline[pos+9:pos+9+6].strip()
                        pos = iline.find("Year Off =")
                        year_off = iline[pos+10:pos+10+6].strip()
                    elif iline.startswith("YEAR"):
                        # Processing:  YEAR    JAN     FEB     MAR     APR     MAY     JUN     JUL     AUG     SEP     OCT     NOV     DEC     TOT
                        # Mainly interested in first month to know whether calendar
                        first_month = iline[6:14].strip()
                elif in_ts_data:
                    # Reading the time series data
                    if iline.startswith("AVG"):
                        # Last line in time series data section - create time series
                        tsid = (id + TSIdent.SEPARATOR + "" + TSIdent.SEPARATOR + "Operation" + TSIdent.SEPARATOR +
                                "Month" + TSIdent.INPUT_SEPARATOR + "StateMod" + TSIdent.INPUT_SEPARATOR +
                                full_filename)
                        ts = TSUtil.new_time_series(tsid, True)
                        ts.set_identifier(tsid)
                        year_type = None
                        if first_month.upper() == "JAN":
                            year_type = YearType.YearType_CALENDAR()
                        if first_month.upper() == "OCT":
                            year_type = YearType.YearType_WATER()
                        if first_month.upper() == "NOV":
                            year_type = YearType.YearType_NOV_TO_OCT()
                        else:
                            logger.warning("Do not know how to handle year starting with month " + first_month)
                            return
                        # First set original period using file dates
                        date1 = DateTime(DateTime.PRECISION_MONTH)
                        date1.set_year(year_array[0] + year_type.getStartYearOffset())
                        date1.set_month(year_type.getStartMonth())
                        ts.set_date1_original(date1)
                        date2 = DateTime(DateTime.PRECISION_MONTH)
                        date2.set_year(year_array[data_row_count - 1])
                        date2.set_month(year_type.getEndMonth())
                        ts.set_date2_original(date2)
                        # Set data period to requested if provided
                        if req_date1 is not None:
                            ts.set_date1(req_date1)
                        else:
                            ts.set_date1(ts.get_date1_original())
                        if req_date2 is not None:
                            ts.set_date2(req_date2)
                        else:
                            ts.set_date2(ts.get_date2_original())
                        ts.set_data_units(units)
                        ts.set_data_units_original(units)
                        ts.set_input_name(full_filename)
                        ts.add_to_genesis("Read StateMod TS for " + ts.get_date1() + " to " + ts.get_date2() +
                                          "from \"" + full_filename + "\"")
                        # Be careful renaming the following because they show up in StateMod_TS_TableModel and
                        # possibly other classes
                        ts.set_property("OprType", int(opr_type))
                        ts.set_property("AdminNum", admin_num)
                        ts.set_property("Source1", source1)
                        ts.set_property("Destination", dest)
                        ts.set_property("YearOn", int(year_on))
                        ts.set_property("YearOff", int(year_off))
                        if read_data:
                            # Transfer the data that was read
                            ts.allocate_data_space()
                        date = DateTime(DateTime.PRECISION_MONTH)
                        for iData in range(data_row_count):
                            date.set_year(year_array[iData] + year_type.getStartYearOffset())
                            date.set_month(year_type.getStartMonth())
                            if read_data:
                                for iMonth in range(12):
                                    date.add_month(1)
                                    ts.set_data_value(date, data_array[iData][iMonth])
                        if (req_id is not None) and (len(req_id) > 0):
                            if req_id.upper() == id:
                                # Found the requested time series so no need to keep reading
                                tslist.append(ts)
                                break
                        else:
                            tslist.append(ts)
                        # Set the flag to read another header and initialized header information
                        # to blanks so they can be populated by the next header
                        in_ts_header = True
                        in_ts_data = False
                        units = ""
                        data_row_count = 0
                        id = ""
                        name = ""
                        opr_type = ""
                        admin_num = ""
                        source1 = ""
                        dest = ""
                        year_on = ""
                        year_off = ""
                        first_month = ""
                    else:
                        # If first 4 characters are a number then it is a data line:
                        # 1950  12983.   3282.   8086.      0.      0.      0.      0.      0.      0.      0.      0.  15628.  39979.
                        # Fixed format read and numbers can be squished together
                        if not iline[0:4].isdigit():
                            # Don't know what to do with line
                            logger.warning("Don't know how to parse data line " + str(line_count) + ": " +
                                           iline.strip())
                        else:
                            # Always read the year so it can be used to set the period in time seires metadat
                            data_row_count += 1
                            if data_row_count <= maxYears:
                                StringUtil.fixed_read2(iline, format, format_w, v)
                                year = int(v[0])
                                year_array[data_row_count - 1] = year
                                if read_data:
                                    for iv in range(14):
                                        data_array[data_row_count - 1][iv - 1] = float(v[iv])
        except Exception as e:
            logger.warning(e)
            return
        return tslist
