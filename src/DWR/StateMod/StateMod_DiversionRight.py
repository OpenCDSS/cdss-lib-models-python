# StateMod_Diversion - class for diversion station

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
# StateMod_DiversionRight - Derived from SMData class
#------------------------------------------------------------------------------
# Copyright:	See the COPYRIGHT file.
#------------------------------------------------------------------------------
# History:
#
# 27 Aug 1997	Catherine E.		Created initial version of class
#		Nutting-Lane, RTi
# 11 Feb 1998	Catherine E.		Added SMFileData.setDirty to all set
#		Nutting-Lane, RTi	routines.  Added throws IOException to
#					read/write routines
# 16 Feb 2001	Steven A. Malers, RTi	Update output header to be consistent
#					with new documentation.  Add finalize().
#					Alphabetize methods.  Set unused
#					variables to null.  Handle null
#					arguments.  Change IO to IOUtil.  Get
#					rid of low-level debugs that are not
#					needed.
# 02 Mar 2001	SAM, RTi		Ray says to use F16.0 for rights and
#					get rid of the 4x.
# 2001-12-27	SAM, RTi		Update to use new fixedRead()to
#					improve performance.
# 2002-09-19	SAM, RTi		Use isDirty()instead of setDirty()to
#					indicate edits.
#------------------------------------------------------------------------------
# 2003-06-04	J. Thomas Sapienza, RTi	Renamed from SMDivRights to
#					StateMod_DiversionRight
# 2003-06-10	JTS, RTi		* Folded dumpDiversionRightsFile() into
#					  writeDiversionRightsFile()
#					* Renamed parseDiversionRightsFile() to
#					  readDiversionRightsFile()
# 2003-06-23	JTS, RTi		Renamed writeDiversionRightsFile() to
#					writeStateModFile()
# 2003-06-26	JTS, RTi		Renamed readDiversionRightsFile() to
#					readStateModFile()
# 2003-07-07	SAM, RTi		Check for null data set to allow the
#					code to be used outside of a full
#					StateMod data set implementation.
# 2003-07-15	JTS, RTi		Changed code to use new dataset design.
# 2003-08-03	SAM, RTi		Changed isDirty() back to setDirty().
# 2003-08-27	SAM, RTi		Change default value of irtem to
#					99999.
# 2003-08-28	SAM, RTi		* Remove linked list logic since a
#					  Vector of rights is now maintained in
#					  StateMod_Diversion.
#					* Call setDirty() on the individual
#					  objects as well as the component.
#					* Clean up Javadoc for parameters to
#					  make more readable.
# 2003-10-09	JTS, RTi		* Implemented Cloneable.
#					* Added clone().
#					* Added equals().
#					* Implemented Comparable.
#					* Added compareTo().
# 2003-10-10	JTS, RTI		Added equals(Vector, Vector)
# 2003-10-14	JTS, RTi		* Make sure diversion right is marked
#					  not dirty after initial read and
#					  construction.
# 2003-10-15	JTS, RTi		Revised the clone() code.
# 2004-10-28	SAM, RTi		Add getIdvrswChoices() and
#					getIdvrswDefault().
# 2005-01-13	JTS, RTi		* Added createBackup().
# 					* Added restoreOriginal().
# 2005-03-13	SAM, RTi		* Clean up output header information for
#					  switch.
# 2007-04-12	Kurt Tometich, RTi		Added checkComponentData() and
#									getDataHeader() methods for check
#									file and data check support.
# 2007-03-01	SAM, RTi		Clean up code based on Eclipse feedback.
# 2007-05-16	SAM, RTi		Implement StateMod_Right interface.
#------------------------------------------------------------------------------
# EndHeader

import logging

import DWR.StateMod.StateMod_Data as StateMod_Data
import DWR.StateMod.StateMod_DataSet as StateMod_DataSet
import DWR.StateMod.StateMod_Util as StateMod_Util

from RTi.Util.String.StringUtil import StringUtil


class StateMod_DiversionRight(StateMod_Data.StateMod_Data):

    def __init__(self):

        # Administration number.
        self._irtem = str()

        # Decreed amount
        self._dcrdiv = float()

        # ID, Name, and Cgoto are in the base class.

        # Initialize data
        self.initialize_StateMod_DiversionRight()

        # Call parent constructor
        super().__init__()

    def initialize_StateMod_DiversionRight(self):
        """
        Initialize data members.
        """
        self._smdata_type = StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_RIGHTS
        self._irtem = "99999"
        self._dcridiv = 0

    @staticmethod
    def readStateModFile(filename):
        """
        Parses the diversion rights file and returns a vector of StateMod_DiversionRight objects.
        :param filename: the diversion rights file to parse
        :return: a Vector of StateMod_DiversionRight objects.
        """
        logger = logging.getLogger("StateMod")
        routine = "StateMod_DiversionRight.readStateModFile"
        theDivRights = []

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
        aRight = None

        logger.info("Reading diversion rights file: " + filename)

        try:
            with open(filename) as f:
                for iline in f:
                    # Check for comments
                    if (iline.startswith("#")) or (len(iline.strip()) == 0):
                        continue

                    aRight = StateMod_DiversionRight()

                    StringUtil.fixedRead2(iline, format_0, format_0w, v)
                    aRight.setID(v[0].strip())
                    aRight.setName(v[1].strip())
                    aRight.setCgoto(v[2].strip())
                    aRight.setIrtem(v[3].strip())
                    aRight.setDcrdiv(float(v[4]))
                    aRight.setSwitch(int(v[5]))
                    # Mark as clean because set methods may have marked dirty...
                    aRight.setDirty(False)
                    theDivRights.append(aRight)
        except Exception as e:
            logger.warning(e)
        return theDivRights

    def setDcrdiv(self, dcrdiv):
        """
        Set the decreed amount
        """
        if dcrdiv != self._dcrdiv:
            self._dcrdiv = dcrdiv
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_RIGHTS, True)

    def setIrtem(self, irtem):
        """
        Set the administration number.
        """
        if irtem is None:
            return
        if not irtem == self._irtem:
            self._irtem = irtem.strip()
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_RIGHTS, True)