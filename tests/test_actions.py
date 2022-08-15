"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import pytest


from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
from scenariogeneration.helpers import prettify
from scenariogeneration.xosc.actions import TrafficSignalControllerAction
from scenariogeneration.xosc.enumerations import ReferenceContext
from scenariogeneration.xosc.exceptions import NoActionsDefinedError

TD = OSC.TransitionDynamics(OSC.DynamicsShapes.step, OSC.DynamicsDimension.rate, 1.0)

tod = OSC.TimeOfDay(True, 2020, 10, 1, 18, 30, 30)
weather = OSC.Weather(OSC.CloudState.free, 100)
rc = OSC.RoadCondition(1)
prop = OSC.Properties()
prop.add_file("mycontrollerfile.xml")
controller = OSC.Controller("mycontroller", prop)
traffic = OSC.TrafficDefinition("my traffic")
traffic.add_controller(controller, 0.5)
traffic.add_controller(OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5)
traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)
env = OSC.Environment("Env_name", tod, weather, rc)


@pytest.mark.parametrize(
    "action",
    [
        OSC.EnvironmentAction(env),
        OSC.AddEntityAction("my new thingy", OSC.WorldPosition()),
        OSC.DeleteEntityAction("my new thingy"),
        OSC.ParameterAddAction("Myparam", 3),
        OSC.ParameterSetAction("Myparam", 3),
        OSC.TrafficSignalStateAction("my signal", "red"),
        OSC.TrafficSignalControllerAction("Phase", "TSCRef_Name"),
        OSC.TrafficSourceAction(10, 10, OSC.WorldPosition(), traffic, 100),
        OSC.TrafficSinkAction(10, OSC.WorldPosition(), traffic, 10),
        OSC.TrafficSwarmAction(10, 20, 10, 2, 10, "Ego", traffic),
        OSC.TrafficStopAction("Stop_Action"),
    ],
)
def test_global_action_factory(action):

    factoryoutput = OSC.actions._GlobalActionFactory.parse_globalaction(
        action.get_element()
    )
    prettyprint(action, None)
    prettyprint(factoryoutput, None)
    assert action == factoryoutput


route = OSC.Route("myroute")
route.add_waypoint(OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest)
route.add_waypoint(OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest)
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


@pytest.mark.parametrize(
    "action",
    [
        OSC.AbsoluteSpeedAction(50.0, TD),
        OSC.RelativeSpeedAction(1, "Ego", TD),
        OSC.LongitudinalDistanceAction(
            "Ego", max_acceleration=3, max_deceleration=2, max_speed=4, distance=1
        ),
        OSC.AbsoluteLaneChangeAction(1, TD),
        OSC.RelativeLaneChangeAction(1, "Ego", TD, 0.2),
        OSC.AbsoluteLaneOffsetAction(1, OSC.DynamicsShapes.step, 3, False),
        OSC.RelativeLaneOffsetAction(1, "Ego", OSC.DynamicsShapes.step, 3, False),
        OSC.LateralDistanceAction("Ego", 3, max_speed=50),
        OSC.VisibilityAction(True, False, True),
        OSC.SynchronizeAction(
            "Ego",
            OSC.WorldPosition(0, 0, 0, 0, 0, 0),
            OSC.WorldPosition(10, 0, 0, 0, 0, 0),
            target_tolerance=1,
            target_tolerance_master=2,
        ),
        OSC.ControllerAction(ass, ocv_action, aca),
        OSC.AssignControllerAction(cnt),
        ocv_action,
        OSC.ActivateControllerAction(True, False),
        OSC.TeleportAction(OSC.WorldPosition(1)),
        OSC.AssignRouteAction(route),
        OSC.FollowTrajectoryAction(
            traj,
            OSC.FollowMode.position,
            reference_domain=ReferenceContext.absolute,
            offset=3,
            scale=4,
        ),
        OSC.AcquirePositionAction(OSC.WorldPosition(1, 1, 0, 0, 0, 0)),
    ],
)
def test_private_action_factory(action):

    factoryoutput = OSC.actions._PrivateActionFactory.parse_privateaction(
        action.get_element()
    )
    prettyprint(action, None)
    prettyprint(factoryoutput, None)

    assert action == factoryoutput
    assert factoryoutput == action


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


