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
from warnings import warn

import numpy as np

from ..helpers import enum2str
from .enumerations import (
    ContactPoint,
    CrossSectionProfileType,
    ElementType,
    StripMode,
    enumchecker,
)
from .utils import XodrBase


class ElevationProfile(XodrBase):
    """Create the elevationProfile element of the road in OpenDRIVE.

    Attributes
    ----------
    elevations : list of _Poly3Profile
        List of elevation profiles.

    Methods
    -------
    get_element(elementname)
        Returns the full ElementTree of the class.
    add_elevation(elevation)
        Adds an elevation profile to the road.
    """

    def __init__(self) -> None:
        """Initialize the ElevationProfile class."""
        self.elevations = []
        super().__init__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ElevationProfile) and super().__eq__(other):
            if self.elevations == other.elevations:
                return True
        return False

    def eval_at_s(self, s: float) -> float:
        return self.elevations[
            [i for i, x in enumerate(self.elevations) if x.s <= s][-1]
        ].eval_at_s(s)

    def eval_derivative_at_s(self, s: float) -> float:
        return self.elevations[
            [i for i, x in enumerate(self.elevations) if x.s <= s][-1]
        ].eval_derivative_at_s(s)

    def add_elevation(self, elevation: "_Poly3Profile") -> "ElevationProfile":
        """Add an elevation to the ElevationProfile.

        Parameters
        ----------
        elevation : _Poly3Profile
            The elevation profile to add to the ElevationProfile.

        Returns
        -------
        ElevationProfile
            The updated ElevationProfile object.
        """
        if not isinstance(elevation, _Poly3Profile):
            raise TypeError(
                "add_elevation requires an _Poly3Profile as input, not "
                + str(type(elevation))
            )
        self.elevations.append(elevation)
        return self

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the ElevationProfile.

        Returns
        -------
        xml.etree.ElementTree.Element
            The elevationProfile element.
        """
        element = ET.Element("elevationProfile")
        self._add_additional_data_to_element(element)
        for i in self.elevations:
            element.append(i.get_element("elevation"))
        return element


class LateralProfile(XodrBase):
    """Create the lateralProfile element of the road in OpenDRIVE.

    Attributes
    ----------
    superelevations : list of _Poly3Profile
        List of superelevations of the road.
    shapes : list of _Poly3Profile
        List of shapes for the road.

    Methods
    -------
    get_element(elementname)
        Returns the full ElementTree of the class.
    add_superelevation(superelevation)
        Adds a superelevation profile to the road.
    add_shape(shape)
        Adds a shape to the lateral profile.
    """

    def __init__(self) -> None:
        """Initialize the LateralProfile class."""
        super().__init__()
        self.superelevations = []
        self.shapes = []
        self.cross_section_surface = None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LateralProfile) and super().__eq__(other):
            if (
                self.superelevations == other.superelevations
                and self.shapes == other.shapes
                and self.cross_section_surface == other.cross_section_surface
            ):
                return True
        return False

    def add_superelevation(
        self, superelevation: "_Poly3Profile"
    ) -> "LateralProfile":
        """Add a superelevation to the LateralProfile.

        Parameters
        ----------
        superelevation : _Poly3Profile
            The superelevation profile to add to the LateralProfile.

        Returns
        -------
        LateralProfile
            The updated LateralProfile object.
        """
        if not isinstance(superelevation, _Poly3Profile):
            raise TypeError(
                "add_superelevation requires an _Poly3Profile as input, not "
                + str(type(superelevation))
            )
        if self.cross_section_surface is not None:
            raise ValueError(
                "A cross section surface cannot be combined with superelevation"
            )
        self.superelevations.append(superelevation)
        return self

    def eval_superelevation_at_s(self, s: float) -> float:
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_at_s(s)
        return 0

    def eval_t_superelevation_at_s(self, s: float, t: float) -> float:
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_t_at_s(s, t)
        return 0

    def eval_superelevation_derivative_at_s(self, s: float) -> float:
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_derivative_at_s(s)
        return 0

    def add_shape(self, shape: "_Poly3Profile") -> "LateralProfile":
        """Add a shape to the LateralProfile.

        Parameters
        ----------
        shape : _Poly3Profile
            The shape profile to add to the LateralProfile.

        Returns
        -------
        LateralProfile
            The updated LateralProfile object.
        """
        if not isinstance(shape, _Poly3Profile):
            raise TypeError(
                "add_shape requires an _Poly3Profile as input, not "
                + str(type(shape))
            )
        if self.cross_section_surface is not None:
            raise ValueError(
                "A cross section surface cannot be combined with shape"
            )
        self.shapes.append(shape)
        return self

    def set_cross_section_surface(
        self, cross_section_surface: "CrossSectionSurface"
    ) -> "LateralProfile":
        """Set the cross section surface of the LateralProfile.

        Parameters
        ----------
        cross_section_surface : CrossSectionSurface
            The cross section surface to set.

        Returns
        -------
        LateralProfile
            The updated LateralProfile object.
        """
        if not isinstance(cross_section_surface, CrossSectionSurface):
            raise TypeError(
                "cross_section_surface is not of type CrossSectionSurface"
            )
        if self.superelevations or self.shapes:
            raise ValueError(
                "A cross section surface cannot be combined with shape or superelevation"
            )
        self.cross_section_surface = cross_section_surface
        return self

    def get_element(self) -> ET.Element:
        """Return the ElementTree of the LateralProfile.

        Returns
        -------
        xml.etree.ElementTree.Element
            The lateralProfile element.
        """
        element = ET.Element("lateralProfile")
        self._add_additional_data_to_element(element)
        for i in self.superelevations:
            element.append(i.get_element("superelevation"))
        for i in self.shapes:
            element.append(i.get_element("shape"))
        if self.cross_section_surface is not None:
            element.append(self.cross_section_surface.get_element())
        return element


class _Poly3Profile:
    """The _Poly3Profile class describes a poly3 along the s-coordinate of a
    road. The elevation is described as a third-degree polynomial: elev(ds) = a
    + b*ds + c*ds^2 + d*ds^3 or (if t is used): shape(ds) = a + b*dt + c*dt^2 +
    d*dt^3.

    This class is used for elevation, superelevation, and shape.

    Parameters
    ----------
    s : float
        Start coordinate of the elevation.
    a : float
        Coefficient of the polynomial.
    b : float
        Coefficient of the polynomial.
    c : float
        Coefficient of the polynomial.
    d : float
        Coefficient of the polynomial.
    t : float, optional
        Variable used only for shape. Default is None.

    Attributes
    ----------
    s : float
        Start coordinate of the elevation.
    a : float
        Coefficient of the polynomial.
    b : float
        Coefficient of the polynomial.
    c : float
        Coefficient of the polynomial.
    d : float
        Coefficient of the polynomial.
    t : float
        Variable used only for shape.

    Methods
    -------
    get_element(elementname)
        Returns the full ElementTree of the class.
    get_attributes()
        Returns the attributes of the class.
    """

    def __init__(
        self,
        s: float,
        a: float,
        b: float,
        c: float,
        d: float,
        t: Optional[float] = None,
        elevation_type: str = "elevation",
    ) -> None:
        """Initialize the _Poly3Profile class.

        Parameters
        ----------
        s : float
            Start coordinate of the elevation.
        a : float
            Coefficient of the polynomial.
        b : float
            Coefficient of the polynomial.
        c : float
            Coefficient of the polynomial.
        d : float
            Coefficient of the polynomial.
        t : float, optional
            Variable used only for shape. Default is None.
        elevation_type : str, optional
            Type of elevation for t-value evaluations. Default is
            "elevation".
        """
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.t = t
        if elevation_type not in ["elevation", "superelevation", "shape"]:
            raise ValueError(
                "elevation_type can only be: elevation, superelevation, "
                "or shape, not " + elevation_type
            )
        self.elevation_type = elevation_type

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Poly3Profile):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def eval_at_s(self, s: float) -> float:
        if s < self.s:
            raise ValueError(
                "When evaluating elevation, s must be larger than s_start."
            )
        return (
            self.a
            + self.b * (s - self.s)
            + self.c * (s - self.s) ** 2
            + self.d * (s - self.s) ** 3
        )

    def eval_t_at_s(self, s: float, t: float) -> float:
        if self.elevation_type == "elevation":
            return self.eval_at_s(s)
        elif self.elevation_type == "superelevation":
            return t * np.sin(self.eval_at_s(s))
        elif self.elevation_type == "shape":
            raise NotImplementedError(
                "t calculations for shape are not implemented yet."
            )
        else:
            raise ValueError(
                "elevation_type can only be: elevation, superelevation, "
                "or shape, not " + self.elevation_type
            )

    def eval_derivative_at_s(self, s: float) -> float:
        if s < self.s:
            raise ValueError(
                "When evaluating elevation, s must be larger than s_start."
            )
        return (
            self.b + 2 * self.c * (s - self.s) + 3 * self.d * (s - self.s) ** 2
        )

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the _Poly3Profile.

        Returns
        -------
        dict
            A dictionary containing the attributes of the profile.
        """
        retdict = {}
        retdict["s"] = str(self.s)
        if self.t is not None:
            retdict["t"] = str(self.t)
        retdict["a"] = str(self.a)
        retdict["b"] = str(self.b)
        retdict["c"] = str(self.c)
        retdict["d"] = str(self.d)
        return retdict

    def get_element(self, elementname: Optional[str] = None) -> ET.Element:
        """Return the ElementTree of the _Poly3Profile.

        Parameters
        ----------
        elementname : str, optional
            Name of the element. Can be "elevation", "superelevation", or
            "shape". Default is the same as elevation_type.

        Returns
        -------
        xml.etree.ElementTree.Element
            The element representing the profile.
        """
        if elementname is None:
            elementname = self.elevation_type

        if elementname == "shape" and self.t is None:
            raise ValueError("When shape is used, the t value has to be set.")
        elif elementname != "shape" and self.t is not None:
            raise ValueError(
                "When shape is not used, the t value should not be set."
            )

        element = ET.Element(elementname, attrib=self.get_attributes())
        return element


