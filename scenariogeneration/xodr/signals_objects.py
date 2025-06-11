"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
from typing import Optional, Union

from ..helpers import enum2str
from ..xosc.utils import get_bool_string
from .enumerations import (
    Access,
    Dynamic,
    FillType,
    LaneType,
    ObjectType,
    Orientation,
    TunnelType,
    enumchecker,
)
from .exceptions import GeneralIssueInputArguments, NotEnoughInputArguments
from .utils import XodrBase


class _SignalObjectBase(XodrBase):
    """Creates a common basis for Signal and Object. This class should not
    be instantiated directly.

    Attributes
    ----------
    s : float
        s-coordinate of Signal/Object.
    t : float
        t-coordinate of Signal/Object.
    id : str
        ID of Signal/Object.
    Type : ObjectType or str
        Type of the Signal (typically string) or Object (typically enum
        ObjectType).
    subtype : str
        Subtype for further specification of Signal/Object.
    dynamic : Dynamic
        Specifies if Signal/Object is static (road sign) or dynamic
        (traffic light).
    name : str
        Name for identification of Signal/Object.
    zOffset : float
        Vertical offset of Signal/Object with respect to the centerline.
    orientation : Orientation
        Orientation of Signal/Object with respect to the road.
    pitch : float
        Pitch angle (rad) of Signal/Object relative to the inertial
        system (xy-plane).
    roll : float
        Roll angle (rad) of Signal/Object after applying pitch, relative
        to the inertial system (x’’y’’-plane).
    width : float
        Width of the Signal/Object.
    height : float
        Height of Signal/Object.
    length : float
        Length of Signal/Object.
    _usedIDs : dict[str, list[str]]
        Dictionary with a list of used IDs. Keys are class names of child
        classes (Object, Signal). Shared among all instances to
        auto-generate unique IDs.
    _IDCounter : dict[str, int]
        Dictionary with counters for auto-generation of IDs. Keys are
        class names of child classes (Object, Signal). Shared among all
        instances to auto-generate unique IDs.

    Methods
    -------
    get_common_attributes()
        Returns a dictionary of all common attributes of Signal/Object.
    _update_id()
        Ensures that an ID is assigned if none was provided and that
        provided IDs are unique. Should be called when adding an Object
        or Signal to the road.
    """

    _usedIDs = {}
    _IDCounter = {}

    def __init__(
        self,
        s: float,
        t: float,
        id: Optional[str],
        Type: Union[ObjectType, str],
        subtype: str,
        dynamic: Dynamic,
        name: Optional[str],
        zOffset: float,
        orientation: Orientation,
        pitch: float,
        roll: float,
        width: Optional[float],
        height: Optional[float],
        length: Optional[float],
    ) -> None:
        """Initialize common attributes for Signal and Object.

        Parameters
        ----------
        s : float
            s-coordinate of Signal/Object.
        t : float
            t-coordinate of Signal/Object.
        id : str, optional
            ID of Signal/Object.
        Type : ObjectType or str
            Type of the Signal (typically string) or Object (typically
            enum ObjectType).
        subtype : str
            Subtype for further specification of Signal/Object.
        dynamic : Dynamic
            Specifies if Signal/Object is static (road sign) or dynamic
            (traffic light).
        name : str, optional
            Name for identification of Signal/Object.
        zOffset : float
            Vertical offset of Signal/Object with respect to the
            centerline.
        orientation : Orientation
            Orientation of Signal/Object with respect to the road.
        pitch : float
            Pitch angle (rad) of Signal/Object relative to the inertial
            system (xy-plane).
        roll : float
            Roll angle (rad) of Signal/Object after applying pitch,
            relative to the inertial system (x’’y’’-plane).
        width : float, optional
            Width of the Signal/Object.
        height : float, optional
            Height of Signal/Object.
        length : float, optional
            Length of Signal/Object.
        """
        super().__init__()
        self.s = s
        self.t = t
        self.height = height
        self.Type = Type
        self.dynamic = enumchecker(dynamic, Dynamic)
        self.name = name
        self.zOffset = zOffset
        self.subtype = subtype
        self.orientation = enumchecker(orientation, Orientation)
        self.pitch = pitch
        self.roll = roll
        self.width = width
        self.length = length
        self.id = id

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _SignalObjectBase) and super().__eq__(other):
            if self.get_common_attributes() == other.get_common_attributes():
                return True
        return False

    def _update_id(self) -> None:
        """Ensure that an ID is assigned if none was provided and that
        provided IDs are unique."""
        # ensure unique IDs
        try:
            if str(self.id) in self._usedIDs[self.__class__.__name__]:
                print(
                    "Warning: id",
                    self.id,
                    "has already been used for another",
                    self.__class__.__name__,
                    "...auto-generating unique id.",
                )

        except KeyError:
            self._usedIDs[self.__class__.__name__] = []
            self._IDCounter[self.__class__.__name__] = 0

        if self.id == None or (
            str(self.id) in self._usedIDs[self.__class__.__name__]
        ):
            while (
                str(self._IDCounter[self.__class__.__name__])
                in self._usedIDs[self.__class__.__name__]
            ):
                self._IDCounter[self.__class__.__name__] += 1
            self.id = str(self._IDCounter[self.__class__.__name__])

        self._usedIDs[self.__class__.__name__].append(str(self.id))

    def get_common_attributes(self) -> dict[str, str]:
        """Return common attributes of Signal and Object as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the common attributes of Signal/Object.
        """
        retdict = {}
        retdict["id"] = str(self.id)
        retdict["s"] = str(self.s)
        retdict["t"] = str(self.t)
        retdict["subtype"] = str(self.subtype)
        retdict["dynamic"] = enum2str(self.dynamic)
        retdict["zOffset"] = str(self.zOffset)
        if self.pitch is not None:
            retdict["pitch"] = str(self.pitch)
        if self.roll is not None:
            retdict["roll"] = str(self.roll)
        if self.width is not None:
            retdict["width"] = str(self.width)
        if self.height is not None:
            retdict["height"] = str(self.height)
        if self.name is not None:
            retdict["name"] = str(self.name)
        if isinstance(self.Type, ObjectType):
            retdict["type"] = enum2str(self.Type)
        else:
            retdict["type"] = str(self.Type)
        if self.orientation == Orientation.positive:
            retdict["orientation"] = "+"
        elif self.orientation == Orientation.negative:
            retdict["orientation"] = "-"
        else:
            retdict["orientation"] = enum2str(self.orientation)

        return retdict


