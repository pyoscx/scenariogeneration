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

import numpy as np

from ..helpers import enum2str
from .enumerations import (
    ContactPoint,
    LaneChange,
    LaneType,
    MarkRule,
    RoadMarkColor,
    RoadMarkType,
    RoadMarkWeight,
    enumchecker,
)
from .exceptions import ToManyOptionalArguments
from .links import LaneLinker, _Link, _Links
from .utils import XodrBase


class Lanes(XodrBase):
    """Create the Lanes element of OpenDRIVE.

    This class represents the lanes of a road, including lane sections and
    lane offsets.

    Attributes
    ----------
    lanesections : list of LaneSection
        A list of all lane sections in the road.
    laneoffsets : list of LaneOffset
        A list of lane offsets applied to the road.
    roadmarks_adjusted : bool
        Indicates whether roadmarks have been adjusted.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the class.
    add_lanesection(lanesection, lanelinks=None)
        Adds a lane section to the Lanes object.
    add_laneoffset(laneoffset)
        Adds a lane offset to the Lanes object.
    adjust_road_marks_from_start(total_road_length,
        connected_lane_section=None, contact_point=ContactPoint.end)
        Adjusts road marks from the start of the road.
    adjust_road_marks_from_end(total_road_length, connected_lane_section=None,
        contact_point=ContactPoint.end)
        Adjusts road marks from the end of the road.
    """

    def __init__(self) -> None:
        """Initialize the `Lanes` class.

        This constructor initializes the `Lanes` object with default
        values for lane sections, lane offsets, and roadmark adjustment
        status.

        Attributes
        ----------
        lanesections : list of LaneSection
            A list of all lane sections in the road.
        laneoffsets : list of LaneOffset
            A list of lane offsets applied to the road.
        roadmarks_adjusted : bool
            Indicates whether roadmarks have been adjusted.

        Returns
        -------
        None
        """
        super().__init__()
        """Initalize Lanes."""
        self.lanesections = []
        self.laneoffsets = []
        self.roadmarks_adjusted = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Lanes) and super().__eq__(other):
            if (
                self.laneoffsets == other.laneoffsets
                and self.lanesections == other.lanesections
            ):
                return True
        return False

    def add_lanesection(
        self,
        lanesection: "LaneSection",
        lanelinks: Optional[Union["LaneLinker", list["LaneLinker"]]] = None,
    ) -> "Lanes":
        """Add a lane section to the `Lanes` object.

        This method adds a `LaneSection` to the `Lanes` object and
        optionally links lanes using a `LaneLinker`.

        Parameters
        ----------
        lanesection : LaneSection
            A `LaneSection` object to add to the `Lanes` object.
        lanelinks : LaneLinker or list of LaneLinker, optional
            A `LaneLinker` or a list of `LaneLinker` objects to link '
            lanes. Default is None.

        Returns
        -------
        Lanes
            The updated `Lanes` object.

        Raises
        ------
        TypeError
            If `lanesection` is not of type `LaneSection` or if
            `lanelinks` contains objects that are not of type
            `LaneLinker`.
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
                        link.predecessor.add_link(
                            "successor", link.successor.lane_id
                        )
                        link.successor.add_link(
                            "predecessor", link.predecessor.lane_id
                        )
                        link.used = True

        self.lanesections.append(lanesection)
        return self

    def add_laneoffset(self, laneoffset: "LaneOffset") -> "Lanes":
        """Add a lane offset to the `Lanes` object.

        This method adds a `LaneOffset` to the `Lanes` object.

        Parameters
        ----------
        laneoffset : LaneOffset
            A `LaneOffset` object to add to the `Lanes` object.

        Returns
        -------
        Lanes
            The updated `Lanes` object.

        Raises
        ------
        TypeError
            If `laneoffset` is not of type `LaneOffset`.
        """
        if not isinstance(laneoffset, LaneOffset):
            raise TypeError(
                "add_laneoffset requires a LaneOffset as input, not "
                + str(type(laneoffset))
            )
        self.laneoffsets.append(laneoffset)
        return self

    def _check_valid_mark_type(self, lane: "Lane") -> bool:
        """Check if the lane's roadmark can be adjusted.

        This method verifies whether the roadmark type of the given lane
        is valid for adjustment.

        Parameters
        ----------
        lane : Lane
            The lane whose roadmark should be checked.

        Returns
        -------
        bool
            True if the roadmark can be adjusted, False otherwise.
        """
        return (
            lane.roadmark[0].marking_type == RoadMarkType.broken
            or lane.roadmark[0].marking_type == RoadMarkType.broken_broken
        )

    def _adjust_for_missing_line_offset(self, roadmark: "RoadMark") -> None:
        """Add an explicit line if the offset is less than 0 ( for adjusting
        from the start) or longer than the space between lines (for adjusting
        from the end).

        Parameters
        ----------
        roadmark : RoadMark
            The roadmark to be adjusted.

        Returns
        -------
        None
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

    def _validity_check_for_roadmark_adjustment(self) -> None:
        """Perform validity checks to determine if the lanes' roadmarks can be
        adjusted.

        This method checks the right, left, and center lanes to ensure
        their roadmarks meet the criteria for adjustment.

        Returns
        -------
        None
        """
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
        connected_lane_section: "LaneSection",
        i_line: int,
        lane_side: str,
        contact_point: "ContactPoint",
        lane_index: Optional[int],
        lane_section_index: int,
        start_or_end: str,
    ) -> float:
        """Get the remainder of a lane marking from a connecting lane section.

        This helper method calculates the remainder of a lane marking for
        length adjustment based on the connected lane section.

        Parameters
        ----------
        connected_lane_section : LaneSection
            The connected lane section (on another road).
        i_line : int
            The index of the line (`roadmark._line`).
        lane_side : str
            The side of the lane ("left", "right", or "center").
        contact_point : ContactPoint
            The contact point of the `connected_lane_section`.
        lane_index : int, optional
            The lane index of the desired lane.
        lane_section_index : int
            The index of the lane section.
        start_or_end : str
            Indicates whether the adjustment is done from the start or end
            of the road.

        Returns
        -------
        float
            The remainder of the previous lane section.
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
                prev_remainder = (
                    neighboring_lane.roadmark[0]._line[i_line]._remainder
                )
            else:
                prev_remainder = (
                    neighboring_lane.roadmark[0]._line[i_line].soffset
                )
        return prev_remainder

    def _get_seg_length(
        self, total_road_length: float, lane_section_index: int
    ) -> float:
        """Calculate the length of a lane section.

        This helper method determines the length of a specific lane
        section based on the total road length and the index of the lane
        section.

        Parameters
        ----------
        total_road_length : float
            The total length of the road.
        lane_section_index : int
            The index of the desired lane section.

        Returns
        -------
        float
            The length of the specified lane section.
        """
        if len(self.lanesections) == 1:
            seg_length = total_road_length
        elif lane_section_index == 0:
            seg_length = self.lanesections[1].s
        elif lane_section_index == len(self.lanesections) - 1:
            seg_length = (
                total_road_length - self.lanesections[lane_section_index].s
            )
        else:
            seg_length = (
                self.lanesections[lane_section_index + 1].s
                - self.lanesections[lane_section_index].s
            )
        return seg_length

    def adjust_road_marks_from_start(
        self,
        total_road_length: float,
        connected_lane_section: Optional["LaneSection"] = None,
        contact_point: "ContactPoint" = ContactPoint.end,
    ) -> None:
        """Adjust road marks from the start of the road.

        This method adjusts road marks based on the connected lane
        section. If `connected_lane_section` is not provided, the last
        roadmark will be placed with zero distance to the start of the
        road.

        Parameters
        ----------
        total_road_length : float
            The total length of the road.
        connected_lane_section : LaneSection, optional
            The lane section connected to the road. Default is None.
        contact_point : ContactPoint, optional
            The contact point of the `connected_lane_section`. Default is
            `ContactPoint.end`.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If `connected_lane_section` is not of type `LaneSection`.
        """
        contact_point = enumchecker(contact_point, ContactPoint)
        if connected_lane_section and not isinstance(
            connected_lane_section, LaneSection
        ):
            raise TypeError(
                "connected_lane_section is not of type LaneSection"
            )
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
                                    self.lanesections[ls].rightlanes[rl],
                                    seg_length,
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
                                    prev_remainder = (
                                        self._get_previous_remainder(
                                            connected_lane_section,
                                            i_line,
                                            "right",
                                            contact_point,
                                            rl,
                                            ls,
                                            "start",
                                        )
                                    )
                                    self.lanesections[ls].rightlanes[
                                        rl
                                    ].roadmark[0]._line[
                                        i_line
                                    ].adjust_remainder(
                                        seg_length,
                                        previous_remainder=prev_remainder,
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls]
                                    .rightlanes[rl]
                                    .roadmark[0]
                                )
                if self._left_lanes_adjustable:
                    for ll in range(len(self.lanesections[ls].leftlanes)):
                        if self._check_valid_mark_type(
                            self.lanesections[ls].leftlanes[ll]
                        ):
                            if ls == 0 and connected_lane_section is None:
                                set_zero_offset_to_lines(
                                    self.lanesections[ls].leftlanes[ll],
                                    seg_length,
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
                                    prev_remainder = (
                                        self._get_previous_remainder(
                                            connected_lane_section,
                                            i_line,
                                            "left",
                                            contact_point,
                                            ll,
                                            ls,
                                            "start",
                                        )
                                    )
                                    self.lanesections[ls].leftlanes[
                                        ll
                                    ].roadmark[0]._line[
                                        i_line
                                    ].adjust_remainder(
                                        seg_length,
                                        previous_remainder=prev_remainder,
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls]
                                    .leftlanes[ll]
                                    .roadmark[0]
                                )
                if self._center_lane_adjustable:
                    if self._check_valid_mark_type(
                        self.lanesections[ls].centerlane
                    ):
                        if ls == 0 and connected_lane_section is None:
                            set_zero_offset_to_lines(
                                self.lanesections[ls].centerlane, seg_length
                            )
                        else:
                            for i_line in range(
                                len(
                                    self.lanesections[ls]
                                    .centerlane.roadmark[0]
                                    ._line
                                )
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
                                self.lanesections[ls].centerlane.roadmark[
                                    0
                                ]._line[i_line].adjust_remainder(
                                    seg_length,
                                    previous_remainder=prev_remainder,
                                )
                            self._adjust_for_missing_line_offset(
                                self.lanesections[ls].centerlane.roadmark[0]
                            )

    def adjust_road_marks_from_end(
        self,
        total_road_length: float,
        connected_lane_section: Optional["LaneSection"] = None,
        contact_point: "ContactPoint" = ContactPoint.end,
    ) -> None:
        """Adjust road marks from the end of the road.

        This method adjusts road marks based on the connected lane
        section. If `connected_lane_section` is not provided, the last
        roadmark will be placed with zero distance to the end of the road.

        Parameters
        ----------
        total_road_length : float
            The total length of the road.
        connected_lane_section : LaneSection, optional
            The lane section connected to the road. Default is None.
        contact_point : ContactPoint, optional
            The contact point of the `connected_lane_section`. Default is
            `ContactPoint.end`.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If `connected_lane_section` is not of type `LaneSection`.
        """
        contact_point = enumchecker(contact_point, ContactPoint)
        if connected_lane_section and not isinstance(
            connected_lane_section, LaneSection
        ):
            raise TypeError(
                "connected_lane_section is not of type LaneSection"
            )
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
                                    self.lanesections[ls].rightlanes[rl],
                                    seg_length,
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
                                    prev_remainder = (
                                        self._get_previous_remainder(
                                            connected_lane_section,
                                            i_line,
                                            "right",
                                            contact_point,
                                            rl,
                                            ls,
                                            "end",
                                        )
                                    )
                                    self.lanesections[ls].rightlanes[
                                        rl
                                    ].roadmark[0]._line[i_line].adjust_soffset(
                                        seg_length,
                                        previous_offset=prev_remainder,
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls]
                                    .rightlanes[rl]
                                    .roadmark[0]
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
                                    self.lanesections[ls].leftlanes[ll],
                                    seg_length,
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
                                    prev_remainder = (
                                        self._get_previous_remainder(
                                            connected_lane_section,
                                            i_line,
                                            "left",
                                            contact_point,
                                            ll,
                                            ls,
                                            "end",
                                        )
                                    )
                                    self.lanesections[ls].leftlanes[
                                        ll
                                    ].roadmark[0]._line[i_line].adjust_soffset(
                                        seg_length,
                                        previous_offset=prev_remainder,
                                    )
                                self._adjust_for_missing_line_offset(
                                    self.lanesections[ls]
                                    .leftlanes[ll]
                                    .roadmark[0]
                                )

                if self._center_lane_adjustable:
                    if self._check_valid_mark_type(
                        self.lanesections[ls].centerlane
                    ):
                        if (
                            ls == len(self.lanesections) - 1
                            and connected_lane_section is None
                        ):
                            set_zero_remainder_to_lines(
                                self.lanesections[ls].centerlane, seg_length
                            )
                        else:
                            for i_line in range(
                                len(
                                    self.lanesections[ls]
                                    .centerlane.roadmark[0]
                                    ._line
                                )
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
                                self.lanesections[ls].centerlane.roadmark[
                                    0
                                ]._line[i_line].adjust_soffset(
                                    seg_length, previous_offset=prev_remainder
                                )
                            self._adjust_for_missing_line_offset(
                                self.lanesections[ls].centerlane.roadmark[0]
                            )

    def get_element(self) -> ET.Element:
        """Returns the ElementTree representation of the `Lanes` object.

        This method generates an XML representation of the `Lanes` object,
        including its lane sections and lane offsets.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the `Lanes` object.
        """
        element = ET.Element("lanes")
        self._add_additional_data_to_element(element)
        for l in self.laneoffsets:
            element.append(l.get_element())
        for l in self.lanesections:
            element.append(l.get_element())
        return element


class LaneOffset(XodrBase):
    """Define an overall lateral offset along the road as a third-degree
    polynomial.

    Parameters
    ----------
    s : float
        The `s` start coordinate of the lane offset.
    a : float
        The `a` coefficient of the polynomial.
    b : float
        The `b` coefficient of the polynomial.
    c : float
        The `c` coefficient of the polynomial.
    d : float
        The `d` coefficient of the polynomial.

    Attributes
    ----------
    s : float
        The `s` start coordinate of the lane offset.
    a : float
        The `a` coefficient of the polynomial.
    b : float
        The `b` coefficient of the polynomial.
    c : float
        The `c` coefficient of the polynomial.
    d : float
        The `d` coefficient of the polynomial.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the class.
    get_attributes()
        Returns the attributes of the class as a dictionary.
    """

    def __init__(
        self,
        s: float = 0,
        a: float = 0,
        b: float = 0,
        c: float = 0,
        d: float = 0,
    ) -> None:
        """Initialize the `LaneOffset` class.

        Parameters
        ----------
        s : float, optional
            The `s` start coordinate of the lane offset. Default is 0.
        a : float, optional
            The `a` coefficient of the polynomial. Default is 0.
        b : float, optional
            The `b` coefficient of the polynomial. Default is 0.
        c : float, optional
            The `c` coefficient of the polynomial. Default is 0.
        d : float, optional
            The `d` coefficient of the polynomial. Default is 0.

        Returns
        -------
        None
        """
        super().__init__()
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LaneOffset) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict:
        """Return the attributes of the `LaneOffset` as a dictionary.

        This method returns the attributes of the `LaneOffset` object,
        including its polynomial coefficients and the `s` start
        coordinate.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `LaneOffset`.
        """

        retdict = {}
        retdict["s"] = str(self.s)
        retdict["a"] = str(self.a)
        retdict["b"] = str(self.b)
        retdict["c"] = str(self.c)
        retdict["d"] = str(self.d)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `LaneOffset`.

        This method generates an XML representation of the `LaneOffset`
        object, including its attributes.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the `LaneOffset`.
        """
        element = ET.Element("laneOffset", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class LaneSection(XodrBase):
    """Create the LaneSection element of OpenDRIVE.

    This class represents a lane section, including its center lane,
    left lanes, and right lanes.

    Parameters
    ----------
    s : float
        The `s` start coordinate of the lane section.
    centerlane : Lane
        The center lane of the road.

    Attributes
    ----------
    s : float
        The `s` start coordinate of the lane section.
    centerlane : Lane
        The center lane of the road.
    leftlanes : list of Lane
        The lanes to the left of the center lane.
    rightlanes : list of Lane
        The lanes to the right of the center lane.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the class.
    get_attributes()
        Returns the attributes of the class as a dictionary.
    add_left_lane(lane)
        Adds a new lane to the left of the center lane.
    add_right_lane(lane)
        Adds a new lane to the right of the center lane.
    """

    def __init__(self, s: float, centerlane: "Lane") -> None:
        """Initialize the `LaneSection` class.

        Parameters
        ----------
        s : float
            The `s` start coordinate of the lane section.
        centerlane : Lane
            The center lane of the road.

        Raises
        ------
        TypeError
            If `centerlane` is not of type `Lane`.
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LaneSection) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.centerlane == other.centerlane
                and self.leftlanes == other.leftlanes
                and self.rightlanes == other.rightlanes
            ):
                return True
        return False

    def add_left_lane(self, lane: "Lane") -> "LaneSection":
        """Add a lane to the left of the center lane.

        Parameters
        ----------
        lane : Lane
            The lane to add.

        Returns
        -------
        LaneSection
            The updated `LaneSection` object.

        Raises
        ------
        TypeError
            If `lane` is not of type `Lane`.
        """
        if not isinstance(lane, Lane):
            raise TypeError("lane input is not of type Lane")
        lane._set_lane_id(self._left_id)
        self._left_id += 1
        self.leftlanes.append(lane)
        return self

    def add_right_lane(self, lane: "Lane") -> "LaneSection":
        """Add a lane to the right of the center lane.

        Parameters
        ----------
        lane : Lane
            The lane to add.

        Returns
        -------
        LaneSection
            The updated `LaneSection` object.

        Raises
        ------
        TypeError
            If `lane` is not of type `Lane`.
        """
        if not isinstance(lane, Lane):
            raise TypeError("lane input is not of type Lane")
        lane._set_lane_id(self._right_id)
        self._right_id -= 1
        self.rightlanes.append(lane)
        return self

    def get_attributes(self) -> dict:
        """Return the attributes of the `LaneSection` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `LaneSection`.
        """
        retdict = {}
        retdict["s"] = str(self.s)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `LaneSection`.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the `LaneSection`.
        """
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
    """Represent a third-degree polynomial structure.

    This class is used to define a polynomial of the form:
        f(s) = a + b * (s - soffset) + c * (s - soffset)^2 + d * (s - soffset)^3

    Parameters
    ----------
    a : float, optional
        The `a` coefficient of the polynomial. Default is 0.
    b : float, optional
        The `b` coefficient of the polynomial. Default is 0.
    c : float, optional
        The `c` coefficient of the polynomial. Default is 0.
    d : float, optional
        The `d` coefficient of the polynomial. Default is 0.
    soffset : float, optional
        The `s` offset for the polynomial. Default is 0.

    Attributes
    ----------
    a : float
        The `a` coefficient of the polynomial.
    b : float
        The `b` coefficient of the polynomial.
    c : float
        The `c` coefficient of the polynomial.
    d : float
        The `d` coefficient of the polynomial.
    soffset : float
        The `s` offset for the polynomial.

    Methods
    -------
    get_width(s)
        Calculate the width at a given `s` value.
    get_attributes()
        Return the attributes of the polynomial as a dictionary.
    """

    def __init__(
        self,
        a: float = 0,
        b: float = 0,
        c: float = 0,
        d: float = 0,
        soffset: float = 0,
    ) -> None:
        """Initialize the `_poly3struct` class.

        Parameters
        ----------
        a : float, optional
            The `a` coefficient of the polynomial. Default is 0.
        b : float, optional
            The `b` coefficient of the polynomial. Default is 0.
        c : float, optional
            The `c` coefficient of the polynomial. Default is 0.
        d : float, optional
            The `d` coefficient of the polynomial. Default is 0.
        soffset : float, optional
            The `s` offset for the polynomial. Default is 0.
        """
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.soffset = soffset

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _poly3struct):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_width(self, s: float) -> float:
        """Calculate the width at a given `s` value.

        Parameters
        ----------
        s : float
            The `s` value at which to calculate the width.

        Returns
        -------
        float
            The width at the given `s` value.
        """
        width = (
            self.a
            + self.b * (s - self.soffset)
            + self.c * (s - self.soffset) ** 2
            + self.d * (s - self.soffset) ** 3
        )
        return width

    def get_attributes(self) -> dict:
        """Return the attributes of the polynomial as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the polynomial.
        """
        polynomialdict = {}
        polynomialdict["a"] = str(self.a)
        polynomialdict["b"] = str(self.b)
        polynomialdict["c"] = str(self.c)
        polynomialdict["d"] = str(self.d)
        polynomialdict["sOffset"] = str(self.soffset)
        return polynomialdict


