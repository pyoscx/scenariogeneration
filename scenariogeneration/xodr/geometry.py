"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
from typing import List, Optional, Union

import numpy as np
import pyclothoids as pcloth
from scipy.integrate import quad

from .exceptions import (
    MixOfGeometryAddition,
    NotEnoughInputArguments,
    ToManyOptionalArguments,
)
from .utils import XodrBase


def wrap_pi(angle):
    return angle % (2 * np.pi)


class _BaseGeometry(XodrBase):
    """Base class for geometries."""

    def __init__(self) -> None:
        super().__init__()


class AdjustablePlanview:
    """AdjustablePlanview can be used to fit a geometry between two fixed
    roads.

    Parameters
    ----------
    left_lane_defs : optional
        Definitions for the left lanes.
    right_lane_defs : optional
        Definitions for the right lanes.
    center_road_mark : optional
        Definition for the center road marking.
    lane_width : optional
        Width of the lanes at the start.
    lane_width_end : optional
        Width of the lanes at the end.

    Attributes
    ----------
    fixed : bool
        Indicates whether the planview is fixed.
    adjusted : bool
        Indicates whether the planview has been adjusted.
    left_lane_defs : optional
        Definitions for the left lanes.
    right_lane_defs : optional
        Definitions for the right lanes.
    center_road_mark : optional
        Definition for the center road marking.
    lane_width : optional
        Width of the lanes at the start.
    lane_width_end : optional
        Width of the lanes at the end.
    """

    def __init__(
        self,
        left_lane_defs: Optional[List] = None,
        right_lane_defs: Optional[List] = None,
        center_road_mark: Optional[str] = None,
        lane_width: Optional[float] = None,
        lane_width_end: Optional[float] = None,
    ) -> None:
        """Initialize the `AdjustablePlanview` instance.

        Parameters
        ----------
        left_lane_defs : list, optional
            Definitions for the left lanes. Default is None.
        right_lane_defs : list, optional
            Definitions for the right lanes. Default is None.
        center_road_mark : str, optional
            Definition for the center road marking. Default is None.
        lane_width : float, optional
            Width of the lanes at the start. Default is None.
        lane_width_end : float, optional
            Width of the lanes at the end. Default is None.

        Returns
        -------
        None
        """
        self.fixed = False
        self.adjusted = False
        self.left_lane_defs = left_lane_defs
        self.right_lane_defs = right_lane_defs
        self.center_road_mark = center_road_mark
        self.lane_width = lane_width
        self.lane_width_end = lane_width_end


