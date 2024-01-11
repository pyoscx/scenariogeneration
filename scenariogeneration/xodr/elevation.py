"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""
import xml.etree.ElementTree as ET
from .utils import XodrBase
from .enumerations import ContactPoint, ElementType
import numpy as np


class ElevationProfile(XodrBase):
    """the ElevationProfile creates the elevationProfile element of the road in opendrive,


    Attributes
    ----------
        elevations (list of _Poly3Profile):

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        add_elevation(elevation)
            adds an elevation profile to the road
    """

    def __init__(self):
        """initalize the ElevationProfile class"""
        self.elevations = []
        super().__init__()

    def __eq__(self, other):
        if isinstance(other, ElevationProfile) and super().__eq__(other):
            if self.elevations == other.elevations:
                return True
        return False

    def eval_at_s(self, s):
        return self.elevations[
            [i for i, x in enumerate(self.elevations) if x.s <= s][-1]
        ].eval_at_s(s)

    def eval_derivative_at_s(self, s):
        return self.elevations[
            [i for i, x in enumerate(self.elevations) if x.s <= s][-1]
        ].eval_derivative_at_s(s)

    def add_elevation(self, elevation):
        """adds an elevation to the ElevationProfile

        Parameters
        ----------
            elevation (_Poly3Profile): the elevation profile to add to the ElevationProfile

        """
        if not isinstance(elevation, _Poly3Profile):
            raise TypeError(
                "add_elevation requires an _Poly3Profile as input, not "
                + str(type(elevation))
            )
        self.elevations.append(elevation)
        return self

    def get_element(self):
        """returns the elementTree of the ElevationProfile"""

        element = ET.Element("elevationProfile")
        self._add_additional_data_to_element(element)
        for i in self.elevations:
            element.append(i.get_element("elevation"))

        return element


class LateralProfile(XodrBase):
    """the LateralProfile creates the elevationProfile element of the road in opendrive,


    Attributes
    ----------
        superelevation (list of _Poly3Profile): list of superelevations of the road

        shape (list of _Poly3Profile): list of shapes for the road

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        add_superelevation(superelevation)
            adds an superelevation profile to the road

        add_shape(shape)
            adds a shape to the lateral profile
    """

    def __init__(self):
        """initalize the LateralProfile class"""
        super().__init__()
        self.superelevations = []
        self.shapes = []

    def __eq__(self, other):
        if isinstance(other, LateralProfile) and super().__eq__(other):
            if (
                self.superelevations == other.superelevations
                and self.shapes == other.shapes
            ):
                return True
        return False

    def add_superelevation(self, superelevation):
        """adds an elevation to the LateralProfile

        Parameters
        ----------
            superelevation (_Poly3Profile): the elevation profile to add to the LateralProfile

        """
        if not isinstance(superelevation, _Poly3Profile):
            raise TypeError(
                "add_elevation requires an _Poly3Profile as input, not "
                + str(type(superelevation))
            )
        self.superelevations.append(superelevation)
        return self

    def eval_superelevation_at_s(self, s):
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_at_s(s)
        return 0

    def eval_t_superelevation_at_s(self, s, t):
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_t_at_s(s, t)
        return 0

    def eval_superelevation_derivative_at_s(self, s):
        if self.superelevations:
            return self.superelevations[
                [i for i, x in enumerate(self.superelevations) if x.s <= s][-1]
            ].eval_derivative_at_s(s)
        return 0

    def add_shape(self, shape):
        """adds an elevation to the LateralProfile

        Parameters
        ----------
            shape (_Poly3Profile): the elevation profile to add to the LateralProfile

        """
        if not isinstance(shape, _Poly3Profile):
            raise TypeError(
                "add_elevation requires an _Poly3Profile as input, not "
                + str(type(shape))
            )
        self.shapes.append(shape)
        return self

    def get_element(self):
        """returns the elementTree of the LateralProfile"""

        element = ET.Element("lateralProfile")
        self._add_additional_data_to_element(element)
        for i in self.superelevations:
            element.append(i.get_element("superelevation"))
        for i in self.shapes:
            element.append(i.get_element("shape"))
        return element


