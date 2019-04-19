# StateMod_Util - Utility functions for StateMod operation

# NoticeStart

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

# ------------------------------------------------------------------------------
# StateMod_Util - Utility functions for StateMod operation
# ------------------------------------------------------------------------------
#  Copyright:	See the COPYRIGHT file.
# ------------------------------------------------------------------------------
#  History:
#
#  2003-07-02	J. Thomas Sapienza, RTi	Initial version.
#  2003-07-30	Steven A. Malers, RTi	* Remove import for
# 					  StateMod_DataSetComponnent.
# 					* Remove static __basinName, which is
# 					  the response file name without the
# 					  .rsp.  StateMod now can take the name
# 					  with or without the .rsp so just pass
# 					  the response file name to the
# 					  runStateMod() method.
# 					* Change runStateModOption() to
# 					  runStateMod() and pass the data set
# 					  to the method.
# 					* Make __statemod_version and
# 					  __statemod_executable private and
# 					  add set/get methods.
# 					* Move remaining static methods from
# 					  StateMod_Data.
# 					* Alphabetize methods.
#  2003-08-21	SAM, RTi		* Add lookupTimeSeries() to simplify
# 					  finding time series for components.
# 					* Add createDataList() to help with
# 					  choices, etc.
#  2003-08-25	SAM, RTi		Add getUpstreamNetworkNodes() from
# 					old SMRiverInfo.retrieveUpstreams().
# 					Change it to return data objects, not
# 					strings.
#  2003-09-11	SAM, RTi		Update due to changes in the river
# 					station component names.
#  2003-09-19	JTS, RTi		Added createCgotoDataList().
#  2003-09-24	SAM, RTi		* Change findEarliestPOR() to
# 					  findEarliestDateInPOR().
#  					* Change findLatestPOR() to
# 					  findLatestDateInPOR().
# 					* Change the above methods to return
# 					  null if no date can be found (e.g.,
# 					  for a new data set).
#  2003-09-29	SAM, RTi		Add formatDataLabel().
#  2003-10-09	JTS, RTi		* Added removeFromVector().
# 					* Added sortStateMod_DataVector().
#  2003-10-10	SAM, RTi		Add estimateDayTS ().
#  2003-10-24	SAM, RTi		Overload runStateMod() to take a
# 					StateMod_DataSet, so the response file
# 					can be determined.
#  2003-10-29	SAM, RTi		* Change estimateDailyTS() to
# 					  createDailyEstimateTS().
# 					* Add createWaterRightTS().
#  2003-11-03	SAM, RTi		Change From_Well parameter to
# 					From_River_By_Well.
#  2003-11-05	SAM, RTi		Got clarification from Ray Bennett on
# 					which parameters should be listed for
# 					output.
#  2003-11-14	SAM, RTi		Ray Bennett provided documentation for
# 					the reservoir and well monthly binary
# 					files as well as all the daily binary
# 					files.  Therefore update the data type
# 					lists, etc.
#  2003-11-29	SAM, RTi		In getTimeSeriesDataTypes(),
# 					automatically turn off input types if
# 					the request is for reservoirs and
# 					the identifier has an account part.
#  2004-06-01	SAM, RTi		Update getTimeSeriesDataTypes() to have
# 					a flag for data groups and use Ray
# 					Bennett feedback for the groups.
#  2004-07-02	SAM, RTi		Add indexOfRiverNodeID().
#  2004-07-06	SAM, RTi		Overload sortStateMod_DataVector() to
# 					allow option of creating new or using
# 					existing data Vector.
#  2004-08-12	JTS, RTi		Added calculateTimeSeriesDifference().
#  2004-08-25	JTS, RTi		Removed the property that defined a
# 					"HelpKey" for the dialog that runs
# 					StateMod.
#  2004-09-07	SAM, RTi		* Reordered some methods to be
# 					  alphabetical.
# 					* Add findWaterRightInsertPosition().
#  2004-09-14	SAM, RTi		For findWaterRightInsertPosition(), just
# 					insert based on the right ID.
#  2004-10-05	SAM, RTi		* Add data type notes as per recent
# 					  documentation (? are removed).
# 					* Add River_Outflow for reservoir
# 					  station output parameters.
#  2005-03-03	SAM, RTi		* Add compareFiles() to help with
# 					  testing.
#  2005-04-01	SAM, RTi		* Add createTotalTimeSeries() method to
# 					  facilitate summarizing information.
#  2005-04-05	SAM, RTi		* Add lookupTimeSeriesGraphTitle() to
# 					  provide default titles based on the
# 					  component type.
#  2005-04-18	JTS, RTi		Added the lookup methods.
#  2005-04-19	JTS, RTi		Removed testDirty().
#  2005-05-06	SAM, RTi		Correct a couple of typos in reservoir
# 					subcomponent IDs in lookupPropValue().
#  2005-08-30	SAM, RTi		Add getTimeSeriesOutputPrecision().
#  2005-10-05	SAM, RTi		Handle well historical pumping time
# 					series in createTotalTS().
#  2005-12-20	SAM, RTi		Add VERSION_XXX and isVersionAtLeast()
# 					to help with binary file format
# 					versions.
#  2006-01-15	SAM, RTi		Overload getTimeSeriesDataTypes() to
# 					take the file name, to facilitate
# 					reading the parameters from the newer
# 					binary files.
#  2006-03-05	SAM, RTi		calculateTimeSeriesDifference() was
# 					resulting in a division by zero, with
# 					infinity values being returned.
#  2006-04-10	SAM, RTi		Add getRightsForStation(), which
# 					extracts rights for an identifier.
#  2006-06-13	SAM, RTi		Add properties for downstream ID for
# 					river network file.
#  2006-08-20	SAM, RTi		Move code to check for edits before
# 					running to StateModGUI_JFrame.
#  2007-04-15	Kurt Tometich, RTi		Added some helper methods that
# 								return validators for data checks.
#  2007-03-01	SAM, RTi		Clean up code based on Eclipse feedback.
# ------------------------------------------------------------------------------
#  EndHeader

