import pytest

pytest.importorskip("celery")

from celery import Celery


@pytest.fixture
def celery(sentry_init):
    sentry_init(integrations=["celery"])
    celery = Celery(__name__)
    celery.conf.CELERY_ALWAYS_EAGER = True
    return celery


def test_simple(capture_events, celery):

    events = capture_events()

    @celery.task(name="dummy_task")
    def dummy_task(x, y):
        return x / y

    dummy_task.delay(1, 2)
    dummy_task.delay(1, 0)
    event, = events
    assert event["transaction"] == "dummy_task"

    exception, = event["exception"]["values"]
    assert exception["type"] == "ZeroDivisionError"


def test_ignore_expected(capture_events, celery):
    events = capture_events()

    @celery.task(name="dummy_task", throws=(ZeroDivisionError,))
    def dummy_task(x, y):
        return x / y

    dummy_task.delay(1, 2)
    dummy_task.delay(1, 0)
    assert not events
