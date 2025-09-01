import importlib
import os
import sys

import pytest
import xmlschema
import xml.etree.ElementTree as ET

from scenariogeneration import xosc

OSC_FILES = {
    0: [
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
    1: [
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
    2: [
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
        "variable_usage",
    ],
    3: [
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
        "variable_usage",
        "angle_condition_trigger",
        "clothoid_spline_shape_trajectory",
        "trailer_example",
    ],
}


@pytest.fixture(scope="session", name="test_folder")
def create_test_files(tmp_path_factory):
    """Uncomment the line below to generate files that will be used for
    regression tests. Then the files will be compared between two versions
    of scenariogeneration. Can be used as robustness tests
    """
    regression_test_folder = None
    # regression_test_folder = Path("regression_files")

    sys.path.insert(
        1,
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "examples", "xosc"
        ),
    )
    sys.path.insert(
        1,
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "examples", "xodr"
        ),
    )

    def generate_files(test_folder):
        for version, files in OSC_FILES.items():
            version_dir = test_folder / f"osc_version_{version}"
            version_dir.mkdir(exist_ok=True)
            for file_name in files:
                try:
                    imp = importlib.import_module(file_name)
                    sce = imp.Scenario()
                    sce.open_scenario_version = version
                    xosc, _ = sce.generate(version_dir)
                except Exception as e:
                    print(
                        f"Error generating {file_name} for version {version}: {e}"
                    )

    if regression_test_folder is None:
        regression_test_folder = tmp_path_factory.mktemp("test_dir")
        generate_files(regression_test_folder)
        use_as_regression = False
    else:
        if not regression_test_folder.exists():
            regression_test_folder.mkdir()
            generate_files(regression_test_folder)
        use_as_regression = True

    return regression_test_folder.absolute(), use_as_regression


params = []
ids = []
for version, files in OSC_FILES.items():
    for file_name in files:
        params.append((file_name, version))
        ids.append(f"{file_name}_v{version}")


@pytest.mark.parametrize("params", params, ids=ids)
def test_xosc_schema_validation(params, test_folder):
    sys.path.insert(
        1,
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "examples", "xosc"
        ),
    )
    python_file, version = params[0], params[1]

    xosc_file = (
        test_folder[0]
        / f"osc_version_{version}"
        / "xosc"
        / f"{python_file}0.xosc"
    )

    with open(xosc_file, "r", encoding="utf-8") as f:
        loaded_xosc = ET.parse(f)
    scenario = xosc.validate_schema(loaded_xosc)
    assert scenario is True


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
        1,
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "examples", "xodr"
        ),
    )
    validator = xmlschema.XMLSchema(
        os.path.join(
            os.path.split(__file__)[0],
            os.pardir,
            "schemas",
            "opendrive_17_core.xsd",
        )
    )
    imp = importlib.import_module(python_file)
    sce = imp.Scenario()

    _, xodr = sce.generate(tmpdir, write_relative_road_path=False)
    validator.validate(xodr[0])
