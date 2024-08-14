"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

from operator import index
import xml.etree.ElementTree as ET
from ..helpers import enum2str
from .enumerations import (
    LaneType,
    LaneChange,
    RoadMarkWeight,
    RoadMarkColor,
    RoadMarkType,
    MarkRule,
    ContactPoint,
    enumchecker,
)
from .exceptions import ToManyOptionalArguments
from .utils import XodrBase
from .links import _Links, _Link, LaneLinker
import numpy as np


class Lanes(XodrBase):
    """creates the Lanes element of opendrive


    Attributes
    ----------
        lane_sections (list of LaneSection): a list of all lanesections

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        add_lanesection(lanesection)
            adds a lane section to Lanes

        add_laneoffset(laneoffset)
            adds a lane offset to Lanes
    """

    def __init__(self):
        super().__init__()
        """initalize Lanes"""
        self.lanesections = []
        self.laneoffsets = []
        self.roadmarks_adjusted = False

    def __eq__(self, other):
        if isinstance(other, Lanes) and super().__eq__(other):
            if (
                self.laneoffsets == other.laneoffsets
                and self.lanesections == other.lanesections
            ):
                return True
        return False

    def add_lanesection(self, lanesection, lanelinks=None):
        """creates the Lanes element of opendrive

        Parameters
        ----------
            lanesection (LaneSection): a LaneSection to add

            lanelink (LaneLinker): (optional) a LaneLink to add

        """
        if not isinstance(lanesection, LaneSection):
            raise TypeError("input lanesection is not of type LaneSection")
        # add links to the lanes
        if lanelinks:
            # loop over all links
            if not isinstance(lanelinks, list):
                lanelinks = [lanelinks]
            if any([not isinstance(x, LaneLinker) for x in lanelinks]):
                raise TypeError("lanelinks contains a none LaneLinker type")
            for lanelink in lanelinks:
                for link in lanelink.links:
                    # check if link already added
                    if not link.used:
                        link.predecessor.add_link("successor", link.successor.lane_id)
                        link.successor.add_link("predecessor", link.predecessor.lane_id)
                        link.used = True

        self.lanesections.append(lanesection)
        return self

    def add_laneoffset(self, laneoffset):
        """adds a lane offset to Lanes

        Parameters
        ----------
            laneoffset (LaneOffset): a LaneOffset to add
        """
        if not isinstance(laneoffset, LaneOffset):
            raise TypeError(
                "add_laneoffset requires a LaneOffset as input, not "
                + str(type(laneoffset))
            )
        self.laneoffsets.append(laneoffset)
        return self

    def _check_valid_mark_type(self, lane):
        """simple checker if the lanemark can be adjusted

        Parameters
        ----------
            lane (Lane): the lane which roadmark should be checked
        """
        return (
            lane.roadmark[0].marking_type == RoadMarkType.broken
            or lane.roadmark[0].marking_type == RoadMarkType.broken_broken
        )

    def _adjust_for_missing_line_offset(self, roadmark):
        """adds an explicit line if soofset is less than 0 (for adjusting from start) or longer than the space between lines (for adjusting from end)

        Parameters
        ----------
            roadmark (RoadMark): the roadmark to be adjusted
        """
        for line in roadmark._line:
            if line.soffset < 0 or line.soffset > line.length + line.soffset:
                roadmark.add_explicit_road_line(
                    ExplicitRoadLine(
                        line.width,
                        line.length + line.soffset,
                        line.toffset,
                        0,
                        line.rule,
                    )
                )
            elif line.soffset > line.space:
                roadmark.add_explicit_road_line(
                    ExplicitRoadLine(
                        line.width,
                        line.soffset - line.space,
                        line.toffset,
                        0,
                        line.rule,
                    )
                )
            if line.soffset < 0:
                line.shift_soffset()

    def _validity_check_for_roadmark_adjustment(self):
        """does some simple checks if the the different lanes can be adjusted"""
        self._right_lanes_adjustable = len(self.lanesections[0].rightlanes) > 0
        self._left_lanes_adjustable = len(self.lanesections[0].leftlanes) > 0
        self._center_lane_adjustable = True
        for ls in range(len(self.lanesections) - 1):
            if len(self.lanesections[ls].centerlane.roadmark) != 1:
                self.center_lane_adjustable = False
            if (
                self.lanesections[ls].centerlane.roadmark
                != self.lanesections[ls + 1].centerlane.roadmark
            ):
                self.center_lane_adjustable = False
            if (
                self.lanesections[ls].centerlane.roadmark[0].marking_type
                != RoadMarkType.broken
                and self.lanesections[ls].centerlane.roadmark[0].marking_type
                != RoadMarkType.broken_broken
            ):
                self.center_lane_adjustable = False

            for rl in range(len(self.lanesections[ls].rightlanes)):
                if self._right_lanes_adjustable:
                    if len(self.lanesections[ls].rightlanes[rl].roadmark) != 1:
                        self._right_lanes_adjustable = False
            for ll in range(len(self.lanesections[ls].leftlanes)):
                if self._left_lanes_adjustable:
                    if len(self.lanesections[ls].leftlanes[ll].roadmark) != 1:
                        self._left_lanes_adjustable = False

    def _get_previous_remainder(
        self,
        connected_lane_section,
        i_line,
        lane_side,
        contact_point,
        lane_index,
        lane_section_index,
        start_or_end,
    ):
        """_get_previous_remainder is a helper method to get the remainder of a lanemarking of a connecting lane section (for lenght adjustment)

        Parameters
        ----------
            connected_lane_section (LaneSection): connected lane section (on another road)

            i_line (int): index of the line (roadmark._line)

            lane_side (str): "left", "right", or "center" describing what lane is of interest

            contact_point (ContactPoint): contact point of the connected_lane_section

            lane_index (int): the lane index of the wanted lane

            lane_section_index (int): index of the lane section

            start_or_end (str): if the adjustment is done from the end or from the start of the road

        Return
        ------
            float: remainder of the previous lanesection

        """
        active_lane_sec = self.lanesections[lane_section_index]
        neighbor_lane_sec = None
        if start_or_end == "end":
            on_edge = lane_section_index == len(self.lanesections) - 1
            connection = "successor"
            if not on_edge:
                neighbor_lane_sec = self.lanesections[lane_section_index + 1]
        else:
            on_edge = lane_section_index == 0
            connection = "predecessor"
            if not on_edge:
                neighbor_lane_sec = self.lanesections[lane_section_index - 1]

        linked_lane_id = 0
        found_linked_lane_id = None
        if lane_side == "right":
            found_linked_lane_id = active_lane_sec.rightlanes[
                lane_index
            ].get_linked_lane_id(connection)
            if neighbor_lane_sec:
                neighboring_lane = neighbor_lane_sec.rightlanes[linked_lane_id]
        elif lane_side == "left":
            found_linked_lane_id = active_lane_sec.leftlanes[
                lane_index
            ].get_linked_lane_id(connection)
            if neighbor_lane_sec:
                neighboring_lane = neighbor_lane_sec.leftlanes[linked_lane_id]
        else:  # center
            if neighbor_lane_sec:
                neighboring_lane = neighbor_lane_sec.centerlane
        if found_linked_lane_id:
            linked_lane_id = abs(found_linked_lane_id) - 1

        prev_remainder = 0
        if on_edge:
            if lane_side == "right":
                if (
                    contact_point == ContactPoint.end
                    and connected_lane_section.rightlanes[linked_lane_id]
                    .roadmark[0]
                    ._line
                ):
                    prev_remainder = (
                        connected_lane_section.rightlanes[linked_lane_id]
                        .roadmark[0]
                        ._line[i_line]
                        ._remainder
                    )
                elif (
                    contact_point == ContactPoint.start
                    and connected_lane_section.leftlanes[linked_lane_id]
                    .roadmark[0]
                    ._line
                ):
                    prev_remainder = (
                        connected_lane_section.leftlanes[linked_lane_id]
                        .roadmark[0]
                        ._line[i_line]
                        .soffset
                    )

            if lane_side == "left":
                if (
                    contact_point == ContactPoint.end
                    and connected_lane_section.leftlanes[linked_lane_id]
                    .roadmark[0]
                    ._line
                ):
                    prev_remainder = (
                        connected_lane_section.leftlanes[linked_lane_id]
                        .roadmark[0]
                        ._line[i_line]
                        ._remainder
                    )
                elif (
                    contact_point == ContactPoint.start
                    and connected_lane_section.rightlanes[linked_lane_id]
                    .roadmark[0]
                    ._line
                ):
                    prev_remainder = (
                        connected_lane_section.rightlanes[linked_lane_id]
                        .roadmark[0]
                        ._line[i_line]
                        .soffset
                    )

            if (
                lane_side == "center"
                and connected_lane_section.centerlane.roadmark[0]._line
            ):
                if contact_point == ContactPoint.end:
                    prev_remainder = (
                        connected_lane_section.centerlane.roadmark[0]
                        ._line[i_line]
                        ._remainder
                    )
                elif contact_point == ContactPoint.start:
                    prev_remainder = (
                        connected_lane_section.centerlane.roadmark[0]
                        ._line[i_line]
                        .soffset
                    )

        else:
            if start_or_end == "start":
                prev_remainder = neighboring_lane.roadmark[0]._line[i_line]._remainder
            else:
                prev_remainder = neighboring_lane.roadmark[0]._line[i_line].soffset
        return prev_remainder

    def _get_seg_length(self, total_road_length, lane_section_index):
        """_get_seg_length is a helper method to figure out how long a lane section is

        Parameters
        ----------
            total_road_length (float): total length of the road

            lane_section_index (int): the index of the wanted lanesection

        Returns
        -------
            float: length of the lanesection

        """
        if len(self.lanesections) == 1:
            seg_length = total_road_length
        elif lane_section_index == 0:
            seg_length = self.lanesections[1].s
        elif lane_section_index == len(self.lanesections) - 1:
            seg_length = total_road_length - self.lanesections[lane_section_index].s
        else:
            seg_length = (
                self.lanesections[lane_section_index + 1].s
                - self.lanesections[lane_section_index].s
            )
        return seg_length

    def adjust_road_marks_from_start(
        self,
        total_road_length,
        connected_lane_section=None,
        contact_point=ContactPoint.end,
    ):
        """Adjusts road marks from the start of the road, based on the connected lane section.
        If connected_lane_section is not provided, the last roadmark will be placed with zero
        distance to the start of the road

        Parameters
        ----------
            total_road_length (float): total length of the road

            connected_lane_section (LaneSection): the lane section connected to the road
                Default: None

            contact_point (ContactPoint)
                Default: ContactPoint.end
        """
        contact_point = enumchecker(contact_point, ContactPoint)
        if connected_lane_section and not isinstance(
            connected_lane_section, LaneSection
        ):
            raise TypeError("connected_lane_section is not of type LaneSection")
        if not self.roadmarks_adjusted:
            self._validity_check_for_roadmark_adjustment()
            self.roadmarks_adjusted = True

            def set_zero_offset_to_lines(lane, seg_length):
                for i_line in range(len(lane.roadmark[0]._line)):
                    lane.roadmark[0]._line[i_line].adjust_remainder(
                        seg_length, soffset=0
                    )

            for ls in range(0, len(self.lanesections)):
                seg_length = self._get_seg_length(total_road_length, ls)
                if self._right_lanes_adjustable:
                    for rl in range(len(self.lanesections[ls].rightlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].rightlanes[rl]
                        ):
                            if ls == 0 and connected_lane_section is None:
                                set_zero_offset_to_lines(
                                    self.lanesections[ls].rightlanes[rl], seg_length
                                )
                            else:
                                for i_line in range(
                                    len(
                                        self.lanesections[ls]
                                        .rightlanes[rl]
                                        .roadmark[0]
                                        ._line
                                    )
                                ):
                                    prev_remainder = self._get_previous_remainder(
                                        connected_lane_section,
                                        i_line,
                                        "right",
                                        contact_point,
                                        rl,
                                        ls,
                                        "start",
                                    )
                                    self.lanesections[ls].rightlanes[rl].roadmark[
                                        0
                                    ]._line[i_line].adjust_remainder(
                                        seg_length, previous_remainder=prev_remainder
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls].rightlanes[rl].roadmark[0]
                                )
                if self._left_lanes_adjustable:
                    for ll in range(len(self.lanesections[ls].leftlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].leftlanes[ll]
                        ):
                            if ls == 0 and connected_lane_section is None:
                                set_zero_offset_to_lines(
                                    self.lanesections[ls].leftlanes[ll], seg_length
                                )
                            else:
                                for i_line in range(
                                    len(
                                        self.lanesections[ls]
                                        .leftlanes[ll]
                                        .roadmark[0]
                                        ._line
                                    )
                                ):
                                    prev_remainder = self._get_previous_remainder(
                                        connected_lane_section,
                                        i_line,
                                        "left",
                                        contact_point,
                                        ll,
                                        ls,
                                        "start",
                                    )
                                    self.lanesections[ls].leftlanes[ll].roadmark[
                                        0
                                    ]._line[i_line].adjust_remainder(
                                        seg_length, previous_remainder=prev_remainder
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls].leftlanes[ll].roadmark[0]
                                )
                if self._center_lane_adjustable:
                    if self._check_valid_mark_type(self.lanesections[ls].centerlane):
                        if ls == 0 and connected_lane_section is None:
                            set_zero_offset_to_lines(
                                self.lanesections[ls].centerlane, seg_length
                            )
                        else:
                            for i_line in range(
                                len(self.lanesections[ls].centerlane.roadmark[0]._line)
                            ):
                                prev_remainder = self._get_previous_remainder(
                                    connected_lane_section,
                                    i_line,
                                    "center",
                                    contact_point,
                                    None,
                                    ls,
                                    "start",
                                )
                                self.lanesections[ls].centerlane.roadmark[0]._line[
                                    i_line
                                ].adjust_remainder(
                                    seg_length, previous_remainder=prev_remainder
                                )
                            self._adjust_for_missing_line_offset(
                                self.lanesections[ls].centerlane.roadmark[0]
                            )

    def adjust_road_marks_from_end(
        self,
        total_road_length,
        connected_lane_section=None,
        contact_point=ContactPoint.end,
    ):
        """Adjusts road marks from the end of the road, based on the connected lane section.
        If connected_lane_section is not provided, the last roadmark will be placed with zero
        distance to the end of the road

        Parameters
        ----------
            total_road_length (float): total length of the road

            connected_lane_section (LaneSection): the lane section connected to the road
                Default: None

            contact_point (ContactPoint)
                Default: ContactPoint.end
        """
        contact_point = enumchecker(contact_point, ContactPoint)
        if connected_lane_section and not isinstance(
            connected_lane_section, LaneSection
        ):
            raise TypeError("connected_lane_section is not of type LaneSection")
        if not self.roadmarks_adjusted:
            self._validity_check_for_roadmark_adjustment()
            self.roadmarks_adjusted = True

            def set_zero_remainder_to_lines(lane, seg_length):
                for i_line in range(len(lane.roadmark[0]._line)):
                    lane.roadmark[0]._line[i_line].adjust_soffset(
                        seg_length, remainder=0
                    )

            for ls in range(len(self.lanesections) - 1, -1, -1):
                seg_length = self._get_seg_length(total_road_length, ls)
                if self._right_lanes_adjustable:
                    for rl in range(len(self.lanesections[ls].rightlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].rightlanes[rl]
                        ):
                            if (
                                ls == len(self.lanesections) - 1
                                and connected_lane_section is None
                            ):
                                set_zero_remainder_to_lines(
                                    self.lanesections[ls].rightlanes[rl], seg_length
                                )
                            else:
                                for i_line in range(
                                    len(
                                        self.lanesections[ls]
                                        .rightlanes[rl]
                                        .roadmark[0]
                                        ._line
                                    )
                                ):
                                    prev_remainder = self._get_previous_remainder(
                                        connected_lane_section,
                                        i_line,
                                        "right",
                                        contact_point,
                                        rl,
                                        ls,
                                        "end",
                                    )
                                    self.lanesections[ls].rightlanes[rl].roadmark[
                                        0
                                    ]._line[i_line].adjust_soffset(
                                        seg_length, previous_offset=prev_remainder
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls].rightlanes[rl].roadmark[0]
                                )
                if self._left_lanes_adjustable:
                    for ll in range(len(self.lanesections[ls].leftlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].leftlanes[ll]
                        ):
                            if (
                                ls == len(self.lanesections) - 1
                                and connected_lane_section is None
                            ):
                                set_zero_remainder_to_lines(
                                    self.lanesections[ls].leftlanes[ll], seg_length
                                )
                            else:
                                for i_line in range(
                                    len(
                                        self.lanesections[ls]
                                        .leftlanes[ll]
                                        .roadmark[0]
                                        ._line
                                    )
                                ):
                                    prev_remainder = self._get_previous_remainder(
                                        connected_lane_section,
                                        i_line,
                                        "left",
                                        contact_point,
                                        ll,
                                        ls,
                                        "end",
                                    )
                                    self.lanesections[ls].leftlanes[ll].roadmark[
                                        0
                                    ]._line[i_line].adjust_soffset(
                                        seg_length, previous_offset=prev_remainder
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls].leftlanes[ll].roadmark[0]
                                )

                if self._center_lane_adjustable:
                    if self._check_valid_mark_type(self.lanesections[ls].centerlane):
                        if (
                            ls == len(self.lanesections) - 1
                            and connected_lane_section is None
                        ):
                            set_zero_remainder_to_lines(
                                self.lanesections[ls].centerlane, seg_length
                            )
                        else:
                            for i_line in range(
                                len(self.lanesections[ls].centerlane.roadmark[0]._line)
                            ):
                                prev_remainder = self._get_previous_remainder(
                                    connected_lane_section,
                                    i_line,
                                    "center",
                                    contact_point,
                                    None,
                                    ls,
                                    "end",
                                )
                                self.lanesections[ls].centerlane.roadmark[0]._line[
                                    i_line
                                ].adjust_soffset(
                                    seg_length, previous_offset=prev_remainder
                                )
                            self._adjust_for_missing_line_offset(
                                self.lanesections[ls].centerlane.roadmark[0]
                            )

    def get_element(self):
        """returns the elementTree of Lanes"""
        element = ET.Element("lanes")
        self._add_additional_data_to_element(element)
        for l in self.laneoffsets:
            element.append(l.get_element())
        for l in self.lanesections:
            element.append(l.get_element())
        return element


