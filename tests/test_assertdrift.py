"""Self-test cases for assertdrift tool."""


def test_low_score_exists():
    """Test with LOW score assertion (existence check)."""
    result = some_function()
    assert result is not None  # LOW: existence check


def test_high_score_exact_value():
    """Test with HIGH score assertion (exact value)."""
    user = get_user()
    assert user.email == "test@example.com"  # HIGH: exact value


def test_zero_score_tautology():
    """Test with ZERO score assertion (tautology)."""
    assert True  # ZERO: tautology


def test_high_score_literal():
    """Test with HIGH score assertion (literal comparison)."""
    result = calculate_sum(2, 3)
    assert result == 5  # HIGH: exact literal value


def some_function():
    return "result"


def get_user():
    class User:
        email = "test@example.com"
    return User()


def calculate_sum(a, b):
    return a + b
