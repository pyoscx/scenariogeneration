"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""


class NotSameAmountOfLanesError(Exception):
    """Raised when the amount of Lanes are not the same (used for the automation of linking)"""

    pass


class NotEnoughInputArguments(Exception):
    """Raised when one of the needed "optional" inputs are not used"""

    pass


class ToManyOptionalArguments(Exception):
    """Raised when one of the needed "optional" inputs are not used"""

    pass


class UndefinedRoadNetwork(Exception):
    """Raised when the user haven't connected the roads in a correct way"""

    pass


class RoadsAndLanesNotAdjusted(Exception):
    """Raised when the user tries to perform an action on non-adjusted lanes and roads that requires adjusted lanes and roads"""

    pass


class MixOfGeometryAddition(Exception):
    """Raise when the wrong way of adding geometires are used for the planview"""

    pass


class GeneralIssueInputArguments(Exception):
    """Raise when there is something wrong in the input arguments"""

    pass


class IdAlreadyExists(Exception):
    """Raise when there is a clash between ids"""

    pass


class RemovedFunctionality(Exception):
    """Raise when a function has been removed"""

    pass
