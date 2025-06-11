"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import os
import subprocess
from typing import Optional, Union

from .scenario_generator import ScenarioGenerator
from .xodr import OpenDrive
from .xosc import Scenario


def esmini(
    generator: Union[OpenDrive, Scenario, ScenarioGenerator],
    esminipath: str = "esmini",
    window_size: str = "60 60 800 400",
    save_osi: Optional[str] = None,
    record: Optional[str] = "",
    disable_controllers: bool = False,
    args: str = "",
    index_to_run: Union[str, int] = "first",
    run_with_replayer: bool = False,
    generation_path: str = "generated",
    resource_path: Optional[str] = None,
    timestep: float = 0.01,
    car_density: int = 15,
    headless: bool = False,
) -> None:
    """Write a scenario and run it in esmini's OpenDriveViewer with random
    traffic.

    Parameters
    ----------
    generator : OpenDrive, Scenario, or ScenarioGenerator
        The xodr road or scenario to run.
    esminipath : str, optional
        The path to the esmini executable. Default is "esmini".
    window_size : str, optional
        Sets the window size of the esmini viewer. Default is "60 60 800 400".
    save_osi : str, optional
        Name of the desired OSI file. If None, no OSI file is created.
        Default is None.
    record : str, optional
        Name of the esmini `.dat` file to save. Default is an empty string
        (no recording).
    disable_controllers : bool, optional
        Disable all controllers in the scenario and run with default behavior.
        Default is False.
    args : str, optional
        Additional options to pass to esmini. Default is an empty string.
    index_to_run : str or int, optional
        If a class inheriting `ScenarioGenerator` is used as input and the
        scenario is parametrized, this specifies which scenario to view.
        Can be "first", "middle", "random", or an integer
        Default is "first".
    run_with_replayer : bool, optional
        Run esmini in headless mode and then replay the viewer afterward.
        Only used for scenarios, not roads. Default is False.
    generation_path : str, optional
        Path to where the files should be generated. Default is "generated".
    resource_path : str, optional
        Path to the catalogs/xodrs to add. Relative paths in the scenario
        should be relative to this one. Default is None.
    timestep : float, optional
        Fixed timestep to use in combination with the replayer.
        Default is 0.01.
    car_density : int, optional
        Density of fictitious cars (used only for pure OpenDRIVE cases).
        Default is 15.
    headless : bool, optional
        Run esmini in headless mode (no viewer). Default is False.

    Returns
    -------
    None
    """
    additional_args = []
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
        filetype = "--odr"
        additional_args += ["--density", str(car_density)]
        if not headless:
            additional_args += ["--window"] + window_size.split()
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
        filetype = "--osc"
        if run_with_replayer:
            additional_args += ["--headless", "--fixed_timestep", str(ts)]
            if not record:
                record = "python_record"
        elif not headless:
            additional_args += ["--window"] + window_size.split()

        filename = os.path.join(
            generation_path, "xosc", "python_scenario.xosc"
        )
        generator.write_xml(filename)

    elif isinstance(generator, ScenarioGenerator):
        scenario_file, road_file = generator.generate_single(
            generation_path, order=index_to_run
        )

        if scenario_file == "":
            run_with_replayer = False
            executable = "odrviewer"
            filetype = "--odr"
            additional_args += ["--density", str(car_density)]
            additional_args += ["--window"] + window_size.split()
            filename = os.path.join(
                generation_path, "xodr", os.path.split(road_file)[1]
            )
        else:
            executable = "esmini"
            filetype = "--osc"
            if run_with_replayer:
                additional_args += ["--headless", "--fixed_timestep", str(ts)]
                if not record:
                    record = "python_record"
            elif not headless:
                additional_args += ["--window"] + window_size.split()

            filename = scenario_file
    else:
        raise TypeError(
            "generator is not of type OpenDrive, Scenario, or ScenarioGenerator"
        )

    # create the additional_args for the esmini execusion
    if save_osi:
        additional_args += ["--osi_file", save_osi]

    if record:
        additional_args += ["--record", record]

    if disable_controllers:
        additional_args += ["--disable_controllers"]

    if timestep != None:
        additional_args += ["--fixed_timestep", str(timestep)]

    additional_args += [args, "--path", resource_path]

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

    cmd_and_args = (
        [executable_path] + [filetype] + [filename] + additional_args
    )
    print("Executing: ", " ".join(cmd_and_args))
    result = subprocess.run(cmd_and_args)
    if result.returncode != 0:
        print("An error occurred while trying to execute the scenario")
        return

    # run viewer if wanted
    if run_with_replayer:
        cmd_and_args = [
            replay_executable,
            "--file",
            record,
            "--res_path",
            os.path.join(resource_path, os.pardir),
            "--window",
            *window_size.split(),
            "--path",
            generation_path,
        ]
        print("Replaying: ", " ".join(cmd_and_args))
        result = subprocess.run(cmd_and_args)
        if result.returncode != 0:
            print("An error occurred while trying to replay the scenario")
            return
