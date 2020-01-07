# StateMod_DataSet - this class manages data components in a StateMod data set

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
#     CDSS Models Java Library is distributed in the hope that it will be useful,
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

from RTi.Util.IO.DataSet import DataSet
from RTi.Util.IO.DataSetComponent import DataSetComponent
from RTi.Util.IO.IOUtil import IOUtil
from RTi.Util.IO.PropList import PropList
from RTi.Util.Time.StopWatch import StopWatch
from RTi.Util.Time.TimeInterval import TimeInterval
from DWR.StateMod.StateMod_Data import StateMod_Data
from DWR.StateMod.StateMod_DataSetComponentType import StateMod_DataSetComponentType
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

    # Cubic-feet per second. Potential parameter in setIresop.
    SM_CFS = 1

    # Acre-feet per second. Potential parameter in setIresop.
    SM_ACFT = 2

    # Kilo Acre-feet per second. Potential parameter in setIresop.
    SM_KACFT = 3

    # CFS for daily, ACFT for monthly. Potential parameter in setIresop.
    SM_CFS_ACFT = 4

    # Cubic meters per second. Potential parameter in setIresop.
    SM_CMS = 5

    # Monthly data. Potential parameter in setMoneva.
    SM_MONTHLY = 0

    # Average data. Potential parameter in setMoneva.
    SM_AVERAGE = 1

    # Average data. Potential parameter in setIopflo.
    SM_TOT = 1

    # Gains data. Potential parameter in setIopflo.
    SM_GAINS = 2

    # The StateMod data set type is unknown.
    TYPE_UNKNOWN = 0
    NAME_UNKNOWN = "Unknown"

    # The following should be sequential from 0 because they have lookup position in DataSet arrays.
    """
    
    # Use for initialization, if needed.
    COMP_UNKNOWN = -1
    # Used when defining other nodes in the network, via the GUI.
    COMP_OTHER_NODE = -5

    # The following is now defined in StateMod_DataSetComponentType enumeration
    
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
    """

    # The data set component names, including the component groups. Subcomponent
    # names are defined after this array and are currently treated as special cases.
    component_names = [
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

    # Subcomponent names used with lookup_component_name(). These are special cases for labels
    # and displays but the data are managed with a component listed above. Make private to force
    # handling through lookup methods.
    COMPNAME_DIVERSION_STATION_DELAY_TABLES = "Diversion Station Delay Table Assignment"
    COMPNAME_DIVERSION_STATION_COLLECTIONS = "Diversion Station Collection Definitions"
    COMPNAME_RESERVOIR_STATION_ACCOUNTS = "Reservoir Station Accounts"
    COMPNAME_RESERVOIR_STATION_PRECIP_STATIONS = "Reservoir Station Precipitation Stations"
    COMPNAME_RESERVOIR_STATION_EVAP_STATIONS = "Reservoir Station Evaporation Stations"
    COMPNAME_RESERVOIR_STATION_CURVE = "Reservoir Station Content/Area/Seepage"
    COMPNAME_RESERVOIR_STATION_COLLECTIONS = "Reservoir Station Collection Definitions"
    COMPNAME_WELL_STATION_DELAY_TABLES = "Well Station Delay Table Assignment"
    COMPNAME_WELL_STATION_DEPLETION_TABLES = "Well Station Depletion Table Assignment"
    COMPNAME_WELL_STATION_COLLECTIONS = "Well Station Collection Definitions"

    # List of all the components, by number (type).
    component_types = [
        StateMod_DataSetComponentType.CONTROL_GROUP,
        StateMod_DataSetComponentType.RESPONSE,
        StateMod_DataSetComponentType.CONTROL,
        StateMod_DataSetComponentType.OUTPUT_REQUEST,
        StateMod_DataSetComponentType.REACH_DATA,

        StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP,
        StateMod_DataSetComponentType.STATECU_STRUCTURE,
        StateMod_DataSetComponentType.IRRIGATION_PRACTICE_TS_YEARLY,
        StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY,
        StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY,

        StateMod_DataSetComponentType.STREAMGAGE_GROUP,
        StateMod_DataSetComponentType.STREAMGAGE_STATIONS,
        StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_MONTHLY,
        StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_DAILY,
        StateMod_DataSetComponentType.STREAMGAGE_NATURAL_FLOW_TS_MONTHLY,
        StateMod_DataSetComponentType.STREAMGAGE_NATURAL_FLOW_TS_DAILY,

        StateMod_DataSetComponentType.DELAY_TABLE_MONTHLY_GROUP,
        StateMod_DataSetComponentType.DELAY_TABLES_MONTHLY,

        StateMod_DataSetComponentType.DELAY_TABLE_DAILY_GROUP,
        StateMod_DataSetComponentType.DELAY_TABLES_DAILY,

        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_STATIONS,
        StateMod_DataSetComponentType.DIVERSION_RIGHTS,
        StateMod_DataSetComponentType.DIVERSION_TS_MONTHLY,
        StateMod_DataSetComponentType.DIVERSION_TS_DAILY,
        StateMod_DataSetComponentType.DEMAND_TS_MONTHLY,
        StateMod_DataSetComponentType.DEMAND_TS_OVERRIDE_MONTHLY,
        StateMod_DataSetComponentType.DEMAND_TS_AVERAGE_MONTHLY,
        StateMod_DataSetComponentType.DEMAND_TS_DAILY,

        StateMod_DataSetComponentType.PRECIPITATION_GROUP,
        StateMod_DataSetComponentType.PRECIPITATION_TS_MONTHLY,
        StateMod_DataSetComponentType.PRECIPITATION_TS_YEARLY,

        StateMod_DataSetComponentType.EVAPORATION_GROUP,
        StateMod_DataSetComponentType.EVAPORATION_TS_MONTHLY,
        StateMod_DataSetComponentType.EVAPORATION_TS_YEARLY,

        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_STATIONS,
        StateMod_DataSetComponentType.RESERVOIR_RIGHTS,
        StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_MONTHLY,
        StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_DAILY,
        StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_MONTHLY,
        StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_DAILY,
        StateMod_DataSetComponentType.RESERVOIR_RETURN,

        StateMod_DataSetComponentType.INSTREAM_GROUP,
        StateMod_DataSetComponentType.INSTREAM_STATIONS,
        StateMod_DataSetComponentType.INSTREAM_RIGHTS,
        StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_MONTHLY,
        StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_AVERAGE_MONTHLY,
        StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_DAILY,

        StateMod_DataSetComponentType.WELL_GROUP,
        StateMod_DataSetComponentType.WELL_STATIONS,
        StateMod_DataSetComponentType.WELL_RIGHTS,
        StateMod_DataSetComponentType.WELL_PUMPING_TS_MONTHLY,
        StateMod_DataSetComponentType.WELL_PUMPING_TS_DAILY,
        StateMod_DataSetComponentType.WELL_DEMAND_TS_MONTHLY,
        StateMod_DataSetComponentType.WELL_DEMAND_TS_DAILY,

        StateMod_DataSetComponentType.PLAN_GROUP,
        StateMod_DataSetComponentType.PLANS,
        StateMod_DataSetComponentType.PLAN_WELL_AUGMENTATION,
        StateMod_DataSetComponentType.PLAN_RETURN,

        StateMod_DataSetComponentType.STREAMESTIMATE_GROUP,
        StateMod_DataSetComponentType.STREAMESTIMATE_STATIONS,
        StateMod_DataSetComponentType.STREAMESTIMATE_COEFFICIENTS,
        StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY,
        StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_DAILY,

        StateMod_DataSetComponentType.RIVER_NETWORK_GROUP,
        StateMod_DataSetComponentType.RIVER_NETWORK,
        StateMod_DataSetComponentType.NETWORK,

        StateMod_DataSetComponentType.OPERATION_GROUP,
        StateMod_DataSetComponentType.OPERATION_RIGHTS,
        StateMod_DataSetComponentType.DOWNSTREAM_CALL_TS_DAILY,
        StateMod_DataSetComponentType.SANJUAN_RIP,
        StateMod_DataSetComponentType.RIO_GRANDE_SPILL,

        StateMod_DataSetComponentType.GEOVIEW_GROUP,
        StateMod_DataSetComponentType.GEOVIEW
    ]

    # This array indicates the default file extension to use with each component.
    # These extensions can be used in file choosers.
    component_file_extensions = [
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

    # This array indicates the StateMod response file property name to use with each
    # component.  The group names are suitable for comments (put a # in front when
    # writing the response file).  Any value that is a blank string should NOT be written to the StateMod file.
    statemod_file_properties = [
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
    component_groups = [
        StateMod_DataSetComponentType.CONTROL_GROUP,
        StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP,
        StateMod_DataSetComponentType.STREAMGAGE_GROUP,
        StateMod_DataSetComponentType.DELAY_TABLE_MONTHLY_GROUP,
        StateMod_DataSetComponentType.DELAY_TABLE_DAILY_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.PRECIPITATION_GROUP,
        StateMod_DataSetComponentType.EVAPORATION_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.INSTREAM_GROUP,
        StateMod_DataSetComponentType.WELL_GROUP,
        StateMod_DataSetComponentType.PLAN_GROUP,
        StateMod_DataSetComponentType.STREAMESTIMATE_GROUP,
        StateMod_DataSetComponentType.RIVER_NETWORK_GROUP,
        StateMod_DataSetComponentType.OPERATION_GROUP,
        StateMod_DataSetComponentType.GEOVIEW_GROUP
    ]

    # Array indicating the primary components within each component group. The primary components are used to
    # get the list of identifiers for displays and processing. The number of values should agree with the list
    # above.
    component_group_primaries = [
        StateMod_DataSetComponentType.RESPONSE,  # StateMod_DataSetComponentType.CONTROL_GROUP
        StateMod_DataSetComponentType.STATECU_STRUCTURE,  # StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP
        StateMod_DataSetComponentType.STREAMGAGE_STATIONS,  # StateMod_DataSetComponentType.STREAMGAGE_GROUP
        StateMod_DataSetComponentType.DELAY_TABLES_MONTHLY,  # StateMod_DataSetComponentType.DELAY_TABLES_MONTHLY_GROUP
        StateMod_DataSetComponentType.DELAY_TABLES_DAILY,  # StateMod_DataSetComponentType.DELAY_TABLES_DAILY_GROUP
        StateMod_DataSetComponentType.DIVERSION_STATIONS,  # StateMod_DataSetComponentType.DIVERSION_GROUP
        StateMod_DataSetComponentType.PRECIPITATION_TS_MONTHLY,  # StateMod_DataSetComponentType.PRECIPITATION_GROUP
        StateMod_DataSetComponentType.EVAPORATION_TS_MONTHLY,  # StateMod_DataSetComponentType.EVAPORATION_GROUP
        StateMod_DataSetComponentType.RESERVOIR_STATIONS,  # StateMod_DataSetComponentType.RESERVOIR_GROUP
        StateMod_DataSetComponentType.INSTREAM_STATIONS,  # StateMod_DataSetComponentType.INSTREAM_GROUP
        StateMod_DataSetComponentType.WELL_STATIONS,  # StateMod_DataSetComponentType.WELL_GROUP
        StateMod_DataSetComponentType.PLANS,  # StateMod_DataSetComponentType.PLAN_GROUP
        StateMod_DataSetComponentType.STREAMESTIMATE_STATIONS,  # StateMod_DataSetComponentType.STREAMESTIMATE_GROUP
        StateMod_DataSetComponentType.RIVER_NETWORK,  # StateMod_DataSetComponentType.RIVER_NETWORK_GROUP
        StateMod_DataSetComponentType.OPERATION_RIGHTS,  # StateMod_DataSetComponentType.OPERATION_GROUP
        StateMod_DataSetComponentType.GEOVIEW  # StateMod_DataSetComponentType.GEOVIEW_GROUP
    ]

    # Array indicating the groups for each component.
    component_group_assignments = [
        StateMod_DataSetComponentType.CONTROL_GROUP,
        StateMod_DataSetComponentType.CONTROL_GROUP,
        StateMod_DataSetComponentType.CONTROL_GROUP,
        StateMod_DataSetComponentType.CONTROL_GROUP,
        StateMod_DataSetComponentType.CONTROL_GROUP,

        StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP,
        StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP,
        StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP,
        StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP,
        StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP,

        StateMod_DataSetComponentType.STREAMGAGE_GROUP,
        StateMod_DataSetComponentType.STREAMGAGE_GROUP,
        StateMod_DataSetComponentType.STREAMGAGE_GROUP,
        StateMod_DataSetComponentType.STREAMGAGE_GROUP,
        StateMod_DataSetComponentType.STREAMGAGE_GROUP,
        StateMod_DataSetComponentType.STREAMGAGE_GROUP,

        StateMod_DataSetComponentType.DELAY_TABLE_MONTHLY_GROUP,
        StateMod_DataSetComponentType.DELAY_TABLE_MONTHLY_GROUP,

        StateMod_DataSetComponentType.DELAY_TABLE_DAILY_GROUP,
        StateMod_DataSetComponentType.DELAY_TABLE_DAILY_GROUP,

        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,
        StateMod_DataSetComponentType.DIVERSION_GROUP,

        StateMod_DataSetComponentType.PRECIPITATION_GROUP,
        StateMod_DataSetComponentType.PRECIPITATION_GROUP,
        StateMod_DataSetComponentType.PRECIPITATION_GROUP,

        StateMod_DataSetComponentType.EVAPORATION_GROUP,
        StateMod_DataSetComponentType.EVAPORATION_GROUP,
        StateMod_DataSetComponentType.EVAPORATION_GROUP,

        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_GROUP,
        StateMod_DataSetComponentType.RESERVOIR_GROUP,

        StateMod_DataSetComponentType.INSTREAM_GROUP,
        StateMod_DataSetComponentType.INSTREAM_GROUP,
        StateMod_DataSetComponentType.INSTREAM_GROUP,
        StateMod_DataSetComponentType.INSTREAM_GROUP,
        StateMod_DataSetComponentType.INSTREAM_GROUP,
        StateMod_DataSetComponentType.INSTREAM_GROUP,

        StateMod_DataSetComponentType.WELL_GROUP,
        StateMod_DataSetComponentType.WELL_GROUP,
        StateMod_DataSetComponentType.WELL_GROUP,
        StateMod_DataSetComponentType.WELL_GROUP,
        StateMod_DataSetComponentType.WELL_GROUP,
        StateMod_DataSetComponentType.WELL_GROUP,
        StateMod_DataSetComponentType.WELL_GROUP,

        StateMod_DataSetComponentType.PLAN_GROUP,
        StateMod_DataSetComponentType.PLAN_GROUP,
        StateMod_DataSetComponentType.PLAN_GROUP,
        StateMod_DataSetComponentType.PLAN_GROUP,

        StateMod_DataSetComponentType.STREAMESTIMATE_GROUP,
        StateMod_DataSetComponentType.STREAMESTIMATE_GROUP,
        StateMod_DataSetComponentType.STREAMESTIMATE_GROUP,
        StateMod_DataSetComponentType.STREAMESTIMATE_GROUP,
        StateMod_DataSetComponentType.STREAMESTIMATE_GROUP,

        StateMod_DataSetComponentType.RIVER_NETWORK_GROUP,
        StateMod_DataSetComponentType.RIVER_NETWORK_GROUP,
        StateMod_DataSetComponentType.RIVER_NETWORK_GROUP,

        StateMod_DataSetComponentType.OPERATION_GROUP,
        StateMod_DataSetComponentType.OPERATION_GROUP,
        StateMod_DataSetComponentType.OPERATION_GROUP,
        StateMod_DataSetComponentType.OPERATION_GROUP,
        StateMod_DataSetComponentType.OPERATION_GROUP,

        StateMod_DataSetComponentType.GEOVIEW_GROUP,
        StateMod_DataSetComponentType.GEOVIEW_GROUP
    ]

    # The following array assigns the time series data types for use with time series.
    # For example, StateMod data sets do not contain a data type and therefore after
    # reading the file, the time series data type must be assumed. If the data component
    # is known (e.g., because reading from a response file), then the following array
    # can be used to look up the data type for the time series. Components that are not
    # time series have blank strings for data types.
    component_ts_data_types = [
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

    # The following array assigns the time series data intervals for use with time
    # series.  This information is important because the data types themselves may
    # not be unique and the interval must be examined
    component_ts_data_intervals = [
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
    component_ts_data_units = [
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

    def __init__(self, dataset_type=None):
        """
        Construct a dataset.
        :param dataset_type:  Dataset type, currently unused.
        """
        # Initialize the base class data in DataSet so that its methods can be used to process components
        super().__init__(component_types=StateMod_DataSet.component_types,
                         component_names=StateMod_DataSet.component_names,
                         component_groups=StateMod_DataSet.component_groups,
                         component_group_assignments=StateMod_DataSet.component_group_assignments,
                         component_group_primaries=StateMod_DataSet.component_group_primaries)

        self.WAIT = 0
        self.READY = 1

        self.process_listeners = None

        # Indicates whether time series are read when reading the data set.  This was put in place when software
        # performance was slow but generally now it is not an issue.  Leave in for some period but phase out if
        # performance is not an issue.
        self.read_time_series = True

        # String indicating blank file name - allowed to be a duplicate.
        self.BLANK_FILE_NAME = ""

        # Appended to some daily time series data types to indicate an estimated time series.
        self.ESTIMATED = "Estimated"

        # List of unknown file propery names in the *.rsp. These are properties not understood by
        # the code but will need to be retained when writing the *.rsp to keep it whole.
        # This list WILL include special properties like StateModExecutable that are used by the GUI.
        self.unhandled_response_file_properties = PropList("Unhandled response file properties.")

        # Heading for output
        self.heading1 = ""

        # Heading for output
        self.heading2 = ""

        # Starting year of the simulation. Must be defined.
        self.iystr = StateMod_Util.MISSING_INT

        # Ending year of simulation. Must be defined.
        self.iyend = StateMod_Util.MISSING_INT

        # Switch for output untis. Default is ACFT.
        self.iresop = 2

        # Monthly or avg monthly evap. Default to monthly.
        self.moneva = 0

        # Monthly or avg monthly evap. Default to total.
        self.iopflo = 1

        # Number of precipitation stations - should be set when the time series are read -
        # this will be phased out in the future.
        self.numpre = 0

        # Number of evaporation stations - should be set when the time series are read -
        # this will be phased out in the future.
        self.numeva = 0

        # Max number entries in delay pattern.  Default is variable number as percents.
        # The following defaults assume normal operation...
        self.interv = -1

        # Factor, CFS to AF/D
        self.factor = 1.9835

        # Divisor for streamflow data units.
        self.rfacto = 1.9835

        # Divisor for diversion data units.
        self.dfacto = 1.9835

        # Divisor for instream flow data units.
        self.ffacto = 1.9835

        # Factor, reservoir content data to AF.
        self.cfacto = 1.0

        # Factor, evaporation data to Ft.
        self.efacto = 1.0

        # Factor, precipitation data to Ft.
        self.pfacto = 1.0

        # Calendar/water/irrigation year - default to calendar.
        self.cyrl = "Calendar"

        # Switch for demand type. Default to historic approach.
        self.icondem = 1

        # Switch for detailed output. Default is no detailed output.
        self.ichk = 0

        # Switch for re-operation control.  Default is yes re-operate.
        # Unlike most StateMod options this uses 0 for do it.
        self.ireopx = 0

        # Switch for instream flow approach.  Default to use reaches and average monthly demands.
        self.ireach = 1

        # Switch for detailed call data.  Default to no data.
        self.icall = 0

        # Default to not used.  Detailed call water right ID.
        self.ccall = ""

        # Switch for daily analysis.  Default to no daily analysis.
        self.iday = 0

        # Switch for well analysis.  Default to no well analysis.
        self.iwell = 0

        # Maximum recharge limit.  Default to not used.
        self.gwmaxrc = 0.0

        # San Juan recovery program.  Default to no SJRIP.
        self.isjrip = 0

        # Is IPY data used?  Default to no data.
        self.itsfile = 0

        # IWR switch - default to no data.
        self.ieffmax = 0

        # Sprinkler switch.  Default to no sprinkler data.
        self.isprink = 0

        # Soil moisture accounting.  Default to not used.
        self.soild = 0.0

        # Significant figures for output.
        self.isig = 0

        # if type is None:
        #    self.statemod_dataset_init(type)
        self.initialize()

    def StateMod_DataSet(self):
        """
        Constructor.  Makes a blank data set.  Specific output files, by default, will
        use the output directory and base file name in output file names.
        :param dataset_type: Data set type (currently ignored).
        """
        try:
            # self.set_dataset_type(dataset_type, True)
            # Dataset type is not currently used
            pass
        except Exception as e:
            pass  # not important
        self.initialize()

    def check_component_visibility(self):
        visibility = True

        # Check for daily data set (some may be reset in other checks below)...

        if self.iday != 0:
            visibility = True
        else:
            visibility = False
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMGAGE_NATURAL_FLOW_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DEMAND_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_DEMAND_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DELAY_TABLE_DAILY_GROUP)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DELAY_TABLES_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DIVERSION_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_PUMPING_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_DAILY)
        if comp is not None:
            comp.set_visible(visibility)

        # The stream estimate natural flow time series are always invisible because
        # they are shared with the stream gage natural time series files...

        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY)
        if comp is not None:
            comp.set_visible(False)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_DAILY)
        if comp is not None:
            comp.set_visible(False)

        # Check well data set...

        if self.has_well_data(False):
            visiblity = True
        else:
            visibility = False
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_GROUP)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_STATIONS)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_RIGHTS)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_DEMAND_TS_MONTHLY)
        if comp is not None:
            comp.set_visible(visibility)
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_PUMPING_TS_MONTHLY)
        if comp is not None:
            comp.set_visible(visibility)
        if self.iday != 0:  # Else checked above
            comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_DEMAND_TS_DAILY)
            if comp is not None:
                comp.set_visible(visibility)
            comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_PUMPING_TS_DAILY)
            if comp is not None:
                comp.set_visible(visibility)

        # Check instream demand flag (component is in the instream flow group)...

        if (self.ireach == 2) or (self.ireach == 3):
            visibility = True
        else:
            visibility = False
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_MONTHLY)
        if comp is not None:
            comp.set_visible(visibility)

        # Check SJRIP flag...

        if self.isjrip != 0:
            visiblity = True
        else:
            visibility = False
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.SANJUAN_RIP)
        if comp is not None:
            comp.set_visible(visibility)

        # Check irrigation practice flag (component is in the diversion group)...
        if self.itsfile != 0:
            visibility = True
        else:
            visibility = False
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.IRRIGATION_PRACTICE_TS_YEARLY)
        if comp is not None:
            comp.set_visible(visibility)

        # Check variable efficiency flag (component is in the diversions group)...

        if self.ieffmax != 0:
            visibility = True
        else:
            visibility = False
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY)
        if comp is not None:
            comp.set_visible(visibility)
        if self.iday != 0:  # Else already check above
            comp = self.get_component_for_component_type(StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY)
            if comp is not None:
                comp.set_visible(visibility)

        # Check the soil moisture flag (component is in the diversion group)...
        if self.soild != 0.0:
            visibility = True
        else:
            visibility = False
        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STATECU_STRUCTURE)
        if comp is not None:
            comp.set_visible(visibility)

        # Hide the network (Graphical) file until it is fully implemented...

        comp = self.get_component_for_component_type(StateMod_DataSetComponentType.NETWORK)
        if comp is not None:
            comp.set_visible(True)

    def get_data_file_path_absolute(self, file_object):
        """
        Determine the full path to a component data file, including accounting for the
        working directory.  If the file is already an absolute path, the same value is
        returned.  Otherwise, the data set directory is prepended to the component data
        file name (which may be relative to the data set directory) and then calls IOUtil.get_path_using_working_dir().
        :param file_object: Data file object, either a string path or DataSetComponent.
        :return: Full path to the data file (absolute), using the working directory.
        """
        # First get the filename
        logger = logging.getLogger(__name__)
        if isinstance(file_object, DataSetComponent):
            file = file_object.get_data_file_name()
        elif isinstance(file_object, str):
            file = file_object
        else:
            logger.warning("Cannot handle file object type " + str(type(file_object)))
        # Get the absolute path to the component
        if file is None:
            logger.info("StateMod component data file name is None (not set).")
        else:
            logger.info("StateMod component data file name is '" + file + "'.")
        if os.path.isabs(file):
            return file
        else:
            return IOUtil.get_path_using_working_dir(str(self.get_dataset_directory() + os.path.sep + file))

    def get_unhandled_response_file_properties(self):
        """
        Return the list of unhandled response file properties. These are entries in the *rsp file that the
        code does not specifically handle, such as new files or unimplemented files.
        :return: properties from the response file that are not explicitly handled
        """
        return self.unhandled_response_file_properties

    def has_sanjuan_data(self, is_active):
        """
        Indicate whether the data set has San Juan Recovery data (isjrip not missing and isjrip not equal 0).
        Use this method instead of checking isjrip directly to simplify logic and allow
        for future changes to the model input.
        :param is_active: Only return true if San Juan Recovery data are included in the
        data set and the data are active (isjrip = 1).
        :return: true if the data set includes San Juan Recovery data (isjrip not missing
        and isjrip != 0).  Return false if San Juan Recovery data are not used.
        """
        if is_active:
            if self.isjrip == 1:
                # San Juan Recovery data are included in the data set and are used...
                return True
            else:
                # San Juan Recovery data may or may not be included in the data set but are not used...
                return False
        elif not StateMod_Util.is_missing(self.isjrip) and (self.isjrip != 0):
            # Data are specified in the data set but are not used...
            return True
        else:
            # San Juan Recovery data are not included...
            return False

    def has_well_data(self, is_active):
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
            if self.iwell == 1:
                # Well data are included in the data set and are used...
                return True
            else:
                # Well data may or may not be included in the data set but are not used...
                return False
        elif not StateMod_Util.is_missing(self.iwell) and (self.iwell != 0):
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

        # Initialize the control data
        self.initialize_control_data()

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
        logger = logging.getLogger(__name__)
        try:
            logger.info("Initializing dataset components")
            comp = DataSetComponent(self, StateMod_DataSetComponentType.CONTROL_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RESPONSE)
            subcomp.set_data(PropList())
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.CONTROL)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.OUTPUT_REQUEST)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.REACH_DATA)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.CONSUMPTIVE_USE_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STATECU_STRUCTURE)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.IRRIGATION_PRACTICE_TS_YEARLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMGAGE_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMGAGE_STATIONS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMGAGE_NATURAL_FLOW_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMGAGE_NATURAL_FLOW_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.DELAY_TABLE_MONTHLY_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DELAY_TABLES_MONTHLY)
            subcomp.set_data([])

            comp = DataSetComponent(self, StateMod_DataSetComponentType.DELAY_TABLE_DAILY_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DELAY_TABLES_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.DIVERSION_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DIVERSION_STATIONS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DIVERSION_RIGHTS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DIVERSION_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DIVERSION_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DEMAND_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DEMAND_TS_OVERRIDE_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DEMAND_TS_AVERAGE_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DEMAND_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.PRECIPITATION_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.PRECIPITATION_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.PRECIPITATION_TS_YEARLY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.EVAPORATION_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.EVAPORATION_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.EVAPORATION_TS_YEARLY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.RESERVOIR_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RESERVOIR_STATIONS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RESERVOIR_RIGHTS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RESERVOIR_RETURN)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.INSTREAM_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.INSTREAM_STATIONS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.INSTREAM_RIGHTS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_AVERAGE_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.WELL_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.WELL_STATIONS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.WELL_RIGHTS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.WELL_PUMPING_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.WELL_PUMPING_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.WELL_DEMAND_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.WELL_DEMAND_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.PLAN_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.PLANS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.PLAN_WELL_AUGMENTATION)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.PLAN_RETURN)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMESTIMATE_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMESTIMATE_STATIONS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMESTIMATE_COEFFICIENTS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.RIVER_NETWORK_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RIVER_NETWORK)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.NETWORK)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.OPERATION_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.OPERATION_RIGHTS)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.DOWNSTREAM_CALL_TS_DAILY)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.SANJUAN_RIP)
            subcomp.set_data([])
            comp.add_component(subcomp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.RIO_GRANDE_SPILL)
            subcomp.set_data([])
            comp.add_component(subcomp)

            comp = DataSetComponent(self, StateMod_DataSetComponentType.GEOVIEW_GROUP)
            comp.set_list_source(DataSetComponent.LIST_SOURCE_PRIMARY_COMPONENT)
            self.add_component(comp)
            subcomp = DataSetComponent(self, StateMod_DataSetComponentType.GEOVIEW)
            subcomp.set_data([])
            comp.add_component(subcomp)
        except Exception as e:
            # Should not happen...
            # Message.printWarning(2, routine, e)
            pass

    def initialize_control_data(self):
        """
        Initialize the control data values to reasonable defaults.
        """
        self.heading1 = ""
        self.heading2 = ""
        self.iystr = StateMod_Util.MISSING_INT  # Start year of simulation
        self.iyend = StateMod_Util.MISSING_INT
        self.iresop = 2  # Switch for output units (default is ACFT for all)
        self.moneva = 0  # Monthly or avg monthly evap. Default to total.
        self.iopflo = 1  # Total or gains streamflow. Default to total.
        self.numpre = 0  # Number of precipitation stations - set when the time series are read
        # this will be phased out in the future.
        self.numeva = 0  # Number of evaporation stations - set when the time series are read -
        # this will be phased out in the future.
        self.interv = -1  # Max number entries in delay pattern. Default is variable number as percents.
        self.factor = 1.9835  # Factor, CFS to AF/D
        self.rfacto = 1.9835  # Divisor for streamflow data units.
        self.dfacto = 1.9835  # Divisor for diversion data units.
        self.ffacto = 1.9835  # Divisor for instream flow data units.
        self.cfacto = 1.0  # Factor, reservoir content data to AF.
        self.efacto = 1.0  # Factor, evaporation data to Ft.
        self.pfacto = 1.0  # Factor, precipitation data to Ft.
        self.cyrl = "Calendar"
        self.icondem = 1  # Switch for demand type. Default to historic approach.
        self.ichk = 0  # Switch for detailed output. Default is no detailed output.
        self.ireopx = 0  # Switch for re-operation control. Default is yes re-operate.
        self.ireach = 1  # Switch for instream flow approach.
        # Default to use reaches and average monthly demands.
        self.icall = 0  # Switch for detailed call data. Default to no data.
        self.ccall = ""  # Deatiled call water right ID. Default to not used.
        self.iday = 0  # Switch for daily analysis. Default to no daily analysis.
        self.iwell = 0  # Switch for well analysis. Default to no well analysis.
        self.gwmaxrc = 0.0  # Maximum rehcharge limit. Default to not used.
        self.isjrip = 0  # San Juan recovery program. Default to no SJRIP.
        self.itsfile = 0  # Is IPY data used? Default to no data.
        self.ieffmax = 0  # IWR switch - default to no data.
        self.isprink = 0  # Sprinkler switch. Default to no sprinkler data.
        self.soild = 0.0  # Soil moisture accounting. Default to not used.
        self.isig = 0  # Significant figures for output.

    def is_free_format_response_file(self, filepath):
        """
        Determine whether a StateMod response file is free format.  The response file
        is opened and checked for a non-commented line with "=".
        :param filepath: Path to response file as a Path, as full path.
        :return: true if the file is a free format file.
        """
        is_free_format = False
        with open(filepath.as_posix()) as fp:
            for line in fp:
                string_trimmed = line.strip()
                if string_trimmed.startswith("#") or string_trimmed == "":
                    # Comment
                    continue
                if string_trimmed.find("=") >= 0:
                    is_free_format = True
                    break
        return is_free_format

    def lookup_time_series_data_type(self, comp_type):
        """
        Determine the time series data type string for a component type.
        :param comp_type: Component type.
        :return: the time series data type string or an empty string if not found.
        The only problem is with StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_MONTHLY and
        StateMod_DataSetComponentType.COMP_RESERVOIR_TARGET_TS_DAILY, each of which contain both the maximum and
        minimum time series.  For these components, add "Max" and "Min" to the returned values.
        """
        if isinstance(comp_type, int):
            comp_type_value = comp_type
        else:
            # Assume Enum
            comp_type_value = comp_type.value
        return self.component_ts_data_types[comp_type_value]

    def read_statemod_file(self, filepath, read_data, read_time_series, use_gui, parent):
        """
        Read the StateMod response file and fill the current StateMod_DataSet object.
        The file MUST be a newer free-format response file.
        The file and settings that are read are those set when the object was created.
        :param filepath: Path to StateMod response file, as Path.  This must be the full path.
        The working directory will be set to the directory of the response file.
        :param read_data: if true, then all the data for files in the response file are read, if false, only read
        the filenames from the response file but do not try to read the
        data from station, rights, time series, etc.  False is useful for testing I/O on the response file itself.
        :param read_time_series: indicates whether the time series files should be read (this parameter was implemented
        when performance was slow and it made sense to avoid reading time series - this paramter may be phased out
        because it is not generally how an issue to read the time series).  If read_data=false, then time series
        will not be read in any case.
        :param use_gui: If true, then interactive prompts will be used where necessary.
        :param parent: The parent JFrame used to position warning dialogs if use_gui is true.
        """
        logger = logging.getLogger(__name__)

        if not read_data:
            read_time_series = False

        self.read_time_series = read_time_series

        print("Read StateMod file: " + filepath.as_posix())

        self.set_dataset_directory(filepath.parent.as_posix())
        self.set_dataset_filename(filepath.name)

        # String printed at the end of warning messages
        warning_end_string = "\"."
        if use_gui:
            # This string is used if there are problems reading
            warning_end_string = "\"\nInteractive edits for file will be disabled."

        # Check whether the response file is free format.
        # If it is free format then the file is read into a PropList below...
        if not self.is_free_format_response_file(filepath):
            message = "File \"" + filepath + "\" does not appear to be free-format response file - unable to read."
            logger.warning(message)
            raise ValueError(message)

        IOUtil.set_program_working_dir(filepath.parent.as_posix())

        # The following sets the static reference to the current data set
        # that is then accessible by every data object that extends StateMod_Data.
        # This is done in order that setting components dirty or not can be handled
        # at a low level when values change.
        StateMod_Data.dataset = self

        # Set basic information about the response file component - only save
        # the file name - the data itself are stored in this data set object.
        self.get_component_for_component_type(
            StateMod_DataSetComponentType.RESPONSE).set_data_file_name(filepath.as_posix())

        fn = ""

        i = 0
        size = 0  # For general use

        comp = None

        # Now start reading new scenario...
        total_read_time = StopWatch()
        read_time = StopWatch()

        logger.info("Reading all information from input directory: \"" + self.get_dataset_directory())
        logger.info("Reading response file: \"" + filepath.as_posix() + "\"")

        total_read_time.start()

        response_props = PropList("Response")
        response_props.set_persistent_name(filepath.as_posix())
        response_props.read_persistent()

        debug = True
        if debug:
            # Print the properties for troubleshooting
            for prop in response_props.get_list():
                logger.info("Property \"" + prop.get_key() + "\" = \"" + str(prop.get_value()) + "\"")

        try:
            # Try for all reads.

            # Read the lines of the response file. Of major importance is reading the control file,
            # which indicates data set properties that allow figuring out which files are being read.

            # Read the files in the order of the StateMod documentation for the response file,
            # checking the control settings where a decision is needed.

            # Control file (.ctl)...

            try:
                fn = response_props.get_value("Control")
                logger.info("Filename for Control: " + str(fn))
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.CONTROL)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie read data...
                if (read_data and (fn is not None)) and \
                          (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                     read_time.clear()
                     read_time.start()
                     fn = self.get_data_file_path_absolute(fn)
                     self.read_statemod_file_announce1(comp)
                #     self.read_statemod_control_file()
            except Exception as e:
                logger.warning("Unexpected error reading control file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # Control does not have its own data file now so use the data set
                comp.set_data(self)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # River network file (.rin)...

            try:
                fn = response_props.get_value("River_Network")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RIVER_NETWORK)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    comp.set_data(StateMod_RiverNetworkNode.read_statemod_file(fn))
            except Exception as e:
                logger.warning("Unexpected error reading river network file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Reservoir stations file (.res)...

            try:
                fn = response_props.get_value("Reservoir_Station")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_STATIONS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading reservoir station file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Diversion stations file (.dds)...

            try:
                fn = response_props.get_value("Diversion_Station")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DIVERSION_STATIONS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and os.path.getsize(self.get_data_file_path_absolute(fn)):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    comp.set_data(StateMod_Diversion.read_statemod_file(fn))
            except Exception as e:
                logger.warning("Unexpected error reading diversion station file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Stream gage stations file (.ris)...

            try:
                fn = response_props.get_value("StreamGage_Station")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMGAGE_STATIONS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    comp.set_data(StateMod_StreamGage.read_statemod_file(fn))
            except Exception as e:
                logger.warning("Unexpected error reading stream gage station file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                # TODO @jurentie 04/19/2019 - needs updating
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # If not a free-format data set with separate stream estimate station,
            # re-read the legacy stream station file because some stations will be stream estimate stations.
            # If free format, get the file name...

            try:
                fn = response_props.get_value("StreamEstimate_Station")
                # Get from the stream gage component because Ray has not adopted a separate stream
                # estimate file...
                logger.info("Using StreamGage_Station for StreamEstimate_Station (no separate 2nd file).")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMGAGE_STATIONS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading stream estimate station file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Instream flow stations file (.ifs)...

            try:
                fn = response_props.get_value("Instreamflow_Station")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.INSTREAM_STATIONS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading instream flow station file:\n" + "\"" + fn +
                               warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # Control does not have its own data file now so use the data set
                comp.set_data(self)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Well stations..

            try:
                fn = response_props.get_value("Well_Station")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_STATIONS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading well station file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Plans...

            try:
                fn = response_props.get_value("Plan_Data")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.PLANS)
                if comp is None:
                    logger.warning("Unable to look up plans component " + str(StateMod_DataSetComponentType.PLANS))
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading plan data file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Plan well augmentation (.plw)...

            try:
                fn = response_props.get_value("Plan_Wells")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.PLAN_WELL_AUGMENTATION)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading plan wells file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Plan return (.prf)...

            try:
                fn = response_props.get_value("Plan_Return")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.PLAN_RETURN)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading plan return file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Instream flow rights files (.ifr)...

            try:
                fn = response_props.get_value("Instreamflow_Right")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.INSTREAM_RIGHTS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading instream rights file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Reservoir rights file (.rer)...

            try:
                fn = response_props.get_value("Reservoir_Right")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_RIGHTS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading reservoir rights file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Diversion rights file (.ddr)...

            try:
                fn = response_props.get_value("Diversion_Right")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DIVERSION_RIGHTS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    comp.set_data(StateMod_DiversionRight.read_statemod_file(fn))
                    logger.info("Connecting diversion rights to diversion stations")
                    StateMod_Diversion.connect_all_rights(
                        self.get_component_for_component_type(
                            StateMod_DataSetComponentType.DIVERSION_STATIONS).get_data(), comp.get_data()
                    )
            except Exception as e:
                logger.warning("Unexpected error reading diversion rights file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Operational rights file (.opr)...

            try:
                fn = response_props.get_value("Operational_Right")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.OPERATION_RIGHTS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading operational rights file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Well rights file (.wer)...

            try:
                fn = response_props.get_value("Well_Right")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_RIGHTS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading well right file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            try:
                fn = response_props.get_value("Precipitation_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.PRECIPITATION_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn) > 0)):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    self.set_numpre(size)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.PRECIPITATION_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading precipitation (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Precipitation TS yearly file (.pra) - always read...

            try:
                fn = response_props.get_value("Precipitation_Annual")
                # Always set the file name...
                logger.info("StateMod GUI does not yet handle annual precipitation data.")
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.PRECIPITATION_TS_YEARLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    self.set_numpre(size)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.PRECIPITATION_TS_YEARLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading precipitation (annual) file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Evaporation time series file monthly (.eva) - always read...

            try:
                fn = response_props.get_value("Evaporation_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.EVAPORATION_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    self.set_numeva(size)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.EVAPORATION_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading evaporation (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Evaporation time series file yearly (.eva) - always read...

            try:
                fn = response_props.get_value("Evaporation_Annual")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.EVAPORATION_TS_YEARLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    self.set_numeva(size)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.EVAPORATION_TS_YEARLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading evaporation (annual) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Stream gage natural flow time series (.rim or .xbm) - always read...
            comp2 = None
            try:
                fn = response_props.get_value("Stream_Base_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(
                    StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.STREAMGAGE_NATURAL_FLOW_TS_MONTHLY))
                    comp.set_data(v)

                    # The StreamGage and STreamEstimate groups share the same natural flow time series files...

                    comp2 = self.get_component_for_component_type(
                        StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY)
                    comp2.set_data_file_name(comp.get_data_file_name())
                    comp2.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading stream baseflow (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")", exc_info=True)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # Control does not have its own data file now so use the data set
                if comp2 is not None:
                    # Never read data above so no need to call the following
                    comp2.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Diversion direct flow demand time series (monthly) file (.ddm)...

            try:
                fn = response_props.get_value("Diversion_Demand_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DEMAND_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn))):
                    read_time.clear()
                    read_time.start()
                    self.read_statemod_file_announce1(comp)
                    fn = self.get_data_file_path_absolute(fn)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(StateMod_DataSetComponentType.DEMAND_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading diversion demand (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # Control does not have its own data file now so use the data set
                comp.set_data(self)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Direct flow demand time series override (monthly) file (.ddo)...

            try:
                fn = response_props.get_value("Diversion_DemandOverride_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DEMAND_TS_OVERRIDE_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    self.read_statemod_file_announce1(comp)
                    fn = self.get_data_file_path_absolute(fn)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is not None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.DEMAND_TS_OVERRIDE_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading diversion demand override (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Direct flow demand time series average (monthly) file (.dda)...

            try:
                fn = response_props.get_value("Diversion_Demand_AverageMonthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DEMAND_TS_AVERAGE_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    self.read_statemod_file_announce1(comp)
                    fn = self.get_data_file_path_absolute(fn)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is not None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.DEMAND_TS_AVERAGE_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading diversion demand (average monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Monthly instream flow demand...

            try:
                fn = response_props.get_value("Instreamflow_Demand_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn))> 0):
                    read_time.clear()
                    read_time.start()
                    self.read_statemod_file_announce1(comp)
                    fn = self.get_data_file_path_absolute(fn)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading instream flow demand (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Instream demand time series (average monthly) file (.ifa)...

            try:
                fn = response_props.get_value("Instreamflow_Demand_AverageMonthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_AVERAGE_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is not None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_AVERAGE_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading instream flow demand (average monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Well demand time series (monthly) file (.wem)...

            try:
                fn = response_props.get_value("Well_Demand_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_DEMAND_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is not None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.WELL_DEMAND_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading well demand (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Delay file (monthly) file (.dly)

            try:
                fn = response_props.get_value("DelayTable_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DELAY_TABLES_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie read data
            except Exception as e:
                logger.warning("Unexpected error reading delay table (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Reservoir target time series (monthly) file (.tar)...

            try:
                fn = response_props.get_value("Reservoir_Target_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        if (i % 2) == 0:
                            v[i].set_data_type(self.lookup_time_series_data_type(
                                StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_MONTHLY) + "Min")
                        else:
                            v[i].set_data_type(self.lookup_time_series_data_type(
                                StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_MONTHLY) + "Max")
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading reservoir target (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Reservoir return (.rrf)...

            try:
                fn = response_props.get_value("Reservoir_Return")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_RETURN)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and not self.has_sanjuan_data(False) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    logger.warning("Reading Rio Grande Spill file is not enabled.")
                    self.read_statemod_file_announce1(comp)
                    # comp.set_data( StateMod_ReturnFlow.read_statemod_file(fn,
                    #                StateMod_DataSetComponentType.RESERVOIR_RETURN)
            except Exception as e:
                logger.warning("Unexpected error reading reservoir return file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # TODO @jurentie 04/18/2019 - San Juan Sediment Recovery

            try:
                fn = response_props.get_value("SanJuanRecovery")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.SANJUAN_RIP)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # readInputAnnounce1(comp)
                if read_data and (fn is not None) and self.has_sanjuan_data(False) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    logger.warning("Do not know how to read the San Juan Recovery file.")
            except Exception as e:
                logger.warning("Unexpected error reading San Juan Recovery file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                # self.readInputAnnounce2(comp, read_time.get_seconds())

            # TODO @jurentie 04/18/2019 - Enable - Rio Grande Spill

            try:
                fn = response_props.get_value("RioGrande_Spill_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RIO_GRANDE_SPILL)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # readInputAnnounce1(comp)
                if read_data and (fn is not None) and self.has_sanjuan_data(False) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    logger.warning("Reading Rio Grande Spill file is not enabled.")
            except Exception as e:
                logger.warning("Unexpected error reading Rio Grande spill (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                # self.readInputAnnounce2(comp, read_time.get_seconds())

            # Irrigation practice time series (tsp/ipy)...

            try:
                fn = response_props.get_value("IrrigationPractice_Yearly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.IRRIGATION_PRACTICE_TS_YEARLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading irrigation practice (yearly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Irrigation water requirement (iwr) - monthly...

            try:
                fn = response_props.get_value("ConsumptiveWaterRequirement_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(
                    StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading consumptive water requirement (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # StateMod used to read PAR but the AWC is now in the StateCU STR file.

            try:
                fn = response_props.get_value("StateCU_")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_RETURN)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading StateCU file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Soil moisture (*.par) file no longer supported (print a warning)...

            fn = response_props.get_value("SoilMoisture")
            if fn is not None and (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                logger.warning("StateCU soil moisture file - not supported - not reading \"" + fn + "\"")

            # Reservoir content time series (monthly) file (.eom)...

            try:
                fn = response_props.get_value("Reservoir_Historic_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading reservoir historic (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Stream estimate coefficients file (.rib)...

            try:
                fn = response_props.get_value("StreamEstimate_Coefficients")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMESTIMATE_COEFFICIENTS)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading stream estimate coefficients file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Historical streamflow (monthly) file (.rih)...

            try:
                fn = response_props.get_value("StreamGage_Historic_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading stream gage historic (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Diversion time series (historical monthly) file (.ddh)...

            try:
                fn = response_props.get_value("Diversion_Historic_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DIVERSION_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    self.read_statemod_file_announce1(comp)
                    fn = self.get_data_file_path_absolute(fn)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    logger.info("Read " + str(len(v)) + " diversion historic (monthly) time series.")
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.DIVERSION_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading diversion historic (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")",
                               exc_info=True)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Well historical pumping time series (monthly) file (.weh)...

            try:
                fn = response_props.get_value("Well_Historic_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_PUMPING_TS_MONTHLY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                read_time.clear()
                read_time.start()
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.WELL_PUMPING_TS_MONTHLY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading well historic (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # GeoView Project file...

            try:
                fn = response_props.get_value("GeographicInformation")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.GEOVIEW)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                if fn is not None and (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    # readInputAnnounce1(comp)
            except Exception as e:
                logger.warning("Unexpected error reading geographic information file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                # readInputAnnounce2(comp, read_time.get_seconds())
                # Read data and display when the GUI is shown - no read for data to be read if no GUI

            # TODO output control - this is usually read separately when running
            # reports, etc. Just read the line but do not read the file...

            try:
                fn = response_props.get_value("OutputRequest")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.OUTPUT_REQUEST)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # readInputAnnounce1(comp)
            except Exception as e:
                logger.warning("Unexpected error reading output request file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                # readInputAnnounce2(comp, read_time.get_seconds())
                # Read data and display when the GUI is shown - no read for data to be read if no GUI

            # TODO Enable reach data file

            try:
                fn = response_props.get_value("Reach_Data")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.REACH_DATA)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # readInputAnnounce1(comp, read_time.get_seconds())
                if read_data and (fn is not None) and (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    logger.warning("Reach data file - not yet supported.")
            except Exception as e:
                logger.warning("Unexpected error reading reach data file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                # readInputAnnounce2(comp, read_time.get_seconds())

            # Stream natural flow flow time series (daily) file (.rid)...
            # Always read if a daily set.
            try:
                fn = response_props.get_value("Stream_Base_Daily")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMGAGE_NATURAL_FLOW_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.STREAMGAGE_NATURAL_FLOW_TS_MONTHLY))
                    comp.set_data(v)

                    # The StreamGage and StreamEstimate groups share the same natural flow time series files...

                    comp2 = self.get_component_for_component_type(
                        StateMod_DataSetComponentType.STREAMESTIMATE_NATURAL_FLOW_TS_DAILY)
                    comp2.set_data_file_name(comp.get_data_file_name())
                    comp2.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading stream baseflow (daily) file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                if comp2 is not None:
                    # Never read data above so no need to call the following
                    comp2.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Direct diversion demand time series (daily) file (.ddd)...

            try:
                fn = response_props.get_value("Diversion_Demand_Daily")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DEMAND_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(StateMod_DataSetComponentType.DEMAND_TS_DAILY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading diversion demand (daily) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Instream flow demand time series (daily) file (.ifd)...

            try:
                fn = response_props.get_value("Instreamflow_Demand_Daily")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.INSTREAM_DEMAND_TS_DAILY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading instream flow demand (daily) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Well demand time series (daily) file (.wed)...

            try:
                fn = response_props.get_value("Well_Demand_Daily")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_DEMAND_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.WELL_DEMAND_TS_DAILY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading well demand (daily) file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Reservoir target time series (daily) file (.tad)...

            try:
                fn = response_props.get_value("Reservoir_Target_Daily")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        if (i % 2) == 0:
                            v[i].set_data_type(self.lookup_time_series_data_type(
                                               StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_DAILY) + "Min")
                        else:
                            v[i].set_data_type(self.lookup_time_series_data_type(
                                               StateMod_DataSetComponentType.RESERVOIR_TARGET_TS_DAILY) + "Max")
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading reservoir target (daily) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Delay table (daily)...

            try:
                fn = response_props.get_value("DelayTable_Daily")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DELAY_TABLES_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading delay table (daily) file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Irrigation water requirement (.iwr) - daily...

            try:
                fn = response_props.get_value("ConsumptiveWaterRequirement_Daily")
                # Always set the file name...
                comp = self.get_component_for_component_type(
                    StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading consumptive water requirement (daily) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Streamflow historical time series (daily) file (.riy) - always read...

            try:
                fn = response_props.get_value("StreamGage_Historic_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        # Set this information because it is not in the StateMod time series file...
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.STREAMGAGE_HISTORICAL_TS_DAILY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading stream gage historic (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Diversion (daily) time series (.ddd)...

            try:
                fn = response_props.get_value("Diversion_Historic_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DIVERSION_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    # Set the data type because it is not in the StateMod file...
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(StateMod_DataSetComponentType.DIVERSION_TS_DAILY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading diversion historic (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Well pumping (daily) time series...
            try:
                fn = response_props.get_value("Well_Historic_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.WELL_PUMPING_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.WELL_PUMPING_TS_DAILY))
                    comp.set_data(v)
            except Exception as e:
                logger.warning("Unexpected error reading well historic (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Daily reservoir content "eoy" ...

            try:
                fn = response_props.get_value("Reservoir_Historic_Monthly")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                if read_data and self.read_time_series and (fn is not None) and \
                        (os.path.getsize(self.get_data_file_path_absolute(fn)) > 0):
                    read_time.clear()
                    read_time.start()
                    fn = self.get_data_file_path_absolute(fn)
                    self.read_statemod_file_announce1(comp)
                    v = StateMod_TS.read_time_series_list(fn, None, None, None, True)
                    if v is None:
                        v = []
                    size = len(v)
                    for i in range(size):
                        v[i].set_data_type(self.lookup_time_series_data_type(
                                           StateMod_DataSetComponentType.RESERVOIR_CONTENT_TS_DAILY))
            except Exception as e:
                logger.warning("Unexpected error reading reservoir historic (monthly) file:\n" + "\"" +
                               fn + warning_end_string + " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Downstream call (.cal)...

            try:
                fn = response_props.get_value("Downstream_Call")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.DOWNSTREAM_CALL_TS_DAILY)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading downstream call file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())

            # Keep track of files/properties that are not explicitly handled in this class
            # These may be new files added to the model, old files being phased out, or simple properties.
            unhandled_response_file_properties = self.get_unhandled_response_file_properties()
            unhandled_response_file_properties.clear()
            for prop in response_props.get_list():
                file_key = prop.get_key()
                # See if the key is matched in the known StateMod file type keys...
                found = False
                for file in self.statemod_file_properties:
                    if file_key == file:
                        found = True
                        break
                if not found:
                    # The file property was not found so need to carry around as unknown
                    logger.info("Unhandled response file property: " + prop.get_key() + " = " + prop.get_value())
                    unhandled_response_file_properties.set(prop)

            logger.info("DataSet: \n" + self.to_string_definitions())

            total_read_time.stop()
            logger.info("Total time to read StateMod files is " + "{:3f} ".format(total_read_time.get_seconds()) +
                        "seconds")
            total_read_time.start()

            logger.info("Reading generalized network.")

            try:
                fn = response_props.get_value("Network")
                # Always set the file name...
                comp = self.get_component_for_component_type(StateMod_DataSetComponentType.NETWORK)
                if comp is not None and fn is not None:
                    comp.set_data_file_name(fn)
                # Read the data...
                # TODO @jurentie 04/18/2019 - read the data
            except Exception as e:
                logger.warning("Unexpected error reading network file:\n" + "\"" + fn + warning_end_string +
                               " See log file for more on error:" + str(e) + ")")
                logger.warning(e)
                comp.set_error_reading_input_file(True)
            finally:
                comp.set_dirty(False)
                # read_time.stop()
                self.read_statemod_file_announce2(comp, read_time.get_seconds())
        except Exception as e:
            # Main catch for all reads
            message = "Unexpected error during read."
            logger.warning(message, exc_info=True)
            # TODO Just rethrow for now
            raise

        # Set component visibility based on the control information...
        self.check_component_visibility()

        total_read_time.stop()
        msg = "Total time to read all files is {:3f} seconds".format(total_read_time.get_seconds())
        logger.info(msg)
        # self.sendProcessListenerMessage(22, msg)
        self.set_dirty(StateMod_DataSetComponentType.CONTROL, False)

    def read_statemod_file_announce1(self, comp):
        """
        This method is a helper routine to read_statemod_file().  It calls
        Message.printStatus() with the message that a particular file is being read,
        including path.  Then it prints a similar, but shorter,
        message to the status bar.  If there is an error with the file (not specified,
        does not exist, etc.), then an Exception is thrown.  There are many StateMod
        files and therefore the same basic checks are done many times.
        :param comp: Data set component that is being read.
        """
        logger = logging.getLogger(__name__)
        fn = self.get_data_file_path_absolute(comp)
        description = comp.get_component_name()

        if (fn is None) or (len(fn) == 0):
            logger.warning(description + " file name unavailable")
        # TODO - need to know whether this is an error that the user should acknowledge...
        # TODO - error handling

        msg = "Reading " + description + " data from \"" + fn + "\""
        # The status message is printed because process listeners may not be registered.
        logger.info(msg)
        # self.sendProcessListenerMessage( StateMod_GUIUtil.STATUS_READ_START, msg)

    def read_statemod_file_announce2(self, comp, seconds):
        """
        This method is a helper routine to read_statemod_file().  It calls
        Message.printStatus() with the message that a file has been read successively.
        Then it prints a similar, but shorter, message to the status bar.
        :param comp: Component being read.
        :param seconds: Number of seconds to read.
        """
        logger = logging.getLogger(__name__)
        fn = self.get_data_file_path_absolute(comp)
        description = comp.get_component_name()

        # The status message is printed because process listeners may not be registered.
        msg = description + " data read from \"" + fn + "\" in " + str("{:3f}".format(seconds)) + " seconds"
        logger.info(msg)

    def set_numeva(self, numeva):
        """
        Set number of evaporation stations.
        :param numeva: number of stations
        """
        if numeva != self.numeva:
            self.numeva = numeva
            self.set_dirty(StateMod_DataSetComponentType.CONTROL, True)

    def set_numpre(self, numpre):
        """
        Set number of precipition stations.
        :param numpre: number of stations
        """
        if numpre != self.numpre:
            self.numpre = numpre
            self.set_dirty(StateMod_DataSetComponentType.CONTROL, True)

    def to_string_definitions(self):
        """
        Return a string representation of the data set definition information, useful for troubleshooting
        """
        nl = os.path.sep
        s = ""
        for i in range(len(self.component_names)):
            comp = self.get_component_for_component_type(i)
            s += "[{}]".format(i) + " Name=\"" + self.component_names[i]
            s += "\" Group={}".format(self.component_group_assignments[i])
            s += " RspProperty=\"" + self.statemod_file_properties[i]
            s += "\" Filename=\"" + comp.get_data_file_name()
            s += "\" Ext=\"" + self.component_file_extensions[i]
            s += "\" TSType=\"" + self.component_ts_data_types[i]
            s += "\" TSInt={}".format(self.component_ts_data_intervals[i])
            s += " TSUnits=\"" + self.component_ts_data_units[i] + "\"\n"
        return s
