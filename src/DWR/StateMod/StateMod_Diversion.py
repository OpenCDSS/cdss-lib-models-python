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

import DWR.StateMod.StateMod_Data as StateMod_Data


class StateMod_Diversion(StateMod_Data.StateMod_Data()):
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

    def __init__(self, initialize_defaults=None):
        # Daily diversion ID
        self._cdividy = str()

        # Diversion capacity
        self._divcap = int()

        # User name
        self._username = str()