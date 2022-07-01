"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""

from .enumerations import JunctionType, ElementType, ContactPoint
from .geometry import Spiral, Line
from .generators import create_road, _get_related_lanesection, _create_junction_links
from .links import Junction, Connection
from .exceptions import (
    NotEnoughInputArguments,
    UndefinedRoadNetwork,
    NotSameAmountOfLanesError,
)
import pyclothoids as pcloth

import numpy as np

STD_START_CLOTH = 1 / 1000000000


class CommonJunctionCreator:
    """CommonJunctionCreator is a helper class to create custom common junctions.

    Parameters
    ----------
        id (int): the id of the junction

        name (str): name of the junction

        startnum (int): the starting id of this junctions roads
            Default: 100

    Attributes
    ----------
        id (int): the id of the junction

        startnum (int): the starting id of this junctions roads

        incoming_roads (list of Road): all incoming roads for the junction

        junction_roads (list of Road): all generated connecting roads

        junction (Junction): the junction xodr element for the junction

    Methods
    -------
        add_incoming_road_circular_geometry(road, radius, angle, road_connection)
            Adds a road on a circle defining the junction geometry
            Note: cannot be used together with 'add_incoming_road_cartesian_geometry'

        add_incoming_road_cartesian_geometry(road, x, y, heading, road_connection)
            Adds a road on a generic x, y, heading geometry
            Note: cannot be used together with 'add_incoming_road_circular_geometry'

        add_connection(first_road_id, second_road_id, first_lane_id, second_lane_id)
    """

    def __init__(self, id, name, startnum=100):
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

    def add_incoming_road_circular_geometry(
        self, road, radius, angle, road_connection=None
    ):
        """add_incoming_road_circular_geometry adds an incoming road to a junction, assuming a cirular geometry of the junction,
        Meaning all roads will be placed on a circle based on the radius and angle.
        The radius can be different from different incoming roads, however the origin stays the same.

        NOTE: Note, this method can not be used toghether with add_incoming_road_cartesian_geometry

        Parameters
        ----------
            road (Road): the incoming road

            radius (float): the radius on where to put the road

            angle (float): the angle on where to put the road

            road_connection (str): can be used to say how the incoming road connects to the junction 'predecessor', or 'successor'
                Default: None
        """
        self.incoming_roads.append(road)
        self._handle_connection_input(road, road_connection)
        self._radie.append(radius)
        self._angles.append(angle)
        self._circular_junction = True

    def add_incoming_road_cartesian_geometry(
        self, road, x, y, heading, road_connection=None
    ):
        """add_incoming_road_cartesian_geometry adds an incoming road to a junction, assuming a
        local coordinate system for the junction.

        NOTE: Note, this method can not be used toghether with add_incoming_road_circular_geometry

        Parameters
        ----------
            road (Road): the incoming road

            x (float): the local x-position of the road

            y (float): the local y-position of the road

            heading (float): the local heading of the road (pointing in to the junction)

            road_connection (str): can be used to say how the incoming road connects to the junction 'predecessor', or 'successor'
                Default: None
        """
        self.incoming_roads.append(road)
        self._handle_connection_input(road, road_connection)

        self._x.append(x)
        self._y.append(y)
        self._h.append(heading)
        self._generic_junction = True

    def _get_minimum_lanes_to_connect(self, incoming_road, linked_road):

        (
            incoming_connection,
            incoming_sign,
            incoming_lane_section,
        ) = _get_related_lanesection(incoming_road, linked_road)
        linked_connection, sign, linked_lane_section = _get_related_lanesection(
            linked_road, incoming_road
        )

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
        self, road_one_id, road_two_id, lane_one_id=None, lane_two_id=None
    ):
        """add_connection adds a connection between two roads by generating three clothoids to fit
        their given positions in the local coordinate system (circular or cartesian)
        All roads has to be added to the junction with either:
            add_incoming_road_cartesian_geometry
            add_incoming_road_circular_geometry

        NOTE: if no lane ids are provided, add_connection will add as many connections as the two roads have in common

        Parameters
        ----------
            road_one_id (int): the id of the first road to connect

            road_two_id (int): the id of the second road to connect

            lane_one_id (int or list of int): the lane id(s) on the first road to connect

            lane_two_id (int or list of int): the lane id(s) on the second road to connect
        """
        if (lane_one_id == None) and (lane_two_id == None):
            # check if the connection is symetric (same number of lanes on both sides)
            if (
                self._number_of_left_lanes[self._get_list_index(road_one_id)]
                == self._number_of_right_lanes[self._get_list_index(road_one_id)]
                and self._number_of_left_lanes[self._get_list_index(road_two_id)]
                == self._number_of_right_lanes[self._get_list_index(road_two_id)]
                and self._number_of_left_lanes[self._get_list_index(road_one_id)]
                == self._number_of_right_lanes[self._get_list_index(road_two_id)]
            ):
                self._create_connecting_roads_with_equal_lanes(road_one_id, road_two_id)
            else:

                self._create_connecting_roads_unequal_lanes(road_one_id, road_two_id)
        elif lane_one_id is not None and lane_two_id is not None:
            if isinstance(lane_one_id, list):
                for i in range(len(lane_one_id)):
                    self._create_connecting_road_with_lane_input(
                        road_one_id, road_two_id, lane_one_id[i], lane_two_id[i]
                    )
            else:
                self._create_connecting_road_with_lane_input(
                    road_one_id, road_two_id, lane_one_id, lane_two_id
                )
        else:
            raise NotEnoughInputArguments(
                "if lane input is used, both has to be provided"
            )

    def _handle_connection_input(self, road, road_connection):
        """Checker to see if enough data is provided for an incoming road

        Parameters
        ----------
            road (Road): the incoming road

            road_connection (str): the connection type (predecessor or successor)

        """

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
                or (road.predecessor and road.predecessor.element_id == self.id)
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
            self._number_of_left_lanes.append(len(road.lanes.lanesections[0].leftlanes))
            self._number_of_right_lanes.append(
                len(road.lanes.lanesections[0].rightlanes)
            )

    def _get_list_index(self, id):
        """helping method to get the index of the road based on a road id

        Parameters
        ----------
            id (int): the road id

        Returns
        -------
            index (int)

        """
        return [
            self.incoming_roads.index(x) for x in self.incoming_roads if x.id == id
        ][0]

    def _set_offset_for_incoming_road(self, road_idx, connecting_road_id, offset):
        """_set_offset_for_incoming_road is a helper function to set the correct offsets for a incoming road

        Parameters
        ----------
            road_idx (int): the index of the road

            connecting_road_id (int): the id of the connecting road

            offset (int): the lane offset

        """

        if self._get_connection_type(road_idx) == "successor":
            self.incoming_roads[road_idx].lane_offset_suc[
                str(connecting_road_id)
            ] = offset
        else:
            self.incoming_roads[road_idx].lane_offset_pred[
                str(connecting_road_id)
            ] = offset

    def _get_contact_point_connecting_road(self, road_id):
        """_get_contact_point_connecting_road is a helper method to get the ContactPoint for a connecting road

        Parameters
        ----------
            road_id (int): id of the incoming road

        Returns
        -------
            contact_point (ContactPoint)
        """
        incoming_road = self.incoming_roads[self._get_list_index(road_id)]
        if incoming_road.successor and incoming_road.successor.element_id == self.id:
            return ContactPoint.end
        elif (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            return ContactPoint.start
        else:
            raise AttributeError("road is not connected to this junction")

    def _get_connecting_lane_section(self, idx):
        """_get_connecting_lane_section is a helper method to get the connected

        Parameters
        ----------
            idx (int): the road index

        """
        incoming_road = self.incoming_roads[idx]
        if incoming_road.successor and incoming_road.successor.element_id == self.id:
            return -1
        elif (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            return 0
        else:
            raise AttributeError("road is not connected to this junction")

    def _create_connecting_roads_unequal_lanes(self, road_one_id, road_two_id):
        """_create_connecting_roads_unequal_lanes is a helper method that connects two roads that have different number of lanes going in to the junciton, will only connect lanes that are common between the roads

        Parameters
        ----------
            road_one_id (int): id of the first road

            road_two_id (int): id of the second road

        """
        idx1 = self._get_list_index(road_one_id)
        idx2 = self._get_list_index(road_two_id)
        if (
            self.incoming_roads[idx1]
            .lanes.lanesections[self._get_connecting_lane_section(idx1)]
            .leftlanes
        ):
            lane_width = (
                self.incoming_roads[idx1]
                .lanes.lanesections[self._get_connecting_lane_section(idx1)]
                .leftlanes[0]
                .widths[0]
                .a
            )
        else:
            lane_width = (
                self.incoming_roads[idx1]
                .lanes.lanesections[self._get_connecting_lane_section(idx1)]
                .rightlanes[0]
                .widths[0]
                .a
            )
        # check if the road has _angles/radius for these roads
        if self._circular_junction:
            roadgeoms = self._create_geometry_from_circular(idx1, idx2)
        elif self._generic_junction:
            roadgeoms = self._create_geometry_from_carthesian(idx1, idx2)
        first_road_lane_ids, _ = self._get_minimum_lanes_to_connect(
            self.incoming_roads[idx1], self.incoming_roads[idx2]
        )

        left_lanes = 0
        right_lanes = 0
        if any([x > 0 for x in first_road_lane_ids]):
            if self._get_connection_type(idx1) == "successor":
                left_lanes = max(first_road_lane_ids)
            else:
                right_lanes = max(first_road_lane_ids)

        if any([x < 0 for x in first_road_lane_ids]):
            if self._get_connection_type(idx1) == "successor":
                right_lanes = abs(min(first_road_lane_ids))
            else:
                left_lanes = abs(min(first_road_lane_ids))

        tmp_junc_road = create_road(
            roadgeoms,
            self.startnum,
            left_lanes=left_lanes,
            right_lanes=right_lanes,
            lane_width=lane_width,
            road_type=self.id,
        )

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
        ) = self._get_minimum_lanes_to_connect(self.incoming_roads[idx1], tmp_junc_road)
        connection = Connection(road_one_id, tmp_junc_road.id, ContactPoint.start)
        for i in range(len(first_road_lane_ids)):
            connection.add_lanelink(first_road_lane_ids[i], connecting_road_lane_ids[i])
        self.junction.add_connection(connection)

        (
            second_road_lane_ids,
            connecting_road_lane_ids,
        ) = self._get_minimum_lanes_to_connect(self.incoming_roads[idx2], tmp_junc_road)
        connection = Connection(
            tmp_junc_road.successor.element_id, tmp_junc_road.id, ContactPoint.end
        )
        for i in range(len(second_road_lane_ids)):
            connection.add_lanelink(
                second_road_lane_ids[i], connecting_road_lane_ids[i]
            )
        self.junction.add_connection(connection)

        self.junction_roads.append(tmp_junc_road)
        self.startnum += 1

    def _create_connecting_roads_with_equal_lanes(self, road_one_id, road_two_id):
        """_create_connecting_roads_with_equal_lanes is a helper method that connects two roads that have the
        same number of left and right lanes

        Parameters
        ----------
            road_one_id (int): id of the first road

            road_two_id (int): id of the second road

        """
        idx1 = self._get_list_index(road_one_id)
        idx2 = self._get_list_index(road_two_id)

        # check if the road has _angles/radius for these roads
        if self._circular_junction:
            roadgeoms = self._create_geometry_from_circular(idx1, idx2)
        elif self._generic_junction:
            roadgeoms = self._create_geometry_from_carthesian(idx1, idx2)
        if (
            self.incoming_roads[idx1]
            .lanes.lanesections[self._get_connecting_lane_section(idx1)]
            .leftlanes
        ):
            lane_width = (
                self.incoming_roads[idx1]
                .lanes.lanesections[self._get_connecting_lane_section(idx1)]
                .leftlanes[0]
                .widths[0]
                .a
            )
        else:
            lane_width = (
                self.incoming_roads[idx1]
                .lanes.lanesections[self._get_connecting_lane_section(idx1)]
                .rightlanes[0]
                .widths[0]
                .a
            )
        tmp_junc_road = create_road(
            roadgeoms,
            self.startnum,
            left_lanes=len(
                self.incoming_roads[idx1]
                .lanes.lanesections[self._get_connecting_lane_section(idx1)]
                .leftlanes
            ),
            right_lanes=len(
                self.incoming_roads[idx1]
                .lanes.lanesections[self._get_connecting_lane_section(idx1)]
                .rightlanes
            ),
            lane_width=lane_width,
            road_type=self.id,
        )

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

    def _get_connection_type(self, road_idx):
        if (
            self.incoming_roads[road_idx].successor
            and self.incoming_roads[road_idx].successor.element_id == self.id
        ):
            return "successor"
        else:
            return "predecessor"

    def _create_connecting_road_with_lane_input(
        self, road_one_id, road_two_id, lane_one_id, lane_two_id
    ):
        """_create_connecting_road_with_lane_input is a helper method that connects two roads with one lane on each road

        Parameters
        ----------
            road_one_id (int): the id of the first road to connect

            road_two_id (int): the id of the second road to connect

            lane_one_id (int): the lane id(s) on the first road to connect

            lane_two_id (int): the lane id(s) on the second road to connect
        """

        idx1 = self._get_list_index(road_one_id)
        idx2 = self._get_list_index(road_two_id)
        if (
            self.incoming_roads[idx1]
            .lanes.lanesections[self._get_connecting_lane_section(idx1)]
            .leftlanes
        ):
            lane_width = (
                self.incoming_roads[idx1]
                .lanes.lanesections[self._get_connecting_lane_section(idx1)]
                .leftlanes[0]
                .get_width(0)
            )
        else:
            lane_width = (
                self.incoming_roads[idx1]
                .lanes.lanesections[self._get_connecting_lane_section(idx1)]
                .rightlanes[0]
                .get_width(0)
            )
        start_offset = (abs(lane_one_id) - 1) * lane_width
        end_offset = (abs(lane_two_id) - 1) * lane_width

        if self._get_connection_type(idx1) == "successor":
            angle_offset_start = np.sign(lane_one_id) * np.pi / 2
        else:
            angle_offset_start = -np.sign(lane_one_id) * np.pi / 2
        if self._get_connection_type(idx2) == "successor":
            angle_offset_end = np.sign(lane_two_id) * np.pi / 2
        else:
            angle_offset_end = -np.sign(lane_two_id) * np.pi / 2

        if self._circular_junction:
            an1 = self._angles[idx2] - self._angles[idx1] - np.pi
            # adjust angle if multiple of pi
            if an1 > np.pi:
                an1 = -(2 * np.pi - an1)
            # -self._radie[idx1],
            #     0,
            #     0,
            #     STD_START_CLOTH,
            #     self._radie[idx2] * np.cos(an1),
            #     self._radie[idx2] * np.sin(an1),
            #     an1,
            #     STD_START_CLOTH,
            start_x = -self._radie[idx1]
            start_y = start_offset
            start_h = 0
            end_x = self._radie[idx2] * np.cos(an1) + end_offset * np.cos(
                self._angles[idx2] + angle_offset_end
            )
            end_y = self._radie[idx2] * np.sin(an1) + end_offset * np.sin(
                self._angles[idx2] + angle_offset_end
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
                self._h[idx2] + angle_offset_end
            )
            end_y = self._y[idx2] + end_offset * np.sin(
                self._h[idx2] + angle_offset_end
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
            Spiral(x.KappaStart, x.KappaEnd, length=x.length) for x in clothoids
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
            lane_width=lane_width,
            road_type=self.id,
        )

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
        self._set_offset_for_incoming_road(idx1, tmp_junc_road.id, -pred_lane_offset)
        self._set_offset_for_incoming_road(idx2, tmp_junc_road.id, -succ_lane_offset)

        self.junction_roads.append(tmp_junc_road)
        connection = Connection(road_one_id, tmp_junc_road.id, ContactPoint.start)
        if num_left_lanes:
            connection.add_lanelink(lane_one_id, 1)
        else:
            connection.add_lanelink(lane_one_id, -1)
        self.junction.add_connection(connection)
        self.startnum += 1

    def _add_connection_full(self, connecting_road):
        """_add_connection_full is a helper method creating connections for connections with equal amount of lanes

        Parameters
        ----------
            connecting_road (Road): the connecting road
        """
        conne1 = Connection(
            connecting_road.successor.element_id, connecting_road.id, ContactPoint.end
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

    def _create_geometry_from_carthesian(self, idx1, idx2):
        """_create_geometry_from_carthesian creates a connecting road between two roads added with carthesian coordinates

        Parameters
        ----------
            idx1 (int): index of the first road

            idx2 (int): index of the second road

        Returns
        -------
            list of Geometries
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
            Spiral(x.KappaStart, x.KappaEnd, length=x.length) for x in clothoids
        ]
        return roadgeoms

    def _create_geometry_from_circular(self, idx1, idx2):
        """_create_geometry_from_circular creates a connecting road between two roads added with circular geometry

        Parameters
        ----------
            idx1 (int): index of the first road

            idx2 (int): index of the second road

        Returns
        -------
            list of Geometries

        """
        an1 = self._angles[idx2] - self._angles[idx1] - np.pi
        # adjust angle if multiple of pi
        if an1 > np.pi:
            an1 = -(2 * np.pi - an1)

        if np.sign(an1) == 0:
            roadgeoms = Line(self._radie[idx1] + self._radie[idx2])
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
                Spiral(x.KappaStart, x.KappaEnd, length=x.length) for x in clothoids
            ]

        return roadgeoms

    def get_connecting_roads(self):
        """returns the connecting roads generated for the junction

        Returns
        -------
            list of Road

        """
        return self.junction_roads


class DirectJunctionCreator:
    """DirectJunctionCreator is a helper class to create custom direct junctions.

    Parameters
    ----------
        id (int): the id of the junction

        name (str): name of the junction

    Attributes
    ----------
        id (int): the id of the junction

        junction (Junction): the junction xodr element for the junction

    Methods
    -------

        add_connection(first_road_id, second_road_id, first_lane_id, second_lane_id)
    """

    def __init__(self, id, name):
        """Initalize the DirectJunctionCreator

        Parameters
        ----------
            id (int): the id of the junction

            name (str): name of the junction

        """
        self.id = id
        self.junction = Junction(name, id, JunctionType.direct)
        self._incoming_lane_ids = []
        self._linked_lane_ids = []

    def _get_connecting_lane_section(self, idx):
        """_get_connecting_lane_section is a helper method to get the connected

        Parameters
        ----------
            idx (int): the road index

        """
        incoming_road = self.incoming_roads[idx]
        if incoming_road.successor and incoming_road.successor.element_id == self.id:
            return -1
        elif (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            return 0
        else:
            raise AttributeError("road is not connected to this junction")

    def _get_minimum_lanes_to_connect(self, incoming_road, linked_road):

        incoming_connection, _, incoming_lane_section = _get_related_lanesection(
            incoming_road, linked_road
        )
        linked_connection, sign, linked_lane_section = _get_related_lanesection(
            linked_road, incoming_road
        )

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
                [x for x in range(-min(incoming_right_lanes, linked_right_lanes), 0, 1)]
            )
            self._linked_lane_ids.extend(
                [x for x in range(-min(incoming_right_lanes, linked_right_lanes), 0, 1)]
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
                [x for x in range(-min(incoming_left_lanes, linked_right_lanes), 0, 1)]
            )
            self._linked_lane_ids.extend(
                [-x for x in range(-min(incoming_left_lanes, linked_right_lanes), 0, 1)]
            )

            self._incoming_lane_ids.extend(
                [
                    x
                    for x in range(
                        1, min(incoming_right_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )
            self._linked_lane_ids.extend(
                [
                    -x
                    for x in range(
                        1, min(incoming_right_lanes, linked_left_lanes) + 1, 1
                    )
                ]
            )

    def _get_contact_point_linked_road(self, incoming_road):
        """_get_contact_point_linked_road is a helper method to get the ContactPoint for a linked road

        Parameters
        ----------
            road_id (int): id of the incoming road

        Returns
        -------
            contact_point (ContactPoint)
        """
        if incoming_road.successor and incoming_road.successor.element_id == self.id:
            return ContactPoint.end
        elif (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            return ContactPoint.start
        else:
            raise AttributeError("road is not connected to this junction")

    def add_connection(
        self, incoming_road, linked_road, incoming_lane_ids=None, linked_lane_ids=None
    ):
        """add_connection adds a connection between an incoming_road and a linked_road.
        Withouth any lane information, it will add connections to all lanes that the two roads have in common

        Parameters
        ----------
            incoming_road (Road): the incoming road

            linked_road (Road): the linked road

            incoming_lane_ids (int or list of ints): the incoming lane ids to connect
                Default: None

            linked_lane_ids (int or list of ints): the linked lane ids to connect
                Default: None
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
            if len(self._linked_lane_ids) != len(self._linked_lane_ids):
                raise NotSameAmountOfLanesError(
                    "the incoming_lane_ids and linked_lane_ids are not the same length"
                )

            if abs(self._incoming_lane_ids[0]) != abs(self._linked_lane_ids[0]):
                lane_offset = abs(
                    abs(self._incoming_lane_ids[0]) - abs(self._linked_lane_ids[0])
                )

                if incoming_main_road:
                    linked_lane_offset = np.sign(self._linked_lane_ids[0]) * lane_offset
                    inc_lane_offset = (
                        -1
                        * np.sign(self._incoming_lane_ids[0] * self._linked_lane_ids[0])
                        * linked_lane_offset
                    )
                else:
                    inc_lane_offset = np.sign(self._incoming_lane_ids[0]) * lane_offset
                    linked_lane_offset = (
                        -1
                        * np.sign(self._incoming_lane_ids[0] * self._linked_lane_ids[0])
                        * inc_lane_offset
                    )
        if (
            incoming_road.predecessor
            and incoming_road.predecessor.element_id == self.id
        ):
            incoming_road.pred_direct_junction[linked_road.id] = inc_lane_offset
        else:

            incoming_road.succ_direct_junction[linked_road.id] = inc_lane_offset

        if linked_road.predecessor and linked_road.predecessor.element_id == self.id:
            linked_road.pred_direct_junction[incoming_road.id] = linked_lane_offset
        else:
            linked_road.succ_direct_junction[incoming_road.id] = linked_lane_offset

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
