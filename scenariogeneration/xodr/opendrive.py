"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET


from ..helpers import printToFile, enum2str
from .links import _Link, _Links, create_lane_links, Junction
from .enumerations import (
    ElementType,
    ContactPoint,
    RoadSide,
    TrafficRule,
    JunctionType,
    enumchecker,
    RoadType,
)
from .exceptions import (
    UndefinedRoadNetwork,
    RoadsAndLanesNotAdjusted,
    IdAlreadyExists,
    MixingDrivingDirection,
    GeneralIssueInputArguments,
)
from .elevation import (
    LateralProfile,
    ElevationProfile,
    _Poly3Profile,
    ElevationCalculator,
)
from .exceptions import (
    UndefinedRoadNetwork,
    RoadsAndLanesNotAdjusted,
    IdAlreadyExists,
    MixingDrivingDirection,
    GeneralIssueInputArguments,
)
from .lane import Lanes
from .signals_objects import Object, Signal, Tunnel, SignalReference
from .utils import get_lane_sec_and_s_for_lane_calc
from .geometry import AdjustablePlanview, Spiral, PlanView
from .lane_def import LaneDef, create_lanes_merge_split, std_roadmark_solid
import pyclothoids as pcloth
import datetime as dt
from itertools import combinations
import numpy as np
import copy as cpy
from .utils import XodrBase


class _Header:
    """Header creates the header of the OpenDrive file

    Parameters
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE

        revMinor (str): minor revision of OpenDRIVE

        geo_reference (str): The information for geographic reference of a database

    Attributes
    ----------
        name (str): name of the scenario

        revMajor (str): major revision of OpenDRIVE

        revMinor (str): minor revision of OpenDRIVE

        geo_reference (str): The information for geographic reference of a database

    Methods
    -------
        get_element()
            Returns the full ElementTree of FileHeader

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

    """

    def __init__(self, name, revMajor, revMinor, geo_reference=None):
        """Initalize the Header

         Parameters
        ----------
            name (str): name of the road

            revMajor (str): major revision of OpenDRIVE

            revMinor (str): minor revision of OpenDRIVE

            geo_reference (str): The information for geographic reference of a database
                Default: None

        """
        self.name = name
        self.revMajor = revMajor
        self.revMinor = revMinor
        self.geo_reference = geo_reference

    def __eq__(self, other):
        if isinstance(other, _Header):
            if (
                self.name == other.name
                and self.revMajor == other.revMajor
                and self.revMinor == other.revMinor
                and self.geo_reference == other.geo_reference
            ):
                return True
        return False

    def get_attributes(self):
        """returns the attributes as a dict of the FileHeader"""
        retdict = {}
        retdict["name"] = self.name
        retdict["revMajor"] = str(self.revMajor)
        retdict["revMinor"] = str(self.revMinor)
        retdict["date"] = str(dt.datetime.now())
        retdict["north"] = "0.0"
        retdict["south"] = "0.0"
        retdict["east"] = "0.0"
        retdict["west"] = "0.0"
        return retdict

    def get_element(self):
        """returns the elementTree of the FileHeader"""
        element = ET.Element("header", attrib=self.get_attributes())

        if self.geo_reference is not None:
            geo_reference_element = ET.SubElement(element, "geoReference")
            geo_reference_element.text = self.geo_reference

        return element


