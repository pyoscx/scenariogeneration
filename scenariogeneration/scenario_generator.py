import itertools
import os
import pyoscx
import pyodrx
import shutil

class ScenarioGenerator():
    """ ScenarioTemplate is a class that should be inherited by a Scenario class in order to generate xodr and xosc files based on pyoscx and pyodrx

        Two main uses, in your generation class define self.parameters as either as
         - a dict of lists, where the lists are the values you want to sweep over, all permutations of these sets will be generated
         - a list of dicts, where the dicts are identical and each element in the list is one scenario

        Attributes
        ----------
            road_file (str): name of the roadfile,

            parameters (dict of lists, or list of dicts): parameter sets to be used

            naming (str): two options
    """
    def __init__(self):
        self.road_file = ''
        self.parameters = {}
        self.naming = 'numerical' # can be 'numerical', 'parameter'

    def road(self,**kwargs):
        """ Dummy method for generating an OpenDRIVE road

            Should be overwritten by the user, and return a pyodrx.OpenDrive object

            Return
            ------
                sce (pyodrx.OpenDrive): a road on pyodrx format
        """
        return []

    def scenario(self,**kwargs):
        """ Dummy method for generating a OpenScenario file
            
            Should be overwritten by the user, and return a pyoscx.Scenario object

            Return
            ------
                sce (pyoscx.Scenario): a scenario on pyoscx format
        """
        return []

    def _create_folder_structure(self,generation_folder):
        """ method to create a folder structure (if needed) to generate the scenarios and roads in

            Parameters
            ----------
                generation_folder (str): the path to a folder where the files should be generated

        """
        if not os.path.exists(generation_folder):
            os.mkdir(generation_folder)
            os.mkdir(os.path.join(generation_folder,'xosc'))
            os.mkdir(os.path.join(generation_folder,'xodr'))
        
    def print_permutations(self,override_parameters = None):
        """print_permutations will create a printout to view all permutations created

            Parameters
            ----------               
                override_parameters (list of dicts, or dict of lists): overrides the self.parameters attribute

        """
        if override_parameters:
            self.parameters = override_parameters
        self._handle_input_parameters()
        it = 0
        for p in self.all_permutations:
            print('Permutation: ' + str(it))
            printstr = ''
            for key, value in p.items():
                printstr += key + ': ' + str(value) + ', '
            print(printstr)
            it += 1

    def _handle_input_parameters(self):
        """ _handle_input_parameters takes care of different types of parameters inputs, such as list of dicts or a dict of lists

        """

        if isinstance(self.parameters,dict):
            self._create_permutations()
            print('Generated ' + str(len(self.all_permutations)) + ' scenarios, using all permutations of parameters input')

        elif isinstance(self.parameters,list):
            print('Using parameters as a list of cases')
            self.all_permutations = self.parameters

    def generate(self,generation_folder,override_parameters = None):
        """ generate uses the pyoscx.Scenario defined in the method scenario and the pyodrx.OpenDrive (optional) in the road method
            together with the parameters attribute to generate scenarios and roads for all permutations defined and save those files
            in the generation_folder.
        
            Parameters
            ----------
                generation_folder (str): the path to a folder where the files should be generated
                
                override_parameters (list of dicts, or dict of lists): overrides the self.parameters attribute
        """

        self._create_folder_structure(generation_folder)
        if override_parameters:
            print('Overriding inputs via input')
            self.parameters = override_parameters
        self._handle_input_parameters()
    
        it = 0
        for p in self.all_permutations:
            name_prefix = ''

            if self.naming == 'numerical':
                name_prefix = str(it)
                it += 1
            elif self.naming == 'parameter':
                for  key, value in p.items():
                    name_prefix += '_' + key + '-' + str(value)
            else:
                raise NameError('Attribute naming, can only be "numerical" or "parameter", not ' + self.naming)

            scenario_name = os.path.basename(__file__).split('.')[0]+name_prefix
            
            # generate road
            road = self.road(**p)
            
            if road:
                self.road_file = os.path.abspath(os.path.join(generation_folder,'xodr',scenario_name+'.xodr'))
                road.write_xml(self.road_file)

            sce = self.scenario(**p)

            scenario_file = os.path.join(generation_folder,'xosc',scenario_name+'.xosc')
            sce.write_xml(scenario_file)

    def _create_permutations(self):
        """ generates all permutations of the defined parameters.

        """
        parameterlist = []
        for key in self.parameters:
            parameterlist.append(self.parameters[key])

        available_permutations = list(itertools.product(*parameterlist))
        self.all_permutations = []
        keys = list(self.parameters.keys())
        for p in available_permutations:
            inputdict = {}
            for i in range(len(self.parameters)):
                inputdict[keys[i]] = p[i]
            self.all_permutations.append(inputdict)