class CrossSectionCoefficients:
    """Coefficients of a cubic polynomial in s-direction.

    Parameters
    ----------
    a : float
        Coefficient a.
    b : float
        Coefficient b.
    c : float
        Coefficient c.
    d : float
        Coefficient d.
    s : float, optional
        Start coordinate along the road reference line. Default is 0.
    """

    def __init__(
        self, a: float, b: float, c: float, d: float, s: float = 0
    ) -> None:
        if s < 0:
            raise ValueError("s must be non-negative")
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.s = s

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CrossSectionCoefficients):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self) -> dict:
        return {
            "a": str(self.a),
            "b": str(self.b),
            "c": str(self.c),
            "d": str(self.d),
            "s": str(self.s),
        }

    def get_element(self) -> ET.Element:
        return ET.Element("coefficients", attrib=self.get_attributes())


def _sorted_cross_section_coefficients(
    coefficients: list[CrossSectionCoefficients],
) -> list[CrossSectionCoefficients]:
    ordered = sorted(coefficients, key=lambda item: item.s)
    if not ordered or ordered[0].s != 0:
        raise ValueError("Cross section coefficients must start at s=0")
    if len({item.s for item in ordered}) != len(ordered):
        raise ValueError("Cross section coefficient positions must be unique")
    return ordered


