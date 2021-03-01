import xml.etree.ElementTree as ET
import xml.dom.minidom as mini
import os


def esminiRunner(scenario, esminipath='esmini', args='--window 60 60 800 400'):
    """ write a scenario and runs it in esmini
        Parameters
        ----------
            scenario (Scenario): the pypscx scenario to run

            esminipath (str): the path to esmini 
                Default: pyoscx

            args: pass through esmini launch commands

    """
    _scenariopath = os.path.join(esminipath, 'resources', 'xosc')
    scenario.write_xml(os.path.join(_scenariopath, 'pythonscenario2.xosc'), True)

    if os.name == 'posix':
        os.system(os.path.join('.',
                               esminipath,
                               'bin',
                               'esmini') + ' --osc ' + esminipath + '/resources/xosc/pythonscenario2.xosc ' + args)
    elif os.name == 'nt':
        os.system(os.path.join(esminipath,
                               'bin',
                               'esmini.exe') + ' --osc ' + esminipath + '/resources/xosc/pythonscenario2.xosc ' + args)

def esminiRunViewer(scenario,esminipath='esmini',args=' --window 100 100 1000 600'):
    """ writes and runs esmini in headless mode then launch the replayer for analysis of the scenario
        Parameters
        ----------
            scenario (Scenario): the pypscx scenario to run

            esminipath (str): the path to esmini 
                Default: esmini

            args: pass through replayer commands
    """
    _scenariopath = os.path.join(esminipath, 'resources', 'xosc')
    scenario.write_xml(os.path.join(_scenariopath, 'pythonscenario2.xosc'), True)

    if os.name == 'posix':
        os.system(os.path.join('.',
                               esminipath,
                               'bin',
                               'esmini') + ' --osc ' + esminipath + '/resources/xosc/pythonscenario2.xosc --record python_replay --headless')

        os.system(os.path.join('.',
                               esminipath,
                               'bin',
                               'replayer') + ' --file python_replay --res_path ' + os.path.join(esminipath,'resources') + args)

                               
    elif os.name == 'nt':
        os.system(os.path.join(esminipath,
                               'bin',
                               'esmini.exe') + ' --osc ' + esminipath + '/resources/xosc/pythonscenario2.xosc --record python_replay --headless' + args)
    
        os.system(os.path.join('.',
                               esminipath,
                               'bin',
                               'replayer.exe') + ' --file python_replay --res_path ' + os.path.join(esminipath,'resources') + args)

def prettyprint(element):
    """ prints the element to the commandline

        Parameters
        ----------
            element (Element): element to print

    """
    rough = ET.tostring(element, 'utf-8')
    reparsed = mini.parseString(rough)
    print(reparsed.toprettyxml(indent="\t"))


def printToFile(element, filename, prettyprint=True):
    """ prints the element to a xml file

        Parameters
        ----------
            element (Element): element to print

            filename (str): file to save to

            prettyprint (bool): pretty or "ugly" print

    """
    if prettyprint:
        rough = ET.tostring(element, 'utf-8').replace(b'\n', b'').replace(b'\t', b'')
        reparsed = mini.parseString(rough)
        towrite = reparsed.toprettyxml(indent="\t")
        with open(filename, "w") as file_handle:
            file_handle.write(towrite)
    else:
        tree = ET.ElementTree(element)
        with open(filename, "wb") as file_handle:
            tree.write(file_handle)
