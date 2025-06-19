"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
from typing import Optional

from .enumerations import RouteStrategy
from .exceptions import (
    NotAValidElement,
    NotEnoughInputArguments,
    OpenSCENARIOVersionError,
    ToManyOptionalArguments,
    XMLStructureError,
)
from .utils import (
    CatalogReference,
    Orientation,
    ParameterDeclarations,
    VersionBase,
    _BaseCatalog,
    _PositionType,
    convert_bool,
    convert_enum,
    convert_float,
    convert_int,
    find_mandatory_field,
    get_bool_string,
)


class _TrajectoryShape(VersionBase):
    """Used for typing of trajectory shapes."""


class _PositionFactory:
    @staticmethod
    def parse_position(element: ET.Element) -> _PositionType:
        if element.findall("WorldPosition"):
            return WorldPosition.parse(element)
        if element.findall("RelativeWorldPosition"):
            return RelativeWorldPosition.parse(element)
        if element.findall("RelativeObjectPosition"):
            return RelativeObjectPosition.parse(element)
        if element.findall("RoadPosition"):
            return RoadPosition.parse(element)
        if element.findall("RelativeRoadPosition"):
            return RelativeRoadPosition.parse(element)
        if element.findall("LanePosition"):
            return LanePosition.parse(element)
        if element.findall("RelativeLanePosition"):
            return RelativeLanePosition.parse(element)
        if element.findall("RoutePosition/InRoutePosition/FromCurrentEntity"):
            return RoutePositionOfCurrentEntity.parse(element)
        if element.findall(
            "RoutePosition/InRoutePosition/FromRoadCoordinates"
        ):
            return RoutePositionInRoadCoordinates.parse(element)
        if element.findall(
            "RoutePosition/InRoutePosition/FromLaneCoordinates"
        ):
            return RoutePositionInLaneCoordinates.parse(element)
        if element.findall("TrajectoryPosition"):
            return TrajectoryPosition.parse(element)
        if element.findall("GeoPosition"):
            return GeoPosition.parse(element)
        raise NotAValidElement("element ", element, "is not a valid position")


class _ShapeFactory:
    @staticmethod
    def parse_shape(element) -> _TrajectoryShape:
        if element.findall("Polyline"):
            return Polyline.parse(element)
        if element.findall("Clothoid"):
            return Clothoid.parse(element)
        if element.findall("Nurbs"):
            return Nurbs.parse(element)
        raise NotAValidElement("element ", element, "is not a valid shape")


class WorldPosition(_PositionType):
    """The WorldPosition creates a world position in OpenScenario.

    Parameters
    ----------
    x : float
        X-coordinate of the entity.
    y : float
        Y-coordinate of the entity.
    z : float, optional
        Z-coordinate of the entity. Default is None.
    h : float, optional
        Heading of the entity. Default is None.
    p : float, optional
        Pitch of the entity. Default is None.
    r : float, optional
        Roll of the entity. Default is None.

    Attributes
    ----------
    x : float
        X-coordinate of the entity.
    y : float
        Y-coordinate of the entity.
    z : float
        Z-coordinate of the entity.
    h : float
        Heading of the entity.
    p : float
        Pitch of the entity.
    r : float
        Roll of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: Optional[float] = None,
        h: Optional[float] = None,
        p: Optional[float] = None,
        r: Optional[float] = None,
    ) -> None:
        """Initialize the WorldPosition.

        Parameters
        ----------
        x : float
            X-coordinate of the entity.
        y : float
            Y-coordinate of the entity.
        z : float, optional
            Z-coordinate of the entity. Default is None.
        h : float, optional
            Heading of the entity. Default is None.
        p : float, optional
            Pitch of the entity. Default is None.
        r : float, optional
            Roll of the entity. Default is None.
        """
        self.x = convert_float(x)
        self.y = convert_float(y)

        self.z = convert_float(z)
        self.h = convert_float(h)
        self.p = convert_float(p)
        self.r = convert_float(r)

    def __eq__(self, other) -> bool:
        if isinstance(other, WorldPosition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "WorldPosition":
        """Parse the XML element of WorldPosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        WorldPosition
            A WorldPosition object.
        """
        position_element = find_mandatory_field(element, "WorldPosition")
        x = convert_float(position_element.attrib["x"])
        y = convert_float(position_element.attrib["y"])
        z = None
        h = None
        r = None
        p = None
        if "z" in position_element.attrib:
            z = convert_float(position_element.attrib["z"])
        if "h" in position_element.attrib:
            h = convert_float(position_element.attrib["h"])
        if "p" in position_element.attrib:
            p = convert_float(position_element.attrib["p"])
        if "r" in position_element.attrib:
            r = convert_float(position_element.attrib["r"])
        return WorldPosition(x, y, z, h, p, r)

    def get_attributes(self) -> dict:
        """Return the attributes of the WorldPosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the WorldPosition.
        """
        retdict = {"x": str(self.x), "y": str(self.y)}
        if self.z is not None:
            retdict["z"] = str(self.z)
        if self.h is not None:
            retdict["h"] = str(self.h)
        if self.p is not None:
            retdict["p"] = str(self.p)
        if self.r is not None:
            retdict["r"] = str(self.r)
        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the WorldPosition.

        Parameters
        ----------
        elementname : str, optional
            Used if another name is needed for the position. Default is
            "Position".

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the WorldPosition.
        """
        element = ET.Element(elementname)
        ET.SubElement(element, "WorldPosition", attrib=self.get_attributes())
        return element