def test_speedaction_rel():
    speedaction = OSC.RelativeSpeedAction(1, "Ego", TD)

    prettyprint(speedaction.get_element())
    speedaction2 = OSC.RelativeSpeedAction(1, "Ego", TD)
    speedaction3 = OSC.RelativeSpeedAction(1, "Ego1", TD)
    assert speedaction == speedaction2
    assert speedaction != speedaction3

    speedaction4 = OSC.RelativeSpeedAction.parse(speedaction.get_element())
    assert speedaction == speedaction4


def test_longdistaction_dist():
    longdist = OSC.LongitudinalDistanceAction(
        "Ego", max_acceleration=3, max_deceleration=2, max_speed=4, distance=1
    )
    prettyprint(longdist.get_element())
    longdist2 = OSC.LongitudinalDistanceAction(
        "Ego", max_acceleration=3, max_deceleration=2, max_speed=4, distance=1
    )
    longdist3 = OSC.LongitudinalDistanceAction(
        "Ego", max_acceleration=3, max_deceleration=2, max_speed=4, distance=2
    )
    assert longdist == longdist2
    assert longdist != longdist3

    longdist4 = OSC.LongitudinalDistanceAction.parse(longdist.get_element())
    prettyprint(longdist4.get_element())
    assert longdist == longdist4


def test_longdistaction_time():
    longdist = OSC.LongitudinalDistanceAction("Ego", max_acceleration=1, timeGap=2)
    prettyprint(longdist.get_element())
    longdist2 = OSC.LongitudinalDistanceAction("Ego", max_acceleration=1, timeGap=2)
    longdist3 = OSC.LongitudinalDistanceAction("Ego", max_acceleration=1, timeGap=3)
    assert longdist == longdist2
    assert longdist != longdist3

    longdist4 = OSC.LongitudinalDistanceAction.parse(longdist.get_element())
    prettyprint(longdist4.get_element())
    assert longdist == longdist4


def test_lanechange_abs():
    lanechange = OSC.AbsoluteLaneChangeAction(1, TD)
    prettyprint(lanechange.get_element())
    lanechange2 = OSC.AbsoluteLaneChangeAction(1, TD)
    lanechange3 = OSC.AbsoluteLaneChangeAction(2, TD)
    assert lanechange == lanechange2
    assert lanechange != lanechange3

    lanechange4 = OSC.AbsoluteLaneChangeAction.parse(lanechange.get_element())
    assert lanechange == lanechange4


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


def test_laneoffset_abs():
    laneoffset = OSC.AbsoluteLaneOffsetAction(1, OSC.DynamicsShapes.step, 3, False)
    prettyprint(laneoffset.get_element(), None)
    laneoffset2 = OSC.AbsoluteLaneOffsetAction(1, OSC.DynamicsShapes.step, 3, False)
    laneoffset3 = OSC.AbsoluteLaneOffsetAction(1, OSC.DynamicsShapes.step, 2, True)

    assert laneoffset == laneoffset2
    assert laneoffset != laneoffset3

    laneoffset4 = OSC.AbsoluteLaneOffsetAction.parse(laneoffset.get_element())
    prettyprint(laneoffset.get_element(), None)
    assert laneoffset == laneoffset4


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


def test_teleport():
    teleport = OSC.TeleportAction(OSC.WorldPosition())
    prettyprint(teleport.get_element())
    teleport2 = OSC.TeleportAction(OSC.WorldPosition())
    teleport3 = OSC.TeleportAction(OSC.WorldPosition(1))
    assert teleport == teleport2
    assert teleport != teleport3
    teleport4 = OSC.TeleportAction.parse(teleport.get_element())
    assert teleport == teleport4


def test_assign_route():

    route = OSC.Route("myroute")
    route.add_waypoint(OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest)
    route.add_waypoint(OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest)
    ara = OSC.AssignRouteAction(route)
    prettyprint(ara.get_element(), None)
    ara2 = OSC.AssignRouteAction(route)
    route2 = OSC.Route("myroute2")
    route2.add_waypoint(OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest)
    route2.add_waypoint(OSC.WorldPosition(1, 1, 1, 0, 0, 0), OSC.RouteStrategy.shortest)
    ara3 = OSC.AssignRouteAction(route2)
    assert ara == ara2
    assert ara != ara3

    ara4 = OSC.AssignRouteAction.parse(ara.get_element())
    prettyprint(ara4.get_element(), None)
    assert ara == ara4


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