class CrossSectionStripProfile:
    """A strip profile element (constant, linear, quadratic, or cubic).

    Parameters
    ----------
    profile_type : CrossSectionProfileType
        Type of profile: constant, linear, quadratic, or cubic.
    """

    def __init__(self, profile_type: CrossSectionProfileType) -> None:
        self.profile_type = enumchecker(profile_type, CrossSectionProfileType)
        self.coefficients = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CrossSectionStripProfile):
            if (
                self.profile_type == other.profile_type
                and self.coefficients == other.coefficients
            ):
                return True
        return False

    def add_coefficients(
        self, coefficients: CrossSectionCoefficients
    ) -> "CrossSectionStripProfile":
        if not isinstance(coefficients, CrossSectionCoefficients):
            raise TypeError(
                "coefficients is not of type CrossSectionCoefficients"
            )
        self.coefficients.append(coefficients)
        return self

    def get_element(self) -> ET.Element:
        element = ET.Element(enum2str(self.profile_type))
        for coefficients in _sorted_cross_section_coefficients(
            self.coefficients
        ):
            element.append(coefficients.get_element())
        return element


class CrossSectionStripWidth:
    """Width element for a cross section strip.

    Contains coefficients describing width variation along s.
    """

    def __init__(self) -> None:
        self.coefficients = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CrossSectionStripWidth):
            if self.coefficients == other.coefficients:
                return True
        return False

    def add_coefficients(
        self, coefficients: CrossSectionCoefficients
    ) -> "CrossSectionStripWidth":
        if not isinstance(coefficients, CrossSectionCoefficients):
            raise TypeError(
                "coefficients is not of type CrossSectionCoefficients"
            )
        self.coefficients.append(coefficients)
        return self

    def get_element(self) -> ET.Element:
        element = ET.Element("width")
        for coefficients in _sorted_cross_section_coefficients(
            self.coefficients
        ):
            element.append(coefficients.get_element())
        return element


