"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
from lxml import etree
import os


def prettify(element, encoding=None, xml_declaration=True):
    """Returns a bytes string representing a prettified version of an XML element.

    Parameters:
    ----------
        element (ET.Element): The XML element to prettify.
        encoding (str): The encoding to use for the output, defaults to 'utf-8'.
                        If None, then 'utf-8' will be used as default.

    Returns:
    ----------
        bytes: The prettified XML as bytes string with 4-space indentation.
    """
    if not isinstance(element, ET.Element):
        element = element.get_element()

    if encoding is None:
        encoding = "utf-8"

    # Define a 4-space indent string
    indent_str = "    "

    # Use the etree.Parser class from lxml to specify a custom parser
    parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)

    # Convert the ElementTree element to an lxml etree form
    lxml_element = etree.fromstring(ET.tostring(element, encoding), parser=parser)

    # Replace the CDATA marker with a real CDATA node
    for cdata_marker in lxml_element.xpath('//*[starts-with(text(), "<![CDATA[")]'):
        cdata_content = cdata_marker.text[len("<![CDATA[") : -len("]]>")]
        cdata_marker.text = etree.CDATA(cdata_content)

    # Now generate a 2-space indented pretty_print string (bytes type)
    # and Decode the bytes type pretty_print string to utf-8 encoded string,
    # then replace 2-space indents with 4 spaces
    pretty_print_str = (
        etree.tostring(
            lxml_element,
            pretty_print=True,
            encoding=encoding,
            xml_declaration=xml_declaration,
        )
        .decode(encoding)
        .replace("  ", indent_str)
        # .replace("'", '"') // This was added for geo_reference. Will remove for now since it's causing issues with stacking double quotations
    )

    # Encode the string back into bytes type and return
    return pretty_print_str.encode(encoding)


def prettyprint(element, encoding=None):
    """returns the element prettyfied for writing to file or printing to the commandline

    Parameters
    ----------
        element (Element, or any generation class of scenariogeneration): element to print

        encoding (str): specify the output encoding
            Default: None (works best for printing in terminal on ubuntu atleast)

    """
    print(prettify(element, encoding=encoding).decode())


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
            if os.path.dirname(filename):
                os.makedirs(os.path.dirname(filename), exist_ok=True)
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
