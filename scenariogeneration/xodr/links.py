"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import warnings
import xml.etree.ElementTree as ET
from typing import Optional

import numpy as np

from ..helpers import enum2str
from .enumerations import (
    ContactPoint,
    Direction,
    ElementType,
    JunctionGroupType,
    JunctionType,
    Orientation,
    enumchecker,
)
from .exceptions import (
    GeneralIssueInputArguments,
    NotEnoughInputArguments,
    NotSameAmountOfLanesError,
)
from .utils import XodrBase


class _Links(XodrBase):
    """Create a Link element used for road linking in OpenDRIVE.

    Attributes
    ----------
    links : list of _Link
        All links added to this object.

    Methods
    -------
    add_link(link)
        Add a link to the list of links.
    get_predecessor_contact_point()
        Get the contact point of the predecessor link, if it exists.
    get_successor_contact_point()
        Get the contact point of the successor link, if it exists.
    get_predecessor_type()
        Get the type of the predecessor link, if it exists.
    get_successor_type()
        Get the type of the successor link, if it exists.
    get_predecessor_id()
        Get the ID of the predecessor link, if it exists.
    get_successor_id()
        Get the ID of the successor link, if it exists.
    get_element()
        Return the ElementTree representation of the `_Links` object.
    """

    def __init__(self) -> None:
        """Initialize the `_Links` object.

        Attributes
        ----------
        links : list of _Link
            A list to store all links added to this object.
        """
        super().__init__()
        self.links = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Links) and super().__eq__(other):
            if self.links == other.links:
                return True
        return False

    def add_link(self, link: "_Link") -> "_Links":
        """Add a `_Link` to the list of links.

        Parameters
        ----------
        link : _Link
            The link to be added.

        Returns
        -------
        _Links
            The updated `_Links` object.

        Raises
        ------
        TypeError
            If `link` is not of type `_Link`.
        """
        if not isinstance(link, _Link):
            raise TypeError("link input is not of type _Link")

        if link in self.links:
            warnings.warn(
                "Multiple identical links is detected, this might cause problems. Using the first one created. ",
                UserWarning,
            )
        elif any([link.link_type == x.link_type for x in self.links]):
            warnings.warn(
                "Multiple links of the same link_type: "
                + link.link_type
                + " is detected, this might cause problems, overwriting the old one. ",
                UserWarning,
            )
            for l in self.links:
                if l == link.link_type:
                    self.links.remove(l)
            self.links.append(link)
        else:
            self.links.append(link)
        return self

    def get_predecessor_contact_point(self) -> Optional[ContactPoint]:
        """Get the contact point of the predecessor link, if it exists.

        Returns
        -------
        ContactPoint or None
            The contact point of the predecessor link, or None if it does
            not exist.
        """
        retval = None
        for l in self.links:
            if l.link_type == "predecessor":
                retval = l.contact_point
        return retval

    def get_successor_contact_point(self) -> Optional[ContactPoint]:
        """Get the contact point of the successor link, if it exists.

        Returns
        -------
        ContactPoint or None
            The contact point of the successor link, or None if it does
            not exist.
        """
        retval = None
        for l in self.links:
            if l.link_type == "successor":
                retval = l.contact_point
        return retval

    def get_predecessor_type(self) -> Optional[ElementType]:
        """Get the type of the predecessor link, if it exists.

        Returns
        -------
        ElementType or None
            The type of the predecessor link, or None if it does not
            exist.
        """
        retval = None
        for l in self.links:
            if l.link_type == "predecessor":
                retval = l.element_type
        return retval

    def get_successor_type(self) -> Optional[ElementType]:
        """Get the type of the successor link, if it exists.

        Returns
        -------
        ElementType or None
            The type of the successor link, or None if it does not exist.
        """
        retval = None
        for l in self.links:
            if l.link_type == "successor":
                retval = l.element_type
        return retval

    def get_predecessor_id(self) -> Optional[int]:
        """Get the ID of the predecessor link, if it exists.

        Returns
        -------
        int or None
            The ID of the predecessor link, or None if it does not exist.
        """
        retval = None
        for l in self.links:
            if l.link_type == "predecessor":
                retval = l.element_id
        return retval

    def get_successor_id(self) -> Optional[int]:
        """Get the ID of the successor link, if it exists.

        Returns
        -------
        int or None
            The ID of the successor link, or None if it does not exist.
        """
        retval = None
        for l in self.links:
            if l.link_type == "successor":
                retval = l.element_id
        return retval

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `_Links` object.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the `_Links` object.
        """
        element = ET.Element("link")
        self._add_additional_data_to_element(element)
        # sort links alphabetically by link type to ensure predecessor
        # appears before successor to comply to schema
        for l in sorted(self.links, key=lambda x: x.link_type):
            element.append(l.get_element())
        return element


class _Link(XodrBase):
    """Create a predecessor/successor/neighbor element used for links in
    OpenDRIVE.

    Parameters
    ----------
    link_type : str
        The type of link (successor, predecessor, or neighbor).
    element_id : str
        The name of the linked road.
    element_type : ElementType, optional
        The type of the linked road. Default is None.
    contact_point : ContactPoint, optional
        The contact point of the link. Default is None.
    direction : Direction, optional
        The direction of the link (used for neighbors). Default is None.

    Attributes
    ----------
    link_type : str
        The type of link (successor, predecessor, or neighbor).
    element_id : str
        The name of the linked road.
    element_type : ElementType
        The type of the linked road.
    contact_point : ContactPoint
        The contact point of the link (used for successor and predecessor).
    direction : Direction
        The direction of the link (used for neighbors).

    Methods
    -------
    get_element()
        Return the ElementTree representation of the `_Link`.
    get_attributes()
        Return the attributes of the `_Link` as a dictionary.
    """

    def __init__(
        self,
        link_type: str,
        element_id: str,
        element_type: Optional[ElementType] = None,
        contact_point: Optional[ContactPoint] = None,
        direction: Optional[Direction] = None,
    ) -> None:
        """Initialize the `_Link` object.

        Parameters
        ----------
        link_type : str
            The type of link (successor, predecessor, or neighbor).
        element_id : str
            The name of the linked road.
        element_type : ElementType, optional
            The type of the linked road. Default is None.
        contact_point : ContactPoint, optional
            The contact point of the link. Default is None.
        direction : Direction, optional
            The direction of the link (used for neighbors).
            Default is None.

        Raises
        ------
        ValueError
            If `link_type` is "neighbor" and `direction` is not provided.
        """
        super().__init__()
        if link_type == "neighbor" and direction is None:
            raise ValueError("direction has to be defined for neighbor")

        self.link_type = link_type

        self.element_type = enumchecker(element_type, ElementType, True)
        self.element_id = element_id
        self.contact_point = enumchecker(contact_point, ContactPoint, True)
        self.direction = enumchecker(direction, Direction, True)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Link) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.link_type == other.link_type
            ):
                return True
        return False

    def get_attributes(self) -> dict:
        """Return the attributes of the `_Link` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `_Link`.
        """
        retdict = {}
        if self.element_type is None:
            retdict["id"] = str(self.element_id)
        else:
            retdict["elementType"] = enum2str(self.element_type)
            retdict["elementId"] = str(self.element_id)

        if self.contact_point:
            retdict["contactPoint"] = enum2str(self.contact_point)
        elif self.link_type == "neighbor":
            retdict["direction"] = enum2str(self.direction)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `_Link`.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the `_Link`.
        """
        element = ET.Element(self.link_type, attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class LaneLinker:
    """Store information for linking lane sections.

    NOTE: This class is not part of OpenDRIVE but serves as a helper to
    link lanes for the user.

    Attributes
    ----------
    links : list of _lanelink
        All lane links added, each represented as a tuple of predecessor
        lane, successor lane, and a boolean indicating if the link is
        found.

    Methods
    -------
    add_link(predlane, succlane, connecting_road=None)
        Add a lane link to the list.
    """

    def __init__(self) -> None:
        """Initialize the `LaneLinker` object.

        Attributes
        ----------
        links : list of _lanelink
            A list to store all lane links added to this object.
        """

        self.links = []

    def add_link(
        self,
        predlane: "Lane",
        succlane: "Lane",
        connecting_road: Optional[int] = None,
    ) -> "LaneLinker":
        """Add a lane link to the list.

        Parameters
        ----------
        predlane : Lane
            The predecessor lane.
        succlane : Lane
            The successor lane.
        connecting_road : int, optional
            The ID of a connecting road (used for junctions). Default is None.

        Returns
        -------
        LaneLinker
            The updated `LaneLinker` object.
        """
        self.links.append(_lanelink(predlane, succlane, connecting_road))
        return self


class _lanelink:
    """Helper class for `LaneLinker`.

    This class represents a link between a predecessor lane and a
    successor lane, optionally including a connecting road.

    Parameters
    ----------
    predecessor : Lane
        The predecessor lane.
    successor : Lane
        The successor lane.
    connecting_road : int, optional
        The ID of the connecting road (used for junctions).

    Attributes
    ----------
    predecessor : Lane
        The predecessor lane.
    successor : Lane
        The successor lane.
    connecting_road : int or None
        The ID of the connecting road, or None if not provided.
    used : bool
        Indicates whether the link has been used.
    """

    def __init__(
        self,
        predecessor: "Lane",
        successor: "Lane",
        connecting_road: Optional[int],
    ) -> None:
        """Initialize the `_lanelink` object.

        Parameters
        ----------
        predecessor : Lane
            The predecessor lane.
        successor : Lane
            The successor lane.
        connecting_road : int, optional
            The ID of the connecting road (used for junctions).
        """
        self.predecessor = predecessor
        self.successor = successor
        self.connecting_road = connecting_road
        self.used = False


class Connection(XodrBase):
    """Create a connection as a base of a junction in OpenDRIVE.

    Parameters
    ----------
    incoming_road : int
        The ID of the incoming road to the junction.
    connecting_road : int
        The ID of the connecting road (type junction).
    contact_point : ContactPoint
        The contact point of the link.
    id : int, optional
        The ID of the connection (automated). Default is None.

    Attributes
    ----------
    incoming_road : int
        The ID of the incoming road to the junction.
    connecting_road : int
        The ID of the connecting road (type junction).
    contact_point : ContactPoint
        The contact point of the link.
    id : int or None
        The ID of the connection (automated).
    links : list of tuple(int, int)
        A list of all lane links in the connection.

    Methods
    -------
    add_lanelink(in_lane, out_lane)
        Add a lane link to the connection.
    get_attributes(junctiontype=JunctionType.default)
        Return the attributes of the connection as a dictionary.
    get_element(junctiontype=JunctionType.default)
        Return the ElementTree representation of the connection.
    """

    def __init__(
        self,
        incoming_road: int,
        connecting_road: int,
        contact_point: ContactPoint,
        id: Optional[int] = None,
    ) -> None:
        """Initialize the `Connection` object.

        Parameters
        ----------
        incoming_road : int
            The ID of the incoming road to the junction.
        connecting_road : int
            The ID of the connecting road (type junction).
        contact_point : ContactPoint
            The contact point of the link.
        id : int, optional
            The ID of the connection (automated). Default is None.
        """
        super().__init__()
        self.incoming_road = incoming_road
        self.connecting_road = connecting_road
        self.contact_point = enumchecker(contact_point, ContactPoint, True)
        self.id = id
        self.links = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Connection) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.links == other.links
            ):
                return True
        return False

    def _set_id(self, id: int) -> None:
        """Set the ID of the connection.

        Parameters
        ----------
        id : int
            The ID to assign to the connection.
        """
        if self.id == None:
            self.id = id

    def add_lanelink(self, in_lane: int, out_lane: int) -> "Connection":
        """Add a new lane link to the connection.

        Parameters
        ----------
        in_lane : int
            The lane ID of the incoming road.
        out_lane : int
            The lane ID of the outgoing road.

        Returns
        -------
        Connection
            The updated `Connection` object.
        """
        self.links.append((in_lane, out_lane))
        return self

    def get_attributes(
        self, junctiontype: JunctionType = JunctionType.default
    ) -> dict:
        """Return the attributes of the connection as a dictionary.

        Parameters
        ----------
        junctiontype : JunctionType, optional
            The type of junction created (connections will differ).
            Default is `JunctionType.default`.

        Returns
        -------
        dict
            A dictionary containing the attributes of the connection.
        """
        retdict = {}
        retdict["incomingRoad"] = str(self.incoming_road)
        retdict["id"] = str(self.id)
        retdict["contactPoint"] = enum2str(self.contact_point)
        if junctiontype == JunctionType.direct:
            retdict["linkedRoad"] = str(self.connecting_road)
        else:
            retdict["connectingRoad"] = str(self.connecting_road)
        return retdict

    def get_element(
        self, junctiontype: JunctionType = JunctionType.default
    ) -> ET.Element:
        """Return the ElementTree representation of the connection.

        Parameters
        ----------
        junctiontype : JunctionType, optional
            The type of junction created (connections will differ).
            Default is `JunctionType.default`.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the connection.
        """

        element = ET.Element(
            "connection", attrib=self.get_attributes(junctiontype)
        )
        self._add_additional_data_to_element(element)
        for l in sorted(self.links, key=lambda x: x[0], reverse=True):
            ET.SubElement(
                element,
                "laneLink",
                attrib={"from": str(l[0]), "to": str(l[1])},
            )
        return element


