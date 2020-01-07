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

    # Used with get_precision_with_units
    last_units = ""
    last_units_precision = PRECISION_DEFAULT

    # Used with get_precision
    exp_saved = -999
    largest_number_saved = 0.0

    debug = False

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
        interval_unknown = -999  # Return if can't figure out interval
        interval = interval_unknown
        full_filename = IOUtil.get_path_using_working_dir(filename)
        try:
            f = open(full_filename)
        except Exception as e:
            msg = "Unable to open file \"{}\" to determine data interval.".format(full_filename)
            logger.warning(msg, exc_info=True)
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
    def get_line_total(ts, standard_ts, nvals, line_objects, format_objects, req_interval_base, do_total, sum, count,
                       do_sum_to_printed):
        """
        Get the total for a line as a Double.  This computes the total based on what will be printed, not what
        is in memory.  In this way the printed total will agree with the printed monthly or daily values.
        @param ts time series being written
        @param standard_ts if false, it is an annual average so no year
        @param nvals number of values possible in the line of data (12 for monthly or the number of days in the month
        for daily)
        @param line_objects data values to print as objects of the appropriate type
        @param format_objects formats that are used to print each value
        @param req_interval_base indicates whether monthly or daily time series are being printed
        @param do_total if true then the total is calculated for the end of the line, if false the average is calculated
        @param sum the sum of the values to be considered for the total
        @param count the count of the values to be considered for the average (includes only non-missing values)
        @param do_sum_to_printed whether or not to include sum in printed output
        """
        if do_sum_to_printed:
            # The total needs to sum to the printed values on the line
            # Loop through the original values and format each.  Then add them and format the total
            i1 = 2  # Start and end indices for looping through values, year, ID, first value
            if not standard_ts:
                i1 = i1 - 1  # Average annual so no year
            i2 = i1 + nvals - 1  # always 12 values
            if req_interval_base == TimeInterval.DAY:
                i1 = 3  # Year, month, ID, first value
                i2 = i1 + nvals - 1  # actual number of values (may be less than 31 for daily)
            sum = 0.0
            count = 0
            for i in range(i1, (i2 + 1)):
                formatted_string = StringUtil.format_string(line_objects[i], format_objects[i])
                val = float(formatted_string)
                if not ts.is_data_missing(val):
                    sum += val
                    count = count + 1

        # Legacy code where the total sums to the in-memory values
        if count == 0:
            # Missing
            return ts.get_missing()
        elif do_total:
            # Sum of whatever is available
            return sum
        else:
            # Mean of whatever is available
            return sum/count

    @staticmethod
    def get_precision(req_precision, width, value):
        """
        @return The appropriate precision to output a value.
        @param req_precision The requested precision.  If 0 or positive, then use the
        requested precision.  If negative, use the requested precision (positive value)
        if the resulting number fits into the width of the column.  Otherwise adjust the precision to fit.
        @param width
        @param value
        """
        # If req_precision is > PRECISION_SPECIAL_OFFSET, divide to get the
        # numeric requested precision...

        if (req_precision > StateMod_TS.PRECISION_SPECIAL_OFFSET) or \
                (req_precision*-1 > StateMod_TS.PRECISION_SPECIAL_OFFSET):
            req_precision = req_precision/StateMod_TS.PRECISION_SPECIAL_OFFSET

        # If req_precision is a positive value, return req_precision...
        if req_precision >= 0:
            return req_precision
        # Else if value is within the width of column, return req_precision...
        # The 2 allows for the decimal and a sign.
        # For example, for a width of 8, and a requested precision of -2:
        #
        # -1234.12
        #
        # Would be the output format.  Because width is negative if we get to
        # here, add to the width instead of subtracting...
        # int exp
        if value < 0.0:
            # Decimal point and sign...
            exp = width + req_precision - 2
        else:
            # Decimal only...
            exp = width + req_precision - 1
        largest_number = 0.0
        if (exp == StateMod_TS.exp_saved) and (exp != -999):
            # We have called this code with the same information before
            # so don't regenerate the largest_number...
            largest_number = StateMod_TS.largest_number_saved
        else:
            # Need to compute the largest number.  Using the example above,
            # we would get 10^4 = 10000 - 1.0 = 9999.99
            largest_number = pow(10, float(exp)) - 1.0
            StateMod_TS.largest_number_saved = largest_number
            StateMod_TS.exp_saved = exp
        # Handle negative and positive values...
        if value > 0.0:
            plus_value = value
        else:
            plus_value = value*-1.0
        if plus_value <= largest_number:
            # It fits within the precision.  Return the positive value of the precision...
            return req_precision*-1
        # Else, the value is larger than the allowable width and req_precision
        # indicates that some changes are allowed - return 0
        # Note that this handles big numbers well but may not handle the case
        # of small numbers.  That may be an enhancement for later.
        return 0

    @staticmethod
    def get_precision_with_units(req_precision, width, value, units):
        """
        @return The appropriate precision to output a value.
        @param req_precision The requested precision.  If 0 or positive, then use the
        requested precision.  If negative, use the requested precision (positive value)
        if the resulting number fits into the width of the column.  Otherwise adjust
        the precision to fit.  If PRECISION_USE_UNITS, use the units to determine the precision.
        @param width
        @param value
        @param units
        """
        # if no units data, call the simple version...

        if (units is None) or (units == ""):
            return StateMod_TS.get_precision(req_precision, width, value)

        # Else we need to check the units and get the precision.  In general
        # all the units in the file will be the same so we just save the
        # last lookup and return that if the units match...

        if units.upper() == StateMod_TS.last_units.upper():
            return StateMod_TS.last_units_precision

        units_precision = StateMod_TS.PRECISION_DEFAULT

        try:
            # TODO smalers 2020-02-04 For now hard-code precision
            # - eventually will need to use a DataUnits-type file or or just hard code based on StateMod typical use
            # units_format = DataUnits.get_output_format(units, width)
            StateMod_TS.last_units = units
            # StateMod_TS.last_units_precision = units_format.get_precision()
            StateMod_TS.last_units_precision = 2  # TODO smalers 2020-01-04 hard-code for now
        except Exception as e:
            # Could not get units so return the requested precision without checking units...
            return StateMod_TS.get_precision(req_precision, width, value)

        # Now have the units precision so call the general routine with a negative value...

        if units_precision < 0:
            return StateMod_TS.get_precision(units_precision, width, value)
        else:
            return StateMod_TS.get_precision(-1*units_precision, width, value)

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
        if not os.path.isfile(full_fname):
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
            logger.warning("Could not read file: \"{]\"".format(full_fname), exc_info=True)
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
        ndata_per_line = 12
        numts = 0
        doffset = 2

        v = []
        date = None
        if full_filename.upper().endswith("XOP"):
            # XOP file is similar to the normal time series format but has some difference
            # in that the header is different, station identifier is provided in the header, and
            # time series are listed vertically one after another, not interwoven by interval like
            # *.stm
            return StateMod_TS.read_x_time_series_list(req_ts, f, full_filename, file_interval,
                                                       req_date1, req_date2, req_units, read_data)
        file_interval_string = "Unknown"
        if file_interval == TimeInterval.DAY:
            date = DateTime(flag=DateTime.PRECISION_DAY)
            doffset = 3  # Used when setting data to skip the leading fields on the data line
            file_interval_string = "Day"
        elif file_interval == TimeInterval.MONTH:
            date = DateTime(flag=DateTime.PRECISION_MONTH)
            file_interval_string = "Month"
        else:
            logger.warning("Requested file interval is invalid.")
        logger.info("Reading time series file interval: " + file_interval_string)

        req_id_found = False  # Indicates if we have found the requested TS in the file.
        standard_ts = True  # Non-standard indicates 12 monthly averages in file.

        tslist = None  # List of time series to return.
        req_id = None
        if req_ts is not None:
            req_id = req_ts.getLocation()
            req_id_upper = req_id.upper()  # used for string ignore case comparisons
        # Declare here so are visible in final catch to provide feedback for bad format files
        date1_header = None
        date2_header = None
        units = ""
        yeartype = YearType(YearType.CALENDAR)  # Default
        # The Python code reads all the lines into a list and then iterates over the list whereas Java
        # read the file lines as needed.  'line_pos' is  zero-index line number int the list.
        try:  # General error handler
            # Read first line of the file
            line_pos = -1  # 0-index
            # Read all the file lines into a list "lines"
            lines = f.readlines()
            len_lines = len(lines)
            if len_lines == 0:
                logger.warning("Zero length file.")
                return None
            line_pos += 1
            iline = lines[line_pos]
            if iline is None:
                logger.warning("Zero length file.")
                return None
            # if len(iline.strip()) < 1:
            #    logger.warning("Zero length file.")
            #    return None

            # Read lines until no more comments are found. The last line read will
            # need to be processed as the main header line...

            while iline.startswith("#"):
                if line_pos == len_lines - 1:
                    # No more input lines
                    break
                line_pos += 1
                iline = lines[line_pos]

            if StateMod_TS.debug:
                logger.debug("Done with comments.")

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
            if StateMod_TS.debug:
                logger.debug("Parsing header line: \"" + iline + "\"")

            v = StringUtil.fixed_read(iline, format_file_contents)

            m1 = int(v[0])
            y1 = int(v[1])
            m2 = int(v[2])
            y2 = int(v[3])
            if file_interval == TimeInterval.DAY:
                date1_header = DateTime(flag=DateTime.PRECISION_DAY)
                date1_header.set_year(y1)
                date1_header.set_month(m1)
                date1_header.set_day(1)
            else:
                date1_header = DateTime(flag=DateTime.PRECISION_MONTH)
                date1_header.set_year(y1)
                date1_header.set_month(m1)
            if file_interval == TimeInterval.DAY:
                date2_header = DateTime(flag=DateTime.PRECISION_DAY)
                date2_header.set_year(y2)
                date2_header.set_month(m2)
                date2_header.set_day(TimeUtil.num_days_in_month(m2, y2))
            else:
                date2_header = DateTime(flag=DateTime.PRECISION_MONTH)
                date2_header.set_year(y2)
                date2_header.set_month(m2)
            units = v[4].strip()
            yeartypes = v[5].strip()
            logger.info("Header year type string =\"" + yeartypes + "\"")
            # Year type is used in one place to initialize the year when
            # transferring data. However, it is assumed that m1 is always correct for the year type.
            if yeartypes.upper() == "CAL" or yeartypes.upper() == "":
                yeartype = YearType(YearType.WATER)
            elif yeartypes.upper() == "WYR":
                yeartype = YearType(YearType.WATER)
            elif yeartypes.upper() == "IYR":
                yeartype = YearType(YearType.NOV_TO_OCT)
            else:
                raise ValueError("Unknown year type " + yeartypes)

            # year that are specified are used to set the period.

            logger.info("Header has start date=" + str(date1_header) + " end date=" + str(date2_header) +
                        " units=" + units + " yeartype=" + str(yeartype))

            format_t = []
            format_w = []
            if file_interval == TimeInterval.DAY:
                format_t = [int()]*35  # Format type
                format_w = [int()]*35  # Format width
                format_t[0] = StringUtil.TYPE_INTEGER
                format_t[1] = StringUtil.TYPE_INTEGER
                format_t[2] = StringUtil.TYPE_SPACE
                format_t[3] = StringUtil.TYPE_STRING
                for i_format in range(4,35):
                    format_t[i_format] = StringUtil.TYPE_DOUBLE
                format_w[0] = 4
                format_w[1] = 4
                format_w[2] = 1
                format_w[3] = 12
                for i_format in range(4,35):
                    format_w[i_format] = 8
            else:
                format_t = [int()] * 14
                format_t[0] = StringUtil.TYPE_INTEGER
                format_t[1] = StringUtil.TYPE_STRING
                for i_format in range(2,14):
                    format_t[i_format] = StringUtil.TYPE_DOUBLE
                format_w = [int()] * 14
                format_w[0] = 5
                format_w[1] = 12
                for i_format in range(2,14):
                    format_w[i_format] = 8
            if y1 == 0:
                # average monthly series
                standard_ts = False
                format_t[0] = StringUtil.TYPE_STRING  # Year not used
                current_year = 0  # Start year will be calendar year 0
                init_year = 0
                if m2 < m1:
                    y2 = 1  # End year is calendar year 1
            else:
                # Standard time series, includes a year on input lines
                standard_ts = True
                current_year = y1
                if (file_interval == TimeInterval.MONTH) and (m2 < m1):
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
                    if line_pos == len_lines - 1:
                        # No more input lines
                        break
                    # Get another input line
                    line_pos += 1
                    iline = lines[line_pos]
                    if iline is None:
                        break
                    if iline.startswith("#"):
                        # Comment line. Count the line but do not treat as data...
                        continue
                    # To allow for the case where only one time series is in
                    # the file and a req_id is specified that may be different
                    # (but always return the file contents), read the second line...
                    if line_pos == len_lines - 1:
                        # No more input lines
                        break
                    line_pos += 1
                    second_iline = lines[line_pos]
                    have_second_line = True
                    if second_iline is not None:
                        # Check to see if the year from the first line is different
                        # from the second line, and the identifiers are the same.
                        # If so, assume one time series in the file.
                        # Some files with average time series do not include a year.
                        line1_year_string = iline[0:5].strip()
                        if line1_year_string == "":
                            line1_year = 0
                        else:
                            line1_year = int(line1_year_string)
                        line2_year_string = second_iline[0:5].strip()
                        if line2_year_string == "":
                            line2_year = 0
                        else:
                            line2_year = int(line2_year_string)
                        line1_id = iline[5:17].strip()
                        line2_id = second_iline[5:17].strip()
                        if (line1_id == line2_id) and (line1_year != line2_year):
                            single_ts = True
                            logger.info("Single TS detected - reading all.")
                            if (req_id is not None) and (line1_id.upper() != req_id_upper):
                                logger.info("Reading StateMod file, the requested ID is \"" +
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
                    # Check if at end of lines list
                    if line_pos == (len_lines - 1):
                        break
                    line_pos += 1
                    iline = lines[line_pos]
                if iline is None:
                    # No more data...
                    break
                if iline.startswith("#"):
                    # Comment line. Count the line but do not treat as data...
                    continue
                # Count the data line
                data_line_count += 1
                if len(iline) == 0:
                    # Treat as a blank data line...
                    continue

                if StateMod_TS.debug:
                    logger.debug("Parsing line: \"" + iline + "\" line_pos=" + str(line_pos) +
                                 " data_line_count=" + str(data_line_count))

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
                        if id.upper() != req_id_upper:
                            # We are not interested in this time series so don't process...
                            if StateMod_TS.debug:
                                logger.debug("Looking for \"" + req_id +
                                             "\".  Not interested in \"" + id + "\".  Continuing.")
                            continue

                # Parse the data line...
                StringUtil.fixed_read2(iline, format_t, format_w, v)
                if standard_ts:
                    # This is monthly and includes year
                    current_year = int(v[0])
                    if file_interval == TimeInterval.DAY:
                        current_month = int(v[1])
                        if StateMod_TS.debug:
                            logger.debug("Found id!  Current date is " + str(current_year) + "-" + str(current_month))
                    else:
                        if StateMod_TS.debug:
                            logger.debug("Found id!  Current year is " + str(current_year))
                else:
                    if StateMod_TS.debug:
                        logger.debug("Found ID!  Read average format.")

                # If we are reading the entire file, set id to current id
                if req_id is None:
                    if file_interval == TimeInterval.DAY:
                        # Have year, month, and then ID...
                        locid = v[2].strip()
                    else:
                        # Have year and then ID...
                        locid = v[1].strip()
                    if StateMod_TS.debug:
                        logger.debug("Location ID:  " + str(locid))

                # We are still establishing the list of stations in file
                if StateMod_TS.debug:
                    logger.debug("Current year: " + str(current_year) + ", Init year: " + str(init_year))
                if ((file_interval == TimeInterval.DAY) and (current_year == init_year) and
                    (current_month == init_month)) or ((file_interval == TimeInterval.MONTH) and
                                                       (current_year == init_year)):
                    if req_id is None:
                        # Create a new time series...
                        if file_interval == TimeInterval.DAY:
                            ts = DayTS()
                        else:
                            ts = MonthTS()
                    elif (id.upper() == req_id_upper) or single_ts:
                        # We want the requested time series to get filled in...
                        ts = req_ts
                        req_id_found = True
                        numts = 1
                        # Save this index as that used for the requested time series...
                    # Else, we already caught this in a check above and would not get to here.
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
                        if StateMod_TS.debug:
                            logger.info("Input file start date = " + str(date))
                        ts.set_date1(date)
                        ts.set_date1_original(date1_header)

                        date.set_month(m2)
                        date.set_year(y2)
                        if file_interval == TimeInterval.DAY:
                            date.set_day(TimeUtil.num_days_in_month(m2, y2))
                        if StateMod_TS.debug:
                            logger.info("Input file end date = " + str(date))
                        ts.set_date2(date)
                        ts.set_date2_original(date2_header)

                    if read_data:
                        if StateMod_TS.debug:
                            logger.debug("Allocating data space")
                        ts.allocate_data_space()

                    if StateMod_TS.debug:
                        logger.debug("Setting data units to " + units)
                    ts.set_data_units(units)
                    ts.set_data_units_original(units)

                    # The input name is the full path to the input file...
                    ts.set_input_name(full_filename)
                    # Set other identifier information. The readTimeSeries() version that
                    # takes a full identifier will reset teh file information because it
                    # knows whether the original filename was from the scenario, etc.
                    ident = TSIdent()
                    if StateMod_TS.debug:
                        logger.debug("Setting ident location to full location: " + str(locid))
                    ident.set_location(full_location=locid)
                    if file_interval == TimeInterval.DAY:
                        ident.set_interval_string("DAY")
                    else:
                        ident.set_interval_string("MONTH")
                    ident.set_input_type("StateMod")
                    ident.set_input_name(full_filename)
                    # Don't have anything else so use the ID
                    ts.set_description(locid)
                    # May be forcing a read if only one time series but only reset the
                    # identifier if the file identifier does match the requested...
                    if ((req_id is not None) and req_id_found and (id.upper() == req_id_upper)) or (req_id is None):
                        # Found the matching ID.
                        if StateMod_TS.debug:
                            logger.debug("Setting ts.identifier to " + str(ident))
                        ts.set_identifier(ident)
                        if StateMod_TS.debug:
                            logger.debug(
                                "Identifier after setting identifier=\"" + str(ts.get_identifier()) + "\" location=" +
                                ts.get_identifier().get_location() + "\"")
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

                if StateMod_TS.debug:
                    logger.debug("Before getting time series from index")

                if current_ts_index >= numts:
                    current_ts_index = 0
                if not req_id_found:
                    # Filling a vector of TS...
                    current_ts = tslist[current_ts_index]
                else:
                    # Filling a single time series...
                    current_ts = req_ts

                if StateMod_TS.debug:
                    logger.debug("Before setting date")

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
                    if standard_ts and (yeartype != YearType.CALENDAR):
                        date.set_year(current_year - 1)
                    else:
                        date.set_year(current_year)
                    # Month is assumed from calendar type - it is assumed that the header
                    # is correct...
                    date.set_month(m1)

                if StateMod_TS.debug:
                    logger.debug("Data date is:  " + str(date))

                if req_date2 is not None:
                    if date.greater_than(req_date2):
                        break

                if StateMod_TS.debug:
                    logger.debug("Before checking read_data")
                if read_data:
                    if file_interval == TimeInterval.DAY:
                        # Need to loop through the proper number of days for the month...
                        ndata_per_line = TimeUtil.num_days_in_month(date.get_month(), date.get_year())
                    for i in range(ndata_per_line):
                        current_ts.set_data_value(date, float(v[i + doffset]))
                        if file_interval == TimeInterval.DAY:
                            date.add_day(1)
                        else:
                            date.add_month(1)
                current_ts_index += 1
                # print("time end: " + str(time.time() - start))
            # end of while(True) to read lines
        except Exception as e:
            message = ("Error reading file near line " + str(line_pos + 1) + " header indicates interval " +
                       file_interval_string + ", period " + str(date1_header) + " to " + str(date2_header) +
                       ", units =\"" + units + "\" line: " + iline)
            logger.warning(message, exc_info=True)
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
            max_years = 500  # Maximum years of data in a time series handled
            year_array = [int()] * max_years
            data_array = [[float()]*13]*max_years
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
                        tsid = id + TSIdent.SEPARATOR + "" + TSIdent.SEPARATOR + "Operation" + TSIdent.SEPARATOR + \
                               "Month" + TSIdent.INPUT_SEPARATOR + "StateMod" + TSIdent.INPUT_SEPARATOR + \
                               full_filename
                        ts = TSUtil.new_time_series(tsid, True)
                        ts.set_identifier(identifier=tsid)
                        year_type = None
                        if first_month.upper() == "JAN":
                            year_type = YearType.CALENDAR
                        if first_month.upper() == "OCT":
                            year_type = YearType.WATER
                        if first_month.upper() == "NOV":
                            year_type = YearType.NOV_TO_OCT
                        else:
                            logger.warning("Do not know how to handle year starting with month " + first_month)
                            return
                        # First set original period using file dates
                        date1 = DateTime(flag=DateTime.PRECISION_MONTH)
                        date1.set_year(year_array[0] + year_type.getStartYearOffset())
                        date1.set_month(year_type.getStartMonth())
                        ts.set_date1_original(date1)
                        date2 = DateTime(flag=DateTime.PRECISION_MONTH)
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
                        date = DateTime(flag=DateTime.PRECISION_MONTH)
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
                            if data_row_count <= max_years:
                                StringUtil.fixed_read2(iline, format, format_w, v)
                                year = int(v[0])
                                year_array[data_row_count - 1] = year
                                if read_data:
                                    for iv in range(14):
                                        data_array[data_row_count - 1][iv - 1] = float(v[iv])
        except Exception as e:
            logger.warning("Error reading time series.", exc_info=True)
            return
        return tslist

    @staticmethod
    def write_time_series_list_props(tslist, props):
        """
        Write time series to a StateMod format file.
        The IOUtil.getPathUsingWorkingDir() method is applied to the filename.
        @param tslist List of time series to write, which must be of the same interval.
        @param props Properties of the output, as described in the following table

        <table width=100% cellpadding=10 cellspacing=0 border=2>
        <tr>
        <td><b>Property</b></td>	<td><b>Description</b></td>	<td><b>Default</b></td>
        </tr>

        <tr>
        <td><b>CalendarType</b></td>
        <td>The type of calendar, either "Water" (Oct through Sep);
        "NovToOct", or "Calendar" (Jan through Dec), consistent with the YearType enumeration.
        </td>
        <td>CalenderYear (but may be made sensitive to the data type or units in the future).</td>
        </tr>

        <tr>
        <td><b>InputFile</b></td>
        <td>Name of input file (or null if no input file).  If specified, the
        file headers of the input file will be transferred to the output file.</td>
        </td>
        <td>null</td>
        </tr>

        <tr>
        <td><b>MissingDataValue</b></td>
        <td>The missing data value to use for output.
        </td>
        <td>-999</td>
        </tr>

        <tr>
        <td><b>NewComments</b></td>
        <td>New comments to add to the header at output.  Set the object in the
        PropList to a String[] (the String value part of the property is ignored).
        </td>
        <td>None</td>
        </tr>

        <tr>
        <td><b>OutputEnd (previously End)</b></td>
        <td>Ending date output (YYYY-MM).
        </td>
        <td>Write all data.</td>
        </tr>

        <tr>
        <td><b>OutputFile</b></td>
        <td>Name of output file to write.  The name can be the same as the input
        file.  This property must be specified.</td>
        </td>
        <td>None - must be specified.</td>
        </tr>

        <tr>
        <td><b>OutputPrecision</b></td>
        <td>Number of digits after the decimal point on output for data values.  If
        positive, the precision is always used.  If negative, then the number of
        digits will be <= the absolute value of the requested precision, with less
        digits to accommodate large numbers.  This allows some flexibility to fit
        large numbers into the standard field widths of StateMod files.
        If PRECISION_FROM_UNITS, then the data units are checked to determine
        the precision, using the negative precision convention.  For example, if the
        units "AF" are to be shown to one digit of precision after the decimal point,
        then -1 would be used for the precision.
        </td>
        <td>2</td>
        </tr>

        <tr>
        <td><b>OutputStart (previously Start)</b></td>
        <td>Starting date for output (YYYY-MM).
        </td>
        <td>Write all data.</td>
        </tr>

        <tr>
        <td><b>PrintGenesis</b></td>
        <td>Indicates whether to print time series creation history (true) or not (false).
        </td>
        <td>false</td>
        </tr>

        </table>
        @throws Exception if there is an error writing the file.
        """
        # Get the calendar type...

        logger = logging.getLogger(__name__)

        prop_value = props.get_value("CalendarType")
        if prop_value is None:
            # Default is calendar year
            prop_value = str(YearType.CALENDAR)
        logger.info("Writing StateMod time series, CalendarType=\"" + prop_value + "\"")
        year_type = YearType.value_of_ignore_case(prop_value)
        if year_type is None:
            # Default is calendar year
            year_type = YearType(YearType.CALENDAR)
        logger.info("Writing StateMod time series, year_type=\"" + str(year_type) + "\"")

        # Get the input file...

        prop_value = props.get_value("InputFile")
        infile = None  # Default
        if prop_value is not None:
            infile = prop_value

        # Get the missing data value...

        missing_dv = -999.0  # Default
        prop_value = props.get_value("MissingDataValue")
        if prop_value is not None:
            missing_dv = float(prop_value)

        # Get the start of the period...

        date1 = None  # Default
        prop_value = props.get_value("OutputStart")
        if prop_value is None:
            prop_value = props.get_value("Start")
            if prop_value is not None:
                logger.warning("StateMod write property Start is obsolete.  Use OutputStart.")
        if prop_value is not None:
            try:
                date1 = DateTime.parse(prop_value.strip())
            except Exception as e:
                logger.warning("Error parsing starting date \"" + prop_value + "\"." + "  Using null.", exc_info=True)
                date1 = None

        # Get the end of the period...

        date2 = None  # Default
        prop_value = props.get_value("OutputEnd")
        if prop_value is None:
            prop_value = props.get_value("End")
            if prop_value is not None:
                logger.warning("StateMod write property End is obsolete.  Use OutputEnd.")
        if prop_value is not None:
            try:
                date2 = DateTime.parse(prop_value.strip())
            except Exception as e:
                logger.warning("Error parsing ending date \"" + prop_value + "\".  Using null.")
                date2 = None

        # Get new comments for the file...

        new_comments = None  # Default
        prop_contents = props.get_contents("NewComments")
        if prop_contents is not None:
            new_comments = prop_contents

        # Get the output file...

        outfile = None  # Default
        prop_value = props.get_value("OutputFile")
        if prop_value is not None:
            outfile = prop_value

        # Get the output precision...

        prop_value = props.get_value("OutputPrecision")
        precision = StateMod_TS.PRECISION_DEFAULT  # Default
        if prop_value is not None:
            precision = int(prop_value)

        # Check to see if should print genesis information...

        prop_value = props.get_value("PrintGenesis")
        print_genesis = "false"  # Default
        if prop_value is not None:
            print_genesis = prop_value
        print_genesis_flag = True
        if print_genesis.upper() == "TRUE":
            print_genesis_flag = True
        else:
            print_genesis_flag = False

        # Process the header from the old file...

        logger.info("Writing new time series to file \"" + str(outfile) + "\" using \"" + str(infile) + "\" header...")

        out = None
        try:
            comment_indicators = ["#"]
            ignored_comment_indicators = ["#>"]
            out = IOUtil.process_file_headers(IOUtil.get_path_using_working_dir(infile),
                                              IOUtil.get_path_using_working_dir(outfile),
                                              new_comments, comment_indicators, ignored_comment_indicators, 0 )
            if out is None:
                logger.warning("Error writing time series to \"" + IOUtil.get_path_using_working_dir(outfile) + "\"")
                raise RuntimeError("Error writing time series to \"" +
                                   IOUtil.get_path_using_working_dir(outfile) + "\"")

            # Now write the new data...
            if StateMod_TS.debug:
                logger.debug("Calling writeTimeSeriesList")
            StateMod_TS.write_time_series_list(out, tslist, date1, date2, year_type, missing_dv,
                                               precision, print_genesis_flag)
        finally:
            if out is not None:
                out.close()

    @staticmethod
    def write_time_series_list(out, tslist, date1, date2, output_year_type, missing_dv, req_precision, print_genesis):
        """
        This method is typically not called directly but is called by others that set up the output file.
        This method writes a file in StateMod format.  It is the lowest-level write
        method.  The dates can each be specified as null, in which case, the
        maximum period of record for all the time series will be used for output.
        Time series with shorter periods will be filled with "MissingDV."
        @param out The PrintWriter to which to write.
        @param tslist A list of time series.
        @param date1 Start of period to write.
        @param date2 End of period to write.
        @param output_year_type output year type
        @param missing_dv Value to be printed when missing values are encountered.
        @param req_precision Requested precision of output (number of digits after the decimal
        point).  The default is generally 2.  This should be set according to the
        datatype in calling routines and is not automatically set here.  The full width
        for time series values is 8 characters and 10 for the total.
        @param print_genesis Specify as true to include time series genesis information
        in the file header, or false to omit from the header.
        @exception Exception if there is an error writing the file.
        """
        # String cmnt	= "#>"; // non-permanent comment string
        # SAM switch to the following when doing genesis output...
        logger = logging.getLogger(__name__)
        debug = True
        nl = "\n"  # Use for all platforms
        cmnt = StateMod_TS.PERMANENT_COMMENT
        # iline  # string for use with StringUtil.formatString
        # annual_sum	 # Used when printing each data item
        annual_count = 0
        year = 0  # A "counter" for the year
        v = []  # Reused below for formatting output
        tsptr = None  # Reference to current time series
        standard_ts = True  # Non-standard indicates 12 monthly average values

        # Verify that the ts vector is not null.  Then count the number of series in list.
        if tslist is None:
            logger.warning("Null time series list")
            return

        nseries = len(tslist)
        # The interval for time series passed to this method.
        # Get from the first non - null time series - later may pass in.
        req_interval_base = TimeInterval.MONTH

        # Determine the interval by checking the time series.  The first
        # interval found will be written later in the code...

        logger.info("Writing " + str(nseries) + " time series using output year type " + str(output_year_type))
        for i in range(nseries):
            if tslist[i] is None:
                continue

            if isinstance(tslist[i], DayTS):
                req_interval_base = TimeInterval.DAY
            elif isinstance(tslist[i], MonthTS):
                req_interval_base = TimeInterval.MONTH
            else:
                iline = "StateMod time series list has time series other than daily or monthly."
                logger.warning(iline)
                raise Exception(iline)
            break

        # Check the intervals to make sure that all the intervals are
        # consistent.  Also, figure out if summary should be total or average.
        # Use the first non-null time series.  Put in a separate loop from
        # above because to make sure that the requested interval is determined first.

        units_found = False
        year_title = "Total"
        # Used to check each time series against the
        # interval for the file, which was determined above
        # interval_base

        output_units = ""  # Output units.
        include_ts = [False]*nseries
        for i in range(nseries):
            include_ts[i] = True
            if tslist[i] is None:
                include_ts[i] = False
                continue
            tsptr = tslist[i]
            # Get the units for output...
            if not units_found:
                output_units = tsptr.get_data_units()
                units_found = True
            # Determine if a monthly_average - check all time series
            # because mixing a monthly average with normal monthly data
            # will result in output starting in year 0.
            if tsptr.get_date1().get_year() == 0:
                standard_ts = False
            interval_base = tsptr.get_data_interval_base()
            if interval_base != req_interval_base:
                include_ts[i] = False
                if req_interval_base == TimeInterval.MONTH:
                    logger.warning("A TS interval other than monthly detected for " + tsptr.get_identifier() +
                                   " - skipping in output.")
                elif req_interval_base == TimeInterval.DAY:
                    logger.warning("A TS interval other than daily detected for " + tsptr.get_identifier() +
                                   " - skipping in output.")

        do_total = True
        if (output_units.upper() == "AF") or (output_units.upper() == "ACFT") or \
           (output_units.upper() == "AF/M") or (output_units.upper() == "IN") or \
           (output_units.upper() == "MM"):
            # Assume only these need to be totaled...
            logger.info("Using total for annual value, based on units \"" + output_units + "\"")
            do_total = True
            year_title = "Total"  # Also used as "month_title" for daily
        else:
            logger.info("Using average for annual value, based on units \"" + output_units + "\"")
            do_total = False
            year_title = "Average"

        # Write comments at the top of the file...

        out.write(cmnt + nl)
        out.write(cmnt + " StateMod time series" + nl)
        out.write(cmnt + " ********************" + nl)
        out.write(cmnt + nl)
        if output_year_type == YearType.WATER:
            out.write(cmnt + " Years Shown = Water Years (Oct to Sep)" + nl)
        elif output_year_type == YearType.NOV_TO_OCT:
            out.write(cmnt + " Years Shown = Irrigation Years (Nov to Oct)" + nl)
        else:
            # if ( output_format.equalsIgnoreCase ("CYR" ))
            out.write(cmnt + " Years Shown = Calendar Years" + nl)
        out.write(cmnt + " The period of record for each time series may vary" + nl)
        out.write(cmnt + " because of the original input and data processing steps." + nl)
        out.write(cmnt + nl)

        # Print each time series id, description, and type...

        out.write(cmnt + "     TS ID                    Type" +
                  "   Source   Units  Period of Record    Location    Description" + nl)

        empty_string = "-"
        # tmpdesc, tmpid, tmplocation, tmpsource, tmptype, tmpunits;
        format = "%s %3d %-24.24s %-6.6s %-8.8s %-6.6s %3.3s/%d - %3.3s/%d %-12.12s%-24.24s"
        # List<String> genesis = null;

        for i in range(nseries):
            tsptr = tslist[i]
            tmpid = tsptr.get_identifier_string()
            if StateMod_TS.debug:
                logger.debug("Processing time series [" + str(i) + "] \"" + tmpid + "\"")
            if len(tmpid) == 0:
                tmpid = empty_string

            tmpdesc = tsptr.get_description()
            if len(tmpdesc) == 0:
                tmpdesc = empty_string

            tmptype = tsptr.get_identifier().get_type()
            if len(tmptype) == 0:
                tmptype = empty_string

            tmpsource = tsptr.get_identifier().get_source()
            if len(tmpsource) == 0:
                tmpsource = empty_string

            tmpunits = tsptr.get_data_units()
            if len(tmpunits) == 0:
                tmpunits = empty_string

            tmplocation = tsptr.get_identifier().get_location()
            if len(tmplocation) == 0:
                tmplocation = empty_string

            v.clear()
            v.append(cmnt)
            v.append((i + 1))
            v.append(tmpid)
            v.append(tmptype)
            v.append(tmpsource)
            v.append(tmpunits)
            v.append(TimeUtil.month_abbreviation(tsptr.get_date1().get_month()))
            v.append(tsptr.get_date1().get_year())
            v.append(TimeUtil.month_abbreviation(tsptr.get_date2().get_month()))
            v.append(tsptr.get_date2().get_year())
            v.append(tmplocation)
            v.append(tmpdesc)
            iline = StringUtil.format_string(v, format)
            out.write(iline + nl)

            # Print the genesis information if requested...

            if print_genesis:
                genesis = tsptr.get_genesis()
                if genesis is not None:
                    size = len(genesis)
                    if size > 0:
                        out.write(cmnt + "      Time series creation history:" + nl)
                        for igen in range(size):
                            out.write( cmnt + "      " + genesis[igen])
        out.write(cmnt + nl)

        # Ready to write to file.  Check for no data, which was not checked
        # before because the comments should be printed even if there is no time series data to print.

        if nseries == 0:
            return

        # Switch to non-permanent comments...

        cmnt = StateMod_TS.NONPERMANENT_COMMENT
        out.write(cmnt + "EndHeader" + nl)
        out.write(cmnt)
        if req_interval_base == TimeInterval.MONTH:
            if output_year_type == YearType.WATER:
                out.write(cmnt + " Yr ID            Oct     Nov     Dec     Jan" +
                          "     Feb     Mar     Apr     May     Jun     Jul" +
                          "     Aug     Sep     " + year_title + nl)
            elif output_year_type == YearType.NOV_TO_OCT:
                out.write(cmnt + " Yr ID            Nov     Dec     Jan     Feb" +
                          "     Mar     Apr     May     Jun     Jul     Aug" +
                          "     Sep     Oct     " + year_title + nl)
            else:
                out.write(cmnt + " Yr ID            Jan" +
                          "     Feb     Mar     Apr     May     Jun     Jul" +
                          "     Aug     Sep     Oct     Nov     Dec     " + year_title + nl)

            out.write(cmnt + "-e-b----------eb------eb------eb------eb------e" +
                      "b------eb------eb------eb------eb------eb------e" +
                      "b------eb------eb--------e" + nl)
        else:
            # Daily output...
            out.write(cmnt + "Yr  Mo ID            d(x,1)  d(x,2)  d(x,3)  " +
                      "d(x,4)  d(x,5)  d(x,6)  d(x,7)  d(x,8)  d(x,9) " +
                      "d(x,10) d(x,11) d(x,12) d(x,13) d(x,14) d(x,15) " +
                      "d(x,16) d(x,17) d(x,18) d(x,19) d(x,20) d(x,21) " +
                      "d(x,22) d(x,23) d(x,24) d(x,25) d(x,26) d(x,27) " +
                      "d(x,28) d(x,29) d(x,30) d(x,31)   " + year_title + nl)

            out.write(cmnt + "--xx--xb----------eb------eb------eb------eb------e" +
                      "b------eb------eb------eb------eb------eb------eb------e" +
                      "b------eb------eb------eb------eb------eb------eb------e" +
                      "b------eb------eb------eb------eb------eb------eb------e" +
                      "b------eb------eb------eb------eb------eb------eb--------e" + nl)

        # Calculate period of record using months since that is the block of
        # time that StateMod operates with...

        month1 = 0
        year1 = 0
        month2 = 0
        year2 = 0
        if date1 is not None:
            month1 = date1.get_month()
            year1 = date1.get_year()
        if date2 is not None:
            month2 = date2.get_month()
            year2 = date2.get_year()
        # Initialize...
        req_date1 = DateTime(flag=DateTime.PRECISION_MONTH)
        req_date2 = DateTime(flag=DateTime.PRECISION_MONTH)
        req_date1.set_month(month1)
        req_date1.set_year(year1)
        req_date2.set_month(month2)
        req_date2.set_year(year2)

        # Define string variables for output;
        # initial_format contains the initial part of each output line
        #   For monthly, either
        #   "year ID3456789012" (monthly) or
        #   "     ID3456789012" (average monthly).
        #   For daily,
        #   "year  mo ID3456789012"
        # iline_format_buffer is created on the fly (it depends on precision and initial_format)
        # These are set in the following section
        # String initial_format;
        year_format = "%4d"  # Only used when formatting total to printed
        month_format = "%4d"  # Only used when formatting total to printed
        id_format = " %-12.12s"  # Only used when formatting total to printed

        # If period of record of interest was not requested, find
        # period of record that covers all time series...
        yeartype = "WYR"
        if standard_ts:
            if (date1 is None) or (date2 is None):
                try:
                    valid_dates = TSUtil.get_period_from_ts(tslist, TSUtil.MAX_POR)
                    if (month1 == 0) or (year1 == 0):
                        req_date1.set_month(valid_dates.get_date1().get_month())
                        req_date1.set_year(valid_dates.get_date1().get_year())
                    if (month2 == 0) or (year2 == 0):
                        req_date2.set_month(valid_dates.get_date2().get_month())
                        req_date2.set_year(valid_dates.get_date2().get_year())
                except Exception as e:
                    logger.warning("Unable to determine output period.")
                    raise Exception("Unable to determine output period.")

            # Set req_date* to the appropriate month if req_date* doesn't
            # agree with output_format (e.g., if "WYR" requested but req_date1 != 10)
            if output_year_type == YearType.WATER:
                while req_date1.get_month() != 10:
                    req_date1.add_month(-1)
                while req_date2.get_month() != 9:
                    req_date2.add_month(1)
                year = req_date1.get_year() + 1
                yeartype = "WYR"
            elif output_year_type == YearType.NOV_TO_OCT:
                while req_date1.get_month() != 11:
                    req_date1.add_month(-1)
                while req_date2.get_month() != 10:
                    req_date2.add_month(1)
                year = req_date1.get_year() + 1
                yeartype = "IYR"
            else:
                # if ( output_format.equalsIgnoreCase ( "CYR" ))
                while req_date1.get_month() != 1:
                    req_date1.add_month(-1)
                while req_date2.get_month() != 12:
                    req_date2.add_month(1)
                year = req_date1.get_year()
                yeartype = "CYR"
            format_header = "   %2d/%4d  -     %2d/%4d%5.5s" + StringUtil.format_string(yeartype, "%5.5s")
            # Format for start of line...
            if req_interval_base == TimeInterval.MONTH:
                initial_format = "%4d %-12.12s"
            else:
                # daily...
                initial_format = "%4d%4d %-12.12s"
        else:
            # Average monthly...
            if output_year_type == YearType.WATER:
                req_date1.set_month(10)
                req_date1.set_year(0)
                req_date2.set_month(9)
                req_date2.set_year(1)
                yeartype = "WYR"
            elif output_year_type == YearType.NOV_TO_OCT:
                req_date1.set_month(11)
                req_date1.set_year(0)
                req_date2.set_month(10)
                req_date2.set_year(1)
                yeartype = "IYR"
            else:
                # if ( output_format.equalsIgnoreCase ( "CYR" ))
                req_date1.set_month(1)
                req_date1.set_year(0)
                req_date2.set_month(12)
                req_date2.set_year(0)
                yeartype = "CYR"
            format_header = "   %2d/   0  -     %2d/   0%5.5s" + StringUtil.format_string(yeartype, "%5.5s")
            initial_format = "     %-12.12s"

        # Write the header line with the period of record...

        # v.clear()
        v = (req_date1.get_month(),)
        if standard_ts:
            t = (req_date1.get_year(),)
            v = (v + t)
        t = (req_date2.get_month(),)
        v = (v + t)
        if standard_ts:
            t = (req_date2.get_year(),)
            v = (v + t)
        t = (output_units,)
        v = (v + t)
        iline = StringUtil.format_string(v, format_header)
        out.write(iline + nl)

        # Write the data...

        # date is the starting date for each line and is incremented once
        # 	each station's time series has been written for that year
        # cdate is a counter for 12 months' worth of data for each station
        logger.info("Writing time series data for " + str(req_date1) + " to " + str(req_date2))
        date = DateTime(flag=DateTime.PRECISION_MONTH)
        cdate = DateTime(flag=DateTime.PRECISION_MONTH)
        date.set_month(req_date1.get_month())
        date.set_year(req_date1.get_year())
        precision = StateMod_TS.PRECISION_DEFAULT
        # List<Object> iline_v = null; // Vector for output lines (objects to be formatted).
        # List<String> iline_format_v = null; // Vector for formats for objects.
        # int	ndays  # Number of days in a month.
        # mon, day, j  # counters
        double_missing_dv = float(missing_dv)

        if req_interval_base == TimeInterval.MONTH:
            iline_v = []  # new Vector<Object>(15,1)
            iline_format_v = []  # new Vector<String>(15,1)
        else:
            # Daily...
            iline_v = []  # new Vector<Object>(36,1)
            iline_format_v = []  # new Vector<String>(36,1)

        # Buffer that is used to format each line...

        iline_format_buffer = ""

        do_sum_to_printed = True  # Current default is for total to sum to printed values, not in-memory

        if req_interval_base == TimeInterval.MONTH:
            # Monthly data file.  Need to output in the calendar for the
            # file, which results in a little juggling of data...
            # Print one year at a time for each time series

            year = year - 1  # Decrement because the loop increments it
            units = ""
            # The basic format for data generally includes a . regardless.
            # However, implementation of the .ifm file for the RGDSS has
            # some huge negative numbers where we don't want the period.
            # Check here for the requested format and set accordingly...
            data_format8 = "%#8."
            data_format10 = "%#10."
            if (req_precision > StateMod_TS.PRECISION_SPECIAL_OFFSET) or \
                    (req_precision*-1 > StateMod_TS.PRECISION_SPECIAL_OFFSET):
                remainder = req_precision % StateMod_TS.PRECISION_SPECIAL_OFFSET
                if remainder < 0:
                    remainder *= -1
                if (remainder & StateMod_TS.PRECISION_NO_DECIMAL_FOR_LARGE) != 0:
                    data_format8 = "%8."
                    data_format10 = "%10."
            # Put together the formats that could be used.  This is faster
            # than reformatting for each number to be written.  Although
            # some will never use, set up the array so that a precision of
            # "i" will be found in array position "i" - this will
            # optimize performance.  These formats are slightly different
            # than the monthly formats - trailing "." is enforced - not sure why?
            format10_for_precision = [None]*11  # new String[11]
            format8_for_precision = [None]*9  # new String[9]
            for i in range(11):
                format10_for_precision[i] = data_format10 + str(i) + "f"
            for i in range(9):
                format8_for_precision[i] = data_format8 + str(i) + "f"
            # Python for loops are not as clean as original Java code
            # for ( ; date.lessThanOrEqualTo(req_date2); date.addMonth(12)):
            first_iteration = True
            while date.less_than_or_equal_to(req_date2):
                if first_iteration:
                    first_iteration = False
                else:
                    # Not the first iteration, increment the date as if it occurred at end of traditional for loop
                    date.add_month(12)
                year = year + 1
                for j in range(nseries):
                    cdate.set_month(date.get_month())
                    cdate.set_year(date.get_year())
                    # First, clear this string out, then append to
                    # it until ready to println to the output file...
                    if not include_ts[j]:
                        continue
                    tsptr = tslist[j]
                    if tsptr.get_data_interval_base() != req_interval_base:
                        # We've already warned user above.
                        continue
                    if req_precision == StateMod_TS.PRECISION_USE_UNITS:
                        # Only get the units if we are going to use them...
                        units = tsptr.get_data_units()
                    annual_sum = 0
                    annual_count = 0
                    iline_v.clear()
                    iline_format_v.clear()
                    iline_format_buffer = initial_format
                    if standard_ts:
                        iline_v.append(year)
                        iline_format_v.append(year_format)
                    iline_v.append(tsptr.get_identifier().get_location())
                    if StateMod_TS.debug:
                        logger.debug("Identifier for output=\"" + str(tsptr.get_identifier()) + "\" location=" +
                                                                      tsptr.get_identifier().get_location() + "\"")
                    iline_format_v.append(id_format)

                    for mon in range(12):
                        value = tsptr.get_data_value(cdate)
                        if req_precision == StateMod_TS.PRECISION_USE_UNITS:
                            precision = StateMod_TS.get_precision_with_units(req_precision, 8, value, units)
                        else:
                            precision = StateMod_TS.get_precision(req_precision, 8, value)
                        iline_format_buffer = iline_format_buffer + format8_for_precision[precision]
                        iline_format_v.append(format8_for_precision[precision])

                        if tsptr.is_data_missing(value):
                            # Missing data so don't add to the annual value.  Print
                            # using the same format as for other data...
                            iline_v.append(double_missing_dv)
                            if StateMod_TS.debug:
                                # Wrap to increase performance...
                                logger.warning("Missing Data Found in TS at " +
                                               cdate.to_string(DateTime.FORMAT_YYYY_MM) + ", printing " + missing_dv)
                        else:
                            annual_sum += value
                            annual_count = annual_count + 1
                            iline_v.append(float(value))
                        cdate.add_month(1)

                    # Add total to output, format and print output line
                    if req_precision == StateMod_TS.PRECISION_USE_UNITS:
                        precision = StateMod_TS.get_precision_with_units(req_precision, 10, annual_sum, units)
                    else:
                        precision = StateMod_TS.get_precision(req_precision, 10, annual_sum)
                    iline_format_buffer = iline_format_buffer + format10_for_precision[precision]
                    # Total value at the end of the line...
                    iline_v.append(StateMod_TS.get_line_total(
                        tsptr, standard_ts, 12, iline_v, iline_format_v, req_interval_base, do_total,
                        annual_sum, annual_count, do_sum_to_printed))
                    if StateMod_TS.debug:
                        logger.debug("Output using format:  " + iline_format_buffer)
                    iline = StringUtil.format_string(iline_v, iline_format_buffer)
                    out.write(iline + nl)
        elif req_interval_base == TimeInterval.DAY:
            # Daily format files.  Because the output is always in calendar
            # date and because counts are slightly different, include separate code,
            # rather than trying to merge with monthly output.
            # The outer loop iterates on months...
            monthly_count = 0
            monthly_sum = 0.0
            # Put together the formats that could be used.  This is faster
            # than reformatting for each number to be written.  Although
            # some will never use, set up the array so that a precision of
            # "i" will be found in array position "i" - this will
            # optimize performance.  These formats are slightly different
            # than the monthly formats - trailing "." is enforced - not sure why?
            format10_for_precision = [None]*11  # new String[11];
            format8_for_precision = [None]*9  # new String[9];
            for i in range(11):
                format10_for_precision[i] = "%#10." + str(i) + "f"
            for i in range(9):
                format8_for_precision[i] = "%#8." + str(i) + "f"
            # Python for loops are not as clean as original Java code
            # for ( ; date.less_than_or_equal_to(req_date2); date.add_month(1)):
            first_iteration = True
            while date.less_than_or_equal_to(req_date2):
                if first_iteration:
                    first_iteration = False
                else:
                    # Not the first iteration, increment the date as if it occurred at end of traditional for loop
                    date.add_month(1)
                for j in range(nseries):
                    # Set the calendar date for daily data...
                    cdate.set_month(date.get_month())
                    cdate.set_year(date.get_year())
                    # First, clear this string out, then append to
                    # it until ready to println to the output file...
                    if not include_ts[j]:
                        continue
                    tsptr = tslist[j]
                    if tsptr.get_data_interval_base() != req_interval_base:
                        # Only output the requested, matching interval.
                        continue
                    monthly_sum = 0
                    monthly_count = 0
                    iline_v.clear()
                    iline_format_v.clear()
                    iline_format_buffer = initial_format
                    iline_v.append(cdate.get_year())
                    iline_format_v.append(year_format)
                    iline_v.append(cdate.get_month())
                    iline_format_v.append(month_format)
                    iline_v.append(tsptr.get_identifier().get_location())
                    iline_format_v.append(id_format)

                    # StateMod daily time series contain 31 values for every month (months containing
                    # fewer than 31 days use 0s as fillers).
                    ndays = TimeUtil.num_days_in_month(cdate.get_month(), cdate.get_year())
                    for day in range(1,32):
                        if day <= ndays:
                            cdate.set_day(day)
                            value = tsptr.get_data_value(cdate)
                        else:
                            # Extra non-existent days up to 31 days...
                            # TODO SAM 2010-02-25 Should this be set to missing?  How does StateMod use it?
                            value = 0.0
                        precision = StateMod_TS.get_precision(req_precision, 8, value)
                        iline_format_buffer = iline_format_buffer + format8_for_precision[precision]
                        iline_format_v.append(format8_for_precision[precision])
                        if tsptr.is_data_missing(value):
                            # Missing data so don't add to the annual value.  Print
                            # using the same format as for other data...
                            iline_v.append(double_missing_dv)
                            if StateMod_TS.debug:
                                # Wrap to increase performance...
                                logger.warning("Missing Data Found in TS at " +
                                               cdate.to_string(DateTime.FORMAT_YYYY_MM_DD) +
                                               ", printing " + missing_dv)
                        else:
                            monthly_sum += value
                            if day <= ndays:
                                # Don't add to the count for days outside actual days.
                                monthly_count = monthly_count + 1
                            iline_v.append(value)

                    # Add total onto format line, format, and print
                    precision = StateMod_TS.get_precision(req_precision, 10, monthly_sum)
                    iline_format_buffer.append(format10_for_precision[precision])
                    # Total value at the end of the line...
                    iline_v.append(StateMod_TS.get_line_total(tsptr, standard_ts, ndays, iline_v, iline_format_v,
                                   req_interval_base, do_total, monthly_sum, monthly_count, do_sum_to_printed))
                    iline = StringUtil.format_string(iline_v, iline_format_buffer)
                    out.write(iline + nl)
        # Do not close the files.  They are closed in the calling routine.
