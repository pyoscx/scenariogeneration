"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import xml.etree.ElementTree as ET
import os


from .parameters import ParameterValueDistribution
from .scenario import Scenario, Catalog
from .exceptions import NoCatalogFoundError, NotAValidElement
from .entities import Vehicle, Pedestrian, MiscObject
from .utils import ParameterDeclarations, Controller, Environment, CatalogReference
from .storyboard import Maneuver
from .position import Trajectory, Route


class CatalogLoader:
    """CatalogLoader makes it possible to read certain elements from a catalog


    Attributes
    ----------

        all_catalogs (dict with all catalogs): all catalogs loaded

    Methods
    -------
        load_catalog(catalog_reference,catalog_path)
            loads a catalog that can be parsed later on

        get_entry(catalog_reference)
            reads a loaded catalog and returns the object
    """

    def __init__(self):
        """CatalogLoader makes it possible to read certain elements from a catalog

        Main use case for this is to be able to parametrize and write scenarios based on a catalog based entry

        """
        self.all_catalogs = {}

    def load_catalog(self, catalog_reference, catalog_path):
        """CatalogLoader makes it possible to read certain elements from a catalog

        Parameters
        ----------
            catalog_reference (CatalogReference or str): name/reference to the catalog

            catalog_path (str): path to the catalog
        """
        if isinstance(catalog_reference, CatalogReference):
            fullpath = os.path.join(
                catalog_path, catalog_reference.catalogname + ".xosc"
            )
            name_ref = catalog_reference.catalogname
        else:
            fullpath = os.path.join(catalog_path, catalog_reference + ".xosc")
            name_ref = catalog_reference

        with open(fullpath, "r") as f:
            catalog_element = ET.parse(f).find("Catalog")
            self.all_catalogs[name_ref] = catalog_element

    def parse(self, catalog_reference):
        """parse reads reads a specific entry from a loaded catalog

        Parameters
        ----------
            catalog_reference (CatalogReference): reference to the catalog

        Returns
        -------
            The catalog entry

        """
        if not catalog_reference.catalogname in self.all_catalogs:
            raise NoCatalogFoundError(
                "Catalog " + catalog_reference.catalogname + " is not loaded yet."
            )
        catalog = self.all_catalogs[catalog_reference.catalogname]
        for entry in catalog:
            if entry.tag == "Vehicle":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Vehicle.parse(entry)
            elif entry.tag == "Pedestrian":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Pedestrian.parse(entry)
            elif entry.tag == "Controller":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Controller.parse(entry)
            elif entry.tag == "MiscObject":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return MiscObject.parse(entry)
            elif entry.tag == "Environment":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Environment.parse(entry)
            elif entry.tag == "Maneuver":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Maneuver.parse(entry)
            elif entry.tag == "Trajectory":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Trajectory.parse(entry)
            elif entry.tag == "Route":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Route.parse(entry)
            else:
                raise NotImplementedError("This catalogtype is not supported yet.")

    def read_entry(self, catalog_reference, catalog_path):
        """read_entry loads and reads a catalog directly (both load_catalog, and parse)

        The catalog will still be loaded and can be used with parse after this.

        Parameters
        ----------
            catalog_reference (CatalogReference): reference to the catalog

            catalog_path (str): path to the catalog
        """
        self.load_catalog(catalog_reference, catalog_path)
        return self.parse(catalog_reference)


def CatalogReader(catalog_reference, catalog_path):
    """CatalogReader is a function that will read a openscenario catalog and return the corresponding scenariogeneration.xosc object

    Main use case for this is to be able to parametrize and write scenarios based on a catalog based entry

    NOTE: only Vehicle, and Pedestrian is implemented

    Parameters
    ----------
        catalog_reference (CatalogReference): the catalog reference needed

        catalog_path (str): path to the catalog

    Returns
    -------
        The catalog entry
    """

    # TODO: add a raised error if the catalog doesn't contain the correct data
    loaded_catalog = catalog_reference.catalogname

    with open(
        os.path.join(catalog_path, catalog_reference.catalogname + ".xosc"), "r"
    ) as f:
        loaded_catalog = ET.parse(f)

        catalog = loaded_catalog.find("Catalog")

        for entry in catalog:
            if entry.tag == "Vehicle":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Vehicle.parse(entry)
            elif entry.tag == "Pedestrian":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Pedestrian.parse(entry)
            elif entry.tag == "Controller":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Controller.parse(entry)
            elif entry.tag == "MiscObject":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return MiscObject.parse(entry)
            elif entry.tag == "Environment":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Environment.parse(entry)
            elif entry.tag == "Maneuver":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Maneuver.parse(entry)
            elif entry.tag == "Trajectory":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Trajectory.parse(entry)
            elif entry.tag == "Route":
                if entry.attrib["name"] == catalog_reference.entryname:
                    return Route.parse(entry)
            else:
                raise NotImplementedError("This catalogtype is not supported yet.")

        raise NoCatalogFoundError(
            "A catalog entry with the name "
            + catalog_reference.entryname
            + " could not be found in the given Catalog."
        )


def ParameterDeclarationReader(file_path):
    """ParameterDeclarationReader reads the parameter declaration of a xosc file and creates a ParameterDeclaration object from it

    Parameters
    ----------
        file_path (str): path to the xosc file wanted to be parsed

    """
    param_decl = ParameterDeclarations()
    with open(file_path, "r") as f:
        loaded_xosc = ET.parse(f)
        paramdec = loaded_xosc.find("ParameterDeclarations")
        param_decl = ParameterDeclarations.parse(paramdec)

    return param_decl


def ParseOpenScenario(file_path):
    """ParseOpenScenario parses a openscenario file (of any type) and returns the python object

    Parameters
    ----------
        file_path (str): full path to the .xosc file

    Returns
    -------
        xosc_object (Scenario, Catalog, or ParameterValueDistribution)
    """
    with open(file_path, "r") as f:
        loaded_xosc = ET.parse(f)
        if loaded_xosc.find("ParameterValueDistribution") is not None:
            return ParameterValueDistribution.parse(loaded_xosc)
        elif loaded_xosc.find("Catalog") is not None:
            return Catalog.parse(loaded_xosc)
        elif loaded_xosc.find("Storyboard") is not None:
            return Scenario.parse(loaded_xosc)
        else:
            raise NotAValidElement(
                "The provided file is not on a OpenSCENARIO compatible format."
            )
