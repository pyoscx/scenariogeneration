"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import os
import xml.etree.ElementTree as ET
from typing import Optional, Union

from lxml import etree


def prettify(
    element: ET.Element,
    encoding: Optional[str] = None,
    xml_declaration: bool = True,
) -> bytes:
    """Returns a bytes string representing a prettified version of an XML
    element.

    Parameters
    ----------
    element : ET.Element
        The XML element to prettify.
    encoding : str, optional
        The encoding to use for the output. Defaults to 'utf-8'. If None,
        'utf-8' will be used as the default.
    xml_declaration : bool, optional
        Whether to include the XML declaration in the output. Default is True.

    Returns
    -------
    bytes
        The prettified XML as a bytes string with 4-space indentation.
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
    lxml_element = etree.fromstring(
        ET.tostring(element, encoding), parser=parser
    )

    # Replace the CDATA marker with a real CDATA node
    for cdata_marker in lxml_element.xpath(
        '//*[starts-with(text(), "<![CDATA[")]'
    ):
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


def prettyprint(element: ET.Element, encoding: Optional[str] = None) -> None:
    """Returns the element prettified for writing to a file or printing to
    the command line.

    Parameters
    ----------
    element : ET.Element
        The XML element to print. Can also be any generation class of
        scenariogeneration.
    encoding : str, optional
        Specify the output encoding. Default is None, which works best for
        printing in the terminal on Ubuntu.

    Returns
    -------
    None
    """
    print(prettify(element, encoding=encoding).decode())


def printToFile(
    element: ET.Element,
    filename: str,
    prettyprint: bool = True,
    encoding: str = "utf-8",
) -> None:
    """Prints the element to an XML file.

    Parameters
    ----------
    element : ET.Element
        The XML element to print.
    filename : str
        The file path to save the XML content.
    prettyprint : bool, optional
        Whether to format the XML with indentation. Default is True.
    encoding : str, optional
        The output encoding to use. Default is 'utf-8'.

    Returns
    -------
    None
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


def enum2str(enum: "Enum") -> str:
    """Helper to create strings from enums that should contain spaces but
    use underscores internally.

    Parameters
    ----------
    enum : Enum
        An enum instance from pyodrx.

    Returns
    -------
    str
        The enum as a string with underscores replaced by spaces.
    """
    return enum.name.replace("_", " ")


def convert_bool(value: Union[bool, str]) -> Union[str, bool]:
    """Transform booleans to the correct XML version (lowercase) or
    validate string inputs.

    Parameters
    ----------
    value : bool or str
        The boolean or string to convert. Strings can represent boolean
        values ("true", "false", "1", "0") or parameterized expressions
        (starting with "$").

    Returns
    -------
    str or bool
        - "true" or "false" if the input is a boolean.
        - True or False if the input is a valid string representation of
          a boolean.
        - The input string if it starts with "$".

    Raises
    ------
    ValueError
        If the input string is not a valid boolean or parameterized value.
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
