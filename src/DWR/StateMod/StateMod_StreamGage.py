# StateMod_StreamGage - class to store stream gage data (.ris)

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

from DWR.StateMod.StateMod_Data import StateMod_Data
from DWR.StateMod.StateMod_DataSet import StateMod_DataSet

from RTi.Util.String.StringUtil import StringUtil


class StateMod_StreamGage(StateMod_Data):

    def __init__(self, initialize_defaults=None):
        # Monthly historical TS from the .rih file that is associated with the
        # .ris station - only streamflow gages in the .ris have these data.
        self.historical_monthts = None

        # Monthly base flow time series, for use with the river station (.ris)
        # file, read from the .xbm/.rim file.
        self.baseflow_monthts = None

        # Daily base flow time series, read from the .rid file.
        self.baseflow_dayts = None

        # Daily historical TS from the .riy file that is associated with the .ris
        # station - only streamflow gages in the .riy have these data
        self.historical_dayts = None

        # Used with .ris (columnh 4) - daily stream station identifier
        self.crunidy = None

        # Reference to spatial data for this river station. Currently not cloned.
        # self.gerecord = None

        # The StateMod_DataSet component type for the node. At some point the related object
        # reference may also be added, but there are cases when this is not known (only the type is known,
        # for example in StateDMI).
        self.related_smdata_type = None

        # Second related type. This is only used for D&W node types and should be set to the well
        # stations component type.
        self.related_smdata_type2 = None

        if initialize_defaults is None:
            initialize_defaults = True

        super().__init__()
        self.initialize_streamgage(initialize_defaults)

    def initialize_streamgage(self, initialize_defaults):
        """
        Initialize data.
        :param initialize_defaults: If true, the time series are set to null and other
        information to empty strings or other reasonable defaults - this is suitable
        for the StateMod GUI when creating new instances.  If false, the
        data values are set to missing - this is suitable for use with StateDMI, where
        data will be filled with commands.
        """
        self.smdata_type = StateMod_DataSet.COMP_STREAMGAGE_STATIONS
        self.cgoto = ""
        self.historical_monthts = None
        self.historical_dayts = None
        self.baseflow_monthts = None
        self.baseflow_dayts = None
        if initialize_defaults:
            # Set the reasonable defaults...
            self.crunidy = "0"  # Use monthly data
        else:
            # Initialize to missing
            self.crunidy = ""
        # self.gerecord = None

    def accept_changes(self):
        """
        Accepts any changes made inside of a GUI to this object.
        :return:
        """
        self.is_clone = False
        self.original = None

    @staticmethod
    def read_statemod_file(filename):
        """
        Read the stream gage station file and store return a Vector of StateMod_StreamGage.
        :param filename: Name of file to read.
        :return: a list of StateMod_StreamGage.
        """
        logger = logging.getLogger(__name__)
        the_rivs = []
        iline = str()
        v = []
        format_0 = [int()] * 5
        format_0[0] = StringUtil.TYPE_STRING
        format_0[1] = StringUtil.TYPE_STRING
        format_0[2] = StringUtil.TYPE_STRING
        format_0[3] = StringUtil.TYPE_STRING
        format_0[4] = StringUtil.TYPE_STRING
        format_0w = [int()] * 5
        format_0w[0] = 12
        format_0w[1] = 24
        format_0w[2] = 12
        format_0w[3] = 1
        format_0w[4] = 12
        linecount = 0

        try:
            with open(filename) as f:
                for iline in f:
                    iline.strip()
                    linecount += 1
                    # Check for comments
                    if iline.startswith("#") or (len(iline.strip()) == 0):
                        continue

                    # allocate new StateMod_StreamGage node
                    a_river_node = StateMod_StreamGage()

                    v = ["elaphant"]
                    # line 1
                    StringUtil.fixed_read2(iline, format_0, format_0w, v)
                    a_river_node.set_id(v[0].strip())
                    a_river_node.set_name(v[1].strip())
                    a_river_node.set_cgoto(v[2].strip())
                    # Space
                    a_river_node.set_crunidy(v[4].strip())

                    # add the node to the vector of river nodes
                    the_rivs.append(a_river_node)
        except Exception as e:
            # Clean up...
            logger.warning("Error reading \"{}\" at line {}".format(filename, linecount))

        return the_rivs

    def set_baseflow_dayts(self, ts):
        """
        Set the daily baseflow TS.
        :param ts: daily baseflow ts
        """
        self.baseflow_dayts = ts

    def set_baseflow_monthts(self, ts):
        """
        Set the monthly baseflow TS.
        :param ts: monthly baseflow ts.
        :return:
        """
        self.baseflow_monthts = ts

    def set_cgoto(self, cgoto):
        """
        Set the river node identifier.
        :param cgoto: River node identifier.
        """
        if (cgoto is not None) and (cgoto != self.cgoto):
            self.cgoto = cgoto
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)

    def set_crunidy(self, crunidy):
        """
        Set the daily stream station for the node.
        :param crunidy: Daily station identifier for node.
        """
        if (crunidy is not None) and (crunidy != crunidy):
            self.crunidy = crunidy
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)

    def set_historical_dayts(self, ts):
        """
        Set the daily historical TS pointer.
        :param ts: historical monthly TS.
        """
        self.historical_monthts = ts

    def set_related_smdata_type(self, related_smdata_type):
        """
        Set the StateMod_DataSet component type for the data for this node.
        :param related_smdata_type: The StateMod_DataSet component type for the data for this node.
        """
        self.related_smdata_type = related_smdata_type

    def set_related_smdata_type2(self, related_smdata_type2):
        """
        Set the second StateMod_DataSet component type for the data for this node.
        :param related_smdata_type2: The second StateMod_DataSet component type for the data for this node.
        This is only used for D&W nodes and should be set to the well component type.
        """
        self.related_smdata_type2 = related_smdata_type2
