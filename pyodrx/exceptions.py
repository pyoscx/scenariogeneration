


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