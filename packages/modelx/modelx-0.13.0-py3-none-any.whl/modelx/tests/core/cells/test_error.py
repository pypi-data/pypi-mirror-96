from textwrap import dedent
import pytest

import modelx as mx
from modelx.core.errors import NoneReturnedError
from modelx.testing.testutil import SuppressFormulaError

# --------------------------------------------------------------------------
# Test errors


def test_none_returned_error():

    errfunc = dedent(
        """\
        def return_none(x, y):
            return None"""
    )

    space = mx.new_model(name="ErrModel").new_space(name="ErrSpace")
    cells = space.new_cells(formula=errfunc)
    cells.allow_none = False

    with SuppressFormulaError():
        with pytest.raises(NoneReturnedError) as errinfo:
            cells(1, 3)

    errmsg = "ErrModel.ErrSpace.return_none(x=1, y=3)"
    assert errinfo.value.args[0] == errmsg

    with pytest.raises(mx.core.system.FormulaError) as errinfo:
        cells(1, 3)

    errmsg = dedent("""\
        Error raised during formula execution
        modelx.core.errors.NoneReturnedError: ErrModel.ErrSpace.return_none(x=1, y=3)
        
        Formula traceback:
        0: ErrModel.ErrSpace.return_none(x=1, y=3)
        
        Formula source:
        def return_none(x, y):
            return None
        """)

    assert errinfo.value.args[0] == errmsg


def test_zerodiv():

    zerodiv = dedent(
        """\
        def zerodiv(x):
            if x == 3:
                return x / 0
            else:
                return zerodiv(x + 1)"""
    )

    space = mx.new_model().new_space(name="ZeroDiv")
    cells = space.new_cells(formula=zerodiv)

    with SuppressFormulaError():
        with pytest.raises(ZeroDivisionError):
            cells(0)


# --------------------------------------------------------------------------
# Test graph clean-up upon error

def test_trace_cleanup_value_error():

    @mx.defcells
    def foo(i):
        import datetime
        return foo(i - 1).replace(
            month=foo(i - 1).month + 1) if i > 0 else datetime.date(2016, 1, 1)

    with SuppressFormulaError():
        with pytest.raises(ValueError):
            foo(20)

    assert foo._impl.check_sanity()
    assert len(foo) == 12


def test_trace_cleanup_type_error():

    @mx.defcells
    def foo(i):
        if i > 0:
            return foo(i - 1) + (1 if i < 2 else "error")
        else:
            return 0

    with SuppressFormulaError():
        with pytest.raises(TypeError):
            foo(2)

    assert foo._impl.check_sanity()
    assert len(foo) == 2