class CrossSectionStrip:
    """A strip defining the lateral profile in t- and s-direction.

    Parameters
    ----------
    width : CrossSectionStripWidth, optional
        Width element for the strip.
    profile : CrossSectionStripProfile, optional
        Initial polynomial component. Add further components with add_profile.
    id : int, optional
        Strip ID: 1 or -1 for an inner strip, 2 or -2 for an outer strip.
        Default is 1.
    mode : StripMode, optional
        Height calculation mode, allowed only on outer strips.
    """

    def __init__(
        self,
        width: Optional[CrossSectionStripWidth] = None,
        profile: Optional[CrossSectionStripProfile] = None,
        id: int = 1,
        mode: Optional[StripMode] = None,
    ) -> None:
        if id not in (-2, -1, 1, 2):
            raise ValueError("Strip ID must be -2, -1, 1, or 2")
        if width is not None and not isinstance(width, CrossSectionStripWidth):
            raise TypeError("width is not of type CrossSectionStripWidth")
        self.id = id
        self.mode = enumchecker(mode, StripMode, True)
        if self.mode is not None and abs(id) != 2:
            raise ValueError("Only outer strips may define a mode")
        if width is not None and abs(id) == 2:
            raise ValueError("Only inner strips may define a width")
        self.width = width
        self.profile = profile

    @property
    def profile(self) -> Optional[CrossSectionStripProfile]:
        return self.profiles[0] if self.profiles else None

    @profile.setter
    def profile(self, profile: Optional[CrossSectionStripProfile]) -> None:
        if profile is not None and not isinstance(
            profile, CrossSectionStripProfile
        ):
            raise TypeError("profile is not of type CrossSectionStripProfile")
        self.profiles = [] if profile is None else [profile]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CrossSectionStrip):
            if (
                self.get_attributes() == other.get_attributes()
                and self.width == other.width
                and self.profiles == other.profiles
            ):
                return True
        return False

    def add_profile(
        self, profile: CrossSectionStripProfile
    ) -> "CrossSectionStrip":
        """Add a distinct polynomial component to the strip."""
        if not isinstance(profile, CrossSectionStripProfile):
            raise TypeError("profile is not of type CrossSectionStripProfile")
        if any(
            item.profile_type == profile.profile_type for item in self.profiles
        ):
            raise ValueError(
                "A strip may contain each polynomial component only once"
            )
        self.profiles.append(profile)
        return self

    def get_attributes(self) -> dict:
        attributes = {"id": str(self.id)}
        if self.mode is not None:
            attributes["mode"] = enum2str(self.mode)
        return attributes

    def get_element(self) -> ET.Element:
        element = ET.Element("strip", attrib=self.get_attributes())
        if self.width is not None:
            element.append(self.width.get_element())
        for profile in sorted(
            self.profiles, key=lambda item: item.profile_type.value
        ):
            element.append(profile.get_element())
        return element


class CrossSectionSurfaceStrips:
    """Container for surface strips within a cross section surface."""

    def __init__(self) -> None:
        self.strips = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CrossSectionSurfaceStrips):
            if self.strips == other.strips:
                return True
        return False

    def add_strip(
        self, strip: CrossSectionStrip
    ) -> "CrossSectionSurfaceStrips":
        if not isinstance(strip, CrossSectionStrip):
            raise TypeError("strip is not of type CrossSectionStrip")
        self.strips.append(strip)
        return self

    def get_element(self) -> ET.Element:
        if not 1 <= len(self.strips) <= 4:
            raise ValueError(
                "A cross section surface requires one to four strips"
            )
        strip_ids = {strip.id for strip in self.strips}
        if len(strip_ids) != len(self.strips):
            raise ValueError("Strip IDs must be unique")
        for strip in self.strips:
            if abs(strip.id) == 2 and strip.id // 2 not in strip_ids:
                raise ValueError(
                    "An outer strip requires an inner strip on the same side"
                )
            if abs(strip.id) == 1:
                has_outer = strip.id * 2 in strip_ids
                if has_outer != (strip.width is not None):
                    raise ValueError(
                        "An inner strip requires a width exactly when an outer strip exists"
                    )
        element = ET.Element("surfaceStrips")
        for s in self.strips:
            element.append(s.get_element())
        return element


class CrossSectionTOffset:
    """T-offset element for a cross section surface.

    Shifts all strips relative to the road reference line in t-direction.
    """

    def __init__(self) -> None:
        self.coefficients = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CrossSectionTOffset):
            if self.coefficients == other.coefficients:
                return True
        return False

    def add_coefficients(
        self, coefficients: CrossSectionCoefficients
    ) -> "CrossSectionTOffset":
        if not isinstance(coefficients, CrossSectionCoefficients):
            raise TypeError(
                "coefficients is not of type CrossSectionCoefficients"
            )
        self.coefficients.append(coefficients)
        return self

    def get_element(self) -> ET.Element:
        element = ET.Element("tOffset")
        for coefficients in _sorted_cross_section_coefficients(
            self.coefficients
        ):
            element.append(coefficients.get_element())
        return element