class Lane(XodrBase):
    """Create a Lane element of OpenDRIVE.

    The lane is defined using a polynomial of the form:
        f(s) = a + b * s + c * s^2 + d * s^3

    Parameters
    ----------
    lane_type : LaneType, optional
        The type of the lane. Default is `LaneType.driving`.
    a : float, optional
        The `a` coefficient of the polynomial. Default is 0.
    b : float, optional
        The `b` coefficient of the polynomial. Default is 0.
    c : float, optional
        The `c` coefficient of the polynomial. Default is 0.
    d : float, optional
        The `d` coefficient of the polynomial. Default is 0.
    soffset : float, optional
        The `s` offset of the lane. Default is 0.

    Attributes
    ----------
    lane_id : int
        The ID of the lane (automatically assigned by `LaneSection`).
    lane_type : LaneType
        The type of the lane.
    widths : list of _poly3struct
        The width elements of the lane.
    heights : list of dict
        The height entries of the lane.
    roadmark : list of RoadMark
        The roadmarks associated with the lane.
    links : _Links
        The lane links associated with the lane.
    materials : list of dict
        The material descriptions of the lane.

    Methods
    -------
    add_lane_width(a, b, c, d, soffset)
        Add an additional width element to the lane.
    get_width(s)
        Calculate the width of the lane at a given `s` value.
    add_link(link_type, id)
        Add a link to the lane.
    get_linked_lane_id(link_type)
        Get the ID of the linked lane for a given link type.
    add_roadmark(roadmark)
        Add a roadmark to the lane.
    add_height(inner, outer=None, soffset=0)
        Add a height entry to the lane.
    add_lane_material(friction, roughness=None, soffset=0, surface=None)
        Add a material description entry to the lane.
    get_attributes()
        Return the attributes of the lane as a dictionary.
    get_element()
        Return the ElementTree representation of the lane.
    """

    def __init__(
        self,
        lane_type: LaneType = LaneType.driving,
        a: float = 0,
        b: float = 0,
        c: float = 0,
        d: float = 0,
        soffset: float = 0,
    ) -> None:
        """Initialize the `Lane` class.

        Parameters
        ----------
        lane_type : LaneType, optional
            The type of the lane. Default is `LaneType.driving`.
        a : float, optional
            The `a` coefficient of the polynomial. Default is 0.
        b : float, optional
            The `b` coefficient of the polynomial. Default is 0.
        c : float, optional
            The `c` coefficient of the polynomial. Default is 0.
        d : float, optional
            The `d` coefficient of the polynomial. Default is 0.
        soffset : float, optional
            The `s` offset of the lane. Default is 0.
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

    def __eq__(self, other: object) -> bool:
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

    def add_lane_width(
        self,
        a: float = 0,
        b: float = 0,
        c: float = 0,
        d: float = 0,
        soffset: float = 0,
    ) -> None:
        """Add an additional width element to the lane.

        Parameters
        ----------
        a : float, optional
            The `a` coefficient of the polynomial. Default is 0.
        b : float, optional
            The `b` coefficient of the polynomial. Default is 0.
        c : float, optional
            The `c` coefficient of the polynomial. Default is 0.
        d : float, optional
            The `d` coefficient of the polynomial. Default is 0.
        soffset : float, optional
            The `s` offset of the lane. Default is 0.
        """
        self.widths.append(_poly3struct(a, b, c, d, soffset))

    def get_width(self, s: float) -> float:
        """Calculate the width of the lane at a given `s` value.

        Parameters
        ----------
        s : float
            The `s` value at which to calculate the width.

        Returns
        -------
        float
            The width of the lane at the given `s` value.
        """
        index_to_calc = 0
        for i in range(len(self.widths)):
            if s >= self.widths[i].soffset:
                index_to_calc = i
            else:
                break
        return self.widths[index_to_calc].get_width(s)

    def add_link(self, link_type: str, id: Union[str, int]) -> "Lane":
        """Add a link to the lane.

        Parameters
        ----------
        link_type : str
            The type of the link (e.g., "successor" or "predecessor").
        id : str or int
            The ID of the linked lane.

        Returns
        -------
        Lane
            The updated `Lane` object.
        """
        self.links.add_link(_Link(link_type, str(id)))
        return self

    def get_linked_lane_id(self, link_type: str) -> Optional[int]:
        """Get the ID of the linked lane for a given link type.

        Parameters
        ----------
        link_type : str
            The type of the link (e.g., "successor" or "predecessor").

        Returns
        -------
        int or None
            The ID of the linked lane, or None if no link exists.
        """
        for link in self.links.links:
            if link.link_type == link_type:
                return int(link.element_id)
        return None

    def _set_lane_id(self, lane_id: int) -> None:
        """Set the lane ID of the lane and update the lane type to 'none' if it
        is a center lane.

        Parameters
        ----------
        lane_id : int
            The ID to assign to the lane.

        Returns
        -------
        None
        """
        self.lane_id = lane_id
        if self.lane_id == 0:
            self.lane_type = LaneType.none

    def add_roadmark(self, roadmark: "RoadMark") -> "Lane":
        """Add a roadmark to the lane.

        Parameters
        ----------
        roadmark : RoadMark
            The roadmark to add.

        Returns
        -------
        Lane
            The updated `Lane` object.

        Raises
        ------
        TypeError
            If `roadmark` is not of type `RoadMark`.
        """
        if not isinstance(roadmark, RoadMark):
            raise TypeError("roadmark input is not of type RoadMark")
        self.roadmark.append(roadmark)
        return self

    def add_height(
        self, inner: float, outer: Optional[float] = None, soffset: float = 0
    ) -> "Lane":
        """Add a height entry to the lane.

        Parameters
        ----------
        inner : float
            The inner height of the lane.
        outer : float, optional
            The outer height of the lane. If not provided, the inner
            height is used. Default is None.
        soffset : float, optional
            The `s` offset of the height record. Default is 0.

        Returns
        -------
        Lane
            The updated `Lane` object.
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

    def add_lane_material(
        self,
        friction: float,
        roughness: Optional[float] = None,
        soffset: float = 0,
        surface: Optional[str] = None,
    ) -> "Lane":
        """Add a material description entry to the lane.

        Parameters
        ----------
        friction : float
            The friction coefficient of the material.
        roughness : float, optional
            The roughness of the material. Default is None.
        soffset : float, optional
            The `s` offset of the material. Default is 0.
        surface : str, optional
            The surface material code. Default is None.

        Returns
        -------
        Lane
            The updated `Lane` object.
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

    def get_attributes(self) -> dict:
        """Return the attributes of the lane as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the lane.

        Raises
        ------
        ValueError
            If the lane ID is not set.
        """
        retdict = {}
        if self.lane_id == None:
            raise ValueError("lane id is not set correctly.")
        retdict["id"] = str(self.lane_id)
        retdict["type"] = enum2str(self.lane_type)
        retdict["level"] = "false"
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the lane.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the lane.
        """
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
    """Create a RoadMark element of OpenDRIVE.

    Parameters
    ----------
    marking_type : RoadMarkType
        The type of marking.
    width : float, optional
        The width of the marking/line. Default is None.
    length : float, optional
        The length of the visible, marked part of the line (used for
        broken lines). Default is None.
    space : float, optional
        The length of the invisible, unmarked part of the line (used for
        broken lines). Default is None.
    toffset : float, optional
        The offset in the `t` direction. Default is None.
    soffset : float, optional
        The offset in the `s` direction. Default is 0.
    rule : MarkRule, optional
        The marking rule. Default is None.
    color : RoadMarkColor, optional
        The color of the marking. Default is `RoadMarkColor.standard`.
    marking_weight : RoadMarkWeight, optional
        The weight of the marking. Default is `RoadMarkWeight.standard`.
    height : float, optional
        The thickness of the marking. Default is 0.02.
    laneChange : LaneChange, optional
        Indicates the direction in which lane changes are allowed.
        Default is None.

    Attributes
    ----------
    marking_type : RoadMarkType
        The type of marking.
    width : float
        The width of the marking/line.
    length : float
        The length of the visible, marked part of the line.
    space : float
        The length of the invisible, unmarked part of the line.
    toffset : float
        The offset in the `t` direction.
    soffset : float
        The offset in the `s` direction.
    rule : MarkRule
        The marking rule.
    color : RoadMarkColor
        The color of the marking.
    marking_weight : RoadMarkWeight
        The weight of the marking.
    height : float
        The thickness of the marking.
    laneChange : LaneChange
        Indicates the direction in which lane changes are allowed.

    Methods
    -------
    add_specific_road_line(line)
        Add a custom road line to the RoadMark.
    add_explicit_road_line(line)
        Add an explicit road line to the RoadMark.
    get_attributes()
        Return the attributes of the RoadMark as a dictionary.
    get_element()
        Return the ElementTree representation of the RoadMark.
    """

    def __init__(
        self,
        marking_type: RoadMarkType,
        width: Optional[float] = None,
        length: Optional[float] = None,
        space: Optional[float] = None,
        toffset: Optional[float] = None,
        soffset: float = 0,
        rule: Optional[MarkRule] = None,
        color: RoadMarkColor = RoadMarkColor.standard,
        marking_weight: RoadMarkWeight = RoadMarkWeight.standard,
        height: float = 0.02,
        laneChange: Optional[LaneChange] = None,
    ) -> None:
        """Initialize the `RoadMark` class.

        Parameters
        ----------
        marking_type : RoadMarkType
            The type of marking.
        width : float, optional
            The width of the marking/line. Default is None.
        length : float, optional
            The length of the visible, marked part of the line (used for
            broken lines). Default is None.
        space : float, optional
            The length of the invisible, unmarked part of the line (used
            for broken lines). Default is None.
        toffset : float, optional
            The offset in the `t` direction. Default is None.
        soffset : float, optional
            The offset in the `s` direction. Default is 0.
        rule : MarkRule, optional
            The marking rule. Default is None.
        color : RoadMarkColor, optional
            The color of the marking. Default is `RoadMarkColor.standard`.
        marking_weight : RoadMarkWeight, optional
            The weight of the marking. Default is
            `RoadMarkWeight.standard`.
        height : float, optional
            The thickness of the marking. Default is 0.02.
        laneChange : LaneChange, optional
            Indicates the direction in which lane changes are allowed.
            Default is None.
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RoadMark) and super().__eq__(other):
            if (
                self._line == other._line
                and self._explicit_line == other._explicit_line
                and self.get_attributes() == other.get_attributes()
                and self.marking_type == other.marking_type
            ):
                return True
        return False

    def add_specific_road_line(self, line: "RoadLine") -> "RoadMark":
        """Add a custom road line to the RoadMark.

        Parameters
        ----------
        line : RoadLine
            The road line to add.

        Returns
        -------
        RoadMark
            The updated `RoadMark` object.

        Raises
        ------
        TypeError
            If `line` is not of type `RoadLine`.
        """
        if not isinstance(line, RoadLine):
            raise TypeError("line input is not of type RoadLine")
        self._line.append(line)
        return self

    def add_explicit_road_line(self, line: "ExplicitRoadLine") -> "RoadMark":
        """Add an explicit road line to the RoadMark.

        Parameters
        ----------
        line : ExplicitRoadLine
            The explicit road line to add.

        Returns
        -------
        RoadMark
            The updated `RoadMark` object.

        Raises
        ------
        TypeError
            If `line` is not of type `ExplicitRoadLine`.
        """
        if not isinstance(line, ExplicitRoadLine):
            raise TypeError("line input is not of type RoadLine")
        self._explicit_line.append(line)
        return self

    def get_attributes(self) -> dict:
        """Return the attributes of the `RoadMark` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `RoadMark`.
        """
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

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `RoadMark`.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the `RoadMark`.
        """
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
    """Create a Line type to be used in roadmark.

    Parameters
    ----------
    width : float, optional
        The width of the line. Default is 0.
    length : float, optional
        The length of the line. Default is 0.
    space : float, optional
        The length of space between (broken) lines. Default is 0.
    toffset : float, optional
        The offset in the `t` direction. Default is 0.
    soffset : float, optional
        The offset in the `s` direction. Default is 0.
    rule : MarkRule, optional
        The marking rule. Default is None.
    color : RoadMarkColor, optional
        The color of the line. Default is None.

    Attributes
    ----------
    length : float
        The length of the line.
    space : float
        The length of space between (broken) lines.
    toffset : float
        The offset in the `t` direction.
    soffset : float
        The offset in the `s` direction.
    rule : MarkRule
        The marking rule.
    width : float
        The width of the line.
    color : RoadMarkColor
        The color of the line.

    Methods
    -------
    adjust_remainder(total_length, soffset=None, previous_remainder=None)
        Adjust the remainder of a broken mark for offset adjustments.
    shift_soffset()
        Shift the `soffset` by one period.
    adjust_soffset(total_length, remainder=None, previous_offset=None)
        Adjust the `soffset` of a broken mark for offset adjustments.
    get_attributes()
        Return the attributes of the `RoadLine` as a dictionary.
    get_element()
        Return the ElementTree representation of the `RoadLine`.
    """

    # TODO: check this for 1.5
    def __init__(
        self,
        width: float = 0,
        length: float = 0,
        space: float = 0,
        toffset: float = 0,
        soffset: float = 0,
        rule: Optional[MarkRule] = None,
        color: Optional[RoadMarkColor] = None,
    ) -> None:
        """Initialize the `RoadLine` class.

        Parameters
        ----------
        width : float, optional
            The width of the line. Default is 0.
        length : float, optional
            The length of the line. Default is 0.
        space : float, optional
            The length of space between (broken) lines. Default is 0.
        toffset : float, optional
            The offset in the `t` direction. Default is 0.
        soffset : float, optional
            The offset in the `s` direction. Default is 0.
        rule : MarkRule, optional
            The marking rule. Default is None.
        color : RoadMarkColor, optional
            The color of the line. Default is None.
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RoadLine) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def adjust_remainder(
        self,
        total_length: float,
        soffset: Optional[float] = None,
        previous_remainder: Optional[float] = None,
    ) -> None:
        """Adjust the remainder of a broken mark for offset adjustments.

        Parameters
        ----------
        total_length : float
            The length of the lane section where this line is valid.
        soffset : float, optional
            The desired `soffset` at the beginning of the line. Use this
            or `previous_remainder`. Default is None.
        previous_remainder : float, optional
            The remainder of the previous line. Use this or `soffset`.
            Default is None.

        Raises
        ------
        ToManyOptionalArguments
            If both `soffset` and `previous_remainder` are provided.
        """
        if soffset and previous_remainder:
            raise ToManyOptionalArguments(
                "for adjusting line lengths, use only soffset or previous_remainder."
            )
        if soffset is not None:
            self.soffset = soffset
        if previous_remainder is not None:
            self.soffset = self.space - previous_remainder
        self._remainder = self._calculate_remainder_of_line(
            self.soffset, total_length
        )

    def shift_soffset(self) -> None:
        """Shift the `soffset` by one period.

        This method shifts the `soffset` by the sum of the space and
        length of the line.
        """
        self.soffset += self.space + self.length

    def adjust_soffset(
        self,
        total_length: float,
        remainder: Optional[float] = None,
        previous_offset: Optional[float] = None,
    ) -> None:
        """Adjust the `soffset` of a broken mark for offset adjustments.

        Parameters
        ----------
        total_length : float
            The length of the lane section where this line is valid.
        remainder : float, optional
            The desired remainder (`soffset` at the end of the line). Use
            this or `previous_offset`. Default is None.
        previous_offset : float, optional
            The `soffset` of the previous line. Use this or `remainder`.
            Default is None.

        Raises
        ------
        ToManyOptionalArguments
            If both `remainder` and `previous_offset` are provided.
        """
        if remainder and previous_offset:
            raise ToManyOptionalArguments(
                "for adjusting line lengths, use only soffset or previous_remainder."
            )
        if remainder is not None:
            self._remainder = remainder
        if previous_offset is not None:
            self._remainder = self.space - previous_offset
        self.soffset = self._calculate_remainder_of_line(
            self._remainder, total_length
        )

    def _calculate_remainder_of_line(
        self, soffset: float, total_length: float
    ) -> float:
        """Calculate the remainder of the line.

        Parameters
        ----------
        soffset : float
            The `s` offset of the line.
        total_length : float
            The total length of the lane section.

        Returns
        -------
        float
            The remainder of the line.
        """
        n = (total_length - soffset + self.space) / (self.space + self.length)
        return (
            total_length
            - soffset
            - np.floor(n) * (self.space + self.length)
            + self.space
        )

    def get_attributes(self) -> dict:
        """Return the attributes of the `RoadLine` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `RoadLine`.
        """
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

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `RoadLine`.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the `RoadLine`.
        """
        """Returns the elementTree of the RoadLine."""
        element = ET.Element("line", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class ExplicitRoadLine(XodrBase):
    """Create an Explicit RoadLine type to be used in roadmark.

    Parameters
    ----------
    width : float, optional
        The width of the line. Default is 0.
    length : float, optional
        The length of the line. Default is 0.
    toffset : float, optional
        The offset in the `t` direction. Default is 0.
    soffset : float, optional
        The offset in the `s` direction. Default is 0.
    rule : MarkRule, optional
        The marking rule. Default is None.

    Attributes
    ----------
    length : float
        The length of the line.
    toffset : float
        The offset in the `t` direction.
    soffset : float
        The offset in the `s` direction.
    rule : MarkRule
        The marking rule.
    width : float
        The width of the line.

    Methods
    -------
    get_element()
        Return the ElementTree representation of the `ExplicitRoadLine`.
    get_attributes()
        Return the attributes of the `ExplicitRoadLine` as a dictionary.
    """

    # TODO: check this for 1.5
    def __init__(
        self,
        width: float = 0,
        length: float = 0,
        toffset: float = 0,
        soffset: float = 0,
        rule: Optional[MarkRule] = None,
    ) -> None:
        """Initialize the `ExplicitRoadLine` class.

        Parameters
        ----------
        width : float, optional
            The width of the line. Default is 0.
        length : float, optional
            The length of the line. Default is 0.
        toffset : float, optional
            The offset in the `t` direction. Default is 0.
        soffset : float, optional
            The offset in the `s` direction. Default is 0.
        rule : MarkRule, optional
            The marking rule. Default is None.
        """
        super().__init__()
        self.length = length
        self.toffset = toffset
        self.rule = enumchecker(rule, MarkRule, True)
        self.soffset = soffset
        self.width = width
        self._remainder = 0

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ExplicitRoadLine) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict:
        """Return the attributes of the `ExplicitRoadLine` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            `ExplicitRoadLine`.
        """
        retdict = {}
        retdict["length"] = str(self.length)
        retdict["tOffset"] = str(self.toffset)
        retdict["width"] = str(self.width)
        retdict["sOffset"] = str(self.soffset)
        if self.rule:
            retdict["rule"] = enum2str(self.rule)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `ExplicitRoadLine`.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the `ExplicitRoadLine`.
        """
        element = ET.Element("line", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element
