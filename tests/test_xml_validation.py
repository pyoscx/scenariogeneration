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


@pytest.mark.parametrize(
    "python_file",
    [
        "common_junction_creator",
        "direct_junction_creator",
        "full_junction_with_LaneDef",
        "full_junction",
        "highway_bridge_example",
        "highway_example_with_merge_and_split",
        "highway_example",
        "highway_exit_with_lane_types",
        "junction_trippel_twoway",
        "junction_with_signals",
        "road_split",
        "road_split_w_lane_split",
        "lane_number_change_merge",
        "manual_add_of_geometries",
        "multiple_geometries_one_road_with_objects",
        "multiple_geometries_one_road",
        "road_link_unequal_number_of_lanes",
        "road_merge_w_lane_merge",
        "road_merge",
        "road_with_changing_lane_width",
        "road_with_custom_lanes",
        "road_with_custom_roadmarkers",
        "road_with_multiple_lane_widths",
        "simple_road_with_objects",
        "two_roads",
        "junction_with_varying_lane_widths",
        "road_with_lane_adjustment",
        "clothoid_generation",
        "adjustable_planview",
        "super_elevation_automation_example",
        "road_with_speed_signs",
    ],
)
def test_ODR(tmpdir, python_file):
    sys.path.insert(
        1, os.path.join(os.path.split(__file__)[0], os.pardir, "examples", "xodr")
    )
    validator = xmlschema.XMLSchema(
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "schemas", "opendrive_17_core.xsd"
        )
    )
    imp = importlib.import_module(python_file)
    sce = imp.Scenario()

    _, xodr = sce.generate(tmpdir, write_relative_road_path=False)
    validator.validate(xodr[0])
