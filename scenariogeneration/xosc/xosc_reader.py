import xml.etree.ElementTree as ET
import os

from scenariogeneration.xosc import Vehicle, Pedestrian, ParameterDeclarations, Controller, MiscObject, Maneuver, Environment, Trajectory, Route
from .parameters import ParameterValueDistribution
from .scenario import Scenario
from .scenario import Catalog
from .exceptions import NoCatalogFoundError, NotAValidElement

def CatalogReader(catalog_reference,catalog_path):
    """ CatalogReader is a function that will read a openscenario catalog and return the corresponding scenariogeneration.xosc object

        Main use case for this is to be able to parametrize and write scenarios based on a catalog based entry
        
        NOTE: only Vehicle, and Pedestrian is implemented
        
        Parameters
        ----------
            catalog_reference (CatalogReference): the catalog reference needed

            catalog_path (str): path to the catalog

        Returns
        -------
            Vehcile, or Pedestrian
    """
    
    # TODO: add a raised error if the catalog doesn't contain the correct data
    loaded_catalog = catalog_reference.catalogname
    
    with open(os.path.join(catalog_path,catalog_reference.catalogname + '.xosc'),'r') as f:
        loaded_catalog = ET.parse(f)
        
        catalog = loaded_catalog.find('Catalog')

        for entry in catalog:
            if entry.tag == 'Vehicle':
                if entry.attrib['name'] == catalog_reference.entryname:
                    return Vehicle.parse(entry)
            elif entry.tag == 'Pedestrian':
                if entry.attrib['name'] == catalog_reference.entryname:
                    return Pedestrian.parse(entry)
            elif entry.tag == 'Controller':
                if entry.attrib['name'] == catalog_reference.entryname:
                    return Controller.parse(entry)
            elif entry.tag == 'MiscObject':
                if entry.attrib['name'] == catalog_reference.entryname:
                    return MiscObject.parse(entry)
            elif entry.tag == 'Environment':
                if entry.attrib['name'] == catalog_reference.entryname:
                    return Environment.parse(entry)
            elif entry.tag == 'Maneuver':
                if entry.attrib['name'] == catalog_reference.entryname:
                    return Maneuver.parse(entry)
            elif entry.tag == 'Trajectory':
                if entry.attrib['name'] == catalog_reference.entryname:
                    return Trajectory.parse(entry)
            elif entry.tag == 'Route':
                if entry.attrib['name'] == catalog_reference.entryname:
                    return Route.parse(entry)    
            else:
                raise NotImplementedError('This catalogtype is not supported yet.')

        raise NoCatalogFoundError('A catalog entry with the name ' + catalog_reference.entryname + ' could not be found in the given Catalog.')

def ParameterDeclarationReader(file_path):
    """ ParameterDeclarationReader reads the parameter declaration of a xosc file and creates a ParameterDeclaration object from it

        Parameters
        ----------
            file_path (str): path to the xosc file wanted to be parsed

    """
    param_decl = ParameterDeclarations()
    with open(file_path,'r') as f:
        loaded_xosc = ET.parse(f)
        paramdec = loaded_xosc.find('ParameterDeclarations')
        param_decl = ParameterDeclarations.parse(paramdec)
            
    return param_decl


def ParseOpenScenario(file_path):
    """ ParseOpenScenario parses a openscenario file (of any type) and returns the python object

        Parameters
        ---------- 
            file_path (str): full path to the .xosc file

        Returns
        -------
            xosc_object (Scenario, Catalog, or ParameterValueDistribution)
    """
    with open(file_path,'r') as f:
        loaded_xosc = ET.parse(f)
        if loaded_xosc.find('ParameterValueDistribution') is not None:
            return ParameterValueDistribution.parse(loaded_xosc)
        elif loaded_xosc.find('Catalog') is not None:
            return Catalog.parse(loaded_xosc)
        elif loaded_xosc.find('Storyboard') is not None:
            return Scenario.parse(loaded_xosc)
        else:
            raise NotAValidElement('The provided file is not on a OpenSCENARIO compatible format.')