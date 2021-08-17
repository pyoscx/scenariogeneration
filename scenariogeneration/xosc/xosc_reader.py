import xml.etree.ElementTree as ET
import os

from scenariogeneration.xosc import BoundingBox, Vehicle, Axle, VehicleCategory, Parameter, ParameterType, Pedestrian, PedestrianCategory, ParameterDeclarations
from .exceptions import NoCatalogFoundError

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
                    return _parseVehicleCatalog(entry)
            elif entry.tag == 'Pedestrian':
                
                if entry.attrib['name'] == catalog_reference.entryname:
                    return _parsePedestrianCatalog(entry)
            else:
                raise NotImplementedError('This catalogtype is not supported yet.')

        raise NoCatalogFoundError('A catalog entry with the name ' + catalog_reference.entryname + ' could not be found in the given Catalog.')

def _parsePedestrianCatalog(pedestrian):
    """ _parsePedestrianCatalog parses a catalog of a pedestrian and creates a xosc.Pedestrian from a premade catalog

        Parameters
        ----------
            pedestrian (ET.Element): a vehicle tagged xml element

        Return
        ------
            pedestrian (Pedestrian)
    """

    # Get the mandatory info
    center = pedestrian.find('BoundingBox').find('Center').attrib
    dim = pedestrian.find('BoundingBox').find('Dimensions').attrib
    ped_bb = BoundingBox(float(dim['width']),float(dim['length']),float(dim['height']),float(center['x']),float(center['y']),float(center['z']))

    # create the vehicle
    if pedestrian.find('model'):
        model = pedestrian.attrib['model']
    elif pedestrian.find('model3d'):
        model = pedestrian.attrib['model3d']
    else:
        model = ''
    
    return_pedestrian = Pedestrian(pedestrian.attrib['name'],model,float(pedestrian.attrib['mass']),getattr(PedestrianCategory,pedestrian.attrib['pedestrianCategory']),ped_bb)


    if pedestrian.find('Properties'):
        for prop in pedestrian.find('Properties'):
            if prop.tag == 'File':
                return_pedestrian.add_property_file(prop.attrib['filepath'])
            else:
                return_pedestrian.add_property(prop.attrib['name'],prop.attrib['value'])
    if pedestrian.find('ParameterDeclarations'):
        for param in pedestrian.find('ParameterDeclarations'):
            return_pedestrian.add_parameter(Parameter(param.attrib['name'],ParameterType[param.attrib['parameterType']],param.attrib['value']))
            
    return return_pedestrian




def _parseVehicleCatalog(vehicle):
    """ _parseVehicleCatalog parses a catalog of a vehicle and creates a xosc.Vehicle from a premade catalog

        Parameters
        ----------
            vehicle (ET.Element): a vehicle tagged xml element

        Return
        ------
            vehicle (Vehicle)
    """

    #TODO: add for more axles

    # Get the mandatory info
    center = vehicle.find('BoundingBox').find('Center').attrib
    dim = vehicle.find('BoundingBox').find('Dimensions').attrib
    veh_bb = BoundingBox(float(dim['width']),float(dim['length']),float(dim['height']),float(center['x']),float(center['y']),float(center['z']))

    perf = vehicle.find('Performance').attrib
    axels = vehicle.find('Axles')
    frontaxle = axels.find('FrontAxle')
    veh_front_axle = Axle(float(frontaxle.attrib['maxSteering']),float(frontaxle.attrib['wheelDiameter']),float(frontaxle.attrib['trackWidth']),float(frontaxle.attrib['positionX']),float(frontaxle.attrib['positionZ']))
    rearaxle = axels.find('RearAxle')
    veh_rear_axle = Axle(float(rearaxle.attrib['maxSteering']),float(rearaxle.attrib['wheelDiameter']),float(rearaxle.attrib['trackWidth']),float(rearaxle.attrib['positionX']),float(rearaxle.attrib['positionZ']))
    

    maxspeed = float(vehicle.find('Performance').attrib['maxSpeed'])
    maxacc = float(vehicle.find('Performance').attrib['maxAcceleration'])
    maxdec = float(vehicle.find('Performance').attrib['maxDeceleration'])

    
    # create the vehicle
    return_vehicle = Vehicle(vehicle.attrib['name'],getattr(VehicleCategory,vehicle.attrib['vehicleCategory']),veh_bb,veh_front_axle,veh_rear_axle,maxspeed,maxacc,maxdec)

    if vehicle.find('Properties'):
        for prop in vehicle.find('Properties'):
            if prop.tag == 'File':
                return_vehicle.add_property_file(prop.attrib['filepath'])
            else:
                return_vehicle.add_property(prop.attrib['name'],prop.attrib['value'])
    if vehicle.find('ParameterDeclarations'):
        for param in vehicle.find('ParameterDeclarations'):
            return_vehicle.add_parameter(Parameter(param.attrib['name'],getattr(ParameterType, param.attrib['parameterType']),param.attrib['value']))
    
    return return_vehicle

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
        for param in paramdec:
            print(param.attrib['parameterType'])
            param_type = getattr(ParameterType,param.attrib['parameterType'])
            if param_type == ParameterType.double:
                value = float(param.attrib['value'])
            elif param_type == ParameterType.integer or param_type == ParameterType.unsighedInt or param_type == ParameterType.unsighedShort:
                value = int(param.attrib['value'])
            elif param_type == ParameterType.boolean:
                value = bool(param.attrib['value'])
            else:
                value = param.attrib['value']
            
            param_decl.add_parameter(Parameter(param.attrib['name'],param_type,value))
            
    return param_decl
