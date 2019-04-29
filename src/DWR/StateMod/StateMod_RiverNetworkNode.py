# StateMod_RiverNetworkNode - class to store network node data

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
# StateMod_RiverNetworkNode - class derived from StateMod_Data.  Contains
#	information read from the river network file
#------------------------------------------------------------------------------
# Copyright:	See the COPYRIGHT file.
#------------------------------------------------------------------------------
# History:
#
# 02 Sep 1997	Catherine E.		Created initial version of class.
#		Nutting-Lane, RTi
# 23 Feb 1998	Catherine E.		Added write routines.
#		Nutting-Lane, RTi
# 21 Dec 1998	CEN, RTi		Added throws IOException to read/write
#					routines.
# 06 Feb 2001	Steven A. Malers, RTi	Update to handle new daily data.  Also,
#					Ray added a gwmaxr data item to the
#					.rin file.  Consequently, this
#					StateMod_RiverInfo class can not be
#					shared as
#					transparently between .rin and .ris
#					files.  Probably need to make this a
#					base class and derive SMStation (or
#					similar) from it, but for now just put
#					specific .rin and .ris data here and use
#					a flag to indicate which is used.  Need
#					some help from Catherine to clean up at
#					some point.  Update javadoc as I go
#					through and figure things out.  Add
#					finalize method and set unused data to
#					null to help garbage collection.
#					Alphabetize methods.  Optimize loops so
#					size() is not called each iteration.
#					Check for null arguments.  Change some
#					low-level status messages to debug
#					messages to improve performance.
#					Optimize lookups by using _id rather
#					than calling getID().  There are still
#					places (like cases where strings are
#					manipulated without checking for null)
#					where error handling is not complete but
#					leave for now since it seems to be
#					working.  Use trim() instead of
#					StringUtil to simplify code.  Add line
#					cound to read routine to print in
#					error message.  Remove all "additional
#					string" code in favor of specific data
#					since Ray is beginning to add to files
#					in inconsistent ways.  Change IO to
#					IOUtil.  Add constructor to parse a
#					string and handle the setrin() syntax
#					used by makenet.  This allows the
#					StateMod_RiverInfo object to store set
#					information with not much more work.
#					Add applySetRinCommands() to apply
#					edits.
# 2001-12-27	SAM, RTi		Update to use new fixedRead() to
#					improve performance.
# 2002-09-12	SAM, RTi		Add the baseflow time series (.xbm or
#					.rim) to this class for the (.ris) file
#					display.  Remove the overloaded
#					connectAllTS() that only handled monthly
#					time series.  One version of the method
#					should be ok since the StateMod GUI is
#					the only thing that uses it.
#					Also add the daily baseflow time series
#					corresponding to the .rid file.
# 2002-09-19	SAM, RTi		Use isDirty() instead of setDirty() to
#					indicate edits.
# 2002-10-07	SAM, RTi		Add GeoRecord reference to allow 2-way
#					connection between spatial and StateMod
#					data.
#------------------------------------------------------------------------------
# 2003-06-04	J. Thomas Sapienza, RTi	Renamed from SMrivInfo
# 2003-06-10	JTS, RTi		* Folded dumpRiverInfoFile() into
#					  writeRiverInfoFile()
#					* Renamed parseRiverInfoFile() to
#					  readRiverInfoFile()
# 2003-06-23	JTS, RTi		Renamed writeRiverInfoFile() to
#					writeStateModFile()
# 2003-06-26	JTS, RTi		Renamed readRiverInfoFile() to
#					readStateModFile()
# 2003-07-30	SAM, RTi		* Change name of class from
#					  StateMod_RiverInfo to
#					  StateMod_RiverNetworkNode.
#					* Remove all code related to the RIS
#					  file, which is now in
#					  StateMod_RiverStation.
#					* Change isDirty() back to setDirty().
# 2003-08-28	SAM, RTi		* Call setDirty() on each object in
#					  addition to the data set component.
#					* Clean up javadoc and parameters.
# 2004-07-10	SAM, RTi		Add the _related_smdata_type and
#					_related_smdata_type2 data members.
#					This allows the node types to
#					be set when the list of stream estimate
#					stations is read from the network file.
#					This allows the node type to be properly
#					set for the last 3 characters in the
#					name, as has traditionally been done.
#					This change is made for stream gage and
#					stream estimate stations because in
#					order to support old data sets, the
#					stream estimate stations are combined
#					with stream gage stations.
# 2004-07-14	JTS, RTi		* Added acceptChanges().
#					* Added changed().
#					* Added clone().
#					* Added compareTo().
#					* Added createBackup().
#					* Added restoreOriginal().
#					* Now implements Cloneable.
#					* Now implements Comparable.
#					* Clone status is checked via _isClone
#					  when the component is marked as dirty.
# 2005-04-18	JTS, RTi		Added writeListFile().
# 2005-06-13	JTS, RTi		Made a new toString().
# 2007-03-01	SAM, RTi		Clean up code based on Eclipse feedback.
#------------------------------------------------------------------------------
# EndHeader

