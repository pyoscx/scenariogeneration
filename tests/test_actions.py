"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import pytest

from scenariogeneration import prettyprint
from scenariogeneration import xosc as OSC
from scenariogeneration.helpers import prettify
from scenariogeneration.xosc.actions import TrafficSignalControllerAction
from scenariogeneration.xosc.enumerations import (
    _MINOR_VERSION,
    ReferenceContext,
)
from scenariogeneration.xosc.actions import ObjectController
from scenariogeneration.xosc.exceptions import NoActionsDefinedError

from .xml_validator import ValidationResponse, version_validation

TD = OSC.TransitionDynamics(
    OSC.DynamicsShapes.step, OSC.DynamicsDimension.rate, 1.0
)

tod = OSC.TimeOfDay(True, 2020, 10, 1, 18, 30, 30)
weather = OSC.Weather(OSC.FractionalCloudCover.nineOktas, 100)
rc = OSC.RoadCondition(1)
prop = OSC.Properties()
prop.add_file("mycontrollerfile.xml")
controller = OSC.Controller("mycontroller", prop)
traffic = OSC.TrafficDefinition("my traffic")
traffic.add_controller(controller, 0.5)
traffic.add_controller(
    OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
)
traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)
env = OSC.Environment("Env_name", tod, weather, rc)

entity_distribution = OSC.EntityDistribution()
catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")
entity_distribution.add_entity_distribution_entry(0.5, catalog_ref)
traffic_distribution = OSC.TrafficDistribution()
traffic_distribution.add_traffic_distribution_entry(0.5, entity_distribution)


@pytest.fixture(autouse=True)
def reset_version():
    OSC.enumerations.VersionBase().setVersion(minor=_MINOR_VERSION)


actions_and_versions = [
    (OSC.EnvironmentAction(env), 2),
    (OSC.EnvironmentAction(env), _MINOR_VERSION),
    (
        OSC.AddEntityAction("my new thingy", OSC.WorldPosition()),
        _MINOR_VERSION,
    ),
    (OSC.AddEntityAction("my new thingy", OSC.WorldPosition()), 1),
    (OSC.AddEntityAction("my new thingy", OSC.WorldPosition()), 2),
    (OSC.DeleteEntityAction("my new thingy"), _MINOR_VERSION),
    (OSC.DeleteEntityAction("my new thingy"), 1),
    (OSC.DeleteEntityAction("my new thingy"), 2),
    (OSC.ParameterAddAction("Myparam", 3), 1),
    (OSC.ParameterMultiplyAction("Myparam", 3), 1),
    (OSC.ParameterSetAction("Myparam", 3), 1),
    (OSC.VariableAddAction("Myparam", 3), _MINOR_VERSION),
    (OSC.VariableAddAction("Myparam", 3), 2),
    (OSC.VariableMultiplyAction("Myparam", 3), _MINOR_VERSION),
    (OSC.VariableMultiplyAction("Myparam", 3), 2),
    (OSC.VariableSetAction("Myparam", 3), _MINOR_VERSION),
    (OSC.VariableSetAction("Myparam", 3), 2),
    (OSC.TrafficSignalStateAction("my signal", "red"), _MINOR_VERSION),
    (OSC.TrafficSignalStateAction("my signal", "red"), 1),
    (OSC.TrafficSignalStateAction("my signal", "red"), 2),
    (
        OSC.TrafficSignalControllerAction("Phase", "TSCRef_Name"),
        _MINOR_VERSION,
    ),
    (OSC.TrafficSignalControllerAction("Phase", "TSCRef_Name"), 1),
    (OSC.TrafficSignalControllerAction("Phase", "TSCRef_Name"), 2),
    (OSC.TrafficSourceAction(10, 10, OSC.WorldPosition(), traffic, 100), 1),
    (OSC.TrafficSourceAction(10, 10, OSC.WorldPosition(), traffic, 100), 2),
    (
        OSC.TrafficSourceAction(
            10, 10, OSC.WorldPosition(), traffic_distribution, 100
        ),
        _MINOR_VERSION,
    ),
    (OSC.TrafficSinkAction(10, OSC.WorldPosition(), traffic, 10), 1),
    (OSC.TrafficSinkAction(10, OSC.WorldPosition(), traffic, 10), 2),
    (OSC.TrafficSinkAction(10, OSC.WorldPosition()), _MINOR_VERSION),
    (OSC.TrafficSwarmAction(10, 20, 10, 2, 10, "Ego", traffic), 1),
    (OSC.TrafficSwarmAction(10, 20, 10, 2, 10, "Ego", traffic), 2),
    (
        OSC.TrafficSwarmAction(10, 20, 10, 2, 10, "Ego", traffic_distribution),
        _MINOR_VERSION,
    ),
    (OSC.TrafficStopAction("Stop_Action"), _MINOR_VERSION),
    (OSC.TrafficStopAction("Stop_Action"), 1),
    (OSC.TrafficStopAction("Stop_Action"), 2),
    (OSC.SetMonitorAction("MyMonitor", True), _MINOR_VERSION),
]


def idfn(action, osc_version):
    return f"GlobalAction: {action.__class__.__name__}_osc {osc_version}"


ids = [
    idfn(action, osc_version) for action, osc_version in actions_and_versions
]


class TestGlobalActionFactory:
    @pytest.mark.parametrize(
        "action, osc_version",
        actions_and_versions,
        ids=ids,
    )
    def test_global_action_factory(self, action, osc_version):
        action.setVersion(minor=osc_version)
        factoryoutput = OSC.actions._GlobalActionFactory.parse_globalaction(
            action.get_element()
        )
        prettyprint(action, None)
        prettyprint(factoryoutput, None)
        assert action == factoryoutput


route = OSC.Route("myroute")
route.add_waypoint(
    OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest
)
route.add_waypoint(
    OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest
)
prop2 = OSC.Properties()
prop2.add_property("mything", "2")
prop2.add_property("theotherthing", "true")
cnt = OSC.Controller("mycontroller", prop2)
positionlist = []
positionlist.append(OSC.RelativeLanePosition(-3, "Ego", 0, 10))
positionlist.append(OSC.RelativeLanePosition(-3, "Ego", 0, 10))
positionlist.append(OSC.RelativeLanePosition(-3, "Ego", 0, 10))
positionlist.append(OSC.RelativeLanePosition(-3, "Ego", 0, 10))
polyline = OSC.Polyline([0, 0.5, 1, 1.5], positionlist)
traj = OSC.Trajectory("my_trajectory", False)
traj.add_shape(polyline)

ocv_action = OSC.OverrideControllerValueAction()
ocv_action.set_brake(True, 2)
aca = OSC.ActivateControllerAction(True, True)
ass = OSC.AssignControllerAction(cnt)
object_controller = ObjectController(name="my_obj_controller", controller=cnt)

private_actions_and_version = [
    (OSC.AbsoluteSpeedAction(50.0, TD), _MINOR_VERSION),
    (OSC.RelativeSpeedAction(1, "Ego", TD), _MINOR_VERSION),
    (
        OSC.LongitudinalDistanceAction(
            "Ego",
            max_acceleration=3,
            max_deceleration=2,
            max_speed=4,
            distance=1,
        ),
        _MINOR_VERSION,
    ),
    (OSC.AbsoluteLaneChangeAction(1, TD), _MINOR_VERSION),
    (OSC.RelativeLaneChangeAction(1, "Ego", TD, 0.2), _MINOR_VERSION),
    (
        OSC.AbsoluteLaneOffsetAction(1, OSC.DynamicsShapes.step, 3, False),
        _MINOR_VERSION,
    ),
    (
        OSC.RelativeLaneOffsetAction(
            1, "Ego", OSC.DynamicsShapes.step, 3, False
        ),
        _MINOR_VERSION,
    ),
    (OSC.LateralDistanceAction("Ego", 3, max_speed=50), _MINOR_VERSION),
    (OSC.VisibilityAction(True, False, True), _MINOR_VERSION),
    (
        OSC.SynchronizeAction(
            "Ego",
            OSC.WorldPosition(0, 0, 0, 0, 0, 0),
            OSC.WorldPosition(10, 0, 0, 0, 0, 0),
            target_tolerance=1,
            target_tolerance_master=2,
        ),
        _MINOR_VERSION,
    ),
    (OSC.ControllerAction(ass, ocv_action, aca), 2),
    (OSC.AssignControllerAction(object_controller), _MINOR_VERSION),
    (ocv_action, _MINOR_VERSION),
    (OSC.ActivateControllerAction(True, False), _MINOR_VERSION),
    (OSC.AssignControllerAction(cnt), 2),
    (OSC.TeleportAction(OSC.WorldPosition(1)), _MINOR_VERSION),
    (OSC.AssignRouteAction(route), _MINOR_VERSION),
    (
        OSC.FollowTrajectoryAction(
            traj,
            OSC.FollowingMode.position,
            reference_domain=ReferenceContext.absolute,
            offset=3,
            scale=4,
        ),
        _MINOR_VERSION,
    ),
    (
        OSC.AcquirePositionAction(OSC.WorldPosition(1, 1, 0, 0, 0, 0)),
        _MINOR_VERSION,
    ),
    (
        OSC.AnimationAction(
            OSC.VehicleComponentType.doorFrontRight, 1, False, 1
        ),
        _MINOR_VERSION,
    ),
    (
        OSC.LightStateAction(
            OSC.VehicleLightType.brakeLights,
            OSC.LightMode.on,
            transition_time=0.1,
            color=OSC.Color(OSC.ColorType.black, OSC.ColorRGB(0, 0, 0)),
        ),
        _MINOR_VERSION,
    ),
    (
        OSC.SpeedProfileAction(
            [5, 4, 3],
            OSC.FollowingMode.follow,
            [1, 2, 3],
            OSC.DynamicsConstraints(1, 1, 1),
            "ego",
        ),
        _MINOR_VERSION,
    ),
    (OSC.RandomRouteAction(), _MINOR_VERSION),
]


def idfn(private_action, osc_version):
    return (
        f"PrivateAction: {private_action.__class__.__name__}_osc {osc_version}"
    )


ids = [
    idfn(private_action, osc_version)
    for private_action, osc_version in private_actions_and_version
]


