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
# StateMod_Diversion - class derived from StateMod_Data.  Contains information
#			read from the diversion file.
#------------------------------------------------------------------------------
# Copyright:	See the COPYRIGHT file.
#------------------------------------------------------------------------------
# History:
#
# 19 Aug 1997	Catherine E.
#		Nutting-Lane, RTi	Created initial version of class
# 27 Mar 1998	CEN, RTi		Added pointers to TS.
# 06 Apr 1998	CEN, RTi		Added java style documentation.
# 21 Dec 1998	CEN, RTi		Added throws IOException to read/write
#					routines.
# 25 Oct 1999	CEN, RTi		Added daily diversion id.
#
# 01 Dec 1999	Steven A. Malers, RTi	Change so that connectAllTS is
#					overloaded to work the old way(no daily
#					time series)and with daily time series.
# 15 Feb 2001	SAM, RTi		Add use_daily_data flag to write methods
#					to allow writing old format files.
#					Change IO to IOUtil.  Add finalize();
#					Alphabetize methods.  Set unused
#					variables to null.  Add more checks for
#					null.  Update file output header.
#					In dumpDiversionsFile, reuse the vector
#					for output, optimize output formats
#					(don't need to format blank strings),
#					and remove debug statements.
# 2001-12-27	SAM, RTi		Update to use new fixedRead()to
#					improve performance.
# 2002-09-09	SAM, RTi		Add GeoRecord reference to allow 2-way
#					connection between spatial and StateMod
#					data.
# 2002-09-19	SAM, RTi		Use isDirty()instead of setDirty()to
#					indicate edits.
#					dds file.
#------------------------------------------------------------------------------
# 2003-06-04	J. Thomas Sapienza, RTi	Renamed from SMDiversion to
#					StateMod_Diversion
# 2003-06-10	JTS, RTi		* Folded dumpDiversionsFile() into
#					  writeDiversionsFile()
#					* Renamed parseDiversionsFile() to
#					  readDiversionsFile()
# 2003-06-23	JTS, RTi		Renamed writeDiversionsFile() to
#					writeStateModFile()
# 2003-06-26	JTS, RTi		Renamed readDiversionsFile() to
#					readStateModFile()
# 2003-08-03	SAM, RTi		Change isDirty() to setDirty().
# 2003-08-14	SAM, RTi		Change GeoRecordNoSwing to GeoRecord.
# 2003-08-27	SAM, RTi		* Change default for cdividy to "0".
#					* Rework time series data members and
#					  methods to have better names,
#					  consistent with the data set
#					  components.
#					* Change so water rights are stored in
#					  a Vector, not an internally-maintained
#					  linked-list.
#					* Add all diversion data for the current
#					  StateMod design so that nothing is
#					  left out.
#					* Change connectDivRights() to
#					  connectRights().
#					* Change connectAllDivRights() to
#					  connectAllRights().
#					* Allow case-independent searches for
#					  time series identifiers.
#					* In addition to calling setDirty() on
#					  the data set component, do so on the
#					  individual objects.
#					* Clean up Javadoc.
#					* Remove data members for size of
#					  Vectors - the size can be determined
#					  from the Vectors.  Nduser is no longer
#					  used so don't need in any case.  Still
#					  output to allow file comparisons.
# 2003-09-30	SAM, RTi		Pass component type to
#					StateMod_ReturnFlow constructor.
# 2003-10-07	SAM, RTi		* As per Ray Bennett, default the demand
#					  source to 0, Unknown.
#					* Similarly, default efficiency is 60.
# 2003-10-10	SAM, RTi		Add disconnectRights().
# 2003-10-14	SAM, RTi		* Add a copy constructor for use by the
#					  StateMod_Diversion_JFrame to track
#					  edits.
#					* Change IWR to CWR (irrigation to
#					  consumptive) as per Ray Bennett
#					  feedback.
#					* Set the diversion dirty to false after
#					  read or construction - it may have
#					  been marked dirty with set() methods.
# 2003-10-21	SAM, RTi		Change demand override average monthly
#					to demand average monthly - more
#					consistent with documentation.
# 2004-02-25	SAM, RTi		Add isStateModDiversionFile().
# 2004-03-31	SAM, RTi		Print the line number and line when an
#					error occurs reading the file.
# 2004-04-12	SAM, RTi		* Change so read and write methods
#					  convert file paths using working
#					  directory.
# 2004-06-05	SAM, RTi		* Add methods to handle collections,
#					  similar to StateCU locations.
#					* Define static values here, that are
#					  possible values for some data members.
#					  These values were previously defined
#					  in StateMod_Diversion_JFrame.
#					* Add methods to retrieve the option
#					  strings.
# 2004-06-14	SAM, RTi		* Define public final int's for
#					  important demsrc values to help with
#					  StateDMI.
#					* Overload the constructor to allow
#					  initialization as completely missing
#					  or with reasonable defaults.  The
#					  former is better for StateDMI, the
#					  latter for StateMod GUI.
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
# 2004-08-16	SAM, RTi		* Output old Nduser as 1 instead of 0
#					  since that is what old files have.
# 2004-09-01	SAM, RTi		* Add the following for use with
#					  StateDMI only - no need to check for
#					  dirty - only set/gets on the entire
#					  array are enabled:
#						__cwr_monthly
#						__ddh_monthly
#						__calculated_efficiencies
#						__calculated_efficiency_stddevs
#						__model_efficiecies
# 2004-09-06	SAM, RTi		* Add "MultiStruct" to the types of
#					  collection.
# 2005-03-30	JTS, RTi		* Added getCollectionPartType().
#					* Added getCollectionYears().
# 2005-04-14	JTS, RTi		Added writeListFile().
# 2005-04-19	JTS, RTi		Added writeCollectionListFile().
# 2005-15-16	SAM, RTi		Overload setDiveff() to accept a
#					parameter indicating the year type of
#					the diversion stations file, to simplify
#					adjustments for water year, etc.
# 2006-04-09	SAM, RTi		Add _parcels_Vector data member and
#					associated methods, to help with
#					StateDMI error handling.
# 2007-04-12	Kurt Tometich, RTi		Added checkComponentData() and
#									getDataHeader() methods for check
#									file and data check support.
# 2007-03-01	SAM, RTi		Clean up code based on Eclipse feedback.
#------------------------------------------------------------------------------
# EndHeader
# REVISIT SAM 2006-04-09
# The _parcel_Vector has minimal support and is not yet considered in
# copy, clone, equals, etc.