class RelativeWorldPosition(_PositionType):
    """The RelativeWorldPosition creates a RelativePosition with the option of
    world as reference.

    Parameters
    ----------
    entity : str
        The entity to be relative to.
    dx : float
        Relative x-coordinate.
    dy : float
        Relative y-coordinate.
    dz : float
        Relative z-coordinate.
    orientation : Orientation, optional
        The angular orientation of the entity. Default is Orientation().

    Attributes
    ----------
    target : str
        The entity to be relative to.
    dx : float
        Relative x-coordinate.
    dy : float
        Relative y-coordinate.
    dz : float
        Relative z-coordinate.
    orient : Orientation
        The angular orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        entity: str,
        dx: float,
        dy: float,
        dz: float,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the RelativeWorldPosition.

        Parameters
        ----------
        entity : str
            The entity to be relative to.
        dx : float
            Relative x-coordinate.
        dy : float
            Relative y-coordinate.
        dz : float
            Relative z-coordinate.
        orientation : Orientation, optional
            The angular orientation of the entity. Default is
            Orientation().
        """
        self.target = entity
        self.dx = convert_float(dx)
        self.dy = convert_float(dy)
        self.dz = convert_float(dz)
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orient = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, RelativeWorldPosition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.orient == other.orient
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeWorldPosition":
        """Parse the XML element of RelativeWorldPosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RelativeWorldPosition
            A RelativeWorldPosition object.
        """
        position_element = find_mandatory_field(
            element, "RelativeWorldPosition"
        )
        dx = convert_float(position_element.attrib["dx"])
        dy = convert_float(position_element.attrib["dy"])
        dz = convert_float(position_element.attrib["dz"])
        entityref = position_element.attrib["entityRef"]

        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        return RelativeWorldPosition(entityref, dx, dy, dz, orientation)

    def get_attributes(self) -> dict:
        """Return the attributes of the RelativeWorldPosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            RelativeWorldPosition.
        """
        retdict = {}
        retdict["entityRef"] = self.target
        retdict["dx"] = str(self.dx)
        retdict["dy"] = str(self.dy)
        retdict["dz"] = str(self.dz)
        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the RelativeWorldPosition.

        Parameters
        ----------
        elementname : str, optional
            Used if another name is needed for the position. Default is
            "Position".

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the RelativeWorldPosition.
        """
        element = ET.Element(elementname)
        relpos = ET.SubElement(
            element, "RelativeWorldPosition", attrib=self.get_attributes()
        )
        if self.orient.is_filled():
            relpos.append(self.orient.get_element())
        return element


class RelativeObjectPosition(_PositionType):
    """The RelativeObjectPosition creates a RelativePosition with the option of
    object as reference.

    Parameters
    ----------
    entity : str
        The entity to be relative to.
    dx : float
        Relative x-coordinate.
    dy : float
        Relative y-coordinate.
    dz : float, optional
        Relative z-coordinate. Default is None.
    orientation : Orientation, optional
        The angular orientation of the entity. Default is Orientation().

    Attributes
    ----------
    target : str
        The entity to be relative to.
    dx : float
        Relative x-coordinate.
    dy : float
        Relative y-coordinate.
    dz : float
        Relative z-coordinate.
    orient : Orientation
        The angular orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        entity: str,
        dx: float,
        dy: float,
        dz: Optional[float] = None,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the RelativeObjectPosition.

        Parameters
        ----------
        entity : str
            The entity to be relative to.
        dx : float
            Relative x-coordinate.
        dy : float
            Relative y-coordinate.
        dz : float, optional
            Relative z-coordinate. Default is None.
        orientation : Orientation, optional
            The angular orientation of the entity. Default is
            Orientation().
        """
        self.target = entity
        self.dx = convert_float(dx)
        self.dy = convert_float(dy)
        self.dz = convert_float(dz)
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orient = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, RelativeObjectPosition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.orient == other.orient
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeObjectPosition":
        """Parse the XML element of RelativeObjectPosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RelativeObjectPosition
            A RelativeObjectPosition object.
        """
        position_element = find_mandatory_field(
            element, "RelativeObjectPosition"
        )
        dx = convert_float(position_element.attrib["dx"])
        dy = convert_float(position_element.attrib["dy"])
        if "dz" in position_element.attrib:
            dz = convert_float(position_element.attrib["dz"])
        else:
            dz = None
        entityref = position_element.attrib["entityRef"]

        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        return RelativeObjectPosition(entityref, dx, dy, dz, orientation)

    def get_attributes(self) -> dict:
        """Return the attributes of the RelativeObjectPosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            RelativeObjectPosition.
        """
        retdict = {}
        retdict["entityRef"] = self.target
        retdict["dx"] = str(self.dx)
        retdict["dy"] = str(self.dy)
        if self.dz is not None:
            retdict["dz"] = str(self.dz)
        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the RelativeObjectPosition.

        Parameters
        ----------
        elementname : str, optional
            Used if another name is needed for the position. Default is
            "Position".

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the RelativeObjectPosition.
        """
        element = ET.Element(elementname)
        relpos = ET.SubElement(
            element, "RelativeObjectPosition", attrib=self.get_attributes()
        )
        if self.orient.is_filled():
            relpos.append(self.orient.get_element())
        return element


class RoadPosition(_PositionType):
    """The RoadPosition creates a RoadPosition in OpenScenario.

    Parameters
    ----------
    s : float
        Length along the road.
    t : float
        Lateral offset from the center.
    reference_id : str
        ID of the road.
    orientation : Orientation, optional
        The angular orientation of the entity. Default is Orientation().

    Attributes
    ----------
    s : float
        Length along the road.
    t : float
        Lateral offset from the center.
    id : str
        ID of the road.
    orient : Orientation
        The angular orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        s: float,
        t: float,
        reference_id: int,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the RoadPosition.

        Parameters
        ----------
        s : float
            Length along the road.
        t : float
            Lateral offset from the center.
        reference_id : int
            ID of the road.
        orientation : Orientation, optional
            The angular orientation of the entity. Default is
            Orientation().
        """
        self.s = convert_float(s)
        self.t = convert_float(t)
        self.id = convert_int(reference_id)
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orient = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, RoadPosition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.orient == other.orient
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RoadPosition":
        """Parse the XML element of RoadPosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RoadPosition
            A RoadPosition object.
        """
        position_element = find_mandatory_field(element, "RoadPosition")
        roadId = convert_int(position_element.attrib["roadId"])
        s = convert_float(position_element.attrib["s"])
        t = convert_float(position_element.attrib["t"])

        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        return RoadPosition(s, t, roadId, orientation)

    def get_attributes(self) -> dict:
        """Return the attributes of the RoadPosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the RoadPosition.
        """
        retdict = {}
        retdict["roadId"] = str(self.id)
        retdict["s"] = str(self.s)
        retdict["t"] = str(self.t)
        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the RoadPosition.

        Parameters
        ----------
        elementname : str, optional
            Used if another name is needed for the position. Default is
            "Position".

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the RoadPosition.
        """
        element = ET.Element(elementname)
        roadpos = ET.SubElement(
            element, "RoadPosition", attrib=self.get_attributes()
        )
        if self.orient.is_filled():
            roadpos.append(self.orient.get_element())
        return element


class RelativeRoadPosition(_PositionType):
    """The RelativeRoadPosition creates a RelativeRoadPosition in OpenScenario.

    Parameters
    ----------
    ds : float
        Length along the road.
    dt : float
        Lateral offset from the center.
    entity : str
        ID of the entity.
    orientation : Orientation, optional
        The angular orientation of the entity. Default is Orientation().

    Attributes
    ----------
    ds : float
        Length along the road.
    dt : float
        Lateral offset from the center.
    target : str
        ID of the entity.
    orient : Orientation
        The angular orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        ds: float,
        dt: float,
        entity: str,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the RelativeRoadPosition.

        Parameters
        ----------
        ds : float
            Length along the road.
        dt : float
            Lateral offset from the center.
        entity : str
            ID of the entity.
        orientation : Orientation, optional
            The angular orientation of the entity. Default is
            Orientation().
        """
        self.ds = convert_float(ds)
        self.dt = convert_float(dt)
        self.target = entity
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orient = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, RelativeRoadPosition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.orient == other.orient
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeRoadPosition":
        """Parse the XML element of RelativeRoadPosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RelativeRoadPosition
            A RelativeRoadPosition object.
        """
        position_element = find_mandatory_field(
            element, "RelativeRoadPosition"
        )

        ds = convert_float(position_element.attrib["ds"])
        dt = convert_float(position_element.attrib["dt"])
        entityref = position_element.attrib["entityRef"]

        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        return RelativeRoadPosition(ds, dt, entityref, orientation)

    def get_attributes(self) -> dict:
        """Return the attributes of the RelativeRoadPosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            RelativeRoadPosition.
        """
        retdict = {}
        retdict["entityRef"] = self.target
        retdict["ds"] = str(self.ds)
        retdict["dt"] = str(self.dt)
        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the RelativeRoadPosition.

        Parameters
        ----------
        elementname : str, optional
            Used if another name is needed for the position. Default is
            "Position".

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the RelativeRoadPosition.
        """
        element = ET.Element(elementname)
        roadpos = ET.SubElement(
            element, "RelativeRoadPosition", attrib=self.get_attributes()
        )
        if self.orient.is_filled():
            roadpos.append(self.orient.get_element())
        return element


