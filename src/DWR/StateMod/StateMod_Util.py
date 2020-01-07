# StateMod_Util - Utility functions for StateMod operation

# NoticeStart

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
    # - TODO smalers 2020-01-01 need to evaluate use
    # COMP_RESERVOIR_AREA_CAP = -102

    # Used by getStationTypes()
    station_types = [
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
    output_ts_data_types_stream_0100 = [
        "Station In/Out - UpstreamInflow",
        "Station In/Out - ReachGain",
        "Station In/Out - ReturnFlow",
        "Station Balance - RiverInflow",
        "Station Balance - RiverDivert",
        "Station Balance - RiverOutflow"
    ]

    output_ts_data_types_stream_0901 = [
        "Station In/Out - UpstreamInflow",
        "Station In/Out - ReachGain",
        "Station In/Out - ReturnFlow",
        "Station Balance - RiverInflow",
        "Station Balance - RiverDivert",
        "Station Balance - RiverOutflow",
        "Available Flow - AvailableFlow"
    ]

    output_ts_data_types_stream_0969 = [
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
    output_ts_data_types_reservoir_0100 = [
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

    output_ts_data_types_reservoir_0901 = [
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

    output_ts_data_types_reservoir_0969 = [
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
    output_ts_data_types_instream_0100 = [
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

    output_ts_data_types_instream_0901 = [
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

    output_ts_data_types_instream_0969 = [
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
    output_ts_data_types_diversion_0100 = [
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

    output_ts_data_types_diversion_0901 = [
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

    output_ts_data_types_diversion_0969 = [
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
    output_ts_data_types_well_0901 = [
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

    output_ts_data_types_well_0969 = [
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
    statemod_version = ""

    # The StateMod revision date.  This is normally set at the
    # beginning of a StateMod GUI session by calling runStateMod ( ... "-version" ).
    # Then its value can be checked with getStateModVersion();
    statemod_revision_date = "Unknown"

    # The latest known version is returned by getStateModVersionLatest() as a
    # default.  This is used by StateMod_BTS when requesting parameters.
    statemod_version_latest = "12.20"

    # The program to use when running StateMod.  If relying on the path, this should just be the
    # program name.  However, a full path can be specified to override the PATH.
    # See the system/StateModGUI.cfg file for configuration properties, which should be used to set
    # the executable as soon as the GUI starts.
    statemod_executable = "StateMod"

    # The program to use when running the SmDelta utility program.  If relying on the path, this should just be the
    # program name.  However, a full path can be specified to override the PATH.
    # See the system/StateModGUI.cfg file for configuration properties.
    smdelta_executable = "SmDelta"

    @staticmethod
    def is_missing(i):
        """
        Determine whether an integer value is missing.
        :param i: Integer value to check
        :return: True if the value is missing, False if not.
        """
        if i == StateMod_Util.MISSING_INT:
            return True
        else:
            return False