import logging
import re

import DWR.StateMod.StateMod_Data as StateMod_Data
import DWR.StateMod.StateMod_DataSet as StateMod_DataSet
# import DWR.StateMod.StateMod_ReturnFlow as StateMod_ReturnFlow
import DWR.StateMod.StateMod_Util as StateMod_Util
import DWR.StateMod.StateMod_StreamGage as StateMod_StreamGage

from RTi.Util.String.StringUtil import StringUtil
from DWR.StateMod.StateMod_ReturnFlow import StateMod_ReturnFlow


class StateMod_Diversion(StateMod_Data.StateMod_Data):
    """
    Object used to store diversion information.  All set routines set
    the COMP_DIVERSION_STATIONS flag dirty.  A new object will have empty non-null
    lists, null time series, and defaults for all other data.
    """

    # Demand source values used by other software. Most interaction is expected to occur through GUIs.
    DEMSRC_UNKNOWN = 0
    DEMSRC_GIS = 1
    DEMSRC_TIA = 2
    DEMSRC_GIS_PRIMARY = 3
    DEMSRC_TIA_PRIMARY = 4
    DEMSRC_GIS_SECONDARY = 5
    DEMSRC_MI_TRANSBASIN = 6
    DEMSRC_CARRIER = 7
    DEMSRC_USER = 8

    # Collection are set up to be specified by year, although currently for
    # diversion collections are always the same for the full period.

    # Types of collections.  An aggregate merges the water rights whereas
    # a system keeps all the water rights but just has one ID.  See email from Erin
    # Wilson 2004-09-01, to reiterate current modeling procedures:
    # <pre>
    # <ol>
    # <li>Multistructure should be used to represent two or more structures
    # that divert from DIFFERENT TRIBUTARIES to serve the same demand
    # (irrigated acreage or M&I demand).  In the Historic model used to
    # estimate Baseflows, the historic diversions need to be represented on
    # the correct tributary, so all structures are in the network.  Average
    # efficiencies need to be set for these structures, since IWR has been
    # assigned to only one structure.  In Baseline and Calculated mode, the
    # multistruct(x,x) command will assign all demand to the primary structure
    # and zero out the demand for the secondary structures.  Water rights will
    # continue to be assigned to each individual structure, and operating
    # rules need to be included to allow the model to divert from the
    # secondary structure location (under their water right) to meet the
    # primary structure demand.</li>
    # <li>Divsystems should be used to represents two or more structures with
    # intermingled lands and/or diversions that divert from the SAME
    # TRIBUTARY.  Only the primary structure should be included in the
    # network.  The Divsystem(x,x) command will combine historic diversions,
    # capacities, and acreages for use in the Historic model and to create
    # Baseflows.  Water rights for all structures will be assigned explicitly
    # to the primary structure.  No operating rules or set efficiency commands are required.</li>
    # <li>Aggregates.  The only difference between Divsystems and Aggregates
    # is that the water rights are not necessarily assigned explicitly, but
    # are generally grouped into water rights classes.</li>
    COLLECTION_TYPE_AGGREGATE = "Aggregate"
    COLLECTION_TYPE_SYSTEM = "System"
    COLLECTION_TYPE_MULTISTRUCT = "MultiStruct"

    def __init__(self, initialize_defaults=None):
        # Daily diversion ID
        self._cdividy = str()

        # Diversion capacity
        self._divcap = int()

        # User name
        self._username = str()

        # data type switch
        self._idvcom = int()

        # System efficiency switch
        self._divefc = float()

        # Efficiency % by month. The efficiencies are in order of the calendar for
        # the data set. Therefore, for proper display, the calendar type must be known.
        self._diveff = []

        # The following are used only by StateDMI and do not need to be handled in comparison,
        # initialization, etc.
        self.__calculated_efficiencies = None
        self.__calculated_efficiency_stddevs = None
        self.__model_efficiencies = None

        # irrigated acreage, future
        self._area = float()

        # use type
        self._irturn = int()

        # river nodes receiving return flow
        self._rivret = []

        # direct diversions rights
        self._rights = []

        # Acreage source
        self._demsrc = int()

        # Replacement code
        self._ireptype = int()

        # Pointer to monthly demand ts.
        #self._demand_MonthTS = MonthTS()

        # Pointer to monthly demand override ts.
        #self._demand_override_MonthTS = MonthTS()

        # Pointer to average monthly demand override ts.
        #self._demand_average_MonthTS = MonthTS()

        # Pointer to daily demand ts.
        #self._demand_DayTS = DayTS()

        # Pointer to historical monthly diversion ts.
        #self._diversion_MonthTS = MonthTS()

        # 12 monthly and annual average over period, used by StateDMI.
        self.__ddh_monthly = None

        # Pointer to monthly consumptive water requirement ts.
        #self._cwr_MonthTS = MonthTS()

        # 12 monthly and annual average over period, used by StateDMI
        self._cwr_monthly = None

        # Pointer to daily consumptive water requirement ts.
        #self._swr_DayTS = DayTS()

        # Pointer to the StateCU_IrrigationPracticeTS. This object actually contains other time series,
        # which can be retrieved for displays.
        #self._ipy_YearTS = StateCU_IrrigationPracticeTS()

        # Soil available water content, from StateCU file.
        self._awc = float()

        # Reference to spatial data for this diversion -- currently NOT cloned. If null, then no spatial
        # are available
        #self._georecord = GeoRecord()

        # List of parcel data, in particular to allow StateDMI to detect when a diversion had no data.
        self._parcel_Vector = []

        self.__collection_type = StateMod_Util.StateMod_Util.MISSING_STRING

        # Used by DMI software - currently no options.
        self.__collection_part_type = "Ditch"

        # The identifiers for data that are collected - null if not a collection location.
        # This is a list of lists where the __collection_year is the first dimension.
        # This is ugly but need to use the code to see if it can be made cleaner.
        self.__collection_Vector = None

        # An array of year that correspond to the aggregate/system. Ditches currently only have one year.
        self.__collection_year = None

        # Constructor
        if initialize_defaults is not None:
            self.initialize_StateMod_Diversion(initialize_defaults)
        else:
            self.initialize_StateMod_Diversion(True)

        super().__init__()

    def initialize_StateMod_Diversion(self, initialize_defaults):
        """
        Initialize data. Sets the smdata_type to _dataset.COMP_DIVERSION_STATIONS.
        :param initialize_defaults: If True, assign data to reasonable defaults.
        If False, all data are set to missing.
        """
        self._smdata_type = StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS
        if initialize_defaults:
            self._divefc = -60.0
            self._diveff = [float()] * 12
            for i, diveff in enumerate(self._diveff):
                self._diveff[i] = 60.0
            self._username = ""
            self._cdividy = "0"  # Use the average monthly TS for daily TS
            self._divcap = 0
            self._idvcom = 1
            self._area = 0
            self._irturn = 1
            self._demsrc = StateMod_Diversion.DEMSRC_UNKNOWN
            self._ireptype = -1  # Provide depletion replacement
        else:
            self._divefc = StateMod_Util.StateMod_Util.MISSING_DOUBLE
            self._diveff = [float()] * 12
            for i, diveff in enumerate(self._diveff):
                self._diveff[i] = StateMod_Util.StateMod_Util.MISSING_DOUBLE
            self._username = StateMod_Util.StateMod_Util.MISSING_STRING
            self._cdividy = StateMod_Util.StateMod_Util.MISSING_INT
            self._idvcom = StateMod_Util.StateMod_Util.MISSING_INT
            self._area = StateMod_Util.StateMod_Util.MISSING_DOUBLE
            self._irturn = StateMod_Util.StateMod_Util.MISSING_INT
            self._demsrc = StateMod_Util.StateMod_Util.MISSING_INT
            self._ireptype = StateMod_Util.StateMod_Util.MISSING_INT
        self._rivret = []
        self._rights = []
        #self._diversion_MonthTS = None
        #self._diversion_DayTS = None
        #self._demand_MonthTS = None
        #self._demand_override_MonthTS = None
        #self._demand_average_MonthTS = None
        #self._demand_DayTS = None
        #self._ipy_YearTS = None
        #self._cwr_MonthTS = None
        #self._cwr_DayTS = None
        #self._georecord = None

    def addReturnFlow(self, rivret):
        """
        Add return flow node to the vector of return flow nodes.
        :param rivret: riveret return flow
        """
        pass

    @staticmethod
    def connectAllRights(diversions, rights):
        if (diversions is None) or (rights is None):
            return
        num_divs = len(diversions)

        for i in range(num_divs):
            div = diversions[i]
            if div is not None:
                continue
            div.connectRights(rights)

    def getDivcap(self):
        """
        :return: the diversion capacity
        """
        return self._divcap

    def getDivefc(self):
        """
        :return: the system efficiency switch
        """
        return self._divefc

    @staticmethod
    def readStateModFile(filename):
        """
        Read return information in and store in a list.
        :param filename: filename containing return flow information
        """
        logger = logging.getLogger("StateMod")
        routine = "StateMod_Diversion.readStateModFile"
        iline = None
        v = []
        theDiversions = []
        i = int()
        linecount = 0
        s = None

        format_0 = [
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_INTEGER,
            StringUtil.TYPE_DOUBLE,
            StringUtil.TYPE_INTEGER,
            StringUtil.TYPE_INTEGER,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING
        ]

        format_0w = [
            12,
            24,
            12,
            8,
            8,
            8,
            8,
            1,
            12
        ]

        format_1 = [
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_INTEGER,
            StringUtil.TYPE_INTEGER,
            StringUtil.TYPE_DOUBLE,
            StringUtil.TYPE_DOUBLE,
            StringUtil.TYPE_INTEGER,
            StringUtil.TYPE_INTEGER
        ]

        format_1w = [
            12,
            24,
            12,
            8,
            8,
            8,
            8,
            8,
            8
        ]

        format_2 = [
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_STRING,
            StringUtil.TYPE_DOUBLE,
            StringUtil.TYPE_INTEGER
        ]

        format_2w = [
            36,
            12,
            8,
            8
        ]

        aDiversion = None
        aReturnNode = None

        try:
            with open(filename) as f:
                lines = f.readlines()
                i = -1
                while i < len(lines) - 1:
                    i+=1
                    iline = lines[i]
                    linecount += 1
                    # check for comments
                    if (iline.startswith('#')) or (len(iline.strip()) == 0):
                        continue

                    # Allocate new diversion node
                    aDiversion = StateMod_Diversion()

                    # line 1
                    StringUtil.fixedRead2(iline, format_0, format_0w, v)
                    aDiversion.setID(v[0].strip())
                    aDiversion.setName(v[1].strip())
                    aDiversion.setCgoto(v[2].strip())
                    aDiversion.setSwitch(int(v[3]))
                    aDiversion.setDivcap(float(v[4]))
                    aDiversion.setIreptype(int(v[6]))
                    aDiversion.setCdividy(v[8].strip())

                    # line 2
                    i += 1
                    iline = lines[i]
                    linecount += 1
                    StringUtil.fixedRead2(iline, format_1, format_1w, v)
                    aDiversion.setUsername(v[1].strip())
                    aDiversion.setIdvcom(int(v[3]))
                    nrtn = int(v[4])
                    aDiversion.setDivefc(float(v[5]))
                    aDiversion.setArea(float(v[6]))
                    aDiversion.setIrturn(int(v[7]))
                    aDiversion.setDemsrc(int(v[8]))

                    # Get the efficiency information
                    if aDiversion.getDivefc() < 0:
                        # Negative value indicates monthly efficiencies will follow...
                        i += 1
                        iline = lines[i]
                        linecount += 1
                        # Free format...
                        chars = [' ', '\t', '\n', '\r', '\f']
                        split = re.split(' +|\n|\t|\r|\f', iline)
                        split = split[1:len(split)-1]
                        if (split is not None) and len(split) == 12:
                            for j, nextToken in enumerate(split):
                                aDiversion.setDiveff(j, nextToken)
                    else:
                        # Annual efficiency so set monthly efficiencies to the annual...
                        aDiversion.setDiveff(0, aDiversion.getDivefc())
                        aDiversion.setDiveff(1, aDiversion.getDivefc())
                        aDiversion.setDiveff(2, aDiversion.getDivefc())
                        aDiversion.setDiveff(3, aDiversion.getDivefc())
                        aDiversion.setDiveff(4, aDiversion.getDivefc())
                        aDiversion.setDiveff(5, aDiversion.getDivefc())
                        aDiversion.setDiveff(6, aDiversion.getDivefc())
                        aDiversion.setDiveff(7, aDiversion.getDivefc())
                        aDiversion.setDiveff(8, aDiversion.getDivefc())
                        aDiversion.setDiveff(9, aDiversion.getDivefc())
                        aDiversion.setDiveff(10, aDiversion.getDivefc())
                        aDiversion.setDiveff(11, aDiversion.getDivefc())

                    # Get the return information
                    for j in range(nrtn):
                        i += 1
                        iline = lines[i]
                        linecount += 1
                        StringUtil.fixedRead2(iline, format_2, format_2w, v)
                        aReturnNode = StateMod_ReturnFlow(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS)
                        s = v[1].strip()
                        if len(s) <= 0:
                            aReturnNode.setCrtnid(v[0].strip())
                            logger.warning("Return node for structure \"{}\" is blank.".format(aDiversion.getID()))
                        else:
                            aReturnNode.setCrtnid(s)

                        aReturnNode.setPcttot(float(v[2]))
                        aReturnNode.setIrtndl(int(v[3]))
                        aDiversion.addReturnFlow(aReturnNode)

                    # Set the diversion to not dirty because it was just initialized...
                    aDiversion.setDirty(False)

                    # print(aDiversion.__str__())

                    # add the diversion to the vector of the diversion
                    theDiversions.append(aDiversion)

        except Exception as e:
            logger.warning("Error reading line {} \"{}\"".format(linecount, iline))
            logger.warning(e)

        return theDiversions

    def setArea(self, area):
        """
        Set the irrigated acreage.
        :param area: acreage
        """
        if self._area != area:
            self._area = area
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setCdividy(self, cdividy):
        """
        Set the daily id
        :param cdividy: daily id
        """
        if cdividy == None:
            return
        if not cdividy == self._cdividy:
            self._cdividy = cdividy
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setDemsrc(self, demsrc):
        """
        Set the demand source
        :param demsrc: areage source.
        """
        if demsrc != self._demsrc:
            self._demsrc = demsrc
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setDivcap(self, divcap):
        """
        Set the diversion capacity
        :param divcap: diversion capacity
        """
        if divcap != self._divcap:
            self._divcap = divcap
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setDivefc(self, divefc):
        """
        Set the system efficiency switch
        :param divefc: efficiency
        """
        if divefc != self._divefc:
            self._divefc = divefc
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setDiveff(self, index, diveff):
        """
        Set the system efficiency for a particular month.
        The efficiencies are stored in the order of the year for the data set.  For
        example, if water years are used, the first efficiency will be for October.  For
        calendar year, the first efficiency will be for January.
        :param index: month index
        :param diveff: monthly efficiency
        """
        if self._diveff[index] != diveff:
            self._diveff[index] = diveff
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setIdvcom(self, idvcom):
        """
        Set the data type switch
        :param idvcom: data type switch.
        """
        if idvcom != self._idvcom:
            self._idvcom = idvcom
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setIreptype(self, ireptype):
        """
        Set the replacement code.
        :param ireptype: replacement code.
        """
        if ireptype != self._ireptype:
            self._ireptype = ireptype
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setIrturn(self, irturn):
        """
        Set the use type.
        :param irturn: use type.
        """
        if irturn != self._irturn:
            self._irturn = irturn
            self.setDirty(True)
            if (not self._isClone) and (self._dataset is not None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)

    def setUsername(self, username):
        """
        Set the user name
        :param username: user name.
        """
        if username == None:
            return
        if username != self._username:
            self._username = username
            self.setDirty(True)
            if (not self._isClone) and (self._dataset != None):
                self._dataset.setDirty(StateMod_DataSet.StateMod_DataSet.COMP_DIVERSION_STATIONS, True)