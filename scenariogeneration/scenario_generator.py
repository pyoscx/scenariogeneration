"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import itertools
import os
import numpy as np
import sys
from multiprocessing import Pool
from .helpers import printToFile


class _generation_struct:
    def __init__(self, data, filename, prettyprint, encoding="utf-8"):
        self.data = data
        self.filename = filename
        self.prettyprint = prettyprint
        self.encoding = encoding


def _write_xml_file(data_struct):
    printToFile(
        data_struct.data,
        data_struct.filename,
        data_struct.prettyprint,
        data_struct.encoding,
    )


class ScenarioGenerator:
    """ScenarioTemplate is a class that should be inherited by a Scenario class in order to generate xodr and xosc files based on pyoscx and pyodrx

    Two main uses, in your generation class define self.parameters as either as
     - a dict of lists, where the lists are the values you want to sweep over, all permutations of these sets will be generated
     - a list of dicts, where the dicts are identical and each element in the list is one scenario

    Attributes
    ----------
        road_file (str): name of the roadfile

        parameters (dict of lists, or list of dicts): parameter sets to be used

        naming (str): two options "numerical" or "parameter"

        generate_all_roads (bool): will only generate unique roads

        number_of_parallel_writings (int): parallelize the writing of the xml files
            Default: 1 (no parallelization)

        basename (str): basename of the scenariofiles,
            Default: name of file

        encoding (str): encoding of the outputs
            Default:
    """

    def __init__(self):
        self.road_file = ""
        self.parameters = {}
        self.naming = "numerical"  # can be 'numerical', 'parameter'
        self._it = 0
        self._generation_folder = ""

        self.generate_all_roads = True
        self._created_roads = {}
        self._name_separator = "_"
        self.number_of_parallel_writings = 1
        self._prettyprint = True
        self.basename = os.path.basename(
            sys.modules[self.__class__.__module__].__file__
        ).split(".")[0]
        self.encoding = "utf-8"

    def road(self, **kwargs):
        """Dummy method for generating an OpenDRIVE road

        Should be overwritten by the user, and return a pyodrx.OpenDrive object

        Return
        ------
            sce (pyodrx.OpenDrive): a road on pyodrx format
        """
        return []

    def scenario(self, **kwargs):
        """Dummy method for generating a OpenScenario file

        Should be overwritten by the user, and return a pyoscx.Scenario object

        Return
        ------
            sce (pyoscx.Scenario): a scenario on pyoscx format
        """
        return []

    def _reset_name_counter(self):
        """method to reset the counter if numerical naming is used."""
        self._it = 0

    def _create_folder_structure(self, generation_folder):
        """method to create a folder structure (if needed) to generate the scenarios and roads in

        Parameters
        ----------
            generation_folder (str): the path to a folder where the files should be generated

        """
        xosc_folder = os.path.join(generation_folder, "xosc")
        xodr_folder = os.path.join(generation_folder, "xodr")

        if not os.path.exists(generation_folder):
            os.mkdir(generation_folder)
        if not os.path.exists(xosc_folder):
            os.mkdir(xosc_folder)
        if not os.path.exists(xodr_folder):
            os.mkdir(xodr_folder)

        self._generation_folder = generation_folder

    def print_permutations(self, override_parameters=None):
        """print_permutations will create a printout to view all permutations created

        Parameters
        ----------
            override_parameters (list of dicts, or dict of lists): overrides the self.parameters attribute

        """
        if override_parameters:
            self.parameters = override_parameters
        self._handle_input_parameters()
        for it, p in enumerate(self.all_permutations):
            print(f"Permutation: {str(it)}")
            printstr = "".join(f"{key}: {str(value)}, " for key, value in p.items())
            print(printstr)

    def _handle_input_parameters(self):
        """_handle_input_parameters takes care of different types of parameters inputs, such as list of dicts or a dict of lists"""

        if isinstance(self.parameters, dict):
            self._create_permutations()

        elif isinstance(self.parameters, list):
            self.all_permutations = self.parameters

    def _generate_road_and_scenario(self, permutation):
        """_generate_road_and_scenario takes a permutation and generates the road/scenario (if specified)

        Parameters
        ----------
            permutation (dict): the parameter dict of the wanted scenario

        Returns
        -------
            open_scenario_file (str), open_drive_file (str)
        """
        scenario_name = self._get_scenario_name(permutation)
        self.road_file = ""
        scenario_file = ""
        files_to_write = []
        if road := self.road(**permutation):
            new_unique_road = True
            if not self.generate_all_roads:
                for previous_road in self._created_roads:
                    if self._created_roads[previous_road] == road:
                        self.road_file = previous_road
                        new_unique_road = False

            if new_unique_road:
                self.road_file = os.path.abspath(
                    os.path.join(
                        self._generation_folder, "xodr", f"{scenario_name}.xodr"
                    )
                )
                if self.number_of_parallel_writings == 1:
                    road.write_xml(self.road_file, prettyprint=self._prettyprint)
                else:
                    files_to_write.append(
                        _generation_struct(
                            road.get_element(),
                            self.road_file,
                            self._prettyprint,
                            self.encoding,
                        )
                    )

                if self.write_relative_road_path:
                    self.road_file = self.road_file.replace(
                        os.path.abspath(self._generation_folder), os.path.pardir
                    )

                self._created_roads[self.road_file] = road

        if sce := self.scenario(**permutation):
            scenario_file = os.path.join(
                self._generation_folder, "xosc", f"{scenario_name}.xosc"
            )
            if self.number_of_parallel_writings == 1:
                sce.write_xml(scenario_file, prettyprint=self._prettyprint)
            else:
                files_to_write.append(
                    _generation_struct(
                        sce.get_element(),
                        scenario_file,
                        self._prettyprint,
                        self.encoding,
                    )
                )
        return scenario_file, self.road_file, files_to_write

    def _get_scenario_name(self, permutation):
        """_get_scenario_name generates the name of the wanted file, based on the permutation

        Parameters
        ----------
            permutation (dict): a permutation to create name from (used for the parameter naming option)

        Returns
        -------
            scenario_name (str)
        """
        name_prefix = ""

        if self.naming == "numerical":
            name_prefix = str(self._it)
            self._it += 1
        elif self.naming in ["parameter", "parameter_no_lists"]:
            for key, value in permutation.items():
                if isinstance(value, list) and self.naming == "parameter_no_lists":
                    value_str = str(self._it)
                    self._it += 1
                else:
                    value_str = str(value).replace("\\", "-").replace("/", "-")
                name_prefix += (
                    self._name_separator
                    + key.replace("\\", "-").replace("/", "-")
                    + "-"
                    + value_str
                )

        else:
            raise NameError(
                'Attribute naming, can only be "numerical" or "parameter", not '
                + self.naming
            )

        return self.basename + name_prefix

    def generate_single(
        self,
        generation_folder,
        order="first",
        override_parameters=None,
        write_relative_road_path=True,
        name_separator=None,
        prettyprint=True,
    ):
        """generate_single will generate only one scenario

        Parameters
        ----------
            generation_folder (str): the path to a folder where the files should be generated

            order (str, or int): if multiple permutations are defined, this enables the picking of different permutations
                                 int - the number of that permutation
                                 str - first: first permutation
                                       middle: the permutation in the middle
                                       random: a random permutation
                Default: 'first'

            override_parameters (list of dicts, or dict of lists): overrides the self.parameters attribute (optional)

            write_relative_road_path (bool): if the generator will write the path to a generated xodr file relative to the xosc (true),
                                             or the absolute path to the xodr (false)
                Default: True

            name_separator (str): for generation with multiple parameters, this will change the separator between the variables
                Default: '_'

            prettyprint (bool): determins if the prettify funciton should be used while writing to xml (will take longer time)
                Default: True
        """
        self._prettyprint = prettyprint
        if name_separator:
            self._name_separator = name_separator
        self.write_relative_road_path = write_relative_road_path
        self._create_folder_structure(generation_folder)
        if override_parameters:
            self.parameters = override_parameters
        self._handle_input_parameters()

        if isinstance(order, str):
            if order == "first":
                it = 0
            elif order == "middle":
                it = int(np.floor(len(self.all_permutations) / 2))
            elif order == "random":
                it = int(np.floor(np.random.rand() * len(self.all_permutations)))
        else:
            it = order
            self._it = it
        self.number_of_parallel_writings = 1
        osc, odr, _ = self._generate_road_and_scenario(self.all_permutations[it])
        self._reset_name_counter()
        return osc, odr

    def generate(
        self,
        generation_folder,
        override_parameters=None,
        write_relative_road_path=True,
        name_separator=None,
        prettyprint=True,
    ):
        """generate uses the xosc.Scenario defined in the method scenario and the xodr.OpenDrive (optional) in the road method
        together with the parameters attribute to generate scenarios and roads for all permutations defined and save those files
        in the generation_folder.

        Parameters
        ----------
            generation_folder (str): the path to a folder where the files should be generated

            override_parameters (list of dicts, or dict of lists): overrides the self.parameters attribute (optional)

            write_relative_road_path (bool): if the generator will write the path to a generated xodr file relative to the xosc (true), or the absolute path to the xodr (false)
                Default: True

            name_separator (str): for generation with multiple parameters, this will change the separator between the variables
                Default: '_'

            prettyprint (bool): determins if the prettify funciton should be used while writing to xml (will take longer time)
                Default: True
        """
        self._prettyprint = prettyprint
        if name_separator:
            self._name_separator = name_separator

        self.write_relative_road_path = write_relative_road_path
        scenario_files = []
        road_files = []
        self._create_folder_structure(generation_folder)
        if override_parameters:
            self.parameters = override_parameters
        self._handle_input_parameters()
        files_to_write = []
        for p in self.all_permutations:
            scenario_file, road_file, writables = self._generate_road_and_scenario(p)
            scenario_files.append(scenario_file)
            road_files.append(road_file)
            files_to_write.extend(writables)

        if self.number_of_parallel_writings != 1:
            with Pool(self.number_of_parallel_writings) as p:
                p.map(_write_xml_file, files_to_write)
        self._reset_name_counter()
        return scenario_files, road_files

    def _create_permutations(self):
        """generates all permutations of the defined parameters.

        Returns
        -------
            scenario_files (list of str): all scenenario files generated
        """
        parameterlist = [self.parameters[key] for key in self.parameters]
        available_permutations = list(itertools.product(*parameterlist))
        self.all_permutations = []
        keys = list(self.parameters.keys())
        for p in available_permutations:
            inputdict = {keys[i]: p[i] for i in range(len(self.parameters))}
            self.all_permutations.append(inputdict)