class LanePosition(_PositionType):
    """The LanePosition creates a LanePosition in OpenScenario.

    Parameters
    ----------
    s : float
        Length along the road.
    offset : float
        Offset from the center of the lane.
    lane_id : str
        Lane of the road.
    road_id : str
        ID of the road.
    orientation : Orientation, optional
        The angular orientation of the entity. Default is Orientation().

    Attributes
    ----------
    s : float
        Length along the road.
    offset : float
        Offset from the center of the lane.
    lane_id : str
        Lane of the road.
    road_id : str
        ID of the road.
    orient : Orientation
        The angular orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        s: float,
        offset: float,
        lane_id: str,
        road_id: str,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the LanePosition.

        Parameters
        ----------
        s : float
            Length along the road.
        offset : float
            Offset from the center of the lane.
        lane_id : str
            Lane of the road.
        road_id : str
            ID of the road.
        orientation : Orientation, optional
            The angular orientation of the entity. Default is
            Orientation().
        """
        self.s = convert_float(s)
        self.lane_id = lane_id
        self.offset = convert_float(offset)
        self.road_id = road_id
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orient = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, LanePosition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.orient == other.orient
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "LanePosition":
        """Parse the XML element of LanePosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        LanePosition
            A LanePosition object.
        """
        position_element = find_mandatory_field(element, "LanePosition")
        roadId = position_element.attrib["roadId"]
        s = convert_float(position_element.attrib["s"])
        offset = convert_float(position_element.attrib["offset"])
        laneid = position_element.attrib["laneId"]

        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        return LanePosition(s, offset, laneid, roadId, orientation)

    def get_attributes(self) -> dict:
        """Return the attributes of the LanePosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the LanePosition.
        """
        retdict = {}
        retdict["roadId"] = str(self.road_id)
        retdict["laneId"] = str(self.lane_id)
        retdict["s"] = str(self.s)
        retdict["offset"] = str(self.offset)

        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the LanePosition.

        Parameters
        ----------
        elementname : str, optional
            Used if another name is needed for the position. Default is
            "Position".

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the LanePosition.
        """
        element = ET.Element(elementname)
        lanepos = ET.SubElement(
            element, "LanePosition", attrib=self.get_attributes()
        )
        if self.orient.is_filled():
            lanepos.append(self.orient.get_element())
        return element


class RelativeLanePosition(_PositionType):
    """The RelativeLanePosition creates a RelativeLanePosition in OpenScenario.

    Parameters
    ----------
    lane_id : int
        Lane of the road.
    entity : str
        ID of the entity.
    offset : float, optional
        Offset from the center of the lane. Default is 0.
    ds : float, optional
        Length along the road (use this or dsLane). Default is None.
    dsLane : float, optional
        Relative offset along the lane (valid from V1.1) (use this or
        ds). Default is None.
    orientation : Orientation, optional
        The angular orientation of the entity. Default is Orientation().

    Attributes
    ----------
    ds : float
        Length along the road.
    dsLane : float
        Relative offset along the lane (valid from V1.1).
    offset : float
        Offset from the center of the lane.
    road_id : str
        ID of the road.
    lane_id : int
        Lane of the road.
    orient : Orientation
        The angular orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        lane_id: int,
        entity: str,
        offset: float = 0,
        ds: Optional[float] = None,
        dsLane: Optional[float] = None,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the RelativeLanePosition.

        Parameters
        ----------
        lane_id : int
            Lane of the road.
        entity : str
            ID of the entity.
        offset : float, optional
            Offset from the center of the lane. Default is 0.
        ds : float, optional
            Length along the road (use this or dsLane). Default is None.
        dsLane : float, optional
            Relative offset along the lane (valid from V1.1) (use this
            or ds). Default is None.
        orientation : Orientation, optional
            The angular orientation of the entity. Default is
            Orientation().
        """
        if ds is not None and dsLane is not None:
            raise ToManyOptionalArguments(
                "Not both of ds and dsLane can be used."
            )
        if ds is None and dsLane is None:
            raise NotEnoughInputArguments(
                "Either ds or dsLane is needed as input."
            )
        self.ds = convert_float(ds)
        self.dsLane = convert_float(dsLane)
        self.lane_id = convert_int(lane_id)
        self.offset = convert_float(offset)
        self.entity = entity

        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orient = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, RelativeLanePosition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.orient == other.orient
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeLanePosition":
        """Parse the XML element of RelativeLanePosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RelativeLanePosition
            A RelativeLanePosition object.
        """
        position_element = find_mandatory_field(
            element, "RelativeLanePosition"
        )
        ds = None
        dslane = None
        if "ds" in position_element.attrib:
            ds = convert_float(position_element.attrib["ds"])

        offset = convert_float(position_element.attrib["offset"])
        if "dsLane" in position_element.attrib:
            dslane = convert_float(position_element.attrib["dsLane"])

        dLane = convert_int(position_element.attrib["dLane"])

        entityref = position_element.attrib["entityRef"]
        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        return RelativeLanePosition(
            dLane, entityref, offset, ds, dslane, orientation
        )

    def get_attributes(self) -> dict:
        """Return the attributes of the RelativeLanePosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            RelativeLanePosition.
        """
        retdict = {}
        retdict["entityRef"] = self.entity
        if self.ds is not None:
            retdict["ds"] = str(self.ds)
        if self.dsLane is not None and not self.isVersion(minor=0):
            retdict["dsLane"] = str(self.dsLane)
        elif self.dsLane is not None and self.isVersion(minor=0):
            raise OpenSCENARIOVersionError(
                "dsLane was introduced in OpenSCENARIO V1.1, not in 1.0"
            )
        retdict["offset"] = str(self.offset)
        retdict["dLane"] = str(self.lane_id)
        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the RelativeLanePosition.

        Parameters
        ----------
        elementname : str, optional
            Used if another name is needed for the position. Default is
            "Position".

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the RelativeLanePosition.
        """
        element = ET.Element(elementname)
        lanepos = ET.SubElement(
            element, "RelativeLanePosition", attrib=self.get_attributes()
        )
        if self.orient.is_filled():
            lanepos.append(self.orient.get_element())
        return element


