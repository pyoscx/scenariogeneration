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
from .links import _Link, _Links, create_lane_links
from .enumerations import ElementType, ContactPoint, RoadSide, TrafficRule, JunctionType
from .exceptions import UndefinedRoadNetwork, RoadsAndLanesNotAdjusted, IdAlreadyExists
from .elevation import LateralProfile, ElevationProfile, _Poly3Profile
from .utils import get_lane_sec_and_s_for_lane_calc

import datetime as dt
from itertools import combinations
import numpy as np
import copy as cpy


class _Header:
    """Header creates the header of the OpenDrive file

    Parameters
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE

        revMinor (str): minor revision of OpenDRIVE

    Attributes
    ----------
        name (str): name of the scenario

        revMajor (str): major revision of OpenDRIVE

        revMinor (str): minor revision of OpenDRIVE

    Methods
    -------
        get_element()
            Returns the full ElementTree of FileHeader

        get_attributes()
            Returns a dictionary of all attributes of FileHeader

    """

    def __init__(self, name, revMajor, revMinor):
        """Initalize the Header

         Parameters
        ----------
            name (str): name of the road

            revMajor (str): major revision of OpenDRIVE

            revMinor (str): minor revision of OpenDRIVE

        """
        self.name = name
        self.revMajor = revMajor
        self.revMinor = revMinor

    def __eq__(self, other):
        if isinstance(other, _Header):
            if (
                self.name == other.name
                and self.revMajor == other.revMajor
                and self.revMinor == other.revMinor
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

        return element


class Road:
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
        self.id = road_id
        self.planview = planview
        self.lanes = lanes
        self.road_type = road_type
        self.name = name
        self.rule = rule
        self.links = _Links()
        self._neighbor_added = 0
        self.successor = None
        self.predecessor = None
        self.lane_offset_suc = {}
        self.lane_offset_pred = {}
        self.succ_direct_junction = {}
        self.pred_direct_junction = {}
        self.adjusted = False
        self.objects = []
        self.signals = []
        self.types = []
        self.elevationprofile = ElevationProfile()
        self.lateralprofile = LateralProfile()

    def __eq__(self, other):
        if isinstance(other, Road):
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
        self.successor = _Link("successor", element_id, element_type, contact_point)
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
        self.predecessor = _Link("predecessor", element_id, element_type, contact_point)
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
        self.elevationprofile.add_elevation(_Poly3Profile(s, a, b, c, d))
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
        self.lateralprofile.add_superelevation(_Poly3Profile(s, a, b, c, d))
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
        self.lateralprofile.add_shape(_Poly3Profile(s, a, b, c, d, t))
        return self

    def add_object(self, road_object):
        """add_object adds an object to a road and calls a function that ensures unique IDs

        Parameters
        ----------
            road_object (Object/list(Object)): object(s) to be added to road

        """
        if isinstance(road_object, list):
            for single_object in road_object:
                single_object._update_id()
            self.objects = self.objects + road_object
        else:
            road_object._update_id()
            self.objects.append(road_object)
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
        if not self.planview.adjusted:
            raise RoadsAndLanesNotAdjusted(
                "Could not add roadside object because roads and lanes need to be adjusted first. Consider calling 'adjust_roads_and_lanes()'."
            )

        hdg_factors = []
        total_widths = []
        road_objects = []
        s_lanesections = []
        # TODO: handle width parameters apart from a
        for lanesection in self.lanes.lanesections:
            if side != RoadSide.right:
                s_lanesections.append(lanesection.s)
                hdg_factors.append(1)
                total_widths.append(0)
                road_objects.append(cpy.deepcopy(road_object_prototype))
                for lane in lanesection.leftlanes:
                    total_widths[-1] = total_widths[-1] + lane.widths[0].a
            if side != RoadSide.left:
                s_lanesections.append(lanesection.s)
                hdg_factors.append(-1)
                total_widths.append(0)
                road_objects.append(cpy.deepcopy(road_object_prototype))
                for lane in lanesection.rightlanes:
                    total_widths[-1] = total_widths[-1] + lane.widths[0].a

        for idx, road_object in enumerate(road_objects):
            road_object.t = (total_widths[idx] + tOffset) * hdg_factors[idx]
            road_object.s = sOffset + s_lanesections[idx]
            road_object.hdg = np.pi * (1 + hdg_factors[idx]) / 2
            road_object.repeat(
                self.planview.get_total_length() - sOffset - s_lanesections[idx],
                repeatDistance,
                widthStart=widthStart,
                widthEnd=widthEnd,
                lengthStart=lengthStart,
                lengthEnd=lengthEnd,
                radiusStart=radiusStart,
                radiusEnd=radiusEnd,
            )
        self.add_object(road_objects)
        return self

    def add_signal(self, signal):
        """add_signal adds a signal to a road"""
        if isinstance(signal, list):
            for single_signal in signal:
                single_signal._update_id()
            self.signals = self.signals + signal
        else:
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
        """returns the elementTree of the FileHeader"""
        element = ET.Element("road", attrib=self.get_attributes())
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


class OpenDrive:
    """OpenDrive is the main class of the pyodrx to generate an OpenDrive road

    Parameters
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE written to header
            Default: '1'

        revMinor (str): minor revision of OpenDRIVE written to header
            Default: '5'

    Attributes
    ----------
        name (str): name of the road

        revMajor (str): major revision of OpenDRIVE written to header
            Default: '1'

        revMinor (str): minor revision of OpenDRIVE written to header
            Default: '5'

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

    def __init__(self, name, revMajor="1", revMinor="5"):
        """Initalize the Header

        Parameters
        ----------
        name (str): name of the road

        """
        self.name = name
        self.revMajor = revMajor
        self.revMinor = revMinor
        self._header = _Header(self.name, self.revMajor, self.revMinor)
        self.roads = {}
        self.junctions = []
        # self.road_ids = []

    def __eq__(self, other):
        if isinstance(other, OpenDrive):
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
            road (CommonJunctionCreator/DirectJunctionCreator): the junction creator

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
            if self.roads[k].planview.fixed and not self.roads[k].planview.adjusted:
                self.roads[k].planview.adjust_geometries()
                # print('Fixing Road: ' + k)
                count_total_adjusted_roads += 1
                fixed_road = True
            elif self.roads[k].planview.adjusted:
                fixed_road = True
                count_total_adjusted_roads += 1

        # If no roads are fixed, select the first road is selected as the pivot-road
        if len(self.roads) > 0:
            if fixed_road is False:
                self.roads[list(self.roads.keys())[0]].planview.adjust_geometries()
                # print('Selecting and adjusting the first road {}'.format(self.roads[list(self.roads.keys())[0] ].id))
                count_total_adjusted_roads += 1

        while count_total_adjusted_roads < len(self.roads):

            count_adjusted_roads = 0

            for k in self.roads:  # Check all

                if self.roads[k].planview.adjusted is False:

                    # check if it has a normal (road) predecessor
                    if (
                        self.roads[k].predecessor is not None
                        and self.roads[k].predecessor.element_type
                        is not ElementType.junction
                        and self.roads[
                            str(self.roads[k].predecessor.element_id)
                        ].planview.adjusted
                        is True
                    ):

                        # print('  Adjusting {}road {} to predecessor {}'.\
                        #     format('' if self.roads[k].road_type == -1 else 'connecting ', self.roads[k].id, self.roads[k].predecessor.element_id))
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
                            ].planview.adjusted
                            is False
                        ):
                            succ_id = self.roads[k].successor.element_id
                            # print('    Adjusting successor connecting road {} in junction {} to road {} '.\
                            #     format(succ_id, self.roads[k].road_type, self.roads[k].id))
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
                        ].planview.adjusted
                        is True
                    ):

                        # print('  Adjusting {}successor {} to road {}'.\
                        #     format('' if self.roads[k].road_type == -1 else 'connecting ', self.roads[k].id, self.roads[k].successor.element_id))
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
                            ].planview.adjusted
                            is False
                        ):
                            pred_id = self.roads[k].predecessor.element_id
                            # print('    Adjusting predecessor connecting road {} in junction {} to road {} '.\
                            #     format(pred_id, self.roads[k].road_type, self.roads[k].id))
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
                                if self.roads[str(dr)].planview.adjusted is True:
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
                                if self.roads[str(dr)].planview.adjusted is True:
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

    def add_junction(self, junction):
        """Adds a junction to the opendrive

        Parameters
        ----------
            junction (Junction): the junction to add

        """
        if any([junction.id == x.id for x in self.junctions]):
            raise IdAlreadyExists(
                "Junction with id " + str(junction.id) + " has already been added. "
            )
        self.junctions.append(junction)
        return self

    def get_element(self):
        """returns the elementTree of the FileHeader"""
        element = ET.Element("OpenDRIVE")
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


class _Type:
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
        self.road_type = road_type
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
        if isinstance(other, _Type):
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
        if self.speed:
            ET.SubElement(
                element,
                "speed",
                attrib={"max": str(self.speed), "unit": self.speed_unit},
            )
        return element
