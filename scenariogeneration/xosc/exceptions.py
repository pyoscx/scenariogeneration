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