import logging

import DWR.StateMod.StateMod_Data as StateMod_Data
import DWR.StateMod.StateMod_DataSet as StateMod_DataSet

from RTi.Util.String.StringUtil import StringUtil

class StateMod_RiverNetworkNode(StateMod_Data.StateMod_Data):
    """
    This StateMod_RiverNetworkNode class manages a record of data from the StateMod
    river network (.rin) file.  It is derived from StateMod_Data similar to other
    StateMod data objects.  It should not be confused with network node objects
    (e.g., StateMod_Diversion_Node).   See the readStateModFile() method to read
    the .rin file into a true network.
    """

    def __init__(self):

        # Downstream node identifier - third column of files.
        self._cstadn = str()

        # Used with .rin (column 4) - not really used anymore except by old watright code.
        self._comment = str()

        # Reference to spatial data for this diversion -- currently NOT cloned.  If null, then no spatial data
        # are available.
        self._georecord = None

        # used with .rin (column 5) - ground water maximum recharge limit.
        self._gwmaxr = float()

        # The StateMod_DataSet component type for the node.  At some point the related object reference
        # may also be added, but there are cases when this is not known (only the type is
        # known, for example in StateDMI).
        self._related_smdata_type = int()

        # Second related type.  This is only used for D&W node types and should
        # be set to the well stations component type.
        self._related_smdata_type2 = int()

        super().__init__()
        self.initialize_StateMod_RiverNetworkNode()

    def initialize_StateMod_RiverNetworkNode(self):
        """
        Initialize data.
        """
        self._cstadn = ""
        self._comment = ""
        self._gwmaxr = -999
        self._smdata_type = StateMod_DataSet.StateMod_DataSet.COMP_RIVER_NETWORK

    @staticmethod
    def readStateModFile(filename):
        """
        Read river network or stream gage information and return a list of StateMod_RiverNetworkNode.
        :param filename: Name of file to read.
        """
        logger = logging.getLogger("StateMod")
        routine = "StateMod_RiverNetworkNode.readStateModFile"
        theRivs = []
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
                    aRiverNode = StateMod_RiverNetworkNode()

                    # line 1
                    StringUtil.fixedRead2(iline, format_0, format_0w, v)
                    aRiverNode.setID(v[0].strip())
                    aRiverNode.setName(v[1].strip())
                    # 3 is whitespace
                    # Expect that we also may have the comment and possibly the gwmaxr value...
                    aRiverNode.setComment(v[4].strip())
                    # 5 is whitespace
                    s = v[6].strip()
                    if len(s) > 0:
                        aRiverNode.setGwmaxr(float(s))

                    theRivs.append(aRiverNode)
        except Exception as e:
            logger.warning("Error reading \"{}\" at line {}".format(filename, linecount))
        return theRivs

    def setComment(self, comment):
        """
        Set the comment for use with the network file.
        :param comment: Comment for node
        """
        if (comment is not None) and (self._comment != comment):
            self._comment = comment
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(self._smdata_type, True)

    def setCstadn(self, cstadn):
        """
        Set the downstream river node identifier
        :param cstadn: Downstream river node identifier.
        """
        if (cstadn is not None) and (cstadn != self._cstadn):
            self._cstadn = cstadn
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(self._smdata_type, True)

    def setGwmaxr(self, gwmaxr):
        """
        Set the maximum recharge limit for network file.
        :param gwmaxr: Maximum recharge limit.
        """
        if self._gwmaxr != gwmaxr:
            self._gwmaxr = gwmaxr
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(self._smdata_type, True)