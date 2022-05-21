"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import os

from .scenario_generator import ScenarioGenerator
from .xodr import OpenDrive
from .xosc import Scenario


def esmini(
    generator,
    esminipath="esmini",
    window_size="60 60 800 400",
    save_osi=False,
    record=False,
    disable_controllers=False,
    args="",
    index_to_run="first",
    run_with_replayer=False,
    generation_path="generated",
    resource_path=None,
    timestep=0.01,
    car_density=15,
):
    """write a scenario and runs it in esminis OpenDriveViewer with some random traffic

    Parameters
    ----------
        generator (OpenDrive, Scenario, or ScenarioGenerator): the xodr road to run

        esminipath (str): the path to esmini
            Default: esmini

        window_size (str): sets the window size of the esmini viewer
            Default: 60 60 800 400

        save_osi (str): name of the wanted osi file (None will not create a osi file)
            Default: None

        record (str): name of a esmini .dat file should be saved
            Default: '' (no recording)

        disable_controllers (bool): let esmini disable all controllers in the scenario and run with default behaviour
            Default: False

        args (str): additional options to esmini

        index_to_run (str,int): if the a class inheriting ScenarioGenerator is used as input, and the scenario is parametrized
                                this will make it possible to choose what scenario to view. can be: 'first','middle','random', or an int
            Default: first

        run_with_replayer (bool): bool to run esmini in headless mode and then run the viewer afterwards (only used for scenarios not for roads)
            Default: False

        generation_path (str): path to where the files should be generated
            Default: generated

        resource_path (str): path to the catalogs/xodrs that you want to add (relative path in scenario should be relative to this one)
            Default: esminipath/resources/xosc

        timestep (float): fixed timestep to use in combination with replayer

        car_density (int): density of fictious cars (used only for pure OpenDRIVE cases)

    """
    additional_args = ""
    # resource_path = os.path.join(esminipath,'resources')
    if not resource_path:
        resource_path = os.path.join(esminipath, "resources", "xosc")

    if timestep == None:
        ts = 0.01
    else:
        ts = timestep
    # genereate file for running in esmini, and set some esmini replated parameters
    if isinstance(generator, OpenDrive):
        if not os.path.exists(generation_path):
            os.mkdir(generation_path)
        if not os.path.exists(os.path.join(generation_path, "xosc")):
            os.mkdir(os.path.join(generation_path, "xosc"))
        if not os.path.exists(os.path.join(generation_path, "xodr")):
            os.mkdir(os.path.join(generation_path, "xodr"))
        executable = "odrviewer"
        filetype = " --odr "
        additional_args += " --density " + str(car_density)
        additional_args += " --window " + window_size
        run_with_replayer = False
        filename = os.path.join(generation_path, "xodr", "python_road.xodr")
        generator.write_xml(filename, True)

    elif isinstance(generator, Scenario):
        if not os.path.exists(generation_path):
            os.mkdir(generation_path)
        if not os.path.exists(os.path.join(generation_path, "xosc")):
            os.mkdir(os.path.join(generation_path, "xosc"))
        if not os.path.exists(os.path.join(generation_path, "xodr")):
            os.mkdir(os.path.join(generation_path, "xodr"))
        executable = "esmini"
        filetype = " --osc "
        if run_with_replayer:
            additional_args += " --headless" + " --fixed_timestep " + str(ts)
            if not record:
                record = "python_record"
        else:
            additional_args += " --window " + window_size

        filename = os.path.join(generation_path, "xosc", "python_scenario.xosc")
        generator.write_xml(filename)

    elif isinstance(generator, ScenarioGenerator):
        scenario_file, road_file = generator.generate_single(
            generation_path, order=index_to_run
        )

        if scenario_file == "":
            run_with_replayer = False
            executable = "odrviewer"
            filetype = " --odr "
            additional_args += " --density " + str(car_density)
            additional_args += " --window " + window_size
            filename = road_file
        else:
            executable = "esmini"
            filetype = " --osc "
            if run_with_replayer:
                additional_args += " --headless" + " --fixed_timestep " + str(ts)
                if not record:
                    record = "python_record"
            else:
                additional_args += " --window " + window_size

            filename = scenario_file
    else:
        raise TypeError(
            "generator is not of type OpenDrive, Scenario, or ScenarioGenerator"
        )

    # create the additional_args for the esmini execusion
    if save_osi:
        additional_args += " --osi_file " + save_osi

    if record:
        additional_args += " --record " + record

    if disable_controllers:
        additional_args += " --disable_controllers"

    if timestep != None:
        additional_args += " --fixed_timestep " + str(timestep)

    additional_args += " " + args + "--path " + resource_path

    # find executable based on OS
    if os.name == "posix":
        executable_path = os.path.join(".", esminipath, "bin", executable)
        replay_executable = os.path.join(".", esminipath, "bin", "replayer")
    elif os.name == "nt":
        executable_path = os.path.join(
            os.path.realpath(esminipath), "bin", executable + ".exe"
        )
        replay_executable = os.path.join(
            ".", os.path.realpath(esminipath), "bin", "replayer.exe"
        )

    # run esmini
    if os.system(executable_path + filetype + filename + additional_args) != 0:
        print("An error occurred while trying to execute the scenario")
        return

    # run viewer if wanted
    if run_with_replayer:
        os.system(
            replay_executable
            + " --file "
            + record
            + " --res_path "
            + os.path.join(resource_path, os.pardir)
            + " --window "
            + window_size
        )
