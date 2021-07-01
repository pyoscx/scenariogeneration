""" Some custom exceptions

"""


class NoActionsDefinedError(Exception):
    """ Raised when no actions are defined in a class
    """
    pass

class NoCatalogFoundError(Exception):
    """ Raised when no catalog is found with the given name
    """
    pass

class OpenSCENARIOVersionError(Exception):
    """ Raised when trying to use features from a newer version of OpenSCENARIO than the desiered version
    """
    pass

class ToManyOptionalArguments(Exception):
    """ Raised when one of the needed "optional" inputs are not used
    """
    pass


class NotEnoughInputArguments(Exception):
    """ Raised when one of the needed "optional" inputs are not used
    """
    pass