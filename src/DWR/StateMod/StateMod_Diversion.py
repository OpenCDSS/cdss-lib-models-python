# StateMod_Diversion - class for diversion station

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
import os
import re

from DWR.StateMod.StateMod_Data import StateMod_Data
from DWR.StateMod.StateMod_DataSetComponentType import StateMod_DataSetComponentType
from DWR.StateMod.StateMod_ReturnFlow import StateMod_ReturnFlow
from DWR.StateMod.StateMod_Util import StateMod_Util
from RTi.Util.IO.IOUtil import IOUtil

from RTi.Util.String.StringUtil import StringUtil


class StateMod_Diversion(StateMod_Data):
    """
    Object used to store diversion station information.  All set routines set
    the StateMod_DataSetComponentType.DIVERSION_STATIONS flag dirty.  A new object will have empty non-null
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
        self.cdividy = None

        # Diversion capacity
        self.divcap = None

        # User name
        self.username = None

        # data type switch
        self.idvcom = None

        # System efficiency switch
        self.divefc = None

        # Efficiency % by month. The efficiencies are in order of the calendar for
        # the data set. Therefore, for proper display, the calendar type must be known.
        self.diveff = []

        # The following are used only by StateDMI and do not need to be handled in comparison,
        # initialization, etc.
        self.calculated_efficiencies = None
        self.calculated_efficiency_stddevs = None
        self.model_efficiencies = None

        # irrigated acreage, future
        self.area = None

        # use type
        self.irturn = None

        # river nodes receiving return flow
        self.rivret = []

        # direct diversions rights
        self.rights = []

        # Acreage source
        self.demsrc = None

        # Replacement code
        self.ireptype = None

        # Pointer to monthly demand ts.
        self.demand_monthts = None

        # Pointer to monthly demand override ts.
        self.demand_override_monthts = None

        # Pointer to average monthly demand override ts.
        self.demand_average_monthts = None

        # Pointer to daily demand ts.
        self.demand_dayts = None

        # Pointer to historical monthly diversion ts.
        self.diversion_monthts = None

        # Pointer to historical daily diversion ts.
        self.diversion_dayts = None

        # 12 monthly and annual average over period, used by StateDMI.
        self.ddh_monthly = None

        # Pointer to monthly consumptive water requirement ts.
        self.cwr_monthts = None

        # 12 monthly and annual average over period, used by StateDMI
        self.cwr_monthly = None

        # Pointer to daily consumptive water requirement ts.
        self.cwr_dayts = None

        # Pointer to the StateCU_IrrigationPracticeTS. This object actually contains other time series,
        # which can be retrieved for displays.
        self.ipy_yearts = None

        # Soil available water content, from StateCU file.
        self.awc = None

        # Reference to spatial data for this diversion -- currently NOT cloned. If null, then no spatial
        # are available
        # self._georecord = GeoRecord()

        # List of parcel data, in particular to allow StateDMI to detect when a diversion had no data.
        self.parcel_Vector = []

        self.collection_type = StateMod_Util.MISSING_STRING

        # Used by DMI software - currently no options.
        self.collection_part_type = "Ditch"

        # The identifiers for data that are collected - null if not a collection location.
        # This is a list of lists where the __collection_year is the first dimension.
        # This is ugly but need to use the code to see if it can be made cleaner.
        self.collection_Vector = None

        # An array of year that correspond to the aggregate/system. Ditches currently only have one year.
        self.collection_year = None

        # Constructor
        if initialize_defaults is not None:
            self.initialize_statemod_diversion(initialize_defaults)
        else:
            self.initialize_statemod_diversion(True)

        super().__init__()

    def initialize_statemod_diversion(self, initialize_defaults):
        """
        Initialize data. Sets the smdata_type to StateMod_DataSetComponentTYpe.DIVERSION_STATIONS.
        :param initialize_defaults: If True, assign data to reasonable defaults.
        If False, all data are set to missing.
        """
        self.smdata_type = StateMod_DataSetComponentType.DIVERSION_STATIONS
        if initialize_defaults:
            self.divefc = -60.0
            self.diveff = [float()] * 12
            for i, diveff in enumerate(self.diveff):
                self.diveff[i] = 60.0
            self.username = ""
            self.cdividy = "0"  # Use the average monthly TS for daily TS
            self.divcap = 0
            self.idvcom = 1
            self.area = 0
            self.irturn = 1
            self.demsrc = StateMod_Diversion.DEMSRC_UNKNOWN
            self.ireptype = -1  # Provide depletion replacement
        else:
            self.divefc = StateMod_Util.MISSING_DOUBLE
            self.diveff = [float()] * 12
            for i, diveff in enumerate(self.diveff):
                self.diveff[i] = StateMod_Util.MISSING_DOUBLE
            self.username = StateMod_Util.MISSING_STRING
            self.cdividy = StateMod_Util.MISSING_INT
            self.idvcom = StateMod_Util.MISSING_INT
            self.area = StateMod_Util.MISSING_DOUBLE
            self.irturn = StateMod_Util.MISSING_INT
            self.demsrc = StateMod_Util.MISSING_INT
            self.ireptype = StateMod_Util.MISSING_INT
        self.rivret = []
        self.rights = []
        self.diversion_monthts = None
        self.diversion_dayts = None
        self.demand_monthts = None
        self.demand_override_monthts = None
        self.demand_average_monthts = None
        self.demand_dayts = None
        self.ipy_yearts = None
        self.cwr_monthts = None
        self.cwr_dayts = None
        # self.georecord = None

    def add_return_flow(self, rivret):
        """
        Add return flow node to the list of return flow nodes.
        :param rivret: riveret return flow
        """
        self.rivret.append(rivret)

    @staticmethod
    def connect_all_rights(diversions, rights):
        if (diversions is None) or (rights is None):
            return
        num_divs = len(diversions)

        for i in range(num_divs):
            div = diversions[i]
            if div is not None:
                continue
            div.connect_rights(rights)

    def get_area(self):
        """
        :return: the irrigated acreage
        """
        return self.area

    def get_cdividy(self):
        """
        :return: the daily ID
        """
        return self.cdividy

    def get_demsrc(self):
        """
        :return: the demand source
        """
        return self.demsrc

    def get_divcap(self):
        """
        :return: the diversion capacity
        """
        return self.divcap

    def get_divefc(self):
        """
        :return: the system efficiency switch
        """
        return self.divefc

    def get_diveff(self, i):
        """
        :param i: month index 0, where 0 is the first month in the year type
        :return: the system efficiency for the specified month index
        """
        return self.diveff[i]

    def get_idvcom(self):
        """
        :return: the data type switch
        """
        return self.idvcom

    def get_ireptype(self):
        """
        :return: the replacement code
        """
        return self.ireptype

    def get_irturn(self):
        """
        :return: the use type
        """
        return self.irturn

    def get_nrtn(self):
        """
        :return: the number of return tables
        """
        if self.rivret is None:
            return 0
        else:
            return len(self.rivret)

    def get_return_flow(self, i):
        """
        :return: the return flow item from the list, or None if index is out of bounds
        """
        if (i < 0) or (i >= len(self.rivret)):
            return None
        else:
            return self.rivret[i]

    def get_return_flows(self):
        """
        :return: the return flows list
        """
        return self.rivret

    def get_username(self):
        """
        :return: the user name
        """
        return self.username

    @staticmethod
    def read_statemod_file(filename):
        """
        Read return information in and store in a list.
        :param filename: filename containing return flow information
        """
        logger = logging.getLogger(__name__)
        # iline = None
        v = []
        the_diversions = []
        linecount = 0

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

        try:
            with open(filename) as f:
                lines = f.readlines()
                i = -1
                while i < len(lines) - 1:
                    i += 1
                    iline = lines[i]
                    linecount += 1
                    # check for comments
                    if (iline.startswith('#')) or (len(iline.strip()) == 0):
                        continue

                    # Allocate new diversion node
                    a_diversion = StateMod_Diversion()

                    # line 1
                    StringUtil.fixed_read2(iline, format_0, format_0w, v)
                    a_diversion.set_id(v[0].strip())
                    a_diversion.set_name(v[1].strip())
                    a_diversion.set_cgoto(v[2].strip())
                    a_diversion.set_switch(int(v[3]))
                    a_diversion.set_divcap(float(v[4]))
                    a_diversion.set_ireptype(int(v[6]))
                    a_diversion.set_cdividy(v[8].strip())

                    # line 2
                    i += 1
                    iline = lines[i]
                    linecount += 1
                    StringUtil.fixed_read2(iline, format_1, format_1w, v)
                    a_diversion.set_username(v[1].strip())
                    a_diversion.set_idvcom(int(v[3]))
                    nrtn = int(v[4])
                    a_diversion.set_divefc(float(v[5]))
                    a_diversion.set_area(float(v[6]))
                    a_diversion.set_irturn(int(v[7]))
                    a_diversion.set_demsrc(int(v[8]))

                    # Get the efficiency information
                    if a_diversion.get_divefc() < 0:
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
                                a_diversion.set_diveff(j, float(nextToken))
                    else:
                        # Annual efficiency so set monthly efficiencies to the annual...
                        a_diversion.set_diveff(0, a_diversion.get_divefc())
                        a_diversion.set_diveff(1, a_diversion.get_divefc())
                        a_diversion.set_diveff(2, a_diversion.get_divefc())
                        a_diversion.set_diveff(3, a_diversion.get_divefc())
                        a_diversion.set_diveff(4, a_diversion.get_divefc())
                        a_diversion.set_diveff(5, a_diversion.get_divefc())
                        a_diversion.set_diveff(6, a_diversion.get_divefc())
                        a_diversion.set_diveff(7, a_diversion.get_divefc())
                        a_diversion.set_diveff(8, a_diversion.get_divefc())
                        a_diversion.set_diveff(9, a_diversion.get_divefc())
                        a_diversion.set_diveff(10, a_diversion.get_divefc())
                        a_diversion.set_diveff(11, a_diversion.get_divefc())

                    # Get the return information
                    for j in range(nrtn):
                        i += 1
                        iline = lines[i]
                        linecount += 1
                        StringUtil.fixed_read2(iline, format_2, format_2w, v)
                        a_return_node = StateMod_ReturnFlow(StateMod_DataSetComponentType.DIVERSION_STATIONS)
                        s = v[1].strip()
                        if len(s) <= 0:
                            a_return_node.set_crtnid(v[0].strip())
                            logger.warning("Return node for structure \"{}\" is blank.".format(a_diversion.get_id()))
                        else:
                            a_return_node.set_crtnid(s)

                        a_return_node.set_pcttot(float(v[2]))
                        a_return_node.set_irtndl(int(v[3]))
                        a_diversion.add_return_flow(a_return_node)

                    # Set the diversion to not dirty because it was just initialized...
                    a_diversion.set_dirty(False)

                    # print(a_diversion.__str__())

                    # add the diversion to the vector of the diversion
                    the_diversions.append(a_diversion)

        except Exception as e:
            logger.warning("Error reading line {} \"{}\"".format(linecount, iline), exc_info=True)

        return the_diversions

    def set_area(self, area):
        """
        Set the irrigated acreage.
        :param area: acreage
        """
        if self.area != area:
            self.area = area
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_cdividy(self, cdividy):
        """
        Set the daily id
        :param cdividy: daily id
        """
        if cdividy is None:
            return
        if not cdividy == self.cdividy:
            self.cdividy = cdividy
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_demsrc(self, demsrc):
        """
        Set the demand source
        :param demsrc: acreage source.
        """
        if demsrc != self.demsrc:
            self.demsrc = demsrc
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_divcap(self, divcap):
        """
        Set the diversion capacity
        :param divcap: diversion capacity
        """
        if divcap != self.divcap:
            self.divcap = divcap
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_divefc(self, divefc):
        """
        Set the system efficiency switch
        :param divefc: efficiency
        """
        if divefc != self.divefc:
            self.divefc = divefc
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_diveff(self, index, diveff):
        """
        Set the system efficiency for a particular month.
        The efficiencies are stored in the order of the year for the data set.  For
        example, if water years are used, the first efficiency will be for October.  For
        calendar year, the first efficiency will be for January.
        :param index: month index
        :param diveff: monthly efficiency
        """
        if self.diveff[index] != diveff:
            self.diveff[index] = diveff
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_idvcom(self, idvcom):
        """
        Set the data type switch
        :param idvcom: data type switch.
        """
        if idvcom != self.idvcom:
            self.idvcom = idvcom
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_ireptype(self, ireptype):
        """
        Set the replacement code.
        :param ireptype: replacement code.
        """
        if ireptype != self.ireptype:
            self.ireptype = ireptype
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_irturn(self, irturn):
        """
        Set the use type.
        :param irturn: use type.
        """
        if irturn != self.irturn:
            self.irturn = irturn
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def set_username(self, username):
        """
        Set the user name
        :param username: user name.
        """
        if username is None:
            return
        if username != self.username:
            self.username = username
            self.set_dirty(True)
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(StateMod_DataSetComponentType.DIVERSION_STATIONS, True)

    def write_statemod_file(instrfile, outstrfile, the_diversions, new_comments, use_daily_data):
        """
        Write diversion information to output.
        History header information is also maintained by calling this routine.

        :param instrfile: input file from which previous history should be taken
        :param outstrfile: output file to which to write
        :param the_diversions: list of diversions to write.
        :param new_comments: addition comments which should be included in history
        :param use_daily_data: Indicates whether daily data should be written.
        The data are only used if the control file indicates that a daily run is occurring.
        :return:
        """
        comment_indicators = ["#"]
        ignored_comment_indicators = ["#>"]
        logger = logging.getLogger(__name__)
        out = None
        try:
            out = IOUtil.process_file_headers(IOUtil.get_path_using_working_dir(instrfile),
                                              IOUtil.get_path_using_working_dir(outstrfile),
                                              new_comments, comment_indicators, ignored_comment_indicators, 0)

            # int i
            # int j
            # iline
            cmnt = "#>"
            # With daily ID....
            #format_1 = "%-12.12s%-24.24s%-12.12s%8d%#8.2F%8d%8d %-12.12s"
            format_1 = "%-12.12s%-24.24s%-12.12s%8d%#8.2f%8d%8d %-12.12s"
            # Without daily ID...
            #format_1a = "%-12.12s%-24.24s%-12.12s%8d%#8.2F%8d%8d"
            format_1a = "%-12.12s%-24.24s%-12.12s%8d%#8.2f%8d%8d"
            #format_2 = "            %-24.24s            %8d%8d%#8.0F%#8.2F%8d%8d"
            format_2 = "            %-24.24s            %8d%8d%#8.0f%#8.2f%8d%8d"
            # format_3 = "%1.1s%#5.0F"
            format_3 = "%1.1s%#5.0f"
            #format_4 = "                                    %-12.12s%8.2F%8d"
            format_4 = "                                    %-12.12s%8.2f%8d"
            div = None
            ret = None
            v = []  # Reuse for all output lines.
            v5 = None  # For return flows.
            nl = "\n"  # Use for all platforms

            out.write(cmnt + nl)
            out.write(cmnt + "*************************************************" + nl)
            out.write(cmnt + "  Direct Diversion Station File" + nl)
            out.write(cmnt + nl)
            out.write(cmnt + "  Card 1 format (a12, a24, a12, i8, f8.2, 2i8, 1x, a12)" + nl)
            out.write(cmnt + nl)
            out.write(cmnt + "  ID          cdivid:  Diversion station ID" + nl)
            out.write(cmnt + "  Name        divnam:  Diversion name" + nl)
            out.write(cmnt + "  Riv ID       cgoto:  River node for diversion" + nl)
            out.write(cmnt + "  On/Off      idivsw:  Switch 0=off, 1=on" + nl)
            out.write(cmnt + "  Capacity    divcap:  Diversion capacity (CFS)" + nl)
            out.write(cmnt + "                dumx:  Not currently used" + nl)
            out.write(cmnt + "  RepType    ireptyp:  Replacement reservoir option (see StateMod doc)" + nl)
            out.write(cmnt + "  Daily ID   cdividy:  Daily diversion ID" + nl)
            out.write(cmnt + nl)
            out.write(cmnt + "  Card 2 format (12x, a24, 12x, 2i8, f8.2, f8.0, 2i8)" + nl)
            out.write(cmnt + nl)
            out.write(cmnt + "  User Name  usernam:  User name." + nl)
            out.write(cmnt + "  DemType     idvcom:  Demand data type switch (see StateMod doc)" + nl)
            out.write(cmnt + "  #-Ret         nrtn:  Number of return flow table ref" + nl)
            out.write(cmnt + "  Eff         divefc:  Annual system efficiency" + nl)
            out.write(cmnt + "  Area          area:  Irrigated acreage" + nl)
            out.write(cmnt + "  UseType     irturn:  Use type (see StateMod doc)" + nl)
            out.write(cmnt + "  Demsrc      demsrc:  Demand source (see StateMod doc)" + nl)
            out.write(cmnt + nl)
            out.write(cmnt + "  Card 3 format (free format)" + nl)
            out.write(cmnt + nl)
            out.write(cmnt + "     diveff (12):  System efficiency % by month" + nl)
            out.write(cmnt + nl)
            out.write(cmnt + "  Card 4 format (36x, a12, f8.2, i8)" + nl)
            out.write(cmnt + nl)
            out.write(cmnt + "  Ret ID      crtnid:  River node receiving return flow" + nl)
            out.write(cmnt + "  Ret %       pcttot:  Percent of return flow to this river node" + nl)
            out.write(cmnt + "  Table #     irtndl:  Delay (return flow) table for this return flow." + nl)
            out.write(cmnt + nl)

            out.write(cmnt +
                      " ID               Name             Riv ID     On/Off  Capacity        RepType   Daily ID" + nl)
            out.write(cmnt +
                      "---------eb----------------------eb----------eb------eb------eb------eb------exb----------e" +
                      nl)
            out.write(cmnt +
                      "              User Name                       DemType   #-Ret   Eff %   Area  UseType DemSrc" +
                      nl)
            out.write(cmnt +
                      "xxxxxxxxxxb----------------------exxxxxxxxxxxxb------eb------eb------eb------eb------eb------e" +
                      nl)
            out.write(cmnt + "          ... Monthly Efficiencies..." + nl)
            out.write(cmnt + "b----------------------------------------------------------------------------e" + nl)
            out.write(cmnt + "                                   Ret ID       Ret % Table #" + nl)
            out.write(cmnt + "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxb----------eb------eb------e" + nl)
            out.write(cmnt + "EndHeader" + nl)

            # num = 0
            # if the_diversions is not None:
            #     num = len(the_diversions)

            # i = -1
            for div in the_diversions:
                # i = i + 1
                # div = the_diversions[i]
                if div is None:
                    continue

                # line 1
                v.clear()
                v.append(div.get_id())
                v.append(div.get_name())
                v.append(div.get_cgoto())
                v.append(div.get_switch())
                v.append(div.get_divcap())
                v.append(1)  # old nduser, which is not used anymore
                v.append(div.get_ireptype())
                if use_daily_data:
                    v.append(div.get_cdividy())
                    iline = StringUtil.format_string(v, format_1)
                else:
                    iline = StringUtil.format_string(v, format_1a)
                out.write(iline + nl)

                # line 2
                v.clear()
                v.append(div.get_username())
                v.append(div.get_idvcom())
                v.append(div.get_nrtn())
                v.append(div.get_divefc())
                v.append(div.get_area())
                v.append(div.get_irturn())
                v.append(div.get_demsrc())
                iline = StringUtil.format_string(v, format_2)
                out.write(iline + nl)

                # line 3 - diversion efficiency
                if div.get_divefc() < 0:
                    # Monthly efficiencies
                    for j in range(12):
                        v.clear()
                        v.append("")
                        v.append(div.get_diveff(j))
                        iline = StringUtil.format_string(v, format_3)
                        # Each value is written with leading space and then a newline is written below
                        out.write(iline)

                    # Write the newline
                    out.write(nl)

                # line 4 - return information
                nrtn = div.get_nrtn()
                rivrets = div.get_return_flows()
                for j in range(nrtn):
                    v.clear()
                    ret = rivrets[j]
                    v.append(ret.get_crtnid())
                    v.append(ret.get_pcttot())
                    v.append(ret.get_irtndl())
                    iline = StringUtil.format_string(v, format_4)
                    out.write(iline + nl)
        except Exception as e:
            logger.warning("Exception writing diversions.", exc_info=True)
            # Rethrow
            raise
        finally:
            if out is not None:
                out.close()