class CrossSectionSurface:
    """Cross section surface defining the lateral profile.

    Parameters
    ----------
    surface_strips : CrossSectionSurfaceStrips
        The surface strips container.
    t_offset : CrossSectionTOffset, optional
        The t-offset element.
    """

    def __init__(
        self,
        surface_strips: CrossSectionSurfaceStrips,
        t_offset: Optional[CrossSectionTOffset] = None,
    ) -> None:
        self.surface_strips = surface_strips
        self.t_offset = t_offset

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CrossSectionSurface):
            if (
                self.surface_strips == other.surface_strips
                and self.t_offset == other.t_offset
            ):
                return True
        return False

    def get_element(self) -> ET.Element:
        element = ET.Element("crossSectionSurface")
        if self.t_offset is not None:
            element.append(self.t_offset.get_element())
        element.append(self.surface_strips.get_element())
        return element


class _ElevationConnectionHelper:
    def __init__(
        self,
        road: "Road",
        connection: str,
        contact_point: ContactPoint,
        lateral_offset: float,
    ) -> None:
        self.road = road
        self.connection = connection
        self.contact_point = contact_point
        self.lateral_offset = lateral_offset


class ElevationCalculator:
    """ElevationCalculator is a helper class to add elevation profiles to a
    road based on its neighbors' elevations.

    Parameters
    ----------
    main_road : Road
        The road that an elevation should be added to.

    Methods
    -------
    add_successor(road)
        Adds a successor road to the main_road. This can be done
        multiple times for junctions.
    add_predecessor(road)
        Adds a predecessor road to the main_road. This can be done
        multiple times for junctions.
    create_profile(domain)
        Tries to create a profile of the domain (elevation or
        superelevation).
    set_zero_elevation()
        Sets an elevation at zero for the main_road.
    """

    def __init__(self, main_road: "Road") -> None:
        self.main_road = main_road
        self.successors = []
        self.predecessors = []
        self._super_elevation_needed = not self.main_road.is_adjusted(
            "superelevation"
        )
        self._elevation_needed = not self.main_road.is_adjusted("elevation")
        self._extra_elevation_needed = False
        self._reset_active_roads()

    def _reset_active_roads(self) -> None:
        """Resets all active roads for a calculation."""
        self._successor_road = None
        self._predecessor_road = None
        self._predecessor_cp = None
        self._successor_cp = None
        self._successor_lateral_offset = 0
        self._predecessor_lateral_offset = 0

    def set_zero_elevation(self) -> None:
        """Sets an elevation at zero for the main_road."""
        self.main_road.add_elevation(0, 0, 0, 0, 0)
        self._elevation_needed = False

    def _calculate_lateral_elevation_offset(
        self,
        road: _ElevationConnectionHelper,
        lanesection: int,
        offsets: int,
        main_lanesection: int,
    ) -> float:
        """Calculate an elevation offset needed if a direct junction is
        present.

        Parameters
        ----------
        road : _ElevationConnectionHelper
            The road to calculate the offset from.
        lanesection : int
            The connected lanesection.
        offsets : int
            How many lanes the offset is.
        main_lanesection : int
            The lanesection of the main_road.

        Returns
        -------
        float
            The elevation offset.
        """
        s_value = 0
        tvalue = 0
        if offsets == 0:
            return 0
        sign = 1
        # this is to find out if the main_road or the connected road has most lanes to calculate the offset
        if offsets < 0 and len(
            road.road.lanes.lanesections[lanesection].rightlanes
        ) < abs(offsets):
            road = self.main_road
            lanesection = main_lanesection
            offsets = -offsets
        elif offsets > 0 and len(
            road.road.lanes.lanesections[lanesection].leftlanes
        ) < abs(offsets):
            road = self.main_road
            lanesection = main_lanesection
            offsets = -offsets
        else:
            road = road.road

        if lanesection == -1:
            s_value = road.planview.get_total_length()
        if offsets < 0:
            for lane_iter in range(abs(offsets)):
                tvalue += (
                    road.lanes.lanesections[lanesection]
                    .rightlanes[lane_iter]
                    .get_width(s_value)
                )
        else:
            for lane_iter in range(abs(offsets)):
                tvalue -= (
                    road.lanes.lanesections[lanesection]
                    .leftlanes[lane_iter]
                    .get_width(s_value)
                )
        if tvalue != 0:
            self._extra_elevation_needed = True
        return road.lateralprofile.eval_t_superelevation_at_s(s_value, tvalue)

    def _calculate_lateral_offsets_based_on_superelevation(self) -> None:
        """Calculate the elevation offsets based on superelevation.

        This method must be run as soon as any road might have been
        updated to ensure correct offsets.
        """
        for successor_road in self.successors:
            if (
                successor_road.road.predecessor
                and successor_road.road.predecessor.element_type
                == ElementType.junction
                and self.main_road.id
                in list(successor_road.road.pred_direct_junction.keys())
            ):
                lane_offsets = successor_road.road.pred_direct_junction[
                    self.main_road.id
                ]
                successor_road.lateral_offset = (
                    self._calculate_lateral_elevation_offset(
                        successor_road, 0, lane_offsets, -1
                    )
                )

            elif (
                successor_road.road.successor
                and successor_road.road.successor.element_type
                == ElementType.junction
                and self.main_road.id
                in list(successor_road.road.succ_direct_junction.keys())
            ):
                lane_offsets = successor_road.road.succ_direct_junction[
                    self.main_road.id
                ]
                successor_road.lateral_offset = (
                    self._calculate_lateral_elevation_offset(
                        successor_road, -1, lane_offsets, -1
                    )
                )
        for predecessor_road in self.predecessors:
            if (
                predecessor_road.road.successor
                and predecessor_road.road.successor.element_type
                == ElementType.junction
                and self.main_road.id
                in list(predecessor_road.road.succ_direct_junction.keys())
            ):
                lane_offsets = predecessor_road.road.succ_direct_junction[
                    self.main_road.id
                ]
                predecessor_road.lateral_offset = (
                    self._calculate_lateral_elevation_offset(
                        predecessor_road, -1, lane_offsets, 0
                    )
                )
            elif (
                predecessor_road.road.predecessor
                and predecessor_road.road.predecessor.element_type
                == ElementType.junction
                and self.main_road.id
                in list(predecessor_road.road.pred_direct_junction.keys())
            ):
                lane_offsets = predecessor_road.road.pred_direct_junction[
                    self.main_road.id
                ]
                predecessor_road.lateral_offset = (
                    self._calculate_lateral_elevation_offset(
                        predecessor_road, -1, lane_offsets, 0
                    )
                )

    def add_successor(self, successor_road: "Road") -> None:
        """Add a succeeding road to the main_road.

        This method can be called multiple times for junctions.

        Parameters
        ----------
        successor_road : Road
            A road succeeding the main_road.
        """
        successor_lateral_offset = 0
        if successor_road.predecessor is not None and (
            successor_road.predecessor.element_type == ElementType.road
            and successor_road.predecessor.element_id == self.main_road.id
            or successor_road.predecessor.element_type == ElementType.junction
            and successor_road.pred_direct_junction
            and self.main_road.id
            in list(successor_road.pred_direct_junction.keys())
            or successor_road.predecessor.element_type == ElementType.junction
            and not successor_road.pred_direct_junction
            and self.main_road.road_type
            == successor_road.predecessor.element_id
        ):
            successor_cp = ContactPoint.start
        elif successor_road.successor is not None and (
            successor_road.successor.element_type == ElementType.road
            and successor_road.successor.element_id == self.main_road.id
            or successor_road.successor.element_type == ElementType.junction
            and successor_road.succ_direct_junction
            and self.main_road.id
            in list(successor_road.succ_direct_junction.keys())
            or successor_road.successor.element_type == ElementType.junction
            and not successor_road.succ_direct_junction
            and self.main_road.road_type == successor_road.successor.element_id
        ):
            successor_cp = ContactPoint.end
        else:
            raise ValueError("could not figure out the contact point")
        self.successors.append(
            _ElevationConnectionHelper(
                successor_road,
                "successor",
                successor_cp,
                successor_lateral_offset,
            )
        )
        self._calculate_lateral_offsets_based_on_superelevation()

    def add_predecessor(self, predecessor_road: "Road") -> None:
        """Adds a preceding road to the main_road.

        This method can be called multiple times for junctions.

        Parameters
        ----------
        predecessor_road : Road
            A road preceding the main_road.
        """
        predecessor_lateral_offset = 0
        if predecessor_road.predecessor is not None and (
            predecessor_road.predecessor.element_type == ElementType.road
            and predecessor_road.predecessor.element_id == self.main_road.id
            or predecessor_road.predecessor.element_type
            == ElementType.junction
            and predecessor_road.pred_direct_junction
            and self.main_road.id
            in list(predecessor_road.pred_direct_junction.keys())
            or predecessor_road.predecessor.element_type
            == ElementType.junction
            and not predecessor_road.pred_direct_junction
            and self.main_road.road_type
            == predecessor_road.predecessor.element_id
        ):
            predecessor_cp = ContactPoint.start
            if (
                predecessor_road.predecessor.element_type
                == ElementType.junction
            ):
                pass

        elif predecessor_road.successor is not None and (
            predecessor_road.successor.element_type == ElementType.road
            and predecessor_road.successor.element_id == self.main_road.id
            or predecessor_road.successor.element_type == ElementType.junction
            and predecessor_road.succ_direct_junction
            and self.main_road.id
            in list(predecessor_road.succ_direct_junction.keys())
            or predecessor_road.successor.element_type == ElementType.junction
            and not predecessor_road.succ_direct_junction
            and self.main_road.road_type
            == predecessor_road.successor.element_id
        ):
            predecessor_cp = ContactPoint.end
            if predecessor_road.successor.element_type == ElementType.junction:
                pass
        else:
            raise ValueError("could not figure out the contact point")
        self.predecessors.append(
            _ElevationConnectionHelper(
                predecessor_road,
                "predecessor",
                predecessor_cp,
                predecessor_lateral_offset,
            )
        )
        self._calculate_lateral_offsets_based_on_superelevation()

    def _set_active_roads(self, domain: str) -> None:
        """Checks what successors/predecessor roads are adjusted in the wanted
        domain and set those for calculations.

        Parameters
        ----------
        domain : str
            The domain (elevation, or superelevation).
        """
        for successor in self.successors:
            if successor.road.is_adjusted(domain):
                self._successor_road = successor.road
                self._successor_cp = successor.contact_point
                self._successor_lateral_offset = successor.lateral_offset

        for predecessor in self.predecessors:
            if predecessor.road.is_adjusted(domain):
                self._predecessor_road = predecessor.road
                self._predecessor_cp = predecessor.contact_point
                self._predecessor_lateral_offset = predecessor.lateral_offset

    def _create_elevation(self) -> None:
        """Method that calculates and adds the elevation profile to the
        main_road based on the elevations on the predecessor or successor
        roads."""
        self._calculate_lateral_offsets_based_on_superelevation()
        self._set_active_roads("elevation")
        if self._successor_road and self._predecessor_road:
            (
                pre_s,
                pre_sign,
                suc_s,
                suc_sign,
                A,
            ) = self._get_related_data_for_double_connection()
            if self.main_road.road_type != -1:
                warn(
                    "Having automatic elevation adjustment for junction roads will yeild in ambigious results, please set the elevation for the connecting roads."
                )
            B = np.array(
                [
                    self._predecessor_road.elevationprofile.eval_at_s(pre_s)
                    + self._predecessor_lateral_offset,
                    pre_sign
                    * self._predecessor_road.elevationprofile.eval_derivative_at_s(
                        pre_s
                    ),
                    self._successor_road.elevationprofile.eval_at_s(suc_s)
                    + self._successor_lateral_offset,
                    suc_sign
                    * self._successor_road.elevationprofile.eval_derivative_at_s(
                        suc_s
                    ),
                ]
            )
            coeffs = np.linalg.solve(A, B)
            self.main_road.add_elevation(
                0, coeffs[0], coeffs[1], coeffs[2], coeffs[3]
            )
            self._elevation_needed = False
        elif self._successor_road or self._predecessor_road:
            if self.main_road.road_type != -1:
                warn(
                    "Having automatic elevation adjustment for junction roads will yeild in ambigious results, please set the elevation for the connecting roads."
                )

            (
                related_road,
                neighbor_s,
                sign,
                main_s,
            ) = self._get_related_data_for_single_connection()
            b = sign * related_road.elevationprofile.eval_derivative_at_s(
                neighbor_s
            )
            a = (
                related_road.elevationprofile.eval_at_s(neighbor_s)
                - b * main_s
                + self._successor_lateral_offset
                + self._predecessor_lateral_offset
            )
            self.main_road.add_elevation(0, a, b, 0, 0)
            self._elevation_needed = False
        self._reset_active_roads()

    def _get_related_data_for_single_connection(
        self,
    ) -> tuple["Road", float, int, float]:
        """Common functionality for both elevation and superelevation. For a
        road that has elevations on one side to adjust to.

        Returns
        -------
        related_road : Road
            The road to adjust to.
        neighbor_s : float
            S value to be used on the related_road.
        sign : int
            Sign switch.
        main_s : float
            S to be used on the main_road.
        """
        if self._successor_road:
            main_s = self.main_road.planview.get_total_length()
            related_road = self._successor_road
            if self._successor_cp == ContactPoint.start:
                neighbor_s = 0
                sign = 1
            else:
                neighbor_s = related_road.planview.get_total_length()
                sign = -1
        else:
            main_s = 0
            related_road = self._predecessor_road
            if self._predecessor_cp == ContactPoint.start:
                neighbor_s = 0
                sign = -1
            else:
                neighbor_s = related_road.planview.get_total_length()
                sign = 1
        return related_road, neighbor_s, sign, main_s

    def _get_related_data_for_double_connection(
        self,
    ) -> tuple[float, int, float, int, np.ndarray]:
        """Common functionality for both elevation and superelevation. For a
        road that has elevations on both sides to adjust to.

        Returns
        -------
        pre_s : float
            S of the predecessor.
        pre_sign : int
            Sign switch of predecessor.
        suc_s : float
            S of the successor.
        suc_sign : int
            Sign switch of successor.
        A : numpy.ndarray
            Matrix for solving continuous derivative and value.
        """
        if self._predecessor_cp == ContactPoint.start:
            pre_s = 0
            pre_sign = -1
        else:
            pre_s = self._predecessor_road.planview.get_total_length()
            pre_sign = 1
        if self._successor_cp == ContactPoint.start:
            suc_s = 0
            suc_sign = 1
        else:
            suc_s = self._successor_road.planview.get_total_length()
            suc_sign = -1
        main_s = self.main_road.planview.get_total_length()
        A = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [1, main_s, main_s**2, main_s**3],
                [0, 1, 2 * main_s, 3 * main_s**2],
            ]
        )
        return pre_s, pre_sign, suc_s, suc_sign, A

    def _create_super_elevation(self) -> None:
        self._set_active_roads("superelevation")
        if self._successor_road and self._predecessor_road:
            (
                pre_s,
                pre_sign,
                suc_s,
                suc_sign,
                A,
            ) = self._get_related_data_for_double_connection()
            if self.main_road.road_type != -1:
                warn(
                    "Having automatic elevation adjustment for junction roads will yeild in ambigious results, please set the elevation for the connecting roads."
                )
            B = np.array(
                [
                    pre_sign
                    * self._predecessor_road.lateralprofile.eval_superelevation_at_s(
                        pre_s
                    ),
                    self._predecessor_road.lateralprofile.eval_superelevation_derivative_at_s(
                        pre_s
                    ),
                    suc_sign
                    * self._successor_road.lateralprofile.eval_superelevation_at_s(
                        suc_s
                    ),
                    self._successor_road.lateralprofile.eval_superelevation_derivative_at_s(
                        suc_s
                    ),
                ]
            )
            coeffs = np.linalg.solve(A, B)
            self.main_road.add_superelevation(
                0, coeffs[0], coeffs[1], coeffs[2], coeffs[3]
            )
            self._super_elevation_needed = False

        elif self._successor_road or self._predecessor_road:
            (
                related_road,
                neighbor_s,
                sign,
                _,
            ) = self._get_related_data_for_single_connection()
            if self.main_road.road_type != -1:
                warn(
                    "Having automatic elevation adjustment for junction roads will yeild in ambigious results, please set the elevation for the connecting roads."
                )
            a = sign * related_road.lateralprofile.eval_superelevation_at_s(
                neighbor_s
            )
            self.main_road.add_superelevation(0, a, 0, 0, 0)
            self._super_elevation_needed = False

        self._reset_active_roads()

    def create_profile(self, domain: str = "elevation") -> None:
        """Main method to try to calculate an elevation or superelevation.

        Parameters
        ----------
        domain : str
            What domain to calculate (elevation or superelevation).
            Default: elevation.
        """
        if domain == "elevation":
            if self._elevation_needed:
                self._create_elevation()
        elif domain == "superelevation":
            if self.main_road.lateralprofile.cross_section_surface is not None:
                self._super_elevation_needed = False
            elif self._super_elevation_needed:
                self._create_super_elevation()
                self._calculate_lateral_offsets_based_on_superelevation()
        elif domain == "shape":
            raise NotImplementedError(
                "Shape adjustment is not implemented yet."
            )
        else:
            raise ValueError(
                "Domain can only be: elevation, superelevation, or shape, "
                f"not {domain}."
            )
