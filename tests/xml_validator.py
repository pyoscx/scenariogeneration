import xmlschema
import os
from scenariogeneration.xosc import OpenSCENARIOVersionError
from enum import Enum, auto


class ValidationResponse(Enum):
    """Enum for MarkRule"""

    OK = auto()
    OSC_VERSION = auto()
    XSD_FAILURE = auto() # should not be asserted as true!
    UNKNOWN_ERROR = auto()




def version_validation(top_element_name, scenariogeneration_object, osc_version=2):
    schema = xmlschema.XMLSchema(os.path.join(os.path.split(__file__)[0], os.pardir, "schemas", "OpenSCENARIO_1_" + str(osc_version) + ".xsd"))
    validator = schema.create_element("Test",type=top_element_name)
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