class Junction(XodrBase):
    """Create a junction in OpenDRIVE.

    Parameters
    ----------
    name : str
        The name of the junction.
    id : int
        The ID of the junction.
    junction_type : JunctionType, optional
        The type of the junction. Default is `JunctionType.default`.
    orientation : Orientation, optional
        The orientation of the junction (used for virtual junctions).
        Default is None.
    sstart : float, optional
        The start of the virtual junction (used for virtual junctions).
        Default is None.
    send : float, optional
        The end of the virtual junction (used for virtual junctions).
        Default is None.
    mainroad : int, optional
        The main road for a virtual junction. Default is None.

    Attributes
    ----------
    name : str
        The name of the junction.
    id : int
        The ID of the junction.
    connections : list of Connection
        All the connections in the junction.
    junction_type : JunctionType
        The type of the junction.
    orientation : Orientation or None
        The orientation of the junction (used for virtual junctions).
    sstart : float or None
        The start of the virtual junction (used for virtual junctions).
    send : float or None
        The end of the virtual junction (used for virtual junctions).
    mainroad : int or None
        The main road for a virtual junction.

    Methods
    -------
    add_connection(connection)
        Add a connection to the junction.
    get_attributes()
        Return the attributes of the junction as a dictionary.
    get_element()
        Return the ElementTree representation of the junction.
    """

    def __init__(
        self,
        name: str,
        id: int,
        junction_type: JunctionType = JunctionType.default,
        orientation: Optional[Orientation] = None,
        sstart: Optional[float] = None,
        send: Optional[float] = None,
        mainroad: Optional[int] = None,
    ) -> None:
        """Initialize the `Junction` object.

        Parameters
        ----------
        name : str
            The name of the junction.
        id : int
            The ID of the junction.
        junction_type : JunctionType, optional
            The type of the junction. Default is `JunctionType.default`.
        orientation : Orientation, optional
            The orientation of the junction (used for virtual junctions).
            Default is None.
        sstart : float, optional
            The start of the virtual junction (used for virtual junctions).
            Default is None.
        send : float, optional
            The end of the virtual junction (used for virtual junctions).
            Default is None.
        mainroad : int, optional
            The main road for a virtual junction. Default is None.

        Raises
        ------
        NotEnoughInputArguments
            If required parameters for a virtual junction are missing.
        """
        super().__init__()
        self.name = name
        self.id = id
        self.connections = []
        self._id_counter = 0

        self.junction_type = enumchecker(junction_type, JunctionType)
        if junction_type == JunctionType.virtual:
            if not (
                sstart is not None
                and send is not None
                and mainroad is not None
                and orientation is not None
            ):
                raise NotEnoughInputArguments(
                    "For virtual junctions sstart, send, orientation, and mainroad has to be added"
                )
        self.sstart = sstart
        self.send = send
        self.mainroad = mainroad
        self.orientation = enumchecker(orientation, Orientation, True)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Junction) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.connections == other.connections
            ):
                return True
        return False

    def add_connection(self, connection: Connection) -> "Junction":
        """Add a new connection to the junction.

        Parameters
        ----------
        connection : Connection
            The connection to add to the junction.

        Returns
        -------
        Junction
            The updated `Junction` object.

        Raises
        ------
        TypeError
            If `connection` is not of type `Connection`.
        """
        if not isinstance(connection, Connection):
            raise TypeError("connection is not of type Connection")
        connection._set_id(self._id_counter)
        self._id_counter += 1
        self.connections.append(connection)
        return self

    def get_attributes(self) -> dict:
        """Return the attributes of the junction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the junction.
        """
        retdict = {}
        retdict["name"] = self.name
        retdict["id"] = str(self.id)
        retdict["type"] = self.junction_type.name

        # these are only used for virtual junctions
        if self.junction_type == JunctionType.virtual:
            if self.orientation == Orientation.positive:
                retdict["orientation"] = "+"
            elif self.orientation == Orientation.negative:
                retdict["orientation"] = "-"
            retdict["sEnd"] = str(self.send)
            retdict["sStart"] = str(self.sstart)
            retdict["mainRoad"] = str(self.mainroad)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the junction.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the junction.
        """
        element = ET.Element("junction", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        for con in self.connections:
            element.append(con.get_element(self.junction_type))
        return element


# from .exceptions import NotSameAmountOfLanesError
from .enumerations import ContactPoint


def are_roads_consecutive(road1: "Road", road2: "Road") -> bool:
    """Check if `road2` follows `road1`.

    Parameters
    ----------
    road1 : Road
        The first road.
    road2 : Road
        The second road.

    Returns
    -------
    bool
        True if `road2` follows `road1`, False otherwise.
    """

    if road1.successor is not None and road2.predecessor is not None:
        if (
            road1.successor.element_type == ElementType.road
            and road2.predecessor.element_type == ElementType.road
        ):
            if (
                road1.successor.element_id == road2.id
                and road2.predecessor.element_id == road1.id
            ):
                return True

    return False


def are_roads_connected(road1: "Road", road2: "Road") -> tuple[bool, str]:
    """Check if `road1` and `road2` are connected as successor/successor or
    predecessor/predecessor.

    Parameters
    ----------
    road1 : Road
        The first road.
    road2 : Road
        The second road.

    Returns
    -------
    tuple[bool, str]
        A tuple where the first element is a boolean indicating if the
        roads are connected, and the second element is a string
        ("successor" or "predecessor") describing the connection type.
    """
    if road1.successor is not None and road2.successor is not None:
        if (
            road1.successor.element_type == ElementType.road
            and road2.successor.element_type == ElementType.road
        ):
            if (
                road1.successor.element_id == road2.id
                and road2.successor.element_id == road1.id
            ):
                return True, "successor"
    if road1.predecessor is not None and road2.predecessor is not None:
        if (
            road1.predecessor.element_type == ElementType.road
            and road2.predecessor.element_type == ElementType.road
        ):
            if (
                road1.predecessor.element_id == road2.id
                and road2.predecessor.element_id == road1.id
            ):
                return True, "predecessor"
    return False, ""


def create_lane_links_from_ids(
    road1: "Road",
    road2: "Road",
    road1_lane_ids: list[int],
    road2_lane_ids: list[int],
) -> None:
    """Connect lanes of two roads given their corresponding lane IDs.

    NOTE: This function is typically used when the number of lanes at
    the connection of two roads differs or when new lanes with zero
    width exist at the beginning of a road.

    Parameters
    ----------
    road1 : Road
        The first road.
    road2 : Road
        The second road.
    road1_lane_ids : list of int
        List of lane IDs for `road1` (do not include the center lane with ID 0).
    road2_lane_ids : list of int
        List of lane IDs for `road2` (do not include the center lane with ID 0).

    Raises
    ------
    GeneralIssueInputArguments
        If the lengths of `road1_lane_ids` and `road2_lane_ids` differ.
    ValueError
        If the center lane (ID 0) is included in either `road1_lane_ids`
        or `road2_lane_ids`.
    NotImplementedError
        If linking with junction connecting roads is not supported.
    """
    if len(road1_lane_ids) != len(road2_lane_ids):
        raise GeneralIssueInputArguments(
            "Length of the lane ID lists is not the same."
        )

    if (0 in road1_lane_ids) or (0 in road2_lane_ids):
        raise ValueError("The center lane (ID 0) should not be linked.")

    if road1.road_type == -1 and road2.road_type == -1:
        first_linktype, _, first_connecting_lanesec = _get_related_lanesection(
            road1, road2
        )
        (
            second_linktype,
            _,
            second_connecting_lanesec,
        ) = _get_related_lanesection(road2, road1)

        # The road links need to be reciprocal for the lane linking to succeed
        if first_linktype == None or second_linktype == None:
            raise ValueError(
                "Unable to create lane links for road with ID "
                + str(road1.id)
                + " and road with ID "
                + str(road2.id)
                + " due to non reciprocal road successor/predecessor links."
            )

        for i in range(len(road1_lane_ids)):
            if road1_lane_ids[i] > 0:
                road1.lanes.lanesections[first_connecting_lanesec].leftlanes[
                    road1_lane_ids[i] - 1
                ].add_link(first_linktype, road2_lane_ids[i])
            else:
                road1.lanes.lanesections[first_connecting_lanesec].rightlanes[
                    abs(road1_lane_ids[i]) - 1
                ].add_link(first_linktype, road2_lane_ids[i])
            if road2_lane_ids[i] > 0:
                road2.lanes.lanesections[second_connecting_lanesec].leftlanes[
                    road2_lane_ids[i] - 1
                ].add_link(second_linktype, road1_lane_ids[i])
            else:
                road2.lanes.lanesections[second_connecting_lanesec].rightlanes[
                    abs(road2_lane_ids[i]) - 1
                ].add_link(second_linktype, road1_lane_ids[i])
    else:
        raise NotImplementedError(
            "This API currently does not support linking with junction connecting roads."
        )


def create_lane_links(road1: "Road", road2: "Road") -> None:
    """Match lanes of two roads and create lane links if they are
    connected.

    Parameters
    ----------
    road1 : Road
        The first road to be lane linked.
    road2 : Road
        The second road to be lane linked.
    """
    if road1.road_type == -1 and road2.road_type == -1:
        # both are roads
        if are_roads_consecutive(road1, road2):
            _create_links_roads(road1, road2)
        elif are_roads_consecutive(road2, road1):
            _create_links_roads(road2, road1)
        else:
            connected, connectiontype = are_roads_connected(road1, road2)
            if connected:
                _create_links_roads(road1, road2, connectiontype)

    elif road1.road_type != -1:
        _create_links_connecting_road(road1, road2)
    elif road2.road_type != -1:
        _create_links_connecting_road(road2, road1)


def _create_links_connecting_road(connecting: "Road", road: "Road") -> None:
    """Create lane links between a connecting road and a normal road.

    Parameters
    ----------
    connecting : Road
        A road of type connecting road (not -1).
    road : Road
        A road that connects to the connecting road.
    """
    linktype, sign, connecting_lanesec = _get_related_lanesection(
        connecting, road
    )
    _, _, road_lanesection_id = _get_related_lanesection(road, connecting)

    if connecting_lanesec is not None:
        if connecting.lanes.lanesections[connecting_lanesec].leftlanes:
            # do left lanes
            for i in range(
                len(
                    connecting.lanes.lanesections[
                        road_lanesection_id
                    ].leftlanes
                )
            ):
                linkid = (
                    connecting.lanes.lanesections[road_lanesection_id]
                    .leftlanes[i]
                    .lane_id
                    * sign
                )
                if linktype == "predecessor":
                    if str(road.id) in connecting.lane_offset_pred:
                        linkid += int(
                            np.sign(linkid)
                            * abs(connecting.lane_offset_pred[str(road.id)])
                        )
                else:
                    if str(road.id) in connecting.lane_offset_suc:
                        linkid += int(
                            np.sign(linkid)
                            * abs(connecting.lane_offset_suc[str(road.id)])
                        )
                connecting.lanes.lanesections[connecting_lanesec].leftlanes[
                    i
                ].add_link(linktype, linkid)

        if connecting.lanes.lanesections[connecting_lanesec].rightlanes:
            # do right lanes
            for i in range(
                len(
                    connecting.lanes.lanesections[
                        connecting_lanesec
                    ].rightlanes
                )
            ):
                linkid = (
                    connecting.lanes.lanesections[road_lanesection_id]
                    .rightlanes[i]
                    .lane_id
                    * sign
                )
                if linktype == "predecessor":
                    if str(road.id) in connecting.lane_offset_pred:
                        linkid += int(
                            np.sign(linkid)
                            * abs(connecting.lane_offset_pred[str(road.id)])
                        )
                else:
                    if str(road.id) in connecting.lane_offset_suc:
                        linkid += int(
                            np.sign(linkid)
                            * abs(connecting.lane_offset_suc[str(road.id)])
                        )
                connecting.lanes.lanesections[connecting_lanesec].rightlanes[
                    i
                ].add_link(linktype, linkid)


def _get_related_lanesection(
    road: "Road", connected_road: "Road"
) -> tuple[Optional[str], Optional[int], Optional[int]]:
    """Determine the correct lane section to use, the type of link, and
    whether the sign of lanes should be switched between two roads.

    Parameters
    ----------
    road : Road
        The road for which the information is required.
    connected_road : Road
        The road connected to `road`.

    Returns
    -------
    tuple[Optional[str], Optional[int], Optional[int]]
        A tuple containing:
        - linktype (str or None): The type of link ("successor" or "predecessor").
        - sign (int or None): +1 or -1 depending on whether the sign should
          change in the linking.
        - road_lanesection_id (int or None): The lane section ID in the road
          to be used for linking.
    """
    linktype = None
    sign = None
    road_lanesection_id = None

    if road.successor and road.successor.element_id == connected_road.id:
        linktype = "successor"
        if road.successor.contact_point == ContactPoint.start:
            sign = 1
        else:
            sign = -1
        road_lanesection_id = -1
        return linktype, sign, road_lanesection_id

    elif road.predecessor and road.predecessor.element_id == connected_road.id:
        linktype = "predecessor"
        if road.predecessor.contact_point == ContactPoint.start:
            sign = -1
        else:
            sign = 1
        road_lanesection_id = 0
        return linktype, sign, road_lanesection_id

    # treat direct junctions differently
    if (
        road.predecessor
        and connected_road.predecessor
        and road.predecessor.element_type == ElementType.junction
        and connected_road.predecessor.element_type == ElementType.junction
        and road.predecessor.element_id
        == connected_road.predecessor.element_id
    ):
        # predecessor - predecessor connection
        linktype = "predecessor"
        sign = -1
        road_lanesection_id = 0
        return linktype, sign, road_lanesection_id

    elif (
        road.successor
        and connected_road.predecessor
        and road.successor.element_type == ElementType.junction
        and connected_road.predecessor.element_type == ElementType.junction
        and road.successor.element_id == connected_road.predecessor.element_id
    ):
        # successor - predecessor connection
        linktype = "successor"
        sign = 1
        road_lanesection_id = -1
        return linktype, sign, road_lanesection_id

    elif (
        road.successor
        and connected_road.successor
        and road.successor.element_type == ElementType.junction
        and connected_road.successor.element_type == ElementType.junction
        and road.successor.element_id == connected_road.successor.element_id
    ):
        # successor - successor connection
        linktype = "successor"
        sign = -1
        road_lanesection_id = -1
        return linktype, sign, road_lanesection_id

    elif (
        road.predecessor
        and connected_road.successor
        and road.predecessor.element_type == ElementType.junction
        and connected_road.successor.element_type == ElementType.junction
        and road.predecessor.element_id == connected_road.successor.element_id
    ):
        # predecessor - successor connection
        linktype = "predecessor"
        sign = 1
        road_lanesection_id = 0
        return linktype, sign, road_lanesection_id

    if connected_road.road_type != -1:
        # treat connecting road in junction differently
        if (
            connected_road.predecessor
            and connected_road.predecessor.element_id == road.id
        ):
            if connected_road.predecessor.contact_point == ContactPoint.start:
                road_lanesection_id = 0
                sign = -1
            else:
                road_lanesection_id = -1
                sign = 1
        elif (
            connected_road.successor
            and connected_road.successor.element_id == road.id
        ):
            if connected_road.successor.contact_point == ContactPoint.start:
                road_lanesection_id = 0
                sign = 1
            else:
                road_lanesection_id = -1
                sign = -1

    return linktype, sign, road_lanesection_id


def _create_links_roads(
    pre_road: "Road", suc_road: "Road", same_type: str = ""
) -> None:
    """Connect the lanes of two roads with links if they have the same
    number of lanes.

    Parameters
    ----------
    pre_road : Road
        The predecessor road.
    suc_road : Road
        The successor road.
    same_type : str, optional
        Specifies the type of connection ("predecessor" or "successor").
        Default is an empty string, which indicates a general connection.

    Raises
    ------
    NotSameAmountOfLanesError
        If the number of lanes in the predecessor and successor roads
        does not match.
    """
    if same_type != "":
        if same_type == "successor":
            lane_sec_pos = -1
        else:
            lane_sec_pos = 0

        if len(pre_road.lanes.lanesections[lane_sec_pos].leftlanes) == len(
            suc_road.lanes.lanesections[lane_sec_pos].rightlanes
        ):
            for i in range(
                len(pre_road.lanes.lanesections[lane_sec_pos].leftlanes)
            ):
                linkid = (
                    pre_road.lanes.lanesections[lane_sec_pos]
                    .leftlanes[i]
                    .lane_id
                )
                pre_road.lanes.lanesections[lane_sec_pos].leftlanes[
                    i
                ].add_link(same_type, linkid * -1)
                suc_road.lanes.lanesections[lane_sec_pos].rightlanes[
                    i
                ].add_link(same_type, linkid)
        else:
            raise NotSameAmountOfLanesError(
                "Road "
                + str(pre_road.id)
                + " and road "
                + str(suc_road.id)
                + " does not have the same number of right and left lanes, to connect as "
                + same_type
                + "/"
                + same_type
            )

        if len(pre_road.lanes.lanesections[lane_sec_pos].rightlanes) == len(
            suc_road.lanes.lanesections[-1].leftlanes
        ):
            for i in range(
                len(pre_road.lanes.lanesections[lane_sec_pos].rightlanes)
            ):
                linkid = (
                    pre_road.lanes.lanesections[lane_sec_pos]
                    .rightlanes[i]
                    .lane_id
                )
                pre_road.lanes.lanesections[lane_sec_pos].rightlanes[
                    i
                ].add_link(same_type, linkid * -1)
                suc_road.lanes.lanesections[lane_sec_pos].leftlanes[
                    i
                ].add_link(same_type, linkid)
        else:
            raise NotSameAmountOfLanesError(
                "Road "
                + str(pre_road.id)
                + " and road "
                + str(suc_road.id)
                + " does not have the same number of right and left lanes, to connect as "
                + same_type
                + "/"
                + same_type
            )

    else:
        (
            pre_linktype,
            pre_sign,
            pre_connecting_lanesec,
        ) = _get_related_lanesection(pre_road, suc_road)
        suc_linktype, _, suc_connecting_lanesec = _get_related_lanesection(
            suc_road, pre_road
        )
        if len(
            pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes
        ) == len(
            suc_road.lanes.lanesections[suc_connecting_lanesec].leftlanes
        ):
            for i in range(
                len(
                    pre_road.lanes.lanesections[
                        pre_connecting_lanesec
                    ].leftlanes
                )
            ):
                linkid = (
                    pre_road.lanes.lanesections[pre_connecting_lanesec]
                    .leftlanes[i]
                    .lane_id
                    * pre_sign
                )
                pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes[
                    i
                ].add_link(pre_linktype, linkid)
                suc_road.lanes.lanesections[suc_connecting_lanesec].leftlanes[
                    i
                ].add_link(suc_linktype, linkid * pre_sign)
        else:
            raise NotSameAmountOfLanesError(
                "Road "
                + str(pre_road.id)
                + " and road "
                + str(suc_road.id)
                + " does not have the same number of right lanes."
            )

        if len(
            pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes
        ) == len(
            suc_road.lanes.lanesections[suc_connecting_lanesec].rightlanes
        ):
            for i in range(
                len(
                    pre_road.lanes.lanesections[
                        pre_connecting_lanesec
                    ].rightlanes
                )
            ):
                linkid = (
                    pre_road.lanes.lanesections[pre_connecting_lanesec]
                    .rightlanes[i]
                    .lane_id
                )
                pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes[
                    i
                ].add_link(pre_linktype, linkid)
                suc_road.lanes.lanesections[suc_connecting_lanesec].rightlanes[
                    i
                ].add_link(suc_linktype, linkid)
        else:
            raise NotSameAmountOfLanesError(
                "Road "
                + str(pre_road.id)
                + " and road "
                + str(suc_road.id)
                + " does not have the same number of right lanes."
            )


class JunctionGroup(XodrBase):
    """Create a JunctionGroup in OpenDRIVE.

    Parameters
    ----------
    name : str
        The name of the junction group.
    group_id : int
        The ID of the junction group.
    junction_type : JunctionGroupType, optional
        The type of the junction group.
        Default is `JunctionGroupType.roundabout`.

    Attributes
    ----------
    name : str
        The name of the junction group.
    group_id : int
        The ID of the junction group.
    junctions : list of int
        All the junctions in the junction group.
    junction_type : JunctionGroupType
        The type of the junction group.

    Methods
    -------
    add_junction(junction_id)
        Add a junction to the junction group.
    get_attributes()
        Return the attributes of the junction group as a dictionary.
    get_element()
        Return the ElementTree representation of the junction group.
    """

    def __init__(
        self,
        name: str,
        group_id: int,
        junction_type: JunctionGroupType = JunctionGroupType.roundabout,
    ) -> None:
        """Initialize the JunctionGroup.

        Parameters
        ----------
        name : str
            The name of the junction group.
        group_id : int
            The ID of the junction group.
        junction_type : JunctionGroupType, optional
            The type of the junction group.
            Default is `JunctionGroupType.roundabout`.
        """
        super().__init__()
        self.name = name
        self.group_id = group_id
        self.junctions = []
        self.junction_type = enumchecker(junction_type, JunctionGroupType)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, JunctionGroup) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.junctions == other.junctions
            ):
                return True
        return False

    def add_junction(self, junction_id: int) -> "JunctionGroup":
        """Add a new junction to the JunctionGroup.

        Parameters
        ----------
        junction_id : int
            The ID of the junction to add.

        Returns
        -------
        JunctionGroup
            The updated JunctionGroup object.
        """
        self.junctions.append(junction_id)
        return self

    def get_attributes(self) -> dict:
        """Return the attributes of the JunctionGroup as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the JunctionGroup.
        """
        retdict = {}
        retdict["name"] = self.name
        retdict["id"] = str(self.group_id)
        retdict["type"] = enum2str(self.junction_type)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the JunctionGroup.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the JunctionGroup.
        """
        element = ET.Element("junctionGroup", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        for j in self.junctions:
            ET.SubElement(
                element, "junctionReference", attrib={"junction": str(j)}
            )
        return element
