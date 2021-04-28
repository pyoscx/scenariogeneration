import xml.etree.ElementTree as ET
import xml.dom.minidom as mini
import os




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
        towrite = reparsed.toprettyxml(indent="    ")
        with open(filename, "w") as file_handle:
            file_handle.write(towrite)
    else:
        tree = ET.ElementTree(element)
        with open(filename, "wb") as file_handle:
            tree.write(file_handle)


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
    ped_bb = BoundingBox(dim['width'],dim['length'],dim['height'],center['x'],center['y'],center['z'])

    prettyprint(ped_bb)
    
    # create the vehicle
    return_pedestrian = Pedestrian(pedestrian.attrib['name'],pedestrian.attrib['model'],pedestrian.attrib['mass'],PedestrianCategory[pedestrian.attrib['pedestrianCategory']],ped_bb)


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
    veh_bb = BoundingBox(dim['width'],dim['length'],dim['height'],center['x'],center['y'],center['z'])

    perf = vehicle.find('Performance').attrib
    axels = vehicle.find('Axles')
    frontaxle = axels.find('FrontAxle')
    veh_front_axle = Axle(frontaxle.attrib['maxSteering'],frontaxle.attrib['wheelDiameter'],frontaxle.attrib['trackWidth'],frontaxle.attrib['positionX'],frontaxle.attrib['positionZ'])
    rearaxle = axels.find('RearAxle')
    veh_rear_axle = Axle(rearaxle.attrib['maxSteering'],rearaxle.attrib['wheelDiameter'],rearaxle.attrib['trackWidth'],rearaxle.attrib['positionX'],rearaxle.attrib['positionZ'])
    

    maxspeed = vehicle.find('Performance').attrib['maxSpeed']
    maxacc = vehicle.find('Performance').attrib['maxAcceleration']
    maxdec = vehicle.find('Performance').attrib['maxDeceleration']

    
    # create the vehicle
    return_vehicle = Vehicle(vehicle.attrib['name'],VehicleCategory[vehicle.attrib['vehicleCategory']],veh_bb,veh_front_axle,veh_rear_axle,maxspeed,maxacc,maxdec)

    if vehicle.find('Properties'):
        for prop in vehicle.find('Properties'):
            if prop.tag == 'File':
                return_vehicle.add_property_file(prop.attrib['filepath'])
            else:
                return_vehicle.add_property(prop.attrib['name'],prop.attrib['value'])
    if vehicle.find('ParameterDeclarations'):
        for param in vehicle.find('ParameterDeclarations'):
            return_vehicle.add_parameter(Parameter(param.attrib['name'],ParameterType[param.attrib['parameterType']],param.attrib['value']))
    
    return return_vehicle