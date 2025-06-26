"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
from copy import deepcopy

import pytest

from scenariogeneration import prettyprint
from scenariogeneration import xosc as OSC

from .xml_validator import ValidationResponse, version_validation


@pytest.fixture(autouse=True)
def reset_version():
    OSC.enumerations.VersionBase().setVersion(minor=2)


def test_endofroadcond():
    cond = OSC.EndOfRoadCondition(20)
    prettyprint(cond.get_element(), None)

    cond2 = OSC.EndOfRoadCondition(20)
    cond3 = OSC.EndOfRoadCondition(23)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.EndOfRoadCondition.parse(cond.get_element())
    assert cond == cond4

    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )


def test_collision_condition():
    cond = OSC.CollisionCondition("Ego")
    prettyprint(cond.get_element())
    cond1 = OSC.CollisionCondition(OSC.ObjectType.pedestrian)
    prettyprint(cond1.get_element())
    cond2 = OSC.CollisionCondition("Ego")
    assert cond == cond2
    assert cond != cond1

    cond3 = OSC.CollisionCondition.parse(cond.get_element())
    assert cond3 == cond
    cond4 = OSC.CollisionCondition.parse(cond1.get_element())
    assert cond4 == cond1

    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )


def test_offroadcondition():
    cond = OSC.OffroadCondition(20)
    prettyprint(cond.get_element())
    cond2 = OSC.OffroadCondition(20)
    cond3 = OSC.OffroadCondition(23)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.OffroadCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )


