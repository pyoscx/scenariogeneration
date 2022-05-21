"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import pytest
import os

from scenariogeneration import xosc
from scenariogeneration import prettyprint
from scenariogeneration import ScenarioGenerator


class writer_dummy:
    def write_xml(self, filename):
        with open(filename, "w") as f:
            pass


class ClassScenarioOnly(ScenarioGenerator):
    def __init__(self, parameters, naming):
        ScenarioGenerator.__init__(self)

        self.parameters = parameters
        self.naming = naming

    def scenario(self, **kwargs):
        return writer_dummy()


class ClassRoadOnly(ScenarioGenerator):
    def __init__(self, parameters, naming):
        ScenarioGenerator.__init__(self)

        self.parameters = parameters
        self.naming = naming

    def road(self, **kwargs):
        return writer_dummy()


class ClassBoth(ScenarioGenerator):
    def __init__(self, parameters, naming):
        ScenarioGenerator.__init__(self)

        self.parameters = parameters
        self.naming = naming

    def scenario(self, **kwargs):
        return writer_dummy()

    def road(self, **kwargs):
        return writer_dummy()


@pytest.fixture
def list_of_params():
    d1 = {}
    d1["road_curvature"] = 0.001
    d1["speed"] = 10
    d2 = {}
    d2["road_curvature"] = 0.002
    d2["speed"] = 20
    return [d1, d2]


@pytest.fixture
def dict_of_params():
    retdict = {}
    retdict["parameter1"] = [1, 2, 3]
    retdict["parameter2"] = [1, 2]
    return retdict


def test_list_of_params(list_of_params):

    sg = ScenarioGenerator()
    sg.parameters = list_of_params
    sg._handle_input_parameters()
    assert len(sg.all_permutations) == 2


def test_dict_paramss(dict_of_params):

    sg = ScenarioGenerator()
    sg.parameters = dict_of_params
    print(sg.parameters)
    sg._handle_input_parameters()
    assert len(sg.all_permutations) == 6


def test_numerical_naming(list_of_params):
    sg = ScenarioGenerator()
    sg.parameters = list_of_params
    sg.naming = "numerical"
    name = sg._get_scenario_name(sg.parameters[0])

    assert name == "scenario_generator0"
    name = sg._get_scenario_name(sg.parameters[1])
    assert name == "scenario_generator1"


def test_parameter_naming(list_of_params):
    sg = ScenarioGenerator()
    sg.parameters = list_of_params
    sg.naming = "parameter"
    name = sg._get_scenario_name(sg.parameters[0])

    assert name == "scenario_generator_road_curvature-0.001_speed-10"
    name = sg._get_scenario_name(sg.parameters[1])
    assert name == "scenario_generator_road_curvature-0.002_speed-20"


def test_folder_creation(tmpdir):
    sg = ScenarioGenerator()

    # test no folder existing
    nodir = os.path.join(tmpdir, "dir1")
    sg._create_folder_structure(nodir)

    assert "xodr" in os.listdir(nodir)
    assert "xosc" in os.listdir(nodir)

    # test path exist
    dir_exist = os.path.join(tmpdir, "dir2")
    os.mkdir(dir_exist)
    sg._create_folder_structure(dir_exist)
    assert "xodr" in os.listdir(dir_exist)
    assert "xosc" in os.listdir(dir_exist)

    # test folder exists and the xosc fodler
    xosc_dir_exist = os.path.join(tmpdir, "dir3")
    os.mkdir(xosc_dir_exist)
    os.mkdir(os.path.join(xosc_dir_exist, "xosc"))
    sg._create_folder_structure(xosc_dir_exist)
    assert "xodr" in os.listdir(xosc_dir_exist)
    assert "xosc" in os.listdir(xosc_dir_exist)

    # test folder exists and the xodr fodler
    xodr_dir_exist = os.path.join(tmpdir, "dir4")
    os.mkdir(xodr_dir_exist)
    os.mkdir(os.path.join(xodr_dir_exist, "xodr"))
    sg._create_folder_structure(xodr_dir_exist)
    assert "xodr" in os.listdir(xodr_dir_exist)
    assert "xosc" in os.listdir(xodr_dir_exist)


def test_generate_only_scenario(dict_of_params, tmpdir):
    sg = ClassScenarioOnly(dict_of_params, "numerical")
    sg.generate(tmpdir)
    scenarios = os.listdir(os.path.join(tmpdir, "xosc"))
    opendrives = os.listdir(os.path.join(tmpdir, "xodr"))
    assert len(scenarios) == 6
    assert len(opendrives) == 0


def test_generate_road(dict_of_params, tmpdir):
    sg = ClassRoadOnly(dict_of_params, "numerical")
    sg.generate(tmpdir)
    scenarios = os.listdir(os.path.join(tmpdir, "xosc"))
    opendrives = os.listdir(os.path.join(tmpdir, "xodr"))
    assert len(scenarios) == 0
    assert len(opendrives) == 6


def test_generate_both(dict_of_params, tmpdir):
    sg = ClassBoth(dict_of_params, "numerical")
    sg.generate(tmpdir)
    scenarios = os.listdir(os.path.join(tmpdir, "xosc"))
    opendrives = os.listdir(os.path.join(tmpdir, "xodr"))
    assert len(scenarios) == 6
    assert len(opendrives) == 6


def test_generate_single_only_scenario(dict_of_params, tmpdir):
    sg = ClassScenarioOnly(dict_of_params, "numerical")
    sg.generate_single(tmpdir)
    scenarios = os.listdir(os.path.join(tmpdir, "xosc"))
    opendrives = os.listdir(os.path.join(tmpdir, "xodr"))
    assert len(scenarios) == 1
    assert len(opendrives) == 0


def test_generate_single_road(dict_of_params, tmpdir):
    sg = ClassRoadOnly(dict_of_params, "numerical")
    sg.generate_single(tmpdir)
    scenarios = os.listdir(os.path.join(tmpdir, "xosc"))
    opendrives = os.listdir(os.path.join(tmpdir, "xodr"))
    assert len(scenarios) == 0
    assert len(opendrives) == 1


def test_generate_single_both(dict_of_params, tmpdir):
    sg = ClassBoth(dict_of_params, "numerical")
    sg.generate_single(tmpdir)
    scenarios = os.listdir(os.path.join(tmpdir, "xosc"))
    opendrives = os.listdir(os.path.join(tmpdir, "xodr"))
    assert len(scenarios) == 1
    assert len(opendrives) == 1
