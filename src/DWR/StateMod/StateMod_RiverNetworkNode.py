# StateMod_RiverNetworkNode - class to store network node data

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
from DWR.StateMod.StateMod_DataSetComponentType import StateMod_DataSetComponentType

from RTi.Util.String.StringUtil import StringUtil


class StateMod_RiverNetworkNode(StateMod_Data):
    """
    This StateMod_RiverNetworkNode class manages a record of data from the StateMod
    river network (.rin) file.  It is derived from StateMod_Data similar to other
    StateMod data objects.  It should not be confused with network node objects
    (e.g., StateMod_Diversion_Node).   See the read_statemod_file() method to read
    the .rin file into a true network.
    """

    def __init__(self):

        # Downstream node identifier - third column of files.
        self.cstadn = None

        # Used with .rin (column 4) - not really used anymore except by old watright code.
        self.comment = None

        # Reference to spatial data for this diversion -- currently NOT cloned.  If null, then no spatial data
        # are available.
        self.georecord = None

        # used with .rin (column 5) - ground water maximum recharge limit.
        self.gwmaxr = None

        # The StateMod_DataSet component type for the node.  At some point the related object reference
        # may also be added, but there are cases when this is not known (only the type is
        # known, for example in StateDMI).
        self.related_smdata_type = None

        # Second related type.  This is only used for D&W node types and should
        # be set to the well stations component type.
        self.related_smdata_type2 = None

        super().__init__()
        self.initialize_statemod_rivernetworknode()

    def initialize_statemod_rivernetworknode(self):
        """
        Initialize data.
        """
        self.cstadn = ""
        self.comment = ""
        self.gwmaxr = -999
        self.smdata_type = StateMod_DataSetComponentType.RIVER_NETWORK

    @staticmethod
    def read_statemod_file(filename):
        """
        Read river network or stream gage information and return a list of StateMod_RiverNetworkNode.
        :param filename: Name of file to read.
        """
        logger = logging.getLogger(__name__)
        the_rivs = []
        inline = str()
        s = str()
        v = []

        format_0 = [
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING
        ]

        format_0w = [
            12,
            24,
            12,
            1,
            12,
            1,
            8
        ]

        linecount = 0

        try:
            with open(filename) as f:
                for iline in f:
                    linecount += 1
                    # Check for comments
                    if (iline.startswith("#")) or (len(iline.strip()) == 0):
                        continue

                    # allocate new StateMod_RiverNetworkNode
                    a_river_node = StateMod_RiverNetworkNode()

                    # line 1
                    StringUtil.fixed_read2(iline, format_0, format_0w, v)
                    a_river_node.set_id(v[0].strip())
                    a_river_node.set_name(v[1].strip())
                    # 3 is whitespace
                    # Expect that we also may have the comment and possibly the gwmaxr value...
                    a_river_node.set_comment(v[4].strip())
                    # 5 is whitespace
                    s = v[6].strip()
                    if len(s) > 0:
                        a_river_node.set_gwmaxr(float(s))

                    the_rivs.append(a_river_node)
        except Exception as e:
            logger.warning("Error reading \"{}\" at line {}".format(filename, linecount))
        return the_rivs

    def set_comment(self, comment):
        """
        Set the comment for use with the network file.
        :param comment: Comment for node
        """
        if (comment is not None) and (self.comment != comment):
            self.comment = comment
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)

    def set_cstadn(self, cstadn):
        """
        Set the downstream river node identifier
        :param cstadn: Downstream river node identifier.
        """
        if (cstadn is not None) and (cstadn != self.cstadn):
            self.cstadn = cstadn
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)

    def set_gwmaxr(self, gwmaxr):
        """
        Set the maximum recharge limit for network file.
        :param gwmaxr: Maximum recharge limit.
        """
        if self.gwmaxr != gwmaxr:
            self.gwmaxr = gwmaxr
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)