class LaneOffset(XodrBase):
    """the LaneOffset class defines an overall lateral offset along the road, described as a third degree polynomial

    Parameters
    ----------
        s (float): s start coordinate of the elevation

        a (float): a coefficient of the polynomial

        b (float): b coefficient of the polynomial

        c (float): c coefficient of the polynomial

        d (float): d coefficient of the polynomial

    Attributes
    ----------
        s (float): s start coordinate of the elevation

        a (float): a coefficient of the polynomial

        b (float): b coefficient of the polynomial

        c (float): c coefficient of the polynomial

        d (float): d coefficient of the polynomial

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns the attributes of the class

    """

    def __init__(self, s=0, a=0, b=0, c=0, d=0):
        """initalize the LaneOffset class

        Parameters
        ----------
            s (float): s start coordinate of the LaneOffset

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

        """
        super().__init__()
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __eq__(self, other):
        if isinstance(other, LaneOffset) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        """returns the attributes of the LaneOffset"""

        retdict = {}
        retdict["s"] = str(self.s)
        retdict["a"] = str(self.a)
        retdict["b"] = str(self.b)
        retdict["c"] = str(self.c)
        retdict["d"] = str(self.d)
        return retdict

    def get_element(self):
        """returns the elementTree of the LaneOffset"""
        element = ET.Element("laneOffset", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class LaneSection(XodrBase):
    """Creates the LaneSection element of opendrive

    Parameters
    ----------
        s (float): start of lanesection

        centerlane (Lane): the centerline of the road

    Attributes
    ----------
        s (float): start of lanesection

        centerlane (Lane): the centerline of the road

        leftlanes (list of Lane): the lanes left to the center

        rightlanes (list of Lane): the lanes right to the center

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of class

        add_left_lane(Lane)
            adds a new lane to the left

        add_right_lane(Lane)
            adds a new lane to the right
    """

    def __init__(self, s, centerlane):
        """initalize the LaneSection

        Parameters
        ----------
            s (float): start of lanesection

            centerlane (Lane): the centerline of the road
        """
        super().__init__()
        self.s = s
        if not isinstance(centerlane, Lane):
            raise TypeError("centerlane input is not of type Lane")
        self.centerlane = centerlane
        self.centerlane._set_lane_id(0)
        self.leftlanes = []
        self.rightlanes = []
        self._left_id = 1
        self._right_id = -1

    def __eq__(self, other):
        if isinstance(other, LaneSection) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.centerlane == other.centerlane
                and self.leftlanes == other.leftlanes
                and self.rightlanes == other.rightlanes
            ):
                return True
        return False

    def add_left_lane(self, lane):
        """adds a lane to the left of the center, add from center outwards

        Parameters
        ----------
            lane (Lane): the lane to add
        """
        if not isinstance(lane, Lane):
            raise TypeError("lane input is not of type Lane")
        lane._set_lane_id(self._left_id)
        self._left_id += 1
        self.leftlanes.append(lane)
        return self

    def add_right_lane(self, lane):
        """adds a lane to the right of the center, add from center outwards

        Parameters
        ----------
            lane (Lane): the lane to add
        """
        if not isinstance(lane, Lane):
            raise TypeError("lane input is not of type Lane")
        lane._set_lane_id(self._right_id)
        self._right_id -= 1
        self.rightlanes.append(lane)
        return self

    def get_attributes(self):
        """returns the attributes of the Lane as a dict"""
        retdict = {}
        retdict["s"] = str(self.s)
        return retdict

    def get_element(self):
        """returns the elementTree of the WorldPostion"""
        element = ET.Element("laneSection", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self.leftlanes:
            left = ET.SubElement(element, "left")
            for l in reversed(self.leftlanes):
                left.append(l.get_element())

        center = ET.SubElement(element, "center")
        center.append(self.centerlane.get_element())

        if self.rightlanes:
            right = ET.SubElement(element, "right")
            for l in self.rightlanes:
                right.append(l.get_element())

        return element


class _poly3struct:
    def __init__(self, a=0, b=0, c=0, d=0, soffset=0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.soffset = soffset

    def __eq__(self, other):
        if isinstance(other, _poly3struct):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_width(self, s):
        width = (
            self.a
            + self.b * (s - self.soffset)
            + self.c * (s - self.soffset) ** 2
            + self.d * (s - self.soffset) ** 3
        )
        return width

    def get_attributes(self):
        polynomialdict = {}
        polynomialdict["a"] = str(self.a)
        polynomialdict["b"] = str(self.b)
        polynomialdict["c"] = str(self.c)
        polynomialdict["d"] = str(self.d)
        polynomialdict["sOffset"] = str(self.soffset)
        return polynomialdict


class Lane(XodrBase):
    """creates a Lane of opendrive

    the inputs are on the following format:
        f(s) = a + b*s + c*s^2 + d*s^3

    Parameters
    ----------

        lane_type (LaneType): type of lane
            Default: LaneType.driving

        a (float): a coefficient
            Default: 0

        b (float): b coefficient
            Default: 0

        c (float): c coefficient
            Default: 0

        d (float): d coefficient
            Default: 0

        soffset (float): soffset of lane
            Default: 0


    Attributes
    ----------
        lane_id (int): id of the lane (automatically assigned by LaneSection)

        lane_type (LaneType): type of lane

        a (float): a coefficient

        b (float): b coefficient

        c (float): c coefficient

        d (float): d coefficient

        soffset (float): soffset of lane

        roadmark (RoadMark): roadmarks related to the lane

        links (_Links): Lane links to the lane

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of class

        add_roadmark(roadmark)
            adds a new roadmark to the lane

        add_lane_width(a, b, c, d, soffset)
            adds an additional width element to the lane

        get_width(s)
            returns the width of the lane at s

        add_height(self, inner, outer=None, soffset=0)
            add_height adds a height entry to the lane to elevate it independent from the road elevation

        add_lane_material(self, friction, roughness=None, soffset=0, surface=None)
            add_lane_material adds a material description entry to the lane


    """

    def __init__(self, lane_type=LaneType.driving, a=0, b=0, c=0, d=0, soffset=0):
        """initalizes the Lane

        Parameters
        ----------

            lane_type (LaneType): type of lane
                Default: LaneType.driving

            a (float): a polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            b (float): b polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            c (float): c polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            d (float): d polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            soffset (float): soffset of lane renamed to s in case of centerlane
                Default: 0

        """
        super().__init__()
        self.lane_id = None
        self.lane_type = enumchecker(lane_type, LaneType)
        self.widths = []
        self.add_lane_width(a, b, c, d, soffset)

        self.soffset = soffset
        # TODO: enable multiple widths records per lane (only then soffset really makes sense! ASAM requires one width record to have sOffset=0)
        self.heights = (
            []
        )  # height entries to elevate the lane independent from the road elevation
        self.roadmark = []
        self.links = _Links()
        self.materials = []

    def __eq__(self, other):
        if isinstance(other, Lane) and super().__eq__(other):
            if (
                self.links == other.links
                and self.get_attributes() == other.get_attributes()
                and self.widths == other.widths
                and self.heights == other.heights
                and self.roadmark == other.roadmark
                and self.materials == other.materials
            ):
                return True
        return False

        # TODO: add more features to add for lane

    def add_lane_width(self, a=0, b=0, c=0, d=0, soffset=0):
        """adds an additional width element to the lane

        Parameters
        ----------
            a (float): a polynomial coefficient for width
                Default: 0

            b (float): b polynomial coefficient for width
                Default: 0

            c (float): c polynomial coefficient for width
                Default: 0

            d (float): d polynomial coefficient for width
                Default: 0

            soffset (float): soffset of lane renamed to s in case of centerlane
                Default: 0

        """
        self.widths.append(_poly3struct(a, b, c, d, soffset))

    def get_width(self, s):
        """function that calculates the width of a lane at a point s

        Note: no check that s is on the road can be made, that has to be taken care of by the user

        Parameters
        ----------
            s (float): the point where the width is wished

        Returns
        -------
            width (float): the width at point s
        """
        index_to_calc = 0
        for i in range(len(self.widths)):
            if s >= self.widths[i].soffset:
                index_to_calc = i
            else:
                break
        return self.widths[index_to_calc].get_width(s)

    def add_link(self, link_type, id):
        """adds a link to the lane section

        Parameters
        ----------
            link_type (str): type of link, successor or predecessor

            id (str/id): id of the linked lane
        """
        self.links.add_link(_Link(link_type, str(id)))
        return self

    def get_linked_lane_id(self, link_type):
        """adds a link to the lane section

        Parameters
        ----------
            link_type (str): type of link, successor or predecessor
        """
        for link in self.links.links:
            if link.link_type == link_type:
                return int(link.element_id)
        return None

    def _set_lane_id(self, lane_id):
        """set the lane id of the lane and set lane type to 'none' in case of centerlane"""
        self.lane_id = lane_id
        if self.lane_id == 0:
            self.lane_type = LaneType.none

    def add_roadmark(self, roadmark):
        """add_roadmark adds a roadmark to the lane

        Parameters
        ----------
            roadmark (RoadMark): roadmark of the lane

        """
        if not isinstance(roadmark, RoadMark):
            raise TypeError("roadmark input is not of type RoadMark")
        self.roadmark.append(roadmark)
        return self

    def add_height(self, inner, outer=None, soffset=0):
        """add_height adds a height entry to the lane to elevate it independent from the road elevation

        Parameters
        ----------
            inner (float): inner height

            outer (float): outer height (if not provided, inner height is used)
                Default: None

            s_offset (float): s offset of the height record
                Default: 0

        """
        heightdict = {}
        heightdict["inner"] = str(inner)
        if outer is not None:
            heightdict["outer"] = str(outer)
        else:
            heightdict["outer"] = str(inner)
        heightdict["sOffset"] = str(soffset)

        self.heights.append(heightdict)
        return self

    def add_lane_material(self, friction, roughness=None, soffset=0, surface=None):
        """add_lane_material adds a material description entry to the lane
        Parameters
        ----------
            friction (float): friction coefficient

            roughness (float): roughness, for example, for sound and motion systems
                Default: None

            sOffset (float): s offset of the material
                Default: 0

            surface (str): surface material code, depending on application
                Default: None

        """
        materialdict = {}
        materialdict["friction"] = str(friction)
        if roughness is not None:
            materialdict["roughness"] = str(roughness)
        materialdict["sOffset"] = str(soffset)
        if surface is not None:
            materialdict["surface"] = str(surface)
        self.materials.append(materialdict)
        return self

    def get_attributes(self):
        """returns the attributes of the Lane as a dict"""
        retdict = {}
        if self.lane_id == None:
            raise ValueError("lane id is not set correctly.")
        retdict["id"] = str(self.lane_id)
        retdict["type"] = enum2str(self.lane_type)
        retdict["level"] = "false"
        return retdict

    def get_element(self):
        """returns the elementTree of the Lane"""
        element = ET.Element("lane", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        # according to standard if lane is centerlane it should
        # not have a width record and omit the link record
        if self.lane_id != 0:
            element.append(self.links.get_element())
            for w in sorted(self.widths, key=lambda x: x.soffset):
                ET.SubElement(element, "width", attrib=w.get_attributes())
        # use polynomial dict for laneOffset in case of center lane (only if values provided)
        # removed, should not be here..
        # elif any([self.a,self.b,self.c,self.d]):
        #     polynomialdict['s'] = polynomialdict.pop('sOffset')
        #     ET.SubElement(element,'laneOffset',attrib=polynomialdict)

        if self.roadmark:
            for r in sorted(self.roadmark, key=lambda x: x.soffset):
                element.append(r.get_element())

        for height in self.heights:
            ET.SubElement(element, "height", attrib=height)

        for material in sorted(self.materials, key=lambda x: x["sOffset"]):
            ET.SubElement(element, "material", attrib=material)

        return element


class RoadMark(XodrBase):
    """creates a RoadMark of opendrive

    Parameters
    ----------
        marking_type (RoadMarkType): the type of marking

        width (float): with of the line
            Default: None
        length (float): length of the line
            Default: 0
        toffset (float): offset in t
            Default: 0
        soffset (float): offset in s
            Default: 0
        rule (MarkRule): mark rule (optional)

        color (RoadMarkColor): color of line (optional)

    Attributes
    ----------
        marking_type (str): the type of marking

        width (float): with of the line

        length (float): length of the line
            Default: 0
        toffset (float): offset in t
            Default: 0
        soffset (float): offset in s
            Default: 0
        rule (MarkRule): mark rule (optional)

        color (RoadMarkColor): color of line (optional)

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

        add_roadmark(roadmark)
            adds a new roadmark to the lane

    """

    def __init__(
        self,
        marking_type,
        width=None,
        length=None,
        space=None,
        toffset=None,
        soffset=0,
        rule=None,
        color=RoadMarkColor.standard,
        marking_weight=RoadMarkWeight.standard,
        height=0.02,
        laneChange=None,
    ):
        """initializes the RoadMark

        Parameters
        ----------
            marking_type (str): the type of marking

            width (float): width of the marking / line
                Default: None
            length (float): length of the visible, marked part of the line (used for broken lines)
                Default: None
            space (float): length of the invisible, unmarked part of the line (used for broken lines)
                Default: None
            toffset (float): offset in t
                Default: None
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)
                Default: None
            color (RoadMarkColor): color of marking
                Default: 'standard'
            marking_weight (str): the weight of marking
                Default: standard
            height (float): thickness of marking
                Default: 0.02
            laneChange (LaneChange): indicates direction in which lane change is allowed
                Default: none

        """
        super().__init__()
        # required arguments - must be provided by user
        self.marking_type = enumchecker(marking_type, RoadMarkType)

        # required arguments - must be provided by user or taken from defaults
        self.marking_weight = enumchecker(marking_weight, RoadMarkWeight)
        self.color = enumchecker(color, RoadMarkColor, True)
        self.soffset = soffset
        self.height = height
        self.laneChange = enumchecker(laneChange, LaneChange, True)

        # optional arguments - roadmark is valid without them being defined
        self.width = width
        self.length = length
        self.space = space
        self.toffset = toffset
        self.rule = rule

        # TODO: there may be more line child elements per roadmark, which is currently unsupported
        self._line = []
        self._explicit_line = []
        # check if arguments were passed that require line child element
        if any([length, space, toffset, rule]):
            # set defaults in case no values were provided
            # values for broken lines
            if marking_type == RoadMarkType.broken:
                self.length = length or 3
                self.space = space or 3
            # values for solid lines
            elif marking_type == RoadMarkType.solid:
                self.length = length or 3
                self.space = space or 0
            # create empty line if arguments are missing
            else:
                self.length = length or 0
                self.space = length or 0
                print(
                    "No defaults for arguments 'space' and 'length' for roadmark type",
                    enum2str(marking_type),
                    "available and no values were passed. Creating an empty roadmark.",
                )
            # set remaining defaults
            self.width = width or 0.2
            self.toffset = toffset or 0
            self.rule = rule or MarkRule.none
            self._line.append(
                RoadLine(
                    self.width,
                    self.length,
                    self.space,
                    self.toffset,
                    0,
                    self.rule,
                    self.color,
                )
            )

    def __eq__(self, other):
        if isinstance(other, RoadMark) and super().__eq__(other):
            if (
                self._line == other._line
                and self._explicit_line == other._explicit_line
                and self.get_attributes() == other.get_attributes()
                and self.marking_type == other.marking_type
            ):
                return True
        return False

    def add_specific_road_line(self, line):
        """function to add your own roadline to the RoadMark, to use for multi line type of roadmarks,

        Parameters
        ----------
            line (RoadLine): the roadline to add

        """
        if not isinstance(line, RoadLine):
            raise TypeError("line input is not of type RoadLine")
        self._line.append(line)
        return self

    def add_explicit_road_line(self, line):
        """function to add a explicit roadline to the RoadMark,

        Parameters
        ----------
            line (ExplicitRoadLine): the roadline to add

        """
        if not isinstance(line, ExplicitRoadLine):
            raise TypeError("line input is not of type RoadLine")
        self._explicit_line.append(line)
        return self

    def get_attributes(self):
        """returns the attributes of the RoadMark as a dict"""
        retdict = {}
        retdict["sOffset"] = str(self.soffset)
        retdict["type"] = enum2str(self.marking_type)
        retdict["weight"] = enum2str(self.marking_weight)
        retdict["color"] = enum2str(self.color)
        retdict["height"] = str(self.height)
        if self.width is not None:
            retdict["width"] = str(self.width)
        if self.laneChange is not None:
            retdict["laneChange"] = enum2str(self.laneChange)
        return retdict

    def get_element(self):
        """returns the elementTree of the RoadMark"""
        element = ET.Element("roadMark", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self._line:
            attribs = {"name": enum2str(self.marking_type)}
            if self.width is not None:
                attribs["width"] = str(self.width)
            else:
                offsets = [x.toffset for x in self._line]

                attribs["width"] = str(
                    max(offsets)
                    - min(offsets)
                    + sum(
                        [
                            x.width
                            for x in self._line
                            if x.toffset in [max(offsets), min(offsets)]
                        ]
                    )
                )
            typeelement = ET.SubElement(
                element,
                "type",
                attrib=attribs,
            )
            for l in self._line:
                typeelement.append(l.get_element())
        if self._explicit_line:
            typeelement = ET.SubElement(
                element,
                "explicit",
            )
            for l in self._explicit_line:
                typeelement.append(l.get_element())
        return element


class RoadLine(XodrBase):
    """creates a Line type of to be used in roadmark

    Parameters
    ----------
        width (float): with of the line
            Default: 0
        length (float): length of the line
            Default: 0
        space (float): length of space between (broken) lines
            Default: 0
        toffset (float): offset in t
            Default: 0
        soffset (float): offset in s
            Default: 0
        rule (MarkRule): mark rule (optional)

        color (RoadMarkColor): color of line (optional)

    Attributes
    ----------
        length (float): length of the line

        space (float): length of space between (broken) lines

        toffset (float): offset in t

        soffset (float): offset in s

        rule (MarkRule): mark rule

        width (float): with of the line

        color (RoadMarkColor): color of line

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

    """

    # TODO: check this for 1.5
    def __init__(
        self, width=0, length=0, space=0, toffset=0, soffset=0, rule=None, color=None
    ):
        """initalizes the RoadLine

        Parameters
        ----------
            width (float): with of the line
                Default: 0
            length (float): length of the line
                Default: 0
            space (float): length of space between (broken) lines
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line (optional)


        """
        super().__init__()
        self.length = length
        self.space = space
        self.toffset = toffset
        self.rule = enumchecker(rule, MarkRule, True)
        self.soffset = soffset
        self.width = width
        self.color = enumchecker(color, RoadMarkColor, True)
        self._remainder = 0

    def __eq__(self, other):
        if isinstance(other, RoadLine) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def adjust_remainder(self, total_length, soffset=None, previous_remainder=None):
        """adjust_remainder is used to calculated and set the remainer of a broken mark for offset adjustments

        Parameters
        ----------
            total_length (float): the lenght of the lanesection where this line is valid

            soffset (float): the wanted soffset (at beginning of line), use this or previous remainder
                Default: use defined in class

            previous_remainder (float): the remainder of the previous line, use this or soffset
                Default: use defined in class
        """
        if soffset and previous_remainder:
            raise ToManyOptionalArguments(
                "for adjusting line lengths, use only soffset or previous_remainder."
            )
        if soffset is not None:
            self.soffset = soffset
        if previous_remainder is not None:
            self.soffset = self.space - previous_remainder
        self._remainder = self._calculate_remainder_of_line(self.soffset, total_length)

    def shift_soffset(self):
        """shifts the soffset one period"""
        self.soffset += self.space + self.length

    def adjust_soffset(self, total_length, remainder=None, previous_offset=None):
        """adjust_soffset is used to calculated and set the soffset of a broken mark for offset adjustments

        Parameters
        ----------
            total_length (float): the lenght of the lanesection where this line is valid

            remainder (float): the wanted remainder ("soffset" at end of line), use this or previous_offset
                Default: use defined in class

            previous_offset (float): the soffset of the previous line, use this or remainder
                Default: use defined in class
        """
        if remainder and previous_offset:
            raise ToManyOptionalArguments(
                "for adjusting line lengths, use only soffset or previous_remainder."
            )
        if remainder is not None:
            self._remainder = remainder
        if previous_offset is not None:
            self._remainder = self.space - previous_offset
        self.soffset = self._calculate_remainder_of_line(self._remainder, total_length)

    def _calculate_remainder_of_line(self, soffset, total_length):
        n = (total_length - soffset + self.space) / (self.space + self.length)
        return (
            total_length
            - soffset
            - np.floor(n) * (self.space + self.length)
            + self.space
        )

    def get_attributes(self):
        """returns the attributes of the Lane as a dict"""
        retdict = {}
        retdict["length"] = str(self.length)
        retdict["space"] = str(self.space)
        retdict["tOffset"] = str(self.toffset)
        retdict["width"] = str(self.width)
        retdict["sOffset"] = str(self.soffset)
        # if self.color:
        # retdict['color'] = enum2str(self.color)
        if self.rule:
            retdict["rule"] = enum2str(self.rule)
        return retdict

    def get_element(self):
        """returns the elementTree of the RoadLine"""
        element = ET.Element("line", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class ExplicitRoadLine(XodrBase):
    """creates a Explicit RoadLine type of to be used in roadmark

    Parameters
    ----------
        width (float): with of the line
            Default: 0
        length (float): length of the line
            Default: 0
        toffset (float): offset in t
            Default: 0
        soffset (float): offset in s
            Default: 0
        rule (MarkRule): mark rule (optional)

    Attributes
    ----------
        length (float): length of the line

        toffset (float): offset in t

        soffset (float): offset in s

        rule (MarkRule): mark rule

        width (float): with of the line

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

    """

    # TODO: check this for 1.5
    def __init__(self, width=0, length=0, toffset=0, soffset=0, rule=None):
        """initalizes the RoadLine

        Parameters
        ----------
            width (float): with of the line
                Default: 0
            length (float): length of the line
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

        """
        super().__init__()
        self.length = length
        self.toffset = toffset
        self.rule = enumchecker(rule, MarkRule, True)
        self.soffset = soffset
        self.width = width
        self._remainder = 0

    def __eq__(self, other):
        if isinstance(other, ExplicitRoadLine) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        """returns the attributes of the Lane as a dict"""
        retdict = {}
        retdict["length"] = str(self.length)
        retdict["tOffset"] = str(self.toffset)
        retdict["width"] = str(self.width)
        retdict["sOffset"] = str(self.soffset)
        if self.rule:
            retdict["rule"] = enum2str(self.rule)
        return retdict

    def get_element(self):
        """returns the elementTree of the WorldPostion"""
        element = ET.Element("line", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element
