import os
import sys
import importlib
import xmlschema

import pytest


@pytest.mark.parametrize(
    "python_file",
    [
        "Acceleration_condition",
        "end_of_road_reset_traffic",
        "multi_conditional_and_triggers",
        "multi_conditional_different_actions",
        "multi_conditional_or_triggers",
        "multiple_maneuvers",
        "one_action_example",
        "parallel_distance_actions",
        "route_in_crossing",
        "Speed_condition",
        "Stop_on_offroad",
        "trajectory_example",
        "withcontroller",
    ],
)
def test_OSC_1_0(tmpdir, python_file):
    sys.path.insert(
        1, os.path.join(os.path.split(__file__)[0], os.pardir, "examples", "xosc")
    )
    validator = xmlschema.XMLSchema(
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "schemas", "OpenSCENARIO_1_0.xsd"
        )
    )
    imp = importlib.import_module(python_file)
    sce = imp.Scenario()
    sce.open_scenario_version = 0
    xosc, _ = sce.generate(tmpdir)
    validator.validate(xosc[0])


@pytest.mark.parametrize(
    "python_file",
    [
        "Acceleration_condition",
        "end_of_road_reset_traffic",
        "multi_conditional_and_triggers",
        "multi_conditional_different_actions",
        "multi_conditional_or_triggers",
        "multiple_maneuvers",
        "one_action_example",
        "parallel_distance_actions",
        "route_in_crossing",
        "Speed_condition",
        "Stop_on_offroad",
        "syncronize_straight_example",
        "trajectory_example",
        "withcontroller",
    ],
)
def test_OSC_1_1(tmpdir, python_file):
    sys.path.insert(
        1, os.path.join(os.path.split(__file__)[0], os.pardir, "examples", "xosc")
    )
    validator = xmlschema.XMLSchema(
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "schemas", "OpenSCENARIO_1_1.xsd"
        )
    )
    imp = importlib.import_module(python_file)
    sce = imp.Scenario()
    sce.open_scenario_version = 1
    xosc, _ = sce.generate(tmpdir)
    validator.validate(xosc[0])


@pytest.mark.parametrize(
    "python_file",
    [
        "Acceleration_condition",
        "end_of_road_reset_traffic",
        "multi_conditional_and_triggers",
        "multi_conditional_different_actions",
        "multi_conditional_or_triggers",
        "multiple_maneuvers",
        "one_action_example",
        "parallel_distance_actions",
        "route_in_crossing",
        "Speed_condition",
        "speed_profile",
        "Stop_on_offroad",
        "syncronize_straight_example",
        "trajectory_example",
        "withcontroller",
    ],
)
def test_OSC_1_2(tmpdir, python_file):
    sys.path.insert(
        1, os.path.join(os.path.split(__file__)[0], os.pardir, "examples", "xosc")
    )
    validator = xmlschema.XMLSchema(
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "schemas", "OpenSCENARIO_1_2.xsd"
        )
    )
    imp = importlib.import_module(python_file)
    sce = imp.Scenario()
    sce.open_scenario_version = 2
    xosc, _ = sce.generate(tmpdir)
    validator.validate(xosc[0])
