import xmlschema
import os
from scenariogeneration.xosc import OpenSCENARIOVersionError
from enum import Enum, auto


class ValidationResponse(Enum):
    """Enum for MarkRule"""

    OK = auto()
    OSC_VERSION = auto()
    XSD_MISSING = auto()
    XSD_FAILURE = auto()  # should not be asserted as true!
    UNKNOWN_ERROR = auto()


schemas = []
schemas.append(
    xmlschema.XMLSchema(os.path.join("schemas", "OpenSCENARIO_1_" + str(0) + ".xsd"))
)
schemas.append(
    xmlschema.XMLSchema(os.path.join("schemas", "OpenSCENARIO_1_" + str(1) + ".xsd"))
)
schemas.append(
    xmlschema.XMLSchema(os.path.join("schemas", "OpenSCENARIO_1_" + str(2) + ".xsd"))
)


def version_validation(top_element_name, scenariogeneration_object, osc_version=2):
    schema = schemas[osc_version]
    try:
        validator = schema.create_element("Test", type=top_element_name)
    except xmlschema.validators.exceptions.XMLSchemaParseError as e:
        return ValidationResponse.XSD_MISSING
    scenariogeneration_object.setVersion(minor=osc_version)
    try:
        element_to_test = scenariogeneration_object.get_element()
    except OpenSCENARIOVersionError as e:
        return ValidationResponse.OSC_VERSION
    except Exception as e:
        return ValidationResponse.UNKNOWN_ERROR

    try:
        validator.validate(element_to_test)
        return ValidationResponse.OK
    except Exception as e:
        print(e)
        return ValidationResponse.XSD_FAILURE