class TestPrivateActionFactory:

    @pytest.mark.parametrize(
        "private_action, osc_version",
        private_actions_and_version,
        ids=ids,
    )
    def test_private_action_factory(self, private_action, osc_version):
        private_action.setVersion(minor=osc_version)
        factoryoutput = OSC.actions._PrivateActionFactory.parse_privateaction(
            private_action.get_element()
        )
        prettyprint(private_action, None)
        prettyprint(factoryoutput, None)

        assert private_action == factoryoutput
        assert factoryoutput == private_action


def test_speedaction_abs():
    speedaction = OSC.AbsoluteSpeedAction(50.0, TD)
    prettyprint(speedaction.get_element())

    speedaction2 = OSC.AbsoluteSpeedAction(50.0, TD)
    speedaction3 = OSC.AbsoluteSpeedAction(51, TD)
    assert speedaction == speedaction2
    assert speedaction != speedaction3
    action = OSC.AbsoluteSpeedAction.parse(speedaction.get_element())
    prettyprint(action)
    assert speedaction == action
    assert (
        version_validation("PrivateAction", speedaction, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", speedaction, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", speedaction, 2)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", speedaction, 3)
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        OSC.AbsoluteSpeedAction(50, "dummy")


def test_speedaction_rel():
    speedaction = OSC.RelativeSpeedAction(1, "Ego", TD)

    prettyprint(speedaction.get_element())
    speedaction2 = OSC.RelativeSpeedAction(1, "Ego", TD)
    speedaction3 = OSC.RelativeSpeedAction(1, "Ego1", TD)
    assert speedaction == speedaction2
    assert speedaction != speedaction3

    speedaction4 = OSC.RelativeSpeedAction.parse(speedaction.get_element())
    assert speedaction == speedaction4
    assert (
        version_validation("PrivateAction", speedaction, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", speedaction, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", speedaction, 2)
        == ValidationResponse.OK
    )
    assert version_validation("PrivateAction", speedaction, 3)
    with pytest.raises(TypeError):
        OSC.RelativeSpeedAction(50, "Ego", "dummy")


def test_longdistaction_dist():
    longdist = OSC.LongitudinalDistanceAction(
        "Ego", max_acceleration=3, max_deceleration=2, max_speed=4, distance=1
    )
    prettyprint(longdist.get_element())
    longdist2 = OSC.LongitudinalDistanceAction(
        "Ego", max_acceleration=3, max_deceleration=2, max_speed=4, distance=1
    )
    longdist3 = OSC.LongitudinalDistanceAction(
        "Ego",
        max_acceleration=3,
        max_deceleration=2,
        max_speed=4,
        distance=2,
        coordinate_system="$my_coord",
    )
    assert longdist == longdist2
    assert longdist != longdist3
    prettyprint(longdist3.get_element())
    longdist4 = OSC.LongitudinalDistanceAction.parse(longdist.get_element())
    longdist5 = OSC.LongitudinalDistanceAction.parse(longdist3.get_element())
    prettyprint(longdist4.get_element())
    assert longdist == longdist4
    assert longdist3 == longdist5
    assert (
        version_validation("PrivateAction", longdist, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", longdist, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", longdist, 2)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", longdist3, 2)
        == ValidationResponse.OK
    )

    with pytest.raises(ValueError):
        OSC.LongitudinalDistanceAction(
            "ego", distance=1, coordinate_system="dummy"
        )
    with pytest.raises(ValueError):
        OSC.LongitudinalDistanceAction("ego", distance=1, displacement="dummy")


def test_longdistaction_time():
    longdist = OSC.LongitudinalDistanceAction(
        "Ego", max_acceleration=1, timeGap=2
    )
    prettyprint(longdist.get_element())
    longdist2 = OSC.LongitudinalDistanceAction(
        "Ego", max_acceleration=1, timeGap=2
    )
    longdist3 = OSC.LongitudinalDistanceAction(
        "Ego", max_acceleration=1, timeGap=3
    )
    assert longdist == longdist2
    assert longdist != longdist3

    longdist4 = OSC.LongitudinalDistanceAction.parse(longdist.get_element())
    prettyprint(longdist4.get_element())
    assert longdist == longdist4
    assert (
        version_validation("PrivateAction", longdist, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", longdist, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", longdist, 2)
        == ValidationResponse.OK
    )


def test_lanechange_abs():
    lanechange = OSC.AbsoluteLaneChangeAction(1, TD)
    prettyprint(lanechange.get_element())
    lanechange2 = OSC.AbsoluteLaneChangeAction(1, TD)
    lanechange3 = OSC.AbsoluteLaneChangeAction(2, TD)
    assert lanechange == lanechange2
    assert lanechange != lanechange3

    lanechange4 = OSC.AbsoluteLaneChangeAction.parse(lanechange.get_element())
    assert lanechange == lanechange4
    assert (
        version_validation("PrivateAction", lanechange, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", lanechange, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", lanechange, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        OSC.AbsoluteLaneChangeAction(1, "dummy")


def test_lanechange_rel():
    lanechange = OSC.RelativeLaneChangeAction(1, "Ego", TD, 0.2)
    prettyprint(lanechange.get_element())
    lanechange2 = OSC.RelativeLaneChangeAction(1, "Ego", TD, 0.2)
    lanechange3 = OSC.RelativeLaneChangeAction(1, "Ego", TD, 0.1)
    assert lanechange == lanechange2
    assert lanechange != lanechange3

    lanechange4 = OSC.RelativeLaneChangeAction.parse(lanechange.get_element())
    prettyprint(lanechange4.get_element(), None)
    assert lanechange4 == lanechange
    assert (
        version_validation("PrivateAction", lanechange, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", lanechange, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", lanechange, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        OSC.RelativeLaneChangeAction(1, "Ego", "dummy", 0.2)


def test_laneoffset_abs():
    laneoffset = OSC.AbsoluteLaneOffsetAction(
        1, OSC.DynamicsShapes.step, 3, False
    )
    prettyprint(laneoffset.get_element(), None)
    laneoffset2 = OSC.AbsoluteLaneOffsetAction(
        1, OSC.DynamicsShapes.step, 3, False
    )
    laneoffset3 = OSC.AbsoluteLaneOffsetAction(
        1, OSC.DynamicsShapes.step, 2, True
    )

    assert laneoffset == laneoffset2
    assert laneoffset != laneoffset3

    laneoffset4 = OSC.AbsoluteLaneOffsetAction.parse(laneoffset.get_element())
    prettyprint(laneoffset.get_element(), None)
    assert laneoffset == laneoffset4
    assert (
        version_validation("PrivateAction", laneoffset, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", laneoffset, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", laneoffset, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.AbsoluteLaneOffsetAction(1, "dummy")


def test_laneoffset_rel():
    laneoffset = OSC.RelativeLaneOffsetAction(
        1, "Ego", OSC.DynamicsShapes.step, 3, False
    )
    prettyprint(laneoffset.get_element(), None)
    laneoffset2 = OSC.RelativeLaneOffsetAction(
        1, "Ego", OSC.DynamicsShapes.step, 3, False
    )
    laneoffset3 = OSC.RelativeLaneOffsetAction(
        1, "Ego", OSC.DynamicsShapes.linear, 3, False
    )
    assert laneoffset == laneoffset2
    assert laneoffset != laneoffset3

    laneoffset4 = OSC.RelativeLaneOffsetAction.parse(laneoffset.get_element())
    prettyprint(laneoffset4.get_element(), None)
    assert laneoffset4 == laneoffset
    assert (
        version_validation("PrivateAction", laneoffset, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", laneoffset, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", laneoffset, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        OSC.RelativeLaneOffsetAction(1, "ego", "dummy")


def test_lateraldistance_noconst():
    latdist = OSC.LateralDistanceAction("Ego")
    prettyprint(latdist.get_element(), None)
    latdist2 = OSC.LateralDistanceAction("Ego")
    latdist3 = OSC.LateralDistanceAction("Ego1")
    assert latdist == latdist2
    assert latdist != latdist3

    latdist4 = OSC.LateralDistanceAction.parse(latdist.get_element())
    prettyprint(latdist4.get_element(), None)
    assert latdist4 == latdist
    assert (
        version_validation("PrivateAction", latdist, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", latdist, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", latdist, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.LateralDistanceAction("Ego", 1, coordinate_system="dummy")
    with pytest.raises(ValueError):
        OSC.LateralDistanceAction("Ego", 1, displacement="dummy")


def test_lateraldistance_const():
    latdist = OSC.LateralDistanceAction("Ego", 3, max_speed=50)
    prettyprint(latdist.get_element(), None)
    latdist2 = OSC.LateralDistanceAction("Ego", 3, max_speed=50)
    latdist3 = OSC.LateralDistanceAction("Ego", 3, max_speed=40)
    assert latdist == latdist2
    assert latdist != latdist3

    latdist4 = OSC.LateralDistanceAction.parse(latdist.get_element())
    prettyprint(latdist4.get_element(), None)
    assert latdist4 == latdist
    assert (
        version_validation("PrivateAction", latdist, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", latdist, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", latdist, 2)
        == ValidationResponse.OK
    )


def test_teleport():
    teleport = OSC.TeleportAction(OSC.WorldPosition())
    prettyprint(teleport.get_element())
    teleport2 = OSC.TeleportAction(OSC.WorldPosition())
    teleport3 = OSC.TeleportAction(OSC.WorldPosition(1))
    assert teleport == teleport2
    assert teleport != teleport3
    teleport4 = OSC.TeleportAction.parse(teleport.get_element())
    assert teleport == teleport4
    assert (
        version_validation("PrivateAction", teleport, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", teleport, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", teleport, 2)
        == ValidationResponse.OK
    )


class TestRandomRouteAction:

    def test_base(self):
        ra = OSC.RandomRouteAction()
        prettyprint(ra.get_element())

    def test_eq(self):
        ra = OSC.RandomRouteAction()
        ra2 = OSC.RandomRouteAction()
        assert ra == ra2

    def test_neq(self):
        ra = OSC.RandomRouteAction()
        route = OSC.Route("myroute")
        route.add_waypoint(
            OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest
        )
        route.add_waypoint(
            OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest
        )
        ara = OSC.AssignRouteAction(route)
        assert ra != ara

    def test_parse(self):
        ra = OSC.RandomRouteAction()
        parsed_ra = OSC.RandomRouteAction.parse(ra.get_element())
        assert ra == parsed_ra

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_osc_versions(self, version, expected):
        ra = OSC.RandomRouteAction()
        assert version_validation("PrivateAction", ra, version) == expected


def test_assign_route():
    route = OSC.Route("myroute")
    route.add_waypoint(
        OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )
    route.add_waypoint(
        OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )
    ara = OSC.AssignRouteAction(route)
    prettyprint(ara.get_element(), None)
    ara2 = OSC.AssignRouteAction(route)
    route2 = OSC.Route("myroute2")
    route2.add_waypoint(
        OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )
    route2.add_waypoint(
        OSC.WorldPosition(1, 1, 1, 0, 0, 0), OSC.RouteStrategy.shortest
    )
    ara3 = OSC.AssignRouteAction(route2)
    assert ara == ara2
    assert ara != ara3

    ara4 = OSC.AssignRouteAction.parse(ara.get_element())
    prettyprint(ara4.get_element(), None)
    assert ara == ara4
    assert version_validation("PrivateAction", ara, 0) == ValidationResponse.OK
    assert version_validation("PrivateAction", ara, 1) == ValidationResponse.OK
    assert version_validation("PrivateAction", ara, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.AssignRouteAction("dummy")


def test_aqcuire_position_route():
    ara = OSC.AcquirePositionAction(OSC.WorldPosition(1, 1, 0, 0, 0, 0))
    prettyprint(ara.get_element(), None)
    ara2 = OSC.AcquirePositionAction(OSC.WorldPosition(1, 1, 0, 0, 0, 0))
    ara3 = OSC.AcquirePositionAction(OSC.WorldPosition(1, 1, 1, 0, 0, 0))
    assert ara == ara2
    assert ara != ara3

    ara4 = OSC.AcquirePositionAction.parse(ara.get_element())
    prettyprint(ara4.get_element(), None)
    assert ara4 == ara
    assert version_validation("PrivateAction", ara, 0) == ValidationResponse.OK
    assert version_validation("PrivateAction", ara, 1) == ValidationResponse.OK
    assert version_validation("PrivateAction", ara, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.AcquirePositionAction("dummy")


class TestControllerAction:
    @pytest.fixture(name="aca")
    def activate_controller_action(self):
        aca = OSC.ActivateControllerAction(True, True)
        return aca

    @pytest.fixture(name="ca")
    def controller_action(self, aca):
        prop = OSC.Properties()
        prop.add_property("mything", "2")
        prop.add_property("theotherthing", "true")
        cnt = OSC.Controller("mycontroller", prop)
        object_controller = ObjectController(
            name="my_obj_controller", controller=cnt
        )
        ass = OSC.AssignControllerAction(object_controller)
        ocva = OSC.OverrideControllerValueAction()
        ocva.set_brake(True, 2)
        ca = OSC.ControllerAction(ass, ocva, aca)
        return ca

    @pytest.fixture(name="ca_v3")
    def controller_action_v3(self):
        prop = OSC.Properties()
        prop.add_property("mything", "2")
        prop.add_property("theotherthing", "true")
        cnt = OSC.Controller("mycontroller", prop)
        object_controller = ObjectController(
            name="my_obj_controller", controller=cnt
        )
        ass = OSC.AssignControllerAction(object_controller)
        ca = OSC.ControllerAction(ass)
        return ca

    @pytest.fixture(name="ca_v2")
    def controller_action_v2(self, aca):
        prop = OSC.Properties()
        prop.add_property("mything", "2")
        prop.add_property("theotherthing", "true")
        cnt = OSC.Controller("mycontroller", prop)
        ass = OSC.AssignControllerAction(cnt)
        ocva = OSC.OverrideControllerValueAction()
        ocva.set_brake(True, 2)
        ca = OSC.ControllerAction(ass, ocva, aca)
        return ca

    def test_eq_controller_action(self, ca):
        ca2 = OSC.ControllerAction.parse(ca.get_element())
        prettyprint(ca.get_element(), None)
        prettyprint(ca2.get_element(), None)
        assert ca == ca2

    def test_eq_controller_action_v2(self, ca):
        ca.setVersion(minor=2)
        prop = OSC.Properties()
        prop.add_property("mything", "2")
        prop.add_property("theotherthing", "true")
        cnt = OSC.Controller("mycontroller", prop)
        ca.assignControllerAction.controller = cnt
        ca3 = OSC.ControllerAction.parse(ca.get_element())
        assert ca == ca3

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (1, ValidationResponse.OK),
            (2, ValidationResponse.OK),
        ],
    )
    def test_version_validation(self, version, expected, ca_v2):
        ca_v2.setVersion(minor=version)
        prettyprint(ca_v2.get_element(), None)
        assert version_validation("PrivateAction", ca_v2, version) == expected

    def test_version_validation_v3(self, ca_v3, ca):
        prettyprint(ca_v3.get_element(), None)
        assert (
            version_validation("PrivateAction", ca_v3, 3)
            == ValidationResponse.OK
        )
        assert (
            version_validation("PrivateAction", ca, 3)
            == ValidationResponse.XSD_FAILURE
        )

    def test_invalid_input(self):
        with pytest.raises(TypeError):
            OSC.ControllerAction(assignControllerAction="dummy")
        with pytest.raises(TypeError):
            OSC.ControllerAction(activateControllerAction="dummy")
        with pytest.raises(TypeError):
            OSC.ControllerAction(overrideControllerValueAction="dummy")


class TestActivateControllerAction:

    def test_base(self):
        aca = OSC.ActivateControllerAction(
            True, True, False, True, "some_controller"
        )
        prettyprint(aca.get_element(), None)

    def test_eq(self):
        aca = OSC.ActivateControllerAction(
            True, True, False, True, "some_controller"
        )
        aca2 = OSC.ActivateControllerAction(
            True, True, False, True, "some_controller"
        )
        assert aca == aca2

    def test_neq(self):
        aca = OSC.ActivateControllerAction(
            True, True, False, True, "some_controller"
        )
        aca2 = OSC.ActivateControllerAction(True, True, False, True)
        assert aca != aca2

    @pytest.mark.parametrize(
        "osc_version",
        [0, 1, 2, 3],
    )
    def test_parse(self, osc_version):
        aca = OSC.ActivateControllerAction(
            True, True, False, True, "some_controller"
        )
        aca.setVersion(1, osc_version)
        parsed_aca = OSC.ActivateControllerAction.parse(aca.get_element())
        assert parsed_aca == aca

    @pytest.mark.parametrize(
        "osc_version",
        [0, 1, 2, 3],
    )
    def test_version_simple(self, osc_version):
        aca = OSC.ActivateControllerAction(True, True)
        assert (
            version_validation("PrivateAction", aca, osc_version)
            == ValidationResponse.OK
        )

    @pytest.mark.parametrize(
        "osc_version",
        [0, 1, 2, 3],
    )
    def test_version_more(self, osc_version):
        aca = OSC.ActivateControllerAction(
            True, True, False, True, "some_controller"
        )
        assert (
            version_validation("PrivateAction", aca, osc_version)
            == ValidationResponse.OK
        )


class TestAssignControllerAction:
    @pytest.fixture(name="aca")
    def assign_controller_action(self):
        prop = OSC.Properties()
        prop.add_property("mything", "2")
        prop.add_property("theotherthing", "true")

        cnt = OSC.Controller("mycontroller", prop)
        object_controller = ObjectController(
            name="my_obj_controller", controller=cnt
        )
        aca = OSC.AssignControllerAction(object_controller)
        return aca

    @pytest.fixture(name="aca_v2")
    def assign_controller_action_v2(self):
        OSC.VersionBase().setVersion(minor=2)
        prop = OSC.Properties()
        prop.add_property("mything", "2")
        prop.add_property("theotherthing", "true")

        cnt = OSC.Controller("mycontroller", prop)
        aca = OSC.AssignControllerAction(cnt)
        return aca

    def test_prettyprint(self, aca):
        prettyprint(aca.get_element(), None)

    def test_eq(self, aca):
        prop2 = OSC.Properties()
        prop2.add_property("mything", "3")
        prop2.add_property("theotherthing", "true")
        object_controller = ObjectController(
            name="my_obj_controller", controller=cnt
        )
        aca2 = OSC.AssignControllerAction(object_controller)

        assert aca == aca2

    def test_neq(self, aca):
        prop2 = OSC.Properties()
        prop2.add_property("mything", "3")
        prop2.add_property("theotherthing", "true")

        cnt2 = OSC.Controller("mycontroller", prop2)
        object_controller = ObjectController(
            name="my_obj_controller2", controller=cnt2
        )

        aca3 = OSC.AssignControllerAction(
            object_controller, True, True, True, True
        )
        prettyprint(aca3.get_element(), None)
        assert aca != aca3

    def test_parse(self, aca):
        aca4 = OSC.AssignControllerAction.parse(aca.get_element())
        prettyprint(aca4.get_element(), None)
        assert aca4 == aca

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OK),
            (2, ValidationResponse.OK),
            (3, ValidationResponse.OSC_VERSION),
        ],
    )
    def test_version_validation(self, version, expected, aca_v2):
        assert version_validation("PrivateAction", aca_v2, version) == expected

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.XSD_FAILURE),
            (2, ValidationResponse.XSD_FAILURE),
            (3, ValidationResponse.OK),
        ],
    )
    def test_version_validation_v3(self, version, expected, aca):
        assert version_validation("PrivateAction", aca, version) == expected

    def test_invalid_input(self):
        with pytest.raises(TypeError):
            OSC.AssignControllerAction("dummy")


def test_override_controller():
    ocva = OSC.OverrideControllerValueAction()
    with pytest.raises(NoActionsDefinedError):
        ocva.get_element()
    ocva.set_brake(True, 2)
    # prettyprint(ocva.get_element())
    ocva.set_throttle(False, 0)
    # prettyprint(ocva.get_element())
    ocva.set_clutch(True, 1)
    # prettyprint(ocva.get_element())
    ocva.set_parkingbrake(False, 1)
    # prettyprint(ocva.get_element())
    ocva.set_steeringwheel(True, 1)
    # prettyprint(ocva.get_element(),None)
    ocva.set_gear(False, 0)
    prettyprint(ocva.get_element(), None)

    ocva1 = OSC.OverrideControllerValueAction()
    ocva1.set_brake(True, 2)
    ocva2 = OSC.OverrideControllerValueAction()
    ocva2.set_brake(True, 2)
    ocva3 = OSC.OverrideControllerValueAction()
    ocva3.set_brake(True, 3)

    assert ocva1 == ocva2
    assert ocva1 != ocva3

    ocva4 = OSC.OverrideControllerValueAction.parse(ocva.get_element())
    prettyprint(ocva4.get_element(), None)
    assert ocva4 == ocva
    assert (
        version_validation("PrivateAction", ocva, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("PrivateAction", ocva, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", ocva, 2) == ValidationResponse.OK
    )


def test_visual_action():
    va = OSC.VisibilityAction(True, False, True)
    va.add_sensor_reference("mysensor")
    prettyprint(va.get_element(), None)
    va2 = OSC.VisibilityAction(True, False, True)
    va2.add_sensor_reference("mysensor")
    va3 = OSC.VisibilityAction(True, False, True)
    assert va == va2
    assert va != va3

    va4 = OSC.VisibilityAction.parse(va.get_element())
    prettyprint(va4.get_element(), None)
    assert va4 == va
    assert (
        version_validation("PrivateAction", va, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("PrivateAction", va3, 0) == ValidationResponse.OK
    assert version_validation("PrivateAction", va3, 1) == ValidationResponse.OK
    assert version_validation("PrivateAction", va, 2) == ValidationResponse.OK


def test_sync_action():
    asa = OSC.SynchronizeAction(
        "Ego",
        OSC.WorldPosition(0, 0, 0, 0, 0, 0),
        OSC.WorldPosition(10, 0, 0, 0, 0, 0),
        target_tolerance=1,
        target_tolerance_master=2,
    )
    prettyprint(asa.get_element(), None)
    asa2 = OSC.SynchronizeAction(
        "Ego",
        OSC.WorldPosition(0, 0, 0, 0, 0, 0),
        OSC.WorldPosition(10, 0, 0, 0, 0, 0),
        target_tolerance=1,
        target_tolerance_master=2,
    )
    asa3 = OSC.SynchronizeAction(
        "Ego",
        OSC.WorldPosition(1, 0, 0, 0, 0, 0),
        OSC.WorldPosition(10, 0, 0, 0, 0, 0),
        target_tolerance=1,
        target_tolerance_master=2,
    )
    assert asa == asa2
    assert asa != asa3
    asa4 = OSC.SynchronizeAction(
        "Ego",
        OSC.WorldPosition(0, 0, 0, 0, 0, 0),
        OSC.WorldPosition(10, 0, 0, 0, 0, 0),
        final_speed=OSC.AbsoluteSpeed(20 / 3.6, OSC.TargetTimeSteadyState(2)),
    )
    prettyprint(asa4, None)
    asa5 = OSC.SynchronizeAction(
        "Ego",
        OSC.WorldPosition(0, 0, 0, 0, 0, 0),
        OSC.WorldPosition(10, 0, 0, 0, 0, 0),
        target_tolerance=1,
        target_tolerance_master=2,
        final_speed=OSC.AbsoluteSpeed(20 / 3.6, OSC.TargetTimeSteadyState(2)),
    )

    asa6 = OSC.SynchronizeAction.parse(asa4.get_element())
    prettyprint(asa6.get_element(), None)
    assert asa6 == asa4
    assert version_validation("PrivateAction", asa, 0) == ValidationResponse.OK
    assert version_validation("PrivateAction", asa, 1) == ValidationResponse.OK
    assert version_validation("PrivateAction", asa, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.SynchronizeAction(
            "ego", "dummy", OSC.WorldPosition(0, 0, 0, 0, 0, 0)
        )
    with pytest.raises(TypeError):
        OSC.SynchronizeAction(
            "ego", OSC.WorldPosition(0, 0, 0, 0, 0, 0), "dummy"
        )
    with pytest.raises(TypeError):
        OSC.SynchronizeAction(
            "ego",
            OSC.WorldPosition(0, 0, 0, 0, 0, 0),
            OSC.WorldPosition(0, 0, 0, 0, 0, 0),
            final_speed=10,
        )


def test_follow_traj_action_polyline():
    positionlist = []
    positionlist.append(OSC.RelativeLanePosition(-3, "Ego", 0, 10))
    positionlist.append(OSC.RelativeLanePosition(-3, "Ego", 0, 10))
    positionlist.append(OSC.RelativeLanePosition(-3, "Ego", 0, 10))
    positionlist.append(OSC.RelativeLanePosition(-3, "Ego", 0, 10))
    prettyprint(positionlist[0].get_element(), None)
    polyline = OSC.Polyline([0, 0.5, 1, 1.5], positionlist)

    traj = OSC.Trajectory("my_trajectory", False)
    traj.add_shape(polyline)

    trajact = OSC.FollowTrajectoryAction(
        traj,
        OSC.FollowingMode.position,
        reference_domain=ReferenceContext.absolute,
        offset=3,
        scale=4,
    )
    prettyprint(trajact.get_element(), None)

    trajact2 = OSC.FollowTrajectoryAction(
        traj,
        OSC.FollowingMode.position,
        reference_domain=ReferenceContext.absolute,
        offset=3,
        scale=4,
    )
    traj2 = OSC.Trajectory("my_trajectory", True)
    traj2.add_shape(polyline)

    trajact3 = OSC.FollowTrajectoryAction(traj2, OSC.FollowingMode.position)
    assert trajact == trajact2
    assert trajact != trajact3

    trajact4 = OSC.FollowTrajectoryAction.parse(trajact.get_element())
    prettyprint(trajact4.get_element(), None)
    assert trajact4 == trajact
    assert (
        version_validation("PrivateAction", trajact, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", trajact, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("PrivateAction", trajact, 2)
        == ValidationResponse.OK
    )

    with pytest.raises(TypeError):
        OSC.FollowTrajectoryAction("dummy", OSC.FollowingMode.follow)
    with pytest.raises(ValueError):
        OSC.FollowTrajectoryAction(traj, "dummy")
    with pytest.raises(ValueError):
        OSC.FollowTrajectoryAction(traj, OSC.FollowingMode.follow, "dummy")


def testParameterAddActions():
    pa = OSC.ParameterAddAction("Myparam", 3)
    pa.setVersion(minor=1)
    prettyprint(pa.get_element())
    pa2 = OSC.ParameterAddAction("Myparam", 3)
    pa3 = OSC.ParameterAddAction("Myparam", 2)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.ParameterAddAction.parse(pa.get_element())
    assert pa == pa4
    assert version_validation("GlobalAction", pa, 0) == ValidationResponse.OK
    assert version_validation("GlobalAction", pa, 1) == ValidationResponse.OK
    assert (
        version_validation("GlobalAction", pa, 2)
        == ValidationResponse.OSC_VERSION
    )


def testParameterMultiplyActions():
    pa = OSC.ParameterMultiplyAction("Myparam", 3)
    pa.setVersion(minor=1)
    prettyprint(pa)
    pa2 = OSC.ParameterMultiplyAction("Myparam", 3)
    pa3 = OSC.ParameterMultiplyAction("Myparam", 2)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.ParameterMultiplyAction.parse(pa.get_element())
    assert pa == pa4
    assert version_validation("GlobalAction", pa, 0) == ValidationResponse.OK
    assert version_validation("GlobalAction", pa, 1) == ValidationResponse.OK
    assert (
        version_validation("GlobalAction", pa, 2)
        == ValidationResponse.OSC_VERSION
    )


def testParameterSetActions():
    pa = OSC.ParameterSetAction("Myparam", 3)
    pa.setVersion(minor=1)
    prettyprint(pa)
    pa2 = OSC.ParameterSetAction("Myparam", 3)
    pa3 = OSC.ParameterSetAction("Myparam2", 3)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.ParameterSetAction.parse(pa.get_element())
    assert pa == pa4
    assert version_validation("GlobalAction", pa, 0) == ValidationResponse.OK
    assert version_validation("GlobalAction", pa, 1) == ValidationResponse.OK
    assert (
        version_validation("GlobalAction", pa, 2)
        == ValidationResponse.OSC_VERSION
    )


def testVariableAddActions():
    pa = OSC.VariableAddAction("Myparam", 3)
    prettyprint(pa.get_element())
    pa2 = OSC.VariableAddAction("Myparam", 3)
    pa3 = OSC.VariableAddAction("Myparam", 2)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.VariableAddAction.parse(pa.get_element())
    assert pa == pa4
    assert (
        version_validation("GlobalAction", pa, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("GlobalAction", pa, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("GlobalAction", pa, 2) == ValidationResponse.OK


def testVariableMultiplyActions():
    pa = OSC.VariableMultiplyAction("Myparam", 3)
    prettyprint(pa)
    pa2 = OSC.VariableMultiplyAction("Myparam", 3)
    pa3 = OSC.VariableMultiplyAction("Myparam", 2)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.VariableMultiplyAction.parse(pa.get_element())
    assert pa == pa4
    assert (
        version_validation("GlobalAction", pa, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("GlobalAction", pa, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("GlobalAction", pa, 2) == ValidationResponse.OK


def testVariableSetActions():
    pa = OSC.VariableSetAction("Myparam", 3)
    prettyprint(pa)
    pa2 = OSC.VariableSetAction("Myparam", 3)
    pa3 = OSC.VariableSetAction("Myparam2", 3)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.VariableSetAction.parse(pa.get_element())
    assert pa == pa4
    assert (
        version_validation("GlobalAction", pa, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("GlobalAction", pa, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("GlobalAction", pa, 2) == ValidationResponse.OK


def test_trafficsignalstateaction():
    tss = OSC.TrafficSignalStateAction("my signal", "red")
    prettyprint(tss)
    tss2 = OSC.TrafficSignalStateAction("my signal", "red")
    tss3 = OSC.TrafficSignalStateAction("my signal", "green")
    assert tss == tss2
    assert tss != tss3

    tss4 = OSC.TrafficSignalStateAction.parse(tss.get_element())
    prettyprint(tss4.get_element())
    assert tss4 == tss
    assert version_validation("GlobalAction", tss, 0) == ValidationResponse.OK
    assert version_validation("GlobalAction", tss, 1) == ValidationResponse.OK
    assert version_validation("GlobalAction", tss, 2) == ValidationResponse.OK


def test_addEntity():
    ent = OSC.AddEntityAction("my new thingy", OSC.WorldPosition())
    prettyprint(ent)
    ent2 = OSC.AddEntityAction("my new thingy", OSC.WorldPosition())
    ent3 = OSC.AddEntityAction("my new thingy2", OSC.WorldPosition())
    assert ent == ent2
    assert ent != ent3

    ent4 = OSC.AddEntityAction.parse(ent.get_element())
    prettyprint(ent4.get_element())
    assert ent4 == ent
    assert version_validation("GlobalAction", ent, 0) == ValidationResponse.OK
    assert version_validation("GlobalAction", ent, 1) == ValidationResponse.OK
    assert version_validation("GlobalAction", ent, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.AddEntityAction("ego", "dummy")


def test_deleteEntity():
    ent = OSC.DeleteEntityAction("my new thingy")
    prettyprint(ent)
    ent2 = OSC.DeleteEntityAction("my new thingy")
    ent3 = OSC.DeleteEntityAction("my new thingy2")
    assert ent == ent2
    assert ent != ent3

    ent4 = OSC.DeleteEntityAction.parse(ent.get_element())
    prettyprint(ent4)
    assert ent4 == ent
    assert version_validation("GlobalAction", ent, 0) == ValidationResponse.OK
    assert version_validation("GlobalAction", ent, 1) == ValidationResponse.OK
    assert version_validation("GlobalAction", ent, 2) == ValidationResponse.OK


def test_trafficsignalcontrolleraction():
    tsc_action = OSC.TrafficSignalControllerAction("Phase", "TSCRef_Name")
    tsc_action2 = OSC.TrafficSignalControllerAction("Phase", "TSCRef_Name")
    prettyprint(tsc_action.get_element())
    tsc_action3 = OSC.TrafficSignalControllerAction("Phase2", "TSCRef_Name")
    assert tsc_action == tsc_action2
    assert tsc_action != tsc_action3

    tsc_action4 = OSC.TrafficSignalControllerAction.parse(
        tsc_action.get_element()
    )
    assert tsc_action == tsc_action4
    assert (
        version_validation("GlobalAction", tsc_action, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("GlobalAction", tsc_action, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("GlobalAction", tsc_action, 2)
        == ValidationResponse.OK
    )


class TestTrafficSourceAction:
    def setup_method(self):
        self.prop = OSC.Properties()
        self.prop.add_file("mycontrollerfile.xml")
        self.controller = OSC.Controller("mycontroller", self.prop)
        self.traffic = OSC.TrafficDefinition("my traffic")
        self.traffic.add_controller(self.controller, 0.5)
        self.traffic.add_controller(
            OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
        )
        self.traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
        self.traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)

        self.entity_distribution = OSC.EntityDistribution()
        self.catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")
        self.entity_distribution.add_entity_distribution_entry(
            0.5, self.catalog_ref
        )
        self.traffic_distribution = OSC.TrafficDistribution()
        self.traffic_distribution.add_traffic_distribution_entry(
            0.5, self.entity_distribution
        )
        self.rate = 1
        self.radius = 1
        self.position = OSC.WorldPosition()
        self.velocity = 10

    def test_prettyprint(self):
        traffic_source_12 = OSC.TrafficSourceAction(
            self.rate, self.radius, self.position, self.traffic
        )
        traffic_source_12.setVersion(minor=2)
        prettyprint(traffic_source_12.get_element())
        traffic_source_13 = OSC.TrafficSourceAction(
            self.rate, self.radius, self.position, self.traffic_distribution
        )
        traffic_source_13.setVersion(minor=3)
        prettyprint(traffic_source_13.get_element())

    @pytest.mark.parametrize(
        "rate, radius, position, traffic_obj",
        [
            (1, 1, OSC.WorldPosition(), "traffic"),
            (1, 1, OSC.WorldPosition(), "traffic_distribution"),
        ],
    )
    def test_eq(self, rate, radius, position, traffic_obj):
        traffic = getattr(self, traffic_obj)
        traffic_source = OSC.TrafficSourceAction(
            self.rate, self.radius, self.position, traffic
        )
        traffic_source_copy = OSC.TrafficSourceAction(
            rate, radius, position, traffic
        )
        assert traffic_source == traffic_source_copy

    @pytest.mark.parametrize(
        "rate, radius, position, traffic_obj, velocity",
        [
            (2, 1, OSC.WorldPosition(0, 0), "traffic", 10),
            (1, 2, OSC.WorldPosition(0, 0), "traffic", 10),
            (1, 1, OSC.WorldPosition(1, 0), "traffic", 10),
            (1, 1, OSC.WorldPosition(0, 0), "traffic", 11),
            (2, 1, OSC.WorldPosition(0, 0), "traffic_distribution", 10),
            (1, 2, OSC.WorldPosition(0, 0), "traffic_distribution", 10),
            (1, 1, OSC.WorldPosition(1, 0), "traffic_distribution", 10),
            (1, 1, OSC.WorldPosition(0, 0), "traffic_distribution", 11),
        ],
    )
    def test_neq(self, rate, radius, position, traffic_obj, velocity):
        traffic = getattr(self, traffic_obj)

        traffic_source = OSC.TrafficSourceAction(
            self.rate, self.radius, self.position, traffic, self.velocity
        )

        traffic_source_copy = OSC.TrafficSourceAction(
            rate, radius, position, traffic, velocity
        )

        assert traffic_source != traffic_source_copy

    @pytest.mark.parametrize(
        "traffic_obj, attributes",
        [
            ("traffic", {"rate": "1.0", "radius": "1.0", "velocity": "10.0"}),
            (
                "traffic_distribution",
                {"rate": "1.0", "radius": "1.0", "speed": "10.0"},
            ),
        ],
    )
    def test_get_attributes(self, traffic_obj, attributes):
        traffic = getattr(self, traffic_obj)
        traffic_source = OSC.TrafficSourceAction(
            self.rate, self.radius, self.position, traffic, self.velocity
        )
        if traffic_obj == "traffic":
            traffic_source.setVersion(minor=1)
        assert traffic_source.get_attributes() == attributes

    @pytest.mark.parametrize(
        "traffic_obj",
        [
            ("traffic"),
            ("traffic_distribution"),
        ],
    )
    def test_parse(self, traffic_obj):
        traffic = getattr(self, traffic_obj)
        traffic_source = OSC.TrafficSourceAction(
            self.rate, self.radius, self.position, traffic, self.velocity
        )
        if traffic_obj == "traffic":
            traffic_source.setVersion(minor=2)
        parsed = OSC.TrafficSourceAction.parse(traffic_source.get_element())
        assert parsed == traffic_source

    @pytest.mark.parametrize(
        "traffic_obj, version, expected",
        [
            ("traffic", 2, ValidationResponse.OK),
            ("traffic", 3, ValidationResponse.OSC_VERSION),
            ("traffic_distribution", 2, ValidationResponse.OSC_VERSION),
            ("traffic_distribution", 3, ValidationResponse.OK),
        ],
    )
    def test_version_validation(self, traffic_obj, version, expected):
        traffic = getattr(self, traffic_obj)
        traffic_source = OSC.TrafficSourceAction(
            self.rate, self.radius, self.position, traffic, self.velocity
        )
        traffic_source.setVersion(minor=version)
        assert (
            version_validation("GlobalAction", traffic_source, version)
            == expected
        )

    def test_not_position(self):
        with pytest.raises(TypeError) as excinfo:
            OSC.TrafficSourceAction(
                self.rate,
                self.radius,
                "dummy",
                self.traffic_distribution,
                self.velocity,
            )
        assert str(excinfo.value) == "position input is not a valid Position"

    def test_not_correct_traffic(self):
        with pytest.raises(TypeError) as excinfo:
            OSC.TrafficSourceAction(
                self.rate, self.radius, self.position, "dummy", self.velocity
            )
        assert (
            str(excinfo.value)
            == "trafficdefinition input is not of type TrafficDefinitioon or TrafficDistribution. Should be TrafficDefinition for  version <= v1.2, TrafficDistribution otherwise"
        )


class TestTrafficSinkAction:

    @pytest.fixture
    def traffic_sink_action_12(self):
        prop = OSC.Properties()
        prop.add_file("mycontrollerfile.xml")
        controller = OSC.Controller("mycontroller", prop)

        traffic = OSC.TrafficDefinition("my traffic")
        traffic.add_controller(controller, 0.5)
        traffic.add_controller(
            OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
        )

        traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
        traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)

        traffic_sink_action = OSC.TrafficSinkAction(
            10, OSC.WorldPosition(), traffic, 1
        )
        traffic_sink_action.setVersion(minor=2)
        return traffic_sink_action

    @pytest.fixture
    def traffic_sink_action_13(self):
        traffic_sink_action = OSC.TrafficSinkAction(10, OSC.WorldPosition())
        return traffic_sink_action

    @pytest.fixture
    def traffic_sink_action(self, request):
        return request.getfixturevalue(request.param)

    @pytest.mark.parametrize(
        "traffic_sink_action",
        ["traffic_sink_action_12", "traffic_sink_action_13"],
        indirect=True,
    )
    def test_prettyprint(self, traffic_sink_action):
        prettyprint(traffic_sink_action.get_element())

    def test_eq(self, traffic_sink_action_12):
        prop = OSC.Properties()
        prop.add_file("mycontrollerfile.xml")
        controller = OSC.Controller("mycontroller", prop)

        traffic = OSC.TrafficDefinition("my traffic")
        traffic.add_controller(controller, 0.5)
        traffic.add_controller(
            OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
        )

        traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
        traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)

        traffic_sink_action = OSC.TrafficSinkAction(
            10, OSC.WorldPosition(), traffic, 1
        )
        traffic_sink_action.setVersion(minor=2)
        assert traffic_sink_action == traffic_sink_action_12

    def test_neq(self, traffic_sink_action_12):
        prop = OSC.Properties()
        prop.add_file("mycontrollerfile.xml")
        controller = OSC.Controller("mycontroller", prop)

        traffic = OSC.TrafficDefinition("my traffic")
        traffic.add_controller(controller, 0.5)
        traffic.add_controller(
            OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
        )

        traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
        traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)

        traffic_sink_action_radius = OSC.TrafficSinkAction(
            11, OSC.WorldPosition(), traffic, 1
        )
        traffic_sink_action_rate = OSC.TrafficSinkAction(
            10, OSC.WorldPosition(), traffic, rate=2
        )

        traffic.add_vehicle(OSC.VehicleCategory.truck, 0.1)

        traffic_sink_action_traffic = OSC.TrafficSinkAction(
            10, OSC.WorldPosition(), traffic, 1
        )

        assert traffic_sink_action_radius != traffic_sink_action_12
        assert traffic_sink_action_rate != traffic_sink_action_12
        assert traffic_sink_action_traffic != traffic_sink_action_12

    def test_eq(self, traffic_sink_action_13):
        traffic_sink_action = OSC.TrafficSinkAction(10, OSC.WorldPosition())
        assert traffic_sink_action == traffic_sink_action_13

    def test_neq(self, traffic_sink_action_13):
        traffic_sink_action_radius = OSC.TrafficSinkAction(
            11, OSC.WorldPosition()
        )
        traffic_sink_action_rate = OSC.TrafficSinkAction(
            10, OSC.WorldPosition(), rate=2
        )

        assert traffic_sink_action_radius != traffic_sink_action_13
        assert traffic_sink_action_rate != traffic_sink_action_13

    @pytest.mark.parametrize(
        ["traffic_sink_action", "attributes"],
        [
            ("traffic_sink_action_12", {"rate": "1.0", "radius": "10.0"}),
            ("traffic_sink_action_13", {"radius": "10.0"}),
        ],
        indirect=["traffic_sink_action"],
    )
    def test_get_attribute(self, traffic_sink_action, attributes):
        assert traffic_sink_action.get_attributes() == attributes

    @pytest.mark.parametrize(
        "traffic_sink_action",
        ["traffic_sink_action_12", "traffic_sink_action_13"],
        indirect=True,
    )
    def test_parse(self, traffic_sink_action):
        parsed = OSC.TrafficSinkAction.parse(traffic_sink_action.get_element())
        assert parsed == traffic_sink_action

    @pytest.mark.parametrize(
        ["traffic_sink_action", "version", "expected"],
        [
            ("traffic_sink_action_12", 0, ValidationResponse.OK),
            ("traffic_sink_action_12", 1, ValidationResponse.OK),
            ("traffic_sink_action_12", 2, ValidationResponse.OK),
            ("traffic_sink_action_12", 3, ValidationResponse.OSC_VERSION),
            ("traffic_sink_action_13", 0, ValidationResponse.OK),
            ("traffic_sink_action_13", 1, ValidationResponse.OK),
            ("traffic_sink_action_13", 2, ValidationResponse.OK),
            ("traffic_sink_action_13", 3, ValidationResponse.OK),
        ],
        indirect=["traffic_sink_action"],
    )
    def test_version_validation(self, traffic_sink_action, version, expected):
        assert (
            version_validation("GlobalAction", traffic_sink_action, version)
            == expected
        )

    def test_deprication_error(self):
        prop = OSC.Properties()
        prop.add_file("mycontrollerfile.xml")
        controller = OSC.Controller("mycontroller", prop)

        traffic = OSC.TrafficDefinition("my traffic")
        traffic.add_controller(controller, 0.5)
        traffic.add_controller(
            OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
        )

        traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
        traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)

        traffic_sink_action = OSC.TrafficSinkAction(
            10, OSC.WorldPosition(), traffic
        )
        with pytest.raises(OSC.OpenSCENARIOVersionError) as excinfo:
            traffic_sink_action.get_element()
        assert (
            str(excinfo.value)
            == "TrafficSinkAction with TrafficDefinition was depricated in OSC 1.3"
        )

    def test_not_position_error(self):
        with pytest.raises(TypeError) as excinfo:
            OSC.TrafficSinkAction(10, "dummy")
        assert str(excinfo.value) == "position input is not a valid Position"

    def test_not_traffic_definition_error(self):
        with pytest.raises(TypeError) as excinfo:
            OSC.TrafficSinkAction(10, OSC.WorldPosition(), "dummy")
        assert (
            str(excinfo.value)
            == "trafficdefinition input is not of type TrafficDefinition"
        )


class TestTrafficAreaAction:
    def setup_method(self):
        self.entity_distribution = OSC.EntityDistribution()
        self.catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")
        self.entity_distribution.add_entity_distribution_entry(
            0.5, self.catalog_ref
        )
        self.traffic_distribution = OSC.TrafficDistribution()
        self.traffic_distribution.add_traffic_distribution_entry(
            0.5, self.entity_distribution
        )

        self.polygon = OSC.Polygon(
            [
                OSC.WorldPosition(0, 0, 0),
                OSC.WorldPosition(1, 0, 0),
                OSC.WorldPosition(1, 1, 0),
            ]
        )
        self.roadrange = OSC.RoadRange("10").add_cursor("0").add_cursor("1")
        self.roadrange_list = [
            self.roadrange,
            OSC.RoadRange("10").add_cursor("1").add_cursor("2"),
        ]

    @pytest.mark.parametrize(
        "trafficarea_attr", ["polygon", "roadrange", "roadrange_list"]
    )
    def test_base(self, trafficarea_attr):
        trafficarea = getattr(self, trafficarea_attr)
        taa = OSC.TrafficAreaAction(
            False, 2, self.traffic_distribution, trafficarea
        )
        prettyprint(taa)

    def test_not_traffic_distribution(self):
        with pytest.raises(TypeError) as excinfo:
            OSC.TrafficAreaAction(False, 2, "incorrect_input", self.polygon)
        assert (
            str(excinfo.value)
            == "trafficdistribution input is not of type TrafficDistribution"
        )

    def test_not_traffic_area(self):
        with pytest.raises(TypeError) as excinfo:
            OSC.TrafficAreaAction(
                False, 2, self.traffic_distribution, "incorrect_input"
            )
        assert (
            str(excinfo.value)
            == "trafficarea input is not of type Polygon, RoadRange or list[RoadRange]"
        )

    @pytest.mark.parametrize(
        "trafficarea_attr", ["polygon", "roadrange", "roadrange_list"]
    )
    def test_eq(self, trafficarea_attr):
        trafficarea = getattr(self, trafficarea_attr)
        taa1 = OSC.TrafficAreaAction(
            False, 2, self.traffic_distribution, trafficarea
        )
        taa2 = OSC.TrafficAreaAction(
            False, 2, self.traffic_distribution, trafficarea
        )
        assert taa1 == taa2

    @pytest.mark.parametrize(
        "diff_field, val1, val2",
        [
            ("continuous", False, True),
            ("number_of_entities", 2, 1),
            ("traffic_distribution_weight", 0.5, 1.0),
            ("traffic_area_x", 1, 2),
        ],
    )
    def test_neq(self, diff_field, val1, val2):
        # Common setup
        entity_distribution = OSC.EntityDistribution()
        catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")
        entity_distribution.add_entity_distribution_entry(0.5, catalog_ref)

        # TrafficDistribution
        td1 = OSC.TrafficDistribution()
        td2 = OSC.TrafficDistribution()
        td_weight1 = 0.5
        td_weight2 = 0.5
        if diff_field == "traffic_distribution_weight":
            td_weight1 = val1
            td_weight2 = val2
        td1.add_traffic_distribution_entry(td_weight1, entity_distribution)
        td2.add_traffic_distribution_entry(td_weight2, entity_distribution)

        # TrafficArea
        ta_x1 = 1
        ta_x2 = 1
        if diff_field == "traffic_area_x":
            ta_x1 = val1
            ta_x2 = val2
        polygon_1 = OSC.Polygon(
            [
                OSC.WorldPosition(0, 0, 0),
                OSC.WorldPosition(ta_x1, 0, 0),
                OSC.WorldPosition(ta_x1, ta_x1, 0),
            ]
        )
        polygon_2 = OSC.Polygon(
            [
                OSC.WorldPosition(0, 0, 0),
                OSC.WorldPosition(ta_x2, 0, 0),
                OSC.WorldPosition(ta_x2, ta_x2, 0),
            ]
        )

        # continuous and number_of_entities
        continuous1 = False
        continuous2 = False
        number_of_entities1 = 2
        number_of_entities2 = 2
        if diff_field == "continuous":
            continuous1 = val1
            continuous2 = val2
        if diff_field == "number_of_entities":
            number_of_entities1 = val1
            number_of_entities2 = val2

        taa1 = OSC.TrafficAreaAction(
            continuous1, number_of_entities1, td1, polygon_1
        )
        taa2 = OSC.TrafficAreaAction(
            continuous2, number_of_entities2, td2, polygon_2
        )
        assert taa1 != taa2

    def test_parse(self):
        taa = OSC.TrafficAreaAction(
            False, 2, self.traffic_distribution, self.polygon
        )
        taa_parsed = OSC.TrafficAreaAction.parse(taa.get_element())
        assert taa == taa_parsed

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_validate_xml(self, version, expected):
        taa = OSC.TrafficAreaAction(
            False, 2, self.traffic_distribution, self.polygon
        )
        assert version_validation("GlobalAction", taa, version) == expected


def make_traffic(kind):
    prop = OSC.Properties()
    prop.add_file("mycontrollerfile.xml")
    controller = OSC.Controller("mycontroller", prop)
    if kind == "traffic_definition_diff":
        traffic = OSC.TrafficDefinition("my traffic")
        traffic.add_controller(controller, 0.5)
        traffic.add_controller(
            OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
        )
        traffic.add_vehicle(OSC.VehicleCategory.car, 1)
    elif kind == "traffic_definition":
        traffic = OSC.TrafficDefinition("my traffic")
        traffic.add_controller(controller, 0.5)
        traffic.add_controller(
            OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
        )
        traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
        traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)
    elif kind == "traffic_distribution":
        entity_distribution = OSC.EntityDistribution()
        catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")
        entity_distribution.add_entity_distribution_entry(0.5, catalog_ref)
        traffic = OSC.TrafficDistribution()
        traffic.add_traffic_distribution_entry(0.5, entity_distribution)
    elif kind == "traffic_distribution_diff":
        entity_distribution = OSC.EntityDistribution()
        catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")
        entity_distribution.add_entity_distribution_entry(0.5, catalog_ref)
        traffic = OSC.TrafficDistribution()
        traffic.add_traffic_distribution_entry(1, entity_distribution)
    else:
        raise ValueError(f"Unknown traffic kind: {kind}")
    return traffic


class TestTrafficSwarmAction:

    @pytest.fixture
    def shared_data(self):
        return (1, 1, 1, 1, 1, "test")

    @pytest.fixture
    def attributes_dict(self):
        return {
            "semiMajorAxis": "1.0",
            "semiMinorAxis": "1.0",
            "innerRadius": "1.0",
            "offset": "1.0",
            "numberOfVehicles": "1",
        }

    @pytest.fixture
    def traffic_definition(self):
        prop = OSC.Properties()
        prop.add_file("mycontrollerfile.xml")
        controller = OSC.Controller("mycontroller", prop)
        traffic_def = OSC.TrafficDefinition("my traffic")
        traffic_def.add_controller(controller, 0.5)
        traffic_def.add_controller(
            OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
        )
        traffic_def.add_vehicle(OSC.VehicleCategory.car, 0.9)
        traffic_def.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)
        return traffic_def

    @pytest.fixture
    def traffic_distribution(self):
        entity_distribution = OSC.EntityDistribution()
        catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")
        entity_distribution.add_entity_distribution_entry(0.5, catalog_ref)
        traffic_dist = OSC.TrafficDistribution()
        traffic_dist.add_traffic_distribution_entry(0.5, entity_distribution)
        return traffic_dist

    @pytest.fixture
    def traffic(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture
    def direction_of_travel(self):
        return OSC.DirectionOfTravelDistribution(0.5, 0.5)

    @pytest.fixture
    def tsa_11(self, shared_data, traffic_definition):
        (
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
        ) = shared_data
        velocity = 1
        tsa = OSC.TrafficSwarmAction(
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
            traffic_definition,
            velocity,
        )
        tsa.setVersion(minor=1)
        return tsa

    @pytest.fixture
    def tsa_12(self, shared_data, traffic_definition, direction_of_travel):
        (
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
        ) = shared_data
        vel_range = OSC.Range(1, 2)
        tsa = OSC.TrafficSwarmAction(
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
            traffic_definition,
            vel_range,
            direction_of_travel=direction_of_travel,
        )
        tsa.setVersion(minor=2)
        return tsa

    @pytest.fixture
    def tsa_13(self, shared_data, traffic_distribution, direction_of_travel):
        (
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
        ) = shared_data
        vel_range = OSC.Range(1, 2)
        tsa = OSC.TrafficSwarmAction(
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
            traffic_distribution,
            vel_range,
            direction_of_travel=direction_of_travel,
        )
        return tsa

    @pytest.fixture
    def traffic_swarm_action(self, request):
        return request.getfixturevalue(request.param)

    @pytest.mark.parametrize(
        "traffic_swarm_action",
        [
            "tsa_11",
            "tsa_12",
            "tsa_13",
        ],
        indirect=True,
    )
    def test_prettyprint(self, traffic_swarm_action):
        prettyprint(traffic_swarm_action.get_element())

    @pytest.mark.parametrize(
        [
            "traffic_swarm_action",
            "shared_data",
            "traffic",
            "velocity",
            "direction_of_travel",
        ],
        [
            ("tsa_11", "shared_data", "traffic_definition", 1, None),
            (
                "tsa_12",
                "shared_data",
                "traffic_definition",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                "shared_data",
                "traffic_distribution",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
        ],
        indirect=["traffic_swarm_action", "shared_data", "traffic"],
    )
    def test_eq(
        self,
        traffic_swarm_action,
        shared_data,
        traffic,
        velocity,
        direction_of_travel,
    ):
        (
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
        ) = shared_data
        tsa_copy = OSC.TrafficSwarmAction(
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
            traffic,
            velocity,
            direction_of_travel=direction_of_travel,
        )

        assert traffic_swarm_action == tsa_copy

    @pytest.mark.parametrize(
        [
            "traffic_swarm_action",
            "semimajoraxis",
            "semiminoraxis",
            "innerradius",
            "offset",
            "numberofvehicles",
            "centralobject",
            "traffic",
            "velocity",
            "dot",
        ],
        [
            ("tsa_11", 2, 1, 1, 1, 1, "test", "traffic_definition", 1, None),
            ("tsa_11", 1, 2, 1, 1, 1, "test", "traffic_definition", 1, None),
            ("tsa_11", 1, 1, 2, 1, 1, "test", "traffic_definition", 1, None),
            ("tsa_11", 1, 1, 1, 2, 1, "test", "traffic_definition", 1, None),
            ("tsa_11", 1, 1, 1, 1, 2, "test", "traffic_definition", 1, None),
            (
                "tsa_11",
                1,
                1,
                1,
                1,
                1,
                "test_diff",
                "traffic_definition",
                1,
                None,
            ),
            (
                "tsa_11",
                1,
                1,
                1,
                1,
                1,
                "test",
                "traffic_definition_diff",
                1,
                None,
            ),
            ("tsa_11", 1, 1, 1, 1, 1, "test", "traffic_definition", 2, None),
            (
                "tsa_12",
                2,
                1,
                1,
                1,
                1,
                "test",
                "traffic_definition",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_12",
                1,
                2,
                1,
                1,
                1,
                "test",
                "traffic_definition",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_12",
                1,
                1,
                2,
                1,
                1,
                "test",
                "traffic_definition",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_12",
                1,
                1,
                1,
                2,
                1,
                "test",
                "traffic_definition",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_12",
                1,
                1,
                1,
                1,
                2,
                "test",
                "traffic_definition",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_12",
                1,
                1,
                1,
                1,
                1,
                "test_diff",
                "traffic_definition",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_12",
                1,
                1,
                1,
                1,
                1,
                "test",
                "traffic_definition_diff",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_12",
                1,
                1,
                1,
                1,
                1,
                "test",
                "traffic_definition",
                OSC.Range(2, 3),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_12",
                1,
                1,
                1,
                1,
                1,
                "test",
                "traffic_definition",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.2, 0.8),
            ),
            (
                "tsa_13",
                2,
                1,
                1,
                1,
                1,
                "test",
                "traffic_distribution",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                1,
                2,
                1,
                1,
                1,
                "test",
                "traffic_distribution",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                1,
                1,
                2,
                1,
                1,
                "test",
                "traffic_distribution",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                1,
                1,
                1,
                2,
                1,
                "test",
                "traffic_distribution",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                1,
                1,
                1,
                1,
                2,
                "test",
                "traffic_distribution",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                1,
                1,
                1,
                1,
                1,
                "test_diff",
                "traffic_distribution",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                1,
                1,
                1,
                1,
                1,
                "test",
                "traffic_distribution_diff",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                1,
                1,
                1,
                1,
                1,
                "test",
                "traffic_distribution",
                OSC.Range(2, 3),
                OSC.DirectionOfTravelDistribution(0.5, 0.5),
            ),
            (
                "tsa_13",
                1,
                1,
                1,
                1,
                1,
                "test",
                "traffic_distribution",
                OSC.Range(1, 2),
                OSC.DirectionOfTravelDistribution(0.2, 0.8),
            ),
        ],
        indirect=["traffic_swarm_action"],
    )
    def test_neq(
        self,
        traffic_swarm_action,
        semimajoraxis,
        semiminoraxis,
        innerradius,
        offset,
        numberofvehicles,
        centralobject,
        traffic,
        velocity,
        dot,
    ):
        traffic = make_traffic(traffic)

        tsa_copy = OSC.TrafficSwarmAction(
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
            traffic,
            velocity,
            direction_of_travel=dot,
        )
        assert traffic_swarm_action != tsa_copy

    @pytest.mark.parametrize(
        "traffic_swarm_action", ["tsa_11", "tsa_12", "tsa_13"], indirect=True
    )
    def test_parse(self, traffic_swarm_action):
        parsed = OSC.TrafficSwarmAction.parse(
            traffic_swarm_action.get_element()
        )
        assert parsed == traffic_swarm_action

    @pytest.mark.parametrize(
        ["traffic_swarm_action", "attributes_dict", "velocity"],
        [
            ("tsa_11", "attributes_dict", True),
            ("tsa_12", "attributes_dict", False),
            ("tsa_13", "attributes_dict", False),
        ],
        indirect=["traffic_swarm_action", "attributes_dict"],
    )
    def test_get_attributes(
        self, traffic_swarm_action, attributes_dict, velocity
    ):
        if velocity:
            attributes_dict["velocity"] = "1.0"
        assert traffic_swarm_action.get_attributes() == attributes_dict

    @pytest.mark.parametrize(
        ["traffic_swarm_action", "version", "expected"],
        [
            ("tsa_11", 1, ValidationResponse.OK),
            ("tsa_11", 2, ValidationResponse.OSC_VERSION),
            ("tsa_11", 3, ValidationResponse.OSC_VERSION),
            ("tsa_12", 1, ValidationResponse.OSC_VERSION),
            ("tsa_12", 2, ValidationResponse.OK),
            ("tsa_12", 3, ValidationResponse.OSC_VERSION),
            ("tsa_13", 1, ValidationResponse.OSC_VERSION),
            ("tsa_13", 2, ValidationResponse.OSC_VERSION),
            ("tsa_13", 3, ValidationResponse.OK),
        ],
        indirect=["traffic_swarm_action"],
    )
    def test_version_validation(self, traffic_swarm_action, version, expected):
        assert (
            version_validation("GlobalAction", traffic_swarm_action, version)
            == expected
        )

    def test_not_traffic_distribution(self, shared_data):
        (
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
        ) = shared_data

        with pytest.raises(TypeError) as excinfo:
            OSC.TrafficSwarmAction(
                semimajoraxis,
                semiminoraxis,
                innerradius,
                offset,
                numberofvehicles,
                centralobject,
                "dummy",
            )
        assert (
            str(excinfo.value)
            == "trafficdefinition input is not of type TrafficDefinitioon or TrafficDistribution. Should be TrafficDefinition for  version <= v1.2, TrafficDistribution otherwise"
        )

    def test_not_direction_of_travel(self, shared_data, traffic_distribution):
        (
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
        ) = shared_data

        with pytest.raises(TypeError) as excinfo:
            OSC.TrafficSwarmAction(
                semimajoraxis,
                semiminoraxis,
                innerradius,
                offset,
                numberofvehicles,
                centralobject,
                traffic_distribution,
                direction_of_travel="dummy",
            )
        assert (
            str(excinfo.value)
            == "direction_of_travel is not of type DirectionOfTravelDistribution"
        )


def test_environmentaction():
    tod = OSC.TimeOfDay(True, 2020, 10, 1, 18, 30, 30)
    weather = OSC.Weather(OSC.FractionalCloudCover.sevenOktas, 100)
    weather2 = OSC.Weather(
        OSC.CloudState.free,
        precipitation=OSC.Precipitation(OSC.PrecipitationType.rain, 3),
        fog=OSC.Fog(10, OSC.BoundingBox(1, 2, 3, 4, 5, 6)),
        sun=OSC.Sun(1, 1, 1),
    )
    rc = OSC.RoadCondition(1)

    env = OSC.Environment("Env_name", tod, weather, rc)
    ea = OSC.EnvironmentAction(env)
    prettyprint(ea.get_element())
    ea2 = OSC.EnvironmentAction(env)
    ea3 = OSC.EnvironmentAction(env)
    assert ea == ea2
    assert ea == ea3

    ea4 = OSC.EnvironmentAction.parse(ea.get_element())
    prettyprint(ea4.get_element())
    assert ea == ea4
    assert (
        version_validation("GlobalAction", ea, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("GlobalAction", ea, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("GlobalAction", ea, 2) == ValidationResponse.OK
    weather2 = OSC.Weather(
        OSC.CloudState.free,
        precipitation=OSC.Precipitation(OSC.PrecipitationType.rain, 3),
        fog=OSC.Fog(10, OSC.BoundingBox(1, 2, 3, 4, 5, 6)),
        sun=OSC.Sun(1, 1, 1),
    )
    env2 = OSC.Environment("Env_name", tod, weather2, rc)

    ea5 = OSC.EnvironmentAction(env2)
    assert version_validation("GlobalAction", ea5, 0) == ValidationResponse.OK
    assert version_validation("GlobalAction", ea5, 1) == ValidationResponse.OK
    assert (
        version_validation("GlobalAction", ea5, 2)
        == ValidationResponse.OSC_VERSION
    )

    with pytest.raises(TypeError):
        OSC.EnvironmentAction("dummy")


def test_trafficstopaction():
    tsa = OSC.TrafficStopAction("hej")
    tsa2 = OSC.TrafficStopAction("hej")
    tsa3 = OSC.TrafficStopAction("hey")
    prettyprint(tsa)
    assert tsa == tsa2
    assert tsa != tsa3

    tsa4 = OSC.TrafficStopAction.parse(tsa.get_element())
    prettyprint(tsa4.get_element())
    assert tsa == tsa4
    assert (
        version_validation("GlobalAction", tsa, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("GlobalAction", tsa, 1) == ValidationResponse.OK
    assert version_validation("GlobalAction", tsa, 2) == ValidationResponse.OK


def test_customcommandaction():
    cca = OSC.CustomCommandAction("custom_command", "content")
    prettyprint(cca)
    cca2 = OSC.CustomCommandAction("custom_command", "content")
    assert cca == cca2
    cca3 = OSC.CustomCommandAction("another_custom_command", "content")
    assert cca != cca3
    cca4 = OSC.CustomCommandAction.parse(cca.get_element())
    prettyprint(cca4.get_element())
    assert cca == cca4

    assert (
        version_validation("CustomCommandAction", cca, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("CustomCommandAction", cca, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("CustomCommandAction", cca, 2)
        == ValidationResponse.OK
    )


def test_userdefinedaction():
    cca = OSC.CustomCommandAction("custom_command", "content")
    cca2 = OSC.CustomCommandAction("another_custom_command", "content")
    uda = OSC.UserDefinedAction(cca)
    prettyprint(uda)
    uda2 = OSC.UserDefinedAction(cca)
    assert uda == uda2
    uda3 = OSC.UserDefinedAction(cca2)
    assert uda != uda3
    uda4 = OSC.UserDefinedAction.parse(uda.get_element())
    prettyprint(uda4)
    assert uda4 == uda
    assert (
        version_validation("UserDefinedAction", uda, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("UserDefinedAction", uda, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("UserDefinedAction", uda, 2)
        == ValidationResponse.OK
    )


def test_lightstateaction():
    lsa = OSC.LightStateAction(
        OSC.VehicleLightType.brakeLights,
        OSC.LightMode.on,
        transition_time=0.1,
        color=OSC.Color(OSC.ColorType.black, OSC.ColorRGB(0, 0, 0)),
    )
    lsa2 = OSC.LightStateAction(
        OSC.VehicleLightType.brakeLights,
        OSC.LightMode.on,
        transition_time=0.1,
        color=OSC.Color(OSC.ColorType.black, OSC.ColorRGB(0, 0, 0)),
    )
    lsa3 = OSC.LightStateAction(
        OSC.UserDefinedLight("super light"),
        OSC.LightMode.on,
        transition_time=0.1,
        color=OSC.Color(OSC.ColorType.black, OSC.ColorRGB(0, 0, 0)),
    )
    prettyprint(lsa)
    prettyprint(lsa3)
    assert lsa == lsa2
    assert lsa != lsa3
    lsa4 = OSC.LightStateAction.parse(lsa.get_element())
    assert lsa4 == lsa
    lsa5 = OSC.LightStateAction.parse(lsa3.get_element())
    assert lsa5 == lsa3
    assert (
        version_validation("PrivateAction", lsa, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("PrivateAction", lsa, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("PrivateAction", lsa, 2)
        == ValidationResponse.XSD_FAILURE
    )

    with pytest.raises(TypeError):
        OSC.LightStateAction("dummy", OSC.LightMode.flashing)
    with pytest.raises(ValueError):
        OSC.LightStateAction(OSC.VehicleLightType.fogLights, "dummy")
    with pytest.raises(TypeError):
        OSC.LightStateAction(
            OSC.VehicleLightType.fogLights,
            OSC.LightMode.flashing,
            color="dummy",
        )


def test_speedprofileaction():
    spa = OSC.SpeedProfileAction(
        [5, 4, 3],
        OSC.FollowingMode.follow,
        [1, 2, 3],
        OSC.DynamicsConstraints(1, 1, 1),
        "ego",
    )
    spa2 = OSC.SpeedProfileAction(
        [5, 4, 3],
        OSC.FollowingMode.follow,
        [1, 2, 3],
        OSC.DynamicsConstraints(1, 1, 1),
        "ego",
    )
    spa3 = OSC.SpeedProfileAction([5, 4, 3], OSC.FollowingMode.follow)
    prettyprint(spa)
    prettyprint(spa3)
    assert spa == spa2
    assert spa != spa3
    spa4 = OSC.SpeedProfileAction.parse(spa.get_element())
    prettyprint(spa4)
    assert spa == spa4
    assert (
        version_validation("PrivateAction", spa3, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("PrivateAction", spa3, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("PrivateAction", spa3, 2) == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.SpeedProfileAction([1, 1, 1], "dummy")
    with pytest.raises(TypeError):
        OSC.SpeedProfileAction(
            [1, 1, 1], OSC.FollowingMode.follow, dynamics_constraint="dummy"
        )


def test_animation_action():
    aa = OSC.AnimationAction(
        OSC.VehicleComponentType.doorFrontRight, 1, False, 1
    )

    prettyprint(aa)
    aa2 = OSC.AnimationAction(
        OSC.VehicleComponentType.doorFrontRight, 1, False, 1
    )
    aa3 = OSC.AnimationAction(
        OSC.PedestrianAnimation(OSC.PedestrianMotionType.squatting),
        1,
        False,
        1,
    )

    assert aa == aa2
    assert aa != aa3
    aa4 = OSC.AnimationAction.parse(aa.get_element())
    prettyprint(aa4)
    assert aa == aa4
    assert (
        version_validation("PrivateAction", aa, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("PrivateAction", aa, 1)
        == ValidationResponse.OSC_VERSION
    )
    # BUG IN XSD
    assert (
        version_validation("PrivateAction", aa, 2)
        == ValidationResponse.XSD_FAILURE
    )
    with pytest.raises(ValueError):
        OSC.AnimationAction("dummy")


class TestConnectTrailerAction:
    def test_base(self):
        ta = OSC.ConnectTrailerAction("my Trailer")
        prettyprint(ta)

    def test_eq(self):
        ta = OSC.ConnectTrailerAction("my Trailer")
        ta2 = OSC.ConnectTrailerAction("my Trailer")
        assert ta == ta2

    def test_neq(self):
        ta = OSC.ConnectTrailerAction("my Trailer")
        ta2 = OSC.ConnectTrailerAction("my other Trailer")
        assert ta != ta2

    def test_parse(self):
        ta = OSC.ConnectTrailerAction("my Trailer")
        ta_parsed = OSC.ConnectTrailerAction.parse(ta.get_element())
        assert ta == ta_parsed

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_validate_xml(self, version, expected):
        ta = OSC.ConnectTrailerAction("my Trailer")
        assert version_validation("PrivateAction", ta, version) == expected


class TestDisconnectTrailerAction:
    def test_base(self):
        ta = OSC.DisconnectTrailerAction()
        prettyprint(ta)

    def test_eq(self):
        ta = OSC.DisconnectTrailerAction()
        ta2 = OSC.DisconnectTrailerAction()
        assert ta == ta2

    def test_parse(self):
        ta = OSC.DisconnectTrailerAction()
        ta2 = OSC.DisconnectTrailerAction.parse(ta.get_element())
        assert ta == ta2

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_validate_xml(self, version, expected):
        ta = OSC.DisconnectTrailerAction()
        assert version_validation("PrivateAction", ta, version) == expected


class TestSetMonitorAction:
    @pytest.fixture(name="sma")
    def set_monitor_action(self):
        return OSC.SetMonitorAction("my_monitor", True)

    def test_set_monitor_action(self, sma):
        prettyprint(sma.get_element())
        element = sma.get_element()
        assert element.tag == "GlobalAction"
        set_monitor_elment = OSC.utils.find_mandatory_field(
            element, "SetMonitorAction"
        )
        assert set_monitor_elment.tag == "SetMonitorAction"
        assert set_monitor_elment.attrib["monitorRef"] == "my_monitor"
        assert set_monitor_elment.attrib["value"] == "true"

    def test_set_monitor_action_eq(self, sma):
        sma2 = OSC.SetMonitorAction("my_monitor", True)
        prettyprint(sma2)
        assert sma == sma2

    def test_set_monitor_action_ne(self, sma):
        sma3 = OSC.SetMonitorAction("my_monitor", False)
        assert sma != sma3
        sma4 = OSC.SetMonitorAction("my_monitor2", True)
        assert sma != sma4

    def test_set_monitor_action_parse(self, sma):
        sma4 = OSC.SetMonitorAction.parse(sma.get_element())
        prettyprint(sma4)
        assert sma == sma4

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_set_monitor_action_version_validation(
        self, version, expected, sma
    ):
        assert version_validation("GlobalAction", sma, version) == expected

    def test_set_monitor_action_type_error(self, sma):
        with pytest.raises(ValueError):
            OSC.SetMonitorAction("my_monitor", "dummy")
        with pytest.raises(TypeError):
            OSC.SetMonitorAction(123, True)
        with pytest.raises(TypeError):
            OSC.SetMonitorAction(123, None)
        with pytest.raises(TypeError):
            OSC.SetMonitorAction(None, True)
        with pytest.raises(TypeError):
            OSC.SetMonitorAction()