class PlanView(XodrBase):
    """The PlanView is the geometrical description of a road.

    Parameters
    ----------
    x_start : float, optional
        Start x coordinate of the first geometry. Default is None.
    y_start : float, optional
        Start y coordinate of the first geometry. Default is None.
    h_start : float, optional
        Starting heading of the first geometry. Default is None.

    Attributes
    ----------
    present_x : float
        The start x coordinate of the next geometry added.
    present_y : float
        The y coordinate of the next geometry added.
    present_h : float
        The heading coordinate of the next geometry added.
    present_s : float
        The along-road measure of the next geometry added.

    Methods
    -------
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_total_length()
        Returns the full length of the PlanView.
    add_geometry(geom, length)
        Adds a new geometry entry to the PlanView.
    set_start_point(x_start, y_start, h_start)
        Sets the start point and heading of the PlanView.
    adjust_geometries()
        Adjusts all geometries in the PlanView based on the start point.
    """

    def __init__(
        self,
        x_start: Optional[float] = None,
        y_start: Optional[float] = None,
        h_start: Optional[float] = None,
    ) -> None:
        """Initialize the PlanView.

        Parameters
        ----------
        x_start : float, optional
            Start x coordinate of the first geometry. Default is None.
        y_start : float, optional
            Start y coordinate of the first geometry. Default is None.
        h_start : float, optional
            Starting heading of the first geometry. Default is None.

        Raises
        ------
        NotEnoughInputArguments
            If only some of the start values are provided but not all.
        """
        super().__init__()
        self.present_x: float = 0
        self.present_y: float = 0
        self.present_h: float = 0
        self.present_s: float = 0
        self.fixed: bool = False

        if all([x_start != None, y_start != None, h_start != None]):
            self.set_start_point(x_start, y_start, h_start)
        elif any([x_start != None, y_start != None, h_start != None]):
            raise NotEnoughInputArguments(
                "If a start position is wanted for the PlanView, all inputs must be used."
            )

        self.x_start = None
        self.y_start = None
        self.h_start = None

        self.x_end = None
        self.y_end = None
        self.h_end = None

        self._raw_geometries = []
        self._adjusted_geometries = []
        self._overridden_headings = []

        self.adjusted = False
        # variable to track what mode of adding geometries are used

        self._addition_mode = None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PlanView) and super().__eq__(other):
            if self.adjusted and other.adjusted:
                if self._adjusted_geometries == other._adjusted_geometries:
                    return True
            elif not self.adjusted and not other.adjusted:
                Warning(
                    "Comparing non adjusted geometries, default value will always be False"
                )
                return False

        return False

    def add_geometry(
        self, geom: _BaseGeometry, heading: Optional[float] = None
    ) -> "PlanView":
        """Add a geometry to the PlanView and stitch together all geometries in
        the order they are added.

        This method should be used together with the
        `adjust_roads_and_lanes` method in the OpenDrive class.

        Note
        ----
        Do not mix this method with `add_fixed_geometry`.

        Parameters
        ----------
        geom : _BaseGeometry
            The geometry to add. Must be an instance of `_BaseGeometry`.
        heading : float, optional
            Override the previous heading (not recommended). If used, it
            must be applied consistently for all geometries. Default is None.

        Returns
        -------
        PlanView
            The updated PlanView instance.

        Raises
        ------
        MixOfGeometryAddition
            If a fixed geometry has already been added.
        TypeError
            If `geom` is not an instance of `_BaseGeometry`.
        """
        if self._addition_mode == "add_fixed_geometry":
            raise MixOfGeometryAddition(
                "A fixed geometry has already been added, please use either add_geometry or add_fixed_geometry"
            )

        if heading is not None:
            self._overridden_headings.append(heading)
        if not isinstance(geom, _BaseGeometry):
            raise TypeError("geom_type is not of type _BaseGeometry.")
        self._raw_geometries.append(geom)
        self._addition_mode = "add_geometry"
        return self

    def add_fixed_geometry(
        self,
        geom: Union["Line", "Spiral", "ParamPoly3", "Arc"],
        x_start: float,
        y_start: float,
        h_start: float,
        s: Optional[float] = None,
    ) -> "PlanView":
        """Add a fixed geometry to the PlanView at a specific point.

        If `s` is provided, the values will be coded, and it is up to the
        user to ensure correctness. If `s` is not provided, the geometries
        are expected to be added in order, and `s` will be calculated.

        Note
        ----
        Do not mix this method with `add_geometry`.

        Parameters
        ----------
        geom : Line, Spiral, ParamPoly3, or Arc
            The geometry to add.
        x_start : float
            Start x position of the geometry.
        y_start : float
            Start y position of the geometry.
        h_start : float
            Start heading of the geometry.
        s : float, optional
            Start s value of the geometry. Default is None.

        Returns
        -------
        PlanView
            The updated PlanView instance.

        Raises
        ------
        MixOfGeometryAddition
            If a geometry has already been added using `add_geometry`.
        """

        if self._addition_mode == "add_geometry":
            raise MixOfGeometryAddition(
                "A geometry has already been added with add_geometry, please use either add_geometry, or add_fixed_geometry not both"
            )

        if s != None:
            pres_s = s
        else:
            pres_s = self.present_s

        if not self.fixed:
            self.x_start = x_start
            self.y_start = y_start
            self.h_start = h_start
            self.fixed = True

        newgeom = _Geometry(pres_s, x_start, y_start, h_start, geom)
        self._adjusted_geometries.append(newgeom)
        self.x_end, self.y_end, self.h_end, length = newgeom.get_end_data()
        self.present_s += length
        self.adjusted = True
        self._addition_mode = "add_fixed_geometry"
        return self

    def set_start_point(
        self, x_start: float = 0, y_start: float = 0, h_start: float = 0
    ) -> None:
        """Set the start point of the PlanView.

        Parameters
        ----------
        x_start : float, optional
            Start x coordinate of the first geometry. Default is 0.
        y_start : float, optional
            Start y coordinate of the first geometry. Default is 0.
        h_start : float, optional
            Starting heading of the first geometry. Default is 0.

        Returns
        -------
        None
        """

        self.present_x = x_start
        self.present_y = y_start
        self.present_h = h_start
        self.fixed = True

    def get_start_point(
        self,
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Return the start point of the PlanView.

        Returns
        -------
        tuple of (float or None, float or None, float or None)
            A tuple containing:
            - x_start : float or None
                The start x coordinate of the PlanView.
            - y_start : float or None
                The start y coordinate of the PlanView.
            - h_start : float or None
                The starting heading of the PlanView.
        """

        return self.x_start, self.y_start, self.h_start
        # return self._adjusted_geometries[-1].get_end_point

    def get_end_point(
        self,
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Return the end point of the PlanView.

        Returns
        -------
        tuple of (float or None, float or None, float or None)
            A tuple containing:
            - x_end : float or None
                The end x coordinate of the PlanView.
            - y_end : float or None
                The end y coordinate of the PlanView.
            - h_end : float or None
                The ending heading of the PlanView.
        """

        return self.x_end, self.y_end, self.h_end

    def adjust_geometries(self, from_end: bool = False) -> None:
        """Adjust all geometries to have the correct start point and heading.

        Parameters
        ----------
        from_end : bool, optional
            Indicates whether `(self.present_x, self.present_y,
            self.present_h)` are interpreted as the starting point
            (`False`) or the ending point (`True`) of the geometry.
            Default is `False`.

        Returns
        -------
        None
        """
        if from_end == False:
            self.x_start = self.present_x
            self.y_start = self.present_y
            self.h_start = self.present_h

            for i in range(len(self._raw_geometries)):
                if len(self._overridden_headings) > 0:
                    self.present_h = self._overridden_headings[i]

                newgeom = _Geometry(
                    self.present_s,
                    self.present_x,
                    self.present_y,
                    self.present_h,
                    self._raw_geometries[i],
                )
                (
                    self.present_x,
                    self.present_y,
                    self.present_h,
                    length,
                ) = newgeom.get_end_data()
                self.present_s += length

                self._adjusted_geometries.append(newgeom)
            self.x_end = self.present_x
            self.y_end = self.present_y
            self.h_end = wrap_pi(self.present_h)

        else:
            self.x_end = self.present_x
            self.y_end = self.present_y
            self.h_end = self.present_h + np.pi

            lengths = []
            for i in range(len(self._raw_geometries) - 1, -1, -1):
                newgeom = _Geometry(
                    self.present_s,
                    self.present_x,
                    self.present_y,
                    self.present_h,
                    self._raw_geometries[i],
                )
                (
                    self.present_x,
                    self.present_y,
                    self.present_h,
                    partial_length,
                ) = newgeom.get_start_data()
                lengths.append(partial_length)
                self._adjusted_geometries.append(newgeom)

            self.x_start = self.present_x
            self.y_start = self.present_y
            self.h_start = wrap_pi(self.present_h + np.pi)

            length = sum(lengths)
            self.present_s = 0

            for i in range(len(self._adjusted_geometries) - 1, -1, -1):
                self._adjusted_geometries[i].set_s(self.present_s)
                self.present_s += lengths[i]
            self._adjusted_geometries.reverse()
        self.h_start = wrap_pi(self.h_start)
        self.h_end = wrap_pi(self.h_end)
        self.adjusted = True

    def get_total_length(self) -> float:
        """Return the total length of the PlanView.

        If the geometries have been adjusted, the total length is
        calculated based on the adjusted geometries. Otherwise, it is
        calculated based on the raw geometries.

        Returns
        -------
        float
            The total length of the PlanView.
        """
        if self.adjusted:
            return self.present_s
        else:
            return sum([x.length for x in self._raw_geometries])

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the PlanView.

        This method generates an XML element for the PlanView, including
        all adjusted geometries.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the PlanView.
        """

        element = ET.Element("planView")
        self._add_additional_data_to_element(element)
        for geom in self._adjusted_geometries:
            element.append(geom.get_element())
        return element


class _Geometry(XodrBase):
    """The _Geometry class describes the geometry entry of OpenDRIVE.

    Parameters
    ----------
    s : float
        The start s value (along the road) of the geometry.
    x : float
        Start x coordinate of the geometry.
    y : float
        Start y coordinate of the geometry.
    heading : float
        Heading of the geometry.
    geom_type : Line, Spiral, ParamPoly3, or Arc
        The type of geometry.

    Attributes
    ----------
    s : float
        The start s value (along the road) of the geometry.
    x : float
        Start x coordinate of the geometry.
    y : float
        Start y coordinate of the geometry.
    heading : float
        Heading of the geometry.
    geom_type : Line, Spiral, ParamPoly3, or Arc
        The type of geometry.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the geometry.
    get_attributes()
        Returns a dictionary of all attributes of the geometry.
    """

    def __init__(
        self,
        s: float,
        x: float,
        y: float,
        heading: float,
        geom_type: _BaseGeometry,
    ) -> None:
        """Initialize the _Geometry instance.

        Parameters
        ----------
        s : float
            The start s value (along the road) of the geometry.
        x : float
            Start x coordinate of the geometry.
        y : float
            Start y coordinate of the geometry.
        heading : float
            Heading of the geometry.
        geom_type : _BaseGeometry
            The type of geometry.

        Raises
        ------
        TypeError
            If `geom_type` is not an instance of `_BaseGeometry`.
        """
        super().__init__()
        self.s = s
        self.x = x
        self.y = y

        self.heading = heading
        if not isinstance(geom_type, _BaseGeometry):
            raise TypeError("geom_type is not of type _BaseGeometry.")
        self.geom_type = geom_type
        _, _, _, self.length = self.geom_type.get_end_data(
            self.x, self.y, self.heading
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Geometry) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.geom_type == other.geom_type
            ):
                return True
        return False

    def get_end_data(self) -> tuple[float, float, float, float]:
        """Return the end point of the geometry.

        Parameters
        ----------
        x : float
            The x start coordinate of the geometry.
        y : float
            The y start coordinate of the geometry.
        h : float
            The start heading of the geometry.

        Returns
        -------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_end : float
                The x end coordinate of the geometry.
            - y_end : float
                The y end coordinate of the geometry.
            - h_end : float
                The end heading of the geometry.
            - length : float
                The length of the geometry.
        """
        return self.geom_type.get_end_data(self.x, self.y, self.heading)

    def get_start_data(self) -> tuple[float, float, float, float]:
        """Return the start point of the geometry.

        Returns
        -------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_start : float
                The start x coordinate of the geometry.
            - y_start : float
                The start y coordinate of the geometry.
            - h_start : float
                The start heading of the geometry.
            - length : float
                The length of the geometry.
        """
        x, y, heading, self.length = self.geom_type.get_start_data(
            self.x, self.y, self.heading
        )
        self.x = x
        self.y = y
        self.heading = heading + np.pi
        self.s = None
        return x, y, heading, self.length

    def set_s(self, s: float) -> None:
        """Set the start s value (along the road) of the geometry.

        Parameters
        ----------
        s : float
            The start s value to set for the geometry.

        Returns
        -------
        None
        """
        self.s = s

    def get_attributes(self) -> dict:
        """Return the attributes of the `_Geometry` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `_Geometry`:
            - "s" : str
                The start s value of the geometry.
            - "x" : str
                The start x coordinate of the geometry.
            - "y" : str
                The start y coordinate of the geometry.
            - "hdg" : str
                The heading of the geometry.
            - "length" : str
                The length of the geometry.
        """
        retdict = {}
        retdict["s"] = str(self.s)
        retdict["x"] = str(self.x)
        retdict["y"] = str(self.y)
        retdict["hdg"] = str(self.heading)
        retdict["length"] = str(self.length)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `_Geometry`.

        This method generates an XML element for the `_Geometry`,
        including its attributes and the associated geometry type.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the `_Geometry`.
        """
        element = ET.Element("geometry", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        element.append(self.geom_type.get_element())
        return element


class Line(_BaseGeometry):
    """The `Line` class creates a line type of geometry.

    Parameters
    ----------
    length : float
        The length of the line.

    Attributes
    ----------
    length : float
        The length of the line.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the class.
    get_end_data(x, y, h)
        Returns the end point of the geometry.
    get_start_data(end_x, end_y, end_h)
        Returns the start point of the geometry.
    """

    def __init__(self, length: float) -> None:
        """Initialize the `Line` instance.

        Parameters
        ----------
        length : float
            The length of the line.

        Returns
        -------
        None
        """
        super().__init__()
        self.length = length

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

    def get_end_data(
        self, x: float, y: float, h: float
    ) -> tuple[float, float, float, float]:
        """Return the end point of the geometry.

        Parameters
        ----------
        x : float
            The x start coordinate of the geometry.
        y : float
            The y start coordinate of the geometry.
        h : float
            The start heading of the geometry.

        Returns
        -------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_end : float
                The x end coordinate of the geometry.
            - y_end : float
                The y end coordinate of the geometry.
            - h_end : float
                The end heading of the geometry.
            - length : float
                The length of the geometry.
        """

        new_x = self.length * np.cos(h) + x
        new_y = self.length * np.sin(h) + y
        new_h = h

        return new_x, new_y, new_h, self.length

    def get_start_data(
        self, end_x: float, end_y: float, end_h: float
    ) -> tuple[float, float, float, float]:
        """Return the start point of the geometry.

        Parameters
        ----------
        end_x : float
            The x end coordinate of the geometry.
        end_y : float
            The y end coordinate of the geometry.
        end_h : float
            The end heading of the geometry.

        Returns
        -------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_start : float
                The start x coordinate of the geometry.
            - y_start : float
                The start y coordinate of the geometry.
            - h_start : float
                The start heading of the geometry.
            - length : float
                The length of the geometry.
        """
        start_x = self.length * np.cos(end_h) + end_x
        start_y = self.length * np.sin(end_h) + end_y
        start_h = end_h

        return start_x, start_y, start_h, self.length

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `Line`.

        This method generates an XML element for the `Line`, including
        any additional data.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the `Line`.
        """
        element = ET.Element("line")
        self._add_additional_data_to_element(element)
        return element


class Arc(_BaseGeometry):
    """The `Arc` class creates an arc type of geometry.

    Parameters
    ----------
    curvature : float
        The curvature of the arc.
    length : float, optional
        The length of the arc. Either `length` or `angle` must be provided.
    angle : float, optional
        The angle of the arc. Either `angle` or `length` must be provided.

    Attributes
    ----------
    curvature : float
        The curvature of the arc.
    length : float
        The length of the arc.
    angle : float
        The angle of the arc.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    get_end_data(x, y, h)
        Returns the end point of the geometry.
    get_start_data(end_x, end_y, end_h)
        Returns the start point of the geometry.
    """

    def __init__(
        self,
        curvature: float,
        length: Optional[float] = None,
        angle: Optional[float] = None,
    ) -> None:
        """Initialize the `Arc` instance.

        Parameters
        ----------
        curvature : float
            The curvature of the arc.
        length : float, optional
            The length of the arc. Either `length` or `angle` must be provided.
        angle : float, optional
            The angle of the arc. Either `angle` or `length` must be provided.

        Raises
        ------
        NotEnoughInputArguments
            If neither `length` nor `angle` is provided.
        ToManyOptionalArguments
            If both `length` and `angle` are provided.
        ValueError
            If `curvature` is 0, as it would create a straight line.
        """
        super().__init__()
        if length == None and angle == None:
            raise NotEnoughInputArguments(
                "neither length nor angle defined, for arc"
            )

        if length != None and angle != None:
            raise ToManyOptionalArguments(
                "both length and angle set, only one is requiered"
            )

        self.length = length
        self.angle = angle
        if curvature == 0:
            raise ValueError(
                "You are creating a straight line, please use Line instead"
            )
        self.curvature = curvature

        if self.length:
            self.angle = self.length * self.curvature

        if self.angle:
            _, _, _, self.length = self.get_end_data(0, 0, 0)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Arc) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_end_data(
        self, x: float, y: float, h: float
    ) -> tuple[float, float, float, float]:
        """Return the end point of the geometry.

        Parameters
        ----------
        x : float
            The x start coordinate of the geometry.
        y : float
            The y start coordinate of the geometry.
        h : float
            The start heading of the geometry.

        Returns
        -------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_end : float
                The x end coordinate of the geometry.
            - y_end : float
                The y end coordinate of the geometry.
            - h_end : float
                The end heading of the geometry.
            - length : float
                The length of the geometry.
        """
        radius = 1 / np.abs(self.curvature)
        if self.curvature < 0:
            phi_0 = h + np.pi / 2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius

        else:
            phi_0 = h - np.pi / 2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius

        if self.length:
            self.angle = self.length * self.curvature

        new_ang = self.angle + phi_0
        if self.angle:
            self.length = np.abs(radius * self.angle)

        new_ang = self.angle + phi_0
        new_h = h + self.angle
        new_x = np.cos(new_ang) * radius + x_0
        new_y = np.sin(new_ang) * radius + y_0

        return new_x, new_y, new_h, self.length

    def get_start_data(
        self, end_x: float, end_y: float, end_h: float
    ) -> tuple[float, float, float, float]:
        """Returns information about the end point of the geometry.

        Parameters
        ----------
        end_x : float
            The end x coordinate of the geometry
        end_y : float
            The end y coordinate of the geometry

        end_h : float
            The end h coordinate of the geometry

        Returns
        ---------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_start : float
                The x start coordinate of the geometry.
            - y_start : float
                The y start coordinate of the geometry.
            - h_start : float
                The start heading of the geometry.
            - length : float
                The length of the geometry.
        """
        x = end_x
        y = end_y
        h = end_h
        inv_curv = -self.curvature
        radius = 1 / np.abs(inv_curv)
        if inv_curv < 0:
            phi_0 = h + np.pi / 2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius

        else:
            phi_0 = h - np.pi / 2
            x_0 = x - np.cos(phi_0) * radius
            y_0 = y - np.sin(phi_0) * radius

        if self.length:
            self.angle = self.length * inv_curv

        new_ang = self.angle + phi_0
        if self.angle:
            self.length = np.abs(radius * self.angle)

        new_h = h + self.angle
        new_x = np.cos(new_ang) * radius + x_0
        new_y = np.sin(new_ang) * radius + y_0
        return new_x, new_y, new_h, self.length

    def get_attributes(self) -> dict:
        """Return the attributes of the `Arc` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `Arc`:
            - "curvature" : str
                The curvature of the arc.
        """
        return {"curvature": str(self.curvature)}

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `Arc`.

        This method generates an XML element for the `Arc`, including
        its attributes and any additional data.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the `Arc`.
        """
        element = ET.Element("arc", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class ParamPoly3(_BaseGeometry):
    """The `ParamPoly3` class creates a parametric polynomial type of geometry
    in the coordinate system U (along the road) and V (normal to the road).

    The polynomials are of the form:
        uv(p) = a + b*p + c*p^2 + d*p^3

    Parameters
    ----------
    au : float
        Coefficient `a` of the `u` polynomial.
    bu : float
        Coefficient `b` of the `u` polynomial.
    cu : float
        Coefficient `c` of the `u` polynomial.
    du : float
        Coefficient `d` of the `u` polynomial.
    av : float
        Coefficient `a` of the `v` polynomial.
    bv : float
        Coefficient `b` of the `v` polynomial.
    cv : float
        Coefficient `c` of the `v` polynomial.
    dv : float
        Coefficient `d` of the `v` polynomial.
    prange : str, optional
        Either `"normalized"` or `"arcLength"`. Default is `"normalized"`.
    length : float, optional
        Total length of the arc, used if `prange == "arcLength"`.

    Attributes
    ----------
    au : float
        Coefficient `a` of the `u` polynomial.
    bu : float
        Coefficient `b` of the `u` polynomial.
    cu : float
        Coefficient `c` of the `u` polynomial.
    du : float
        Coefficient `d` of the `u` polynomial.
    av : float
        Coefficient `a` of the `v` polynomial.
    bv : float
        Coefficient `b` of the `v` polynomial.
    cv : float
        Coefficient `c` of the `v` polynomial.
    dv : float
        Coefficient `d` of the `v` polynomial.
    prange : str
        Either `"normalized"` or `"arcLength"`. Default is `"normalized"`.
    length : float
        Total length of the arc, used if `prange == "arcLength"`.

    Methods
    -------
    get_element(elementname)
        Returns the full ElementTree representation of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    get_end_coordinate(length, x, y, h)
        Returns the end point of the geometry.
    """

    def __init__(
        self,
        au: float,
        bu: float,
        cu: float,
        du: float,
        av: float,
        bv: float,
        cv: float,
        dv: float,
        prange: str = "normalized",
        length: Optional[float] = None,
    ) -> None:
        """Initialize the `ParamPoly3` instance.

        Parameters
        ----------
        au : float
            Coefficient `a` of the `u` polynomial.
        bu : float
            Coefficient `b` of the `u` polynomial.
        cu : float
            Coefficient `c` of the `u` polynomial.
        du : float
            Coefficient `d` of the `u` polynomial.
        av : float
            Coefficient `a` of the `v` polynomial.
        bv : float
            Coefficient `b` of the `v` polynomial.
        cv : float
            Coefficient `c` of the `v` polynomial.
        dv : float
            Coefficient `d` of the `v` polynomial.
        prange : str, optional
            Either `"normalized"` or `"arcLength"`. Default is `"normalized"`.
        length : float, optional
            Total length of the arc, used if `prange == "arcLength"`.

        Raises
        ------
        ValueError
            If `prange == "arcLength"` and `length` is not provided.
        """
        super().__init__()
        self.au = au
        self.bu = bu
        self.cu = cu
        self.du = du
        self.av = av
        self.bv = bv
        self.cv = cv
        self.dv = dv
        self.prange = prange
        if prange == "arcLength" and length == None:
            raise ValueError(
                "No length was provided for ParamPoly3 with arcLength option"
            )
        if length:
            self.length = length
        else:
            _, _, _, self.length = self.get_end_data(0, 0, 0)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ParamPoly3) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def _integrand(self, p: float) -> float:
        """Integral function to calculate the length of the polynomial.

        Note
        ----
        This method is not tested or verified.

        Parameters
        ----------
        p : float
            The parameter value for the polynomial.

        Returns
        -------
        float
            The value of the integral function at `p`.
        """
        return np.sqrt(
            (abs(3 * self.du * p**2 + 2 * self.cu * p + self.bu)) ** 2
            + (abs(3 * self.dv * p**2 + 2 * self.cv * p + self.bv)) ** 2
        )

    def get_start_data(
        self, x: float, y: float, h: float
    ) -> tuple[float, float, float, float]:
        """Returns the start point of the geometry.

        Parameters
        ----------
        x : float
            The x end coordinate of the geometry
        y : float
            The y end coordinate of the geometry
        h : float
            The x end heading of the geometry

        Returns
        ---------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_start : float
                The start x coordinate of the geometry.
            - y_start : float
                The start y coordinate of the geometry.
            - h_start : float
                The start heading of the geometry.
            - length : float
                The length of the geometry.
        """
        if self.prange == "normalized":
            p = 1
            I = quad(self._integrand, 0, 1)
            self.length = I[0]
        else:
            p = self.length
        newu = self.au + self.bu * p + self.cu * p**2 + self.du * p**3
        newv = self.av + self.bv * p + self.cv * p**2 + self.dv * p**3

        new_x = x - (newu * np.cos(h) - np.sin(h) * newv)
        new_y = y - (newu * np.sin(h) + np.cos(h) * newv)
        new_h = h - np.arctan2(
            self.bv + 2 * self.cv * p + 3 * self.dv * p**2,
            self.bu + 2 * self.cu * p + 3 * self.du * p**2,
        )

        return new_x, new_y, new_h, self.length

    def get_end_data(
        self, x: float, y: float, h: float
    ) -> tuple[float, float, float, float]:
        """Returns the end point of the geometry.

        Parameters
        ----------
        x : float
            The x start coordinate of the geometry.
        y : float
            The y start coordinate of the geometry.
        h : float
            The start heading of the geometry.

        Returns
        -------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_end : float
                The x end coordinate of the geometry.
            - y_end : float
                The y end coordinate of the geometry.
            - h_end : float
                The end heading of the geometry.
            - length : float
                The length of the geometry.
        """
        if self.prange == "normalized":
            p = 1
            I = quad(self._integrand, 0, 1)
            self.length = I[0]
        else:
            p = self.length
        newu = self.au + self.bu * p + self.cu * p**2 + self.du * p**3
        newv = self.av + self.bv * p + self.cv * p**2 + self.dv * p**3

        new_x = x + newu * np.cos(h) - np.sin(h) * newv
        new_y = y + newu * np.sin(h) + np.cos(h) * newv
        new_h = h + np.arctan2(
            self.bv + 2 * self.cv * p + 3 * self.dv * p**2,
            self.bu + 2 * self.cu * p + 3 * self.du * p**2,
        )

        return new_x, new_y, new_h, self.length

    def get_attributes(self) -> dict:
        """Return the attributes of the `ParamPoly3` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `ParamPoly3`:
            - "aU" : str
                Coefficient `a` of the `u` polynomial.
            - "bU" : str
                Coefficient `b` of the `u` polynomial.
            - "cU" : str
                Coefficient `c` of the `u` polynomial.
            - "dU" : str
                Coefficient `d` of the `u` polynomial.
            - "aV" : str
                Coefficient `a` of the `v` polynomial.
            - "bV" : str
                Coefficient `b` of the `v` polynomial.
            - "cV" : str
                Coefficient `c` of the `v` polynomial.
            - "dV" : str
                Coefficient `d` of the `v` polynomial.
            - "pRange" : str
                The range type of the polynomial
                (`"normalized"` or `"arcLength"`).
        """
        retdict = {}
        retdict["aU"] = str(self.au)
        retdict["bU"] = str(self.bu)
        retdict["cU"] = str(self.cu)
        retdict["dU"] = str(self.du)
        retdict["aV"] = str(self.av)
        retdict["bV"] = str(self.bv)
        retdict["cV"] = str(self.cv)
        retdict["dV"] = str(self.dv)
        retdict["pRange"] = self.prange
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `ParamPoly3`.

        This method generates an XML element for the `ParamPoly3`,
        including its attributes and any additional data.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the `ParamPoly3`.
        """
        element = ET.Element("paramPoly3", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element


class Spiral(_BaseGeometry):
    """The `Spiral` (Clothoid) class creates a spiral type of geometry.

    Parameters
    ----------
    curvstart : float
        Starting curvature of the spiral.
    curvend : float
        Final curvature of the spiral.
    length : float, optional
        Length of the spiral. Either `length`, `angle`, or `cdot` must
        be provided.
    angle : float, optional
        Angle of the spiral. Either `length`, `angle`, or `cdot` must
        be provided.
    cdot : float, optional
        Curvature change of the spiral. Either `length`, `angle`, or
        `cdot` must be provided.

    Attributes
    ----------
    curvstart : float
        Starting curvature of the spiral.
    curvend : float
        Final curvature of the spiral.

    Methods
    -------
    get_element()
        Returns the full ElementTree representation of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    get_end_data(x, y, h)
        Returns the end point of the geometry.
    get_start_data(end_x, end_y, end_h)
        Returns the start point of the geometry.
    """

    def __init__(
        self,
        curvstart: float,
        curvend: float,
        length: Optional[float] = None,
        angle: Optional[float] = None,
        cdot: Optional[float] = None,
    ) -> None:
        """Initialize the `Spiral` instance.

        Parameters
        ----------
        curvstart : float
            Starting curvature of the spiral.
        curvend : float
            Final curvature of the spiral.
        length : float, optional
            Length of the spiral. Either `length`, `angle`, or `cdot` must
            be provided.
        angle : float, optional
            Angle of the spiral. Either `length`, `angle`, or `cdot` must
            be provided.
        cdot : float, optional
            Curvature change of the spiral. Either `length`, `angle`, or
            `cdot` must be provided.

        Raises
        ------
        NotEnoughInputArguments
            If none of `length`, `angle`, or `cdot` is provided.
        ToManyOptionalArguments
            If more than one of `length`, `angle`, or `cdot` is provided.
        """
        super().__init__()
        self.curvstart = curvstart
        self.curvend = curvend
        if length == None and angle == None and cdot == None:
            raise NotEnoughInputArguments("Spiral is underdefined")
        if sum([x != None for x in [length, angle, cdot]]) > 1:
            raise ToManyOptionalArguments(
                "Spiral is overdefined, please use only one of the optional inputs"
            )
        if angle:
            self.length = (
                2 * abs(angle) / np.maximum(abs(curvend), abs(curvstart))
            )

        elif cdot:
            self.length = (self.curvend - self.curvstart) / cdot
        else:
            self.length = length

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Spiral) and super().__eq__(other):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_end_data(
        self, x: float, y: float, h: float
    ) -> tuple[float, float, float, float]:
        """Returns the end point of the geometry.

        Parameters
        ----------
        x : float
            The x start coordinate of the geometry.
        y : float
            The y start coordinate of the geometry.
        h : float
            The start heading of the geometry.

        Returns
        -------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_end : float
                The x end coordinate of the geometry.
            - y_end : float
                The y end coordinate of the geometry.
            - h_end : float
                The end heading of the geometry.
            - length : float
                The length of the spiral.
        """

        cloth = pcloth.Clothoid.StandardParams(
            x,
            y,
            h,
            self.curvstart,
            (self.curvend - self.curvstart) / self.length,
            self.length,
        )

        return cloth.XEnd, cloth.YEnd, cloth.ThetaEnd, cloth.length

    def get_start_data(
        self, end_x: float, end_y: float, end_h: float
    ) -> tuple[float, float, float, float]:
        """Returns the start point of the geometry.

        Parameters
        ----------
        end_x : float
            The x end coordinate of the geometry.
        end_y : float
            The y end coordinate of the geometry.
        end_h : float
            The end heading of the geometry.

        Returns
        -------
        tuple of (float, float, float, float)
            A tuple containing:
            - x_start : float
                The start x coordinate of the geometry.
            - y_start : float
                The start y coordinate of the geometry.
            - h_start : float
                The start heading of the inverse geometry.
            - length : float
                The length of the spiral.
        """
        cloth = pcloth.Clothoid.StandardParams(
            end_x,
            end_y,
            end_h,
            -self.curvend,
            -(self.curvstart - self.curvend) / self.length,
            self.length,
        )

        return cloth.XEnd, cloth.YEnd, cloth.ThetaEnd, cloth.length

    def get_attributes(self) -> dict:
        """Return the attributes of the `Spiral` as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the `Spiral`:
            - "curvStart" : str
                Starting curvature of the spiral.
            - "curvEnd" : str
                Final curvature of the spiral.
        """
        return {"curvStart": str(self.curvstart), "curvEnd": str(self.curvend)}

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the `Spiral`.

        This method generates an XML element for the `Spiral`, including
        its attributes and any additional data.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the `Spiral`.
        """
        element = ET.Element("spiral", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        return element
