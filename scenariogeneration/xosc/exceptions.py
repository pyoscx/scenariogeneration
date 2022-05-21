"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""


class NoActionsDefinedError(Exception):
    """Raised when no actions are defined in a class"""

    pass


class NoCatalogFoundError(Exception):
    """Raised when no catalog is found with the given name"""

    pass


class OpenSCENARIOVersionError(Exception):
    """Raised when trying to use features from a newer version of OpenSCENARIO than the desiered version"""

    pass


class ToManyOptionalArguments(Exception):
    """Raised when one of the needed "optional" inputs are not used"""

    pass


class NotEnoughInputArguments(Exception):
    """Raised when one of the needed "optional" inputs are not used"""

    pass


class NotAValidElement(Exception):
    """Raised when one of the needed "optional" inputs are not used"""

    pass
