import pytest

from source import calc as cc

class TestArithOp(object):


    def test_add_simple(self):
        obs = cc.arith_op(3,2, '+')
        assert 5 == obs


    @pytest.mark.parametrize("n1, n2, op, exp", [
        (9, 2, '+', 11),
        (19, 2, '-', 17),
        ])
    def test_sub_multi(self, n1, n2, op, exp):
        obs = cc.arith_op(n1, n2, op)
        assert exp == obs

    def test_type_error(self):
        with pytest.raises(TypeError):
            cc.arith_op('3',1,'+')
    
    def test_type_Implementation(self):
        with pytest.raises(NotImplementedError):
            cc.arith_op('3',1,'/')
    
    @pytest.mark.parametrize("n1, n2, op, exp_error", [
        ('9', 2, '+',TypeError),
        (19, 2, '/', NotImplementedError),
        ])
    def test_par_error(self, n1, n2, op, exp_error):
        with pytest.raises(exp_error):
            cc.arith_op(n1,n2,op)

class TestCircleArea(object):
    
    def test_approx(self):
        obs = cc.circle_area(1)
        assert obs == pytest.approx(3.14159, rel=1e-6)
