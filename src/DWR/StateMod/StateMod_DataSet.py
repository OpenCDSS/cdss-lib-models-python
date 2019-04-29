# StateMod_DataSet - this class manages data components in a StateMod data set

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

import logging
import os

from RTi.Util.IO.DataSet import DataSet
from RTi.Util.IO.DataSetComponent import DataSetComponent
from RTi.Util.IO.IOUtil import IOUtil
from RTi.Util.IO.PropList import PropList
from RTi.Util.Time.StopWatch import StopWatch
from RTi.Util.Time.TimeInterval import TimeInterval
from DWR.StateMod.StateMod_Data import StateMod_Data
from DWR.StateMod.StateMod_Diversion import StateMod_Diversion
from DWR.StateMod.StateMod_DiversionRight import StateMod_DiversionRight
from DWR.StateMod.StateMod_RiverNetworkNode import StateMod_RiverNetworkNode
from DWR.StateMod.StateMod_StreamGage import StateMod_StreamGage
from DWR.StateMod.StateMod_TS import StateMod_TS
from DWR.StateMod.StateMod_Util import StateMod_Util


class StateMod_DataSet(DataSet):
    """
    This StateMod_DataSet class manages data components in a StateMod data set,
    essentially managing the list of components from the response file.
    Typically, each component corresponds to a file.  A list of components is
    maintained and is displayed by StateMod_DataSetManager.  The known issues with the class are:

    * The stream gage/estimate station migration is not complete.  Data sets typically still use *ris
    rather than the separate files for gage and estimate stations.</li>
    * The separate list files for subsets of station data (e.g., efficiencies) has not been implemented.</li>
    """

    # String indicating blank file name - allowed to be a duplicate
    BLANK_FILE_NAME = ""

    # Appened to some daily time series data types to indicate an estimated time series.
    __ESTIMATED = "Estimated"

    # The StateMod data set type is unknown.
    TYPE_UNKNOWN = 0
    NAME_UNKNOWN = "Unknown"

    # Use for initialization, if needed.
    COMP_UNKNOWN = -1
    # Used when defining other nodes in the network, via the GUI.
    COMP_OTHER_NODE = -5

    # The following should be sequential from 0 because they have lookup position in DataSet arrays.
    #
    # Some of the following values are for sub-components (e.g., delay table assignments for diversions).
    # These are typically one-to-many data items that are managed with a component but may need to be displayed
    # separately. The sub-components have numbers that are the main component*100 + N. These values are
    # checked in methods like lookupComponentName() but do not have sequential arrays.
    COMP_CONTROL_GROUP = 0
    COMP_RESPONSE = 1
    COMP_CONTROL = 2
    COMP_OUTPUT_REQUEST = 3
    COMP_REACH_DATA = 4

    COMP_CONSUMPTIVE_USE_GROUP = 5
    COMP_STATECU_STRUCTURE = 6
    COMP_IRRIGATION_PRACTICE_TS_YEARLY = 7
    COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY = 8
    COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY = 9

    COMP_STREAMGAGE_GROUP = 10
    COMP_STREAMGAGE_STATIONS = 11
    COMP_STREAMGAGE_HISTORICAL_TS_MONTHLY = 12
    COMP_STREAMGAGE_HISTORICAL_TS_DAILY = 13
    COMP_STREAMGAGE_NATURAL_FLOW_TS_MONTHLY = 14
    COMP_STREAMGAGE_NATURAL_FLOW_TS_DAILY = 15

    COMP_DELAY_TABLE_MONTHLY_GROUP = 16
    COMP_DELAY_TABLES_MONTHLY = 17

    COMP_DELAY_TABLE_DAILY_GROUP = 18
    COMP_DELAY_TABLES_DAILY = 19

    COMP_DIVERSION_GROUP = 20
    COMP_DIVERSION_STATIONS = 21
    COMP_DIVERSION_STATION_DELAY_TABLES = 2101
    COMP_DIVERSION_STATION_COLLECTIONS = 2102
    COMP_DIVERSION_RIGHTS = 22
    COMP_DIVERSION_TS_MONTHLY = 23
    COMP_DIVERSION_TS_DAILY = 24
    COMP_DEMAND_TS_MONTHLY = 25
    COMP_DEMAND_TS_OVERRIDE_MONTHLY = 26
    COMP_DEMAND_TS_AVERAGE_MONTHLY = 27
    COMP_DEMAND_TS_DAILY = 28

    COMP_PRECIPITATION_GROUP = 29
    COMP_PRECIPITATION_TS_MONTHLY = 30
    COMP_PRECIPITATION_TS_YEARLY = 31

    COMP_EVAPORATION_GROUP = 32
    COMP_EVAPORATION_TS_MONTHLY = 33
    COMP_EVAPORATION_TS_YEARLY = 34

    COMP_RESERVOIR_GROUP = 35
    COMP_RESERVOIR_STATIONS = 36
    COMP_RESERVOIR_STATION_ACCOUNTS = 3601
    COMP_RESERVOIR_STATION_PRECIP_STATIONS = 3602
    COMP_RESERVOIR_STATION_EVAP_STATIONS = 3603
    COMP_RESERVOIR_STATION_CURVE = 3604
    COMP_RESERVOIR_STATION_COLLECTIONS = 3605
    COMP_RESERVOIR_RIGHTS = 37
    COMP_RESERVOIR_CONTENT_TS_MONTHLY = 38
    COMP_RESERVOIR_CONTENT_TS_DAILY = 39
    COMP_RESERVOIR_TARGET_TS_MONTHLY = 40
    COMP_RESERVOIR_TARGET_TS_DAILY = 41
    COMP_RESERVOIR_RETURN = 42

    COMP_INSTREAM_GROUP = 43
    COMP_INSTREAM_STATIONS = 44
    COMP_INSTREAM_RIGHTS = 45
    COMP_INSTREAM_DEMAND_TS_MONTHLY = 46
    COMP_INSTREAM_DEMAND_TS_AVERAGE_MONTHLY = 47
    COMP_INSTREAM_DEMAND_TS_DAILY = 48

    COMP_WELL_GROUP = 49
    COMP_WELL_STATIONS = 50
    COMP_WELL_STATION_DELAY_TABLES = 5001
    COMP_WELL_STATION_DEPLETION_TABLES = 5002
    COMP_WELL_STATION_COLLECTIONS = 5003
    COMP_WELL_RIGHTS = 51
    COMP_WELL_PUMPING_TS_MONTHLY = 52
    COMP_WELL_PUMPING_TS_DAILY = 53
    COMP_WELL_DEMAND_TS_MONTHLY = 54
    COMP_WELL_DEMAND_TS_DAILY = 55

    COMP_PLAN_GROUP = 56
    COMP_PLANS = 57
    COMP_PLAN_WELL_AUGMENTATION = 58
    COMP_PLAN_RETURN = 59

    COMP_STREAMESTIMATE_GROUP = 60
    COMP_STREAMESTIMATE_STATIONS = 61
    COMP_STREAMESTIMATE_COEFFICIENTS = 62
    COMP_STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY = 63
    COMP_STREAMESTIMATE_NATURAL_FLOW_TS_DAILY = 64

    COMP_RIVER_NETWORK_GROUP = 65
    COMP_RIVER_NETWORK = 66
    COMP_NETWORK = 67

    COMP_OPERATION_GROUP = 68
    COMP_OPERATION_RIGHTS = 69
    COMP_DOWNSTREAM_CALL_TS_DAILY = 70
    COMP_SANJUAN_RIP = 71
    COMP_RIO_GRANDE_SPILL = 72

    COMP_GEOVIEW_GROUP = 73
    COMP_GEOVIEW = 74

    # The data set component names, including the component groups. Subcomponent
    # names are defined after this array and are currently treated as special cases.
    __component_names = [
        "Control Data",
        "Response",
        "Control",
        "Output Request",
        "Reach Data",

        "Consumptive Use Data",
        "StateCU Structure",  # *.par (SoilMoisture) is no longer supported - both have AWC
        "Irrigation Practice TS (Yearly)",
        "Consumptive Water Requirement TS (Monthly)",
        "Consumptive Water Requirement TS (Daily)",

        "Stream Gage Data",
        "Stream Gage Stations",
        "Stream Gage Historical TS (Monthly)",
        "Stream Gage Historical TS (Daily)",
        "Stream Gage Natural Flow TS (Monthly)",
        "Stream Gage Natural Flow TS (Daily)",

        "Delay Table (Monthly) Data",
        "Delay Tables (Monthly)",

        "Delay Table (Daily) Data",
        "Delay Tables (Daily)",

        "Diversion Data",
        "Diversion Stations",
        "Diversion Rights",
        "Diversion Historical TS (Monthly)",
        "Diversion Historical TS (Daily)",
        "Diversion Demand TS (Monthly)",
        "Diversion Demand TS Override (Monthly)",
        "Diversion Demand TS (Average Monthly)",
        "Diversion Demand TS (Daily)",

        "Precipitation Data",
        "Precipitation Time Series (Monthly)",
        "Precipitation Time Series (Yearly)",

        "Evaporation Data",
        "Evaporation Time Series (Monthly)",
        "Evaporation Time Series (Yearly)",

        "Reservoir Data",
        "Reservoir Stations",
        "Reservoir Rights",
        "Reservoir Content TS, End of Month (Monthly)",
        "Reservoir Content TS, End of Day (Daily)",
        "Reservoir Target TS (Monthly)",
        "Reservoir Target TS (Daily)",
        "Reservoir Return Flows",

        "Instream Flow Data",
        "Instream Flow Stations",
        "Instream Flow Rights",
        "Instream Flow Demand TS (Monthly)",
        "Instream Flow Demand TS (Average Monthly)",
        "Instream Flow Demand TS (Daily)",

        "Well Data",
        "Well Stations",
        "Well Rights",
        "Well Historical Pumping TS (Monthly)",
        "Well Historical Pumping TS (Daily)",
        "Well Demand TS (Monthly)",
        "Well Demand TS (Daily)",

        "Plan Data",
        "Plans",
        "Plan Well Augmentation Data",
        "Plan Return Flows",

        "Stream Estimate Data",
        "Stream Estimate Stations",
        "Stream Estimate Coefficients",
        "Stream Estimate Natural Flow TS (Monthly)",
        "Stream Estimate Natural Flow TS (Daily)",

        "River Network Data",
        "River Network",
        "Network (Graphical)",  # RTi version (behind the scenes)

        "Operational Data",
        "Operational Rights",
        "Downstream Call Time Series (Daily)",
        "San Juan Sediment Recovery Plan",
        "Rio Grande Spill (Monthly)",

        "Spatial Data",
        "GeoView Project"
    ]

    # Subcomponent names used with lookupComponenetName(). These are special cases for labels
    # and displays but the data are managed with a component listed above. Make private to force
    # handling through lookup methods.
    __COMPNAME_DIVERSION_STATION_DELAY_TABLES = "Diversion Station Delay Table Assignment"
    __COMPNAME_DIVERSION_STATION_COLLECTIONS = "Diversion Station Collection Definitions"
    __COMPNAME_RESERVOIR_STATION_ACCOUNTS = "Reservoir Station Accounts"
    __COMPNAME_RESERVOIR_STATION_PRECIP_STATIONS = "Reservoir Station Precipitation Stations"
    __COMPNAME_RESERVOIR_STATION_EVAP_STATIONS = "Reservoir Station Evaporation Stations"
    __COMPNAME_RESERVOIR_STATION_CURVE = "Reservoir Station Content/Area/Seepage"
    __COMPNAME_RESERVOIR_STATION_COLLECTIONS = "Reservoir Station Collection Definitions"
    __COMPNAME_WELL_STATION_DELAY_TABLES = "Well Station Delay Table Assignment"
    __COMPNAME_WELL_STATION_DEPLETION_TABLES = "Well Station Depletion Table Assignment"
    __COMPNAME_WELL_STATION_COLLECTIONS = "Well Station Collection Definitions"

    # List of all the components, by number (type).
    __component_types = [
        COMP_CONTROL_GROUP,
        COMP_RESPONSE,
        COMP_CONTROL,
        COMP_OUTPUT_REQUEST,
        COMP_REACH_DATA,

        COMP_CONSUMPTIVE_USE_GROUP,
        COMP_STATECU_STRUCTURE,
        COMP_IRRIGATION_PRACTICE_TS_YEARLY,
        COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY,
        COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY,

        COMP_STREAMGAGE_GROUP,
        COMP_STREAMGAGE_STATIONS,
        COMP_STREAMGAGE_HISTORICAL_TS_MONTHLY,
        COMP_STREAMGAGE_HISTORICAL_TS_DAILY,
        COMP_STREAMGAGE_NATURAL_FLOW_TS_MONTHLY,
        COMP_STREAMGAGE_NATURAL_FLOW_TS_DAILY,

        COMP_DELAY_TABLE_MONTHLY_GROUP,
        COMP_DELAY_TABLES_MONTHLY,

        COMP_DELAY_TABLE_DAILY_GROUP,
        COMP_DELAY_TABLES_DAILY,

        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_STATIONS,
        COMP_DIVERSION_RIGHTS,
        COMP_DIVERSION_TS_MONTHLY,
        COMP_DIVERSION_TS_DAILY,
        COMP_DEMAND_TS_MONTHLY,
        COMP_DEMAND_TS_OVERRIDE_MONTHLY,
        COMP_DEMAND_TS_AVERAGE_MONTHLY,
        COMP_DEMAND_TS_DAILY,

        COMP_PRECIPITATION_GROUP,
        COMP_PRECIPITATION_TS_MONTHLY,
        COMP_PRECIPITATION_TS_YEARLY,

        COMP_EVAPORATION_GROUP,
        COMP_EVAPORATION_TS_MONTHLY,
        COMP_EVAPORATION_TS_YEARLY,

        COMP_RESERVOIR_GROUP,
        COMP_RESERVOIR_STATIONS,
        COMP_RESERVOIR_RIGHTS,
        COMP_RESERVOIR_CONTENT_TS_MONTHLY,
        COMP_RESERVOIR_CONTENT_TS_DAILY,
        COMP_RESERVOIR_TARGET_TS_MONTHLY,
        COMP_RESERVOIR_TARGET_TS_DAILY,
        COMP_RESERVOIR_RETURN,

        COMP_INSTREAM_GROUP,
        COMP_INSTREAM_STATIONS,
        COMP_INSTREAM_RIGHTS,
        COMP_INSTREAM_DEMAND_TS_MONTHLY,
        COMP_INSTREAM_DEMAND_TS_AVERAGE_MONTHLY,
        COMP_INSTREAM_DEMAND_TS_DAILY,

        COMP_WELL_GROUP,
        COMP_WELL_STATIONS,
        COMP_WELL_RIGHTS,
        COMP_WELL_PUMPING_TS_MONTHLY,
        COMP_WELL_PUMPING_TS_DAILY,
        COMP_WELL_DEMAND_TS_MONTHLY,
        COMP_WELL_DEMAND_TS_DAILY,

        COMP_PLAN_GROUP,
        COMP_PLANS,
        COMP_PLAN_WELL_AUGMENTATION,
        COMP_PLAN_RETURN,

        COMP_STREAMESTIMATE_GROUP,
        COMP_STREAMESTIMATE_STATIONS,
        COMP_STREAMESTIMATE_COEFFICIENTS,
        COMP_STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY,
        COMP_STREAMESTIMATE_NATURAL_FLOW_TS_DAILY,

        COMP_RIVER_NETWORK_GROUP,
        COMP_RIVER_NETWORK,
        COMP_NETWORK,

        COMP_OPERATION_GROUP,
        COMP_OPERATION_RIGHTS,
        COMP_DOWNSTREAM_CALL_TS_DAILY,
        COMP_SANJUAN_RIP,
        COMP_RIO_GRANDE_SPILL,

        COMP_GEOVIEW_GROUP,
        COMP_GEOVIEW
    ]

    # This array indicates the default file extension to use with each component.
    # These extensions can be used in file choosers.
    __component_file_extensions = [
        "Control Group",
        "rsp",
        "ctl",
        "out",
        "rch",

        "Consumptive Use Group",
        "str",  # Do not support *.par
        "ipy",
        "iwr",
        "iwd",

        "Stream Gage Group",
        "ris",
        "rih",
        "riy",
        "rim",
        "rid",

        "Delay Tables (Monthly) Group",
        "dly",

        "Delay Tables (Daily) Group",
        "dld",

        "Diversion Group",
        "dds",
        "ddr",
        "ddh",
        "ddy",
        "ddm",
        "ddo",
        "dda",
        "ddd",

        "Precipitation Group",
        "pre",
        "pra",

        "Evaporation Group",
        "evm",
        "eva",

        "Reservoir Group",
        "res",
        "rer",
        "eom",
        "eoy",
        "tar",
        "tad",
        "rrf",

        "Instream Group",
        "ifs",
        "ifr",
        "ifm",
        "ifa",
        "ifd",

        "Well Group",
        "wes",
        "wer",
        "weh",
        "wey",
        "wem",
        "wed",

        "Plan Group",
        "pln",
        "plw",
        "prf",

        "StreamEstimate Group",
        "ses",
        "rib",
        "rim",  # Note: shared with StreamGage
        "rid",  # Note: shared with StreamGage

        "River Network Group",
        "rin",
        "net",

        "Operation Group",
        "opr",
        "cal",  # Call time series.
        "sjr",  # San Juan sedimentation
        "rgs",  # Rio Grande spill

        "GeoView Group",
        "gvp"
    ]

    __statemod_file_properties = [
        "",  # "Control Data",
        "Response",
        "Control",
        "OutputRequest",
        "Reach_Data",

        "",  # "Consumptive Use Data",
        "StateCU_Structure",  # "SoilMoisture" (*.par) no longer supported
        "IrrigationPractice_Yearly",
        "ConsumptiveWaterRequirement_Monthly",
        "ConsumptiveWaterRequirement_Daily",

        "",  # "Stream Gage Data",
        "StreamGage_Station",
        "StreamGage_Historic_Monthly",
        "StreamGage_Historic_Daily",
        "Stream_Base_Monthly",
        "Stream_Base_Daily",

        "",  # "Delay Tables (Monthly) Data",
        "DelayTable_Monthly",

        "",  # "Delay Tables (Daily) Data",
        "DelayTabe_Daily",

        "",  # "Diversion Data",
        "Diversion_Station",
        "Diversion_Right",
        "Diversion_Historic_Monthly",
        "Diversion_Historic_Daily",
        "Diversion_Demand_Monthly",
        "Diversion_DemandOverride_Monthly",
        "Diversion_Demand_AverageMonthly",
        "Diversion_Demand_Daily",

        "",  # "Precipitation Data",
        "Precipitation_Monthly",
        "Precipitation_Annual",

        "",  # "Evaporation Data",
        "Evaporation_Monthly",
        "Evaporation_Annual",

        "",  # "Reservoir Data",
        "Reservoir_Station",
        "Reservoir_Right",
        "Reservoir_Historic_Monthly",
        "Reservoir_Historic_Daily",
        "Reservoir_Target_Monthly",
        "Reservoir_Target_Daily",
        "Reservoir_Return",

        "",  # "Instream Flow Data",
        "Instreamflow_Station",
        "Instreamflow_Right",
        "Instreamflow_Demand_Monthly",
        "Instreamflow_Demand_AverageMonthly",
        "Instreamflow_Demand_Daily",

        "",  # "Well Data",
        "Well_Station",
        "Well_Right",
        "Well_Historic_Monthly",
        "Well_Historic_Daily",
        "Well_Demand_Monthly",
        "Well_Demand_Daily",

        "",  # "Plan Data",
        "Plan_Data",
        "Plan_Wells",
        "Plan_Return",

        "",  # "Stream (Estimated) Data",
        "StreamEstimate_Station",
        "StreamEstimate_Coefficients",
        "Stream_Base_Monthly",  # Note:  Shared with StreamGage
        "Stream_Base_Daily",  # Note: shared with StreamGage

        "",  # "River Network Data",
        "River_Network",
        "Network",

        "",  # "Operational Rights Data",
        "Operational_Right",
        "Downstream_Call",
        "SanJuanRecovery",
        "RioGrande_Spill_Monthly",

        "",  # "Geographic Data",
        "GeographicInformation"
    ]

    # Array indicating which components are groups.
    __component_groups = [
        COMP_CONTROL_GROUP,
        COMP_CONSUMPTIVE_USE_GROUP,
        COMP_STREAMGAGE_GROUP,
        COMP_DELAY_TABLE_MONTHLY_GROUP,
        COMP_DELAY_TABLE_DAILY_GROUP,
        COMP_DIVERSION_GROUP,
        COMP_PRECIPITATION_GROUP,
        COMP_EVAPORATION_GROUP,
        COMP_RESERVOIR_GROUP,
        COMP_INSTREAM_GROUP,
        COMP_WELL_GROUP,
        COMP_PLAN_GROUP,
        COMP_STREAMESTIMATE_GROUP,
        COMP_RIVER_NETWORK_GROUP,
        COMP_OPERATION_GROUP,
        COMP_GEOVIEW_GROUP
    ]

    # Array indicating the primary components within each component group. The primary components are used to
    # get the list of identifiers for displays and processing. The number of values should agree with the list
    # above.
    __component_group_primaries = [
        COMP_RESPONSE,  # COMP_CONTROL_GROUP
        COMP_STATECU_STRUCTURE,  # COMP_CONSUMPTIVE_USE_GROUP
        COMP_STREAMGAGE_STATIONS,  # COMP_STREAMGAGE_GROUP
        COMP_DELAY_TABLES_MONTHLY,  # COMP_DELAY_TABLES_MONTHLY_GROUP
        COMP_DELAY_TABLES_DAILY,  # COMP_DELAY_TABLES_DAILY_GROUP
        COMP_DIVERSION_STATIONS,  # COMP_DIVERSION_GROUP
        COMP_PRECIPITATION_TS_MONTHLY,  # COMP_PRECIPITATION_GROUP
        COMP_EVAPORATION_TS_MONTHLY,  # COMP_EVAPORATION_GROUP
        COMP_RESERVOIR_STATIONS,  # COMP_RESERVOIR_GROUP
        COMP_INSTREAM_STATIONS,  # COMP_INSTREAM_GROUP
        COMP_WELL_STATIONS,  # COMP_WELL_GROUP
        COMP_PLANS,  # COMP_PLAN_GROUP
        COMP_STREAMESTIMATE_STATIONS,  # COMP_STREAMESTIMATE_GROUP
        COMP_RIVER_NETWORK,  # COMP_RIVER_NETWORK_GROUP
        COMP_OPERATION_RIGHTS,  # COMP_OPERATION_GROUP
        COMP_GEOVIEW  # COMP_GEOVIEW_GROUP
    ]

    # Array indicating the groups for each component.
    __component_group_assignments = [
        COMP_CONTROL_GROUP,
        COMP_CONTROL_GROUP,
        COMP_CONTROL_GROUP,
        COMP_CONTROL_GROUP,
        COMP_CONTROL_GROUP,

        COMP_CONSUMPTIVE_USE_GROUP,
        COMP_CONSUMPTIVE_USE_GROUP,
        COMP_CONSUMPTIVE_USE_GROUP,
        COMP_CONSUMPTIVE_USE_GROUP,
        COMP_CONSUMPTIVE_USE_GROUP,

        COMP_STREAMGAGE_GROUP,
        COMP_STREAMGAGE_GROUP,
        COMP_STREAMGAGE_GROUP,
        COMP_STREAMGAGE_GROUP,
        COMP_STREAMGAGE_GROUP,
        COMP_STREAMGAGE_GROUP,

        COMP_DELAY_TABLE_MONTHLY_GROUP,
        COMP_DELAY_TABLE_MONTHLY_GROUP,

        COMP_DELAY_TABLE_DAILY_GROUP,
        COMP_DELAY_TABLE_DAILY_GROUP,

        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_GROUP,
        COMP_DIVERSION_GROUP,

        COMP_PRECIPITATION_GROUP,
        COMP_PRECIPITATION_GROUP,
        COMP_PRECIPITATION_GROUP,

        COMP_EVAPORATION_GROUP,
        COMP_EVAPORATION_GROUP,
        COMP_EVAPORATION_GROUP,

        COMP_RESERVOIR_GROUP,
        COMP_RESERVOIR_GROUP,
        COMP_RESERVOIR_GROUP,
        COMP_RESERVOIR_GROUP,
        COMP_RESERVOIR_GROUP,
        COMP_RESERVOIR_GROUP,
        COMP_RESERVOIR_GROUP,
        COMP_RESERVOIR_GROUP,

        COMP_INSTREAM_GROUP,
        COMP_INSTREAM_GROUP,
        COMP_INSTREAM_GROUP,
        COMP_INSTREAM_GROUP,
        COMP_INSTREAM_GROUP,
        COMP_INSTREAM_GROUP,

        COMP_WELL_GROUP,
        COMP_WELL_GROUP,
        COMP_WELL_GROUP,
        COMP_WELL_GROUP,
        COMP_WELL_GROUP,
        COMP_WELL_GROUP,
        COMP_WELL_GROUP,

        COMP_PLAN_GROUP,
        COMP_PLAN_GROUP,
        COMP_PLAN_GROUP,
        COMP_PLAN_GROUP,

        COMP_STREAMESTIMATE_GROUP,
        COMP_STREAMESTIMATE_GROUP,
        COMP_STREAMESTIMATE_GROUP,
        COMP_STREAMESTIMATE_GROUP,
        COMP_STREAMESTIMATE_GROUP,

        COMP_RIVER_NETWORK_GROUP,
        COMP_RIVER_NETWORK_GROUP,
        COMP_RIVER_NETWORK_GROUP,

        COMP_OPERATION_GROUP,
        COMP_OPERATION_GROUP,
        COMP_OPERATION_GROUP,
        COMP_OPERATION_GROUP,
        COMP_OPERATION_GROUP,

        COMP_GEOVIEW_GROUP,
        COMP_GEOVIEW_GROUP
    ]

    # The following array assigns the time series data types for use with time series.
    # For example, StateMod data sets do not contain a data type and therefore after
    # reading the file, the time series data type must be assumed. If the data component
    # is known (e.g., because reading from a response file), then the following array
    # can be used to look up the data type for the time series. Components that are not
    # time series have blank strings for data types.
    __component_ts_data_types = [
        "",  # "Control Data",
        "",  # "Response",
        "",  # "Control",
        "",  # "Output Request",
        "",  # "Reach Data",

        "",  # "Consumptive Use Data",
        "",  # "StateCU Structure",
        "",  # "Irrigation Practice TS (Yearly)" - units vary because multiple time series in one file,
        "CWR",  # "Consumptive Water Requirement (Monthly)",
        "CWR",  # "Consumptive Water Requirement (Daily)",

        "",  # "Stream Gage Data",
        "",  # "Stream Gage Stations",
        "FlowHist",
        "FlowHist",
        "FlowNatural",
        "FlowNatural",

        "",  # "Delay Table (Monthly) Data",
        "",  # "Delay Tables (Monthly)",

        "",  # "Delay Table (Daily) Data",
        "",  # "Delay Tables (Daily)",

        "",  # "Diversion Data",
        "",  # "Diversion Stations",
        "TotalWaterRights",  # "Diversion Rights",
        "DiversionHist",  # "Diversion Historical TS (Monthly)",
        "DiversionHist",  # "Diversion Historical TS (Daily)",
        "Demand",  # Demand TS (Monthly)",
        "DemandOverride",
        "DemandAverage",
        "Demand",

        "",  # "Precipitation Data",
        "Precipitation",  # "Precipitation Time Series (Monthly)",
        "Precipitation",  # "Precipitation Time Series (Yearly)",

        "",  # "Evaporation Data",
        "Evaporation",  # "Evaporation Time Series (Monthly)",
        "Evaporation",  # "Evaporation Time Series (Yearly)",

        "",  # "Reservoir Data",
        "",  # "Reservoir Stations",
        "TotalWaterRights",  # "Reservoir Rights",
        "ContentEOMHist",  # "Content, End of Month (Monthly)",
        "ContentEODHist",  # "Content, End of Day (Daily)",
        "Target",  # "Reservoir Targets (Monthly)",
        "Target",  # "Reservoir Targets (Daily)",
        # "Min" and "Max" must be appended since the target always go in pairs
        "",  # Returns

        "",  # "Instream Flow Data",
        "",  # "Instream Flow Stations",
        "TotalWaterRights",  # "Instream Flow Rights",
        "Demand",  # "Demand (Monthly)",
        "DemandAverage",  # "Demand (Average Monthly)",
        "Demand",  # "Demand (Daily)",

        "",  # "Well Data",
        "",  # "Well Stations",
        "TotalWaterRights",  # "Well Rights",
        "PumpingHist",  # "Well Historical Pumping (Monthly)",
        "PumpingHist",  # "Well Historical Pumping (Daily)",
        "Demand",  # "Demand (Monthly)",
        "Demand",  # "Demand (Daily)",

        "",  # "Plan Data",
        "",  # "Plans",
        "",  # Well data
        "",  # Return

        "",  # "Stream Estimate Data",
        "",  # "Stream Estimate Stations",
        "",  # "Stream Estimate Coefficients",
        "FlowNatural",  # "Stream Natural Flow TS (Monthly)",
        "FlowNatural",  # "Stream Natural Flow TS (Daily)",

        "",  # "River Network Data",
        "",  # "River Network",
        "",  # "Network (Graphical)", # For StateDMI and GUI

        "",  # "Operational Data",
        "",  # "Operational Rights",
        "Call",  # "Call time series",
        "SJRIP",  # San Juan
        "RioGrandeSpill",  # Rio Grande spill

        "",  # "Spatial Data",
        ""  # "GeoView Project"
    ]
    __component_ts_data_intervals = [
        TimeInterval.UNKNOWN,  # "Control Data",
        TimeInterval.UNKNOWN,  # "Response",
        TimeInterval.UNKNOWN,  # "Control",
        TimeInterval.UNKNOWN,  # "Output Request",
        TimeInterval.UNKNOWN,  # "Reach Data",

        TimeInterval.UNKNOWN,  # "Consumptive Use Data",
        TimeInterval.UNKNOWN,  # "StatCU Structure",
        TimeInterval.YEAR,  # "Irrigation Practice TS (Yearly)",
        TimeInterval.MONTH,  # "Consumptive Water Req. (Monthly)",
        TimeInterval.DAY,  # "Consumptive Water Req. (Daily)",

        TimeInterval.UNKNOWN,  # "Stream Gage Data",
        TimeInterval.UNKNOWN,  # "Stream Gage Stations",
        TimeInterval.MONTH,
        TimeInterval.DAY,
        TimeInterval.MONTH,
        TimeInterval.DAY,

        TimeInterval.UNKNOWN,  # "Delay Table (Monthly) Data",
        TimeInterval.UNKNOWN,  # "Delay Tables (Monthly)",

        TimeInterval.UNKNOWN,  # "Delay Table (Daily) Data",
        TimeInterval.UNKNOWN,  # "DelayTables (Daily)",

        TimeInterval.UNKNOWN,  # "Diversion Data",
        TimeInterval.UNKNOWN,  # "Diversion Stations",
        TimeInterval.UNKNOWN,  # "Diversion Rights",
        TimeInterval.MONTH,  # "Diversion Historical TS (Monthly)",
        TimeInterval.DAY,  # "Diversion Historical TS (Daily)",
        TimeInterval.MONTH,  # "Demand TS (Monthly)"
        TimeInterval.MONTH,
        TimeInterval.MONTH,
        TimeInterval.DAY,

        TimeInterval.UNKNOWN,  # "Precipitation Data",
        TimeInterval.MONTH,  # "Precipitation Time Series (Monthly)",
        TimeInterval.YEAR,  # "Precipitation Time Series (Yearly)",

        TimeInterval.UNKNOWN,  # "Evaporation Data",
        TimeInterval.MONTH,  # "Evaporation Time Series (Monthly)",
        TimeInterval.YEAR,  # "Evaporation Time Series (Yearly)",

        TimeInterval.UNKNOWN,  # "Reservoir Data",
        TimeInterval.UNKNOWN,  # "Reservoir Stations",
        TimeInterval.UNKNOWN,  # "Reservoir Rights",
        TimeInterval.MONTH,  # "Content, End of Month (Monthly)",
        TimeInterval.DAY,  # "Content, End of Day (Daily)",
        TimeInterval.MONTH,  # "Reservoir Targets (Monthly)",
        TimeInterval.DAY,  # "Reservoir Targets(Daily)",
        TimeInterval.UNKNOWN,  # "Return Flow",

        TimeInterval.UNKNOWN,  # "Instream Flow Data",
        TimeInterval.UNKNOWN,  # "Instream Flow Stations",
        TimeInterval.UNKNOWN,  # "Instream Flow Rights",
        TimeInterval.MONTH,  # "Demand (Monthly)",
        TimeInterval.MONTH,  # "Demand (Average Monthly)",
        TimeInterval.DAY,  # "Demand (Daily)",

        TimeInterval.UNKNOWN,  # "Well Data",
        TimeInterval.UNKNOWN,  # "Well Stations",
        TimeInterval.UNKNOWN,  # "Well Rights",
        TimeInterval.MONTH,  # "Well Historical Pumping (Monthly)",
        TimeInterval.DAY,  # "Well Historical Pumping (Daily)",
        TimeInterval.MONTH,  # "Demand (Monthly)",
        TimeInterval.DAY,  # "Demand (Daily)",

        TimeInterval.UNKNOWN,  # "Plan Data",
        TimeInterval.UNKNOWN,  # "Plans",
        TimeInterval.UNKNOWN,  # "Well augmentation",
        TimeInterval.UNKNOWN,  # "Return",

        TimeInterval.UNKNOWN,  # "Stream Estimate Data",
        TimeInterval.UNKNOWN,  # "Stream Estimate Stations",
        TimeInterval.UNKNOWN,  # "Stream Estimate Coefficients",
        TimeInterval.MONTH,  # "Stream Natural Flow TS (Monthly)",
        TimeInterval.DAY,  # "Stream Natural Flow TS (Daily)",

        TimeInterval.UNKNOWN,  # "River Network Data",
        TimeInterval.UNKNOWN,  # "River Network",
        TimeInterval.UNKNOWN,  # "Network (Graphical)",

        TimeInterval.UNKNOWN,  # "Operational Data",
        TimeInterval.UNKNOWN,  # "Operational Rights",
        TimeInterval.DAY,  # "Call time series",
        TimeInterval.YEAR,  # "San Juan Sediment Recovery Plan",
        TimeInterval.MONTH,  # "Rio Grande Spill",

        TimeInterval.UNKNOWN,  # "Spatial Data",
        TimeInterval.UNKNOWN,  # "GeoView Project"
    ]

    # The following array assigns the time series data units for use with time series.
    # These can be used when creating new time series. If the data component is known (e.g., because
    # reading them from a response file), then the following array can be used to look up the data units
    # for the time series. Components that are not time series have blank strings for data units.
    __component_ts_data_units = [
        "",  # "Control Data",
        "",  # "Response",
        "",  # "Control",
        "",  # "Output Request",
        "",  # "Reach Data",

        "",  # "Consumptive Use Data",
        "",  # "StateCU Structure",
        "",  # "Irrigation Practice TS (Yearly)" - units vary
        "ACFT",  # "Consumptive Water Requirement (Monthly)",
        "CFS",  # "Consumptive Water Requirement (Daily)",

        "",  # "Stream Gage Data",
        "",  # "Stream Gage Stations",
        "ACFT",
        "CFS",
        "ACFT",
        "CFS",

        "",  # "Delay Table (Monthly) Data",
        "",  # "Delay Tables (Monthly)",

        "",  # "Delay Table (Daily) Data",
        "",  # "Delay Tables (Daily)",

        "",  # "Diversion Data",
        "",  # "Diversion Stations",
        "CFS",  # "Diversion Rights",
        "ACFT",  # "Diversion Historical TS (Monthly)",
        "CFS",  # "Diversion Historical TS (Daily)",
        "ACFT",  # "Demand TS (Monthly)",
        "ACFT",
        "ACFT",
        "CFS",

        "",  # "Precipitation Data",
        "IN",  # "Precipitation Time Series (Monthly)",
        "IN",  # "Precipitation Time Series (Yearly)",

        "",  # "Evaporation Data",
        "IN",  # "Evaporation Time Series (Monthly)",
        "IN",  # "Evaporation TIme Series (Daily)",

        "",  # "Reservoir Data",
        "",  # "Reservoir Stations",
        "ACFT",  # "Reservoir Rights",
        "ACFT",  # "Content, End of Month (Monthly)",
        "ACFT",  # "Content, End of Month (Daily)",
        "ACFT",  # "Reservoir Targets (Monthly)",
        "ACFT",  # "Reservoir Targets (Daily)",
        "",  # Return,

        "",  # "Instream Flow Data",
        "",  # "Instream Flow Stations",
        "CFS",  # "Instream Flow Rights",
        "CFS",  # "Demand (Monthly)",
        "CFS",  # "Demand (Average Monthly)",
        "CFS",  # "Demand (Daily)",

        "",  # "Well Data",
        "",  # "Well Stations",
        "CFS",  # "Well Rights",
        "ACFT",  # "Well Historical Pumping (Monthly)",
        "CFS",  # "Well Historical Pumping (Daily)",
        "ACFT",  # "Demand (Monthly)",
        "CFS",  # "Demand (Daily)",

        "",  # "Plan Data",
        "",  # "Plans",
        "",  # "Well Augmentation",
        "",  # "Return",

        "",  # "Stream Estimate Data",
        "",  # "Stream Estimate Stations",
        "",  # "Stream Estimate coefficients",
        "ACFT",  # "Stream Natural Flow TS (Monthly)",
        "CFS",  # "Stream Natural Flow TS (Daily)",

        "",  # "River Network Data",
        "",  # "River Network",
        "",  # "Network (Graphical)",

        "",  # "River Network Data",
        "",  # "Operational Rights",
        "DAY",  # "Call time series",
        "",  # "San Juan Sediment Recovery Plan",
        "",  # "Rio Grande Spill",

        "",  # "Spatial Data",
        ""   # "GeoView Project"
    ]

    def __init__(self, type=None):
        super().__init__(StateMod_DataSet.__component_types, StateMod_DataSet.__component_names,
                         StateMod_DataSet.__component_groups, StateMod_DataSet.__component_group_assignments,
                         StateMod_DataSet.__component_group_primaries)

        # List of unknown file propery names in the *.rsp. These are properties not understood by
        # the code but will need to be retained when writing the *.rsp to keep it whole.
        # This list WILL include special properties like StateModExecutable that are used by the GUI.
        self.__unhandledResponseFileProperties = PropList("Unhandled response file properties.")

        # Heading for output
        self.__heading1 = ""

        # Heading for output
        self.__heading2 = ""

        # Starting year of the simulation. Must be defined.
        self.__iystr = StateMod_Util.MISSING_INT

        # Ending year of simulation. Must be defined.
        self.__iyend = StateMod_Util.MISSING_INT

        # Switch for output untis. Default is ACFT.
        self.__iresop = 2

        # Monthly or avg monthly evap. Default to monthly.
        self.__moneva = 0

        # Monthly or avg monthly evap. Default to total.
        self.__iopflo = 1

        # Number of precipitation stations - should be set when the time series are read -
        # this will be phased out in the future.
        self.__numpre = 0

        # Number of evaporation stations - should be set when the time series are read -
        # this will be phased out in the future.
        self.__numeva = 0

        # Max number entries in delay pattern.  Default is variable number as percents.
        # The following defaults assume normal operation...
        self.__interv = -1

        # Factor, CFS to AF/D
        self.__factor = 1.9835

        # Divisor for streamflow data units.
        self.__rfacto = 1.9835

        # Divisor for diversion data units.
        self.__dfacto = 1.9835

        # Divisor for instream flow data units.
        self.__ffacto = 1.9835

        # Factor, reservoir content data to AF.
        self.__cfacto = 1.0

        # Factor, evaporation data to Ft.
        self.__efacto = 1.0

        # Factor, precipitation data to Ft.
        self.__pfacto = 1.0

        # Calendar/water/irrigation year - default to calendar.
        self.__cyrl = "Calendar"

        # Switch for demand type. Default to historic approach.
        self.__icondem = 1

        # Switch for detailed output. Default is no detailed output.
        self.__ichk = 0

        # Switch for re-operation control.  Default is yes re-operate.
        # Unlike most StateMod options this uses 0 for do it.
        self.__ireopx = 0

        # Switch for instream flow approach.  Default to use reaches and average monthly demands.
        self.__ireach = 1

        # Switch for detailed call data.  Default to no data.
        self.__icall = 0

        # Default to not used.  Detailed call water right ID.
        self.__ccall = ""

        # Switch for daily analysis.  Default to no daily analysis.
        self.__iday = 0

        # Switch for well analysis.  Default to no well analysis.
        self.__iwell = 0

        # Maximum recharge limit.  Default to not used.
        self.__gwmaxrc = 0.0

        # San Juan recovery program.  Default to no SJRIP.
        self.__isjrip = 0

        # Is IPY data used?  Default to no data.
        self.__itsfile = 0

        # IWR switch - default to no data.
        self.__ieffmax = 0

        # Sprinkler switch.  Default to no sprinkler data.
        self.__isprink = 0

        # Soil moisture accounting.  Default to not used.
        self.__soild = 0.0

        # Significant figures for output.
        self.__isig = 0

        if type is None:
            self.StateMod_DataSet_init(type)
        self.initialize()

    def StateMod_DataSet_init(self, type):
        """
        Constructor.  Makes a blank data set.  Specific output files, by default, will
        use the output directory and base file name in output file names.
        :param type: Data set type (currently ignored).
        """
        try:
            self.setDataSetType(type, True)
        except Exception as e:
            pass  # not important

    def checkComponentVisibility(self):
        visibility = True

        # Check for daily data set (some may be reset in other checks below)...

        if self.__iday != 0:
            visibility = True
        else:
            visibility = False
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMGAGE_NATURAL_FLOW_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DEMAND_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_INSTREAM_DEMAND_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_DEMAND_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_TARGET_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DELAY_TABLE_DAILY_GROUP)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DELAY_TABLES_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMGAGE_HISTORICAL_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DIVERSION_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_PUMPING_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_CONTENT_TS_DAILY)
        if comp is not None:
            comp.setVisible(visibility)

        # The stream estimate natural flow time series are always invisible because
        # they are shared with the stream gage natural time series files...

        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY)
        if comp is not None:
            comp.setVisible(False)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMESTIMATE_NATURAL_FLOW_TS_DAILY)
        if comp is not None:
            comp.setVisible(False)

        # Check well data set...

        if self.hasWellData(False):
            visiblity = True
        else:
            visibility = False
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_GROUP)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_STATIONS)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_RIGHTS)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_DEMAND_TS_MONTHLY)
        if comp is not None:
            comp.setVisible(visibility)
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_PUMPING_TS_MONTHLY)
        if comp is not None:
            comp.setVisible(visibility)
        if self.__iday != 0:  # Else checked above
            comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_DEMAND_TS_DAILY)
            if comp is not None:
                comp.setVisible(visibility)
            comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_PUMPING_TS_DAILY)
            if comp is not None:
                comp.setVisible(visibility)

        # Check instream demand flag (component is in the instream flow group)...

        if (self.__ireach == 2) or (self.__ireach == 3):
            visibility = True
        else:
            visibility = False
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_INSTREAM_DEMAND_TS_MONTHLY)
        if comp is not None:
            comp.setVisible(visibility)

        # Check SJRIP flag...

        if self.__isjrip != 0:
            visiblity = True
        else:
            visibility = False
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_SANJUAN_RIP)
        if comp is not None:
            comp.setVisible(visibility)

        # Check irrigation practice flag (component is in the diversion group)...
        if self.__itsfile != 0:
            visibility = True
        else:
            visibility = False
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_IRRIGATION_PRACTICE_TS_YEARLY)
        if comp is not None:
            comp.setVisible(visibility)

        # Check variable efficiency flag (component is in the diversions group)...

        if self.__ieffmax != 0:
            visibility = True
        else:
            visibility = False
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY)
        if comp is not None:
            comp.setVisible(visibility)
        if self.__iday != 0:  # Else already check above
            comp = self.getComponentForComponentType(StateMod_DataSet.COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY)
            if comp is not None:
                comp.setVisible(visibility)

        # Check the soil moisture flag (component is in the diversion group)...
        if self.__soild != 0.0:
            visibility = True
        else:
            visibility = False
        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STATECU_STRUCTURE)
        if comp is not None:
            comp.setVisible(visibility)

        # Hide the network (Graphical) file until it is fully implemented...

        comp = self.getComponentForComponentType(StateMod_DataSet.COMP_NETWORK)
        if comp is not None:
            comp.setVisible(True)


    def getDataFilePathAbsolute(self, comp):
        """
        Determine the full path to a component data file, including accounting for the
        working directory.  If the file is already an absolute path, the same value is
        returned.  Otherwise, the data set directory is prepended to the component data
        file name (which may be relative to the data set directory) and then calls IOUtil.getPathUsingWorkingDir().
        :param comp: Data set component.
        :return: Full path to the data file (absolute), using the working directory.
        """
        file = comp.getDataFileName()
        if(os.path.isabs(file)):
            return file
        else:
            return IOUtil.getPathUsingWorkingDir(str(self.getDataSetDirectory() + os.path.sep + file))

    def getDataFilePathAbsoluteFromString(self, file):
        """
        Determine the full path to a component data file, including accounting for the
        working directory.  If the file is already an absolute path, the same value is
        returned.  Otherwise, the data set directory is prepended to the component data
        file name (which may be relative to the data set directory) and then calls IOUtil.getPathUsingWorkingDir().
        :param file: File name (e.g. from component getFileName())
        :return: Full path to the data file (absolute), using the working directory.
        """
        if os.path.isabs(file):
            return file
        else:
            return IOUtil.getPathUsingWorkingDir(str(self.getDataSetDirectory() + os.path.sep + file))

    def getUnhandledResponseFileProperties(self):
        """
        Return the list of unhandled response file properties. These are entries in the *rsp file that the
        code does not specifically handle, such as new files or unimplemented files.
        :return: properties from the response file that are not explicitly handled
        """
        return self.__unhandledResponseFileProperties

    def hasWellData(self, is_active):
        """
        Indicate whether the data set has well data (iwell not missing and iwell not equal to 0).
        Use this method instead of checking iwell directly to simplify logic and allow
        for future changes to the model input.
        :param is_active: True if the data set includes well data (iwell not missing and i well !=0 ).
        Return False if well data are not used.
        :return: Only return true if well data are included in the dat set and the data are active
        (iwell = 1)
        """
        if is_active:
            if self.__iwell == 1:
                # Well data are included in the data set and are used...
                return True
            else:
                # Well data may or may not be included in the data set but are not used...
                return False
        elif not StateMod_Util.isMissing(self.__iwell) and (self.__iwell != 0):
            return True
        else:
            # Well data are not included...
            return False

    def initialize(self):
        """
        Initialize a data set by defining all the components for the data set.  This
        ensures that software will be able to evaluate all components.  Nulls are avoided where possible for
        data (e.g., empty lists are assigned).  Also initialize the control data to reasonable values.
        """

        routine = "StateMod_DataSet.initialize"
        # Initialize the control data
        self.initializeControlData()

        #  Always add all the components to the data set because StateMod does
        #  not really differentiate between data set types.  Instead, control
        #  file information controls.  Components are added to their groups.
        #  Also initialize the data for each sub-component to empty Vectors so
        #  that GUI based code does not need to check for nulls.  This is
        #  consistent with StateMod GUI initializing data vectors to empty at startup.
        #
        #  TODO - need to turn on data set components (set visible, etc.) as
        #  the control file is changed.  This allows new components to be enabled in the right order.
        #
        #  TODO - should be allowed to have null data Vector but apparently
        #  StateMod GUI cannot handle yet - need to allow null later and use
        #  hasData() or similar to check.
        try:
            comp = DataSetComponent(self, StateMod_DataSet.COMP_CONTROL_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RESPONSE)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, self.COMP_CONTROL)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, self.COMP_OUTPUT_REQUEST)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, self.COMP_REACH_DATA)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_CONSUMPTIVE_USE_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STATECU_STRUCTURE)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_IRRIGATION_PRACTICE_TS_YEARLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMGAGE_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMGAGE_STATIONS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMGAGE_HISTORICAL_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMGAGE_HISTORICAL_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMGAGE_NATURAL_FLOW_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMGAGE_NATURAL_FLOW_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_DELAY_TABLE_MONTHLY_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DELAY_TABLES_MONTHLY)
            subcomp.setData([])

            comp = DataSetComponent(self, StateMod_DataSet.COMP_DELAY_TABLE_DAILY_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DELAY_TABLES_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_DIVERSION_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DIVERSION_STATIONS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DIVERSION_RIGHTS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DIVERSION_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DIVERSION_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DEMAND_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DEMAND_TS_OVERRIDE_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DEMAND_TS_AVERAGE_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DEMAND_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_PRECIPITATION_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_PRECIPITATION_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_PRECIPITATION_TS_YEARLY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_EVAPORATION_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_EVAPORATION_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_EVAPORATION_TS_YEARLY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_RESERVOIR_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RESERVOIR_STATIONS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RESERVOIR_RIGHTS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RESERVOIR_CONTENT_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RESERVOIR_CONTENT_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RESERVOIR_TARGET_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RESERVOIR_TARGET_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RESERVOIR_RETURN)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_INSTREAM_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_INSTREAM_STATIONS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_INSTREAM_RIGHTS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_INSTREAM_DEMAND_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_INSTREAM_DEMAND_TS_AVERAGE_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_INSTREAM_DEMAND_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_WELL_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_WELL_STATIONS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_WELL_RIGHTS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_WELL_PUMPING_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_WELL_PUMPING_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_WELL_DEMAND_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_WELL_DEMAND_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_PLAN_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_PLANS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_PLAN_WELL_AUGMENTATION)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_PLAN_RETURN)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMESTIMATE_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMESTIMATE_STATIONS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMESTIMATE_COEFFICIENTS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_STREAMESTIMATE_NATURAL_FLOW_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_RIVER_NETWORK_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RIVER_NETWORK)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_NETWORK)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_OPERATION_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_OPERATION_RIGHTS)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_DOWNSTREAM_CALL_TS_DAILY)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_SANJUAN_RIP)
            subcomp.setData([])
            comp.addComponent(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_RIO_GRANDE_SPILL)
            subcomp.setData([])
            comp.addComponent(subcomp)

            comp = DataSetComponent(self, StateMod_DataSet.COMP_GEOVIEW_GROUP)
            comp.setListSource(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.addComponent(comp)
            subcomp = DataSetComponent(self, StateMod_DataSet.COMP_GEOVIEW)
            subcomp.setData([])
            comp.addComponent(subcomp)
        except Exception as e:
            # Should not happen...
            # Message.printWarning(2, routine, e)
            pass

    def initializeControlData(self):
        """
        Initialize the control data values to reasonable defaults.
        """
        self.__heading1 = ""
        self.__heading2 = ""
        self.__iystr = StateMod_Util.MISSING_INT  # Start year of simulation
        self.__iyend = StateMod_Util.MISSING_INT
        self.__iresop = 2  # Switch for output units (default is ACFT for all)
        self.__moneva = 0  # Monthly or avg monthly evap. Default to total.
        self.__iopflo = 1  # Total or gains streamflow. Default to total.
        self.__numpre = 0  # Number of precipitation stations - set when the time series are read
        # this will be phased out in the future.
        self.__numeva = 0  # Number of evaporation stations - set when the time series are read -
        # this will be phased out in the future.
        self.__interv = -1  # Max number entries in delay pattern. Default is variable number as percents.
        self.__factor = 1.9835  # Factor, CFS to AF/D
        self.__rfacto = 1.9835  # Divisor for streamflow data units.
        self.__dfacto = 1.9835  # Divisor for diversion data units.
        self.__ffacto = 1.9835  # Divisor for instream flow data units.
        self.__cfacto = 1.0  # Factor, reservoir content data to AF.
        self.__efacto = 1.0  # Factor, evaporation data to Ft.
        self.__pfacto = 1.0  # Factor, precipitation data to Ft.
        self.__cyrl = "Calendar"
        self.__icondem = 1  # Switch for demand type. Default to historic approach.
        self.__ichk = 0  # Switch for detailed output. Default is no detailed output.
        self.__ireopx = 0  # Switch for re-operation control. Default is yes re-operate.
        self.__ireach = 1  # Switch for instream flow approach.
        # Default to use reaches and average monthly demands.
        self.__icall = 0  # Switch for detailed call data. Default to no data.
        self.__ccall = ""  # Deatiled call water right ID. Default to not used.
        self.__iday = 0  # Switch for daily analysis. Default to no daily analysis.
        self.__iwell = 0  # Switch for well analysis. Default to no well analysis.
        self.__gwmaxrc = 0.0  # Maximum rehcharge limit. Default to not used.
        self.__isjrip = 0  # San Juan recovery program. Default to no SJRIP.
        self.__itsfile = 0  # Is IPY data used? Default to no data.
        self.__ieffmax = 0  # IWR switch - default to no data.
        self.__isprink = 0  # Sprinkler switch. Default to no sprinkler data.
        self.__soild = 0.0  # Soil moisture accounting. Default to not used.
        self.__isig = 0  # Significant figures for output.

    def lookupTimeSeriesDataType(self, comp_type):
        """
        Determine the time series data type string for a component type.
        :param comp_type: Component type.
        :return: the time series data type string or an empty string if not found.
        The only problem is with COMP_RESERVOIR_TARGET_TS_MONTHLY and
        COMP_RESERVOIR_TARGET_TS_DAILY, each of which contain both the maximum and
        minimum time series.  For these components, add "Max" and "Min" to the returned values.
        """
        return self.__component_ts_data_types[comp_type]

    def readStateModFile(self, filename, readData, readTimeSeries, useGUI, parent):
        """
        Read the StateMod response file and fill the current StateMod_DataSet object.
        The file MUST be a newer free-format response file.
        The file and settings that are read are those set when the object was created.
        :param filename: Name of the StateMod response file.  This must be the
        full path (e.g., from a JFileChooser, with a drive).  The working directory will
        be set to the directory of the response file.
        :param readData: if true, then all the data for files in the response file are read, if false, only read
        the filenames from the response file but do not try to read the
        data from station, rights, time series, etc.  False is useful for testing I/O on the response file itself.
        :param readTimeSeries: indicates whether the time series files should be read (this parameter was implemented
        when performance was slow and it made sense to avoid reading time series - this paramter may be phased out
        because it is not generally how an issue to read the time series).  If readData=false, then time series
        will not be read in any case.
        :param useGUI: If true, then interactive prompts will be used where necessary.
        :param parent: The parent JFrame used to position warning dialogs if useGUI is true.
        """
        print("Read StateMod File: ... in development ")
        routine = "StateMod_DataSet.readStateModFiles"
        logger = logging.getLogger("StateMod")

        if not readData:
            readTimeSeries = False

        __readTimeSeries = readTimeSeries

        filenameParent = os.path.abspath(os.path.join(filename, os.pardir))
        filenameName = os.path.basename(filename)

        self.setDataSetDirectory(filenameParent)
        self.setDataSetFilename(filenameName)

        # String printed at the end of warning messages
        warningEndString = "\"."
        if useGUI:
            # This string is used if there are problems reading
            warningEndString = "\"\nInteractive edits for file will be disabled."

        # Check whether the response file is free format. If it is free
        # format then the file is read into a PropList below...
        # TODO @jurentie 04/16/2019 - work on isFreeFormatResponseFile()

        IOUtil.setProgramWorkingDir(filenameParent)

        # The following sets the static reference to the current data set
        # which is then accessible by every data object which extends StateMod_Data.
        # This is done in order that setting components dirty or not can be handled
        # at a low level when values change.
        StateMod_Data._dataset = self

        # Set basic information about the response file component - only save
        # the file name - the data itself are stored in this data set object.
        self.getComponentForComponentType(StateMod_DataSet.COMP_RESPONSE).setDataFileName(filenameParent)

        fn = ""

        i = 0
        size = 0  # For general use

        comp = None

        # Now start reading new scenario...
        totalReadTime = StopWatch()
        readTime = StopWatch()

        logger.info("Reading all information from input directory: \"" + self.getDataSetDirectory())
        logger.info ("Reading response file: \"" + filename + "\"")

        totalReadTime.start()

        response_props = PropList("Response")
        response_props.setPersistentName(filename)
        response_props.readPersistent()

        try:
            # Try for all reads.

            # Read the lines of the response file. Of major importance is reading the control file,
            # which indicates data set properties that allow figuring out which files are being read.

            # Read the files in the order of the StateMod documentation for the response file,
            # checking the control settings where a decision is needed.

            # Control file (.ctl)...

            try:
                fn = response_props.getValue("Control")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_CONTROL)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                # Control does not have its own data file now so use the data set
                comp.setData(self)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # River network file (.rin)...

            try:
                fn = response_props.getValue("River_Network")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RIVER_NETWORK)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                if readData and (fn is not None) and (os.path.getsize(self.getDataFilePathAbsoluteFromString(fn)) > 0):
                    readTime.clear()
                    readTime.start()
                    fn = self.getDataFilePathAbsoluteFromString(fn)
                    self.readStateModFile_Announce1(comp)
                    comp.setData(StateMod_RiverNetworkNode.readStateModFile(fn))
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Reservoir stations file (.res)...

            try:
                fn = response_props.getValue("Reservoir_Station")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_STATIONS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Diversion stations file (.dds)...

            try:
                fn = response_props.getValue("Diversion_Station")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DIVERSION_STATIONS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                if (readData) and (fn is not None) and (os.path.getsize(self.getDataFilePathAbsoluteFromString(fn))):
                    readTime.clear()
                    readTime.start()
                    fn = self.getDataFilePathAbsoluteFromString(fn)
                    self.readStateModFile_Announce1(comp)
                    comp.setData(StateMod_Diversion.readStateModFile(fn))
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Stream gage stations file (.ris)...

            try:
                fn = response_props.getValue("StreamGage_Station")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMGAGE_STATIONS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                if readData and (fn is not None) and (os.path.getsize(self.getDataFilePathAbsoluteFromString(fn)) > 0):
                    readTime.clear()
                    readTime.start()
                    fn = self.getDataFilePathAbsoluteFromString(fn)
                    comp.setData(StateMod_StreamGage.readStateModFile(fn))
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                # TODO @jurentie 04/19/2019 - needs updating
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # If not a free-format data set with separate stream estimate station,
            # re-read the legacy stream station file because some stations will be stream estimate stations.
            # If free format, get the file name...

            try:
                fn = response_props.getValue("StreamEstimate_Station")
                # Get from the stream gage component because Ray has not adopted a separate stream
                # estimate file...
                logger.info("Using StreamGage_Station for StreamEstimate_Station (no separate 2nd file).")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMGAGE_STATIONS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Instream flow stations file (.ifs)...

            try:
                fn = response_props.getValue("Instreamflow_Station")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_INSTREAM_STATIONS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                # Control does not have its own data file now so use the data set
                comp.setData(self)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Well stations..

            try:
                fn = response_props.getValue("Well_Station")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_STATIONS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Plans...

            try:
                fn = response_props.getValue("Plan_Data")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_PLANS)
                if comp is None:
                    logger.warning("Unable to look up plans component " + str(StateMod_DataSet.COMP_PLANS))
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Plan well augmentation (.plw)...

            try:
                fn = response_props.getValue("Plan_Wells")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_PLAN_WELL_AUGMENTATION)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Plan return (.prf)...

            try:
                fn = response_props.getValue("Plan_Return")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_PLAN_RETURN)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Instream flow rights files (.ifr)...

            try:
                fn = response_props.getValue("Instreamflow_Right")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_INSTREAM_RIGHTS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Reservoir rights file (.rer)...

            try:
                fn = response_props.getValue("Reservoir_Right")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_RIGHTS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Diversion rights file (.ddr)...

            try:
                fn = response_props.getValue("Diversion_Right")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DIVERSION_RIGHTS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
                if readData and (fn is not None) and (os.path.getsize(self.getDataFilePathAbsoluteFromString(fn)) > 0):
                    readTime.clear()
                    readTime.start()
                    fn = self.getDataFilePathAbsoluteFromString(fn)
                    self.readStateModFile_Announce1(comp)
                    comp.setData(StateMod_DiversionRight.readStateModFile(fn))
                    logger.info("Connecting diversion rights to diversion stations")
                    StateMod_Diversion.connectAllRights(
                        self.getComponentForComponentType(StateMod_DataSet.COMP_DIVERSION_STATIONS).getData(),
                        comp.getData()
                    )
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Operational rights file (.opr)...

            try:
                fn = response_props.getValue("Operational_Right")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_OPERATION_RIGHTS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Well rights file (.wer)...

            try:
                fn = response_props.getValue("Well_Right")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_RIGHTS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            try:
                fn = response_props.getValue("Precipitation_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_PRECIPITATION_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
                if readData and (fn is not None) and (os.path.getsize(self.getDataFilePathAbsoluteFromString(fn) > 0)):
                    readTime.clear()
                    readTime.start()
                    fn = self.getDataFilePathAbsoluteFromString(fn)
                    self.readStateModFile_Announce1(comp)
                    v = StateMod_TS.readTimeSeriesList(fn, None, None, None, True)
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Precipitation TS yearly file (.pra) - always read...

            try:
                fn = response_props.getValue("Precipitation_Annual")
                # Always set the file name...
                logger.info("StateMod GUI does not yet handle annual precipitation data.")
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_PRECIPITATION_TS_YEARLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Evaporation time series file monthly (.eva) - always read...

            try:
                fn = response_props.getValue("Evaporation_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_EVAPORATION_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Evaporation time series file yearly (.eva) - always read...

            try:
                fn = response_props.getValue("Evaporation_Annual")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_EVAPORATION_TS_YEARLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                if readData and (fn is not None) and (os.path.getsize(self.getDataFilePathAbsoluteFromString(fn)) > 0):
                    readTime.clear()
                    readTime.start()
                    fn = self.getDataFilePathAbsoluteFromString(fn)
                    self.readStateModFile_Announce1(comp)
                    v = StateMod_TS.readTimeSeriesList(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    self.setNumeva(size)
                    for i in range(size):
                        v[i].setDataType(self.lookupTimeSeriesDataType(StateMod_DataSet.COMP_EVAPORATION_TS_YEARLY))
                    comp.setData(v)
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Stream gage natural flow time series (.rim or .xbm) - always read...

            try:
                fn = response_props.getValue("Stream_Base_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                # Control does not have its own data file now so use the data set
                # if comp2 is not None:
                #     # Never read data above so no need to call the following
                #     comp2.setDirty( False )
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Diversion direct flow demand time series (monthly) file (.ddm)...

            try:
                fn = response_props.getValue("Diversion_Demand_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DEMAND_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                # Control does not have its own data file now so use the data set
                comp.setData(self)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Direct flow demand time series override (monthly) file (.ddo)...

            try:
                fn = response_props.getValue("Diversion_DemandOverride_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DEMAND_TS_OVERRIDE_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Direct flow demand time series average (monthly) file (.dda)...

            try:
                fn = response_props.getValue("Diversion_Demand_AverageMonthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DEMAND_TS_AVERAGE_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Monthly instream flow demand...

            try:
                fn = response_props.getValue("Instreamflow_Demand_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_INSTREAM_DEMAND_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Instream demand time series (average monthly) file (.ifa)...

            try:
                fn = response_props.getValue("Instreamflow_Demand_AverageMonthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_INSTREAM_DEMAND_TS_AVERAGE_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Well demand time series (monthly) file (.wem)...

            try:
                fn = response_props.getValue("Well_Demand_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_DEMAND_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Delay file (monthly) file (.dly)

            try:
                fn = response_props.getValue("DelayTable_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DELAY_TABLES_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Reservoir target time series (monthly) file (.tar)...

            try:
                fn = response_props.getValue("Reservoir_Target_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_TARGET_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Reservoir return (.rrf)...

            try:
                fn = response_props.getValue("Reservoir_Return")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_RETURN)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # TODO @jurentie 04/18/2019 - San Juan Sediment Recovery

            try:
                fn = response_props.getValue("SanJuanRecovery")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_SANJUAN_RIP)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                #readInputAnnounce1(comp)
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                #self.readInputAnnounce2(comp, readTime.getSeconds())

            # TODO @jurentie 04/18/2019 - ENable - Rio Grande Spill

            try:
                fn = response_props.getValue("RioGrande_Spill_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RIO_GRANDE_SPILL)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                #readInputAnnounce1(comp)
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                #self.readInputAnnounce2(comp, readTime.getSeconds())

            # Irrigation practice time series (tsp/ipy)...

            try:
                fn = response_props.getValue("IrrigationPractice_Yearly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_IRRIGATION_PRACTICE_TS_YEARLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                # readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Irrigation water requirement (iwr) - monthly...

            try:
                fn = response_props.getValue("ConsumptiveWaterRequirement_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # StateMod used to read PAR but the AWC is now in the StateCU STR file.

            try:
                fn = response_props.getValue("StateCU_")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_RETURN)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Soil moisture (*.par) file no longer supported (print a warning)...

            fn = response_props.getValue("SoilMoisture")
            if fn is not None and (os.path.getsize(self.getDataFilePathAbsolute(fn)) > 0):
                logger.warning("StateCU soil moisture file - not supported - not reading \"" + fn + "\"")

            # Reservoir content time series (monthly) file (.eom)...

            try:
                fn = response_props.getValue("Reservoir_Historic_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_CONTENT_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Stream estimate coefficients file (.rib)...

            try:
                fn = response_props.getValue("StreamEstimate_Coefficients")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMESTIMATE_COEFFICIENTS)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Historical streamflow (monthly) file (.rih)...

            try:
                fn = response_props.getValue("StreamGage_Historic_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMGAGE_HISTORICAL_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Diversion time series (historical monthly) file (.ddh)...

            try:
                fn = response_props.getValue("Diversion_Historic_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DIVERSION_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Well historical pumping time series (monthly) file (.weh)...

            try:
                fn = response_props.getValue("Well_Historic_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_PUMPING_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # GeoView Project file...

            try:
                fn = response_props.getValue("GeographicInformation")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_GEOVIEW)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                if fn is not None and (os.path.getsize(self.getDataFilePathAbsolute(fn)) > 0):
                    readTime.clear()
                    readTime.start()
                    fn = self.getDataFilePathAbsolute(fn)
                    #readInputAnnounce1(comp)
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                #readInputAnnounce2(comp, readTime.getSeconds())
                # Read data and display when the GUI is shown - no read for data to be read if no GUI

            # TODO output control - this is usually read separately when running
            # reports, etc. Just read the line but do not read the file...

            try:
                fn = response_props.getValue("OutputRequest")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_OUTPUT_REQUEST)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                #readInputAnnounce1(comp)
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                #readInputAnnounce2(comp, readTime.getSeconds())
                # Read data and display when the GUI is shown - no read for data to be read if no GUI

            # TODO Enable reach data file

            try:
                fn = response_props.getValue("Reach_Data")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_REACH_DATA)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                #readInputAnnounce1(comp, readTime.getSeconds())
                if readData and (fn is not None) and (os.path.getsize(self.getDataFilePathAbsolute(fn)) > 0):
                    logger.warning("Reach data file - not yet supported.")
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                #readInputAnnounce2(comp, readTime.getSeconds())

            # Stream natural flow flow time series (daily) file (.rid)...
            # Always read if a daily set.

            try:
                fn = response_props.getValue("Stream_Base_Daily")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMGAGE_NATURAL_FLOW_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                # if comp2 is not None:
                #     # Never read data above so no need to call the following
                #     comp2.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Direct diversion demand time series (daily) file (.ddd)...

            try:
                fn = response_props.getValue("Diversion_Demand_Daily")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DEMAND_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Instream flow demand time series (daily) file (.ifd)...

            try:
                fn = response_props.getValue("Instreamflow_Demand_Daily")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_INSTREAM_DEMAND_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Well demand time series (daily) file (.wed)...

            try:
                fn = response_props.getValue("Well_Demand_Daily")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_DEMAND_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Reservoir target time series (daily) file (.tad)...

            try:
                fn = response_props.getValue("Reservoir_Target_Daily")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_TARGET_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Delay table (daily)...

            try:
                fn = response_props.getValue("DelayTable_Daily")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DELAY_TABLES_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Irrigation water requirement (.iwr) - daily...

            try:
                fn = response_props.getValue("ConsumptiveWaterRequirement_Daily")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Streamflow historical time series (daily) file (.riy) - always read...

            try:
                fn = response_props.getValue("StreamGage_Historic_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_STREAMGAGE_HISTORICAL_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Diversion (daily) time series (.ddd)...

            try:
                fn = response_props.getValue("Diversion_Historic_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DIVERSION_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Well pumping (daily) time series...
            try:
                fn = response_props.getValue("Well_Historic_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_WELL_PUMPING_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Daily reservoir content "eoy" ...

            try:
                fn = response_props.getValue("Reservoir_Historic_Monthly")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_RESERVOIR_CONTENT_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Downstream call (.cal)...

            try:
                fn = response_props.getValue("Downstream_Call")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_DOWNSTREAM_CALL_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                #readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())

            # Keep track of files/properties that are not explicitly handled in this class
            # These may be new files added to the model, old files being phased out, or simple properties.
            unhandledResponseFileProperties = self.getUnhandledResponseFileProperties()
            unhandledResponseFileProperties.clear()
            for prop in response_props.getList():
                fileKey = prop.getKey()
                # See if the key is matched in the known StateMod file type keys...
                found = False
                for file in self.__statemod_file_properties:
                    if fileKey == file:
                        found = True
                        break
                if not found:
                    # The file property was not found so need to carry around as unknown
                    logger.info("Unhandled response file property: " + prop.getKey() + " = " + prop.getValue())
                    unhandledResponseFileProperties.set(prop)

            logger.info("DataSet: \n" + self.toStringDefinitions())

            totalReadTime.stop()
            logger.info("Total time to read StateMod files is " + "{:3f}".format(totalReadTime.getSeconds()) +
                         "seconds")
            totalReadTime.start()

            logger.info("Reading generalized network.")

            try:
                fn = response_props.getValue("Network")
                # Always set the file name...
                comp = self.getComponentForComponentType(StateMod_DataSet.COMP_NETWORK)
                if comp is not None and fn is not None:
                    comp.setDataFileName(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warningEndString +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.setErrorReadingInputFile(True)
            finally:
                comp.setDirty(False)
                # readTime.stop()
                self.readStateModFile_Announce2(comp, readTime.getSeconds())
        except Exception as e:
            # Main catch for all reads
            message = "Unexpected error during read ( {} ) - please contact support.".format(e)
            logger.info(message)
            logger.warning(e)
            # TODO Just rethrow for now
            # Throw error

        # Set component visibility based on the control information...
        self.checkComponentVisibility()

        totalReadTime.stop()
        msg = "Total time to read all files is {:3f} seconds".format(totalReadTime.getSeconds())
        logger.info(msg)
        #self.sendProcessListenerMessage(22, msg)
        self.setDirty(StateMod_DataSet.COMP_CONTROL, False)

        print("things are going well...")

    def readStateModFile_Announce1(self, comp):
        """
        This method is a helper routine to readStateModFile().  It calls
        Message.printStatus() with the message that a particular file is being read,
        including path.  Then it prints a similar, but shorter,
        message to the status bar.  If there is an error with the file (not specified,
        does not exist, etc.), then an Exception is thrown.  There are many StateMod
        files and therefore the same basic checks are done many times.
        :param comp: Data set component that is being read.
        """
        logger = logging.getLogger("StateMod")
        fn = self.getDataFilePathAbsolute(comp)
        description = comp.getComponentName()

        if (fn is None) or (len(fn) == 0):
            logger.warning(description + " file name unavailable")
        # TODO - need to know whether this is an error that the user should acknowledge...
        # TODO - error handling

        msg = "Reading " + description + " data from \"" + fn + "\""
        # The status message is printed because process listeners may not be registered.
        logger.info(msg)
        # self.sendProcessListenerMessage( StateMod_GUIUtil.STATUS_READ_START, msg)


    def readStateModFile_Announce2(self, comp, seconds):
        """
        This method is a helper routine to readStateModFile().  It calls
        Message.printStatus() with the message that a file has been read successively.
        Then it prints a similar, but shorter, message to the status bar.
        :param comp: Component being read.
        :param seconds: Number of seconds to read.
        """
        routine = "StateMod_DataSet.readStateModFile_Announce2"
        fn = self.getDataFilePathAbsolute(comp)
        description = comp.getComponentName()

        # The status message is printed because process listeners may not be registered.
        msg = description + " data read from \"" + fn + "\" in " + str("{:3f}".format(seconds)) + " seconds"

    def setNumeva(self, numeva):
        """
        Set number of evaporation stations.
        :param numeva: number of stations
        """
        if numeva != self.__numeva:
            self.__numeva = numeva
            self.setDirty(StateMod_DataSet.COMP_CONTROL, True)

    def toStringDefinitions(self):
        """
        Return a string representation of the data set definition information, useful for troubleshooting
        """
        nl = os.path.sep
        str = ""
        for i in range(len(self.__component_names)):
            comp = self.getComponentForComponentType(i)
            str += "[{}]".format(i) + " Name=\"" + self.__component_names[i]
            str += "\" Group={}".format(self.__component_group_assignments[i])
            str += " RspProperty=\"" + self.__statemod_file_properties[i]
            str += "\" Filename=\"" + comp.getDataFileName()
            str += "\" Ext=\"" + self.__component_file_extensions[i]
            str += "\" TSType=\"" + self.__component_ts_data_types[i]
            str += "\" TSInt={}".format(self.__component_ts_data_intervals[i])
            str += " TSUnits=\"" + self.__component_ts_data_units[i] + "\"\n"
        return str