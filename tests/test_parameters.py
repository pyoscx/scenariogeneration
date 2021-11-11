from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint

def test_range():
    r1 = OSC.Range(0,1)
    r2 = OSC.Range(0,1)
    r3 = OSC.Range(0,1.1)
    prettyprint(r1)
    assert r1 == r2
    assert r1 != r3


def test_stocastic():
    nd = OSC.NormalDistribution(0,1)
    stoc = OSC.Stocastic(100,1.234)
    stoc.add_distribution('myparam1',nd)
    
    stoc2 = OSC.Stocastic(100,1.234)
    stoc2.add_distribution('myparam1',nd)
    
    stoc3 = OSC.Stocastic(100,1.234)
    stoc3.add_distribution('myparam1',nd)
    stoc3.add_distribution('myparam2',nd)
    prettyprint(stoc)
    prettyprint(stoc3)

    assert stoc == stoc2
    assert stoc != stoc3

def test_normaldistribution():
    nd = OSC.NormalDistribution(0,1)
    nd2 = OSC.NormalDistribution(0,1)
    nd3 = OSC.NormalDistribution(0,1,OSC.Range(0,1))
    prettyprint(nd)
    prettyprint(nd3)
    assert nd == nd2
    assert nd != nd3

def test_poissondistribution():
    pd = OSC.PoissonDistribution(1)
    pd2 = OSC.PoissonDistribution(1)
    pd3 = OSC.PoissonDistribution(1,OSC.Range(0,1))
    prettyprint(pd)
    prettyprint(pd3)
    assert pd == pd2
    assert pd != pd3

def test_histogrambin():
    hb = OSC.parameters._HistogramBin(1,OSC.Range(0,1))
    hb2 = OSC.parameters._HistogramBin(1,OSC.Range(0,1))
    hb3 = OSC.parameters._HistogramBin(1,OSC.Range(0,2))
    assert hb == hb2
    assert hb != hb3
    prettyprint(hb)
    
def test_histogram():
    h = OSC.Histogram()
    h.add_bin(1,OSC.Range(0,1))
    h2 = OSC.Histogram()
    h2.add_bin(1,OSC.Range(0,1))
    h3 = OSC.Histogram()
    h3.add_bin(1,OSC.Range(0,1))
    h3.add_bin(2,OSC.Range(1,2))
    prettyprint(h)
    prettyprint(h3)
    assert h == h2
    assert h != h3
    

def test_element():
    e = OSC.parameters._ProbabilityDistributionSetElement('112.1',12)
    e2 = OSC.parameters._ProbabilityDistributionSetElement('112.1',12)
    e3 = OSC.parameters._ProbabilityDistributionSetElement('112.2',12)
    prettyprint(e)
    assert e == e2
    assert e != e3


def test_parameter_set():
    pvs = OSC.ParameterValueSet()
    pvs.add_parameter('myparam1','1')
    pvs2 = OSC.ParameterValueSet()
    pvs2.add_parameter('myparam1','1')
    pvs3 = OSC.ParameterValueSet()
    pvs3.add_parameter('myparam1','1')
    pvs3.add_parameter('myparam1','2')
    prettyprint(pvs)
    prettyprint(pvs3)
    assert pvs == pvs2
    assert pvs != pvs3


def test_probabilitydistributionset():
    pds = OSC.ProbabilityDistributionSet()
    pds.add_set('12',2)
    pds2 = OSC.ProbabilityDistributionSet()
    pds2.add_set('12',2)
    pds3 = OSC.ProbabilityDistributionSet()
    pds3.add_set('12',2)
    pds3.add_set('13',3)
    prettyprint(pds)
    prettyprint(pds3)
    assert pds == pds2
    assert pds != pds3


def test_distributionrange():
    dr = OSC.DistributionRange(1,OSC.Range(0,3))
    dr2 = OSC.DistributionRange(1,OSC.Range(0,3))
    dr3 = OSC.DistributionRange(2,OSC.Range(0,3))
    dr4 = OSC.DistributionRange(1,OSC.Range(0,4))
    prettyprint(dr)
    assert dr == dr2
    assert dr != dr3
    assert dr != dr4
    
def test_distributionset():
    ds = OSC.DistributionSet()
    ds.add_value('1')
    ds2 = OSC.DistributionSet()
    ds2.add_value('1')
    ds3 = OSC.DistributionSet()
    ds3.add_value('1')
    ds3.add_value('2')
    prettyprint(ds3)
    assert ds == ds2
    assert ds != ds3

def test_DeterministicMultiParameterDistribution():
    pvs = OSC.ParameterValueSet()
    pvs.add_parameter('myparam1','1')
    pvs2 = OSC.ParameterValueSet()
    pvs2.add_parameter('myparam1','2')

    dist = OSC.DeterministicMultiParameterDistribution()
    dist.add_value_set(pvs)

    dist2 = OSC.DeterministicMultiParameterDistribution()
    dist2.add_value_set(pvs)

    dist3 = OSC.DeterministicMultiParameterDistribution()
    dist3.add_value_set(pvs2)
    prettyprint(dist)
    assert dist == dist2
    assert dist != dist3
    

def test_deterministic():
    pvs = OSC.ParameterValueSet()
    pvs.add_parameter('myparam1','1')
    dr = OSC.DistributionRange(1,OSC.Range(0,3))
    
    dist = OSC.DeterministicMultiParameterDistribution()
    dist.add_value_set(pvs)

    det = OSC.Deterministic()
    det.add_multi_distribution(dist)

    det.add_single_distribution('myparam',dr)

    det2 = OSC.Deterministic()
    det2.add_multi_distribution(dist)

    det2.add_single_distribution('myparam',dr)

    det3 = OSC.Deterministic()
    det3.add_multi_distribution(dist)
    prettyprint(det)
    assert det == det2
    assert det != det3
    

def test_declaration_with_stocastic():
    nd = OSC.NormalDistribution(0,1)
    stoc = OSC.Stocastic(100,1.234)
    stoc.add_distribution('myparam1',nd)
    pvd = OSC.ParameterValueDistribution('my_parametrization','Mandolin','my_test.xosc',stoc)

    pvd2 = OSC.ParameterValueDistribution('my_parametrization','Mandolin','my_test.xosc',stoc)

    pvd3 = OSC.ParameterValueDistribution('my_parametrization','Mandolin','my_test2.xosc',stoc)
    stoc2 = OSC.Stocastic(100,1.234)
    stoc2.add_distribution('myparam',nd)
    pvd4 = OSC.ParameterValueDistribution('my_parametrization','Mandolin','my_test.xosc',stoc2)

    prettyprint(pvd)
    assert pvd == pvd2
    assert pvd != pvd3
    assert pvd != pvd4

