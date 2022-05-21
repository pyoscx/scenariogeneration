"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import pytest
import xml.etree.ElementTree as ET
from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint


def test_range():
    r1 = OSC.Range(0, 1)
    r2 = OSC.Range(0, 1)
    r3 = OSC.Range(0, 1.1)
    prettyprint(r1)
    assert r1 == r2
    assert r1 != r3

    r4 = OSC.Range.parse(r1.get_element())
    assert r4 == r1


def test_Stochastic():
    nd = OSC.NormalDistribution(0, 1)
    stoc = OSC.Stochastic(100, 1.234)
    stoc.add_distribution("myparam1", nd)

    stoc2 = OSC.Stochastic(100, 1.234)
    stoc2.add_distribution("myparam1", nd)

    stoc3 = OSC.Stochastic(100, 1.234)
    stoc3.add_distribution("myparam1", nd)
    stoc3.add_distribution("myparam2", nd)
    prettyprint(stoc)
    prettyprint(stoc3)

    assert stoc == stoc2
    assert stoc != stoc3

    stoc4 = OSC.Stochastic.parse(stoc3.get_element())
    assert stoc4 == stoc3


def test_normaldistribution():
    nd = OSC.NormalDistribution(0, 1)
    nd2 = OSC.NormalDistribution(0, 1)
    nd3 = OSC.NormalDistribution(0, 1, OSC.Range(0, 1))
    prettyprint(nd)
    prettyprint(nd3)
    assert nd == nd2
    assert nd != nd3
    nd4 = OSC.NormalDistribution.parse(nd.get_element())
    assert nd4 == nd
    nd5 = OSC.NormalDistribution.parse(nd3.get_element())
    assert nd5 == nd3


def test_poissondistribution():
    pd = OSC.PoissonDistribution(1)
    pd2 = OSC.PoissonDistribution(1)
    pd3 = OSC.PoissonDistribution(1, OSC.Range(0, 1))
    prettyprint(pd)
    prettyprint(pd3)
    assert pd == pd2
    assert pd != pd3
    pd4 = OSC.PoissonDistribution.parse(pd.get_element())
    assert pd4 == pd
    pd5 = OSC.PoissonDistribution.parse(pd3.get_element())
    assert pd5 == pd3


def test_histogrambin():
    hb = OSC.parameters._HistogramBin(1, OSC.Range(0, 1))
    hb2 = OSC.parameters._HistogramBin(1, OSC.Range(0, 1))
    hb3 = OSC.parameters._HistogramBin(1, OSC.Range(0, 2))
    assert hb == hb2
    assert hb != hb3
    prettyprint(hb)

    hb4 = OSC.parameters._HistogramBin.parse(hb.get_element())
    assert hb4 == hb


def test_histogram():
    h = OSC.Histogram()
    h.add_bin(1, OSC.Range(0, 1))
    h2 = OSC.Histogram()
    h2.add_bin(1, OSC.Range(0, 1))
    h3 = OSC.Histogram()
    h3.add_bin(1, OSC.Range(0, 1))
    h3.add_bin(2, OSC.Range(1, 2))
    # prettyprint(h)
    prettyprint(h3, None)
    assert h == h2
    assert h != h3
    h4 = OSC.Histogram.parse(h3.get_element())
    assert h4 == h3


def test_uniformdist():
    ud = OSC.UniformDistribution(OSC.Range(0, 1))
    ud2 = OSC.UniformDistribution(OSC.Range(0, 1))
    ud3 = OSC.UniformDistribution(OSC.Range(0, 2))
    prettyprint(ud)
    assert ud == ud2
    assert ud != ud3
    ud4 = OSC.UniformDistribution.parse(ud.get_element())
    assert ud == ud4


def test_element():
    e = OSC.parameters._ProbabilityDistributionSetElement("112.1", 12)
    e2 = OSC.parameters._ProbabilityDistributionSetElement("112.1", 12)
    e3 = OSC.parameters._ProbabilityDistributionSetElement("112.2", 12)
    prettyprint(e)
    assert e == e2
    assert e != e3
    e4 = OSC.parameters._ProbabilityDistributionSetElement.parse(e.get_element())
    assert e4 == e


def test_parameter_set():
    pvs = OSC.ParameterValueSet()
    pvs.add_parameter("myparam1", "1")
    pvs2 = OSC.ParameterValueSet()
    pvs2.add_parameter("myparam1", "1")
    pvs3 = OSC.ParameterValueSet()
    pvs3.add_parameter("myparam1", "1")
    pvs3.add_parameter("myparam1", "2")
    prettyprint(pvs)
    prettyprint(pvs3)
    assert pvs == pvs2
    assert pvs != pvs3
    pvs4 = OSC.ParameterValueSet.parse(pvs3.get_element())
    assert pvs4 == pvs3


def test_probabilitydistributionset():
    pds = OSC.ProbabilityDistributionSet()
    pds.add_set("12", 2)
    pds2 = OSC.ProbabilityDistributionSet()
    pds2.add_set("12", 2)
    pds3 = OSC.ProbabilityDistributionSet()
    pds3.add_set("12", 2)
    pds3.add_set("13", 3)
    prettyprint(pds)
    prettyprint(pds3)
    assert pds == pds2
    assert pds != pds3
    pds4 = OSC.ProbabilityDistributionSet.parse(pds3.get_element())
    assert pds4 == pds3