class RoutePositionOfCurrentEntity(_PositionType):
    """RoutePositionOfCurrentEntity creates a RoutePosition with the
    InRoutePosition of type PositionOfCurrentEntity.

    Parameters
    ----------
    route_ref : Route or CatalogReference
        Reference to the route the position is calculated from.
    entity : str
        Reference to the entity on the route.
    orientation : Orientation, optional
        Orientation of the entity. Default is Orientation().

    Attributes
    ----------
    route_ref : Route or CatalogReference
        Reference to the route the position is calculated from.
    entity : str
        Reference to the entity on the route.
    orientation : Orientation
        Orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(
        self,
        route_ref: VersionBase,
        entity: str,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the RoutePositionOfCurrentEntity class.

        Parameters
        ----------
        route_ref : Route or CatalogReference
            Reference to the route the position is calculated from.
        entity : str
            Reference to the entity on the route.
        orientation : Orientation, optional
            Orientation of the entity. Default is Orientation().
        """
        if not isinstance(route_ref, (Route, CatalogReference)):
            raise TypeError(
                "route input not of type Route or CatalogReference"
            )
        self.route_ref = route_ref
        self.entity = entity
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orientation = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, RoutePositionOfCurrentEntity):
            if (
                self.entity == other.entity
                and self.orientation == other.orientation
                and self.route_ref == other.route_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RoutePositionOfCurrentEntity":
        """Parse the XML element of RoutePositionOfCurrentEntity.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RoutePositionOfCurrentEntity
            A RoutePositionOfCurrentEntity object.
        """
        position_element = find_mandatory_field(element, "RoutePosition")
        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        entityelement = find_mandatory_field(
            position_element, "InRoutePosition/FromCurrentEntity"
        )
        entity = entityelement.attrib["entityRef"]
        route_element = find_mandatory_field(position_element, "RouteRef")
        if route_element.find("Route") is not None:
            routeref = Route.parse(
                find_mandatory_field(route_element, "Route")
            )
        else:
            routeref = CatalogReference.parse(
                find_mandatory_field(route_element, "CatalogReference")
            )

        return RoutePositionOfCurrentEntity(routeref, entity, orientation)

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the RoutePositionOfCurrentEntity.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the
            RoutePositionOfCurrentEntity.
        """
        element = ET.Element(elementname)
        relement = ET.SubElement(element, "RoutePosition")
        routeref = ET.SubElement(relement, "RouteRef")
        routeref.append(self.route_ref.get_element())
        relement.append(self.orientation.get_element())
        inroute = ET.SubElement(relement, "InRoutePosition")
        ET.SubElement(
            inroute, "FromCurrentEntity", attrib={"entityRef": self.entity}
        )
        return element


class RoutePositionInRoadCoordinates(_PositionType):
    """RoutePositionInRoadCoordinates creates a RoutePosition with the
    InRoutePosition of type PositionInRoadCoordinates.

    Parameters
    ----------
    route_ref : Route or CatalogReference
        Reference to the route the position is calculated from.
    s : float
        S coordinate of the road.
    t : float
        T coordinate of the road.
    orientation : Orientation, optional
        Orientation of the entity. Default is Orientation().

    Attributes
    ----------
    route_ref : Route or CatalogReference
        Reference to the route the position is calculated from.
    s : float
        S coordinate of the road.
    t : float
        T coordinate of the road.
    orientation : Orientation
        Orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(
        self,
        route_ref: VersionBase,
        s: float,
        t: float,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the RoutePositionInRoadCoordinates class.

        Parameters
        ----------
        route_ref : Route or CatalogReference
            Reference to the route the position is calculated from.
        s : float
            S coordinate of the road.
        t : float
            T coordinate of the road.
        orientation : Orientation, optional
            Orientation of the entity. Default is Orientation().
        """
        if not isinstance(route_ref, (Route, CatalogReference)):
            raise TypeError(
                "route input not of type Route or CatalogReference"
            )
        self.route_ref = route_ref
        self.s = convert_float(s)
        self.t = convert_float(t)
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orientation = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, RoutePositionInRoadCoordinates):
            if (
                self.s == other.s
                and self.t == other.t
                and self.orientation == other.orientation
                and self.route_ref == other.route_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RoutePositionInRoadCoordinates":
        """Parse the XML element of RoutePositionInRoadCoordinates.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RoutePositionInRoadCoordinates
            A RoutePositionInRoadCoordinates object.
        """
        position_element = find_mandatory_field(element, "RoutePosition")
        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        road_coord_element = find_mandatory_field(
            position_element, "InRoutePosition/FromRoadCoordinates"
        )
        s = convert_float(road_coord_element.attrib["pathS"])
        t = convert_float(road_coord_element.attrib["t"])
        route_element = find_mandatory_field(position_element, "RouteRef")
        if route_element.find("Route") is not None:
            routeref = Route.parse(
                find_mandatory_field(route_element, "Route")
            )
        else:
            routeref = CatalogReference.parse(
                find_mandatory_field(route_element, "CatalogReference")
            )

        return RoutePositionInRoadCoordinates(routeref, s, t, orientation)

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the RoutePositionInRoadCoordinates.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the
            RoutePositionInRoadCoordinates.
        """
        element = ET.Element(elementname)
        relement = ET.SubElement(element, "RoutePosition")
        routeref = ET.SubElement(relement, "RouteRef")
        routeref.append(self.route_ref.get_element())
        relement.append(self.orientation.get_element())
        inroute = ET.SubElement(relement, "InRoutePosition")
        ET.SubElement(
            inroute,
            "FromRoadCoordinates",
            attrib={"pathS": str(self.s), "t": str(self.t)},
        )
        return element


class RoutePositionInLaneCoordinates(_PositionType):
    """RoutePositionInLaneCoordinates creates a RoutePosition with the
    InRoutePosition of type PositionInLaneCoordinates.

    Parameters
    ----------
    route_ref : Route or CatalogReference
        Reference to the route the position is calculated from.
    s : float
        S coordinate of the road.
    laneid : int
        T coordinate of the road.
    offset : float, optional
        Lateral offset relative to the lane. Default is 0.
    orientation : Orientation, optional
        Orientation of the entity. Default is Orientation().

    Attributes
    ----------
    route_ref : Route or CatalogReference
        Reference to the route the position is calculated from.
    s : float
        S coordinate of the road.
    laneid : int
        T coordinate of the road.
    offset : float
        Lateral offset relative to the lane.
    orientation : Orientation
        Orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(
        self,
        route_ref: VersionBase,
        s: float,
        laneid: int,
        offset: float,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the RoutePositionInLaneCoordinates class.

        Parameters
        ----------
        route_ref : Route or CatalogReference
            Reference to the route the position is calculated from.
        s : float
            S coordinate of the road.
        laneid : int
            T coordinate of the road.
        offset : float, optional
            Lateral offset relative to the lane. Default is 0.
        orientation : Orientation, optional
            Orientation of the entity. Default is Orientation().
        """
        if not isinstance(route_ref, (Route, CatalogReference)):
            raise TypeError(
                "route input not of type Route or CatalogReference"
            )
        self.route_ref = route_ref
        self.s = convert_float(s)
        self.laneid = convert_int(laneid)
        self.offset = convert_float(offset)
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orientation = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, RoutePositionInLaneCoordinates):
            if (
                self.s == other.s
                and self.laneid == other.laneid
                and self.offset == other.offset
                and self.orientation == other.orientation
                and self.route_ref == other.route_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RoutePositionInLaneCoordinates":
        """Parse the XML element of RoutePositionInLaneCoordinates.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RoutePositionInLaneCoordinates
            A RoutePositionInLaneCoordinates object.
        """
        position_element = find_mandatory_field(element, "RoutePosition")
        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        lane_coord_element = find_mandatory_field(
            position_element, "InRoutePosition/FromLaneCoordinates"
        )
        s = convert_float(lane_coord_element.attrib["pathS"])
        lane_id = convert_int(lane_coord_element.attrib["laneId"])
        try:
            offset = convert_float(lane_coord_element.attrib["laneOffset"])
        except KeyError:
            offset = 0
        route_element = find_mandatory_field(position_element, "RouteRef")
        if route_element.find("Route") is not None:
            routeref = Route.parse(
                find_mandatory_field(route_element, "Route")
            )
        else:
            routeref = CatalogReference.parse(
                find_mandatory_field(route_element, "CatalogReference")
            )

        return RoutePositionInLaneCoordinates(
            routeref, s, lane_id, offset, orientation
        )

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the RoutePositionInLaneCoordinates.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the
            RoutePositionInLaneCoordinates.
        """
        element = ET.Element(elementname)
        relement = ET.SubElement(element, "RoutePosition")
        routeref = ET.SubElement(relement, "RouteRef")
        routeref.append(self.route_ref.get_element())
        relement.append(self.orientation.get_element())
        inroute = ET.SubElement(relement, "InRoutePosition")
        ET.SubElement(
            inroute,
            "FromLaneCoordinates",
            attrib={
                "pathS": str(self.s),
                "laneId": str(self.laneid),
                "laneOffset": str(self.offset),
            },
        )
        return element


class TrajectoryPosition(_PositionType):
    """TrajectoryPosition creates a TrajectoryPosition in OpenSCENARIO.

    Parameters
    ----------
    trajectory : Trajectory or CatalogReference
        T coordinate of the road.
    s : float
        S coordinate of the trajectory.
    t : float, optional
        S coordinate of the road. Default is None.
    orientation : Orientation, optional
        Orientation of the entity. Default is Orientation().

    Attributes
    ----------
    trajectory : Trajectory or CatalogReference
        T coordinate of the road.
    s : float
        S coordinate of the trajectory.
    t : float
        S coordinate of the road. Default is None.
    orientation : Orientation
        Orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        trajectory: VersionBase,
        s: float,
        t: Optional[float] = None,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the TrajectoryPosition class.

        Parameters
        ----------
        trajectory : Trajectory or CatalogReference
            T coordinate of the road.
        s : float
            S coordinate of the trajectory.
        t : float, optional
            S coordinate of the road. Default is None.
        orientation : Orientation, optional
            Orientation of the entity. Default is Orientation().
        """
        if not isinstance(trajectory, (Trajectory, CatalogReference)):
            raise TypeError(
                "trajectory input not of type Trajectory or CatalogReference"
            )
        self.trajectory = trajectory
        self.s = convert_float(s)
        self.t = convert_float(t)
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orientation = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, TrajectoryPosition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.orientation == other.orientation
                and self.trajectory == other.trajectory
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrajectoryPosition":
        """Parse the XML element of TrajectoryPosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        TrajectoryPosition
            A TrajectoryPosition object.
        """
        position_element = find_mandatory_field(element, "TrajectoryPosition")
        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()

        s = position_element.attrib["s"]
        t = None
        if "t" in position_element:
            s = position_element.attrib["s"]

        trajectory_element = find_mandatory_field(
            position_element, "TrajectoryRef"
        )
        if trajectory_element.find("Trajectory") is not None:
            trajectory = Trajectory.parse(
                find_mandatory_field(trajectory_element, "Trajectory")
            )
        else:
            trajectory = CatalogReference.parse(
                find_mandatory_field(trajectory_element, "CatalogReference")
            )

        return TrajectoryPosition(trajectory, s, t, orientation)

    def get_attributes(self) -> dict:
        """Return the attributes of the TrajectoryPosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            TrajectoryPosition.
        """
        retdict = {}
        retdict["s"] = str(self.s)
        if self.t is not None:
            retdict["t"] = str(self.t)
        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the TrajectoryPosition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the TrajectoryPosition.
        """
        if self.isVersion(minor=0):
            raise OpenSCENARIOVersionError(
                "TrajectoryPosition was introduced in OpenSCENARIO V1.1"
            )

        element = ET.Element(elementname)
        traj_element = ET.SubElement(
            element, "TrajectoryPosition", attrib=self.get_attributes()
        )
        trajref_element = ET.SubElement(traj_element, "TrajectoryRef")
        trajref_element.append(self.trajectory.get_element())
        traj_element.append(self.orientation.get_element())

        return element


class GeoPosition(_PositionType):
    """GeoPosition creates a GeoPosition in OpenSCENARIO.

    Parameters
    ----------
    latitue : float
        Latitude point on earth.
    longitude : float
        Longitude point on earth.
    height : float, optional
        Height above surface. Default is None.
    orientation : Orientation, optional
        Orientation of the entity. Default is Orientation().

    Attributes
    ----------
    latitue : float
        Latitude point on earth.
    longitude : float
        Longitude point on earth.
    height : float
        Height above surface. Default is None.
    orientation : Orientation
        Orientation of the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        height: Optional[float] = None,
        orientation: Orientation = Orientation(),
    ) -> None:
        """Initialize the GeoPosition class.

        Parameters
        ----------
        latitue : float
            Latitude point on earth.
        longitude : float
            Longitude point on earth.
        height : float, optional
            Height above surface. Default is None.
        orientation : Orientation, optional
            Orientation of the entity. Default is Orientation().
        """
        self.longitude = convert_float(longitude)
        self.latitude = convert_float(latitude)
        self.height = convert_float(height)
        if not isinstance(orientation, Orientation):
            raise TypeError("input orientation is not of type Orientation")
        self.orientation = orientation

    def __eq__(self, other) -> bool:
        if isinstance(other, GeoPosition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.orientation == other.orientation
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "GeoPosition":
        """Parse the XML element of GeoPosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        GeoPosition
            A GeoPosition object.
        """
        position_element = find_mandatory_field(element, "GeoPosition")
        if "longitude" in position_element.attrib:
            longitude = convert_float(position_element.attrib["longitude"])
        elif "longitudeDeg" in position_element.attrib:
            longitude = convert_float(position_element.attrib["longitudeDeg"])
        else:
            raise KeyError("Cannot find valid longitude for GeoPosition")

        if "latitude" in position_element.attrib:
            latitude = convert_float(position_element.attrib["latitude"])
        elif "latitudeDeg" in position_element.attrib:
            latitude = convert_float(position_element.attrib["latitudeDeg"])
        else:
            raise KeyError("Cannot find valid latitude for GeoPosition")

        if "height" in position_element.attrib:
            height = convert_float(position_element.attrib["height"])
        elif "altitude" in position_element.attrib:
            height = convert_float(position_element.attrib["altitude"])
        else:
            height = None

        if position_element.find("Orientation") is not None:
            orientation = Orientation.parse(
                find_mandatory_field(position_element, "Orientation")
            )
        else:
            orientation = Orientation()
        return GeoPosition(latitude, longitude, height, orientation)

    def get_attributes(self) -> dict:
        """Return the attributes of the GeoPosition as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the GeoPosition.
        """
        retdict = {}
        if self.isVersion(minor=1):
            retdict["longitude"] = str(self.longitude)
            retdict["latitude"] = str(self.latitude)
            if self.height is not None:
                retdict["height"] = str(self.height)
        else:
            retdict["longitudeDeg"] = str(self.longitude)
            retdict["latitudeDeg"] = str(self.latitude)
            if self.height is not None:
                retdict["altitude"] = str(self.height)
        return retdict

    def get_element(self, elementname: str = "Position") -> ET.Element:
        """Return the ElementTree of the GeoPosition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the GeoPosition.
        """
        if self.isVersion(minor=0):
            raise OpenSCENARIOVersionError(
                "GeoPosition was introduced in OpenSCENARIO V1.1"
            )

        element = ET.Element(elementname)
        traj_element = ET.SubElement(
            element, "GeoPosition", self.get_attributes()
        )
        traj_element.append(self.orientation.get_element())

        return element


class Polyline(_TrajectoryShape):
    """The Polyline class creates a polyline of (minimum 2) positions.

    Parameters
    ----------
    time : list of float
        A list of timings for the positions.
    positions : list of _PositionType
        List of positions to create the polyline.

    Attributes
    ----------
    time : list of float
        A list of timings for the positions.
    positions : list of _PositionType
        List of positions to create the polyline.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(
        self, time: list[float], positions: list[_PositionType]
    ) -> None:
        """Initialize the Polyline.

        Parameters
        ----------
        time : list of float
            A list of timings for the positions (as of OpenSCENARIO
            V1.1 this can be empty).
        positions : list of _PositionType
            List of positions to create the polyline.
        """
        if time and len(time) < 2:
            raise ValueError("not enough time inputs")
        if len(positions) < 2:
            raise ValueError("not enough position inputs")
        if time and (len(time) != len(positions)):
            raise ValueError("time and positions are not the same length")
        for p in positions:
            if not isinstance(p, _PositionType):
                raise TypeError("position input is not a valid position")
        self.positions = positions
        self.time = [convert_float(x) for x in time]

    def __eq__(self, other) -> bool:
        if isinstance(other, Polyline):
            if self.time == other.time and self.positions == other.positions:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "Polyline":
        """Parse the XML element of Polyline.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A Polyline element (same as generated by the class itself).

        Returns
        -------
        Polyline
            A Polyline object.
        """
        polyline_element = find_mandatory_field(element, "Polyline")
        vertexes = polyline_element.findall("Vertex")
        time_list = []
        position_list = []
        for vertex in vertexes:
            if "time" in vertex.attrib:
                time_list.append(convert_float(vertex.attrib["time"]))
            position_list.append(
                _PositionFactory.parse_position(
                    find_mandatory_field(vertex, "Position")
                )
            )
        return Polyline(time_list, position_list)

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the Polyline.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the Polyline.
        """
        shape = ET.Element("Shape")
        element = ET.SubElement(shape, ("Polyline"))
        for i, pos in enumerate(self.positions):
            time_dict = {}
            if self.time:
                time_dict = {"time": str(self.time[i])}
            vert = ET.SubElement(element, "Vertex", attrib=time_dict)
            vert.append(pos.get_element())
        return shape


class Clothoid(_TrajectoryShape):
    """The Clothoid class creates a Clothoid shape.

    Parameters
    ----------
    curvature : float
        Start curvature of the clothoid.
    curvature_change : float
        Rate of clothoid curvature change.
    length : float
        Length of the clothoid.
    startposition : _PositionType
        Start position of the clothoid.
    starttime : float, optional
        Start time of the clothoid. Default is None.
    stoptime : float, optional
        End time of the clothoid. Default is None.

    Attributes
    ----------
    curvature : float
        Start curvature of the clothoid.
    curvature_change : float
        Rate of clothoid curvature change.
    length : float
        Length of the clothoid.
    startposition : _PositionType
        Start position of the clothoid.
    starttime : float
        Start time of the clothoid. Default is None.
    stoptime : float
        End time of the clothoid. Default is None.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        curvature: float,
        curvature_change: float,
        length: float,
        startposition: _PositionType,
        starttime: Optional[float] = None,
        stoptime: Optional[float] = None,
    ) -> None:
        """Initialize the Clothoid.

        Parameters
        ----------
        curvature : float
            Start curvature of the clothoid.
        curvature_change : float
            Rate of clothoid curvature change.
        length : float
            Length of the clothoid.
        startposition : _PositionType
            Start position of the clothoid.
        starttime : float, optional
            Start time of the clothoid. Default is None.
        stoptime : float, optional
            End time of the clothoid. Default is None.
        """
        # TODO: The input order needs to be changed, curvature_change has
        # cardinality 0, breaking change!
        self.curvature = convert_float(curvature)
        self.curvature_change = convert_float(curvature_change)
        self.length = convert_float(length)
        if not isinstance(startposition, _PositionType):
            raise TypeError("position input is not a valid position")
        self.startposition = startposition

        self.starttime = convert_float(starttime)
        self.stoptime = convert_float(stoptime)
        if (self.starttime is None and self.stoptime is not None) or (
            self.starttime is not None and self.stoptime is None
        ):
            raise ValueError(
                "Both start and stoptime has to be set, or none of them"
            )

    def __eq__(self, other) -> bool:
        if isinstance(other, Clothoid):
            if (
                self.get_attributes() == other.get_attributes()
                and self.startposition == other.startposition
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "Clothoid":
        """Parse the XML element of Clothoid.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A Clothoid element (same as generated by the class itself).

        Returns
        -------
        Clothoid
            A Clothoid object.
        """
        clothoid_element = find_mandatory_field(element, "Clothoid")
        start_position = _PositionFactory.parse_position(
            find_mandatory_field(clothoid_element, "Position")
        )
        length = convert_float(clothoid_element.attrib["length"])
        curvature = convert_float(clothoid_element.attrib["curvature"])
        starttime = None
        stoptime = None
        if "startTime" in clothoid_element.attrib:
            starttime = convert_float(clothoid_element.attrib["startTime"])

        if "stopTime" in clothoid_element.attrib:
            stoptime = convert_float(clothoid_element.attrib["stopTime"])

        if "curvatureDot" in clothoid_element.attrib:
            curvature_change = convert_float(
                clothoid_element.element["curvaturePrime"]
            )
        elif "curvaturePrime" in clothoid_element.attrib:
            curvature_change = convert_float(
                clothoid_element.attrib["curvaturePrime"]
            )
        else:
            raise XMLStructureError(
                "curatureDot or curvaturePrime not found in Clothoid"
            )
        return Clothoid(
            curvature,
            curvature_change,
            length,
            start_position,
            starttime,
            stoptime,
        )

    def get_attributes(self) -> dict:
        """Return the attributes of the Clothoid as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the Clothoid.
        """
        retdict = {}
        retdict["curvature"] = str(self.curvature)
        if self.isVersion(minor=0):
            retdict["curvatureDot"] = str(self.curvature_change)
        else:
            retdict["curvaturePrime"] = str(self.curvature_change)
        retdict["length"] = str(self.length)
        if self.starttime is not None:
            retdict["startTime"] = str(self.starttime)
            retdict["stopTime"] = str(self.stoptime)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the Clothoid.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the Clothoid.
        """
        shape = ET.Element("Shape")
        element = ET.SubElement(
            shape, "Clothoid", attrib=self.get_attributes()
        )
        element.append(self.startposition.get_element())

        return shape


################## Utilities using positions (here due to parsing dependencies)


class ControlPoint(VersionBase):
    """The ControlPoint class is used by Nurbs to define points.

    Parameters
    ----------
    position : _PositionType
        A position for the point.
    time : float, optional
        Optional time specification of the point. Default is None.
    weight : float, optional
        Optional weight of the point. Default is None.

    Attributes
    ----------
    position : _PositionType
        A position for the point.
    time : float
        Optional time specification of the point. Default is None.
    weight : float
        Optional weight of the point. Default is None.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        position: _PositionType,
        time: Optional[float] = None,
        weight: Optional[float] = None,
    ) -> None:
        """Initialize the ControlPoint.

        Parameters
        ----------
        position : _PositionType
            A position for the point.
        time : float, optional
            Optional time specification of the point. Default is None.
        weight : float, optional
            Optional weight of the point. Default is None.
        """
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not a valid position")
        self.position = position
        self.time = convert_float(time)
        self.weight = convert_float(weight)

    def __eq__(self, other) -> bool:
        if isinstance(other, ControlPoint):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "ControlPoint":
        """Parse the XML element of ControlPoint.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A ControlPoint element (same as generated by the class
            itself).

        Returns
        -------
        ControlPoint
            A ControlPoint object.
        """
        time = None
        weight = None
        if "time" in element.attrib:
            time = convert_float(element.attrib["time"])
        if "weight" in element.attrib:
            weight = convert_float(element.attrib["weight"])
        pos_element = find_mandatory_field(element, "Position")
        position = _PositionFactory.parse_position(pos_element)

        return ControlPoint(position, time, weight)

    def get_attributes(self) -> dict:
        """Return the attributes of the ControlPoint as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the ControlPoint.
        """
        retdict = {}
        if self.time is not None:
            retdict["time"] = str(self.time)
        if self.weight is not None:
            retdict["weight"] = str(self.weight)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the ControlPoint.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the ControlPoint.
        """
        element = ET.Element("ControlPoint", attrib=self.get_attributes())
        element.append(self.position.get_element())
        return element


class Waypoint(VersionBase):
    """The Waypoint class creates a waypoint for a route.

    Parameters
    ----------
    position : _PositionType
        Any position for the route.
    routestrategy : RouteStrategy
        Routing strategy for this waypoint.

    Attributes
    ----------
    position : _PositionType
        Any position for the route.
    routestrategy : RouteStrategy
        Routing strategy for this waypoint.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self, position: _PositionType, routestrategy: RouteStrategy
    ) -> None:
        """Initialize the Waypoint.

        Parameters
        ----------
        position : _PositionType
            Any position for the route.
        routestrategy : RouteStrategy
            Routing strategy for this waypoint.
        """
        if not isinstance(position, _PositionType):
            raise TypeError("position input not a valid Position")
        self.position = position
        self.routestrategy = convert_enum(routestrategy, RouteStrategy)

    def __eq__(self, other) -> bool:
        if isinstance(other, Waypoint):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "Waypoint":
        """Parse the XML element of Waypoint.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A Waypoint element (same as generated by the class itself).

        Returns
        -------
        Waypoint
            A Waypoint object.
        """
        pos_element = find_mandatory_field(element, "Position")
        position = _PositionFactory.parse_position(pos_element)
        strategy = convert_enum(element.attrib["routeStrategy"], RouteStrategy)
        return Waypoint(position, strategy)

    def get_attributes(self) -> dict:
        """Return the attributes of the Waypoint as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the Waypoint.
        """
        return {"routeStrategy": self.routestrategy.get_name()}

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the Waypoint.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the Waypoint.
        """
        element = ET.Element("Waypoint", attrib=self.get_attributes())
        element.append(self.position.get_element())
        return element


class Route(_BaseCatalog):
    """The Route class creates a route, needs at least two waypoints to be
    valid.

    Parameters
    ----------
    name : str
        Name of the Route.
    closed : bool, optional
        If the waypoints form a loop. Default is False.

    Attributes
    ----------
    name : str
        Name of the Route.
    closed : bool
        If the waypoints form a loop.
    waypoints : list of Waypoint
        A list of waypoints.
    parameters : ParameterDeclarations
        Parameters for the route.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    add_waypoint(position, routestrategy)
        Adds a waypoint to the route (minimum two).
    add_parameter(parameter)
        Adds a parameter to the route.
    append_to_catalog(filename)
        Adds the Route to an existing catalog.
    dump_to_catalog(filename, name, description, author)
        Creates a new catalog with the Route.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, name: str, closed: bool = False) -> None:
        """Initialize the Route.

        Parameters
        ----------
        name : str
            Name of the Route.
        closed : bool, optional
            If the waypoints form a loop. Default is False.
        """
        super().__init__()
        self.name = name
        self.closed = convert_bool(closed)
        self.waypoints = []

    def __eq__(self, other) -> bool:
        if isinstance(other, Route):
            if (
                self.get_attributes() == other.get_attributes()
                and self.parameters == other.parameters
                and self.waypoints == other.waypoints
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "Route":
        """Parse the XML element of Route.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A Route element (same as generated by the class itself).

        Returns
        -------
        Route
            A Route object.
        """
        name = element.attrib["name"]
        closed = convert_bool(element.attrib["closed"])
        route = Route(name, closed)
        all_wps = element.findall("Waypoint")
        for wp in all_wps:
            waypoint = Waypoint.parse(wp)
            route.waypoints.append(waypoint)
        return route

    def add_waypoint(
        self, position: _PositionType, routestrategy: RouteStrategy
    ) -> "Route":
        """Add a waypoint to the Route.

        Parameters
        ----------
        position : _PositionType
            Any position for the route.
        routestrategy : RouteStrategy
            Routing strategy for this waypoint.
        """
        # note: the checks for types are done in Waypoint
        self.waypoints.append(Waypoint(position, routestrategy))
        return self

    def get_attributes(self) -> dict:
        """Return the attributes of the Route as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the Route.
        """
        retdict = {}
        retdict["name"] = self.name
        retdict["closed"] = get_bool_string(self.closed)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the Route.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the Route.
        """
        if len(self.waypoints) < 2:
            raise ValueError("Too few waypoints")
        element = ET.Element("Route", attrib=self.get_attributes())
        self.add_parameters_to_element(element)
        for w in self.waypoints:
            element.append(w.get_element())
        return element


class Trajectory(_BaseCatalog):
    """The Trajectory class creates a Trajectory.

    Parameters
    ----------
    name : str
        Name of the trajectory.
    closed : bool
        If the trajectory is closed at the end.

    Attributes
    ----------
    name : str
        Name of the trajectory.
    closed : bool
        If the trajectory is closed at the end.
    parameters : ParameterDeclarations
        Parameters for the trajectory.
    shapes : _TrajectoryShape
        The shape building the trajectory.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    add_shape(shape)
        Adds a shape to the trajectory.
    add_parameter(parameter)
        Adds a parameter to the route.
    append_to_catalog(filename)
        Adds the vehicle to an existing catalog.
    dump_to_catalog(filename, name, description, author)
        Creates a new catalog with the vehicle.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, name: str, closed: bool) -> None:
        """Initialize the Trajectory.

        Parameters
        ----------
        name : str
            Name of the trajectory.
        closed : bool
            If the trajectory is closed at the end.
        """
        super().__init__()
        self.name = name
        self.closed = convert_bool(closed)
        self.shapes = None

    def __eq__(self, other) -> bool:
        if isinstance(other, Trajectory):
            if (
                self.get_attributes() == other.get_attributes()
                and self.parameters == other.parameters
                and self.shapes == other.shapes
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "Trajectory":
        """Parse the XML element of Trajectory.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A Trajectory element (same as generated by the class
            itself).

        Returns
        -------
        Trajectory
            A Trajectory object.
        """
        name = element.attrib["name"]
        closed = convert_bool(element.attrib["closed"])
        pos_element = find_mandatory_field(element, "Shape")
        shape = _ShapeFactory.parse_shape(pos_element)
        params_element = element.find("ParameterDeclarations")
        if type(params_element) is ET.Element:
            params = ParameterDeclarations.parse(params_element)
        else:
            params = ParameterDeclarations()
        trajectory = Trajectory(name, closed)
        trajectory.add_shape(shape)
        for param in params.parameters:
            trajectory.add_parameter(param)
        return trajectory

    def add_shape(self, shape: _TrajectoryShape) -> "Trajectory":
        """Add a shape to the trajectory (only the same shape can be used).

        Parameters
        ----------
        shape : _TrajectoryShape
            The shape to be added to the trajectory.
        """
        if not isinstance(shape, (Polyline, Clothoid, Nurbs)):
            raise TypeError("shape input neither of type _TrajectoryShape")
        self.shapes = shape
        return self

    def get_attributes(self) -> dict:
        """Return the attributes of the Trajectory as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the Trajectory.
        """
        retdict = {}
        retdict["name"] = self.name
        retdict["closed"] = get_bool_string(self.closed)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the Trajectory.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the Trajectory.
        """
        element = ET.Element("Trajectory", attrib=self.get_attributes())
        self.add_parameters_to_element(element)
        if self.shapes:
            element.append(self.shapes.get_element())
        else:
            raise NotEnoughInputArguments(
                "No shape has been added to the trajectory"
            )
        return element


class Nurbs(_TrajectoryShape):
    """The Nurbs class creates a Nurbs shape.

    Parameters
    ----------
    order : int
        Order of the nurbs.

    Attributes
    ----------
    order : int
        Order of the nurbs.
    controlpoints : list of ControlPoint
        A list of control points creating the nurbs.
    knots : list of float
        Knots of the nurbs (must be order + len(controlpoints)) in
        descending order.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    add_knots(knots)
        Adds the knots to the nurbs.
    add_control_point(controlpoint)
        Adds a control point to the nurbs.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, order: int) -> None:
        """Initialize the Nurbs.

        Parameters
        ----------
        order : int
            Order of the nurbs.
        """
        self.order = convert_int(order)
        self.controlpoints = []
        self.knots = []

    def __eq__(self, other) -> bool:
        if isinstance(other, Nurbs):
            if (
                self.get_attributes() == other.get_attributes()
                and self.controlpoints == other.controlpoints
                and self.knots == other.knots
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "Nurbs":
        """Parse the XML element of Nurbs.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A Nurbs element (same as generated by the class itself).

        Returns
        -------
        Nurbs
            A Nurbs object.
        """
        nurbs_element = find_mandatory_field(element, "Nurbs")
        order = convert_int(nurbs_element.attrib["order"])

        # print(pos_element)
        # position = _PositionFactory.parse_position(pos_element)
        nurbs = Nurbs(order)
        control_point_elements = nurbs_element.findall("ControlPoint")
        for cp in control_point_elements:
            nurbs.add_control_point(ControlPoint.parse(cp))
        knots_elements = nurbs_element.findall("Knot")
        knots = []
        for k in knots_elements:
            print(k)
            knots.append(convert_float(k.attrib["value"]))
        nurbs.add_knots(knots)
        return nurbs

    def add_knots(self, knots: list[float]) -> "Nurbs":
        """Add a list of knots to the Nurbs.

        Parameters
        ----------
        knots : list of float
            Knots of the nurbs (must be order + len(controlpoints)) in
            descending order.
        """
        self.knots = knots
        return self

    def add_control_point(self, controlpoint: ControlPoint) -> "Nurbs":
        """Add a control point to the Nurbs.

        Parameters
        ----------
        controlpoint : ControlPoint
            A contact point to add to the nurbs.
        """
        if not isinstance(controlpoint, ControlPoint):
            raise TypeError("controlpoint input is not of type ControlPoint")
        self.controlpoints.append(controlpoint)
        return self

    def get_attributes(self) -> dict:
        """Return the attributes of the Nurbs as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the Nurbs.
        """
        retdict = {}
        retdict["order"] = str(self.order)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the Nurbs.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the Nurbs.
        """
        shape = ET.Element("Shape")
        element = ET.SubElement(shape, "Nurbs", attrib=self.get_attributes())
        if (len(self.controlpoints) + self.order) != len(self.knots):
            raise ValueError(
                "Number of knots is not equal to the number of contactpoints + order"
            )
        for c in self.controlpoints:
            element.append(c.get_element())
        for k in self.knots:
            ET.SubElement(element, "Knot", attrib={"value": str(k)})

        return shape