def test_timeheadwaycondition():
    cond = OSC.TimeHeadwayCondition("Ego", 20, OSC.Rule.equalTo, True, False)
    prettyprint(cond.get_element())
    cond2 = OSC.TimeHeadwayCondition("Ego", 20, OSC.Rule.equalTo, True, False)
    cond3 = OSC.TimeHeadwayCondition(
        "Ego",
        20,
        OSC.Rule.equalTo,
        True,
        True,
        routing_algorithm=OSC.RoutingAlgorithm.assignedRoute,
    )
    assert cond == cond2
    assert cond != cond3
    prettyprint(cond3.get_element())
    cond4 = OSC.TimeHeadwayCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )

    assert (
        version_validation("EntityCondition", cond3, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond3, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond3, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.TimeHeadwayCondition(
            "Ego",
            20,
            "dummy",
            True,
            True,
            routing_algorithm=OSC.RoutingAlgorithm.assignedRoute,
        )
    with pytest.raises(ValueError):
        OSC.TimeHeadwayCondition(
            "Ego",
            20,
            OSC.Rule.equalTo,
            True,
            True,
            routing_algorithm="dummy",
        )


def test_timetocollisioncondition():
    cond = OSC.TimeToCollisionCondition(
        value=20, alongroute=True, rule=OSC.Rule.equalTo, entity="Ego"
    )
    prettyprint(cond.get_element(), None)
    cond2 = OSC.TimeToCollisionCondition(
        value=20, alongroute=True, rule=OSC.Rule.equalTo, entity="Ego"
    )
    cond3 = OSC.TimeToCollisionCondition(
        value=20,
        alongroute=True,
        rule=OSC.Rule.equalTo,
        position=OSC.WorldPosition(),
        routing_algorithm=OSC.RoutingAlgorithm.assignedRoute,
    )
    prettyprint(cond3.get_element(), None)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.TimeToCollisionCondition.parse(cond.get_element())
    assert cond4 == cond
    cond5 = OSC.TimeToCollisionCondition.parse(cond3.get_element())
    assert cond5 == cond3

    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )

    assert (
        version_validation("EntityCondition", cond3, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond3, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond3, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.TimeToCollisionCondition(
            value=20,
            alongroute=True,
            rule="dummy",
            position=OSC.WorldPosition(),
            routing_algorithm=OSC.RoutingAlgorithm.assignedRoute,
        )
    with pytest.raises(TypeError):
        OSC.TimeToCollisionCondition(
            value=20,
            alongroute=True,
            rule=OSC.Rule.equalTo,
            position="dummy",
            routing_algorithm=OSC.RoutingAlgorithm.assignedRoute,
        )
    with pytest.raises(ValueError):
        OSC.TimeToCollisionCondition(
            value=20,
            alongroute=True,
            rule=OSC.Rule.equalTo,
            position=OSC.WorldPosition(),
            routing_algorithm="dummy",
        )


def test_accelerationcondition():
    cond = OSC.AccelerationCondition(1, OSC.Rule.greaterThan)
    prettyprint(cond.get_element())
    cond2 = OSC.AccelerationCondition(1, OSC.Rule.greaterThan)
    cond3 = OSC.AccelerationCondition(1, OSC.Rule.lessThan)
    assert cond == cond2
    assert cond != cond3
    cond4 = OSC.AccelerationCondition.parse(cond.get_element())
    assert cond == cond4
    cond5 = OSC.AccelerationCondition(
        1, OSC.Rule.lessThan, OSC.DirectionalDimension.longitudinal
    )
    cond6 = OSC.AccelerationCondition(
        1, OSC.Rule.lessThan, OSC.DirectionalDimension.lateral
    )
    prettyprint(cond5.get_element())
    cond7 = OSC.AccelerationCondition.parse(cond5.get_element())
    assert cond5 != cond6
    assert cond5 == cond7

    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )

    assert (
        version_validation("EntityCondition", cond5, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond5, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond5, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.AccelerationCondition(
            1, "dummy", OSC.DirectionalDimension.longitudinal
        )
    with pytest.raises(ValueError):
        OSC.AccelerationCondition(1, OSC.Rule.lessThan, "dummy")


def test_standstillcondition():
    cond = OSC.StandStillCondition(1)
    prettyprint(cond.get_element())
    cond2 = OSC.StandStillCondition(1)
    cond3 = OSC.StandStillCondition(3)
    assert cond == cond2
    assert cond != cond3
    cond4 = OSC.StandStillCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )


def test_speedcondition():
    cond = OSC.SpeedCondition(
        1, OSC.Rule.lessThan, OSC.DirectionalDimension.lateral
    )
    prettyprint(cond.get_element())
    cond2 = OSC.SpeedCondition(
        1, OSC.Rule.lessThan, OSC.DirectionalDimension.lateral
    )
    cond3 = OSC.SpeedCondition(2, OSC.Rule.lessThan)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.SpeedCondition.parse(cond.get_element())
    assert cond == cond4

    assert (
        version_validation("EntityCondition", cond, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )

    assert (
        version_validation("EntityCondition", cond3, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond3, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond3, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.SpeedCondition(1, "dummy", OSC.DirectionalDimension.lateral)
    with pytest.raises(ValueError):
        OSC.SpeedCondition(1, OSC.Rule.lessThan, "dummy")


def test_relativespeedcondition():
    cond = OSC.RelativeSpeedCondition(
        1, OSC.Rule.lessThan, "Ego", OSC.DirectionalDimension.lateral
    )
    prettyprint(cond.get_element())
    cond2 = OSC.RelativeSpeedCondition(
        1, OSC.Rule.lessThan, "Ego", OSC.DirectionalDimension.lateral
    )
    cond3 = OSC.RelativeSpeedCondition(1, OSC.Rule.lessThan, "Ego2")
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.RelativeSpeedCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("EntityCondition", cond, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )

    assert (
        version_validation("EntityCondition", cond3, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond3, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond3, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.RelativeSpeedCondition(1, OSC.Rule.lessThan, "Ego", "dummy")
    with pytest.raises(ValueError):
        OSC.RelativeSpeedCondition(
            1, "dummy", "Ego", OSC.DirectionalDimension.lateral
        )


def test_traveleddistancecondition():
    cond = OSC.TraveledDistanceCondition(1)
    prettyprint(cond.get_element())
    cond2 = OSC.TraveledDistanceCondition(1)
    cond3 = OSC.TraveledDistanceCondition(3)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.TraveledDistanceCondition.parse(cond.get_element())
    assert cond == cond4

    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )


def test_reachpositioncondition():
    OSC.enumerations.VersionBase().setVersion(minor=1)
    cond = OSC.ReachPositionCondition(OSC.WorldPosition(), 0.01)
    prettyprint(cond.get_element())
    cond2 = OSC.ReachPositionCondition(OSC.WorldPosition(), 0.01)
    cond3 = OSC.ReachPositionCondition(OSC.WorldPosition(), 0.02)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.ReachPositionCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("EntityCondition", cond, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond, 1) == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        OSC.ReachPositionCondition("dummy", 1)


def test_distancecondition():
    cond = OSC.DistanceCondition(
        1,
        OSC.Rule.lessThan,
        OSC.WorldPosition(),
        True,
        False,
        routing_algorithm=OSC.RoutingAlgorithm.fastest,
    )
    prettyprint(cond.get_element())
    cond2 = OSC.DistanceCondition(
        1,
        OSC.Rule.lessThan,
        OSC.WorldPosition(),
        True,
        False,
        routing_algorithm=OSC.RoutingAlgorithm.fastest,
    )
    cond3 = OSC.DistanceCondition(
        1, OSC.Rule.greaterThan, OSC.WorldPosition(), True, False
    )
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.DistanceCondition.parse(cond.get_element())
    assert cond == cond4

    assert (
        version_validation("EntityCondition", cond, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )

    assert (
        version_validation("EntityCondition", cond3, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond3, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond3, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.DistanceCondition(
            1,
            "dummy",
            OSC.WorldPosition(),
            True,
            False,
            routing_algorithm=OSC.RoutingAlgorithm.fastest,
        )
    with pytest.raises(TypeError):
        OSC.DistanceCondition(
            1,
            OSC.Rule.lessThan,
            "dummy",
            True,
            False,
            routing_algorithm=OSC.RoutingAlgorithm.fastest,
        )
    with pytest.raises(ValueError):
        OSC.DistanceCondition(
            1,
            OSC.Rule.lessThan,
            OSC.WorldPosition(),
            True,
            False,
            routing_algorithm="dummy",
        )


def test_relativedistancecondition():
    cond = OSC.RelativeDistanceCondition(
        1,
        OSC.Rule.equalTo,
        OSC.RelativeDistanceType.longitudinal,
        "Ego",
        True,
        False,
        routing_algorithm=OSC.RoutingAlgorithm.fastest,
        coordinate_system=OSC.CoordinateSystem.trajectory,
    )
    prettyprint(cond.get_element())
    cond2 = OSC.RelativeDistanceCondition(
        1,
        OSC.Rule.equalTo,
        OSC.RelativeDistanceType.longitudinal,
        "Ego",
        True,
        False,
        routing_algorithm=OSC.RoutingAlgorithm.fastest,
        coordinate_system=OSC.CoordinateSystem.trajectory,
    )
    cond3 = OSC.RelativeDistanceCondition(
        1,
        OSC.Rule.equalTo,
        OSC.RelativeDistanceType.longitudinal,
        "Ego",
        True,
        True,
    )
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.RelativeDistanceCondition.parse(cond.get_element())
    assert cond == cond4

    assert (
        version_validation("EntityCondition", cond, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )

    assert (
        version_validation("EntityCondition", cond3, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond3, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("EntityCondition", cond3, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.RelativeDistanceCondition(
            1,
            "dummy",
            OSC.RelativeDistanceType.longitudinal,
            "Ego",
            True,
            False,
            routing_algorithm=OSC.RoutingAlgorithm.fastest,
        )
    with pytest.raises(ValueError):
        OSC.RelativeDistanceCondition(
            1,
            OSC.Rule.equalTo,
            "dummy",
            "Ego",
            True,
            False,
            routing_algorithm=OSC.RoutingAlgorithm.fastest,
        )
    with pytest.raises(ValueError):
        OSC.RelativeDistanceCondition(
            1,
            OSC.Rule.equalTo,
            OSC.RelativeDistanceType.longitudinal,
            "Ego",
            True,
            False,
            routing_algorithm="dummy",
        )


def test_parametercondition():
    cond = OSC.ParameterCondition("MyParam", 1, OSC.Rule.equalTo)
    cond.setVersion(minor=1)
    prettyprint(cond.get_element())
    cond2 = OSC.ParameterCondition("MyParam", 1, OSC.Rule.equalTo)
    cond3 = OSC.ParameterCondition("MyParam", 1, OSC.Rule.lessThan)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.ParameterCondition.parse(cond.get_element())
    assert cond == cond4

    assert (
        version_validation("ParameterCondition", cond, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("ParameterCondition", cond, 1)
        == ValidationResponse.OK
    )
    ## Here a OSC_VERSION should be added
    assert (
        version_validation("ParameterCondition", cond, 2)
        == ValidationResponse.OK
    )

    with pytest.raises(ValueError):
        OSC.ParameterCondition("asdf", 1, "dummy")


def test_variablecondition():
    cond = OSC.VariableCondition("MyParam", 1, OSC.Rule.equalTo)
    prettyprint(cond.get_element())
    cond2 = OSC.VariableCondition("MyParam", 1, OSC.Rule.equalTo)
    cond3 = OSC.VariableCondition("MyParam", 1, OSC.Rule.lessThan)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.VariableCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("VariableCondition", cond, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("VariableCondition", cond, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("VariableCondition", cond, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.VariableCondition("asdf", 1, "dummy")


def test_timeofdaycondition():
    cond = OSC.TimeOfDayCondition(OSC.Rule.equalTo, 2023, 3, 9, 12, 20, 32)
    prettyprint(cond.get_element())
    cond2 = OSC.TimeOfDayCondition(OSC.Rule.equalTo, 2023, 3, 9, 12, 20, 32)
    cond3 = OSC.TimeOfDayCondition(OSC.Rule.equalTo, 2023, 3, 9, 12, 20, 33)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.TimeOfDayCondition.parse(cond.get_element())
    assert cond == cond4

    assert (
        version_validation("TimeOfDayCondition", cond, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TimeOfDayCondition", cond, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TimeOfDayCondition", cond, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.TimeOfDayCondition("dummy", 2023, 3, 9, 12, 20, 32)


def test_simulationtimecondition():
    cond = OSC.SimulationTimeCondition(1.2, OSC.Rule.greaterThan)
    prettyprint(cond.get_element())
    cond2 = OSC.SimulationTimeCondition(1.2, OSC.Rule.greaterThan)
    cond3 = OSC.SimulationTimeCondition(1.3, OSC.Rule.greaterThan)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.SimulationTimeCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("SimulationTimeCondition", cond, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("SimulationTimeCondition", cond, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("SimulationTimeCondition", cond, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.SimulationTimeCondition(1.3, "dummy")


def test_storyboardelementstatecondition():
    cond = OSC.StoryboardElementStateCondition(
        OSC.StoryboardElementType.action,
        "hej",
        OSC.StoryboardElementState.endTransition,
    )
    cond2 = OSC.StoryboardElementStateCondition(
        OSC.StoryboardElementType.action,
        "hej",
        OSC.StoryboardElementState.endTransition,
    )
    cond3 = OSC.StoryboardElementStateCondition(
        OSC.StoryboardElementType.action,
        "hej",
        OSC.StoryboardElementState.startTransition,
    )
    prettyprint(cond.get_element())
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.StoryboardElementStateCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("StoryboardElementStateCondition", cond, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("StoryboardElementStateCondition", cond, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("StoryboardElementStateCondition", cond, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.StoryboardElementStateCondition(
            "dummy", "hej", OSC.StoryboardElementState.endTransition
        )
    with pytest.raises(ValueError):
        OSC.StoryboardElementStateCondition(
            OSC.StoryboardElementType.action, "hej", "dummy"
        )


def test_userdefinedcondition():
    cond = OSC.UserDefinedValueCondition("mytrigger", 10, OSC.Rule.equalTo)
    prettyprint(cond.get_element())
    cond2 = OSC.UserDefinedValueCondition("mytrigger", 10, OSC.Rule.equalTo)
    cond3 = OSC.UserDefinedValueCondition("mytrigger", 12, OSC.Rule.equalTo)
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.UserDefinedValueCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("UserDefinedValueCondition", cond, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("UserDefinedValueCondition", cond, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("UserDefinedValueCondition", cond, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.UserDefinedValueCondition("mytrigger", 10, "dummy")


def test_trafficsignalcondition():
    cond = OSC.TrafficSignalCondition("traflight", "green")
    prettyprint(cond.get_element())
    cond2 = OSC.TrafficSignalCondition("traflight", "green")
    cond3 = OSC.TrafficSignalCondition("traflight", "red")
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.TrafficSignalCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("TrafficSignalCondition", cond, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TrafficSignalCondition", cond, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TrafficSignalCondition", cond, 2)
        == ValidationResponse.OK
    )


def test_relaticeclearancecondition():
    cond = OSC.RelativeClearanceCondition(True, -1, 3)
    cond.add_entity("ego")
    cond.add_relative_lane_range(1, 2)
    prettyprint(cond.get_element())

    cond2 = OSC.RelativeClearanceCondition(True, -1, 3)
    cond2.add_entity("ego")
    cond2.add_relative_lane_range(1, 2)

    cond3 = OSC.RelativeClearanceCondition(True, -1, 3)
    cond3.add_entity("ego")
    cond3.add_entity("target")
    cond3.add_relative_lane_range(1, 2)
    cond3.add_relative_lane_range(5, 6)
    prettyprint(cond3.get_element())

    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.RelativeClearanceCondition.parse(cond.get_element())
    assert cond == cond4

    cond5 = OSC.RelativeClearanceCondition.parse(cond3.get_element())
    prettyprint(cond5.get_element())
    assert cond3 == cond5
    assert (
        version_validation("EntityCondition", cond, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("EntityCondition", cond, 2) == ValidationResponse.OK
    )


def test_trafficsignalconditioncontroller():
    cond = OSC.TrafficSignalControllerCondition("somereferens", "yellow")
    prettyprint(cond.get_element())
    cond2 = OSC.TrafficSignalControllerCondition("somereferens", "yellow")
    cond3 = OSC.TrafficSignalControllerCondition("somereferens", "green")
    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.TrafficSignalControllerCondition.parse(cond.get_element())
    assert cond == cond4
    assert (
        version_validation("TrafficSignalControllerCondition", cond, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TrafficSignalControllerCondition", cond, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TrafficSignalControllerCondition", cond, 2)
        == ValidationResponse.OK
    )


def test_triggeringentities():
    cond = OSC.TriggeringEntities(OSC.TriggeringEntitiesRule.all)
    cond.add_entity("ego")
    prettyprint(cond.get_element())
    cond2 = OSC.TriggeringEntities(OSC.TriggeringEntitiesRule.all)
    cond2.add_entity("ego")
    cond3 = OSC.TriggeringEntities(OSC.TriggeringEntitiesRule.all)
    cond3.add_entity("ego")
    cond3.add_entity("target")

    assert cond == cond2
    assert cond != cond3

    cond4 = OSC.TriggeringEntities.parse(cond.get_element())
    assert cond == cond4
    cond5 = OSC.TriggeringEntities.parse(cond3.get_element())
    assert cond5 == cond3
    assert (
        version_validation("TriggeringEntities", cond, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TriggeringEntities", cond, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TriggeringEntities", cond, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.TriggeringEntities("dummy")


def test_entitytrigger():
    trigcond = OSC.TimeToCollisionCondition(
        10,
        OSC.Rule.equalTo,
        True,
        freespace=False,
        position=OSC.WorldPosition(),
    )
    trigger = OSC.EntityTrigger(
        "mytesttrigger", 0.2, OSC.ConditionEdge.rising, trigcond, "Target_1"
    )
    prettyprint(trigger.get_element())
    trigger2 = OSC.EntityTrigger(
        "mytesttrigger", 0.2, OSC.ConditionEdge.rising, trigcond, "Target_1"
    )
    trigger3 = OSC.EntityTrigger(
        "mytesttrigger", 0.3, OSC.ConditionEdge.rising, trigcond, "Target_1"
    )

    assert trigger == trigger2
    assert trigger != trigger3

    trigger._set_used_by_parent()
    trigger4 = OSC.EntityTrigger.parse(trigger.get_element())
    assert trigger4 == trigger2
    assert version_validation("Trigger", trigger2, 0) == ValidationResponse.OK
    assert version_validation("Trigger", trigger2, 1) == ValidationResponse.OK
    assert version_validation("Trigger", trigger2, 2) == ValidationResponse.OK
    with pytest.raises(ValueError):
        OSC.EntityTrigger("mytesttrigger", 0.2, "dummy", trigcond, "Target_1")
    with pytest.raises(TypeError):
        OSC.EntityTrigger(
            "mytesttrigger",
            0.3,
            OSC.ConditionEdge.rising,
            OSC.SimulationTimeCondition(2, OSC.Rule.equalTo),
            "Target_1",
        )


def test_valuetrigger():
    trigcond = OSC.ParameterCondition("something", 2, OSC.Rule.equalTo)
    trigger = OSC.ValueTrigger(
        "myvaluetrigger",
        0.2,
        OSC.ConditionEdge.rising,
        trigcond,
        triggeringpoint="start",
    )
    prettyprint(trigger.get_element())
    trigger2 = OSC.ValueTrigger(
        "myvaluetrigger",
        0.2,
        OSC.ConditionEdge.rising,
        trigcond,
        triggeringpoint="start",
    )
    trigger3 = OSC.ValueTrigger(
        "myvaluetrigger",
        0.3,
        OSC.ConditionEdge.rising,
        trigcond,
        triggeringpoint="stop",
    )
    assert trigger == trigger2
    assert trigger != trigger3

    trigger._set_used_by_parent()
    trigger4 = OSC.ValueTrigger.parse(trigger.get_element())
    prettyprint(trigger2, None)
    prettyprint(trigger4, None)
    assert trigger2 == trigger4
    assert version_validation("Trigger", trigger2, 0) == ValidationResponse.OK
    assert version_validation("Trigger", trigger2, 1) == ValidationResponse.OK
    assert version_validation("Trigger", trigger2, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.ValueTrigger(
            "myvaluetrigger",
            0.3,
            "dummy",
            trigcond,
            triggeringpoint="stop",
        )
    with pytest.raises(TypeError):
        OSC.ValueTrigger(
            "myvaluetrigger",
            0.3,
            OSC.ConditionEdge.rising,
            OSC.SpeedCondition(1, OSC.Rule.equalTo),
            triggeringpoint="stop",
        )


def test_conditiongroup():
    condgr = OSC.ConditionGroup()

    trig1 = OSC.EntityTrigger(
        "firsttrigger",
        1,
        OSC.ConditionEdge.rising,
        OSC.RelativeDistanceCondition(
            10,
            OSC.Rule.greaterThan,
            OSC.RelativeDistanceType.longitudinal,
            "Ego",
        ),
        "Target",
    )
    trig2 = OSC.EntityTrigger(
        "secondtrigger",
        2,
        OSC.ConditionEdge.rising,
        OSC.SpeedCondition(2, OSC.Rule.equalTo),
        "Target",
    )
    condgr.add_condition(trig1)
    condgr.add_condition(trig2)

    prettyprint(condgr.get_element())

    condgr2 = OSC.ConditionGroup()
    condgr3 = OSC.ConditionGroup()
    condgr2.add_condition(trig1)
    condgr2.add_condition(trig2)
    condgr3.add_condition(trig2)
    assert condgr == condgr2
    assert condgr != condgr3

    condgr._set_used_by_parent()
    condgr4 = OSC.ConditionGroup.parse(condgr.get_element())
    assert condgr4 == condgr2
    assert version_validation("Trigger", condgr2, 0) == ValidationResponse.OK
    assert version_validation("Trigger", condgr2, 1) == ValidationResponse.OK
    assert version_validation("Trigger", condgr2, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        condgr.add_condition("dummy")


def test_trigger():

    trig = OSC.Trigger("stop")
    condgr = OSC.ConditionGroup()

    trig1 = OSC.EntityTrigger(
        "firsttrigger",
        1,
        OSC.ConditionEdge.rising,
        OSC.RelativeDistanceCondition(
            10,
            OSC.Rule.greaterThan,
            OSC.RelativeDistanceType.longitudinal,
            "Ego",
        ),
        "Target",
    )
    trig2 = OSC.EntityTrigger(
        "secondtrigger",
        2,
        OSC.ConditionEdge.rising,
        OSC.SpeedCondition(2, OSC.Rule.equalTo),
        "Target",
    )

    condgr.add_condition(trig1)
    trig.add_conditiongroup(condgr)
    condgr.add_condition(trig2)

    condgr2 = OSC.ConditionGroup()

    trig3 = OSC.EntityTrigger(
        "thirdtrigger",
        1,
        OSC.ConditionEdge.rising,
        OSC.RelativeDistanceCondition(
            10,
            OSC.Rule.greaterThan,
            OSC.RelativeDistanceType.longitudinal,
            "Ego",
        ),
        "Target",
    )
    trig4 = OSC.EntityTrigger(
        "forthtrigger",
        2,
        OSC.ConditionEdge.rising,
        OSC.SpeedCondition(2, OSC.Rule.equalTo),
        "Target",
    )

    condgr2.add_condition(trig3)
    condgr2.add_condition(trig4)

    condgr3 = deepcopy(condgr2)
    trig.add_conditiongroup(condgr2)
    prettyprint(trig.get_element())

    trig2 = OSC.Trigger("stop")
    trig3 = OSC.Trigger()
    trig2.add_conditiongroup(condgr)
    trig2.add_conditiongroup(condgr2)
    trig3.add_conditiongroup(condgr3)

    assert trig == trig2
    assert trig != trig3

    trig4 = OSC.Trigger.parse(trig.get_element())
    assert trig4 == trig
    assert version_validation("Trigger", trig, 0) == ValidationResponse.OK
    assert version_validation("Trigger", trig, 1) == ValidationResponse.OK
    assert version_validation("Trigger", trig, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        trig.add_conditiongroup("dummy")


@pytest.mark.parametrize(
    "valuetrigger",
    [
        OSC.ParameterCondition("asdf", 1, OSC.Rule.greaterOrEqual),
        OSC.VariableCondition("asdf", 1, OSC.Rule.greaterOrEqual),
        OSC.TimeOfDayCondition(OSC.Rule.greaterOrEqual, 2023, 4, 5, 6, 4, 8),
        OSC.SimulationTimeCondition(2, OSC.Rule.greaterOrEqual),
        OSC.StoryboardElementStateCondition(
            OSC.StoryboardElementType.action,
            "my action",
            OSC.StoryboardElementState.endTransition,
        ),
        OSC.UserDefinedValueCondition("myvalue", 2, OSC.Rule.greaterOrEqual),
        OSC.TrafficSignalCondition("stuffs", "red"),
        OSC.TrafficSignalControllerCondition("my signal", "myphase"),
    ],
)
def test_value_condition_factory(valuetrigger):
    element = ET.Element("ByValueCondition")
    element.append(valuetrigger.get_element())
    factoryoutput = OSC.triggers._ValueConditionFactory.parse_value_condition(
        element
    )
    prettyprint(valuetrigger, None)
    prettyprint(factoryoutput, None)
    assert valuetrigger == factoryoutput


@pytest.mark.parametrize("osc_version", [1, 2])
@pytest.mark.parametrize(
    "entitytrigger",
    [
        OSC.EndOfRoadCondition(2),
        OSC.CollisionCondition("hej"),
        OSC.OffroadCondition(3),
        OSC.TimeHeadwayCondition("my entity", 2, OSC.Rule.greaterOrEqual),
        OSC.TimeToCollisionCondition(
            1, OSC.Rule.greaterOrEqual, entity="target"
        ),
        OSC.AccelerationCondition(2, OSC.Rule.greaterOrEqual),
        OSC.StandStillCondition(5),
        OSC.SpeedCondition(15, OSC.Rule.greaterOrEqual),
        OSC.RelativeSpeedCondition(1, OSC.Rule.greaterOrEqual, "target"),
        OSC.TraveledDistanceCondition(59),
        OSC.ReachPositionCondition(OSC.WorldPosition(), 4),
        OSC.DistanceCondition(4, OSC.Rule.greaterOrEqual, OSC.WorldPosition()),
        OSC.RelativeDistanceCondition(
            2,
            OSC.Rule.greaterOrEqual,
            OSC.RelativeDistanceType.lateral,
            "target",
        ),
    ],
)
def test_entity_condition_factory(osc_version, entitytrigger):
    OSC.enumerations.VersionBase().setVersion(minor=osc_version)

    # Skip ReachPositionCondition for OSC version 2
    if osc_version == 2 and isinstance(
        entitytrigger, OSC.ReachPositionCondition
    ):
        return
    # element = ET.Element('ByEntityCondition')
    # element.append(entitytrigger.get_element())
    factoryoutput = (
        OSC.triggers._EntityConditionFactory.parse_entity_condition(
            entitytrigger.get_element()
        )
    )
    prettyprint(entitytrigger, None)
    prettyprint(factoryoutput, None)
    assert entitytrigger == factoryoutput


def test_equalities_trigger_vs_conditiongroup_vs_entity():
    enttrigcond = OSC.TimeToCollisionCondition(
        10,
        OSC.Rule.equalTo,
        True,
        freespace=False,
        position=OSC.WorldPosition(),
    )
    enttrigger = OSC.EntityTrigger(
        "mytesttrigger", 0.2, OSC.ConditionEdge.rising, enttrigcond, "Target_1"
    )
    enttrigger2 = OSC.EntityTrigger(
        "mytesttrigger", 0.2, OSC.ConditionEdge.rising, enttrigcond, "Target_1"
    )
    condgr = OSC.ConditionGroup()
    condgr.add_condition(enttrigger)
    condgr2 = OSC.ConditionGroup()
    condgr2.add_condition(enttrigger)

    trigger = OSC.Trigger()
    trigger.add_conditiongroup(condgr)
    assert condgr == trigger
    assert trigger == condgr
    assert condgr == enttrigger
    assert enttrigger == condgr
    assert trigger == enttrigger
    assert enttrigger == trigger

    parsed_valtrigger = OSC.Trigger.parse(enttrigger2.get_element())

    assert parsed_valtrigger == trigger
    parsed_condgr = OSC.Trigger.parse(condgr2.get_element())

    assert parsed_condgr == trigger


def test_equalities_trigger_vs_conditiongroup_vs_value():
    trigcond = OSC.ParameterCondition("something", 2, OSC.Rule.equalTo)

    valtrigger = OSC.ValueTrigger(
        "myvaluetrigger",
        0.2,
        OSC.ConditionEdge.rising,
        trigcond,
        triggeringpoint="stop",
    )

    valtrigger2 = OSC.ValueTrigger(
        "myvaluetrigger",
        0.2,
        OSC.ConditionEdge.rising,
        trigcond,
        triggeringpoint="stop",
    )
    condgr = OSC.ConditionGroup("stop")
    condgr.add_condition(valtrigger)

    condgr2 = OSC.ConditionGroup("stop")
    condgr2.add_condition(valtrigger)

    trigger = OSC.Trigger("stop")
    trigger.add_conditiongroup(condgr)
    assert condgr == trigger
    assert trigger == condgr
    assert condgr == valtrigger
    assert valtrigger == condgr
    assert trigger == valtrigger
    assert valtrigger == trigger

    parsed_valtrigger = OSC.Trigger.parse(valtrigger2.get_element())

    assert parsed_valtrigger == trigger
    parsed_condgr = OSC.Trigger.parse(condgr2.get_element())

    assert parsed_condgr == trigger
