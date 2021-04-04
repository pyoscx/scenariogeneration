""" Some custom exceptions

"""


class NotSameAmountOfLanesError(Exception):
    """ Raised when the amount of Lanes are not the same (used for the automation of linking)
    """
    pass

class NotEnoughInputArguments(Exception):
    """ Raised when one of the needed "optional" inputs are not used
    """
    pass

class ToManyOptionalArguments(Exception):
    """ Raised when one of the needed "optional" inputs are not used
    """
    pass

class UndefinedRoadNetwork(Exception):
    """ Raised when the user haven't connected the roads in a correct way
    """
    pass

class RoadsAndLanesNotAdjusted(Exception):
    """ Raised when the user tries to perform an action on non-adjusted lanes and roads that requires adjusted lanes and roads
    """
    pass

class MixOfGeometryAddition(Exception):
    """ Raise when the wrong way of adding geometires are used for the planview
    """
    pass