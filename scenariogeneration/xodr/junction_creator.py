"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

from typing import Optional, Union

import numpy as np
import pyclothoids as pcloth

from .enumerations import ContactPoint, ElementType, JunctionType
from .exceptions import (
    MixingDrivingDirection,
    NotEnoughInputArguments,
    NotSameAmountOfLanesError,
    UndefinedRoadNetwork,
)
from .generators import (
    LaneDef,
    _create_junction_links,
    _get_related_lanesection,
    create_road,
)
from .geometry import Line, Spiral
from .links import Connection, Junction

STD_START_CLOTH = 1 / 1000000000


class CommonJunctionCreator:
    """CommonJunctionCreator is a helper class to create custom common
    junctions.

    Parameters
    ----------
    id : int
        The ID of the junction.
    name : str
        Name of the junction.
    startnum : int, optional
        The starting ID of this junction's roads. Default is 100.

    Attributes
    ----------
    id : int
        The ID of the junction.
    startnum : int
        The starting ID of this junction's roads.
    incoming_roads : list of Road
        All incoming roads for the junction.
    junction_roads : list of Road
        All generated connecting roads.
    junction : Junction
        The junction xodr element for the junction.

    Methods
    -------
    add_incoming_road_circular_geometry(road, radius, angle,
    road_connection)
        Adds a road on a circle defining the junction geometry.
        Note: Cannot be used together with
        `add_incoming_road_cartesian_geometry`.
    add_incoming_road_cartesian_geometry(road, x, y, heading,
    road_connection)
        Adds a road on a generic x, y, heading geometry.
        Note: Cannot be used together with
        `add_incoming_road_circular_geometry`.
    add_connection(first_road_id, second_road_id, first_lane_id,
    second_lane_id)
        Adds a connection between two roads.
    """

    def __init__(self, id: int, name: str, startnum: int = 100) -> None:
        """Initialize the `CommonJunctionCreator` instance.

        Parameters
        ----------
        id : int
            The ID of the junction.
        name : str
            Name of the junction.
        startnum : int, optional
            The starting ID of this junction's roads. Default is 100.

        Returns
        -------
        None
        """
        self.id = id
        self.incoming_roads = []
        self._radie = []
        self._angles = []
        self._x = []
        self._y = []
        self._h = []
        self.junction_roads = []
        self._number_of_left_lanes = []
        self._number_of_right_lanes = []
        self.startnum = startnum
        self.junction = Junction(name, id, junction_type=JunctionType.default)
        self._circular_junction = False
        self._generic_junction = False
        self._height = None

    def add_incoming_road_circular_geometry(
        self,
        road: "Road",
        radius: float,
        angle: float,
        road_connection: Optional[str] = None,
    ) -> None:
        """Add an incoming road to a junction, assuming a circular geometry.

        This method places all roads on a circle based on the specified
        radius and angle. The radius can vary for different incoming roads,
        but the origin remains the same.

        Note
        ----
        This method cannot be used together with
        `add_incoming_road_cartesian_geometry`.

        Parameters
        ----------
        road : Road
            The incoming road.
        radius : float
            The radius at which to place the road.
        angle : float
            The angle at which to place the road.
        road_connection : str, optional
            Specifies how the incoming road connects to the junction
            ('predecessor' or 'successor'). Default is None.

        Returns
        -------
        None
        """
        self.incoming_roads.append(road)
        self._handle_connection_input(road, road_connection)
        self._radie.append(radius)
        self._angles.append(angle)
        self._circular_junction = True

    def add_incoming_road_cartesian_geometry(
        self,
        road: "Road",
        x: float,
        y: float,
        heading: float,
        road_connection: Optional[str] = None,
    ) -> None:
        """Add an incoming road to a junction, assuming a Cartesian geometry.

        This method places roads based on a local coordinate system
        defined by x, y, and heading.

        Note
        ----
        This method cannot be used together with
        `add_incoming_road_circular_geometry`.

        Parameters
        ----------
        road : Road
            The incoming road.
        x : float
            The local x-position of the road.
        y : float
            The local y-position of the road.
        heading : float
            The local heading of the road (pointing into the junction).
        road_connection : str, optional
            Specifies how the incoming road connects to the junction
            ('predecessor' or 'successor'). Default is None.

        Returns
        -------
        None
        """
        self.incoming_roads.append(road)
        self._handle_connection_input(road, road_connection)

        self._x.append(x)
        self._y.append(y)
        self._h.append(heading)
        self._generic_junction = True

    def add_constant_elevation(self, height: float) -> None:
        """Add a constant elevation to all connecting roads.

        This method sets both the elevation profile and a zero superelevation
        for all connecting roads in the junction.

        Parameters
        ----------
        height : float
            The height of the junction and all roads.

        Returns
        -------
        None
        """
        self._height = height
        for r in self.junction_roads:
            r.add_elevation(0, self._height, 0, 0, 0)

    def _get_minimum_lanes_to_connect(
        self, incoming_road: "Road", linked_road: "Road"
    ) -> tuple[list[int], list[int]]:
        """Determine the minimum number of lanes to connect between two roads.

        This method calculates the lane IDs for both incoming and linked
        roads based on their lane sections and driving directions.

        Parameters
        ----------
        incoming_road : Road
            The incoming road to the junction.
        linked_road : Road
            The linked road to the junction.

        Returns
        -------
        tuple of (list of int, list of int)
            A tuple containing:
            - incoming_lane_ids : list of int
                Lane IDs for the incoming road.
            - linked_lane_ids : list of int
                Lane IDs for the linked road.
        """
        (
            incoming_connection,
            incoming_sign,
            incoming_lane_section,
        ) = _get_related_lanesection(incoming_road, linked_road)
        (
            linked_connection,
            sign,
            linked_lane_section,
        ) = _get_related_lanesection(linked_road, incoming_road)

        incoming_left_lanes = len(
            incoming_road.lanes.lanesections[incoming_lane_section].leftlanes
        )
        incoming_right_lanes = len(
            incoming_road.lanes.lanesections[incoming_lane_section].rightlanes
        )
        linked_left_lanes = len(
            linked_road.lanes.lanesections[linked_lane_section].leftlanes
        )
        linked_right_lanes = len(
            linked_road.lanes.lanesections[linked_lane_section].rightlanes
        )
        _incoming_lane_ids = []
        _linked_lane_ids = []

        if sign > 0:
            _incoming_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_left_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )
            _linked_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_left_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )

            _incoming_lane_ids.extend(
                [
                    -x
                    for x in range(
                        1, min(incoming_right_lanes, linked_right_lanes) + 1, 1
                    )
                ]
            )
            _linked_lane_ids.extend(
                [
                    -x
                    for x in range(
                        1, min(incoming_right_lanes, linked_right_lanes) + 1, 1
                    )
                ]
            )

        elif sign < 0:
            _incoming_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_left_lanes, linked_right_lanes) + 1, 1
                    )
                ]
            )
            _linked_lane_ids.extend(
                [
                    -x
                    for x in range(
                        1, min(incoming_left_lanes, linked_right_lanes) + 1, 1
                    )
                ]
            )

            _incoming_lane_ids.extend(
                [
                    -x
                    for x in range(
                        1, min(incoming_right_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )
            _linked_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_right_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )
        return _incoming_lane_ids, _linked_lane_ids

    def add_connection(
        self,
        road_one_id: int,
        road_two_id: int,
        lane_one_id: Optional[Union[int, list[int]]] = None,
        lane_two_id: Optional[Union[int, list[int]]] = None,
    ) -> None:
        """Add a connection between two roads.

        This method generates connecting roads between two specified
        roads using either lane IDs or automatically determines the
        lanes to connect if no lane IDs are provided.

        Parameters
        ----------
        first_road_id : int
            The ID of the first road to connect.
        second_road_id : int
            The ID of the second road to connect.
        first_lane_id : int or list of int, optional
            The lane ID(s) on the first road to connect. Default is None.
        second_lane_id : int or list of int, optional
            The lane ID(s) on the second road to connect. Default is None.

        Raises
        ------
        NotEnoughInputArguments
            If lane input is used, both `first_lane_id` and `second_lane_id`
            must be provided.

        Returns
        -------
        None
        """
        if lane_one_id is None and lane_two_id is None:
            # check if the connection is symetric (same number of lanes on both sides)
            if (
                self._number_of_left_lanes[self._get_list_index(road_one_id)]
                == self._number_of_right_lanes[
                    self._get_list_index(road_one_id)
                ]
                and self._number_of_left_lanes[
                    self._get_list_index(road_two_id)
                ]
                == self._number_of_right_lanes[
                    self._get_list_index(road_two_id)
                ]
                and self._number_of_left_lanes[
                    self._get_list_index(road_one_id)
                ]
                == self._number_of_right_lanes[
                    self._get_list_index(road_two_id)
                ]
            ):
                self._create_connecting_roads_with_equal_lanes(
                    road_one_id, road_two_id
                )
            else:
                self._create_connecting_roads_unequal_lanes(
                    road_one_id, road_two_id
                )
        elif lane_one_id is not None and lane_two_id is not None:
            if isinstance(lane_one_id, list):
                for i in range(len(lane_one_id)):
                    self._create_connecting_road_with_lane_input(
                        road_one_id,
                        road_two_id,
                        lane_one_id[i],
                        lane_two_id[i],
                    )
            else:
                self._create_connecting_road_with_lane_input(
                    road_one_id, road_two_id, lane_one_id, lane_two_id
                )
        else:
            raise NotEnoughInputArguments(
                "if lane input is used, both has to be provided"
            )

    def _handle_connection_input(
        self, road: "Road", road_connection: Optional[str]
    ) -> None:
        """Validate and process the connection input for an incoming road.

        This method checks if the provided road connection type is valid
        and ensures the road is properly connected to the junction.

        Parameters
        ----------
        road : Road
            The incoming road.
        road_connection : str, optional
            The connection type ('predecessor' or 'successor').
            Default is None.

        Raises
        ------
        ValueError
            If `road_connection` is not 'predecessor' or 'successor'.
        UndefinedRoadNetwork
            If the road is not connected to the junction.

        Returns
        -------
        None
        """
        # if isinstance(road.planview, AdjustablePlanview):
        if road_connection is not None:
            if road_connection == "successor":
                road.add_successor(ElementType.junction, self.id)
            elif road_connection == "predecessor":
                road.add_predecessor(ElementType.junction, self.id)
            else:
                raise ValueError(
                    "road_connection can only be of the values 'successor', or 'predecessor'. Not "
                    + road_connection
                )
        else:
            if not (
                (road.successor and road.successor.element_id == self.id)
                or (
                    road.predecessor and road.predecessor.element_id == self.id
                )
            ):
                raise UndefinedRoadNetwork(
                    "road : "
                    + str(road.id)
                    + " is not connected to junction: "
                    + str(self.id)
                )
        if road.successor and road.successor.element_id == self.id:
            self._number_of_left_lanes.append(
                len(road.lanes.lanesections[-1].leftlanes)
            )
            self._number_of_right_lanes.append(
                len(road.lanes.lanesections[-1].rightlanes)
            )
        elif road.predecessor and road.predecessor.element_id == self.id:
            self._number_of_left_lanes.append(
                len(road.lanes.lanesections[0].leftlanes)
            )
            self._number_of_right_lanes.append(
                len(road.lanes.lanesections[0].rightlanes)
            )

    def _get_list_index(self, id: int) -> int:
        """Get the index of a road in the incoming roads list based on its ID.

        Parameters
        ----------
        id : int
            The ID of the road.

        Returns
        -------
        int
            The index of the road in the incoming roads list.

        Raises
        ------
        ValueError
            If the road ID is not found in the incoming roads list.
        """
        for i in range(len(self.incoming_roads)):
            if self.incoming_roads[i].id == id:
                return i

    def _set_offset_for_incoming_road(
        self, road_idx: int, connecting_road_id: int, offset: int
    ) -> None:
        """Set the lane offset for an incoming road connected to the junction.

        This method updates the lane offset for the incoming road based on
        whether it is a predecessor or successor of the connecting road.

        Parameters
        ----------
        road_idx : int
            The index of the incoming road in the list.
        connecting_road_id : int
            The ID of the connecting road.
        offset : int
            The lane offset to set.

        Returns
        -------
        None
        """

        if self._get_connection_type(road_idx) == "successor":
            self.incoming_roads[road_idx].lane_offset_suc[
                str(connecting_road_id)
            ] = offset
        else:
            self.incoming_roads[road_idx].lane_offset_pred[
                str(connecting_road_id)
            ] = offset

    def _get_contact_point_connecting_road(self, road_id: int) -> ContactPoint:
        """Get the contact point for a connecting road.

        This method determines whether the connecting road is a
        predecessor or successor of the junction.

        Parameters
        ----------
        road_id : int
            The ID of the incoming road.

        Returns
        -------
        ContactPoint
            The contact point
            (`ContactPoint.start` or `ContactPoint.end`).

        Raises
        ------
        AttributeError
            If the road is not connected to the junction.
        """
        incoming_road = self.incoming_roads[self._get_list_index(road_id)]
        if (
            incoming_road.successor
            and incoming_road.successor.element_id == self.id
        ):
            return ContactPoint.end
        elif (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            return ContactPoint.start
        else:
            raise AttributeError(
                "road : "
                + str(road_id)
                + " is not connected to junction: "
                + str(self.id)
            )

    def _get_connecting_lane_section(self, idx: int) -> int:
        """Get the lane section index for a road connected to the junction.

        This method determines whether the road is a predecessor or
        successor of the junction and returns the corresponding lane
        section index.

        Parameters
        ----------
        idx : int
            The index of the road in the incoming roads list.

        Returns
        -------
        int
            The lane section index
            (`0` for predecessor, `-1` for successor).

        Raises
        ------
        AttributeError
            If the road is not connected to the junction.
        """
        incoming_road = self.incoming_roads[idx]
        if (
            incoming_road.successor
            and incoming_road.successor.element_id == self.id
        ):
            return -1
        elif (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            return 0
        else:
            raise AttributeError(
                "road : "
                + str(incoming_road.id)
                + " is not connected to junction: "
                + str(self.id)
            )

    def _create_connecting_roads_unequal_lanes(
        self, road_one_id: int, road_two_id: int
    ) -> None:
        """Create connecting roads between two roads with unequal lane counts.

        This method connects two roads that have different numbers of
        lanes entering the junction. It only connects lanes that are
        common between the two roads.

        Parameters
        ----------
        road_one_id : int
            The ID of the first road.
        road_two_id : int
            The ID of the second road.

        Returns
        -------
        None
        """
        idx1 = self._get_list_index(road_one_id)
        idx2 = self._get_list_index(road_two_id)

        # check if the road has _angles/radius for these roads
        if self._circular_junction:
            roadgeoms = self._create_geometry_from_circular(idx1, idx2)
        elif self._generic_junction:
            roadgeoms = self._create_geometry_from_carthesian(idx1, idx2)
        first_road_lane_ids, _ = self._get_minimum_lanes_to_connect(
            self.incoming_roads[idx1], self.incoming_roads[idx2]
        )

        left_lane_defs, right_lane_defs = self._get_lane_defs(
            idx1, idx2, sum([x.length for x in roadgeoms]), True
        )

        tmp_junc_road = create_road(
            roadgeoms,
            self.startnum,
            left_lanes=left_lane_defs,
            right_lanes=right_lane_defs,
            lane_width=3,
            road_type=self.id,
        )
        if self._height is not None:
            tmp_junc_road.add_elevation(0, self._height, 0, 0, 0)
            tmp_junc_road.add_superelevation(0, 0, 0, 0, 0)
        tmp_junc_road.add_predecessor(
            ElementType.road,
            road_one_id,
            contact_point=self._get_contact_point_connecting_road(road_one_id),
        )
        tmp_junc_road.add_successor(
            ElementType.road,
            road_two_id,
            contact_point=self._get_contact_point_connecting_road(road_two_id),
        )

        (
            first_road_lane_ids,
            connecting_road_lane_ids,
        ) = self._get_minimum_lanes_to_connect(
            self.incoming_roads[idx1], tmp_junc_road
        )
        connection = Connection(
            road_one_id, tmp_junc_road.id, ContactPoint.start
        )
        for i in range(len(first_road_lane_ids)):
            connection.add_lanelink(
                first_road_lane_ids[i], connecting_road_lane_ids[i]
            )
        self.junction.add_connection(connection)

        (
            second_road_lane_ids,
            connecting_road_lane_ids,
        ) = self._get_minimum_lanes_to_connect(
            self.incoming_roads[idx2], tmp_junc_road
        )
        connection = Connection(
            tmp_junc_road.successor.element_id,
            tmp_junc_road.id,
            ContactPoint.end,
        )
        for i in range(len(second_road_lane_ids)):
            connection.add_lanelink(
                second_road_lane_ids[i], connecting_road_lane_ids[i]
            )
        self.junction.add_connection(connection)

        self.junction_roads.append(tmp_junc_road)
        self.startnum += 1

    def _get_lane_defs(
        self,
        idx1: int,
        idx2: int,
        connecting_road_length: float,
        allow_empty_lane: bool = False,
    ) -> tuple[LaneDef, LaneDef]:
        """Generate lane definitions for connecting roads.

        This method calculates the lane definitions for left and right
        lanes based on the geometry and lane widths of the incoming roads.

        Parameters
        ----------
        idx1 : int
            The index of the first road in the incoming roads list.
        idx2 : int
            The index of the second road in the incoming roads list.
        connecting_road_length : float
            The length of the connecting road.
        allow_empty_lane : bool, optional
            Whether to allow empty lanes if the lane counts differ.
            Default is False.

        Returns
        -------
        tuple of (LaneDef, LaneDef)
            A tuple containing:
            - left_lane_defs : LaneDef
                Lane definitions for the left lanes.
            - right_lane_defs : LaneDef
                Lane definitions for the right lanes.
        """

        def _get_lane_widths(idx: int, l_or_r: str) -> list[float]:
            """Get lane widths for a specific side (left or right) of a road.

            This method retrieves the widths of lanes on the specified
            side of the road based on its lane section.

            Parameters
            ----------
            idx : int
                The index of the road in the incoming roads list.
            side : str
                The side of the road ('left' or 'right').

            Returns
            -------
            list of float
                A list of lane widths for the specified side.
            """
            connected_lane_section = self._get_connecting_lane_section(idx)
            lane_widths = []
            if l_or_r == "left":
                lanes = (
                    self.incoming_roads[idx]
                    .lanes.lanesections[connected_lane_section]
                    .leftlanes
                )
            elif l_or_r == "right":
                lanes = (
                    self.incoming_roads[idx]
                    .lanes.lanesections[connected_lane_section]
                    .rightlanes
                )
            for ll in lanes:
                if connected_lane_section == 0:
                    lane_widths.append(ll.get_width(0))
                else:
                    lane_widths.append(
                        ll.get_width(
                            self.incoming_roads[
                                idx
                            ].planview.get_total_length()
                            - self.incoming_roads[idx]
                            .lanes.lanesections[connected_lane_section]
                            .s
                        )
                    )
            return lane_widths

        incomming_connected_lane_section = self._get_connecting_lane_section(
            idx1
        )
        outgoing_connected_lane_section = self._get_connecting_lane_section(
            idx2
        )

        if incomming_connected_lane_section == -1:
            n_l_lanes = len(
                self.incoming_roads[idx1]
                .lanes.lanesections[incomming_connected_lane_section]
                .leftlanes
            )
            n_r_lanes = len(
                self.incoming_roads[idx1]
                .lanes.lanesections[incomming_connected_lane_section]
                .rightlanes
            )

            left_start_widths = _get_lane_widths(idx1, "left")
            right_start_widths = _get_lane_widths(idx1, "right")
        elif incomming_connected_lane_section == 0:
            n_r_lanes = len(
                self.incoming_roads[idx1]
                .lanes.lanesections[incomming_connected_lane_section]
                .leftlanes
            )
            n_l_lanes = len(
                self.incoming_roads[idx1]
                .lanes.lanesections[incomming_connected_lane_section]
                .rightlanes
            )

            left_start_widths = _get_lane_widths(idx1, "right")
            right_start_widths = _get_lane_widths(idx1, "left")

        if outgoing_connected_lane_section == -1:
            left_end_widths = _get_lane_widths(idx2, "right")
            right_end_widths = _get_lane_widths(idx2, "left")
        elif outgoing_connected_lane_section == 0:
            left_end_widths = _get_lane_widths(idx2, "left")
            right_end_widths = _get_lane_widths(idx2, "right")

        left_lanes = 0
        if len(left_start_widths) == len(left_end_widths):
            left_lanes = LaneDef(
                0,
                connecting_road_length,
                n_l_lanes,
                n_l_lanes,
                None,
                left_start_widths,
                left_end_widths,
            )
        elif allow_empty_lane:
            num_lanes_to_connect = min(
                len(left_start_widths), len(left_end_widths)
            )
            left_lanes = LaneDef(
                0,
                connecting_road_length,
                num_lanes_to_connect,
                num_lanes_to_connect,
                None,
                left_start_widths[0:num_lanes_to_connect],
                left_end_widths[0:num_lanes_to_connect],
            )

        right_lanes = 0
        if (len(right_start_widths)) == (len(right_end_widths)):
            right_lanes = LaneDef(
                0,
                connecting_road_length,
                n_r_lanes,
                n_r_lanes,
                None,
                right_start_widths,
                right_end_widths,
            )
        elif allow_empty_lane:
            num_lanes_to_connect = min(
                len(right_start_widths), len(right_end_widths)
            )
            right_lanes = LaneDef(
                0,
                connecting_road_length,
                num_lanes_to_connect,
                num_lanes_to_connect,
                None,
                right_start_widths[0:num_lanes_to_connect],
                right_end_widths[0:num_lanes_to_connect],
            )
        return left_lanes, right_lanes

    def _create_connecting_roads_with_equal_lanes(
        self, road_one_id: int, road_two_id: int
    ) -> None:
        """Create connecting roads between two roads with equal lane counts.

        This method connects two roads that have the same number of left
        and right lanes entering the junction.

        Parameters
        ----------
        road_one_id : int
            The ID of the first road.
        road_two_id : int
            The ID of the second road.

        Returns
        -------
        None
        """
        idx1 = self._get_list_index(road_one_id)
        idx2 = self._get_list_index(road_two_id)

        # check if the road has _angles/radius for these roads
        if self._circular_junction:
            roadgeoms = self._create_geometry_from_circular(idx1, idx2)
        elif self._generic_junction:
            roadgeoms = self._create_geometry_from_carthesian(idx1, idx2)

        left_lane_defs, right_lane_defs = self._get_lane_defs(
            idx1, idx2, sum([x.length for x in roadgeoms])
        )

        tmp_junc_road = create_road(
            roadgeoms,
            self.startnum,
            left_lanes=left_lane_defs,
            right_lanes=right_lane_defs,
            lane_width=1,
            road_type=self.id,
        )
        if self._height is not None:
            tmp_junc_road.add_elevation(0, self._height, 0, 0, 0)
            tmp_junc_road.add_superelevation(0, 0, 0, 0, 0)
        tmp_junc_road.add_predecessor(
            ElementType.road,
            road_one_id,
            contact_point=self._get_contact_point_connecting_road(road_one_id),
        )
        tmp_junc_road.add_successor(
            ElementType.road,
            road_two_id,
            contact_point=self._get_contact_point_connecting_road(road_two_id),
        )
        self._add_connection_full(tmp_junc_road)
        self.junction_roads.append(tmp_junc_road)
        self.startnum += 1

    def _get_connection_type(self, road_idx: int) -> str:
        """Determine the connection type for a road in the junction.

        This method checks whether the road is a predecessor or successor
        of the junction.

        Parameters
        ----------
        road_idx : int
            The index of the road in the incoming roads list.

        Returns
        -------
        str
            The connection type ('predecessor' or 'successor').
        """
        if (
            self.incoming_roads[road_idx].successor
            and self.incoming_roads[road_idx].successor.element_id == self.id
        ):
            return "successor"
        else:
            return "predecessor"

    def _get_lane_width(self, lane_id: int, road_idx: int) -> float:
        """Get the width of a specific lane on a road.

        This method retrieves the width of the specified lane based on its
        lane ID and the road index in the incoming roads list.

        Parameters
        ----------
        lane_id : int
            The ID of the lane
            (positive for left lanes, negative for right lanes).
        road_idx : int
            The index of the road in the incoming roads list.

        Returns
        -------
        float
            The width of the specified lane.
        """
        if np.sign(lane_id) == -1:
            start_width = (
                self.incoming_roads[road_idx]
                .lanes.lanesections[
                    self._get_connecting_lane_section(road_idx)
                ]
                .rightlanes[abs(lane_id) - 1]
                .get_width(0)
            )
        else:
            start_width = (
                self.incoming_roads[road_idx]
                .lanes.lanesections[
                    self._get_connecting_lane_section(road_idx)
                ]
                .leftlanes[abs(lane_id) - 1]
                .get_width(0)
            )
        return start_width

    def _create_connecting_road_with_lane_input(
        self,
        road_one_id: int,
        road_two_id: int,
        lane_one_id: int,
        lane_two_id: int,
    ) -> None:
        """Create a connecting road between two roads with specified lane
        inputs.

        This method connects two roads using the specified lane IDs and
        creates an appropriate geometry for the connecting road based on
        the start and end lane widths.

        Parameters
        ----------
        road_one_id : int
            The ID of the first road to connect.
        road_two_id : int
            The ID of the second road to connect.
        lane_one_id : int
            The lane ID on the first road to connect.
        lane_two_id : int
            The lane ID on the second road to connect.

        Raises
        ------
        MixingDrivingDirection
            If the driving direction is inconsistent between the two
            roads.

        Returns
        -------
        None
        """

        idx1 = self._get_list_index(road_one_id)
        idx2 = self._get_list_index(road_two_id)

        start_offset = 0.0
        end_offset = 0.0
        if (
            self._get_connection_type(idx2) == self._get_connection_type(idx1)
            and np.sign(lane_one_id) == np.sign(lane_two_id)
        ) or (
            self._get_connection_type(idx2) != self._get_connection_type(idx1)
            and np.sign(lane_one_id) != np.sign(lane_two_id)
        ):
            raise MixingDrivingDirection(
                "driving direction not consistent when trying to make connection between roads:"
                + str(road_one_id)
                + " and "
                + str(road_two_id)
            )
        if np.sign(lane_one_id) == -1:
            for lane_iter in range((np.sign(lane_one_id) * lane_one_id) - 1):
                start_offset += (
                    self.incoming_roads[idx1]
                    .lanes.lanesections[
                        self._get_connecting_lane_section(idx1)
                    ]
                    .rightlanes[lane_iter]
                    .get_width(0)
                )
        else:
            for lane_iter in range((np.sign(lane_one_id) * lane_one_id) - 1):
                start_offset += (
                    self.incoming_roads[idx1]
                    .lanes.lanesections[
                        self._get_connecting_lane_section(idx1)
                    ]
                    .leftlanes[lane_iter]
                    .get_width(0)
                )

        if np.sign(lane_two_id) == -1:
            for lane_iter in range((np.sign(lane_two_id) * lane_two_id) - 1):
                end_offset += (
                    self.incoming_roads[idx2]
                    .lanes.lanesections[
                        self._get_connecting_lane_section(idx2)
                    ]
                    .rightlanes[lane_iter]
                    .get_width(0)
                )
        else:
            for lane_iter in range((np.sign(lane_two_id) * lane_two_id) - 1):
                end_offset += (
                    self.incoming_roads[idx2]
                    .lanes.lanesections[
                        self._get_connecting_lane_section(idx2)
                    ]
                    .leftlanes[lane_iter]
                    .get_width(0)
                )

        start_width = self._get_lane_width(lane_one_id, idx1)

        end_width = self._get_lane_width(lane_two_id, idx2)

        if self._get_connection_type(idx1) == "successor":
            angle_offset_start = np.sign(lane_one_id) * np.pi / 2
        else:
            angle_offset_start = -np.sign(lane_one_id) * np.pi / 2
        if self._get_connection_type(idx2) == "successor":
            angle_offset_end = -np.sign(lane_two_id) * np.pi / 2
        else:
            angle_offset_end = np.sign(lane_two_id) * np.pi / 2

        if self._circular_junction:
            an1 = self._angles[idx2] - self._angles[idx1] - np.pi
            # adjust angle if multiple of pi
            if an1 > np.pi:
                an1 = -(2 * np.pi - an1)
            start_x = -self._radie[idx1]
            start_y = start_offset * np.sin(angle_offset_start)
            start_h = 0
            end_x = self._radie[idx2] * np.cos(an1) + end_offset * np.cos(
                an1 + angle_offset_end
            )
            end_y = self._radie[idx2] * np.sin(an1) + end_offset * np.sin(
                an1 + angle_offset_end
            )
            end_h = an1

        elif self._generic_junction:
            start_x = self._x[idx1] + start_offset * np.cos(
                self._h[idx1] + angle_offset_start
            )
            start_y = self._y[idx1] + start_offset * np.sin(
                self._h[idx1] + angle_offset_start
            )
            start_h = self._h[idx1]
            end_x = self._x[idx2] + end_offset * np.cos(
                self._h[idx2] - angle_offset_end
            )
            end_y = self._y[idx2] + end_offset * np.sin(
                self._h[idx2] - angle_offset_end
            )
            end_h = self._h[idx2] - np.pi
        clothoids = pcloth.SolveG2(
            start_x,
            start_y,
            start_h,
            STD_START_CLOTH,
            end_x,
            end_y,
            end_h,
            STD_START_CLOTH,
        )
        roadgeoms = [
            Spiral(x.KappaStart, x.KappaEnd, length=x.length)
            for x in clothoids
        ]
        if self._get_connection_type(idx1) == "successor":
            if lane_one_id < 0:
                num_left_lanes = 0
                num_right_lanes = 1
            else:
                num_left_lanes = 1
                num_right_lanes = 0

        else:
            if lane_one_id < 0:
                num_left_lanes = 1
                num_right_lanes = 0
            else:
                num_left_lanes = 0
                num_right_lanes = 1

        tmp_junc_road = create_road(
            roadgeoms,
            self.startnum,
            left_lanes=num_left_lanes,
            right_lanes=num_right_lanes,
            lane_width=start_width,
            road_type=self.id,
            lane_width_end=end_width,
        )
        if self._height is not None:
            tmp_junc_road.add_elevation(0, self._height, 0, 0, 0)
            tmp_junc_road.add_superelevation(0, 0, 0, 0, 0)
        pred_lane_offset = np.sign(lane_one_id) * (abs(lane_one_id) - 1)
        if self._get_connection_type(idx1) == "predecessor":
            pred_lane_offset = -pred_lane_offset
        succ_lane_offset = np.sign(lane_two_id) * (abs(lane_two_id) - 1)
        if self._get_connection_type(idx2) == "predecessor":
            succ_lane_offset = -succ_lane_offset

        tmp_junc_road.add_predecessor(
            ElementType.road,
            road_one_id,
            contact_point=self._get_contact_point_connecting_road(road_one_id),
            lane_offset=pred_lane_offset,
        )
        tmp_junc_road.add_successor(
            ElementType.road,
            road_two_id,
            contact_point=self._get_contact_point_connecting_road(road_two_id),
            lane_offset=succ_lane_offset,
        )
        # add offsets to the incomming roads
        self._set_offset_for_incoming_road(
            idx1, tmp_junc_road.id, -pred_lane_offset
        )
        self._set_offset_for_incoming_road(
            idx2, tmp_junc_road.id, -succ_lane_offset
        )

        self.junction_roads.append(tmp_junc_road)
        connection = Connection(
            road_one_id, tmp_junc_road.id, ContactPoint.start
        )
        if num_left_lanes:
            connection.add_lanelink(lane_one_id, 1)
        else:
            connection.add_lanelink(lane_one_id, -1)
        self.junction.add_connection(connection)
        self.startnum += 1

    def _add_connection_full(self, connecting_road: "Road") -> None:
        """Create full lane connections for a connecting road.

        This method generates lane connections for both predecessor and
        successor roads, ensuring all lanes are properly linked.

        Parameters
        ----------
        connecting_road : Road
            The connecting road for which lane connections are created.

        Returns
        -------
        None
        """
        conne1 = Connection(
            connecting_road.successor.element_id,
            connecting_road.id,
            ContactPoint.end,
        )
        _, sign, _ = _get_related_lanesection(
            connecting_road,
            self.incoming_roads[
                self._get_list_index(connecting_road.successor.element_id)
            ],
        )

        _create_junction_links(
            conne1,
            len(connecting_road.lanes.lanesections[-1].rightlanes),
            -1,
            sign,
            to_offset=connecting_road.lane_offset_suc[
                str(connecting_road.successor.element_id)
            ],
        )
        _create_junction_links(
            conne1,
            len(connecting_road.lanes.lanesections[-1].leftlanes),
            1,
            sign,
            to_offset=connecting_road.lane_offset_suc[
                str(connecting_road.successor.element_id)
            ],
        )
        self.junction.add_connection(conne1)

        # handle predecessor lanes
        conne2 = Connection(
            connecting_road.predecessor.element_id,
            connecting_road.id,
            ContactPoint.start,
        )
        _, sign, _ = _get_related_lanesection(
            connecting_road,
            self.incoming_roads[
                self._get_list_index(connecting_road.predecessor.element_id)
            ],
        )
        _create_junction_links(
            conne2,
            len(connecting_road.lanes.lanesections[0].rightlanes),
            -1,
            sign,
            from_offset=connecting_road.lane_offset_pred[
                str(connecting_road.predecessor.element_id)
            ],
        )
        _create_junction_links(
            conne2,
            len(connecting_road.lanes.lanesections[0].leftlanes),
            1,
            sign,
            from_offset=connecting_road.lane_offset_pred[
                str(connecting_road.predecessor.element_id)
            ],
        )
        self.junction.add_connection(conne2)

    def _create_geometry_from_carthesian(self, idx1: int, idx2: int) -> list:
        """Create a connecting road between two roads using Cartesian
        coordinates.

        This method generates the geometry for a connecting road based on
        the Cartesian coordinates and headings of the two roads.

        Parameters
        ----------
        idx1 : int
            The index of the first road in the incoming roads list.
        idx2 : int
            The index of the second road in the incoming roads list.

        Returns
        -------
        list of Geometries
            A list of geometry objects representing the connecting road.
        """
        an1 = self._h[idx2] - self._h[idx1] - np.pi
        # adjust angle if multiple of pi
        if an1 > np.pi:
            an1 = -(2 * np.pi - an1)

        clothoids = pcloth.SolveG2(
            self._x[idx1],
            self._y[idx1],
            self._h[idx1],
            STD_START_CLOTH,
            self._x[idx2],
            self._y[idx2],
            self._h[idx2] - np.pi,
            STD_START_CLOTH,
        )
        roadgeoms = [
            Spiral(x.KappaStart, x.KappaEnd, length=x.length)
            for x in clothoids
        ]
        return roadgeoms

    def _create_geometry_from_circular(self, idx1: int, idx2: int) -> list:
        """Create a connecting road between two roads using circular geometry.

        This method generates the geometry for a connecting road based on
        the circular radius and angles of the two roads.

        Parameters
        ----------
        idx1 : int
            The index of the first road in the incoming roads list.
        idx2 : int
            The index of the second road in the incoming roads list.

        Returns
        -------
        list of Geometries
            A list of geometry objects representing the connecting road.
        """
        an1 = self._angles[idx2] - self._angles[idx1] - np.pi
        # adjust angle if multiple of pi
        if an1 > np.pi:
            an1 = -(2 * np.pi - an1)

        if np.sign(an1) == 0:
            roadgeoms = [Line(self._radie[idx1] + self._radie[idx2])]
        else:
            clothoids = pcloth.SolveG2(
                -self._radie[idx1],
                0,
                0,
                STD_START_CLOTH,
                self._radie[idx2] * np.cos(an1),
                self._radie[idx2] * np.sin(an1),
                an1,
                STD_START_CLOTH,
            )
            roadgeoms = [
                Spiral(x.KappaStart, x.KappaEnd, length=x.length)
                for x in clothoids
            ]

        return roadgeoms

    def get_connecting_roads(self) -> list:
        """Retrieve the connecting roads generated for the junction.

        This method returns a list of all connecting roads created for the
        junction.

        Returns
        -------
        list of Road
            A list of connecting roads.
        """
        return self.junction_roads


class DirectJunctionCreator:
    """DirectJunctionCreator is a helper class to create custom direct
    junctions.

    Parameters
    ----------
    id : int
        The ID of the junction.
    name : str
        Name of the junction.

    Attributes
    ----------
    id : int
        The ID of the junction.
    junction : Junction
        The junction xodr element for the junction.

    Methods
    -------
    add_connection(incoming_road, linked_road, incoming_lane_ids=None,
    linked_lane_ids=None)
        Adds a connection between an incoming road and a linked road.
        If no lane information is provided, it connects all lanes that the
        two roads have in common.
    """

    def __init__(self, id: int, name: str) -> None:
        """Initialize the `DirectJunctionCreator` instance.

        Parameters
        ----------
        id : int
            The ID of the junction.
        name : str
            Name of the junction.

        Returns
        -------
        None
        """
        self.id = id
        self.junction = Junction(name, id, JunctionType.direct)
        self._incoming_lane_ids = []
        self._linked_lane_ids = []

    def _get_minimum_lanes_to_connect(
        self, incoming_road: "Road", linked_road: "Road"
    ) -> tuple[list[int], list[int]]:
        """Determine the minimum number of lanes to connect between two roads.

        This method calculates the lane IDs for both incoming and linked
        roads based on their lane sections and driving directions.

        Parameters
        ----------
        incoming_road : Road
            The incoming road to the junction.
        linked_road : Road
            The linked road to the junction.

        Returns
        -------
        tuple of (list of int, list of int)
            A tuple containing:
            - incoming_lane_ids : list of int
                Lane IDs for the incoming road.
            - linked_lane_ids : list of int
                Lane IDs for the linked road.
        """
        (
            incoming_connection,
            _,
            incoming_lane_section,
        ) = _get_related_lanesection(incoming_road, linked_road)
        (
            linked_connection,
            sign,
            linked_lane_section,
        ) = _get_related_lanesection(linked_road, incoming_road)

        incoming_left_lanes = len(
            incoming_road.lanes.lanesections[incoming_lane_section].leftlanes
        )
        incoming_right_lanes = len(
            incoming_road.lanes.lanesections[incoming_lane_section].rightlanes
        )
        linked_left_lanes = len(
            linked_road.lanes.lanesections[linked_lane_section].leftlanes
        )
        linked_right_lanes = len(
            linked_road.lanes.lanesections[linked_lane_section].rightlanes
        )
        self._incoming_lane_ids = []
        self._linked_lane_ids = []
        # if incoming_connection == "successor" and linked_connection == "predecessor" or incoming_connection == "predecessor" and linked_connection == "successor":
        if sign > 0:
            self._incoming_lane_ids.extend(
                [
                    x
                    for x in range(
                        -min(incoming_right_lanes, linked_right_lanes), 0, 1
                    )
                ]
            )
            self._linked_lane_ids.extend(
                [
                    x
                    for x in range(
                        -min(incoming_right_lanes, linked_right_lanes), 0, 1
                    )
                ]
            )

            self._incoming_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_left_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )
            self._linked_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_left_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )

        elif (
            sign < 0
        ):  # incoming_connection == "successor" and linked_connection == "successor" or incoming_connection == "predecessor" and linked_connection == "predecessor":
            self._incoming_lane_ids.extend(
                [
                    -x
                    for x in range(
                        -min(incoming_left_lanes, linked_right_lanes), 0, 1
                    )
                ]
            )
            self._linked_lane_ids.extend(
                [
                    x
                    for x in range(
                        -min(incoming_left_lanes, linked_right_lanes), 0, 1
                    )
                ]
            )

            self._incoming_lane_ids.extend(
                [
                    -x
                    for x in range(
                        1, min(incoming_right_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )
            self._linked_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_right_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )

    def _get_contact_point_linked_road(
        self, incoming_road: "Road"
    ) -> ContactPoint:
        """Get the contact point for a linked road.

        This method determines whether the linked road is a predecessor
        or successor of the junction.

        Parameters
        ----------
        incoming_road : Road
            The incoming road to the junction.

        Returns
        -------
        ContactPoint
            The contact point (`ContactPoint.start` or `ContactPoint.end`).

        Raises
        ------
        AttributeError
            If the road is not connected to the junction.
        """
        if (
            incoming_road.successor
            and incoming_road.successor.element_id == self.id
        ):
            return ContactPoint.end
        elif (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            return ContactPoint.start
        else:
            raise AttributeError(
                "road : "
                + str(incoming_road.id)
                + " is not connected to junction: "
                + str(self.id)
            )

    def add_connection(
        self,
        incoming_road: "Road",
        linked_road: "Road",
        incoming_lane_ids: Optional[Union[int, list[int]]] = None,
        linked_lane_ids: Optional[Union[int, list[int]]] = None,
    ) -> None:
        """Add a connection between an incoming road and a linked road.

        This method connects two roads using specified lane IDs or
        automatically determines the lanes to connect if no lane IDs are
        provided.

        Parameters
        ----------
        incoming_road : Road
            The incoming road to the junction.
        linked_road : Road
            The linked road to the junction.
        incoming_lane_ids : int or list of int, optional
            The lane ID(s) on the incoming road to connect.
            Default is None.
        linked_lane_ids : int or list of int, optional
            The lane ID(s) on the linked road to connect.
            Default is None.

        Raises
        ------
        MixingDrivingDirection
            If the driving direction is inconsistent between the two
            roads.
        NotSameAmountOfLanesError
            If the number of incoming and linked lane IDs are not the
            same.

        Returns
        -------
        None
        """

        linked_lane_offset = 0
        inc_lane_offset = 0
        incoming_main_road = False
        if incoming_lane_ids == None and linked_lane_ids == None:
            self._get_minimum_lanes_to_connect(incoming_road, linked_road)

        elif incoming_lane_ids is not None and linked_lane_ids is not None:
            if not isinstance(incoming_lane_ids, list):
                self._incoming_lane_ids = [incoming_lane_ids]
            else:
                self._incoming_lane_ids = incoming_lane_ids

            if not isinstance(linked_lane_ids, list):
                self._linked_lane_ids = [linked_lane_ids]

                if abs(linked_lane_ids) == 1:
                    incoming_main_road = True
            else:
                self._linked_lane_ids = linked_lane_ids
                if min([abs(x) for x in self._linked_lane_ids]) == 1:
                    incoming_main_road = True
            # sanity check
            for i in range(len(self._incoming_lane_ids)):
                if self._get_contact_point_linked_road(
                    incoming_road
                ) == self._get_contact_point_linked_road(linked_road):
                    if np.sign(self._incoming_lane_ids[i]) == np.sign(
                        self._linked_lane_ids[i]
                    ):
                        raise MixingDrivingDirection(
                            "driving direction not consistent when trying to make connection between roads:"
                            + str(incoming_road.id)
                            + " and "
                            + str(linked_road.id)
                        )
                else:
                    if np.sign(self._incoming_lane_ids[i]) != np.sign(
                        self._linked_lane_ids[i]
                    ):
                        raise MixingDrivingDirection(
                            "driving direction not consistent when trying to make connection between roads:"
                            + str(incoming_road.id)
                            + " and "
                            + str(linked_road.id)
                        )
            if len(self._linked_lane_ids) != len(self._linked_lane_ids):
                raise NotSameAmountOfLanesError(
                    "the incoming_lane_ids and linked_lane_ids are not the same length"
                )

            if abs(self._incoming_lane_ids[0]) != abs(
                self._linked_lane_ids[0]
            ):
                lane_offset = abs(
                    abs(self._incoming_lane_ids[0])
                    - abs(self._linked_lane_ids[0])
                )

                if incoming_main_road:
                    linked_lane_offset = (
                        np.sign(self._linked_lane_ids[0]) * lane_offset
                    )
                    inc_lane_offset = (
                        -1
                        * np.sign(
                            self._incoming_lane_ids[0]
                            * self._linked_lane_ids[0]
                        )
                        * linked_lane_offset
                    )
                else:
                    inc_lane_offset = (
                        np.sign(self._incoming_lane_ids[0]) * lane_offset
                    )
                    linked_lane_offset = (
                        -1
                        * np.sign(
                            self._incoming_lane_ids[0]
                            * self._linked_lane_ids[0]
                        )
                        * inc_lane_offset
                    )
        if (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            incoming_road.pred_direct_junction[linked_road.id] = (
                inc_lane_offset
            )
        else:
            incoming_road.succ_direct_junction[linked_road.id] = (
                inc_lane_offset
            )

        if (
            linked_road.predecessor
            and linked_road.predecessor.element_id == self.id
        ):
            linked_road.pred_direct_junction[incoming_road.id] = (
                linked_lane_offset
            )
        else:
            linked_road.succ_direct_junction[incoming_road.id] = (
                linked_lane_offset
            )

        connection = Connection(
            incoming_road.id,
            linked_road.id,
            self._get_contact_point_linked_road(linked_road),
        )
        for i in range(len(self._incoming_lane_ids)):
            connection.add_lanelink(
                self._incoming_lane_ids[i], self._linked_lane_ids[i]
            )
        self.junction.add_connection(connection)
