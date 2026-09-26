"""Tests for the modular relief-type registry."""
from app.rules import get_handler, is_supported, list_supported_relief_types
from app.schemas.rules import ReliefType


def test_both_launch_relief_types_are_registered():
    supported = list_supported_relief_types()
    assert ReliefType.CANNABIS_EXPUNGEMENT in supported
    assert ReliefType.CRIMINAL_RECORD_EXPUNGEMENT in supported


def test_unknown_relief_type_is_not_supported():
    assert not is_supported(ReliefType.UNKNOWN)
    assert get_handler(ReliefType.UNKNOWN) is None


def test_registered_handlers_are_callable():
    for relief_type in list_supported_relief_types():
        handler = get_handler(relief_type)
        assert callable(handler)