class Signal(_SignalObjectBase):
    """Signal defines the signal element in OpenDRIVE.

    Attributes
    ----------
    s : float
        s-coordinate of the Signal (inherited from base class).
    t : float
        t-coordinate of the Signal (inherited from base class).
    country : str
        Country code according to ISO 3166-1 (alpha-2 for OpenDRIVE 1.6,
        alpha-3 for OpenDRIVE 1.4).
    countryRevision : str, optional
        Year of the applied traffic rules, ensuring unique sign
        interpretation with country, type, and subtype.
    Type : SignalType or str
        Type of the Signal (inherited from base class).
    subtype : str
        Subtype for further specification of the Signal (inherited from
        base class).
    id : str, optional
        ID of the Signal (inherited from base class).
    name : str, optional
        Name for identification of the Signal (inherited from base class).
    dynamic : Dynamic
        Specifies if the Signal is static or dynamic (inherited from base
        class).
    value : float, optional
        Value for further specification of the Signal.
    unit : str, optional
        Unit of the value, required if `value` is provided.
    zOffset : float
        Vertical offset of the Signal with respect to the centerline
        (inherited from base class).
    orientation : Orientation
        Orientation of the Signal with respect to the road (inherited from
        base class).
    hOffset : float
        Heading offset of the Signal relative to its orientation.
    pitch : float
        Pitch angle (rad) of the Signal relative to the inertial system
        (inherited from base class).
    roll : float
        Roll angle (rad) of the Signal after applying pitch (inherited
        from base class).
    width : float, optional
        Width of the Signal (inherited from base class).
    height : float, optional
        Height of the Signal (inherited from base class).
    length : float, optional
        Length of the Signal (inherited from base class).
    validity : Validity, optional
        Explicit validity information for the Signal.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the Signal.
    get_attributes()
        Returns a dictionary of all attributes of the Signal.
    add_validity(fromLane, toLane)
        Adds a new validity range for the Signal.
    """

    def __init__(
        self,
        s: float,
        t: float,
        country: str,
        Type: Union[ObjectType, str],
        subtype: str = "-1",
        countryRevision: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        dynamic: Dynamic = Dynamic.no,
        value: Optional[float] = None,
        unit: Optional[str] = None,
        zOffset: float = 1.5,
        orientation: Orientation = Orientation.positive,
        hOffset: float = 0,
        pitch: float = 0,
        roll: float = 0,
        height: Optional[float] = None,
        width: Optional[float] = None,
        length: Optional[float] = None,
    ) -> None:
        """Initialize the Signal.

        Parameters
        ----------
        s : float
            s-coordinate of the Signal.
        t : float
            t-coordinate of the Signal.
        country : str
            Country code according to ISO 3166-1 (alpha-2 for OpenDRIVE 1.6,
            alpha-3 for OpenDRIVE 1.4).
        Type : SignalType or str
            Type of the Signal.
        subtype : str, optional
            Subtype for further specification of the Signal. Default is "-1".
        countryRevision : str, optional
            Year of the applied traffic rules. Default is None.
        id : str, optional
            ID of the Signal. Default is None.
        name : str, optional
            Name for identification of the Signal. Default is None.
        dynamic : Dynamic, optional
            Specifies if the Signal is static or dynamic. Default is
            Dynamic.no.
        value : float, optional
            Value for further specification of the Signal. Default is None.
        unit : str, optional
            Unit of the value, required if `value` is provided. Default is
            None.
        zOffset : float, optional
            Vertical offset of the Signal with respect to the centerline.
            Default is 1.5.
        orientation : Orientation, optional
            Orientation of the Signal with respect to the road. Default is
            Orientation.positive.
        hOffset : float, optional
            Heading offset of the Signal relative to its orientation.
            Default is 0.
        pitch : float, optional
            Pitch angle (rad) of the Signal relative to the inertial system.
            Default is 0.
        roll : float, optional
            Roll angle (rad) of the Signal after applying pitch. Default is
            0.
        height : float, optional
            Height of the Signal. Default is None.
        width : float, optional
            Width of the Signal. Default is None.
        length : float, optional
            Length of the Signal. Default is None.
        """

        # get attributes that are common with signals
        super().__init__(
            s,
            t,
            id,
            Type,
            subtype,
            dynamic,
            name,
            zOffset,
            orientation,
            pitch,
            roll,
            width,
            height,
            length,
        )
        self.s = s
        self.t = t
        self.dynamic = dynamic
        self.orientation = orientation
        self.zOffset = zOffset
        self.country = country
        self.countryRevision = countryRevision
        self.type = Type
        self.subtype = subtype
        self.value = value
        self.unit = unit
        self.hOffset = hOffset
        self.validity = None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Signal) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the Signal as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the Signal.
        """
        retdict = super().get_common_attributes()
        retdict["country"] = str(self.country).upper()
        retdict["type"] = str(self.type)
        retdict["subtype"] = str(self.subtype)
        if self.countryRevision is not None:
            retdict["countryRevision"] = str(self.countryRevision)
        if self.hOffset is not None:
            retdict["hOffset"] = str(self.hOffset)
        if self.value is not None:
            retdict["value"] = str(self.value)
            if self.unit is None:
                raise NotEnoughInputArguments(
                    "If value is set for a signal, unit has to be added aswell"
                )
            retdict["unit"] = str(self.unit)
        return retdict

    def add_validity(self, fromLane: int, toLane: int) -> "Signal":
        """Add a validity range to the Signal.

        Parameters
        ----------
        fromLane : int
            The starting lane for the validity range.
        toLane : int
            The ending lane for the validity range.

        Returns
        -------
        Signal
            The updated Signal object.

        Raises
        ------
        ValueError
            If a validity range is already set for the Signal.
        """
        if self.validity:
            raise ValueError("only one validity is allowed")
        self.validity = Validity(fromLane, toLane)
        return self

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the Signal.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the Signal.
        """
        element = ET.Element("signal", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self.validity:
            element.append(self.validity.get_element())
        return element


class Validity(XodrBase):
    """Validity is the explicit validity information for a signal.

    Attributes
    ----------
    fromLane : int
        Minimum ID of the lanes for which the object is valid.
    toLane : int
        Maximum ID of the lanes for which the object is valid.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the Validity.
    get_attributes()
        Returns a dictionary of all attributes of the Validity.
    """

    def __init__(self, fromLane: int, toLane: int) -> None:
        """Initialize the Validity.

        Parameters
        ----------
        fromLane : int
            Minimum ID of the lanes for which the object is valid.
        toLane : int
            Maximum ID of the lanes for which the object is valid.
        """
        super().__init__()
        self.fromLane = fromLane
        self.toLane = toLane

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Validity) and super().__eq__(other):
            if self.fromLane == other.fromLane and self.toLane == other.toLane:
                return True
        return False

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of Validity as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the Validity.
        """
        retdict = {}
        retdict["fromLane"] = str(self.fromLane)
        retdict["toLane"] = str(self.toLane)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the Validity.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the Validity.
        """
        element = ET.Element("validity", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class Dependency(XodrBase):
    """Dependency defines the dependency element in OpenDRIVE. It is placed
    within the signal element.

    Attributes
    ----------
    id : str
        ID of the controlled signal.
    type : str
        Type of dependency.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the Dependency.
    get_attributes()
        Returns a dictionary of all attributes of the Dependency.
    """

    def __init__(self, id: str, type: str) -> None:
        """Initialize the Dependency.

        Parameters
        ----------
        id : str
            ID of the controlled signal.
        type : str
            Type of dependency.
        """
        super().__init__()
        self.id = id
        self.type = type

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Dependency) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the Dependency as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the Dependency.
        """
        retdict = {"id": str(self.id), "type": str(self.type)}
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the Dependency.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the Dependency.
        """
        element = ET.Element("dependency", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class SignalReference(XodrBase):
    """SignalReference defines the signal reference element in OpenDRIVE.

    Attributes
    ----------
    s : float
        s-coordinate of the SignalReference.
    t : float
        t-coordinate of the SignalReference.
    id : str, optional
        ID of the SignalReference.
    orientation : Orientation
        Orientation of the SignalReference with respect to the road.
    validity : Validity, optional
        Explicit validity information for the SignalReference.
    _usedIDs : dict[str, list[str]]
        Dictionary with a list of used IDs. Keys are class names of
        SignalReference. Shared to auto-generate unique IDs.
    _IDCounter : dict[str, int]
        Dictionary with counters for auto-generation of IDs. Keys are
        class names of SignalReference. Shared to auto-generate unique IDs.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the SignalReference.
    get_attributes()
        Returns a dictionary of all attributes of the SignalReference.
    add_validity(fromLane, toLane)
        Adds a new validity range for the SignalReference.
    _update_id()
        Ensures that an ID is assigned if none was provided and that
        provided IDs are unique.
    """

    _usedIDs = {}
    _IDCounter = {}

    def __init__(
        self,
        s: float,
        t: float,
        id: Optional[str] = None,
        orientation: Orientation = Orientation.positive,
    ) -> None:
        """Initialize the SignalReference.

        Parameters
        ----------
        s : float
            s-coordinate of the SignalReference.
        t : float
            t-coordinate of the SignalReference.
        id : str, optional
            ID of the SignalReference. Default is None.
        orientation : Orientation, optional
            Orientation of the SignalReference with respect to the road.
            Default is Orientation.positive.
        """

        # get attributes that are common with signals
        super().__init__()
        self.s = s
        self.t = t
        self.orientation = enumchecker(orientation, Orientation)
        self.validity = None
        self.id = id

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SignalReference) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def _update_id(self) -> None:
        """Ensure that an ID is assigned if none was provided and that
        provided IDs are unique."""
        # ensure unique IDs
        try:
            if str(self.id) in self._usedIDs[self.__class__.__name__]:
                print(
                    "Warning: id",
                    self.id,
                    "has already been used for another",
                    self.__class__.__name__,
                    "...auto-generating unique id.",
                )

        except KeyError:
            self._usedIDs[self.__class__.__name__] = []
            self._IDCounter[self.__class__.__name__] = 0

        if self.id == None or (
            str(self.id) in self._usedIDs[self.__class__.__name__]
        ):
            while (
                str(self._IDCounter[self.__class__.__name__])
                in self._usedIDs[self.__class__.__name__]
            ):
                self._IDCounter[self.__class__.__name__] += 1
            self.id = str(self._IDCounter[self.__class__.__name__])

        self._usedIDs[self.__class__.__name__].append(str(self.id))

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the SignalReference as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the SignalReference.
        """
        retdict = {}
        retdict["id"] = str(self.id)
        retdict["s"] = str(self.s)
        retdict["t"] = str(self.t)
        if self.orientation == Orientation.positive:
            retdict["orientation"] = "+"
        elif self.orientation == Orientation.negative:
            retdict["orientation"] = "-"
        else:
            retdict["orientation"] = enum2str(self.orientation)

        return retdict

    def add_validity(self, fromLane: int, toLane: int) -> "SignalReference":
        """Add a validity range to the SignalReference.

        Parameters
        ----------
        fromLane : int
            The starting lane for the validity range.
        toLane : int
            The ending lane for the validity range.

        Returns
        -------
        SignalReference
            The updated SignalReference object.

        Raises
        ------
        ValueError
            If a validity range is already set for the SignalReference.
        """
        if self.validity:
            raise ValueError("only one validity is allowed")
        self.validity = Validity(fromLane, toLane)
        return self

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the SignalReference.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the SignalReference.
        """
        element = ET.Element("signalReference", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self.validity:
            element.append(self.validity.get_element())
        return element


class Object(_SignalObjectBase):
    """Creates an Object in OpenDRIVE.

    Attributes
    ----------
    s : float
        s-coordinate of the Object (inherited from base class).
    t : float
        t-coordinate of the Object (inherited from base class).
    type : ObjectType or str
        Type of the Object (typically enum ObjectType, inherited from base class).
    subtype : str
        Subtype for further specification of the Object (inherited from base class).
    id : str, optional
        ID of the Object (inherited from base class).
    name : str, optional
        Name for identification of the Object (inherited from base class).
    dynamic : Dynamic
        Specifies if the Object is static or dynamic (inherited from base class).
    zOffset : float
        Vertical offset of the Object with respect to the centerline (inherited from base class).
    orientation : Orientation
        Orientation of the Object with respect to the road (inherited from base class).
    hdg : float
        Heading angle (rad) of the Object relative to the road direction.
    pitch : float
        Pitch angle (rad) of the Object relative to the inertial system (inherited from base class).
    roll : float
        Roll angle (rad) of the Object after applying pitch (inherited from base class).
    width : float, optional
        Width of the Object (inherited from base class).
    length : float, optional
        Length of the Object (shall not be used with radius).
    height : float, optional
        Height of the Object (inherited from base class).
    radius : float, optional
        Radius of the Object (shall not be used with width/length).
    validLength : float, optional
        Validity of the Object along the s-coordinate.
    _repeats : list[dict]
        List of dictionaries containing attributes for repeating Objects.
    validity : Validity, optional
        Explicit validity information for the Object.
    outlines : list[Outline]
        List of outlines for the Object.

    Methods
    -------
    repeat(...)
        Adds a dictionary to `_repeats` to create a subelement for repeating the Object.
    add_outline(outline)
        Adds an outline to the Object.
    add_parking_space(parking_space)
        Adds a parking space to the Object.
    get_element()
        Returns the full ElementTree representation of the Object.
    get_attributes()
        Returns a dictionary of all attributes of the Object.
    """

    def __init__(
        self,
        s: float,
        t: float,
        Type: Union[ObjectType, str] = ObjectType.none,
        subtype: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        dynamic: Dynamic = Dynamic.no,
        zOffset: float = 0,
        orientation: Orientation = Orientation.none,
        hdg: float = 0,
        pitch: float = 0,
        roll: float = 0,
        width: Optional[float] = None,
        length: Optional[float] = None,
        height: Optional[float] = None,
        radius: Optional[float] = None,
        validLength: Optional[float] = None,
    ) -> None:
        """Initialize the Object.

        Parameters
        ----------
        s : float
            s-coordinate of the Object.
        t : float
            t-coordinate of the Object.
        Type : ObjectType or str, optional
            Type of the Object. Default is ObjectType.none.
        subtype : str, optional
            Subtype for further specification of the Object. Default is None.
        id : str, optional
            ID of the Object. Default is None.
        name : str, optional
            Name for identification of the Object. Default is None.
        dynamic : Dynamic, optional
            Specifies if the Object is static or dynamic. Default is Dynamic.no.
        zOffset : float, optional
            Vertical offset of the Object with respect to the centerline. Default is 0.
        orientation : Orientation, optional
            Orientation of the Object with respect to the road. Default is Orientation.none.
        hdg : float, optional
            Heading angle (rad) of the Object relative to the road direction. Default is 0.
        pitch : float, optional
            Pitch angle (rad) of the Object relative to the inertial system. Default is 0.
        roll : float, optional
            Roll angle (rad) of the Object after applying pitch. Default is 0.
        width : float, optional
            Width of the Object. Default is None.
        length : float, optional
            Length of the Object. Default is None.
        height : float, optional
            Height of the Object. Default is None.
        radius : float, optional
            Radius of the Object. Default is None.
        validLength : float, optional
            Validity of the Object along the s-coordinate. Default is None.
        """
        # get attributes that are common with signals
        super().__init__(
            s,
            t,
            id,
            Type,
            subtype,
            dynamic,
            name,
            zOffset,
            orientation,
            pitch,
            roll,
            width,
            height,
            length,
        )

        # attributes that differ from signals
        self.validLength = validLength
        self.length = length
        self.hdg = hdg
        self.radius = radius

        # list for repeat entries
        self._repeats = []
        self.outlines = []
        self.validity = None
        self.parking_space = None

        # check if width/length combination or radius was provided and ensure working defaults
        if radius is not None and (width is not None or length is not None):
            print(
                "Object with id",
                self.id,
                "was provided with radius, width and/or length. Provide either radius or width and length. Using radius as fallback.",
            )
            self.width = None
            self.length = None
        elif width is not None and length is None:
            print(
                "Object with id",
                self.id,
                "was provided with width, but length is missing. Using 0 as fallback.",
            )
            self.length = 0
        elif length is not None and width is None:
            print(
                "Object with id",
                self.id,
                "was provided with length, but width is missing. Using 0 as fallback.",
            )
            self.width = 0
        else:
            pass

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Object) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self._repeats == other._repeats
                and self.outlines == other.outlines
            ):
                return True
        return False

    def repeat(
        self,
        repeatLength: float,
        repeatDistance: float,
        sStart: Optional[float] = None,
        tStart: Optional[float] = None,
        tEnd: Optional[float] = None,
        heightStart: Optional[float] = None,
        heightEnd: Optional[float] = None,
        zOffsetStart: Optional[float] = None,
        zOffsetEnd: Optional[float] = None,
        widthStart: Optional[float] = None,
        widthEnd: Optional[float] = None,
        lengthStart: Optional[float] = None,
        lengthEnd: Optional[float] = None,
        radiusStart: Optional[float] = None,
        radiusEnd: Optional[float] = None,
    ) -> None:
        """Add a repeat entry to the Object.

        Parameters
        ----------
        repeatLength : float
            Length of the repeat.
        repeatDistance : float
            Distance between repeats.
        sStart : float, optional
            Starting s-coordinate. Default is None.
        tStart : float, optional
            Starting t-coordinate. Default is None.
        tEnd : float, optional
            Ending t-coordinate. Default is None.
        heightStart : float, optional
            Starting height. Default is None.
        heightEnd : float, optional
            Ending height. Default is None.
        zOffsetStart : float, optional
            Starting z-offset. Default is None.
        zOffsetEnd : float, optional
            Ending z-offset. Default is None.
        widthStart : float, optional
            Starting width. Default is None.
        widthEnd : float, optional
            Ending width. Default is None.
        lengthStart : float, optional
            Starting length. Default is None.
        lengthEnd : float, optional
            Ending length. Default is None.
        radiusStart : float, optional
            Starting radius. Default is None.
        radiusEnd : float, optional
            Ending radius. Default is None.
        """
        self._repeats.append({})

        self._repeats[-1]["length"] = str(repeatLength)
        self._repeats[-1]["distance"] = str(repeatDistance)

        def infoFallback(id, attributeName):
            pass
            # print ("Info: Using data of parent object with id",id,"as attribute",attributeName,"was not specified for repeat entry.")

        # ensuring that all attributes that are required according to OpenDRIVE 1.6 are filled - for convenience the ones of the parent object are used
        # if not provided specifically
        if sStart == None:
            self._repeats[-1]["s"] = str(self.s)
            infoFallback(self.id, "s")
        else:
            self._repeats[-1]["s"] = str(sStart)
        if tStart == None:
            self._repeats[-1]["tStart"] = str(self.t)
            infoFallback(self.id, "tStart")
        else:
            self._repeats[-1]["tStart"] = str(tStart)
        if tEnd == None:
            self._repeats[-1]["tEnd"] = str(self.t)
            infoFallback(self.id, "tEnd")
        else:
            self._repeats[-1]["tEnd"] = str(tEnd)
        if heightStart == None and self.height != None:
            self._repeats[-1]["heightStart"] = str(self.height)
            infoFallback(self.id, "heightStart")
        else:
            self._repeats[-1]["heightStart"] = str(heightStart)
        if heightEnd == None and self.height != None:
            self._repeats[-1]["heightEnd"] = str(self.height)
            infoFallback(self.id, "heightEnd")
        else:
            self._repeats[-1]["heightEnd"] = str(heightEnd)
        if zOffsetStart == None:
            self._repeats[-1]["zOffsetStart"] = str(self.zOffset)
            infoFallback(self.id, "zOffsetStart")
        else:
            self._repeats[-1]["zOffsetStart"] = str(zOffsetStart)
        if zOffsetEnd == None:
            self._repeats[-1]["zOffsetEnd"] = str(self.zOffset)
            infoFallback(self.id, "zOffsetEnd")
        else:
            self._repeats[-1]["zOffsetEnd"] = str(zOffsetEnd)

        # attributes below are optional according to OpenDRIVE 1.6 - no further checks as these values overrule the ones of parent object
        # and fallbacks might be implemented differently by different simulators
        if widthStart is not None:
            self._repeats[-1]["widthStart"] = str(widthStart)
        if widthEnd is not None:
            self._repeats[-1]["widthEnd"] = str(widthEnd)
        if lengthStart is not None:
            self._repeats[-1]["lengthStart"] = str(lengthStart)
        if lengthEnd is not None:
            self._repeats[-1]["lengthEnd"] = str(lengthEnd)
        if radiusStart is not None:
            self._repeats[-1]["radiusStart"] = str(radiusStart)
        if radiusEnd is not None:
            self._repeats[-1]["radiusEnd"] = str(radiusEnd)

    def add_validity(self, fromLane: int, toLane: int) -> "Object":
        """Add a validity range to the Object.

        Parameters
        ----------
        fromLane : int
            The starting lane for the validity range.
        toLane : int
            The ending lane for the validity range.

        Returns
        -------
        Object
            The updated Object instance.

        Raises
        ------
        ValueError
            If a validity range is already set for the Object.
        """
        if self.validity:
            raise ValueError("only one validity is allowed")
        self.validity = Validity(fromLane, toLane)
        return self

    def add_outline(self, outline: "Outline") -> None:
        """Add an outline to the Object.

        Parameters
        ----------
        outline : Outline
            The outline to be added.
        """
        self.outlines.append(outline)

    def add_parking_space(self, parking_space: "ParkingSpace") -> None:
        """Add a parking space to the Object.

        Parameters
        ----------
        parking_space : ParkingSpace
            The parking space to be added.
        """
        self.parking_space = parking_space

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the Object as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the Object.
        """
        retdict = super().get_common_attributes()
        if self.validLength is not None:
            retdict["validLength"] = str(self.validLength)
        retdict["hdg"] = str(self.hdg)

        if self.radius is not None:
            retdict["radius"] = str(self.radius)
        elif self.length is not None and self.width is not None:
            retdict["length"] = str(self.length)
            retdict["width"] = str(self.width)

        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the Object.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the Object.
        """
        element = ET.Element("object", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        for _repeat in self._repeats:
            ET.SubElement(element, "repeat", attrib=_repeat)
        if self.validity:
            element.append(self.validity.get_element())
        if self.parking_space:
            element.append(self.parking_space.get_element())
        if self.outlines:
            outlines_element = ET.SubElement(element, "outlines")
            for outline in self.outlines:
                outlines_element.append(outline.get_element())
        return element


class Tunnel(XodrBase):
    """A tunnel road object (t_road_objects_tunnel).

    Attributes
    ----------
    s : float
        s-coordinate of the tunnel.
    length : float
        Length of the tunnel.
    id : str
        ID of the tunnel.
    name : str
        Name of the tunnel.
    tunnel_type : TunnelType
        Type of the tunnel.
    daylight : float
        Value between 0.0 and 1.0 (application-specific).
    lighting : float
        Value between 0.0 and 1.0 (application-specific).

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the Tunnel.
    get_attributes()
        Returns a dictionary of all XML attributes of the Tunnel.
    """

    def __init__(
        self,
        s: float,
        length: float,
        id: str,
        name: str,
        tunnel_type: TunnelType = TunnelType.standard,
        daylight: float = 0.5,
        lighting: float = 0.5,
    ) -> None:
        """Initialize a Tunnel.

        Parameters
        ----------
        s : float
            s-coordinate of the tunnel.
        length : float
            Length of the tunnel.
        id : str
            ID of the tunnel.
        name : str
            Name of the tunnel.
        tunnel_type : TunnelType, optional
            Type of the tunnel. Default is TunnelType.standard.
        daylight : float, optional
            Value between 0.0 and 1.0 (application-specific). Default is 0.5.
        lighting : float, optional
            Value between 0.0 and 1.0 (application-specific). Default is 0.5.
        """
        super().__init__()
        self.s = s
        self.length = length
        self.id = id
        self.name = name
        self.tunnel_type = enumchecker(tunnel_type, TunnelType)
        self.daylight = daylight
        self.lighting = lighting

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tunnel) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict[str, str]:
        """Return a dictionary of all XML attributes of the Tunnel.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the Tunnel.
        """
        retdict = {}
        retdict["s"] = str(self.s)
        retdict["length"] = str(self.length)
        retdict["id"] = str(self.id)
        retdict["name"] = str(self.name)
        retdict["type"] = enum2str(self.tunnel_type)
        retdict["daylight"] = str(self.daylight)
        retdict["lighting"] = str(self.lighting)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the Tunnel.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the Tunnel.
        """
        element = ET.Element("tunnel", attrib=self.get_attributes())
        return element


class CornerLocal(XodrBase):
    """CornerLocal is one way to describe an outline for objects.

    Attributes
    ----------
    u : float
        Local u-coordinate.
    v : float
        Local v-coordinate.
    z : float
        Local z-coordinate.
    height : float
        Height of the object at this corner.
    id : int, optional
        ID of the point.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the CornerLocal.
    get_attributes()
        Returns a dictionary of all attributes of the CornerLocal.
    """

    def __init__(
        self,
        u: float,
        v: float,
        z: float,
        height: float,
        id: Optional[int] = None,
    ) -> None:
        """Initialize the CornerLocal.

        Parameters
        ----------
        u : float
            Local u-coordinate.
        v : float
            Local v-coordinate.
        z : float
            Local z-coordinate.
        height : float
            Height of the object at this corner.
        id : int, optional
            ID of the point. Default is None.
        """
        super().__init__()
        self.u = u
        self.v = v
        self.z = z
        self.height = height
        self.id = id

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CornerLocal) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the CornerLocal as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the CornerLocal.
        """
        retdict = {}
        retdict["u"] = str(self.u)
        retdict["v"] = str(self.v)
        retdict["z"] = str(self.z)
        retdict["height"] = str(self.height)
        if self.id is not None:
            retdict["id"] = str(self.id)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the CornerLocal.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the CornerLocal.
        """
        element = ET.Element("cornerLocal", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class CornerRoad(XodrBase):
    """CornerRoad is one way to describe an outline for objects.

    Attributes
    ----------
    s : float
        s-coordinate of the corner.
    t : float
        t-coordinate of the corner.
    dz : float
        z-coordinate relative to the road.
    height : float
        Height of the object at this corner.
    id : int, optional
        ID of the point.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the CornerRoad.
    get_attributes()
        Returns a dictionary of all attributes of the CornerRoad.
    """

    def __init__(
        self,
        s: float,
        t: float,
        dz: float,
        height: float,
        id: Optional[int] = None,
    ) -> None:
        """Initialize the CornerRoad.

        Parameters
        ----------
        s : float
            s-coordinate of the corner.
        t : float
            t-coordinate of the corner.
        dz : float
            z-coordinate relative to the road.
        height : float
            Height of the object at this corner.
        id : int, optional
            ID of the point. Default is None.
        """
        super().__init__()
        self.s = s
        self.t = t
        self.dz = dz
        self.height = height
        self.id = id

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CornerRoad) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the CornerRoad as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the CornerRoad.
        """
        retdict = {}
        retdict["s"] = str(self.s)
        retdict["t"] = str(self.t)
        retdict["dz"] = str(self.dz)
        retdict["height"] = str(self.height)
        if self.id is not None:
            retdict["id"] = str(self.id)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the CornerRoad.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the CornerRoad.
        """
        element = ET.Element("cornerRoad", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class Outline(XodrBase):
    """Outline is used to wrap corners for an object in OpenDRIVE.

    Attributes
    ----------
    closed : bool, optional
        Indicates if the outline is closed.
    fill_type : FillType, optional
        Filling type of the object.
    lane_type : LaneType, optional
        Type of the outline.
    outer : bool, optional
        Defines if the outline is the outer outline.
    id : int, optional
        ID of the outline.
    corners : list[Union[CornerRoad, CornerLocal]]
        List of corners in the outline.

    Methods
    -------
    add_corner(corner)
        Adds a corner to the outline.
    get_element()
        Returns the full ElementTree representation of the Outline.
    get_attributes()
        Returns a dictionary of all attributes of the Outline.
    """

    def __init__(
        self,
        closed: Optional[bool] = None,
        fill_type: Optional[FillType] = None,
        lane_type: Optional[LaneType] = None,
        outer: Optional[bool] = None,
        id: Optional[int] = None,
    ) -> None:
        """Initialize the Outline.

        Parameters
        ----------
        closed : bool, optional
            Indicates if the outline is closed. Default is None.
        fill_type : FillType, optional
            Filling type of the object. Default is None.
        lane_type : LaneType, optional
            Type of the outline. Default is None.
        outer : bool, optional
            Defines if the outline is the outer outline. Default is None.
        id : int, optional
            ID of the outline. Default is None.
        """
        super().__init__()
        self.closed = closed
        self.fill_type = enumchecker(fill_type, FillType, True)
        self.lane_type = enumchecker(lane_type, LaneType, True)
        self.outer = outer
        self.id = id
        self.corners = []
        self._corner_type = None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Outline) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.corners == other.corners
            ):
                return True
        return False

    def add_corner(self, corner: Union[CornerRoad, CornerLocal]) -> None:
        """Add a corner to the outline.

        Note: Only the same type of corners can be added.

        Parameters
        ----------
        corner : CornerRoad or CornerLocal
            The corner to add.

        Raises
        ------
        TypeError
            If the corner is not a valid type.
        GeneralIssueInputArguments
            If a mix of corner types is attempted.
        """
        if not (
            isinstance(corner, CornerLocal) or isinstance(corner, CornerRoad)
        ):
            raise TypeError("Not a valid corner.")
        if len(self.corners) == 0:
            if isinstance(corner, CornerLocal):
                self._corner_type = "local"
            else:
                self._corner_type = "road"
        if (
            isinstance(corner, CornerLocal) and self._corner_type == "local"
        ) or (isinstance(corner, CornerRoad) and self._corner_type == "road"):
            self.corners.append(corner)
        else:
            raise GeneralIssueInputArguments(
                "Mix of cornertypes not allowed. "
            )

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the Outline as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the Outline.
        """
        retdict = {}
        if self.closed is not None:
            retdict["closed"] = get_bool_string(self.closed)
        if self.outer is not None:
            retdict["outer"] = get_bool_string(self.outer)
        if self.fill_type is not None:
            retdict["fillType"] = enum2str(self.fill_type)
        if self.lane_type is not None:
            retdict["laneType"] = enum2str(self.lane_type)
        if self.id is not None:
            retdict["id"] = str(self.id)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the Outline.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the Outline.
        """
        element = ET.Element("outline", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        for corner in self.corners:
            element.append(corner.get_element())

        return element


class ParkingSpace(XodrBase):
    """ParkingSpace is used to define access and restrictions for objects
    in OpenDRIVE.

    Attributes
    ----------
    access : Access, optional
        Type of access of the parking space.
    restrictions : str, optional
        Restrictions of the parking space.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the ParkingSpace.
    get_attributes()
        Returns a dictionary of all attributes of the ParkingSpace.
    """

    def __init__(
        self,
        access: Optional[Access] = None,
        restrictions: Optional[str] = None,
    ) -> None:
        """Initialize the ParkingSpace.

        Parameters
        ----------
        access : Access, optional
            Type of access of the parking space. Default is None.
        restrictions : str, optional
            Restrictions of the parking space. Default is None.
        """
        super().__init__()
        self.access = enumchecker(access, Access)
        self.restrictions = restrictions

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Outline) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the ParkingSpace as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the ParkingSpace.
        """
        retdict = {}
        if self.access is not None:
            retdict["access"] = enum2str(self.access)
        if self.restrictions is not None:
            retdict["restrictions"] = self.restrictions

        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the ParkingSpace.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the ParkingSpace.
        """
        element = ET.Element("parkingSpace", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)

        return element
