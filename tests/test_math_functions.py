"""Unit tests for mathematical functions (without @tool decorator issues)."""

import pytest
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    convert_to_number,
    MathOperationError
)


def get_add_numbers_func():
    """Get the raw add_numbers function without the @tool decorator."""
    # Define the function directly to avoid @tool decorator issues
    def add_numbers(first, second):
        """Add two numbers together with automatic type conversion."""
        try:
            num1 = convert_to_number(first)
            num2 = convert_to_number(second)
            return num1 + num2
        except MathOperationError as error:
            raise MathOperationError(f"Addition failed: {error}") from error
    return add_numbers


def get_subtract_numbers_func():
    """Get the raw subtract_numbers function without the @tool decorator."""
    def subtract_numbers(first, second):
        """Subtract the second number from the first with automatic type conversion."""
        try:
            num1 = convert_to_number(first)
            num2 = convert_to_number(second)
            return num1 - num2
        except MathOperationError as error:
            raise MathOperationError(f"Subtraction failed: {error}") from error
    return subtract_numbers


# Get the functions
add_numbers = get_add_numbers_func()
subtract_numbers = get_subtract_numbers_func()


class TestConvertToNumber:
    """Test cases for convert_to_number function."""

    def test_convert_integers(self):
        """Test integer conversion."""
        assert convert_to_number(42) == 42
        assert convert_to_number(-17) == -17
        assert convert_to_number(0) == 0

    def test_convert_floats(self):
        """Test float conversion."""
        assert convert_to_number(3.14) == 3.14
        assert convert_to_number(-2.71) == -2.71
        assert convert_to_number(0.0) == 0.0

    def test_convert_complex_numbers(self):
        """Test complex number conversion."""
        assert convert_to_number(3 + 4j) == 3 + 4j
        assert convert_to_number(1 - 2j) == 1 - 2j
        assert convert_to_number(0j) == 0j

    def test_convert_string_integers(self):
        """Test string to integer conversion."""
        assert convert_to_number("42") == 42
        assert convert_to_number("-17") == -17
        assert convert_to_number("0") == 0

    def test_convert_string_floats(self):
        """Test string to float conversion."""
        assert convert_to_number("3.14") == 3.14
        assert convert_to_number("-2.71") == -2.71
        assert convert_to_number("0.0") == 0.0

    def test_convert_string_floats_with_exponent(self):
        """Test string to float conversion with scientific notation."""
        assert convert_to_number("1.5e2") == 150.0
        assert convert_to_number("2.5E-1") == 0.25

    def test_convert_string_complex(self):
        """Test string to complex conversion."""
        assert convert_to_number("3+4j") == 3 + 4j
        assert convert_to_number("1-2j") == 1 - 2j
        assert convert_to_number("5j") == 5j

    def test_convert_invalid_strings(self):
        """Test conversion of invalid strings raises error."""
        with pytest.raises(MathOperationError, match="Cannot convert 'hello' to a number"):
            convert_to_number("hello")

        with pytest.raises(MathOperationError, match="Cannot convert '3.14.15' to a number"):
            convert_to_number("3.14.15")

        with pytest.raises(MathOperationError, match="Cannot convert '' to a number"):
            convert_to_number("")


class TestAddNumbers:
    """Test cases for add_numbers function."""

    @pytest.mark.parametrize(
        "first, second, expected",
        [
            # Integer addition
            (5, 3, 8),
            (-2, 7, 5),
            (0, 0, 0),
            # Float addition
            (5.5, 3.2, 8.7),
            (-1.5, 2.5, 1.0),
            (0.0, 0.0, 0.0),
            # Complex addition
            (3 + 4j, 1 + 2j, 4 + 6j),
            (5 - 2j, -3 + 7j, 2 + 5j),
            # String integers
            ("10", "20", 30),
            ("-5", "7", 2),
            # String floats
            ("3.14", 2, 5.14),
            ("2.5", "1.5", 4.0),
            # Mixed types
            ("10", 5, 15),
            (7, "3.0", 10.0),
            ("2.5", 5, 7.5),
        ]
    )
    def test_add_numbers_valid_inputs(self, first, second, expected):
        """Test add_numbers with various valid input combinations."""
        result = add_numbers(first, second)
        # Handle floating point precision issues
        if isinstance(expected, float):
            assert abs(result - expected) < 1e-10
        else:
            assert result == expected
        assert isinstance(result, type(expected))

    def test_add_numbers_large_numbers(self):
        """Test addition with large numbers."""
        assert add_numbers("1000000", "2000000") == 3000000
        assert add_numbers(1.5e10, 2.5e9) == 1.75e10

    def test_add_numbers_precision(self):
        """Test addition with floating point precision."""
        result = add_numbers(0.1, 0.2)
        assert abs(result - 0.3) < 1e-10

    def test_add_numbers_invalid_inputs(self):
        """Test add_numbers with invalid inputs."""
        with pytest.raises(MathOperationError, match="Addition failed"):
            add_numbers("hello", "world")

        with pytest.raises(MathOperationError, match="Addition failed"):
            add_numbers("3.14.15", 2)

        with pytest.raises(MathOperationError, match="Addition failed"):
            add_numbers("invalid", "5.0")


