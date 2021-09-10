from scenariogeneration import xosc
from scenariogeneration import prettyprint

def test_range():
    r1 = xosc.Range(0,1)
    r2 = xosc.Range(0,1)
    r3 = xosc.Range(0,1.1)
    prettyprint(r1)
    assert r1 == r2
    assert r1 != r3


def test_stocastic():
    nd = xosc.NormalDistribution(0,1)
    stoc = xosc.Stocastic(100,1.234)
    stoc.add_distribution('myparam1',nd)
    
    stoc2 = xosc.Stocastic(100,1.234)
    stoc2.add_distribution('myparam1',nd)
    
    stoc3 = xosc.Stocastic(100,1.234)
    stoc3.add_distribution('myparam1',nd)
    stoc3.add_distribution('myparam2',nd)
    prettyprint(stoc)
    prettyprint(stoc3)

    assert stoc == stoc2
    assert stoc != stoc3

def test_normaldistribution():
    nd = xosc.NormalDistribution(0,1)
    nd2 = xosc.NormalDistribution(0,1)
    nd3 = xosc.NormalDistribution(0,1,xosc.Range(0,1))
    prettyprint(nd)
    prettyprint(nd3)
    assert nd == nd2
    assert nd != nd3

def test_poissondistribution():
    pd = xosc.PoissonDistribution(1)
    pd2 = xosc.PoissonDistribution(1)
    pd3 = xosc.PoissonDistribution(1,xosc.Range(0,1))
    prettyprint(pd)
    prettyprint(pd3)
    assert pd == pd2
    assert pd != pd3

def test_histogrambin():
    hb = xosc.parameters._HistogramBin(1,xosc.Range(0,1))
    hb2 = xosc.parameters._HistogramBin(1,xosc.Range(0,1))
    hb3 = xosc.parameters._HistogramBin(1,xosc.Range(0,2))
    assert hb == hb2
    assert hb != hb3
    prettyprint(hb)
    
def test_histogram():
    h = xosc.Histogram()
    h.add_bin(1,xosc.Range(0,1))
    h2 = xosc.Histogram()
    h2.add_bin(1,xosc.Range(0,1))
    h3 = xosc.Histogram()
    h3.add_bin(1,xosc.Range(0,1))
    h3.add_bin(2,xosc.Range(1,2))
    prettyprint(h)
    prettyprint(h3)
    assert h == h2
    assert h != h3
    

def test_element():
    e = xosc.parameters._ProbabilityDistributionSetElement('112.1',12)
    e2 = xosc.parameters._ProbabilityDistributionSetElement('112.1',12)
    e3 = xosc.parameters._ProbabilityDistributionSetElement('112.2',12)
    prettyprint(e)
    assert e == e2
    assert e != e3


def test_parameter_set():
    pvs = xosc.ParameterValueSet()
    pvs.add_parameter('myparam1','1')
    pvs2 = xosc.ParameterValueSet()
    pvs2.add_parameter('myparam1','1')
    pvs3 = xosc.ParameterValueSet()
    pvs3.add_parameter('myparam1','1')
    pvs3.add_parameter('myparam1','2')
    prettyprint(pvs)
    prettyprint(pvs3)
    assert pvs == pvs2
    assert pvs != pvs3


def test_probabilitydistributionset():
    pds = xosc.ProbabilityDistributionSet()
    pds.add_set('12',2)
    pds2 = xosc.ProbabilityDistributionSet()
    pds2.add_set('12',2)
    pds3 = xosc.ProbabilityDistributionSet()
    pds3.add_set('12',2)
    pds3.add_set('13',3)
    prettyprint(pds)
    prettyprint(pds3)
    assert pds == pds2
    assert pds != pds3


def test_distributionrange():
    dr = xosc.DistributionRange(1,xosc.Range(0,3))
    dr2 = xosc.DistributionRange(1,xosc.Range(0,3))
    dr3 = xosc.DistributionRange(2,xosc.Range(0,3))
    dr4 = xosc.DistributionRange(1,xosc.Range(0,4))
    prettyprint(dr)
    assert dr == dr2
    assert dr != dr3
    assert dr != dr4
    
def test_distributionset():
    ds = xosc.DistributionSet()
    ds.add_value('1')
    ds2 = xosc.DistributionSet()
    ds2.add_value('1')
    ds3 = xosc.DistributionSet()
    ds3.add_value('1')
    ds3.add_value('2')
    prettyprint(ds3)
    assert ds == ds2
    assert ds != ds3

def test_DeterministicMultiParameterDistribution():
    pvs = xosc.ParameterValueSet()
    pvs.add_parameter('myparam1','1')
    pvs2 = xosc.ParameterValueSet()
    pvs2.add_parameter('myparam1','2')

    dist = xosc.DeterministicMultiParameterDistribution()
    dist.add_value_set(pvs)

    dist2 = xosc.DeterministicMultiParameterDistribution()
    dist2.add_value_set(pvs)

    dist3 = xosc.DeterministicMultiParameterDistribution()
    dist3.add_value_set(pvs2)
    prettyprint(dist)
    assert dist == dist2
    assert dist != dist3
    

def test_deterministic():
    pvs = xosc.ParameterValueSet()
    pvs.add_parameter('myparam1','1')
    dr = xosc.DistributionRange(1,xosc.Range(0,3))
    
    dist = xosc.DeterministicMultiParameterDistribution()
    dist.add_value_set(pvs)

    det = xosc.Deterministic()
    det.add_multi_distribution(dist)

    det.add_single_distribution('myparam',dr)

    det2 = xosc.Deterministic()
    det2.add_multi_distribution(dist)

    det2.add_single_distribution('myparam',dr)

    det3 = xosc.Deterministic()
    det3.add_multi_distribution(dist)
    prettyprint(det)
    assert det == det2
    assert det != det3
    

def test_declaration_with_stocastic():
    nd = xosc.NormalDistribution(0,1)
    stoc = xosc.Stocastic(100,1.234)
    stoc.add_distribution('myparam1',nd)
    pvd = xosc.ParameterValueDistribution('my_parametrization','Mandolin','my_test.xosc',stoc)

    pvd2 = xosc.ParameterValueDistribution('my_parametrization','Mandolin','my_test.xosc',stoc)

    pvd3 = xosc.ParameterValueDistribution('my_parametrization','Mandolin','my_test2.xosc',stoc)
    stoc2 = xosc.Stocastic(100,1.234)
    stoc2.add_distribution('myparam',nd)
    pvd4 = xosc.ParameterValueDistribution('my_parametrization','Mandolin','my_test.xosc',stoc2)

    prettyprint(pvd)
    assert pvd == pvd2
    assert pvd != pvd3
    assert pvd != pvd4