class Road(XodrBase):
    """Road defines the road element of OpenDrive

    Parameters
    ----------
        road_id (int): identifier of the road

        planview (PlanView): the planview of the road

        lanes (Lanes): the lanes of the road

        road_type (int): type of road (junction)
            Default: -1

        name (str): name of the road (optional)

        rule (TrafficRule): traffic rule (optional)

        signals (Signals): Contains a list of signal objects (optional)

    Attributes
    ----------
        id (int): identifier of the road

        planview (PlanView): the planview of the road

        lanes (Lanes): the lanes of the road

        road_type (int): type of road (junction)
            Default: -1

        name (str): name of the road

        rule (TrafficRule): traffic rule

        signals (Signal): Contains a list of Signal objects

        objects (Object): Contains a list of Object objects

        types (list of _Type): contans a list or _Type objects (optional)

        elevationprofile (ElevationProfile): the elevation profile of the road

        lateralprofile (LateralProfile): the lateral profile of the road
    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_successor (element_type,element_id,contact_point,lane_offset,direct_junction)
            adds a successor for the road

        add_predecessor (element_type,element_id,contact_point,lane_offset,direct_junction)
            adds a predecessor for the road

        add_neighbor (element_type,element_id,direction)
            adds a neighbor for the road

        add_object (road_object)
            adds an object to the road

        add_elevation(s,a,b,c,d)
            adds an elevation profile to the road

        add_superelevation(s,a,b,c,d)
            adds a superelevation to the road

        add_shape(s,t,a,b,c,d,e)
            adds a lateral shape to the road

        add_object_roadside (road_object_prototype, repeatDistance, sOffset=0, tOffset=0, side=RoadSide.both)
            adds an repeated object to the road

        add_signal (signal)
            adds a signal to the road

        get_end_point ()
            returns the x, y and heading at the end of the road
    """

    def __init__(
        self, road_id, planview, lanes, road_type=-1, name=None, rule=TrafficRule.RHT
    ):
        """initalize the Road

        Parameters
        ----------
            road_id (int): identifier of the road

            planview (PlanView): the planview of the road

            lanes (Lanes): the lanes of the road

            road_type (int): type of road (junction)
                Default: -1

            name (str): name of the road (optional)

            rule (TrafficRule): traffic rule (optional)

        """
        super().__init__()
        self.id = road_id
        if not (
            isinstance(planview, PlanView) or isinstance(planview, AdjustablePlanview)
        ):
            raise TypeError(
                "planview input is not of type PlanView or AdjustablePlanview"
            )
        self.planview = planview
        if not isinstance(lanes, Lanes):
            raise TypeError(
                "planview input is not of type PlanView or AdjustablePlanview"
            )
        self.lanes = lanes
        self.road_type = road_type
        self.name = name
        self.rule = enumchecker(rule, TrafficRule)
        self.links = _Links()
        self._neighbor_added = 0
        self.successor = None
        self.predecessor = None
        self.lane_offset_suc = {}
        self.lane_offset_pred = {}
        self.succ_direct_junction = {}
        self.pred_direct_junction = {}

        self.objects = []
        self.signals = []
        self.types = []
        self.elevationprofile = ElevationProfile()
        self.lateralprofile = LateralProfile()
        self._elevation_adjusted = False
        self._superelevation_adjusted = False
        self._shape_adjusted = False

    def __eq__(self, other):
        if isinstance(other, Road) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.objects == other.objects
                and self.signals == other.signals
                and self.types == other.types
                and self.links == other.links
                and self.planview == other.planview
                and self.lanes == other.lanes
                and self.elevationprofile == other.elevationprofile
                and self.lateralprofile == other.lateralprofile
                and self.predecessor == other.predecessor
                and self.successor == other.successor
                and self.lane_offset_suc == other.lane_offset_suc
                and self.lane_offset_pred == other.lane_offset_pred
                and self.pred_direct_junction == other.pred_direct_junction
                and self.succ_direct_junction == other.succ_direct_junction
            ):
                return True
        return False

    def is_adjusted(self, domain="planview"):
        """help method to check if the road has been properly defined in the domain

        Parameters
        ----------
            domain (str): the domain to check, ok values: planview, elevation, superelevation, or shape
                Default: planview

        Returns
        -------
            boolean
        """
        if domain == "planview":
            return self.planview.adjusted
        elif domain == "elevation":
            return self._elevation_adjusted
        elif domain == "superelevation":
            return self._superelevation_adjusted
        elif domain == "shape":
            return self._shape_adjusted
        else:
            raise ValueError(
                "domain can only be: geometry, elevation, superelevation, or shape , not "
                + domain
            )

    def add_successor(
        self,
        element_type,
        element_id,
        contact_point=None,
        lane_offset=0,
    ):
        """add_successor adds a successor link to the road

        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the link

            direct_juction (dict {int, int}): list of dicts, {successor_id, lane offset}

        """

        if self.successor:
            raise ValueError("only one successor is allowed")
        self.successor = _Link(
            "successor",
            element_id,
            enumchecker(element_type, ElementType),
            contact_point,
        )
        self.links.add_link(self.successor)
        self.lane_offset_suc[str(element_id)] = lane_offset
        return self

    def add_predecessor(
        self,
        element_type,
        element_id,
        contact_point=None,
        lane_offset=0,
    ):
        """add_successor adds a successor link to the road

        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the link

            direct_juction (dict {int, int}):  {successor_id, lane offset}

        """
        if self.predecessor:
            raise ValueError("only one predecessor is allowed")
        self.predecessor = _Link(
            "predecessor",
            element_id,
            enumchecker(element_type, ElementType),
            contact_point,
        )
        self.links.add_link(self.predecessor)
        self.lane_offset_pred[str(element_id)] = lane_offset
        return self

    def add_neighbor(self, element_type, element_id, direction):
        """add_neighbor adds a neighbor to a road

        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            direction (Direction): the direction of the link
        """
        if self._neighbor_added > 1:
            raise ValueError("only two neighbors are allowed")
        suc = _Link("neighbor", element_id, element_type, direction=direction)

        self.links.add_link(suc)
        self._neighbor_added += 1
        return self

    def add_elevation(self, s, a, b, c, d):
        """ads an elevation profile to the road (3-degree polynomial)

        Parameters
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial
        """
        self.elevationprofile.add_elevation(
            _Poly3Profile(s, a, b, c, d, elevation_type="elevation")
        )
        self._elevation_adjusted = True
        return self

    def add_superelevation(self, s, a, b, c, d):
        """ads a superelevation profile to the road (3-degree polynomial)

        Parameters
        ----------
            s (float): s start coordinate of the superelevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial
        """
        self.lateralprofile.add_superelevation(
            _Poly3Profile(s, a, b, c, d, elevation_type="superelevation")
        )
        self._superelevation_adjusted = True
        return self

    def add_shape(self, s, t, a, b, c, d):
        """ads a superelevation profile to the road (3-degree polynomial)

        Parameters
        ----------
            s (float): s start coordinate of the superelevation

            t (flaot): the t start coordinate of the lateral profile

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial
        """
        self.lateralprofile.add_shape(
            _Poly3Profile(s, a, b, c, d, t, elevation_type="shape")
        )
        self._shape_adjusted = True
        return self

    def add_object(self, road_object):
        """add_object adds an object to a road and calls a function that ensures unique IDs

        Parameters
        ----------
            road_object (Object/list(Object)): object(s) to be added to road

        """
        if isinstance(road_object, list):
            for single_object in road_object:
                if not isinstance(single_object, Object):
                    raise TypeError(
                        "road_object contains elements that are not of type Object"
                    )
                single_object._update_id()

            self.objects = self.objects + road_object
        else:
            if not isinstance(road_object, Object):
                raise TypeError("road_object is not of type Object")
            road_object._update_id()
            self.objects.append(road_object)
        return self

    def add_tunnel(self, tunnel):
        """Adds a tunnel or list of tunnels to a road

        Parameters
        ----------
            tunnel (Tunnel/list(Tunnel)): tunnel(s) to be added to road

        """
        if isinstance(tunnel, list):
            if any([not isinstance(x, Tunnel) for x in tunnel]):
                raise TypeError("tunnel contains elements that are not of type Tunnel")
            self.objects.extend(tunnel)
        else:
            if not isinstance(tunnel, Tunnel):
                raise TypeError("tunnel is not of type Tunnel")
            self.objects.append(tunnel)
        return self

    def add_object_roadside(
        self,
        road_object_prototype,
        repeatDistance,
        sOffset=0,
        tOffset=0,
        side=RoadSide.both,
        widthStart=None,
        widthEnd=None,
        lengthStart=None,
        lengthEnd=None,
        radiusStart=None,
        radiusEnd=None,
    ):
        """add_object_roadside is a convenience function to add a repeating object on side of the road,
            which can only be used after adjust_roads_and_lanes() has been performed

        Parameters
        ----------
            road_object_prototype (Object): object that will be used as a basis for generation

            repeatDistance (float): distance between repeated Objects, 0 for continuous

            sOffset (float): start s-coordinate of repeating Objects
                Default: 0

            tOffset (float): t-offset additional to lane width, sign will be added automatically (i.e. positive if further from roadside)
                Default: 0

            side (RoadSide): add Objects on both, left or right side
                Default: both

            widthStart (float) : width of object at start-coordinate (None follows .osgb)
                Default: None

            widthEnd (float) : width of object at end-coordinate (if not equal to widthStart, automatic linear width adapted over the distance)
                Default: None

            lengthStart (float) : length of object at start-coordinate (None follows .osgb)
                Default: None

            lengthEnd (float) : length of object at end-coordinate (if not equal to lengthStart, automatic linear length adapted over distance)
                Default: None

            radiusStart (float) : radius of object at start-coordinate (None follows .osgb)
                Default: None

            radiusEnd (float) : radius of object at end-coordinate (if not equal to radiusStart, automatic linear radius adapted over distance)
                Default: None
        """
        if not self.is_adjusted("planview"):
            raise RoadsAndLanesNotAdjusted(
                "Could not add roadside object because roads and lanes need to be adjusted first. Consider calling 'adjust_roads_and_lanes()'."
            )
        if not isinstance(road_object_prototype, Object):
            raise TypeError("road_object_prototype is not of type Object")
        side = enumchecker(side, RoadSide)

        total_widths = {RoadSide.right: [], RoadSide.left: []}
        road_objects = {RoadSide.right: None, RoadSide.left: None}
        repeat_lengths = {RoadSide.right: [], RoadSide.left: []}
        repeat_s = {RoadSide.right: [], RoadSide.left: []}
        repeat_t = {RoadSide.right: [], RoadSide.left: []}
        lanesections_s = []
        lanesections_length = []
        # TODO: handle width parameters apart from a
        for idx, lanesection in enumerate(self.lanes.lanesections):
            # retrieve lengths and widths of lane sections
            if idx == len(self.lanes.lanesections) - 1:
                # last lanesection
                lanesections_length.append(
                    self.planview.get_total_length() - lanesection.s
                )

            else:
                lanesections_length.append(
                    self.lanes.lanesections[idx + 1].s - lanesection.s
                )
            lanesections_s.append(lanesection.s)
            if side != RoadSide.right:
                # adding object for left side
                road_objects[RoadSide.left] = cpy.deepcopy(road_object_prototype)
                total_widths[RoadSide.left].append(0)
                for lane in lanesection.leftlanes:
                    total_widths[RoadSide.left][-1] = (
                        total_widths[RoadSide.left][-1] + lane.widths[0].a
                    )
            if side != RoadSide.left:
                # adding object for right side
                road_objects[RoadSide.right] = cpy.deepcopy(road_object_prototype)
                total_widths[RoadSide.right].append(0)
                for lane in lanesection.rightlanes:
                    total_widths[RoadSide.right][-1] = (
                        total_widths[RoadSide.right][-1] + lane.widths[0].a
                    )
            # both sides are added if RoadSide.both

        for road_side in [RoadSide.left, RoadSide.right]:
            if road_objects[road_side] is None:
                # no road_object is added to this roadside
                continue

            # initialize road objects with meaningful values
            hdg_factor = 1
            if road_side == RoadSide.right:
                hdg_factor = -1
            road_objects[road_side].t = (
                total_widths[road_side][0] + tOffset
            ) * hdg_factor
            road_objects[road_side].hdg = np.pi * (1 + hdg_factor) / 2
            road_objects[road_side].s = sOffset

            accumulated_length = 0
            for idx, length in enumerate(lanesections_length):
                accumulated_length += length
                if idx == 0:
                    repeat_lengths[road_side].append(accumulated_length - sOffset)
                    repeat_s[road_side].append(sOffset)
                    repeat_t[road_side].append(
                        (total_widths[road_side][idx] + tOffset) * hdg_factor
                    )
                else:
                    if total_widths[road_side][idx] != total_widths[road_side][idx - 1]:
                        # add another repeat record only if width is changing
                        repeat_lengths[road_side].append(length)
                        repeat_s[road_side].append(lanesections_s[idx])
                        repeat_t[road_side].append(
                            (total_widths[road_side][idx] + tOffset) * hdg_factor
                        )
                    else:
                        # otherwise add the length to existing repeat entry
                        repeat_lengths[road_side][-1] += length

            for idx, repeat_length in enumerate(repeat_lengths[road_side]):
                if repeat_length < 0:
                    raise ValueError(
                        f"Calculated negative value for s-coordinate of roadside object with name "
                        f"'{road_objects[road_side].name}'. Ensure using sOffset < length of road."
                    )
                road_objects[road_side].repeat(
                    repeat_length,
                    repeatDistance,
                    sStart=repeat_s[road_side][idx],
                    tStart=repeat_t[road_side][idx],
                    tEnd=repeat_t[road_side][idx],
                    widthStart=widthStart,
                    widthEnd=widthEnd,
                    lengthStart=lengthStart,
                    lengthEnd=lengthEnd,
                    radiusStart=radiusStart,
                    radiusEnd=radiusEnd,
                )
            self.add_object(road_objects[road_side])
        return self

    def add_signal(self, signal):
        """add_signal adds a signal to a road"""
        if isinstance(signal, list):
            if any(
                [
                    not any(isinstance(x, Signal) or isinstance(x, SignalReference))
                    for x in signal
                ]
            ):
                raise TypeError("signal contains elements that are not of type Signal")
            for single_signal in signal:
                single_signal._update_id()
            self.signals = self.signals + signal
        else:
            if not (isinstance(signal, Signal) or isinstance(signal, SignalReference)):
                raise TypeError("signal is not of type Signal")
            signal._update_id()
            self.signals.append(signal)
        return self

    def add_type(self, road_type, s=0, country=None, speed=None, speed_unit="m/s"):
        """adds a type to the road (not to mix with junction or not as the init)

        Parameters
        ----------
            road_type (RoadType): the type of road

            s (float): the distance where it starts
                Default: 0

            country (str): country code (should follow ISO 3166-1,alpha-2) (optional)

            speed (float/str): the maximum speed allowed

            sped_unit (str): unit of the speed, can be 'm/s','mph,'kph'
        """
        self.types.append(_Type(road_type, s, country, speed, speed_unit))
        return self

    def get_end_point(self):
        """get the x, y, and heading, of the end of the road

        Return
        ------
            x (float): the end x coordinate
            y (float): the end y coordinate
            h (float): the end heading

        """
        return self.planview.present_x, self.planview.present_y, self.planview.present_h

    def get_attributes(self):
        """returns the attributes as a dict of the Road"""
        retdict = {}
        if self.name:
            retdict["name"] = self.name
        if self.rule:
            retdict["rule"] = enum2str(self.rule)
        retdict["id"] = str(self.id)
        retdict["junction"] = str(self.road_type)
        retdict["length"] = str(self.planview.get_total_length())
        return retdict

    def get_element(self):
        """returns the elementTree of the road"""
        element = ET.Element("road", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        element.append(self.links.get_element())
        if self.types:
            for r in self.types:
                element.append(r.get_element())
        element.append(self.planview.get_element())
        element.append(self.elevationprofile.get_element())
        element.append(self.lateralprofile.get_element())
        element.append(self.lanes.get_element())
        if len(self.objects) > 0:
            objectselement = ET.SubElement(element, "objects")
            for road_object in self.objects:
                objectselement.append(road_object.get_element())
        if len(self.signals) > 0:
            signalselement = ET.SubElement(element, "signals")
            for signal in self.signals:
                signalselement.append(signal.get_element())
        return element


class OpenDrive(XodrBase):
    """OpenDrive is the main class of the pyodrx to generate an OpenDrive road

    Parameters
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE written to header
            Default: '1'

        revMinor (str): minor revision of OpenDRIVE written to header
            Default: '5'

        geo_reference (str): The information for geographic reference of a database
            Default: None

    Attributes
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE written to header
            Default: '1'

        revMinor (str): minor revision of OpenDRIVE written to header
            Default: '5'

        geo_reference (str): The information for geographic reference of a database
            Default: None

        roads (list of Road): all roads

        junctions (list of Junction): all junctions

    Methods
    -------
        get_element()
            Returns the full ElementTree of FileHeader

        add_road(road)
            Adds a road to the opendrive

        add_junction(junction)
            Adds a junction to the opendrive

        add_junction_creator(junction_creator)
            Adds the neccesary info from a junction creator to the opendrive

        adjust_roads_and_lanes()
            Adjust starting position of all geometries of all roads and try to link lanes in neighbouring roads

        adjust_startpoints()
            Adjust starting position of all geometries of all roads

        write_xml(filename)
            write a open scenario xml

    """

    def __init__(self, name, revMajor="1", revMinor="5", geo_reference=None):
        """Initalize the Header

        Parameters
        ----------
        name (str): name of the road

        """
        super().__init__()
        self.name = name
        self.revMajor = revMajor
        self.revMinor = revMinor
        self._header = _Header(self.name, self.revMajor, self.revMinor, geo_reference)
        self.roads = {}
        self.junctions = []
        # self.road_ids = []

    def __eq__(self, other):
        if isinstance(other, OpenDrive) and super().__eq__(other):
            if (
                self.roads == other.roads
                and self.junctions == other.junctions
                and self._header == other._header
            ):
                return True
        return False

    def add_road(self, road):
        """Adds a new road to the opendrive

        Parameters
        ----------
            road (Road): the road to add

        """
        if not isinstance(road, Road):
            raise TypeError("input road is not of type Road")
        if (len(self.roads) == 0) and road.predecessor:
            ValueError(
                "No road was added and the added road has a predecessor, please add the predecessor first"
            )
        if str(road.id) in self.roads:
            raise IdAlreadyExists(
                "Road id " + str(road.id) + " has already been added. "
            )
        self.roads[str(road.id)] = road
        return self

    def add_junction_creator(self, junction_creator):
        """add_junction_creator takes a CommonJunctionCreator as input and adds all neccesary info (roads and junctions)
            to the opendrive

        Parameters
        ----------
            junction_creator (CommonJunctionCreator/DirectJunctionCreator): the junction creator

        """
        if junction_creator.junction.junction_type == JunctionType.default:
            for road in junction_creator.get_connecting_roads():
                self.add_road(road)

        self.add_junction(junction_creator.junction)
        return self

    def adjust_roads_and_lanes(self):
        """Adjust starting position of all geometries of all roads and try to link all lanes in neighbouring roads

        Parameters
        ----------

        """
        # adjust roads and their geometries
        self.adjust_startpoints()

        results = list(combinations(self.roads, 2))

        for r in range(len(results)):
            # print('Analyzing roads', results[r][0], 'and', results[r][1] )
            create_lane_links(self.roads[results[r][0]], self.roads[results[r][1]])

    def adjust_roadmarks(self):
        """Tries to adjust broken roadmarks (if same definition) along roads and lane sections"""

        adjusted_road = self.roads[list(self.roads.keys())[0]]
        if not adjusted_road.is_adjusted("planview"):
            raise RoadsAndLanesNotAdjusted(
                "Cannot adjust roadmarks if geometries are not adjusted properly first. Consider calling 'adjust_roads_and_lanes()' first."
            )
        adjusted_road.lanes.adjust_road_marks_from_start(
            adjusted_road.planview.get_total_length()
        )

        count_total_adjusted_roads = 1

        while count_total_adjusted_roads < len(self.roads):
            for r in self.roads.keys():
                if not self.roads[r].is_adjusted("planview"):
                    raise RoadsAndLanesNotAdjusted(
                        "Cannot adjust roadmarks if geometries are not adjusted properly first. Consider calling 'adjust_roads_and_lanes()' first."
                    )
                if self.roads[r].lanes.roadmarks_adjusted:
                    if self.roads[r].successor:
                        if self.roads[r].successor.element_type == ElementType.road:
                            if (
                                self.roads[r].successor.contact_point
                                == ContactPoint.start
                            ):
                                self.roads[
                                    str(self.roads[r].successor.element_id)
                                ].lanes.adjust_road_marks_from_start(
                                    self.roads[
                                        str(self.roads[r].successor.element_id)
                                    ].planview.get_total_length(),
                                    self.roads[r].lanes.lanesections[-1],
                                    ContactPoint.end,
                                )
                                count_total_adjusted_roads += 1
                            else:
                                self.roads[
                                    str(self.roads[r].successor.element_id)
                                ].lanes.adjust_road_marks_from_end(
                                    self.roads[
                                        str(self.roads[r].successor.element_id)
                                    ].planview.get_total_length(),
                                    self.roads[r].lanes.lanesections[-1],
                                    ContactPoint.end,
                                )
                                count_total_adjusted_roads += 1
                        else:
                            for j in self.junctions:
                                if j.id == self.roads[r].successor.element_id:
                                    junction = j
                                    break

                            for conn in junction.connections:
                                if str(conn.incoming_road) == r:
                                    if conn.contact_point == ContactPoint.start:
                                        self.roads[
                                            str(conn.connecting_road)
                                        ].lanes.adjust_road_marks_from_start(
                                            self.roads[
                                                str(conn.connecting_road)
                                            ].planview.get_total_length(),
                                            self.roads[r].lanes.lanesections[0],
                                            ContactPoint.end,
                                        )
                                    else:
                                        self.roads[
                                            str(conn.connecting_road)
                                        ].lanes.adjust_road_marks_from_end(
                                            self.roads[
                                                str(conn.connecting_road)
                                            ].planview.get_total_length(),
                                            self.roads[r].lanes.lanesections[0],
                                            ContactPoint.end,
                                        )

                                    count_total_adjusted_roads += 1

                    if self.roads[r].predecessor:
                        if self.roads[r].predecessor.element_type == ElementType.road:
                            if (
                                self.roads[r].predecessor.contact_point
                                == ContactPoint.start
                            ):
                                self.roads[
                                    str(self.roads[r].predecessor.element_id)
                                ].lanes.adjust_road_marks_from_start(
                                    self.roads[
                                        str(self.roads[r].predecessor.element_id)
                                    ].planview.get_total_length(),
                                    self.roads[r].lanes.lanesections[0],
                                    ContactPoint.start,
                                )
                                count_total_adjusted_roads += 1
                            else:
                                self.roads[
                                    str(self.roads[r].predecessor.element_id)
                                ].lanes.adjust_road_marks_from_end(
                                    self.roads[
                                        str(self.roads[r].predecessor.element_id)
                                    ].planview.get_total_length(),
                                    self.roads[r].lanes.lanesections[0],
                                    ContactPoint.start,
                                )
                                count_total_adjusted_roads += 1
                        else:
                            for conn in self.junctions[0].connections:
                                if str(conn.incoming_road) == r:
                                    if conn.contact_point == ContactPoint.start:
                                        self.roads[
                                            str(conn.connecting_road)
                                        ].lanes.adjust_road_marks_from_start(
                                            self.roads[
                                                str(conn.connecting_road)
                                            ].planview.get_total_length(),
                                            self.roads[r].lanes.lanesections[-1],
                                            ContactPoint.start,
                                        )
                                    else:
                                        self.roads[
                                            str(conn.connecting_road)
                                        ].lanes.adjust_road_marks_from_end(
                                            self.roads[
                                                str(conn.connecting_road)
                                            ].planview.get_total_length(),
                                            self.roads[r].lanes.lanesections[-1],
                                            ContactPoint.start,
                                        )
                                    count_total_adjusted_roads += 1

    def _adjust_road_wrt_neighbour(
        self, road_id, neighbour_id, contact_point, neighbour_type
    ):
        """Adjust geometries of road[road_id] taking as a successor/predecessor the neighbouring road with id neighbour_id.
        NB Passing the type of contact_point is necessary because we call this function also on roads connecting to
        to a junction road (which means that the road itself do not know the contact point of the junction road it connects to)


        Parameters
        ----------
        road_id (int): id of the road we want to adjust

        neighbour_id (int): id of the neighbour road we take as reference (we suppose the neighbour road is already adjusted)

        contact_point (ContactPoint): type of contact point with point of view of roads[road_id]

        neighbour_type (str): 'successor'/'predecessor' type of linking to the neighbouring road


        """

        main_road = self.roads[str(road_id)]

        if contact_point == ContactPoint.start:
            x, y, h = self.roads[str(neighbour_id)].planview.get_start_point()
            h = (
                h + np.pi
            )  # we are attached to the predecessor's start, so road[k] will start in its opposite direction
        elif contact_point == ContactPoint.end:
            x, y, h = self.roads[str(neighbour_id)].planview.get_end_point()

            # since we are at the end, the relevant s-coordinate for determining widths for lane offset is the length of the last lane section
        else:
            raise ValueError("Unknown ContactPoint")

        if neighbour_type == "predecessor":
            num_lane_offsets = 0
            if main_road.pred_direct_junction:
                num_lane_offsets = main_road.pred_direct_junction[neighbour_id]
            elif str(neighbour_id) in main_road.lane_offset_pred:
                num_lane_offsets = main_road.lane_offset_pred[str(neighbour_id)]
            offset_width = self._calculate_lane_offset_width(
                road_id, neighbour_id, num_lane_offsets, contact_point
            )
            x = -offset_width * np.sin(h) + x
            y = offset_width * np.cos(h) + y

            main_road.planview.set_start_point(x, y, h)
            main_road.planview.adjust_geometries()

        elif neighbour_type == "successor":
            num_lane_offsets = 0
            if main_road.succ_direct_junction:
                num_lane_offsets = main_road.succ_direct_junction[neighbour_id]
            elif str(neighbour_id) in main_road.lane_offset_suc:
                num_lane_offsets = main_road.lane_offset_suc[str(neighbour_id)]
            offset_width = self._calculate_lane_offset_width(
                road_id, neighbour_id, num_lane_offsets, contact_point
            )
            x = offset_width * np.sin(h) + x
            y = -offset_width * np.cos(h) + y

            main_road.planview.set_start_point(x, y, h)
            main_road.planview.adjust_geometries(True)

    def _calculate_lane_offset_width(
        self, road_id, neighbour_id, num_lane_offsets, contact_point
    ):
        """calculate the width for shifting the road if a lane offset is present


        Parameters
        ----------
        neighbour_id(int): id of the neighbour road we take as reference (we suppose the neighbour road is already adjusted)


        """

        relevant_lanesection, relevant_s = get_lane_sec_and_s_for_lane_calc(
            self.roads[str(neighbour_id)], contact_point
        )
        # remains 0 if no lane offset exists
        offset_width = 0
        # if a lane offset exists, loop through relevant lanes (left/right) at the relevant s-coordinate to determine width of offset
        if num_lane_offsets < 0:
            for lane in (
                self.roads[str(neighbour_id)]
                .lanes.lanesections[relevant_lanesection]
                .rightlanes[0 : -1 * num_lane_offsets]
            ):
                offset_width = offset_width - (
                    lane.widths[relevant_lanesection].a
                    + lane.widths[relevant_lanesection].b * relevant_s
                    + lane.widths[relevant_lanesection].c * relevant_s**2
                    + lane.widths[relevant_lanesection].d * relevant_s**3
                )
        if num_lane_offsets > 0:
            for lane in (
                self.roads[str(neighbour_id)]
                .lanes.lanesections[relevant_lanesection]
                .leftlanes[0:num_lane_offsets]
            ):
                offset_width = offset_width + (
                    lane.widths[relevant_lanesection].a
                    + lane.widths[relevant_lanesection].b * relevant_s
                    + lane.widths[relevant_lanesection].c * relevant_s**2
                    + lane.widths[relevant_lanesection].d * relevant_s**3
                )

        return offset_width

    def _connection_sanity_check(self, road_id, connection_type):
        """_connection_sanity_check checks if a connection and input makes sence, ie. checking that
        all predecessor and contact points are done correctly.

        Parameters
        ----------
            road_id (str): id of the road of interest

            connection_type (str): if the predecessor or successor should be checked
        """
        road_id = str(road_id)
        if connection_type == "predecessor":
            contact_point = self.roads[road_id].predecessor.contact_point
            neighbor_id = str(self.roads[road_id].predecessor.element_id)
        elif connection_type == "successor":
            contact_point = self.roads[road_id].successor.contact_point
            neighbor_id = str(self.roads[road_id].successor.element_id)
        else:
            raise GeneralIssueInputArguments(
                "connection_type: " + connection_type + " is unknown."
            )
        if self.roads[road_id].road_type == -1:
            if not (
                (
                    contact_point == ContactPoint.start
                    and self.roads[neighbor_id].predecessor is not None
                    and self.roads[neighbor_id].predecessor.element_id == int(road_id)
                )
                or (
                    contact_point == ContactPoint.end
                    and self.roads[neighbor_id].successor is not None
                    and self.roads[neighbor_id].successor.element_id == int(road_id)
                )
            ):
                raise MixingDrivingDirection(
                    "road "
                    + road_id
                    + " and road "
                    + neighbor_id
                    + " have a mismatch in connections, please check predecessors/sucessors and contact points."
                )
        else:
            if not (
                (
                    contact_point == ContactPoint.start
                    and self.roads[neighbor_id].predecessor is not None
                    and self.roads[neighbor_id].predecessor.element_id
                    == self.roads[road_id].road_type
                )
                or contact_point == ContactPoint.end
                and self.roads[neighbor_id].successor is not None
                and self.roads[neighbor_id].successor.element_id
                == self.roads[road_id].road_type
            ):
                raise MixingDrivingDirection(
                    "road "
                    + road_id
                    + " and road "
                    + neighbor_id
                    + " have a mismatch in connections, please check predecessors/sucessors and contact points."
                )

    def _create_adjustable_planview(
        self,
        road_id,
        predecessor_id,
        predecessor_contact_point,
        successor_id,
        successor_contact_point,
    ):
        """method used to create the geometry of a AdjustablePlanview type of planview. note
        Both the predecessor and the successor of that road has to be fixed/adjusted for this to work.


        Parameters
        ----------
            road_id (str): id of the road with a AdjustablePlanview

            predecessor_id (str): id of the predecessor road

            predecessor_contact_point (ContactPoint): the contact point of the predecessor

            successor_id (str): id of the successor road

            successor_contact_point (ContactPoint): the contact point of the successor

        """

        def recalculate_xy(
            lane_offset, road, lanesection, x, y, h, common_direct_signs=1
        ):
            """helper funciton to recalculate x and y if an offset (in junctions) is present

            Parameters
            ----------
                lane_offset (int): lane offset of the road

                road (Road): the connected road

                x (float): the reference line x coordinate of the connected road

                y (float): the reference line y coordinate  of the connected road

                h (float): the heading of the connected road
            """
            dist = 0
            start_offset = 0
            if lanesection == -1:
                dist = road.planview.get_total_length()
            if np.sign(lane_offset) == -1:
                angle_addition = -common_direct_signs * np.pi / 2
                for lane_iter in range((np.sign(lane_offset) * lane_offset)):
                    start_offset += (
                        road.lanes.lanesections[lanesection]
                        .rightlanes[lane_iter]
                        .get_width(dist)
                    )
            else:
                angle_addition = common_direct_signs * np.pi / 2
                for lane_iter in range((np.sign(lane_offset) * lane_offset)):
                    start_offset += (
                        road.lanes.lanesections[lanesection]
                        .leftlanes[lane_iter]
                        .get_width(dist)
                    )
            new_x = x + start_offset * np.cos(h + angle_addition)
            new_y = y + start_offset * np.sin(h + angle_addition)
            return new_x, new_y

        if predecessor_contact_point == ContactPoint.start:
            start_x, start_y, start_h = self.roads[
                predecessor_id
            ].planview.get_start_point()
            start_lane_section = 0
            start_h = start_h - np.pi
            flip_start = True

        elif predecessor_contact_point == ContactPoint.end:
            start_x, start_y, start_h = self.roads[
                predecessor_id
            ].planview.get_end_point()
            start_lane_section = -1
            flip_start = False

        if (
            self.roads[road_id].pred_direct_junction
            and int(predecessor_id) in self.roads[road_id].pred_direct_junction
        ):
            start_x, start_y = recalculate_xy(
                self.roads[road_id].pred_direct_junction[int(predecessor_id)],
                self.roads[predecessor_id],
                start_lane_section,
                start_x,
                start_y,
                start_h,
            )

        if (
            self.roads[road_id].lane_offset_pred
            and predecessor_id in self.roads[road_id].lane_offset_pred
            and self.roads[road_id].lane_offset_pred[predecessor_id] != 0
        ):
            start_x, start_y = recalculate_xy(
                self.roads[road_id].lane_offset_pred[predecessor_id],
                self.roads[predecessor_id],
                start_lane_section,
                start_x,
                start_y,
                start_h,
                -1,
            )

        if successor_contact_point == ContactPoint.start:
            end_x, end_y, end_h = self.roads[successor_id].planview.get_start_point()
            end_lane_section = 0
            flip_end = False

        elif successor_contact_point == ContactPoint.end:
            end_x, end_y, end_h = self.roads[successor_id].planview.get_end_point()
            end_lane_section = -1
            end_h = end_h - np.pi
            flip_end = True

        if (
            self.roads[road_id].succ_direct_junction
            and int(successor_id) in self.roads[road_id].succ_direct_junction
        ):
            end_x, end_y = recalculate_xy(
                self.roads[road_id].succ_direct_junction[int(successor_id)],
                self.roads[successor_id],
                end_lane_section,
                end_x,
                end_y,
                end_h,
            )

        clothoids = pcloth.SolveG2(
            start_x,
            start_y,
            start_h,
            1 / 1000000000,
            end_x,
            end_y,
            end_h,
            1 / 1000000000,
        )
        pv = PlanView(start_x, start_y, start_h)

        [
            pv.add_geometry(Spiral(x.KappaStart, x.KappaEnd, length=x.length))
            for x in clothoids
        ]
        pv.adjust_geometries()

        s_start = 0
        s_end = 0
        if start_lane_section == -1:
            s_start = self.roads[predecessor_id].planview.get_total_length()
        if end_lane_section == -1:
            s_end = self.roads[successor_id].planview.get_total_length()

        if (
            self.roads[road_id].planview.right_lane_defs is None
            and self.roads[road_id].planview.left_lane_defs is None
        ):
            if flip_start:
                right_lanes_start = [
                    ll.get_width(s_start)
                    for ll in self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .leftlanes
                ]
                left_lanes_start = [
                    rl.get_width(s_start)
                    for rl in self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .rightlanes
                ]
            else:
                left_lanes_start = [
                    ll.get_width(s_start)
                    for ll in self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .leftlanes
                ]
                right_lanes_start = [
                    rl.get_width(s_start)
                    for rl in self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .rightlanes
                ]

            if flip_end:
                right_lanes_end = [
                    ll.get_width(s_end)
                    for ll in self.roads[successor_id]
                    .lanes.lanesections[end_lane_section]
                    .leftlanes
                ]
                left_lanes_end = [
                    rl.get_width(s_end)
                    for rl in self.roads[successor_id]
                    .lanes.lanesections[end_lane_section]
                    .rightlanes
                ]
            else:
                left_lanes_end = [
                    ll.get_width(s_end)
                    for ll in self.roads[successor_id]
                    .lanes.lanesections[end_lane_section]
                    .leftlanes
                ]
                right_lanes_end = [
                    rl.get_width(s_end)
                    for rl in self.roads[successor_id]
                    .lanes.lanesections[end_lane_section]
                    .rightlanes
                ]
            if self.roads[road_id].planview.center_road_mark is None:
                center_road_mark = (
                    self.roads[predecessor_id]
                    .lanes.lanesections[start_lane_section]
                    .centerlane.roadmark[0]
                )
            else:
                center_road_mark = self.roads[road_id].planview.center_road_mark

            lanes = create_lanes_merge_split(
                [
                    LaneDef(
                        0,
                        pv.get_total_length(),
                        len(right_lanes_start),
                        len(right_lanes_end),
                        None,
                        right_lanes_start,
                        right_lanes_end,
                    )
                ],
                [
                    LaneDef(
                        0,
                        pv.get_total_length(),
                        len(left_lanes_start),
                        len(left_lanes_end),
                        None,
                        left_lanes_start,
                        left_lanes_end,
                    )
                ],
                pv.get_total_length(),
                center_road_mark,
                None,
                lane_width_end=None,
            )

        else:
            lanes = create_lanes_merge_split(
                self.roads[road_id].planview.right_lane_defs,
                self.roads[road_id].planview.left_lane_defs,
                pv.get_total_length(),
                self.roads[road_id].planview.center_road_mark,
                self.roads[road_id].planview.lane_width,
                lane_width_end=self.roads[road_id].planview.lane_width_end,
            )
        self.roads[road_id].planview = pv
        self.roads[road_id].lanes = lanes

    def adjust_startpoints(self):
        """Adjust starting position of all geoemtries of all roads

        Parameters
        ----------

        """

        # Adjust logically connected roads, i.e. move them so they connect geometrically.
        # Method:
        #    Fix a pre defined roads (if start position in planview is used), other wise fix the first road at 0
        #    Next, in the set of remaining unconnected roads, find and adjust any roads connecting to a already fixed road
        # Loop until all roads have been adjusted,

        # adjust the roads that have a fixed start of the planview
        count_total_adjusted_roads = 0
        fixed_road = False
        for k in self.roads:
            if self.roads[k].planview.fixed and not self.roads[k].is_adjusted(
                "planview"
            ):
                self.roads[k].planview.adjust_geometries()
                # print('Fixing Road: ' + k)
                count_total_adjusted_roads += 1
                fixed_road = True
            elif self.roads[k].is_adjusted("planview"):
                fixed_road = True
                count_total_adjusted_roads += 1

        # If no roads are fixed, select the first road is selected as the pivot-road
        if len(self.roads) > 0:
            if fixed_road is False:
                for key in self.roads.keys():
                    # make sure it is not a connecting road, patching algorithm can't handle that
                    if self.roads[key].road_type == -1 and not isinstance(
                        self.roads[key].planview, AdjustablePlanview
                    ):
                        self.roads[key].planview.adjust_geometries()
                        break
                count_total_adjusted_roads += 1

        while count_total_adjusted_roads < len(self.roads):
            count_adjusted_roads = 0

            for k in self.roads:  # Check all
                if self.roads[k].planview.adjusted is False:
                    # check if road is a adjustable planview
                    if isinstance(self.roads[k].planview, AdjustablePlanview):
                        predecessor = None
                        successor = None

                        if (
                            self.roads[k].predecessor is None
                            or self.roads[k].successor is None
                        ):
                            raise UndefinedRoadNetwork(
                                "An AdjustablePlanview needs both a predecessor and a successor."
                            )

                        if self.roads[k].successor.element_type == ElementType.junction:
                            if self.roads[k].succ_direct_junction:
                                for key, value in self.roads[
                                    k
                                ].succ_direct_junction.items():
                                    if self.roads[str(key)].planview.adjusted:
                                        successor = str(key)
                                        if (
                                            self.roads[str(key)].successor
                                            and self.roads[
                                                str(key)
                                            ].successor.element_type
                                            == ElementType.junction
                                            and self.roads[
                                                str(key)
                                            ].successor.element_id
                                            == self.roads[k].successor.element_id
                                        ):
                                            suc_contact_point = ContactPoint.end
                                        else:
                                            suc_contact_point = ContactPoint.start
                                        break
                            else:
                                raise UndefinedRoadNetwork(
                                    "cannot handle a successor connection to a junction with an AdjustablePlanView"
                                )
                        else:
                            if self.roads[
                                str(self.roads[k].successor.element_id)
                            ].planview.adjusted:
                                successor = str(self.roads[k].successor.element_id)
                                suc_contact_point = self.roads[
                                    k
                                ].successor.contact_point

                        if (
                            self.roads[k].predecessor.element_type
                            == ElementType.junction
                        ):
                            if self.roads[k].pred_direct_junction:
                                for key, value in self.roads[
                                    k
                                ].pred_direct_junction.items():
                                    if self.roads[str(key)].planview.adjusted:
                                        predecessor = str(key)
                                        if (
                                            self.roads[str(key)].successor
                                            and self.roads[
                                                str(key)
                                            ].successor.element_type
                                            == ElementType.junction
                                            and self.roads[
                                                str(key)
                                            ].successor.element_id
                                            == self.roads[k].predecessor.element_id
                                        ):
                                            pred_contact_point = ContactPoint.end
                                        else:
                                            pred_contact_point = ContactPoint.start
                                        break
                            else:
                                for r_id, r in self.roads.items():
                                    if (
                                        r.road_type
                                        == self.roads[k].predecessor.element_id
                                        and r.planview.adjusted
                                    ):
                                        if r.predecessor.element_id == int(k):
                                            pred_contact_point = ContactPoint.start
                                            predecessor = r_id
                                            break
                                        elif r.successor.element_id == int(k):
                                            pred_contact_point = ContactPoint.end
                                            predecessor = r_id
                                            break

                        else:
                            if self.roads[
                                str(self.roads[k].predecessor.element_id)
                            ].planview.adjusted:
                                predecessor = str(self.roads[k].predecessor.element_id)
                                pred_contact_point = self.roads[
                                    k
                                ].predecessor.contact_point
                        if successor and predecessor:
                            self._create_adjustable_planview(
                                k,
                                predecessor,
                                pred_contact_point,
                                successor,
                                suc_contact_point,
                            )
                            count_adjusted_roads += 1

                    # check if it has a normal (road) predecessor
                    elif (
                        self.roads[k].predecessor is not None
                        and self.roads[k].predecessor.element_type
                        is not ElementType.junction
                        and self.roads[
                            str(self.roads[k].predecessor.element_id)
                        ].is_adjusted("planview")
                        is True
                    ):
                        self._connection_sanity_check(k, "predecessor")
                        self._adjust_road_wrt_neighbour(
                            k,
                            self.roads[k].predecessor.element_id,
                            self.roads[k].predecessor.contact_point,
                            "predecessor",
                        )
                        count_adjusted_roads += 1

                        if (
                            self.roads[k].road_type != -1
                            and self.roads[k].successor is not None
                            and self.roads[
                                str(self.roads[k].successor.element_id)
                            ].is_adjusted("planview")
                            is False
                            and not isinstance(
                                self.roads[
                                    str(self.roads[k].successor.element_id)
                                ].planview,
                                AdjustablePlanview,
                            )
                        ):
                            succ_id = self.roads[k].successor.element_id
                            if (
                                self.roads[k].successor.contact_point
                                == ContactPoint.start
                            ):
                                self._adjust_road_wrt_neighbour(
                                    succ_id, k, ContactPoint.end, "predecessor"
                                )
                            else:
                                self._adjust_road_wrt_neighbour(
                                    succ_id, k, ContactPoint.end, "successor"
                                )
                            count_adjusted_roads += 1

                    # check if geometry has a normal (road) successor
                    elif (
                        self.roads[k].successor is not None
                        and self.roads[k].successor.element_type
                        is not ElementType.junction
                        and self.roads[
                            str(self.roads[k].successor.element_id)
                        ].is_adjusted("planview")
                        is True
                    ):
                        self._connection_sanity_check(k, "successor")
                        self._adjust_road_wrt_neighbour(
                            k,
                            self.roads[k].successor.element_id,
                            self.roads[k].successor.contact_point,
                            "successor",
                        )
                        count_adjusted_roads += 1

                        if (
                            self.roads[k].road_type != -1
                            and self.roads[k].predecessor is not None
                            and self.roads[
                                str(self.roads[k].predecessor.element_id)
                            ].is_adjusted("planview")
                            is False
                            and not isinstance(
                                self.roads[
                                    str(self.roads[k].successor.element_id)
                                ].planview,
                                AdjustablePlanview,
                            )
                        ):
                            pred_id = self.roads[k].predecessor.element_id
                            if (
                                self.roads[k].predecessor.contact_point
                                == ContactPoint.start
                            ):
                                self._adjust_road_wrt_neighbour(
                                    pred_id, k, ContactPoint.start, "predecessor"
                                )
                            else:
                                self._adjust_road_wrt_neighbour(
                                    pred_id, k, ContactPoint.start, "successor"
                                )
                            count_adjusted_roads += 1
                    # do special check for direct junctions
                    elif (
                        self.roads[k].succ_direct_junction
                        or self.roads[k].pred_direct_junction
                    ):
                        if (
                            self.roads[k].successor is not None
                            and self.roads[k].successor.element_type
                            is ElementType.junction
                        ):
                            for dr in self.roads[k].succ_direct_junction:
                                if self.roads[str(dr)].is_adjusted("planview") is True:
                                    if (
                                        int(k)
                                        in self.roads[str(dr)].succ_direct_junction
                                    ):
                                        cp = ContactPoint.end
                                    elif (
                                        int(k)
                                        in self.roads[str(dr)].pred_direct_junction
                                    ):
                                        cp = ContactPoint.start
                                    else:
                                        raise UndefinedRoadNetwork(
                                            "direct junction is not properly defined"
                                        )
                                    self._adjust_road_wrt_neighbour(
                                        k, dr, cp, "successor"
                                    )

                                    count_adjusted_roads += 1
                        if (
                            self.roads[k].predecessor is not None
                            and self.roads[k].predecessor.element_type
                            is ElementType.junction
                        ):
                            for dr in self.roads[k].pred_direct_junction:
                                if self.roads[str(dr)].is_adjusted("planview") is True:
                                    if (
                                        int(k)
                                        in self.roads[str(dr)].succ_direct_junction
                                    ):
                                        cp = ContactPoint.end
                                    elif (
                                        int(k)
                                        in self.roads[str(dr)].pred_direct_junction
                                    ):
                                        cp = ContactPoint.start
                                    else:
                                        raise UndefinedRoadNetwork(
                                            "direct junction is not properly defined"
                                        )
                                    self._adjust_road_wrt_neighbour(
                                        k, dr, cp, "predecessor"
                                    )
                                    count_adjusted_roads += 1
            count_total_adjusted_roads += count_adjusted_roads

            if (
                count_total_adjusted_roads != len(self.roads)
                and count_adjusted_roads == 0
            ):
                # No more connecting roads found, move to next pivot-road
                raise UndefinedRoadNetwork(
                    "Roads are either missing successor, or predecessor to connect to the roads, \n if the roads are disconnected, please add a start position for one of the planviews."
                )

    def adjust_elevations(self):
        elevation_calculators = []
        for k in self.roads:
            ec = ElevationCalculator(self.roads[k])
            if (
                self.roads[k].predecessor is not None
                and self.roads[k].predecessor.element_type == ElementType.road
            ):
                ec.add_predecessor(
                    self.roads[str(self.roads[k].predecessor.element_id)]
                )
            elif (
                self.roads[k].predecessor is not None
                and self.roads[k].predecessor.element_type == ElementType.junction
            ):
                if self.roads[k].pred_direct_junction:
                    for key in self.roads[k].pred_direct_junction:
                        ec.add_predecessor(self.roads[str(key)])

                else:
                    for key in self.roads:
                        if self.roads[key].road_type == self.roads[
                            k
                        ].predecessor.element_id and self.roads[k].id in [
                            self.roads[key].successor.element_id,
                            self.roads[key].predecessor.element_id,
                        ]:
                            ec.add_predecessor(self.roads[str(key)])

            if (
                self.roads[k].successor is not None
                and self.roads[k].successor.element_type == ElementType.road
            ):
                ec.add_successor(self.roads[str(self.roads[k].successor.element_id)])
            elif (
                self.roads[k].successor is not None
                and self.roads[k].successor.element_type == ElementType.junction
            ):
                if self.roads[k].succ_direct_junction:
                    for key in self.roads[k].succ_direct_junction:
                        ec.add_successor(self.roads[str(key)])

                else:
                    for key in self.roads:
                        if self.roads[key].road_type == self.roads[
                            k
                        ].successor.element_id and self.roads[k].id in [
                            self.roads[key].successor.element_id,
                            self.roads[key].predecessor.element_id,
                        ]:
                            ec.add_successor(self.roads[str(key)])

            elevation_calculators.append(ec)
        for elevation_type in ["superelevation", "elevation"]:
            count_total_adjusted_roads = sum(
                [x.is_adjusted(elevation_type) for _, x in self.roads.items()]
            )
            if (
                any([x._extra_elevation_needed for x in elevation_calculators])
                and count_total_adjusted_roads == 0
            ):
                elevation_calculators[0].set_zero_elevation()
                count_total_adjusted_roads = 1
            if count_total_adjusted_roads == 0:
                continue
            while count_total_adjusted_roads < len(self.roads):
                for ec in elevation_calculators:
                    ec.create_profile(elevation_type)

                new_count = sum(
                    [x.is_adjusted(elevation_type) for _, x in self.roads.items()]
                )
                if new_count == count_total_adjusted_roads:
                    Warning("cannot adjust " + elevation_type + " more.")
                    break
                count_total_adjusted_roads = new_count

    def add_junction(self, junction):
        """Adds a junction to the opendrive

        Parameters
        ----------
            junction (Junction): the junction to add

        """
        if not isinstance(junction, Junction):
            raise TypeError("junction input is not of type Junction")
        if any([junction.id == x.id for x in self.junctions]):
            raise IdAlreadyExists(
                "Junction with id " + str(junction.id) + " has already been added. "
            )
        self.junctions.append(junction)
        return self

    def get_element(self):
        """returns the elementTree of the FileHeader"""
        element = ET.Element("OpenDRIVE")
        self._add_additional_data_to_element(element)
        element.append(self._header.get_element())
        for r in self.roads:
            element.append(self.roads[r].get_element())

        for j in self.junctions:
            element.append(j.get_element())

        return element

    def write_xml(self, filename=None, prettyprint=True, encoding="utf-8"):
        """write_xml writes the OpenDRIVE xml file

        Parameters
        ----------
            filename (str): path and filename of the wanted xml file
                Default: name of the opendrive

            prettyprint (bool): pretty print or ugly print?
                Default: True

            encoding (str): specifies the output encoding
                Default: 'utf-8'

        """
        if filename == None:
            filename = self.name + ".xodr"
        printToFile(self.get_element(), filename, prettyprint, encoding)


class _Type(XodrBase):
    """class to generate the type element of a road, (not the Enumeration it self).

    Parameters
    ----------
        road_type (RoadType): the type of road

        s (float): the distance where it starts
            Default: 0

        country (str): country code (should follow ISO 3166-1,alpha-2) (optional)

        speed (float/str): the maximum speed allowed

        speed_unit (str): unit of the speed, can be 'm/s','mph,'kph'

    Attributes
    ----------
        road_type (RoadType): the type of road

        s (float): the distance where it starts

        country (str): country code (should follow ISO 3166-1,alpha-2) (optional)

        speed (float/str): can either be a float or the following strings: "no limit" or "undefined"

        speed_unit (str): unit of the speed
    """

    def __init__(self, road_type, s=0, country=None, speed=None, speed_unit="m/s"):
        """initalize the _Type

        Parameters
        ----------
            road_type (RoadType): the type of road

            s (float): the distance where it starts
                Default: 0

            country (str): country code (should follow ISO 3166-1,alpha-2) (optional)

            speed (float/str): the maximum speed allowed

            speed_unit (str): unit of the speed, can be 'm/s','mph,'kph'


        """
        super().__init__()
        self.road_type = enumchecker(road_type, RoadType)
        self.s = s
        self.country = country
        if (
            isinstance(speed, float)
            or isinstance(speed, int)
            or speed in ["no limit", "undefined"]
            or speed == None
        ):
            self.speed = speed
        else:
            if isinstance(speed, str):
                raise ValueError(
                    'speed can only be numerical or "no limit" and "undefined", not: '
                    + str(speed_unit)
                )

        if speed_unit not in ["m/s", "mph", "kph"]:
            raise ValueError(
                "speed_unit can only be m/s, mph, or kph, not: " + speed_unit
            )
        self.speed_unit = speed_unit

    def __eq__(self, other):
        if isinstance(other, _Type) and super().__eq__(other):
            if (
                self.get_attributes() == other.get_attributes()
                and self.speed == other.speed
                and self.speed_unit == other.speed_unit
            ):
                return True
        return False

    def get_attributes(self):
        """returns the attributes as a dict of the _Type"""
        retdict = {}

        retdict["s"] = str(self.s)
        retdict["type"] = enum2str(self.road_type)
        if self.country:
            retdict["country"] = self.country
        return retdict

    def get_element(self):
        """returns the elementTree of the _Type"""

        element = ET.Element("type", attrib=self.get_attributes())
        self._add_additional_data_to_element(element)
        if self.speed:
            ET.SubElement(
                element,
                "speed",
                attrib={"max": str(self.speed), "unit": self.speed_unit},
            )
        return element
