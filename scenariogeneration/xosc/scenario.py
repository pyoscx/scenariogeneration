"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import datetime
import xml.etree.ElementTree as ET
from typing import Optional

from ..helpers import printToFile
from .entities import Entities
from .enumerations import _MINOR_VERSION, XMLNS, XSI, VersionBase
from .exceptions import NotEnoughInputArguments, OpenSCENARIOVersionError
from .position import _PositionFactory, _PositionType
from .storyboard import StoryBoard
from .utils import (
    Catalog,
    FileHeader,
    License,
    ParameterDeclarations,
    Properties,
    TrafficSignalController,
    VariableDeclarations,
    find_mandatory_field,
)


class Scenario(VersionBase):
    """The Scenario class collects all parts of OpenScenario and creates a .xml
    file.

    Parameters
    ----------
    header : FileHeader
        The header of the scenario file.
    parameters : ParameterDeclarations
        The parameters to be used in the scenario.
    entities : Entities
        The entities in the scenario.
    storyboard : StoryBoard
        The storyboard of the scenario.
    roadnetwork : RoadNetwork
        The roadnetwork of the scenario.
    catalog : Catalog
        The catalogs used in the scenario.
    osc_minor_version : int, optional
        Used to set if another than the newest version of
        OpenSCENARIO should be used. Default is 2.
    license : License, optional
        Optional license to the file header. Default is None.
    creation_date : datetime.datetime, optional
        Optional creation date of the scenario. Default is None
        (will be at the time of generation).

    Attributes
    ----------
    header : FileHeader
        The header of the scenario file.
    parameters : ParameterDeclarations
        The parameters to be used in the scenario.
    entities : Entities
        The entities in the scenario.
    storyboard : StoryBoard
        The storyboard of the scenario.
    roadnetwork : RoadNetwork
        The roadnetwork of the scenario.
    catalog : Catalog
        The catalogs used in the scenario.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns
        an instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    write_xml(filename)
        Writes an OpenScenario XML file.
    """

    _XMLNS = XMLNS
    _XSI = XSI

    def __init__(
        self,
        name: str,
        author: str,
        parameters: ParameterDeclarations,
        entities: Entities,
        storyboard: StoryBoard,
        roadnetwork: "RoadNetwork",
        catalog: Catalog,
        osc_minor_version: int = _MINOR_VERSION,
        license: Optional[License] = None,
        creation_date: Optional[datetime.datetime] = None,
        header_properties: Optional[Properties] = None,
        variable_declaration: Optional[VariableDeclarations] = None,
    ) -> None:
        """Initializes the Scenario class and creates the header.

        Parameters
        ----------
        name : str
            Name of the scenario.
        author : str
            The author of the scenario.
        parameters : ParameterDeclarations
            The parameters to be used in the scenario.
        entities : Entities
            The entities in the scenario.
        storyboard : StoryBoard
            The storyboard of the scenario.
        roadnetwork : RoadNetwork
            The roadnetwork of the scenario.
        catalog : Catalog
            The catalogs used in the scenario.
        osc_minor_version : int, optional
            Used to set if another than the newest version of
            OpenSCENARIO should be used. Default is 1.
        license : License, optional
            Optional license to the file header (valid from OSC
            V1.1). Default is None.
        creation_date : datetime.datetime, optional
            Optional creation date of the scenario. Default is
            None (will be at the time of generation).
        header_properties : Properties, optional
            Properties that can be added to the header (valid
            from OSC V1.2). Default is None.
        variable_declaration : VariableDeclarations, optional
            Variable declarations (valid from OSC V1.2).
        """
        if not isinstance(entities, Entities):
            raise TypeError("entities input is not of type Entities")
        if not isinstance(storyboard, StoryBoard):
            raise TypeError("storyboard input is not of type StoryBoard")
        if not isinstance(roadnetwork, RoadNetwork):
            raise TypeError("roadnetwork input is not of type RoadNetwork")
        if not isinstance(catalog, Catalog):
            raise TypeError("catalog input is not of type StorCatalogyBoard")
        if not isinstance(parameters, ParameterDeclarations):
            raise TypeError(
                "parameters input is not of type ParameterDeclarations"
            )

        if variable_declaration and not isinstance(
            variable_declaration, VariableDeclarations
        ):
            raise TypeError(
                "variable_declaration input is not of type VariableDeclarations"
            )
        self.variable_declaration = variable_declaration
        self.entities = entities
        self.storyboard = storyboard
        self.roadnetwork = roadnetwork
        self.catalog = catalog
        self.parameters = parameters
        self.header = FileHeader(
            author,
            name,
            revMinor=osc_minor_version,
            license=license,
            creation_date=creation_date,
            properties=header_properties,
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Scenario):
            if (
                self.entities == other.entities
                and self.storyboard == other.storyboard
                and self.roadnetwork == other.roadnetwork
                and self.catalog == other.catalog
                and self.header == other.header
                and self.parameters == other.parameters
                and self.variable_declaration == other.variable_declaration
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "Scenario":
        """Parses the XML element of Scenario.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A Scenario element (same as generated by the class
            itself).

        Returns
        -------
        Scenario
            A Scenario object.
        """
        header = FileHeader.parse(find_mandatory_field(element, "FileHeader"))
        parameters = ParameterDeclarations()
        if element.find("ParameterDeclarations") is not None:
            parameters = ParameterDeclarations.parse(
                find_mandatory_field(element, "ParameterDeclarations")
            )
        catalog = Catalog.parse(
            find_mandatory_field(element, "CatalogLocations")
        )
        storyboard = StoryBoard.parse(
            find_mandatory_field(element, "Storyboard")
        )
        entities = Entities.parse(find_mandatory_field(element, "Entities"))
        roadnetwork = RoadNetwork.parse(
            find_mandatory_field(element, "RoadNetwork")
        )

        variables = None
        if element.find("VariableDeclarations") is not None:
            variables = VariableDeclarations.parse(
                find_mandatory_field(element, "VariableDeclarations")
            )
        return Scenario(
            header.description,
            header.author,
            parameters,
            entities,
            storyboard,
            roadnetwork,
            catalog,
            license=header.license,
            osc_minor_version=header.version_minor,
            header_properties=header.properties,
            variable_declaration=variables,
        )

    def get_element(self) -> ET.Element:
        """Returns the ElementTree of the Scenario.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the Scenario.
        """
        element = ET.Element(
            "OpenSCENARIO",
            attrib={
                "xmlns:xsi": self._XMLNS,
                "xsi:noNamespaceSchemaLocation": self._XSI,
            },
        )
        element.append(self.header.get_element())
        if self.parameters.get_element():
            element.append(self.parameters.get_element())
        if self.variable_declaration:
            element.append(self.variable_declaration.get_element())

        element.append(self.catalog.get_element())
        element.append(self.roadnetwork.get_element())
        element.append(self.entities.get_element())
        element.append(self.storyboard.get_element())

        return element

    def write_xml(
        self, filename: str, prettyprint: bool = True, encoding: str = "utf-8"
    ) -> None:
        """Writes the OpenSCENARIO XML file.

        Parameters
        ----------
        filename : str
            Path and filename of the desired XML file.
        prettyprint : bool, optional
            Pretty print or ugly print? Default is True.
        encoding : str, optional
            Specifies the output encoding. Default is 'utf-8'.
        """
        printToFile(self.get_element(), filename, prettyprint, encoding)


class RoadNetwork(VersionBase):
    """The RoadNetwork class creates the RoadNetwork of the OpenScenario.

    Parameters
    ----------
    roadfile : str, optional
        Path to the OpenDRIVE file.
    scenegraph : str, optional
        Path to the OpenSceneGraph file.

    Attributes
    ----------
    road_file : str
        Path to the OpenDRIVE file.
    scene : str
        Path to the OpenSceneGraph file.
    traffic_signals : list of TrafficSignalController
        All traffic signals in the roadnetwork.
    used_area_positions : list of Positions
        The positions that determine the used area of the
        roadnetwork.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns
        an instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(
        self, roadfile: Optional[str] = None, scenegraph: Optional[str] = None
    ) -> None:
        """Initializes the RoadNetwork.

        Parameters
        ----------
        roadfile : str, optional
            Path to the OpenDRIVE file. Default is None.
        scenegraph : str, optional
            Path to the OpenSceneGraph file. Default is None.
        """
        self.road_file = roadfile
        self.scene = scenegraph
        self.traffic_signals = []
        self.used_area_positions = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RoadNetwork):
            if (
                self.road_file == other.road_file
                and self.scene == other.scene
                and self.traffic_signals == other.traffic_signals
                and self.used_area_positions == other.used_area_positions
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RoadNetwork":
        """Parses the XML element of RoadNetwork.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A RoadNetwork element (same as generated by the class
            itself).

        Returns
        -------
        RoadNetwork
            A RoadNetwork object.
        """
        logicFile = None
        if element.find("LogicFile") is not None:
            logicFile = find_mandatory_field(element, "LogicFile").attrib[
                "filepath"
            ]

        sceneGraphFile = None
        if element.find("SceneGraphFile") is not None:
            sceneGraphFile = find_mandatory_field(
                element, "SceneGraphFile"
            ).attrib["filepath"]

        roadnetwork = RoadNetwork(
            roadfile=logicFile, scenegraph=sceneGraphFile
        )

        position_elements = element.findall("UsedArea/Position")
        if position_elements is not None:
            for position in position_elements:
                roadnetwork.add_used_area_position(
                    _PositionFactory.parse_position(position)
                )

        tsc_elements = element.findall(
            "TrafficSignals/TrafficSignalController"
        )
        if tsc_elements is not None:
            for tsc_element in tsc_elements:
                controller = TrafficSignalController.parse(tsc_element)
                roadnetwork.add_traffic_signal_controller(controller)

        return roadnetwork

    def add_traffic_signal_controller(
        self, traffic_signal_controller: TrafficSignalController
    ) -> "RoadNetwork":
        """Adds a TrafficSignalController to the RoadNetwork.

        Parameters
        ----------
        traffic_signal_controller : TrafficSignalController
            The traffic signal controller to add.
        """
        if not isinstance(traffic_signal_controller, TrafficSignalController):
            raise TypeError(
                "traffic_signal_controller input is not of type TrafficSignalController"
            )
        self.traffic_signals.append(traffic_signal_controller)
        return self

    def add_used_area_position(self, position: _PositionType) -> "RoadNetwork":
        """Adds a position to determine the used area of the roadnetwork. This
        feature was added in OpenSCENARIO V1.1. At least 2 positions are
        required.

        Parameters
        ----------
        position : *Position
            Any position to determine the used area.
        """
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not a valid position Type")
        self.used_area_positions.append(position)
        return self

    def get_element(self) -> ET.Element:
        """Returns the ElementTree of the RoadNetwork.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the RoadNetwork.
        """
        roadnetwork = ET.Element("RoadNetwork")
        if self.road_file:
            ET.SubElement(
                roadnetwork, "LogicFile", {"filepath": self.road_file}
            )
        if self.scene:
            ET.SubElement(
                roadnetwork, "SceneGraphFile", {"filepath": self.scene}
            )
        if self.traffic_signals:
            trafsign_element = ET.SubElement(roadnetwork, "TrafficSignals")
            for ts in self.traffic_signals:
                trafsign_element.append(ts.get_element())
        if len(self.used_area_positions) == 1:
            raise NotEnoughInputArguments(
                'To use "usedArea" more than 1 used_area_position is needed.'
            )
        if len(self.used_area_positions) > 1 and self.isVersion(minor=0):
            raise OpenSCENARIOVersionError(
                "UsedArea is not supported in OpenSCENARIO V1.0, "
                "was introduced in OpenSCENARIO V1.1"
            )
        if len(self.used_area_positions) > 1 and not self.isVersion(minor=0):
            usedarea = ET.SubElement(roadnetwork, "UsedArea")
            for p in self.used_area_positions:
                usedarea.append(p.get_element())

        return roadnetwork
