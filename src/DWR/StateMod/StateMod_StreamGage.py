# StateMod_StreamGage - class to store stream gage data

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

# ------------------------------------------------------------------------------
#  StateMod_StreamGage - class derived from StateMod_Data.  Contains
# 	information the stream gage station file (.ris).
# ------------------------------------------------------------------------------
#  Copyright:	See the COPYRIGHT file.
# ------------------------------------------------------------------------------
#  History:
#
#  02 Sep 1997	Catherine E.		Created initial version of class.
# 		Nutting-Lane, RTi
#  23 Feb 1998	Catherine E.		Added write routines.
# 		Nutting-Lane, RTi
#  21 Dec 1998	CEN, RTi		Added throws IOException to read/write
# 					routines.
#  06 Feb 2001	Steven A. Malers, RTi	Update to handle new daily data.  Also,
# 					Ray added a gwmaxr data item to the
# 					.rin file.  Consequently, this
# 					StateMod_RiverInfo class can not be
# 					shared as
# 					transparently between .rin and .ris
# 					files.  Probably need to make this a
# 					base class and derive SMStation (or
# 					similar) from it, but for now just put
# 					specific .rin and .ris data here and use
# 					a flag to indicate which is used.  Need
# 					some help from Catherine to clean up at
# 					some point.  Update javadoc as I go
# 					through and figure things out.  Add
# 					finalize method and set unused data to
# 					null to help garbage collection.
# 					Alphabetize methods.  Optimize loops so
# 					size() is not called each iteration.
# 					Check for null arguments.  Change some
# 					low-level status messages to debug
# 					messages to improve performance.
# 					Optimize lookups by using _id rather
# 					than calling getID().  There are still
# 					places (like cases where strings are
# 					manipulated without checking for null)
# 					where error handling is not complete but
# 					leave for now since it seems to be
# 					working.  Use trim() instead of
# 					StringUtil to simplify code.  Add line
# 					cound to read routine to print in
# 					error message.  Remove all "additional
# 					string" code in favor of specific data
# 					since Ray is beginning to add to files
# 					in inconsistent ways.  Change IO to
# 					IOUtil.  Add constructor to parse a
# 					string and handle the setrin() syntax
# 					used by makenet.  This allows the
# 					StateMod_RiverInfo object to store set
# 					information with not much more work.
# 					Add applySetRinCommands() to apply
# 					edits.
#  2001-12-27	SAM, RTi		Update to use new fixedRead() to
# 					improve performance.
#  2002-09-12	SAM, RTi		Add the baseflow time series (.xbm or
# 					.rim) to this class for the (.ris) file
# 					display.  Remove the overloaded
# 					connectAllTS() that only handled monthly
# 					time series.  One version of the method
# 					should be ok since the StateMod GUI is
# 					the only thing that uses it.
# 					Also add the daily baseflow time series
# 					corresponding to the .rid file.
#  2002-09-19	SAM, RTi		Use isDirty() instead of setDirty() to
# 					indicate edits.
#  2002-10-07	SAM, RTi		Add GeoRecord reference to allow 2-way
# 					connection between spatial and StateMod
# 					data.
# ------------------------------------------------------------------------------
#  2003-06-04	J. Thomas Sapienza, RTi	Renamed from SMRiverInfo
#  2003-06-10	JTS, RTi		* Folded dumpRiverInfoFile() into
# 					  writeRiverInfoFile()
# 					* Renamed parseRiverInfoFile() to
# 					  readRiverInfoFile()
#  2003-06-23	JTS, RTi		Renamed writeRiverInfoFile() to
# 					writeStateModFile()
#  2003-06-26	JTS, RTi		Renamed readRiverInfoFile() to
# 					readStateModFile()
#  2003-07-30	SAM, RTi		* Split river station code out of
# 					  StateMod_RiverInfo into this
# 					  StateMod_RiverStation class to make
# 					  management of data cleaner.
# 					* Change isDirty() back to setDirty().
#  2003-08-28	SAM, RTi		* Clean up time series data members and
# 					  methods.
# 					* Clean up parameter names.
# 					* Call setDirty() on each object in
# 					  addition to the data set component.
#  2003-09-11	SAM, RTi		Rename from StateMod_RiverStation to
# 					StateMod_StreamGage and make
# 					appropriate changes throughout.
#  2004-03-15	JTS, RTi		Added in some old member variables for
# 					use with writing makenet files:
# 					* _comment
# 					* _node
# 					* setNode()
# 					* applySetRinCommands()
# 					* applySetRisCommands()
# 					* _gwmaxr_string
#  2004-07-06	SAM, RTi		* Overload the constructor to allow
# 					  initialization to reasonable defaults
# 					  or missing.
# 					* Remove the above code from Tom since
# 					  these features are either from Makenet
# 					  (and now in StateDMI) and meant for
# 					  the StateMod_RiverNetworkNode class.
#  2004-07-10	SAM, RTi		Add the _related_smdata_type and
# 					_related_smdata_type2 data members.
# 					This allows the node types to
# 					be set when the list of stream estimate
# 					stations is read from the network file.
# 					This allows the node type to be properly
# 					set for the last 3 characters in the
# 					name, as has traditionally been done.
# 					This change is made for stream gage and
# 					stream estimate stations because in
# 					order to support old data sets, the
# 					stream estimate stations are combined
# 					with stream gage stations.
#  2004-07-14	JTS, RTi		* Added acceptChanges().
# 					* Added changed().
# 					* Added clone().
# 					* Added compareTo().
# 					* Added createBackup().
# 					* Added restoreOriginal().
# 					* Now implements Cloneable.
# 					* Now implements Comparable.
# 					* Clone status is checked via _isClone
# 					  when the component is marked as dirty.
#  2005-04-18	JTS, RTi		Added writeListFile().
#  2007-04-12	Kurt Tometich, RTi		Added checkComponentData() and
# 									getDataHeader() methods for check
# 									file and data check support.
#  2007-03-01	SAM, RTi		Clean up code based on Eclipse feedback.
# ------------------------------------------------------------------------------
#  EndHeader

