""" helpers contains a launcher of esmini and a simple print function for the xmls

"""
import xml.etree.ElementTree as ET
import xml.dom.minidom as mini
import os

from .scenario_generator import ScenarioGenerator
from .xodr import OpenDrive
from .xosc import Scenario


def esmini(generator,esminipath='esmini',
    window_size = '60 60 800 400',
    save_osi=False,
    record=False,
    disable_controllers=False,
    args = '',
    index_to_run= 'first',
    run_with_replayer = False,
    timestep = 0.01,
    car_density = 15):
    """ write a scenario and runs it in esminis OpenDriveViewer with some random traffic
     
        Parameters
        ----------
            generator (OpenDrive, Scenario, or ScenarioGenerator): the xodr road to run

            esminipath (str): the path to esmini 
                Default: esmini
            
            window_size (str): sets the window size of the esmini viewer 
                Default: 60 60 800 400

            save_osi (bool): if an .osi file should be saved
                Default: False

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

            timestep (double): fixed timestep to use in combination with replayer

            car_density (int): density of fictious cars (used only for pure OpenDRIVE cases)

    """
    additional_args = ''
    resource_path = os.path.join(esminipath,'resources')
    # genereate file for running in esmini, and set some esmini replated parameters
    if isinstance(generator,OpenDrive):
        executable = 'odrviewer'
        filetype = ' --odr '
        additional_args += ' --density ' + str(car_density)
        run_with_replayer = False
        filename = os.path.join(resource_path,'xodr','python_road.xodr')
        generator.write_xml(filename,True)
    elif isinstance(generator,Scenario):
        executable = 'esmini'
        filetype = ' --osc '
        if run_with_replayer:
            additional_args += ' --headless' + ' --fixed_timestep ' +  str(timestep)
            if not record:
                record = 'python_record'
        else:
                additional_args += ' --window '+ window_size

        filename = os.path.join(resource_path,'xosc','python_scenario.xosc')
        generator.write_xml(filename)

    elif isinstance(generator,ScenarioGenerator):
        scenario_file, road_file = generator.generate_single(resource_path, order = index_to_run)
        
        if scenario_file == '':
            run_with_replayer = False
            executable = 'odrviewer'
            filetype = ' --odr '
            additional_args += ' --density ' + str(car_density)
            filename = road_file
        else:
            executable = 'esmini'
            filetype = ' --osc '
            if run_with_replayer:
                additional_args += ' --headless' + ' --fixed_timestep ' +  str(timestep)
                if not record:
                    record = 'python_record'
            else:
                additional_args += ' --window '+ window_size
            
            filename = scenario_file
    else:
        raise TypeError('generator is not of type OpenDrive, Scenario, or ScenarioGenerator')


    
    # create the additional_args for the esmini execusion
    if save_osi:
        additional_args += ' --osi_file on'
    
    if record:
        additional_args += ' --record ' + record

    if disable_controllers:
        additional_args += ' --disable_controllers'
    

    additional_args += ' ' + args
    
    # find executable based on OS
    if os.name == 'posix':
        executable_path = os.path.join('.', esminipath, 'bin',executable) 
        replay_executable = os.path.join('.', esminipath, 'bin','replayer') 
    elif os.name == 'nt':
        executable_path = os.path.join(esminipath,'bin',executable + '.exe') 
        replay_executable = os.path.join('.', esminipath, 'bin','replayer.exe')


    # run esmini
    if os.system(executable_path + filetype + filename + additional_args) != 0:
        print('An error occurred while trying to execute the scenario')
        return

    # run viewer if wanted
    if run_with_replayer:
        os.system(replay_executable + ' --file ' + record +' --res_path ' + os.path.join(esminipath,'resources') +  ' --window '+ window_size)



def prettyprint(element):
    """ prints the element to the commandline

        Parameters
        ----------
            element (Element, or any generation class of scenariogeneration): element to print

    """
    if not isinstance(element,ET.Element):
        element = element.get_element()
    rough = ET.tostring(element, 'utf-8')
    reparsed = mini.parseString(rough)
    print(reparsed.toprettyxml(indent="    "))




