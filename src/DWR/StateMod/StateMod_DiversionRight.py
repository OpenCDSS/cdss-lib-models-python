# StateMod_DiversionRight - class for diversion station rights

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

from DWR.StateMod.StateMod_Data import StateMod_Data
from DWR.StateMod.StateMod_DataSet import StateMod_DataSet
# from DWR.StateMod.StateMod_Util import StateMod_Util

from RTi.Util.String.StringUtil import StringUtil


class StateMod_DiversionRight(StateMod_Data):

    def __init__(self):

        # Administration number.
        self.irtem = None

        # Decreed amount
        self.dcrdiv = None

        # ID, Name, and Cgoto are in the base class.

        # Initialize data
        self.initialize_statemod_diversionright()

        # Call parent constructor
        super().__init__()

    def initialize_statemod_diversionright(self):
        """
        Initialize data members.
        """
        self.smdata_type = StateMod_DataSet.COMP_DIVERSION_RIGHTS
        self.irtem = "99999"
        self.dcridiv = 0

    @staticmethod
    def read_statemod_file(filename):
        """
        Parses the diversion rights file and returns a vector of StateMod_DiversionRight objects.
        :param filename: the diversion rights file to parse
        :return: a Vector of StateMod_DiversionRight objects.
        """
        logger = logging.getLogger(__name__)
        the_div_rights = []

        format_0 = [
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_DOUBLE,
            StringUtil.TYPE_INTEGER
        ]

        format_0w = [
            12,
            24,
            12,
            16,
            8,
            8
        ]

        iline = None
        v = []
        a_right = None

        logger.info("Reading diversion rights file: " + filename)

        try:
            with open(filename) as f:
                for iline in f:
                    # Check for comments
                    if (iline.startswith("#")) or (len(iline.strip()) == 0):
                        continue

                    a_right = StateMod_DiversionRight()

                    StringUtil.fixed_read2(iline, format_0, format_0w, v)
                    a_right.set_id(v[0].strip())
                    a_right.set_name(v[1].strip())
                    a_right.set_cgoto(v[2].strip())
                    a_right.set_irtem(v[3].strip())
                    a_right.set_dcrciv(float(v[4]))
                    a_right.set_switch(int(v[5]))
                    # Mark as clean because set methods may have marked dirty...
                    a_right.set_dirty(False)
                    the_div_rights.append(a_right)
        except Exception as e:
            logger.warning(e)
        return the_div_rights

    def set_dcrciv(self, dcrdiv):
        """
        Set the decreed amount
        """
        if dcrdiv != self.dcrdiv:
            self.dcrdiv = dcrdiv
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSet.COMP_DIVERSION_RIGHTS, True)

    def set_irtem(self, irtem):
        """
        Set the administration number.
        """
        if irtem is None:
            return
        if not irtem == self.irtem:
            self.irtem = irtem.strip()
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSet.COMP_DIVERSION_RIGHTS, True)