import logging

import DWR.StateMod.StateMod_Data as StateMod_Data
import DWR.StateMod.StateMod_DataSet as StateMod_DataSet

from RTi.Util.String.StringUtil import StringUtil


class StateMod_StreamGage(StateMod_Data.StateMod_Data):

    def __init__(self, initialize_defaults=None):
        # Monthly historical TS from the .rih file that is associated with the
        # .ris station - only streamflow gages in the .ris have these data.
        self._historical_MonthTS = None

        # Monthly base flow time series, for use with the river station (.ris)
        # file, read from the .xbm/.rim file.
        self._baseflow_MonthTS = None

        # Daily base flow time series, read from the .rid file.
        self._baseflow_DayTS = None

        # Daily historical TS from the .riy file that is associated with the .ris
        # station - only streamflow gages in the .riy have these data
        self._historical_DayTS = None

        # Used with .ris (columnh 4) - daily stream station identifier
        self._crunidy = str()

        # Reference to spatial data for this river station. Currently not cloned.
        # self._gerecord = None

        # The StateMod_DataSet component type for the node. At some point the related object
        # reference may also be added, but there are cases when this is not known (only the type is known,
        # for example in StateDMI).
        self._related_smdata_type = int()

        # Second related type. This is only used for D&W node types and should be set to the well
        # stations component type.
        self._related_smdata_type2 = int()

        if initialize_defaults is None:
            initialize_defaults = True

        super().__init__()
        self.initializeStreamGage(initialize_defaults)

    def initializeStreamGage(self, initialize_defaults):
        """
        Initialize data.
        :param initialize_defaults: If true, the time series are set to null and other
        information to empty strings or other reasonable defaults - this is suitable
        for the StateMod GUI when creating new instances.  If false, the
        data values are set to missing - this is suitable for use with StateDMI, where
        data will be filled with commands.
        """
        self._smdata_type = StateMod_DataSet.StateMod_DataSet().COMP_STREAMGAGE_STATIONS
        self._cgoto = ""
        self._historical_MonthTS = None
        self._historical_DayTS = None
        self._baseflow_MonthTS = None
        self._baseflow_DayTS = None
        if initialize_defaults:
            # Set the reasonable defaults...
            self._crunidy = "0"  # Use monthly data
        else:
            # Initialize to missing
            self._crunidy = ""
        # self._gerecord = None

    def acceptChanges(self):
        """
        Accepts any changes made inside of a GUI to this object.
        :return:
        """
        self._isClone = False
        self._original = None

    @staticmethod
    def readStateModFile(filename):
        """
        Read the stream gage station file and store return a Vector of StateMod_StreamGage.
        :param filename: Name of file to read.
        :return: a list of StateMod_StreamGage.
        """
        logger = logging.getLogger("StateMod")
        routine = "StateMod_StreamGage.readStateModFile"
        theRivs = []
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
                    aRiverNode = StateMod_StreamGage()

                    v = ["elaphant"]
                    # line 1
                    StringUtil.fixedRead(iline, format_0, format_0w, v)
                    aRiverNode.setID(v[0].strip())
                    aRiverNode.setName(v[1].strip())
                    aRiverNode.setCgoto(v[2].strip())
                    # Space
                    aRiverNode.setCrunidy(v[4].strip())

                    # add the node to the vector of river nodes
                    theRivs.append(aRiverNode)
        except Exception as e:
            # Clean up...
            logger.warning("Error reading \"{}\" at line {}".format(filename, linecount))

        return theRivs


    def setBaseflowDay(self, ts):
        """
        Set the daily baseflow TS.
        :param ts: daily baseflow ts
        """
        self._baseflow_DayTS = ts

    def setBaseflowMonthTS(self, ts):
        """
        Set the monthly baseflow TS.
        :param ts: monthly baseflow ts.
        :return:
        """
        self._baseflow_MonthTS = ts

    def setCgoto(self, cgoto):
        """
        Set the river node identifier.
        :param cgoto: River node identifier.
        """
        if (cgoto is not None) and (cgoto != self._cgoto):
            self._cgoto = cgoto
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(self._smdata_type, True)

    def setCrunidy(self, crunidy):
        """
        Set the daily stream station for the node.
        :param crundiy: Daily station identifier for node.
        """
        if (crunidy is not None) and (crunidy != crunidy):
            self._crunidy = crunidy
            self.setDirty(True)
            if (not self._isClone) and (self._dataset != None):
                self._dataset.setDirty(self._smdata_type, True)

    def setHistoricalDayTS(self, ts):
        """
        Set the daily historical TS pointer.
        :param ts: historical monthly TS.
        """
        self._historical_MonthTS = ts

    def setRelatedSMDataType(self, related_smdata_type):
        """
        Set the StateMod_DataSet component type for the data for this node.
        :param related_smdata_type: The StateMod_DataSet component type for the data for this node.
        """
        self._related_smdata_type = related_smdata_type

    def setRelatedSMDataType2(self, related_smdata_type2):
        """
        Set the second StateMod_DataSet component type for the data for this node.
        :param related_smdata_type2: The second StateMod_DataSet component type for the data for this node.
        This is only used for D&W nodes and should be set to the well component type.
        """
        self._related_smdata_type2 = related_smdata_type2