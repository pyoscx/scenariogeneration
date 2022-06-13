"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
import xml.dom.minidom as mini


def prettify(element, encoding="utf-8"):
    """prints the element to the commandline

    Parameters
    ----------
        element (Element, or any generation class of scenariogeneration): element to print

        encoding (str): specifies the output encoding
            Default: 'utf-8'

    """
    if not isinstance(element, ET.Element):
        element = element.get_element()
    rough = (
        ET.tostring(element, "utf-8")
        .replace(b"\n", b"")
        .replace(b"\t", b"")
        .replace(b"    ", b"")
    )
    reparsed = mini.parseString(rough)
    return reparsed.toprettyxml(indent="    ", encoding=encoding)


def prettyprint(element, encoding=None):
    """returns the element prettyfied for writing to file or printing to the commandline

    Parameters
    ----------
        element (Element, or any generation class of scenariogeneration): element to print

        encoding (str): specify the output encoding
            Default: None (works best for printing in terminal on ubuntu atleast)

    """
    print(prettify(element, encoding=encoding))


def printToFile(element, filename, prettyprint=True, encoding="utf-8"):
    """prints the element to a xml file

    Parameters
    ----------
        element (Element): element to print

        filename (str): file to save to

        prettyprint (bool): pretty or "ugly" print

        encoding (str): specify the output encoding
            Default: 'utf-8'
    """
    if prettyprint:
        try:
            with open(filename, "wb") as file_handle:
                file_handle.write(prettify(element, encoding=encoding))
        except LookupError:
            print("%s is not a valid encoding option." % encoding)

    else:
        tree = ET.ElementTree(element)
        try:
            tree.write(filename, encoding=encoding)
        except LookupError:
            print("%s is not a valid encoding option." % encoding)


def enum2str(enum):
    """helper to create strings from enums that should contain space but have to have _

    Parameters
    ----------
        enum (Enum): a enum of pyodrx

    Returns
    -------
        enumstr (str): the enum as a string replacing _ with ' '

    """
    return enum.name.replace("_", " ")


def convert_bool(value):
    """Method to transform booleans to correct xml version (lower case)

    Parameter
    ---------
        value (bool): the boolean

    Return
    ------
        boolean (str)
    """
    if isinstance(value, str):
        if value == "true" or value == "1":
            return True
        elif value == "false" or value == "0":
            return False
        elif value[0] == "$":
            return value
        else:
            raise ValueError(
                value
                + "is not a valid type of float input to openscenario, if a string is used as a float value (parameter or expression), it should have a $ as the first char.."
            )

    if value:
        return "true"
    else:
        return "false"