class _Poly3Profile:
    """the _Poly3Profile class describes a poly3  along s of a road, the elevation is described as a third degree polynomial
    elev(ds) = a + b*ds + c*ds^2 * d*ds^3
    or (if t is used)
    shape (ds) = a + b*dt + c*dt^2 * d*dt^3

    This class is used for both elevation, superElevation and shape

    Parameters
    ----------
        s (float): s start coordinate of the elevation

        a (float): a coefficient of the polynomial

        b (float): b coefficient of the polynomial

        c (float): c coefficient of the polynomial

        d (float): d coefficient of the polynomial

        t (float): t variable (used only for shape)
            Default: None

    Attributes
    ----------
        s (float): s start coordinate of the elevation

        a (float): a coefficient of the polynomial

        b (float): b coefficient of the polynomial

        c (float): c coefficient of the polynomial

        d (float): d coefficient of the polynomial

        t (float): t variable (used only for shape)

    Methods
    -------
        get_element(elementname)
            Returns the full ElementTree of the class

        get_attributes()
            Returns the attributes of the class

    """

    def __init__(self, s, a, b, c, d, t=None, elevation_type="elevation"):
        """initalize the Elevation class

        Parameters
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

            t (float): t variable (used only for shape)
                Default: None

            elevation_type (str): describing type of elevation for t value evaluations
                Default: elevation

        """
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.t = t
        if elevation_type not in ["elevation", "superelevation", "shape"]:
            raise ValueError(
                "elevation_type can only be: geometry, elevation, superelevation, or shape , not "
                + elevation_type
            )
        self.elevation_type = elevation_type

    def __eq__(self, other):
        if isinstance(other, _Poly3Profile):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def eval_at_s(self, s):
        if s < self.s:
            raise ValueError("when evaluating elevation, s must be larger than s_start")
        return (
            self.a
            + self.b * (s - self.s)
            + self.c * (s - self.s) ** 2
            + self.d * (s - self.s) ** 3
        )

    def eval_t_at_s(self, s, t):
        if self.elevation_type == "elevation":
            return self.eval_at_s(s)
        elif self.elevation_type == "superelevation":
            return t * np.sin(self.eval_at_s(s))
        elif self.elevation_type == "shape":
            raise NotImplementedError(
                "t calculations for shape is not implemented yet."
            )
        else:
            raise ValueError(
                "elevation_type can only be: geometry, elevation, superelevation, or shape , not "
                + self.elevation_type
            )

    def eval_derivative_at_s(self, s):
        if s < self.s:
            raise ValueError("when evaluating elevation, s must be larger than s_start")
        return self.b + 2 * self.c * (s - self.s) + 3 * self.d * (s - self.s) ** 2

    def get_attributes(self):
        """returns the attributes of the Elevetion"""

        retdict = {}
        retdict["s"] = str(self.s)
        if self.t != None:
            retdict["t"] = str(self.t)
        retdict["a"] = str(self.a)
        retdict["b"] = str(self.b)
        retdict["c"] = str(self.c)
        retdict["d"] = str(self.d)
        return retdict

    def get_element(self, elementname=None):
        """returns the elementTree of the Elevation

        Parameters
        ----------
            elementname (str): name of the element, can be elevation, superelevation or shape
                Default: same as elevation_type
        """
        if elementname is None:
            elementname = self.elevation_type

        if elementname == "shape" and self.t == None:
            raise ValueError("When shape is used, the t value has to be set.")
        elif elementname != "shape" and self.t != None:
            raise ValueError("When shape is not used, the t value should not be set.")

        element = ET.Element(elementname, attrib=self.get_attributes())

        return element


class _ElevationConnectionHelper:
    def __init__(self, road, connection, contact_point, lateral_offset):
        self.road = road
        self.connection = connection
        self.contact_point = contact_point
        self.lateral_offset = lateral_offset


