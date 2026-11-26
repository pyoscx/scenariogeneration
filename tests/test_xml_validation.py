import importlib
import os
import sys
from pathlib import Path

import pytest
import xmlschema
import xml.etree.ElementTree as ET

from scenariogeneration import xosc

from .xml_validator import schemas, xodr_schema


def test_trajectory_motion_speed_export(tmp_path, monkeypatch):
    from examples.xosc.trajectory_motion_speed import Scenario

    monkeypatch.setattr(xosc.VersionBase, "version_minor", 3)
    paths, _ = Scenario().generate(tmp_path)
    path = Path(paths[0])
    tree = ET.parse(path)
    assert tree.find("FileHeader").get("revMinor") == "4"
    assert xosc.validate_schema(tree)
    road_path = path.parent / tree.find("RoadNetwork/LogicFile").get(
        "filepath"
    )
    xodr_schema.validate(road_path)
    parsed = xosc.ParseOpenScenario(path).get_element()
    vertices = parsed.findall(".//Polyline/Vertex")
    assert [float(vertex.get("time")) for vertex in vertices] == [
        0,
        2,
        4,
        6,
        8,
    ]
    assert [vertex.find("Motion").attrib for vertex in vertices] == [
        {"speed_longitudinal": str(speed)}
        for speed in (4.0, 8.0, 12.0, 8.0, 4.0)
    ]


def test_roadworks_scenario_export(tmp_path, monkeypatch):
    from examples.xosc.roadworks_permanent_temporary_layers import Scenario

    monkeypatch.setattr(xosc.VersionBase, "version_minor", 3)
    paths, _ = Scenario().generate(tmp_path)
    path = Path(paths[0])
    tree = ET.parse(path)
    assert tree.find("FileHeader").get("revMinor") == "4"
    assert xosc.validate_schema(tree)
    road_path = path.parent / tree.find("RoadNetwork/LogicFile").get(
        "filepath"
    )
    xodr_schema.validate(road_path)
    parsed = xosc.ParseOpenScenario(path).get_element()
    car_position = parsed.find(".//Private[@entityRef='Car2']//LanePosition")
    assert car_position.get("layer") == "permanent"
    assert car_position.get("laneId") == "-3"
    target = parsed.find(".//AbsoluteTargetLane")
    assert target.attrib == {"value": "-1", "layer": "temporary"}
    assert (
        parsed.find("Storyboard/StopTrigger//SimulationTimeCondition").get(
            "value"
        )
        == "10.0"
    )


def test_openscenario_1_4_lane_actions(monkeypatch):
    monkeypatch.setattr(xosc.VersionBase, "version_minor", 3)
    dynamics = xosc.TransitionDynamics(
        xosc.DynamicsShapes.cubic, xosc.DynamicsDimension.time, 2
    )
    actions = [
        xosc.LanePosition(10, 0, -1, 1, layer="temporary"),
        xosc.AbsoluteLaneChangeAction(-1, dynamics, layer="$layer"),
        xosc.RelativeLaneChangeAction(1, "Car1", dynamics, layer="permanent"),
        xosc.PreferredLaneLayerAction(xosc.LaneLayerType.temporary),
    ]
    for action in actions:
        with pytest.raises(xosc.OpenSCENARIOVersionError, match="1.4"):
            action.get_element()
    xosc.VersionBase.version_minor = 4
    for action in actions:
        element = action.get_element()
        type_name = (
            "Position"
            if isinstance(action, xosc.LanePosition)
            else "PrivateAction"
        )
        schemas[4].create_element(element.tag, type=type_name).validate(
            element
        )
        assert action == type(action).parse(element)


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
        "roadworks_permanent_temporary_layers",
    ],
)
def test_ODR(tmpdir, python_file):
    sys.path.insert(
        1,
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "examples", "xodr"
        ),
    )
    imp = importlib.import_module(python_file)
    sce = imp.Scenario()

    _, xodr = sce.generate(tmpdir, write_relative_road_path=False)
    xodr_schema.validate(xodr[0])
    root = ET.parse(xodr[0]).getroot()
    assert root.find("header").get("revMinor") == "9"

    if python_file == "roadworks_permanent_temporary_layers":
        road = root.find("road")
        permanent = road.find("lanes[@layer='permanent']")
        temporary = road.find("lanes[@layer='temporary']")
        sections = temporary.findall("laneSection")
        assert [
            (float(section.get("s")), float(section.get("length")))
            for section in sections
        ] == [
            (40, 20),
            (60, 280),
            (340, 20),
        ]
        entrance_links = permanent.findall(
            "laneSection[1]/right/lane[@id='-3']/link/successor"
        )
        assert {
            (link.get("id"), link.get("layer")) for link in entrance_links
        } == {
            ("-3", "permanent"),
            ("-1", "temporary"),
        }
        assert sections[-1].find(
            "right/lane[@id='-1']/link/successor"
        ).attrib == {
            "id": "-3",
            "layer": "permanent",
        }
        assert (
            len(road.findall("objects/object[@temporary='true']/repeat")) == 2
        )
