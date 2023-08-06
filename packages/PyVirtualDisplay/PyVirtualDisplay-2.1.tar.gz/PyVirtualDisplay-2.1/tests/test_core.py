from time import sleep

import pytest

from pyvirtualdisplay import Display
from pyvirtualdisplay.abstractdisplay import XStartError
from pyvirtualdisplay.xephyr import XephyrDisplay
from pyvirtualdisplay.xvfb import XvfbDisplay
from pyvirtualdisplay.xvnc import XvncDisplay
from tutil import has_xvnc, rfbport


def test_virt():
    vd = Display()
    assert vd.return_code is None
    assert not vd.is_alive()
    vd.start()
    assert vd.return_code is None
    assert vd.is_alive()
    vd.stop()
    assert vd.return_code == 0
    assert not vd.is_alive()

    vd = Display().start().stop()
    assert vd.return_code == 0
    assert not vd.is_alive()


def test_nest():
    vd = Display().start()
    assert vd.is_alive()

    nd = Display(visible=True).start().stop()

    assert nd.return_code == 0

    vd.stop()
    assert not vd.is_alive()


def test_disp():
    vd = Display().start()
    assert vd.is_alive()

    # d = Display(visible=True).start().sleep(2).stop()
    # .assertEquals(d.return_code, 0)

    d = Display(visible=False).start().stop()
    assert d.return_code == 0

    vd.stop()
    assert not vd.is_alive()


def test_repr_xvfb():
    display = Display()
    print(repr(display))

    display = Display(visible=False)
    print(repr(display))

    display = Display(backend="xvfb")
    print(repr(display))

    display = XvfbDisplay()
    print(repr(display))


if has_xvnc():

    def test_repr_xvnc():
        display = Display(backend="xvnc", rfbport=rfbport())
        print(repr(display))

        display = XvncDisplay()
        print(repr(display))


def test_repr_xephyr():
    display = Display(visible=True)
    print(repr(display))

    display = Display(backend="xephyr")
    print(repr(display))

    display = XephyrDisplay()
    print(repr(display))


def test_stop_nostart():
    with pytest.raises(XStartError):
        Display().stop()


def test_double_start():
    vd = Display()
    try:
        vd.start()
        with pytest.raises(XStartError):
            vd.start()
    finally:
        vd.stop()


def test_double_stop():
    vd = Display().start().stop()
    assert vd.return_code == 0
    assert not vd.is_alive()
    vd.stop()
    assert vd.return_code == 0
    assert not vd.is_alive()


def test_stop_terminated():
    vd = Display().start()
    assert vd.is_alive()
    vd._obj._subproc.terminate()
    sleep(0.2)
    assert not vd.is_alive()
    vd.stop()
    assert vd.return_code == 0
    assert not vd.is_alive()


def test_no_backend():
    with pytest.raises(ValueError):
        Display(backend="unknown")


def test_color_xvfb():
    with pytest.raises(XStartError):
        Display(color_depth=99).start().stop()
    Display(color_depth=16).start().stop()
    Display(color_depth=24).start().stop()
    Display(color_depth=8).start().stop()


def test_color_xephyr():
    with Display():
        # requested screen depth not supported, setting to match hosts
        Display(backend="xephyr", color_depth=99).start().stop()

        Display(backend="xephyr", color_depth=16).start().stop()
        Display(backend="xephyr", color_depth=24).start().stop()
        Display(backend="xephyr", color_depth=8).start().stop()


if has_xvnc():

    def test_color_xvnc():
        with pytest.raises(XStartError):
            with Display(backend="xvnc", color_depth=99, rfbport=rfbport()):
                pass
        with Display(backend="xvnc", color_depth=16, rfbport=rfbport()):
            pass
        with Display(backend="xvnc", color_depth=24, rfbport=rfbport()):
            pass
        # tigervnc no longer works 8-bit pseudocolors, 18.04 is OK
        # with Display(backend="xvnc", color_depth=8, rfbport=rfbport()):
        #     pass


def test_pid():
    with Display() as d:
        assert d.pid > 0
    with XvfbDisplay() as d:
        assert d.pid > 0


def test_bgcolor():
    Display(bgcolor="black").start().stop()
    Display(bgcolor="white").start().stop()
    with pytest.raises(KeyError):
        Display(bgcolor="green").start().stop()


def test_is_started():
    #     d = Display()
    #     assert not d._is_started
    #     d.start()
    #     assert d._is_started
    #     d.stop()
    #     assert d._is_started

    # with Display() as d:
    #     assert d._is_started
    # assert d._is_started

    with XvfbDisplay() as d:
        assert d._is_started
    assert d._is_started

    with Display():
        with XephyrDisplay() as d:
            assert d._is_started
        assert d._is_started

        # with XvncDisplay() as d:
        #     assert d._is_started
        # assert d._is_started


def test_extra_args():
    # Unrecognized option
    d = Display(extra_args=["willcrash"])
    with pytest.raises(XStartError):
        d.start()

    with Display():
        # -c                     turns off key-click
        with Display(visible=True, extra_args=["-c"]) as d:
            assert d.is_alive()
        assert not d.is_alive()

        with XephyrDisplay(extra_args=["-c"]) as d:
            assert d.is_alive()
        assert not d.is_alive()


def test_display():
    d = Display()
    assert d.display is None
    d.start()
    assert d.display >= 0

    d = XvfbDisplay()
    assert d.display is None
    d.start()
    assert d.display >= 0
