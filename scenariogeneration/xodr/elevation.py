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

    def __init__(self, s, a, b, c, d, t=None):
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


        """
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.t = t

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

    def get_element(self, elementname):
        """returns the elementTree of the Elevation

        Parameters
        ----------
            elementname (str): name of the element, can be elevation, superelevation or shape
        """
        if elementname == "shape" and self.t == None:
            raise ValueError("When shape is used, the t value has to be set.")
        elif elementname != "shape" and self.t != None:
            raise ValueError("When shape is not used, the t value should not be set.")

        element = ET.Element(elementname, attrib=self.get_attributes())

        return element


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

    def __init__(self, main_road):
        self.main_road = main_road
        self.successor_road = None
        self.predecessor_road = None
        self.predecessor_cp = None
        self.successor_cp = None

    def add_successor(self, successor_road):
        if successor_road._elevation_adjusted:
            self.successor_road = successor_road
            if (
                self.successor_road.predecessor is not None
                and self.successor_road.predecessor.element_id == self.main_road.id
            ):
                self.successor_cp = ContactPoint.start
            elif (
                self.successor_road.successor is not None
                and self.successor_road.successor.element_id == self.main_road.id
            ):
                self.successor_cp = ContactPoint.end

    def add_predecessor(self, predecessor_road):
        if predecessor_road._elevation_adjusted:
            self.predecessor_road = predecessor_road

            if (
                self.predecessor_road.predecessor is not None
                and self.predecessor_road.predecessor.element_id == self.main_road.id
            ):
                self.predecessor_cp = ContactPoint.start
            elif (
                self.predecessor_road.successor is not None
                and self.predecessor_road.successor.element_id == self.main_road.id
            ):
                self.predecessor_cp = ContactPoint.end

    def _create_elevation(self):
        if self.successor_road and self.predecessor_road:
            if self.predecessor_cp == ContactPoint.start:
                pre_s = 0
                pre_sign = -1
            else:
                pre_s = self.predecessor_road.planview.get_total_length()
                pre_sign = 1
            if self.successor_cp == ContactPoint.start:
                suc_s = 0
                suc_sign = 1
            else:
                suc_s = self.successor_road.planview.get_total_length()
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
            B = np.array(
                [
                    self.predecessor_road.elevationprofile.eval_at_s(pre_s),
                    pre_sign
                    * self.predecessor_road.elevationprofile.eval_derivative_at_s(
                        pre_s
                    ),
                    self.successor_road.elevationprofile.eval_at_s(suc_s),
                    suc_sign
                    * self.successor_road.elevationprofile.eval_derivative_at_s(suc_s),
                ]
            )
            coeffs = np.linalg.solve(A, B)
            self.main_road.add_elevation(0, coeffs[0], coeffs[1], coeffs[2], coeffs[3])

        elif self.successor_road or self.predecessor_road:
            if self.successor_road:
                main_s = self.main_road.planview.get_total_length()
                related_road = self.successor_road
                if self.successor_cp == ContactPoint.start:
                    neighbor_s = 0
                    sign = 1
                else:
                    neighbor_s = related_road.planview.get_total_length()
                    sign = -1
            else:
                main_s = 0
                related_road = self.predecessor_road
                if self.predecessor_cp == ContactPoint.start:
                    neighbor_s = 0
                    sign = -1
                else:
                    neighbor_s = related_road.planview.get_total_length()
                    sign = 1

            b = sign * related_road.elevationprofile.eval_derivative_at_s(neighbor_s)
            a = related_road.elevationprofile.eval_at_s(neighbor_s) - b * main_s
            self.main_road.add_elevation(0, a, b, 0, 0)

    def create_elevation_profiles(self):
        self._create_elevation()
