# StateMod_ReturnFlow - store and manipulate return flow assignments

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

#------------------------------------------------------------------------------
# StateMod_ReturnFlow - store and manipulate return flow assignments
#------------------------------------------------------------------------------
# Copyright:	See the COPYRIGHT file.
#------------------------------------------------------------------------------
# History:
#
# 27 Aug 1997	Catherine E.		Created initial version of class.
#		Nutting-Lane, RTi
# 18 Oct 1999	CEN, RTi		Because this is now being used for both
#					diversions and wells, I am adding a
#					constructor that indicates that any
#					changes affects a particular file
#					(default remains StateMod_DataSet.
#					COMP_DIVERSION_STATIONS).
# 17 Feb 2001	Steven A. Malers, RTi	Code review.  Clean up javadoc.  Add
#					finalize().  Alphabetize methods.
#					Handle nulls and set unused variables
#					to null.
# 2002-09-19	SAM, RTi		Use isDirty()instead of setDirty()to
#					indicate edits.
# 2003-08-03	SAM, RTi		Changed isDirty() back to setDirty().
# 2003-09-30	SAM, RTi		* Fix bug where initialize was not
#					  getting called.
#					* Change _dirtyFlag to use the base
#					  class _smdata_type.
# 2003-10-09	J. Thomas Sapienza, RTi	* Implemented Cloneable.
#					* Added clone().
#					* Added equals().
#					* Implemented Comparable.
#					* Added compareTo().
#					* Added equals(Vector, Vector).
#					* Added isMonthly_data().
# 2003-10-15	JTS, RTi		Revised the clone() code.
# 2004-07-14	JTS, RTi		Changed compareTo to account for
#					crtnids that have descriptions, too.
# 2005-01-17	JTS, RTi		* Added createBackup().
#					* Added restoreOriginal().
# 2005-04-15	JTS, RTi		Added writeListFile().
#------------------------------------------------------------------------------

import DWR.StateMod.StateMod_Data as StateMod_Data


class StateMod_ReturnFlow(StateMod_Data.StateMod_Data):
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

    def __init__(self, smdataType):
        # River node receiving the return flow.
        self.__crtnid = str()

        # % of return flow to this river node.
        self.__pcttot = float()

        # Delay (return q) table for return.
        self.__irtndl = int()

        # Indicates whether the returns are for daily (false) or monthly (true) data.
        self.__isMonthlyData = bool()

        super().__init__()
        self._smdata_type = smdataType
        self.initialize_StateMod_ReturnFlow()

    def initialize_StateMod_ReturnFlow(self):
        self.__crtnid = ""
        self.__pcttot = 100
        self.__irtndl = 1

    def setCrtnid(self, s):
        """
        Set the crtnid
        """
        if s is not None:
            if not (s == self.__crtnid):
                self.setDirty(True)
                if (not self._isClone) and (self._dataset is not None):
                    self._dataset.setDirty(self._smdata_type, True)
                self.__crtnid = s

    def setPcttot(self, d):
        if d != self.__pcttot:
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(self._smdata_type, True)
            self.__pcttot = d

    def setIrtndl(self, i):
        """
        Set the delay table for return.
        """
        if i != self.__irtndl:
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(self._smdata_type, True)
            self.__irtndl = i