def test_distributionrange():
    dr = OSC.DistributionRange(1, OSC.Range(0, 3))
    dr2 = OSC.DistributionRange(1, OSC.Range(0, 3))
    dr3 = OSC.DistributionRange(2, OSC.Range(0, 3))
    dr4 = OSC.DistributionRange(1, OSC.Range(0, 4))
    prettyprint(dr)
    assert dr == dr2
    assert dr != dr3
    assert dr != dr4
    dr5 = OSC.DistributionRange.parse(dr.get_element())
    assert dr5 == dr


def test_distributionset():
    ds = OSC.DistributionSet()
    ds.add_value("1")
    ds2 = OSC.DistributionSet()
    ds2.add_value("1")
    ds3 = OSC.DistributionSet()
    ds3.add_value("1")
    ds3.add_value("2")
    prettyprint(ds3)
    assert ds == ds2
    assert ds != ds3
    ds4 = OSC.DistributionSet.parse(ds3.get_element())
    assert ds3 == ds4


def test_DeterministicMultiParameterDistribution():
    pvs = OSC.ParameterValueSet()
    pvs.add_parameter("myparam1", "1")
    pvs2 = OSC.ParameterValueSet()
    pvs2.add_parameter("myparam1", "2")

    dist = OSC.DeterministicMultiParameterDistribution()
    dist.add_value_set(pvs)

    dist2 = OSC.DeterministicMultiParameterDistribution()
    dist2.add_value_set(pvs)

    dist3 = OSC.DeterministicMultiParameterDistribution()
    dist3.add_value_set(pvs)
    dist3.add_value_set(pvs2)
    prettyprint(dist3, None)
    assert dist == dist2
    assert dist != dist3
    dist4 = OSC.DeterministicMultiParameterDistribution.parse(dist3.get_element())
    prettyprint(dist4, None)
    assert dist4 == dist3


def test_deterministic():
    pvs = OSC.ParameterValueSet()
    pvs.add_parameter("myparam1", "1")
    dr = OSC.DistributionRange(1, OSC.Range(0, 3))

    dist = OSC.DeterministicMultiParameterDistribution()
    dist.add_value_set(pvs)

    det = OSC.Deterministic()
    det.add_multi_distribution(dist)

    det.add_single_distribution("myparam", dr)

    det2 = OSC.Deterministic()
    det2.add_multi_distribution(dist)

    det2.add_single_distribution("myparam", dr)

    det3 = OSC.Deterministic()
    det3.add_multi_distribution(dist)
    prettyprint(det)
    assert det == det2
    assert det != det3
    det4 = OSC.Deterministic.parse(det.get_element())
    assert det4 == det


def test_declaration_with_Stochastic():
    nd = OSC.NormalDistribution(0, 1)
    stoc = OSC.Stochastic(100, 1.234)
    stoc.add_distribution("myparam1", nd)
    pvd = OSC.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test.xosc", stoc
    )

    pvd2 = OSC.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test.xosc", stoc
    )

    pvd3 = OSC.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test2.xosc", stoc
    )
    stoc2 = OSC.Stochastic(100, 1.234)
    stoc2.add_distribution("myparam", nd)
    pvd4 = OSC.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test.xosc", stoc2
    )

    prettyprint(pvd)
    assert pvd == pvd2
    assert pvd != pvd3
    assert pvd != pvd4

    pvd5 = OSC.ParameterValueDistribution.parse(pvd.get_element())
    assert pvd == pvd5


def test_declaration_with_deterministic():
    pvs = OSC.ParameterValueSet()
    pvs.add_parameter("myparam1", "1")
    dist = OSC.DeterministicMultiParameterDistribution()
    dist.add_value_set(pvs)

    det = OSC.Deterministic()
    det.add_multi_distribution(dist)

    pvd = OSC.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test.xosc", det
    )

    pvd2 = OSC.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test.xosc", det
    )

    pvd3 = OSC.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test2.xosc", det
    )
    stoc2 = OSC.Stochastic(100, 1.234)
    stoc2.add_distribution("myparam", OSC.NormalDistribution(0, 1))
    pvd4 = OSC.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test.xosc", stoc2
    )

    prettyprint(pvd)
    assert pvd == pvd2
    assert pvd != pvd3
    assert pvd != pvd4
    pvd5 = OSC.ParameterValueDistribution.parse(pvd.get_element())
    assert pvd == pvd5


hist = OSC.Histogram()
hist.add_bin(4.1, OSC.Range(1, 2))
prob = OSC.ProbabilityDistributionSet()
prob.add_set("2", 0.3)


@pytest.mark.parametrize(
    "distribution",
    [
        OSC.NormalDistribution(1, 2),
        OSC.UniformDistribution(OSC.Range(3, 5)),
        OSC.PoissonDistribution(3),
        hist,
        prob,
    ],
)
def test_Stochastic_factory(distribution):
    element = ET.Element("StochasticDistribution")
    element.append(distribution.get_element())
    prettyprint(element, None)
    factoryoutput = OSC.parameters._StochasticFactory.parse_distribution(element)

    prettyprint(factoryoutput)
    assert distribution == factoryoutput


dist_set = OSC.DistributionSet()
dist_set.add_value("hej")
dist_set.add_value("what")


@pytest.mark.parametrize(
    "distribution", [OSC.DistributionRange(10, OSC.Range(0, 10)), dist_set]
)
def test_deterministic_factory(distribution):
    element = ET.Element("DeterministicSingleParameterDistribution")
    element.append(distribution.get_element())
    prettyprint(element, None)
    factoryoutput = OSC.parameters._DeterministicFactory.parse_distribution(element)

    prettyprint(factoryoutput)
    assert distribution == factoryoutput