class StateMod_Util:
    """
    This class contains utility methods related to a StateMod data set.
    """

    # Strings used when handling free water rights.
    AlwaysOn = "AlwaysOn"
    UseSeniorRightAppropriationDate = "UseSeniorRightAppropriationDate"

    MISSING_STRING = ""
    MISSING_INT = -999
    MISSING_FLOAT = float(-999.0)
    MISSING_DOUBLE = -999.0
    MISSING_DOUBLE_FLOOR = -999.1
    MISSING_DOUBLE_CEILING = -998.9
    MISSING_DATE = None

    # Floating point values indicating binary file versions. These are used by StateMod_BTS and other
    # software to determine appropriate parameters to list.
    VERSION_9_01_DOUBLE = "9.01"
    VERSION_9_69 = "9.69"
    VERSION_11_00 = "11.00"

    # Strings for the station types.  These should be used in displays (e.g., graphing
    # tool) for consistency.  They can also be used to compare GUI values, rather than
    # hard-coding the literal strings.  Make sure that the following lists agree with
    # the StateMod_BTS file - currently the lists are redundant because StateMod_BTS
    # may be used independent of a data set.
    STATION_TYPE_DIVERSION = "Diversion"
    STATION_TYPE_INSTREAM_FLOW = "Instream Flow"
    STATION_TYPE_RESERVOIR = "Reservoir"
    STATION_TYPE_STREAMESTIMATE = "Stream Estimate Station"
    STATION_TYPE_STREAMGAGE = "Stream Gage Station"
    STATION_TYPE_WELL = "Well"

    # Used for looking up properties for data types which do not have separate components.
    COMP_RESERVOIR_AREA_CAP = -102

    # Used by getStationTypes()
    __station_types = [
        STATION_TYPE_DIVERSION,
        STATION_TYPE_INSTREAM_FLOW,
        STATION_TYPE_RESERVOIR,
        STATION_TYPE_STREAMESTIMATE,
        STATION_TYPE_STREAMGAGE,
        STATION_TYPE_WELL
    ]

    # The following arrays list the output time series data types for various station
    # types and various significant versions of StateMod.  These are taken from the
    # StateMod binary data file(s).  Time series should ultimately be read from the
    # following files (the StateMod_BTS class handles):
    # <pre>
    # Diversions      *.B43
    # Reservoirs      *.B44
    # Wells           *.B65
    # StreamGage      *.B43
    # StreamEstimate  *.B43
    # IntreamFlow     *.B43
    # </pre>
    # Use getTimeSeriesDataTypes() to get the list of parameters to use
    # for graphical interfaces, etc.  Important:  the lists are in the order of the
    # StateMod binary file parameters, with no gaps.  If the lists need to be
    # alphabetized, this should be done separately, not by reordering the arrays below.
    # */
    #
    # /**
    # The stream station (stream gage and stream estimate) parameters are written to
    # the *.xdg file by StateMod's -report module.  The raw data are in the *.B43
    # (monthly) binary output file.
    # As per Ray Bennett 2003-11-05 email, all parameters are valid for output.
    # Include a group and remove the group later if necessary.
    __output_ts_data_types_stream_0100 = [
        "Station In/Out - UpstreamInflow",
        "Station In/Out - ReachGain",
        "Station In/Out - ReturnFlow",
        "Station Balance - RiverInflow",
        "Station Balance - RiverDivert",
        "Station Balance - RiverOutflow"
    ]

    __output_ts_data_types_stream_0901 = [
        "Station In/Out - UpstreamInflow",
        "Station In/Out - ReachGain",
        "Station In/Out - ReturnFlow",
        "Station Balance - RiverInflow",
        "Station Balance - RiverDivert",
        "Station Balance - RiverOutflow",
        "Available Flow - AvailableFlow"
    ]

    __output_ts_data_types_stream_0969 = [
        "Demand - Total_Demand",
        "Demand - CU_Demand",
        "Water Supply - From_River_By_Priority",
        "Water Supply - From_River_By_Storage",
        "Water Supply - From_River_By_Exchange",
        "Water Supply - From_River_By_Well",  # Prior to 2003-11-03 was From_Well
        "Water Supply - From_Carrier_By_Priority",
        "Water Supply - From_Carrier_By_Storage",
        "Water Supply - Carried_Water",
        "Water Supply - From_Soil",
        "Water Supply - Total_Supply",
        "Shortage - Total_Short",
        "Shortage - CU_Short",
        "Water Use - Consumptive_Use",
        "Water Use - To_Soil",
        "Water Use - Total_Return",
        "Water Use - Loss",
        "Station In/Out - Upstream_Inflow",
        "Station In/Out - Reach_Gain",
        "Station In/Out - Return_Flow",
        "Station In/Out - Well_Depletion",
        "Station In/Out - To_From_GW_Storage",
        "Station Balance - River_Inflow",
        "Station Balance - River_Divert",
        "Station Balance - River_By_Well",
        "Station Balance - River_Outflow",
        "Available Flow - Available_Flow"
    ]

    # The reservoir station parameters are written to
    # the *.xrg file by StateMod's -report module.  The raw monthly data are in the
    # *.B44 (monthly) binary output file.  The raw daily data are in the
    # *.B50 (daily) binary output file.
    __output_ts_data_types_reservoir_0100 = [
        "General - InitialStorage",
        "Supply From River by - RiverPriority",
        "Supply From River by - RiverStorage",
        "Supply From River by - RiverExchange",
        "Supply From Carrier by - CarrierPriority",
        "Supply From Carrier by - CarrierStorage",
        "Supply From Carrier by - TotalSupply",
        "Water Use from Storage to - StorageUse",
        "Water Use from Storage to - StorageExchange",
        "Water Use from Storage to - CarrierUse",
        "Water Use from Storage to - TotalRelease",
        "Other - Evap",
        "Other - SeepSpill",
        "Other - SimEOM",
        "Other - TargetLimit",
        "Other - FillLimit",
        "Station Balance - Inflow",
        "Station Balance - Outflow"
    ]

    __output_ts_data_types_reservoir_0901 = [
        "General - InitialStorage",
        "Supply From River by - RiverPriority",
        "Supply From River by - RiverStorage",
        "Supply From River by - RiverExchange",
        "Supply From Carrier by - CarrierPriority",
        "Supply From Carrier by - CarrierStorage",
        "Supply From Carrier by - TotalSupply",
        "Water Use from Storage to - StorageUse",
        "Water Use from Storage to - StorageExchange",
        "Water Use from Storage to - CarrierUse",
        "Water Use from Storage to - TotalRelease",
        "Other - Evap",
        "Other - SeepSpill",
        "Other - SimEOM",
        "Other - TargetLimit",
        "Other - FillLimit",
        "Station Balance - RiverInflow",
        "Station Balance - TotalRelease",
        "Station Balance - TotalSupply",
        "Station Balance - RiverByWell",
        "Station Balance - RiverOutflow"
    ]

    __output_ts_data_types_reservoir_0969 = [
        "General - Initial_Storage",
        "Supply From River by - River_Priority",
        "Supply From River by - River_Storage",
        "Supply From River by - River_Exchange",
        "Supply From Carrier by - Carrier_Priority",
        "Supply From Carrier by - Carrier_Storage",
        "Supply From Carrier by - Total_Supply",
        "Water Use from Storage to - Storage_Use",
        "Water Use from Storage to - Storage_Exchange",
        "Water Use from Storage to - Carrier_Use",
        "Water Use from Storage to - Total_Release",
        "Other - Evap",
        "Other - Seep_Spill",
        "Other - Sim_EOM",
        "Other - Target_Limit",
        "Other - Fill_Limit",
        "Station Balance - River_Inflow",
        "Station Balance - Total_Release",
        "Station Balance - Total_Supply",
        "Station Balance - River_By_Well",
        "Station Balance - River_Outflow"
    ]

    # The instream flow station parameters are written to
    # the *.xdg file by StateMod's -report module.  The raw monthly data are in the
    # *.B43 (monthly) binary output file.  The raw daily data are in the *.B49 (daily) binary output file.
    # As per Ray Bennett 2003-11-05 email, all parameters are valid for output.
    __output_ts_data_types_instream_0100 = [
        "Demand - ConsDemand",
        "Water Supply - FromRiverByPriority",
        "Water Supply - FromRiverByStorage",
        "Water Supply - FromRiverByExchange",
        "Water Supply - TotalSupply",
        "Shortage - Short",
        "Water Use - WaterUse,TotalReturn",
        "Station In/Out - UpstreamInflow",
        "Station In/Out - ReachGain",
        "Station In/Out - ReturnFlow",
        "Station Balance - RiverInflow",
        "Station Balance - RiverDivert",
        "Station Balance - RiverOutflow"
    ]

    __output_ts_data_types_instream_0901 = [
        "Demand - ConsDemand",
        "Water Supply - FromRiverByPriority",
        "Water Supply - FromRiverByStorage",
        "Water Supply - FromRiverByExchange",
        "Water Supply - TotalSupply",
        "Shortage - Short",
        "Water Use - WaterUse,TotalReturn",
        "Station In/Out - UpstreamInflow",
        "Station In/Out - ReachGain",
        "Station In/Out - ReturnFlow",
        "Station Balance - RiverInflow",
        "Station Balance - RiverDivert",
        "Station Balance - RiverOutflow",
        "Available Flow - AvailFlow"
    ]

    __output_ts_data_types_instream_0969 = [
        "Demand - Total_Demand",
        "Demand - CU_Demand",
        "Water Supply - From_River_By_Priority",
        "Water Supply - From_River_By_Storage",
        "Water Supply - From_River_By_Exchange",
        "Water Supply - From_River_By_Well",  # Prior to 2003-11-03 was From_Well
        "Water Supply - From_Carrier_By_Priority",
        "Water Supply - From_Carrier_By_Storage",
        "Water Supply - Carried_Water",
        "Water Supply - From_Soil",
        "Water Supply - Total_Supply",
        "Shortage - Total_Short",
        "Shortage - CU_Short",
        "Water Use - Consumptive_Use",
        "Water Use - To_Soil",
        "Water Use - Total_Return",
        "Water Use - Loss",
        "Station In/Out - Upstream_Inflow",
        "Station In/Out - Reach_Gain",
        "Station In/Out - Return_Flow",
        "Station In/Out - Well_Depletion",
        "Station In/Out - To_From_GW_Storage",
        "Station Balance - River_Inflow",
        "Station Balance - River_Divert",
        "Station Balance - River_By_Well",
        "Station Balance - River_Outflow",
        "Available Flow - Available_Flow"
    ]

    # The diversion station parameters are written to
    # the *.xdg file by StateMod's -report module.  The raw data are in the *.B43 (monthly) binary output file.
    # As per Ray Bennett 2003-11-05 email, all parameters are valid for output.
    __output_ts_data_types_diversion_0100 = [
        "Demand - ConsDemand",
        "Water Supply - FromRiverByPriority",
        "Water Supply - FromRiverByStorage",
        "Water Supply - FromRiverByExchange",
        "Water Supply - FromCarrierByPriority",
        "Water Supply - FromCarierByStorage",
        "Water Supply - CarriedWater",
        "Water Supply - TotalSupply",
        "Shortage - Short",
        "Water Use - ConsumptiveWaterUse",
        "Water Use - WaterUse,TotalReturn",
        "Station In/Out - UpstreamInflow",
        "Station In/Out - ReachGain",
        "Station In/Out - ReturnFlow",
        "Station Balance - RiverInflow",
        "Station Balance - RiverDivert",
        "Station Balance - RiverOutflow"
    ]

    __output_ts_data_types_diversion_0901 = [
        "Demand - ConsDemand",
        "Water Supply - FromRiverByPriority",
        "Water Supply - FromRiverByStorage",
        "Water Supply - FromRiverByExchange",
        "Water Supply - FromWell",
        "Water Supply - FromCarrierByPriority",
        "Water Supply - FromCarierByStorage",
        "Water Supply - CarriedWater",
        "Water Supply - TotalSupply",
        "Shortage - Short",
        "Water Use - ConsumptiveWaterUse",
        "Water Use - WaterUse,TotalReturn",
        "Station In/Out - UpstreamInflow",
        "Station In/Out - ReachGain",
        "Station In/Out - ReturnFlow",
        "Station In/Out - WellDepletion",
        "Station In/Out - To/FromGWStorage",
        "Station Balance - RiverInflow",
        "Station Balance - RiverDivert",
        "Station Balance - RiverByWell",
        "Station Balance - RiverOutflow",
        "Available Flow - AvailableFlow"
    ]

    __output_ts_data_types_diversion_0969 = [
        "Demand - Total_Demand",
        "Demand - CU_Demand",
        "Water Supply - From_River_By_Priority",
        "Water Supply - From_River_By_Storage",
        "Water Supply - From_River_By_Exchange",
        "Water Supply - From_River_By_Well",  # Prior to 2003-11-03 was From_Well
        "Water Supply - From_Carrier_By_Priority",
        "Water Supply - From_Carrier_By_Storage",
        "Water Supply - Carried_Water",
        "Water Supply - From_Soil",
        "Water Supply - Total_Supply",
        "Shortage - Total_Short",
        "Shortage - CU_Short",
        "Water Use - Consumptive_Use",
        "Water Use - To_Soil",
        "Water Use - Total_Return",
        "Water Use - Loss",
        "Station In/Out - Upstream_Inflow",
        "Station In/Out - Reach_Gain",
        "Station In/Out - Return_Flow",
        "Station In/Out - Well_Depletion",
        "Station In/Out - To_From_GW_Storage",
        "Station Balance - River_Inflow",
        "Station Balance - River_Divert",
        "Station Balance - River_By_Well",
        "Station Balance - River_Outflow",
        "Available Flow - Available_Flow"
    ]

    # Ray Bennet says not to include these (2003-11-05 email) - they are usefel internally
    # but user should not see.
    # "Divert_For_Instream_Flow",
    # "Divert_For_Power",
    # "Diversion_From_Carrier",
    # "N/A",
    # "Structure Type",
    # "Number of Structures at Node"

    # The well station parameters are written to
    # the *.wdg file by StateMod's -report module.  The raw monthly data are in the
    # *.B42 (monthly) binary output file.  The raw daily data are in the *.B65 (daily)
    # binary output file.
    __output_ts_data_types_well_0901 = [
        "Demand - Demand",
        "Water Supply - FromWell",
        "Water Supply - FromOther",
        "Shortage - Short",
        "Water Use - ConsumptiveUse",
        "Water Use - Return",
        "Water Use - Loss",
        "Water Source - River",
        "Water Source - GWStor",
        "Water Source - Salvage"
    ]

    __output_ts_data_types_well_0969 = [
        "Demand - Total_Demand",
        "Demand - CU_Demand",
        "Water Supply - From_Well",
        "Water Supply - From_SW",
        "Water Supply - From_Soil",
        "Water Supply - Total_Supply",
        "Shortage - Total_Short",
        "Shortage - CU_Short",
        "Water Use - Total_CU",
        "Water Use - To_Soil",
        "Water Use - Total_Return",
        "Water Use - Loss",
        "Water Use - Total_Use",
        "Water Source - From_River",
        "Water Source - To_From_GW_Storage",
        "Water Source - From_Salvage",
        "Water Source - From_Soil",
        "Water Source - Total_Source"
    ]

    # The version of StateMod that is being run as a number (e.g., 11.5).  This is normally set at the
    # beginning of a StateMod GUI session by calling runStateMod ( ... "-version" ).
    # Then its value can be checked with getStateModVersion();
    __statemodVersion = ""

    # The StateMod revision date.  This is normally set at the
    # beginning of a StateMod GUI session by calling runStateMod ( ... "-version" ).
    # Then its value can be checked with getStateModVersion();
    __statemodRevisionDate = "Unknown"

    # The latest known version is returned by getStateModVersionLatest() as a
    # default.  This is used by StateMod_BTS when requesting parameters.
    __statemodVersionLatest = "12.20"

    # The program to use when running StateMod.  If relying on the path, this should just be the
    # program name.  However, a full path can be specified to override the PATH.
    # See the system/StateModGUI.cfg file for configuration properties, which should be used to set
    # the executable as soon as the GUI starts.
    __statemodExecutable = "StateMod"

    # The program to use when running the SmDelta utility program.  If relying on the path, this should just be the
    # program name.  However, a full path can be specified to override the PATH.
    # See the system/StateModGUI.cfg file for configuration properties.
    __smdeltaExecutable = "SmDelta"

    @staticmethod
    def isMissing(i):
        """
        Determine whether an integer value is missing.
        :param i: Integer value to check
        :return: True if the value is missing, False if not.
        """
        if i == StateMod_Util.MISSING_INT:
            return True
        else:
            return False
