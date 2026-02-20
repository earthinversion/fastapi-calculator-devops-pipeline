"""
Unit tests for calculator.py — no browser, no network, runs instantly.
These are the fast tests Jenkins will run on every commit.
"""

import sys
import os
import pytest

# Make src/ importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from calculator import add, subtract, multiply, divide


class TestAdd:
    def test_positive_numbers(self):
        assert add(2, 3) == 5

    def test_negative_numbers(self):
        assert add(-1, -1) == -2

    def test_mixed(self):
        assert add(-1, 3) == 2

    def test_floats(self):
        assert add(0.1, 0.2) == pytest.approx(0.3)


class TestSubtract:
    def test_basic(self):
        assert subtract(5, 3) == 2

    def test_negative_result(self):
        assert subtract(3, 5) == -2


class TestMultiply:
    def test_basic(self):
        assert multiply(4, 3) == 12

    def test_by_zero(self):
        assert multiply(5, 0) == 0


class TestDivide:
    def test_basic(self):
        assert divide(10, 2) == 5

    def test_float_result(self):
        assert divide(1, 3) == pytest.approx(0.333, rel=1e-2)

    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)