def test_controller_action():
    aca = OSC.ActivateControllerAction(True, True)
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")
    cnt = OSC.Controller("mycontroller", prop)

    ass = OSC.AssignControllerAction(cnt)

    ocva = OSC.OverrideControllerValueAction()
    ocva.set_brake(True, 2)
    ca = OSC.ControllerAction(ass, ocva, aca)
    ca2 = OSC.ControllerAction.parse(ca.get_element())
    prettyprint(ca.get_element(), None)
    prettyprint(ca2.get_element(), None)
    assert ca == ca2


def test_activate_controller_action():
    aca = OSC.ActivateControllerAction(True, True)
    prettyprint(aca.get_element(), None)
    aca2 = OSC.ActivateControllerAction(True, True)
    aca3 = OSC.ActivateControllerAction(True, False)

    assert aca == aca2
    assert aca != aca3

    aca4 = OSC.ActivateControllerAction.parse(aca.get_element())
    prettyprint(aca4.get_element(), None)
    assert aca4 == aca
    aca5 = OSC.ActivateControllerAction()
    prettyprint(aca5)
    aca6 = OSC.ActivateControllerAction.parse(aca5.get_element())


def test_assign_controller_action():
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")

    cnt = OSC.Controller("mycontroller", prop)

    aca = OSC.AssignControllerAction(cnt)
    prettyprint(aca.get_element(), None)

    prop2 = OSC.Properties()
    prop2.add_property("mything", "3")
    prop2.add_property("theotherthing", "true")

    cnt2 = OSC.Controller("mycontroller", prop2)

    aca2 = OSC.AssignControllerAction(cnt)
    aca3 = OSC.AssignControllerAction(cnt2)
    assert aca == aca2
    assert aca != aca3

    aca4 = OSC.AssignControllerAction.parse(aca.get_element())
    prettyprint(aca4.get_element(), None)
    assert aca4 == aca


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


def test_visual_action():
    va = OSC.VisibilityAction(True, False, True)
    prettyprint(va.get_element(), None)
    va2 = OSC.VisibilityAction(True, False, True)
    va3 = OSC.VisibilityAction(True, False, False)
    assert va == va2
    assert va != va3

    va4 = OSC.VisibilityAction.parse(va.get_element())
    prettyprint(va4.get_element(), None)
    assert va4 == va


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
        OSC.FollowMode.position,
        reference_domain=ReferenceContext.absolute,
        offset=3,
        scale=4,
    )
    prettyprint(trajact.get_element(), None)

    trajact2 = OSC.FollowTrajectoryAction(
        traj,
        OSC.FollowMode.position,
        reference_domain=ReferenceContext.absolute,
        offset=3,
        scale=4,
    )
    traj2 = OSC.Trajectory("my_trajectory", True)
    traj2.add_shape(polyline)

    trajact3 = OSC.FollowTrajectoryAction(traj2, OSC.FollowMode.position)
    assert trajact == trajact2
    assert trajact != trajact3

    trajact4 = OSC.FollowTrajectoryAction.parse(trajact.get_element())
    prettyprint(trajact4.get_element(), None)
    assert trajact4 == trajact


def testParameterAddActions():
    pa = OSC.ParameterAddAction("Myparam", 3)
    prettyprint(pa.get_element())
    pa2 = OSC.ParameterAddAction("Myparam", 3)
    pa3 = OSC.ParameterAddAction("Myparam", 2)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.ParameterAddAction.parse(pa.get_element())
    assert pa == pa4


def testParameterMultiplyActions():
    pa = OSC.ParameterMultiplyAction("Myparam", 3)
    prettyprint(pa)
    pa2 = OSC.ParameterMultiplyAction("Myparam", 3)
    pa3 = OSC.ParameterMultiplyAction("Myparam", 2)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.ParameterMultiplyAction.parse(pa.get_element())
    assert pa == pa4


def testParameterSetActions():
    pa = OSC.ParameterSetAction("Myparam", 3)
    prettyprint(pa)
    pa2 = OSC.ParameterSetAction("Myparam", 3)
    pa3 = OSC.ParameterSetAction("Myparam2", 3)
    assert pa == pa2
    assert pa != pa3

    pa4 = OSC.ParameterSetAction.parse(pa.get_element())
    assert pa == pa4


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