class ElevationCalculator:
    """ElevationCalculator is a helper class to add elevation profiles to a road based on its neighbors
    elevations.

    Parameters
    ----------
        main_road (Road): the road that an elevation should be added to

    Methods
    -------
        add_successor (Road): adds a successor road to the main_road with an elevation profile

        add_predecessor (Road): adds a predecessor road to the main_road with an elevation profile
    """

    ## TODO: This should be rewritten.. the loop in opendrive could just be fixed and made easier.
    # For superelevation cases, add multiple successors/predecessors. and a flag that extra elevation is needed if junctions are involved.. This will be fun...

    def __init__(self, main_road):  # , domain = "elevation"):
        self.main_road = main_road
        self.successors = []
        self.predecessors = []
        self._super_elevation_needed = not self.main_road.is_adjusted("superelevation")
        self._elevation_needed = not self.main_road.is_adjusted("elevation")

        self._reset_active_roads()

    def _reset_active_roads(self):
        self._successor_road = None
        self._predecessor_road = None
        self._predecessor_cp = None
        self._successor_cp = None
        self._successor_lateral_offset = 0
        self._predecessor_lateral_offset = 0

    def _calculate_lateral_offset(self, road, lanesection, offsets):
        s_value = 0
        tvalue = 0
        if lanesection == -1:
            s_value = road.planview.get_total_length()
        if offsets < 0:
            for lane_iter in range(abs(offsets)):
                tvalue += (
                    self.main_road.lanes.lanesections[lanesection]
                    .rightlanes[lane_iter]
                    .get_width(s_value)
                )
        return tvalue

    def _calculate_lateral_offsets_based_on_superelevation(self):
        for successor_road in self.successors:
            if (
                successor_road.road.predecessor
                and successor_road.road.predecessor.element_type == ElementType.junction
            ):
                if successor_road.road.pred_direct_junction:
                    lane_offsets = successor_road.road.pred_direct_junction[
                        self.main_road.id
                    ]
                    successor_road.lateral_offset = (
                        self.main_road.lateralprofile.eval_t_superelevation_at_s(
                            0,
                            self._calculate_lateral_offset(
                                successor_road, 0, lane_offsets
                            ),
                        )
                    )
                else:
                    pass

    def add_successor(self, successor_road):
        successor_lateral_offset = 0
        if successor_road.predecessor is not None and (
            successor_road.predecessor.element_type == ElementType.road
            and successor_road.predecessor.element_id == self.main_road.id
            or successor_road.predecessor.element_type == ElementType.junction
            and successor_road.pred_direct_junction
            and self.main_road.id in list(successor_road.pred_direct_junction.keys())
            or successor_road.predecessor.element_type == ElementType.junction
            and not successor_road.pred_direct_junction
            and self.main_road.road_type == successor_road.predecessor.element_id
        ):
            successor_cp = ContactPoint.start
        elif successor_road.successor is not None and (
            successor_road.successor.element_type == ElementType.road
            and successor_road.successor.element_id == self.main_road.id
            or successor_road.successor.element_type == ElementType.junction
            and successor_road.succ_direct_junction
            and self.main_road.id in list(successor_road.succ_direct_junction.keys())
            or successor_road.successor.element_type == ElementType.junction
            and not successor_road.succ_direct_junction
            and self.main_road.road_type == successor_road.successor.element_id
        ):
            successor_cp = ContactPoint.end
        else:
            raise ValueError("could not figure out the contact point")
        self.successors.append(
            _ElevationConnectionHelper(
                successor_road, "successor", successor_cp, successor_lateral_offset
            )
        )
        self._calculate_lateral_offsets_based_on_superelevation()

    def add_predecessor(self, predecessor_road):
        predecessor_lateral_offset = 0
        if predecessor_road.predecessor is not None and (
            predecessor_road.predecessor.element_type == ElementType.road
            and predecessor_road.predecessor.element_id == self.main_road.id
            or predecessor_road.predecessor.element_type == ElementType.junction
            and predecessor_road.pred_direct_junction
            and self.main_road.id in list(predecessor_road.pred_direct_junction.keys())
            or predecessor_road.predecessor.element_type == ElementType.junction
            and not predecessor_road.pred_direct_junction
            and self.main_road.road_type == predecessor_road.predecessor.element_id
        ):
            predecessor_cp = ContactPoint.start
            if predecessor_road.predecessor.element_type == ElementType.junction:
                pass

        elif predecessor_road.successor is not None and (
            predecessor_road.successor.element_type == ElementType.road
            and predecessor_road.successor.element_id == self.main_road.id
            or predecessor_road.successor.element_type == ElementType.junction
            and predecessor_road.succ_direct_junction
            and self.main_road.id in list(predecessor_road.succ_direct_junction.keys())
            or predecessor_road.successor.element_type == ElementType.junction
            and not predecessor_road.succ_direct_junction
            and self.main_road.road_type == predecessor_road.successor.element_id
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

    def _set_active_roads(self, domain):
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

    def _create_elevation(self):
        self._set_active_roads("elevation")
        if self._successor_road and self._predecessor_road:
            (
                pre_s,
                pre_sign,
                suc_s,
                suc_sign,
                A,
            ) = self._get_related_data_for_double_connection()

            B = np.array(
                [
                    self._predecessor_road.elevationprofile.eval_at_s(pre_s),
                    pre_sign
                    * self._predecessor_road.elevationprofile.eval_derivative_at_s(
                        pre_s
                    ),
                    self._successor_road.elevationprofile.eval_at_s(suc_s),
                    suc_sign
                    * self._successor_road.elevationprofile.eval_derivative_at_s(suc_s),
                ]
            )
            coeffs = np.linalg.solve(A, B)
            self.main_road.add_elevation(0, coeffs[0], coeffs[1], coeffs[2], coeffs[3])
            self._elevation_needed = False
        elif self._successor_road or self._predecessor_road:
            (
                related_road,
                neighbor_s,
                sign,
                main_s,
            ) = self._get_related_data_for_single_connection()
            b = sign * related_road.elevationprofile.eval_derivative_at_s(neighbor_s)
            a = (
                related_road.elevationprofile.eval_at_s(neighbor_s)
                - b * main_s
                + self._successor_lateral_offset
            )
            self.main_road.add_elevation(0, a, b, 0, 0)
            self._elevation_needed = False
        self._reset_active_roads()

    def _get_related_data_for_single_connection(self):
        """common functionality for both elevation and superelevation
        For a road that has elevations on one side to adjust to

        Returns
        -------
            related_road - the road to adjust to
            neighbor_s - s value to be used on the related_road
            sign - sign switch
            main_s - s to be used on the main_road
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

    def _get_related_data_for_double_connection(self):
        """common functionality for both elevation and superelevation
        For a road that has elevations on both sides to adjust to

        Returns
        -------
        pre_s - s of the predecessor
        pre_sign - sign switch of predecessor
        suc_s - s of the successor
        suc_sign - sign switch of successor
        A - Matrix for solving continuous derivative and value

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

    def _create_super_elevation(self):
        self._set_active_roads("superelevation")
        if self._successor_road and self._predecessor_road:
            (
                pre_s,
                pre_sign,
                suc_s,
                suc_sign,
                A,
            ) = self._get_related_data_for_double_connection()

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

            a = sign * related_road.lateralprofile.eval_superelevation_at_s(neighbor_s)
            self.main_road.add_superelevation(0, a, 0, 0, 0)
            self._super_elevation_needed = False

        self._reset_active_roads()

    def create_profile(self, domain="elevation"):
        if domain == "elevation":
            if self._elevation_needed:
                self._create_elevation()
        elif domain == "superelevation":
            if self._super_elevation_needed:
                self._create_super_elevation()
                self._calculate_lateral_offsets_based_on_superelevation()
        elif domain == "shape":
            raise NotImplementedError("shape adjustment is not implemented yet")
        else:
            raise ValueError(
                "domain can only be: geometry, elevation, superelevation, or shape , not "
                + domain
            )


# class ElevationCalculator:
#     """ElevationCalculator is a helper class to add elevation profiles to a road based on its neighbors
#     elevations.

#     Parameters
#     ----------
#         main_road (Road): the road that an elevation should be added to

#     Methods
#     -------
#         add_successor (Road): adds a successor road to the main_road with an elevation profile

#         add_predecessor (Road): adds a predecessor road to the main_road with an elevation profile
#     """


#     ## TODO: This should be rewritten.. the loop in opendrive could just be fixed and made easier.
#     # For superelevation cases, add multiple successors/predecessors. and a flag that extra elevation is needed if junctions are involved.. This will be fun...

#     def __init__(self, main_road, domain = "elevation"):
#         self.main_road = main_road
#         successor_road = None
#         self.predecessor_road = None
#         self.predecessor_cp = None
#         self.successor_cp = None
#         self._successor_lateral_offset = 0
#         self._predecessor_lateral_offset = 0
#         if domain not in ["elevation", "superelevation", "shape"]:
#             raise ValueError(
#                 "domain can only be: geometry, elevation, superelevation, or shape , not "
#                 + domain
#             )
#         self.domain = domain


#     def add_successor(self, successor_road):
#         if successor_road.is_adjusted(self.domain):
#             successor_road = successor_road
#             if successor_road.predecessor is not None and (successor_road.predecessor.element_type == ElementType.road and successor_road.predecessor.element_id == self.main_road.id or successor_road.predecessor.element_type == ElementType.junction and successor_road.pred_direct_junction and self.main_road.id in list(successor_road.pred_direct_junction.keys()) or successor_road.predecessor.element_type == ElementType.junction and not successor_road.pred_direct_junction and self.main_road.road_type == successor_road.predecessor.element_id):
#                 self.successor_cp = ContactPoint.start
#                 if self.domain == "elevation":
#                     if successor_road.predecessor.element_type == ElementType.junction:
#                         if successor_road.pred_direct_junction:
#                             lane_offsets = successor_road.pred_direct_junction[self.main_road.id]
#                             if lane_offsets < 0:
#                                 tvalue = 0
#                                 for lane_iter in range(abs(lane_offsets)):
#                                     tvalue += (
#                                         self.main_road
#                                         .lanes.lanesections[0]
#                                         .rightlanes[lane_iter]
#                                         .get_width(0)
#                                     )
#                             self._successor_lateral_offset = self.main_road.lateralprofile.eval_t_superelevation_at_s(0, tvalue)
#                         else:
#                             pass
#             elif (successor_road.successor is not None and (successor_road.successor.element_type == ElementType.road and successor_road.successor.element_id == self.main_road.id or successor_road.successor.element_type == ElementType.junction and successor_road.succ_direct_junction and self.main_road.id in list(successor_road.succ_direct_junction.keys()) or successor_road.successor.element_type == ElementType.junction and not successor_road.succ_direct_junction and self.main_road.road_type == successor_road.successor.element_id)):
#                 self.successor_cp = ContactPoint.end
#                 if successor_road.predecessor.element_type == ElementType.junction:
#                     pass
#             else:
#                 raise ValueError("could not figure out the contact point")

#     def add_predecessor(self, predecessor_road):
#         if predecessor_road.is_adjusted(self.domain):
#             self.predecessor_road = predecessor_road

#             if self.predecessor_road.predecessor is not None and (self.predecessor_road.predecessor.element_type == ElementType.road and self.predecessor_road.predecessor.element_id == self.main_road.id or self.predecessor_road.predecessor.element_type == ElementType.junction and self.predecessor_road.pred_direct_junction and self.main_road.id in list(self.predecessor_road.pred_direct_junction.keys()) or self.predecessor_road.predecessor.element_type == ElementType.junction and not self.predecessor_road.pred_direct_junction and self.main_road.road_type == self.predecessor_road.predecessor.element_id):
#                 self.predecessor_cp = ContactPoint.start
#                 if self.predecessor_road.predecessor.element_type == ElementType.junction:
#                     pass

#             elif (self.predecessor_road.successor is not None and (self.predecessor_road.successor.element_type == ElementType.road and self.predecessor_road.successor.element_id == self.main_road.id or self.predecessor_road.successor.element_type == ElementType.junction and self.predecessor_road.succ_direct_junction and self.main_road.id in list(self.predecessor_road.succ_direct_junction.keys()) or self.predecessor_road.successor.element_type == ElementType.junction and not self.predecessor_road.succ_direct_junction and self.main_road.road_type == self.predecessor_road.successor.element_id)):
#                 self.predecessor_cp = ContactPoint.end
#                 if self.predecessor_road.successor.element_type == ElementType.junction:
#                     pass
#             else:
#                 raise ValueError("could not figure out the contact point")


#     def _create_elevation(self):
#         if successor_road and self.predecessor_road:
#             (
#                 pre_s,
#                 pre_sign,
#                 suc_s,
#                 suc_sign,
#                 A,
#             ) = self._get_related_data_for_double_connection()

#             B = np.array(
#                 [
#                     self.predecessor_road.elevationprofile.eval_at_s(pre_s),
#                     pre_sign
#                     * self.predecessor_road.elevationprofile.eval_derivative_at_s(
#                         pre_s
#                     ),
#                     successor_road.elevationprofile.eval_at_s(suc_s),
#                     suc_sign
#                     * successor_road.elevationprofile.eval_derivative_at_s(suc_s),
#                 ]
#             )
#             coeffs = np.linalg.solve(A, B)
#             self.main_road.add_elevation(0, coeffs[0], coeffs[1], coeffs[2], coeffs[3])

#         elif successor_road or self.predecessor_road:
#             (
#                 related_road,
#                 neighbor_s,
#                 sign,
#                 main_s,
#             ) = self._get_related_data_for_single_connection()
#             b = sign * related_road.elevationprofile.eval_derivative_at_s(neighbor_s)
#             a = related_road.elevationprofile.eval_at_s(neighbor_s) - b * main_s + self._successor_lateral_offset
#             self.main_road.add_elevation(0, a, b, 0, 0)

#     def _get_related_data_for_single_connection(self):
#         """common functionality for both elevation and superelevation
#         For a road that has elevations on one side to adjust to

#         Returns
#         -------
#             related_road - the road to adjust to
#             neighbor_s - s value to be used on the related_road
#             sign - sign switch
#             main_s - s to be used on the main_road
#         """
#         if successor_road:
#             main_s = self.main_road.planview.get_total_length()
#             related_road = successor_road
#             if self.successor_cp == ContactPoint.start:
#                 neighbor_s = 0
#                 sign = 1
#             else:
#                 neighbor_s = related_road.planview.get_total_length()
#                 sign = -1
#         else:
#             main_s = 0
#             related_road = self.predecessor_road
#             if self.predecessor_cp == ContactPoint.start:
#                 neighbor_s = 0
#                 sign = -1
#             else:
#                 neighbor_s = related_road.planview.get_total_length()
#                 sign = 1
#         return related_road, neighbor_s, sign, main_s

#     def _get_related_data_for_double_connection(self):
#         """common functionality for both elevation and superelevation
#         For a road that has elevations on both sides to adjust to

#         Returns
#         -------
#         pre_s - s of the predecessor
#         pre_sign - sign switch of predecessor
#         suc_s - s of the successor
#         suc_sign - sign switch of successor
#         A - Matrix for solving continuous derivative and value

#         """
#         if self.predecessor_cp == ContactPoint.start:
#             pre_s = 0
#             pre_sign = -1
#         else:
#             pre_s = self.predecessor_road.planview.get_total_length()
#             pre_sign = 1
#         if self.successor_cp == ContactPoint.start:
#             suc_s = 0
#             suc_sign = 1
#         else:
#             suc_s = successor_road.planview.get_total_length()
#             suc_sign = -1
#         main_s = self.main_road.planview.get_total_length()
#         A = np.array(
#             [
#                 [1, 0, 0, 0],
#                 [0, 1, 0, 0],
#                 [1, main_s, main_s**2, main_s**3],
#                 [0, 1, 2 * main_s, 3 * main_s**2],
#             ]
#         )
#         return pre_s, pre_sign, suc_s, suc_sign, A

#     def _create_super_elevation(self):
#         if successor_road and self.predecessor_road:
#             (
#                 pre_s,
#                 pre_sign,
#                 suc_s,
#                 suc_sign,
#                 A,
#             ) = self._get_related_data_for_double_connection()

#             B = np.array(
#                 [
#                     pre_sign
#                     * self.predecessor_road.lateralprofile.eval_superelevation_at_s(
#                         pre_s
#                     ),
#                     self.predecessor_road.lateralprofile.eval_superelevation_derivative_at_s(
#                         pre_s
#                     ),
#                     suc_sign
#                     * successor_road.lateralprofile.eval_superelevation_at_s(
#                         suc_s
#                     ),
#                     successor_road.lateralprofile.eval_superelevation_derivative_at_s(
#                         suc_s
#                     ),
#                 ]
#             )
#             coeffs = np.linalg.solve(A, B)
#             self.main_road.add_superelevation(
#                 0, coeffs[0], coeffs[1], coeffs[2], coeffs[3]
#             )

#         elif successor_road or self.predecessor_road:
#             (
#                 related_road,
#                 neighbor_s,
#                 sign,
#                 _,
#             ) = self._get_related_data_for_single_connection()

#             a = sign * related_road.lateralprofile.eval_superelevation_at_s(neighbor_s)
#             self.main_road.add_superelevation(0, a, 0, 0, 0)

#     def create_profile(self):#, domain="elevation"):
#         if self.domain == "elevation":
#             self._create_elevation()
#         elif self.domain == "superelevation":
#             self._create_super_elevation()
#         elif self.domain == "shape":
#             raise NotImplementedError("shape adjustment is not implemented yet")
