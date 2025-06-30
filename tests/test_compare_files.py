"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import importlib
import os
import sys
from pathlib import Path

import pytest
from lxml import etree

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
}

ODR_FILES = [
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
]


@pytest.fixture(scope="session", name="test_folder")
def test_create_test_files(tmp_path_factory):

    regression_test_folder = None
    """ Uncomment the line below to generate files that will be used for
    regression tests. Then the files will be compared between two versions
    of scenariogeneration. Can be used as robustness tests
    """
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
        for version in range(3):
            tmpdir = test_folder / f"osc_version_{version}"
            tmpdir.mkdir()
            for f in OSC_FILES[version]:
                imp = importlib.import_module(f)
                sce = imp.Scenario()
                sce.open_scenario_version = version
                xosc, _ = sce.generate(tmpdir)

        tmpdir = test_folder / "roads"
        for f in ODR_FILES:
            imp = importlib.import_module(f)
            sce = imp.Scenario()
            sce.generate(tmpdir)

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


@pytest.mark.parametrize("python_file", OSC_FILES[0])
def test_OSC_1_0_parsing(python_file, test_folder):
    sys.path.insert(
        1,
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "examples", "xosc"
        ),
    )

    xosc_file = (
        test_folder[0] / f"osc_version_0" / "xosc" / f"{python_file}0.xosc"
    )
    old_osc = xosc.ParseOpenScenario(xosc_file)
    assert old_osc.version_minor == 0
    imp = importlib.import_module(python_file)
    scegenerator = imp.Scenario()

    sce = scegenerator.scenario()
    sce.setVersion(minor=0)

    assert sce == old_osc


@pytest.mark.parametrize("python_file", OSC_FILES[1])
def test_OSC_1_1_parsing(python_file, test_folder):
    sys.path.insert(
        1,
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "examples", "xosc"
        ),
    )

    xosc_file = (
        test_folder[0] / f"osc_version_1" / "xosc" / f"{python_file}0.xosc"
    )
    old_osc = xosc.ParseOpenScenario(xosc_file)
    assert old_osc.version_minor == 1
    imp = importlib.import_module(python_file)
    scegenerator = imp.Scenario()

    sce = scegenerator.scenario()
    sce.setVersion(minor=1)

    assert sce == old_osc


@pytest.mark.parametrize("python_file", OSC_FILES[2])
def test_OSC_1_2_parsing(python_file, test_folder):
    sys.path.insert(
        1,
        os.path.join(
            os.path.split(__file__)[0], os.pardir, "examples", "xosc"
        ),
    )

    xosc_file = (
        test_folder[0] / f"osc_version_2" / "xosc" / f"{python_file}0.xosc"
    )
    old_osc = xosc.ParseOpenScenario(xosc_file)
    assert old_osc.version_minor == 2
    imp = importlib.import_module(python_file)
    scegenerator = imp.Scenario()

    sce = scegenerator.scenario()
    sce.setVersion(minor=2)

    assert sce == old_osc


@pytest.mark.parametrize("python_file", ODR_FILES)
def test_ODR(python_file, test_folder, tmpdir):
    if not test_folder[1]:
        return  # since scenariogeneration is not parsing xodr files (yet)

    imp = importlib.import_module(python_file)
    sce = imp.Scenario()
    # _, roadfile = sce.generate(tmpdir,write_relative_road_path=False)
    _, roadfile = sce.generate("dummy", write_relative_road_path=False)
    old_road_file = test_folder[0] / "roads" / "xodr" / f"{python_file}0.xodr"
    with open(old_road_file, "r", encoding="utf-8") as f:
        old_xodr = etree.parse(f)

    with open(roadfile[0], "r", encoding="utf-8") as f:
        new_xodr = etree.parse(f)

    # creation date is different, so remove it
    # old_xodr.find('')
    old_xodr.find("header").attrib["date"] = ""
    new_xodr.find("header").attrib["date"] = ""
    assert etree.tostring(old_xodr) == etree.tostring(new_xodr)
