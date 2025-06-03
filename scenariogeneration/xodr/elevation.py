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

from .enumerations import ContactPoint, ElementType
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LateralProfile) and super().__eq__(other):
            if (
                self.superelevations == other.superelevations
                and self.shapes == other.shapes
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
        self.shapes.append(shape)
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
            if self._super_elevation_needed:
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
