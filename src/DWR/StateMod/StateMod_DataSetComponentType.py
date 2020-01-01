# StateMod_DataSetComponentType - StateMod component types

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

from enum import Enum


class StateMod_DataSetComponentType(Enum):
    """
    Enumeration for StateMod components, which typically correspond to model input files.
    These used to be defined in StateMod_DataSet but cause a circular dependency in Python.
    Therefore, define as an enumeration that is referenced in a non-circular way.
    """

    # Use for initialization, if needed.
    UNKNOWN = -1
    # Used when defining other nodes in the network, via the GUI.
    OTHER_NODE = -5

    CONTROL_GROUP = 0
    RESPONSE = 1
    CONTROL = 2
    OUTPUT_REQUEST = 3
    REACH_DATA = 4

    CONSUMPTIVE_USE_GROUP = 5
    STATECU_STRUCTURE = 6
    IRRIGATION_PRACTICE_TS_YEARLY = 7
    CONSUMPTIVE_WATER_REQUIREMENT_TS_MONTHLY = 8
    CONSUMPTIVE_WATER_REQUIREMENT_TS_DAILY = 9

    STREAMGAGE_GROUP = 10
    STREAMGAGE_STATIONS = 11
    STREAMGAGE_HISTORICAL_TS_MONTHLY = 12
    STREAMGAGE_HISTORICAL_TS_DAILY = 13
    STREAMGAGE_NATURAL_FLOW_TS_MONTHLY = 14
    STREAMGAGE_NATURAL_FLOW_TS_DAILY = 15

    DELAY_TABLE_MONTHLY_GROUP = 16
    DELAY_TABLES_MONTHLY = 17

    DELAY_TABLE_DAILY_GROUP = 18
    DELAY_TABLES_DAILY = 19

    DIVERSION_GROUP = 20
    DIVERSION_STATIONS = 21
    DIVERSION_STATION_DELAY_TABLES = 2101
    DIVERSION_STATION_COLLECTIONS = 2102
    DIVERSION_RIGHTS = 22
    DIVERSION_TS_MONTHLY = 23
    DIVERSION_TS_DAILY = 24
    DEMAND_TS_MONTHLY = 25
    DEMAND_TS_OVERRIDE_MONTHLY = 26
    DEMAND_TS_AVERAGE_MONTHLY = 27
    DEMAND_TS_DAILY = 28

    PRECIPITATION_GROUP = 29
    PRECIPITATION_TS_MONTHLY = 30
    PRECIPITATION_TS_YEARLY = 31

    EVAPORATION_GROUP = 32
    EVAPORATION_TS_MONTHLY = 33
    EVAPORATION_TS_YEARLY = 34

    RESERVOIR_GROUP = 35
    RESERVOIR_STATIONS = 36
    RESERVOIR_STATION_ACCOUNTS = 3601
    RESERVOIR_STATION_PRECIP_STATIONS = 3602
    RESERVOIR_STATION_EVAP_STATIONS = 3603
    RESERVOIR_STATION_CURVE = 3604
    RESERVOIR_STATION_COLLECTIONS = 3605
    RESERVOIR_RIGHTS = 37
    RESERVOIR_CONTENT_TS_MONTHLY = 38
    RESERVOIR_CONTENT_TS_DAILY = 39
    RESERVOIR_TARGET_TS_MONTHLY = 40
    RESERVOIR_TARGET_TS_DAILY = 41
    RESERVOIR_RETURN = 42

    INSTREAM_GROUP = 43
    INSTREAM_STATIONS = 44
    INSTREAM_RIGHTS = 45
    INSTREAM_DEMAND_TS_MONTHLY = 46
    INSTREAM_DEMAND_TS_AVERAGE_MONTHLY = 47
    INSTREAM_DEMAND_TS_DAILY = 48

    WELL_GROUP = 49
    WELL_STATIONS = 50
    WELL_STATION_DELAY_TABLES = 5001
    WELL_STATION_DEPLETION_TABLES = 5002
    WELL_STATION_COLLECTIONS = 5003
    WELL_RIGHTS = 51
    WELL_PUMPING_TS_MONTHLY = 52
    WELL_PUMPING_TS_DAILY = 53
    WELL_DEMAND_TS_MONTHLY = 54
    WELL_DEMAND_TS_DAILY = 55

    PLAN_GROUP = 56
    PLANS = 57
    PLAN_WELL_AUGMENTATION = 58
    PLAN_RETURN = 59

    STREAMESTIMATE_GROUP = 60
    STREAMESTIMATE_STATIONS = 61
    STREAMESTIMATE_COEFFICIENTS = 62
    STREAMESTIMATE_NATURAL_FLOW_TS_MONTHLY = 63
    STREAMESTIMATE_NATURAL_FLOW_TS_DAILY = 64

    RIVER_NETWORK_GROUP = 65
    RIVER_NETWORK = 66
    NETWORK = 67

    OPERATION_GROUP = 68
    OPERATION_RIGHTS = 69
    DOWNSTREAM_CALL_TS_DAILY = 70
    SANJUAN_RIP = 71
    RIO_GRANDE_SPILL = 72

    GEOVIEW_GROUP = 73
    GEOVIEW = 74

    def __str__(self):
        """
        Format the enumeration as a string - just return the name.
        @returns Enumeration as a string.
        """
        return self.name