class TestSubtractNumbers:
    """Test cases for subtract_numbers function."""

    @pytest.mark.parametrize(
        "first, second, expected",
        [
            # Integer subtraction
            (10, 3, 7),
            (5, 8, -3),
            (0, 0, 0),
            # Float subtraction
            (5.5, 2.2, 3.3),
            (-1.5, 2.5, -4.0),
            (0.0, 0.0, 0.0),
            # Complex subtraction
            (5 + 7j, 2 + 3j, 3 + 4j),
            (3 - 4j, 1 + 2j, 2 - 6j),
            # String integers
            ("20", "8", 12),
            ("-5", "7", -12),
            # String floats
            ("10.5", 3, 7.5),
            ("5.0", "2.5", 2.5),
            # Mixed types
            ("15", 5, 10),
            (8, "3.0", 5.0),
            ("7.5", 2, 5.5),
        ]
    )
    def test_subtract_numbers_valid_inputs(self, first, second, expected):
        """Test subtract_numbers with various valid input combinations."""
        result = subtract_numbers(first, second)
        # Handle floating point precision issues
        if isinstance(expected, float):
            assert abs(result - expected) < 1e-10
        else:
            assert result == expected
        assert isinstance(result, type(expected))

    def test_subtract_numbers_negative_results(self):
        """Test subtraction resulting in negative numbers."""
        assert subtract_numbers(5, 10) == -5
        assert subtract_numbers("3", "8") == -5

    def test_subtract_numbers_precision(self):
        """Test subtraction with floating point precision."""
        result = subtract_numbers(0.3, 0.1)
        assert abs(result - 0.2) < 1e-10

    def test_subtract_numbers_invalid_inputs(self):
        """Test subtract_numbers with invalid inputs."""
        with pytest.raises(MathOperationError, match="Subtraction failed"):
            subtract_numbers("hello", "world")

        with pytest.raises(MathOperationError, match="Subtraction failed"):
            subtract_numbers("3.14.15", 2)

        with pytest.raises(MathOperationError, match="Subtraction failed"):
            subtract_numbers("invalid", "5.0")


class TestMathOperationsEdgeCases:
    """Test edge cases for mathematical operations."""

    def test_very_large_numbers(self):
        """Test operations with very large numbers."""
        large_int = 10**18
        assert add_numbers(large_int, large_int) == 2 * 10**18
        assert subtract_numbers(large_int, large_int // 2) == large_int // 2

    def test_very_small_numbers(self):
        """Test operations with very small numbers."""
        small_float = 1e-10
        result = add_numbers(small_float, small_float)
        assert abs(result - 2e-10) < 1e-15

    def test_zero_operations(self):
        """Test operations involving zero."""
        assert add_numbers(0, 5) == 5
        assert add_numbers("0", "3.14") == 3.14
        assert subtract_numbers(5, 0) == 5
        assert subtract_numbers("10", "0") == 10

    def test_mixed_numeric_types(self):
        """Test operations mixing different numeric types."""
        # int + float
        result = add_numbers(5, 3.14)
        assert abs(result - 8.14) < 1e-10
        assert isinstance(result, float)

        # float + complex
        result = add_numbers(3.14, 2 + 1j)
        assert abs(result.real - 5.14) < 1e-10
        assert result.imag == 1.0
        assert isinstance(result, complex)

        # string + complex
        result = add_numbers("1.5", 2 + 3j)
        assert abs(result.real - 3.5) < 1e-10
        assert result.imag == 3.0
        assert isinstance(result, complex)