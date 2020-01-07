# StateMod_Data - super class for many of the StateModLib classes

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


class StateMod_Data:
    """
    Abstract object from which all other StateMod objects are derived.
    Each object can be identified by setting the smdata_type member.
    Possible values for this member come from the SMFileData class (RES_FILE, DIV_FILE, etc.)
    """

    # MISSING_DATA = None
    MISSING_DOUBLE = -999.0
    MISSING_FLOAT = float(-999.0)
    MISSING_INT = -999
    MISSING_LONG = -999
    MISSING_STRING = ""

    # Reference to the dataset into which all the StateMod_* data objects are # being placed.
    # It is used statically because this way every object that extends
    # StateMod_Data will have a reference to the same dataset for using the set_dirty() method.
    dataset = None

    def __init__(self):
        # Whether the data is dirty or not.
        self.is_dirty = False

        # Whether this object is a clone (i.e. data that can be canceled out of).
        self.is_clone = False

        # Specific type of data.  This should be set by each derived class in its
        # constructor.  The types agree with the StateMod_DataSet component types.
        self.smdata_type = -999

        # StateMod data id, for example station ID.
        self.id = ""

        # Station name.
        self.name = ""

        # Comment for data object.
        self.comment = ""

        # For stations, the river node where station is located.  For water rights, the
        # station identifier where the right is located.
        self.cgoto = ""

        # Switch on or off
        self.switch = 0

        # UTM should be written to gis file.
        self.new_utm = 0

        # For mapping, but see StateMod_GeoRecord interface.
        self.utm_x = 0.0

        # For mapping, but see StateMod_GeoRecord interface.
        self.utm_y = 0.0

        # Label used when display on map.
        self.map_label = ""
        self.map_label_display_id = bool
        self.map_label_display_name = bool

        # For screens that can cancel changes, this stores the original values.
        self.original = None

        # Each GRShape has a pointer to the StateMod_Data which is its associated object.
        # This variable whether this object's location was found.  We could
        # have pointed back to the GRShape, but I was trying to avoid including GR in this package.
        # Add a GeoRecord _georecord; object to derived classes that really have
        # location information.  Adding it here would bloat the code since
        # StateMod_Data is the base class for most other classes.
        self.shape_found = bool

        self.initialize()

    def get_cgoto(self):
        """
        Return the cgoto
        """
        return self.cgoto

    def get_id(self):
        """
        Return the ID
        """
        return self.id

    def get_name(self):
        """
        Return the name
        """
        return self.name

    def get_switch(self):
        """
        Return the switch
        """
        return self.switch

    def initialize(self):
        """
        Initialize data members
        """
        self.id = ""
        self.name = ""
        self.comment = ""
        self.cgoto = ""
        self.map_label = ""
        self.map_label_display_id = False
        self.map_label_display_name = False
        self.shape_found = False
        self.switch = 1
        self.new_utm = 0
        self.utm_x = -999
        self.utm_y = -999

    def set_cgoto(self, cgoto):
        """
        Set the Cgoto
        :param cgoto:the new Cgoto
        """
        if cgoto is None:
            return
        if cgoto != self.cgoto:
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)
            self.cgoto = cgoto

    def set_dirty(self, dirty):
        """
        Sets whether the data is dirty or not.
        :param dirty: whether the data is dirty or not.
        """
        self.is_dirty = dirty

    def set_id(self, s):
        """
        Set the ID
        :param s: the new ID
        """
        if (s is not None) and (s != self.id):
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)
            self.id = s

    def set_name(self, s):
        """
        Set the name
        :param s: the new Name
        """
        if (s is not None) and (s != self.name):
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)
            self.name = s

    def set_switch(self, i):
        """
        Set the switch
        :param i: the new switch: 1 = on, 0 = off
        """
        if i != self.switch:
            if (not self.is_clone) and (self.dataset is not None):
                self.dataset.set_dirty(self.smdata_type, True)
            self.switch = i

    def __str__(self):
        """
        Returns a String representation of this object. Omit comment.
        :return: a String representation of this object.
        """
        return "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(self.is_dirty, self.utm_x, self.utm_y,
                                                                       self.new_utm, self.switch, self.id,
                                                                       self.name, self.cgoto, self.smdata_type,
                                                                       self.map_label, self.map_label_display_id,
                                                                       self.map_label_display_name)

    def __repr__(self):
        """
        Returns a String representation of this object. Omit comment.
        :return: a String representation of this object.
        """
        return self.__str__()
