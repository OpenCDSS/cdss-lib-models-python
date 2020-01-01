# StateMod_ReturnFlow - store and manipulate return flow assignments

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

import DWR.StateMod.StateMod_Data as StateMod_Data


class StateMod_ReturnFlow(StateMod_Data):
    """
    <p>
    This class stores return flow assignments.  A list of instances is maintained for each StateMod_Diversion
    and StateMod_Well (included in station files) and separate files for reservoirs and plans.
    Each instance indicates the river node receiving the return flow, percent of the flow going to the node, and
    the delay table identifier to use for the time distribution of the flow.
    </p>
    <p>
    The StateMod_Data ID is the station for which the return flow applies.
    </p>
    """

    def __init__(self, smdata_type):
        # River node receiving the return flow.
        self.crtnid = None

        # % of return flow to this river node.
        self.pcttot = None

        # Delay (return q) table for return.
        self.irtndl = None

        # Indicates whether the returns are for daily (false) or monthly (true) data.
        self.is_monthly_data = None

        super().__init__()
        self.smdata_type = smdata_type
        self.intitialize_statemod_returnflow()

    def intitialize_statemod_returnflow(self):
        self.crtnid = ""
        self.pcttot = 100
        self.irtndl = 1

    def set_crtnid(self, s):
        """
        Set the crtnid
        """
        if s is not None:
            if not (s == self.crtnid):
                self.set_dirty(True)
                if (not self.is_clone) and (self.dataset is not None):
                    self.dataset.set_dirty(self.smdata_type, True)
                self.crtnid = s

    def set_pcttot(self, d):
        if d != self.pcttot:
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)
            self.pcttot = d

    def set_irtndl(self, i):
        """
        Set the delay table for return.
        """
        if i != self.irtndl:
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)
            self.irtndl = i
