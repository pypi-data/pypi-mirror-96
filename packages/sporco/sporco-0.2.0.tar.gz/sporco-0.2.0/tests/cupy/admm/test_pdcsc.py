from __future__ import division
from builtins import object

import pytest
try:
    import cupy as cp
    try:
        cp.cuda.Device(0).compute_capability
    except cp.cuda.runtime.CUDARuntimeError:
        pytest.skip("GPU device inaccessible", allow_module_level=True)
except ImportError:
    pytest.skip("cupy not installed", allow_module_level=True)

from sporco.cupy.admm import pdcsc
from sporco.cupy.array import list2array



class TestSet01(object):

    def setup_method(self, method):
        cp.random.seed(12345)


    def test_01(self):
        Nr = 16
        Nc = 17
        C = 3
        Nd = 5
        Md = 4
        Mb = 4
        D = cp.random.randn(Nd, Nd, Md)
        B = cp.random.randn(C, Mb)
        s = cp.random.randn(Nr, Nc, C)
        lmbda = 1e-1
        try:
            opt = pdcsc.ConvProdDictBPDN.Options({'LinSolveCheck': True})
            b = pdcsc.ConvProdDictBPDN(D, B, s, lmbda, opt=opt, dimK=0)
            b.solve()
        except Exception as e:
            print(e)
            assert 0
        assert list2array(b.getitstat().XSlvRelRes).max() < 1e-4



    def test_02(self):
        Nr = 16
        Nc = 17
        C = 3
        Nd = 5
        Md = 4
        Mb = 4
        D = cp.random.randn(Nd, Nd, Md)
        B = cp.random.randn(C, Mb)
        s = cp.random.randn(Nr, Nc, C)
        lmbda = 1e-1
        mu = 1e-2
        try:
            opt = pdcsc.ConvProdDictBPDNJoint.Options({'LinSolveCheck': True})
            b = pdcsc.ConvProdDictBPDNJoint(D, B, s, lmbda, mu, opt=opt,
                                            dimK=0)
            b.solve()
        except Exception as e:
            print(e)
            assert 0
        assert list2array(b.getitstat().XSlvRelRes).max() < 1e-4



    def test_03(self):
        Nr = 16
        Nc = 17
        C = 3
        Nd = 5
        Md = 4
        Mb = 4
        D = cp.random.randn(Nd, Nd, Md)
        B = cp.random.randn(C, Mb)
        s = cp.random.randn(Nr, Nc, C)
        lmbda = 1e-1
        mu = 1e-2
        try:
            opt = pdcsc.ConvProdDictL1L1Grd.Options({'LinSolveCheck': True})
            b = pdcsc.ConvProdDictL1L1Grd(D, B, s, lmbda, mu, opt=opt, dimK=0)
            b.solve()
        except Exception as e:
            print(e)
            assert 0
        assert list2array(b.getitstat().XSlvRelRes).max() < 1e-4


    def test_04(self):
        Nr = 16
        Nc = 17
        C = 3
        Nd = 5
        Md = 4
        Mb = 4
        D = cp.random.randn(Nd, Nd, Md)
        B = cp.random.randn(C, Mb)
        s = cp.random.randn(Nr, Nc, C)
        lmbda = 1e-1
        mu = 1e-2
        try:
            opt = pdcsc.ConvProdDictL1L1GrdJoint.Options(
                {'LinSolveCheck': True})
            b = pdcsc.ConvProdDictL1L1GrdJoint(D, B, s, lmbda, mu, opt=opt,
                                               dimK=0)
            b.solve()
        except Exception as e:
            print(e)
            assert 0
        assert list2array(b.getitstat().XSlvRelRes).max() < 1e-4
