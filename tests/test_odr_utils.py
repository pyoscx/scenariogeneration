"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
import pytest


from scenariogeneration import xodr
from scenariogeneration import prettyprint


def test_userdata_no_extras():
    userdata = xodr.UserData("stuffs", "more stuffs")
    userdata2 = xodr.UserData("stuffs", "more stuffs")
    userdata3 = xodr.UserData("stuffs", "less stuff")
    prettyprint(userdata)

    assert userdata == userdata2
    assert userdata2 != userdata3


def test_userdata_with_extras():
    userdata = xodr.UserData("stuffs", "more stuffs")
    userdata.add_userdata_content(ET.Element("extraContent"))
    userdata.add_userdata_content(ET.Element("extraContent2"))
    userdata2 = xodr.UserData("stuffs", "more stuffs")
    userdata2.add_userdata_content(ET.Element("extraContent"))
    userdata2.add_userdata_content(ET.Element("extraContent2"))
    userdata3 = xodr.UserData("stuffs", "more stuffs")
    userdata3.add_userdata_content(ET.Element("otherContent"))
    prettyprint(userdata)

    assert userdata == userdata2
    assert userdata2 != userdata3


def test_data_quality():
    dq = xodr.DataQuality()
    dq.add_error(0.1, 0.2, 0.3, 0.4)
    dq.add_raw_data_info(
        "today", xodr.RawDataPostProcessing.cleaned, xodr.RawDataSource.sensor
    )
    prettyprint(dq)

    dq1 = xodr.DataQuality()
    dq1.add_error(0.1, 0.2, 0.3, 0.4)
    dq1.add_raw_data_info(
        "today", xodr.RawDataPostProcessing.cleaned, xodr.RawDataSource.sensor
    )

    dq2 = xodr.DataQuality()
    dq2.add_error(0.1, 0.2, 0.3, 0.3)
    dq2.add_raw_data_info(
        "today", xodr.RawDataPostProcessing.cleaned, xodr.RawDataSource.sensor
    )

    assert dq == dq1
    assert dq != dq2
