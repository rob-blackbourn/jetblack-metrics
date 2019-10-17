"""Tests for monitor"""

from time import sleep
from jetblack_metrics.metrics import Metric, TimedMetric
from jetblack_metrics.monitor import monitor

def test_metric():
    """Test the basic metric"""

    metric = Metric()
    try:
        with monitor(metric):
            1.0 / 0 # pylint: disable=pointless-statement
    except ZeroDivisionError:
        pass
    assert metric.error is not None


def test_timed_metric():
    """Test the timed metric"""

    metric = TimedMetric()
    with monitor(metric):
        sleep(1)
    assert metric.error is None
    assert round(metric.elapsed) >= 1
