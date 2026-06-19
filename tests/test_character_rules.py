from app.core.character_rules import (
    ATTRIBUTE_MAX,
    ATTRIBUTE_MIN,
    ATTRIBUTE_POINTS,
    remaining,
    validate_exact_pool,
)


def test_attribute_pool_valid_when_exactly_spent():
    values = [12, 12, 12, 12, 12]
    assert remaining(values, ATTRIBUTE_MIN, ATTRIBUTE_POINTS) == 0
    ok, message = validate_exact_pool(values, ATTRIBUTE_MIN, ATTRIBUTE_MAX, ATTRIBUTE_POINTS)
    assert ok is True
    assert message == ""


def test_attribute_pool_rejects_unspent_points():
    values = [8, 8, 8, 8, 8]
    ok, message = validate_exact_pool(values, ATTRIBUTE_MIN, ATTRIBUTE_MAX, ATTRIBUTE_POINTS)
    assert ok is False
    assert "reste" in message


def test_attribute_pool_rejects_values_above_max():
    values = [19, 9, 8, 8, 8]
    ok, message = validate_exact_pool(values, ATTRIBUTE_MIN, ATTRIBUTE_MAX, ATTRIBUTE_POINTS)
    assert ok is False
    assert "comprise" in message