def test_trafficsignalcontrolleraction():
    tsc_action = OSC.TrafficSignalControllerAction("Phase", "TSCRef_Name")
    tsc_action2 = OSC.TrafficSignalControllerAction("Phase", "TSCRef_Name")
    prettyprint(tsc_action.get_element())
    tsc_action3 = OSC.TrafficSignalControllerAction("Phase2", "TSCRef_Name")
    assert tsc_action == tsc_action2
    assert tsc_action != tsc_action3

    tsc_action4 = OSC.TrafficSignalControllerAction.parse(tsc_action.get_element())
    assert tsc_action == tsc_action4


def test_trafficsourceaction():

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

    source_action = OSC.TrafficSourceAction(10, 10, OSC.WorldPosition(), traffic, 100)

    # prettyprint(source_action.get_element())

    source_action = OSC.TrafficSourceAction(10, 10, OSC.WorldPosition(), traffic)
    prettyprint(source_action.get_element())

    source_action2 = OSC.TrafficSourceAction(10, 10, OSC.WorldPosition(), traffic)
    source_action3 = OSC.TrafficSourceAction(10, 1, OSC.WorldPosition(), traffic)
    assert source_action == source_action2
    assert source_action != source_action3

    source_action4 = OSC.TrafficSourceAction.parse(source_action.get_element())
    prettyprint(source_action4.get_element())
    assert source_action == source_action4


def test_trafficsinkaction():

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

    sink_action = OSC.TrafficSinkAction(10, OSC.WorldPosition(), traffic, 10)
    prettyprint(sink_action.get_element())
    sink_action2 = OSC.TrafficSinkAction(10, OSC.WorldPosition(), traffic, 10)
    sink_action3 = OSC.TrafficSinkAction(9, OSC.WorldPosition(), traffic, 10)

    assert sink_action == sink_action2
    assert sink_action != sink_action3

    sink_action4 = OSC.TrafficSinkAction.parse(sink_action.get_element())
    prettyprint(sink_action4.get_element())
    assert sink_action == sink_action4


def test_trafficswarmaction():

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

    swarm_action = OSC.TrafficSwarmAction(10, 20, 10, 2, 10, "Ego", traffic)
    # prettyprint(swarm_action.get_element())

    swarm_action2 = OSC.TrafficSwarmAction(10, 20, 10, 2, 10, "Ego", traffic)
    swarm_action3 = OSC.TrafficSwarmAction(
        10, 20, 10, 2, 10, "Ego", traffic, 10, "Traffic_name"
    )
    prettyprint(swarm_action3.get_element())

    assert swarm_action == swarm_action2
    assert swarm_action != swarm_action3

    swarm_action4 = OSC.TrafficSwarmAction.parse(swarm_action3.get_element())
    prettyprint(swarm_action4.get_element())
    assert swarm_action3 == swarm_action4


def test_environmentaction():
    tod = OSC.TimeOfDay(True, 2020, 10, 1, 18, 30, 30)
    weather = OSC.Weather(OSC.CloudState.free, 100)
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


def test_customcommandaction():
    cca = OSC.CustomCommandAction("custom_command")
    prettyprint(cca)
    cca2 = OSC.CustomCommandAction("custom_command")
    assert cca == cca2
    cca3 = OSC.CustomCommandAction("another_custom_command")
    assert cca != cca3
    cca4 = OSC.CustomCommandAction.parse(cca.get_element())
    prettyprint(cca4.get_element())
    assert cca == cca4


def test_userdefinedaction():
    uda = OSC.UserDefinedAction()
    prettyprint(uda)
    uda2 = OSC.UserDefinedAction()
    assert uda == uda2
    cca = OSC.CustomCommandAction("custom_command")
    uda.add_custom_command_action(cca)
    prettyprint(uda)
    assert uda != uda2
    uda2.add_custom_command_action(cca)
    assert uda == uda2
    cca2 = OSC.CustomCommandAction("another_custom_command")
    uda.add_custom_command_action(cca2)
    assert uda != uda2
    uda2.add_custom_command_action(cca2)
    assert uda == uda2
    uda3 = OSC.UserDefinedAction.parse(uda.get_element())
    prettyprint(uda3)
    assert uda3 == uda
