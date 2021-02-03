"""
Test script to create a straight road with a signal at an arbitrary s-coordinate.
"""
import pyodrx


def test_signal():
    signal1 = pyodrx.Signal(s=10.0, t=2, dynamic="no", orientation="+", zOffset=0.00, country="US", Type="R1",
                            subtype="1", value=0.00)
    signals = pyodrx.Signals()
    signals.add_signal(signal1)
    road = pyodrx.create_straight_road(0, signals=signals)
    pyodrx.prettyprint(road.get_element())
