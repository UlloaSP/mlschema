"""Tests for mlschema.strategies.app.number_strategy.

This module provides comprehensive test coverage for the NumberStrategy class,
including initialization, dtype matching, schema generation, and step calculation
for numeric columns.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from pandas import Series
from pydantic import ValidationError

from mlschema.strategies.app.number_strategy import NumberStrategy
from mlschema.strategies.domain import FieldTypes, NumberField


class TestNumberStrategyInitialization:
    """Test suite for NumberStrategy initialization."""

    def test_initialization_sets_correct_attributes(self):
        """Test that NumberStrategy initializes with correct type, schema class, and dtypes."""
        strategy = NumberStrategy()

        assert strategy.type_name == FieldTypes.NUMBER
        assert strategy.schema_cls == NumberField
        assert strategy.dtypes == ("int64", "float64", "int32", "float32")

    def test_initialization_calls_parent_constructor(self):
        """Test that NumberStrategy properly calls parent class constructor."""
        with patch(
            "mlschema.strategies.app.number_strategy.Strategy.__init__"
        ) as mock_parent_init:
            mock_parent_init.return_value = None

            NumberStrategy()

            mock_parent_init.assert_called_once_with(
                type_name=FieldTypes.NUMBER,
                schema_cls=NumberField,
                dtypes=("int64", "float64", "int32", "float32"),
            )


class TestNumberStrategyDtypeHandling:
    """Test suite for dtype recognition and handling."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a NumberStrategy instance."""
        return NumberStrategy()

    @pytest.mark.parametrize("dtype", ["int64", "float64", "int32", "float32"])
    def test_handles_supported_dtypes(self, strategy, dtype):
        """Test that NumberStrategy recognizes supported numeric dtypes."""
        assert dtype in strategy.dtypes

    @pytest.mark.parametrize(
        "unsupported_dtype",
        [
            "object",
            "string",
            "bool",
            "boolean",
            "category",
            "datetime64[ns]",
            "datetime64",
            "timedelta64[ns]",
        ],
    )
    def test_does_not_handle_unsupported_dtypes(self, strategy, unsupported_dtype):
        """Test that NumberStrategy does not handle non-numeric dtypes."""
        assert unsupported_dtype not in strategy.dtypes

    def test_handles_both_integer_precisions(self, strategy):
        """Test that both 32-bit and 64-bit integers are supported."""
        assert "int32" in strategy.dtypes
        assert "int64" in strategy.dtypes

    def test_handles_both_float_precisions(self, strategy):
        """Test that both 32-bit and 64-bit floats are supported."""
        assert "float32" in strategy.dtypes
        assert "float64" in strategy.dtypes


class TestNumberStrategyAttributesFromSeries:
    """Test suite for attributes_from_series method."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a NumberStrategy instance."""
        return NumberStrategy()

    def test_returns_step_0_1_for_float64(self, strategy):
        """Test that float64 series returns step of 0.1."""
        series = Series([1.5, 2.7, 3.9], dtype="float64", name="float_values")

        result = strategy.attributes_from_series(series)

        assert result == {"step": 0.1}

    def test_returns_step_0_1_for_float32(self, strategy):
        """Test that float32 series returns step of 0.1."""
        series = Series([1.5, 2.7, 3.9], dtype="float32", name="float32_values")

        result = strategy.attributes_from_series(series)

        assert result == {"step": 0.1}

    def test_returns_step_1_for_int64(self, strategy):
        """Test that int64 series returns step of 1."""
        series = Series([1, 2, 3, 4, 5], dtype="int64", name="int_values")

        result = strategy.attributes_from_series(series)

        assert result == {"step": 1}

    def test_returns_step_1_for_int32(self, strategy):
        """Test that int32 series returns step of 1."""
        series = Series([1, 2, 3, 4, 5], dtype="int32", name="int32_values")

        result = strategy.attributes_from_series(series)

        assert result == {"step": 1}

    def test_always_returns_dict_with_step_key(self, strategy):
        """Test that the method always returns a dict with 'step' key."""
        series = Series([1, 2, 3], dtype="int64", name="test")

        result = strategy.attributes_from_series(series)

        assert isinstance(result, dict)
        assert "step" in result
        assert isinstance(result["step"], int | float)

    def test_handles_series_with_negative_numbers(self, strategy):
        """Test behavior with series containing negative numbers."""
        negative_ints = Series([-5, -10, -1], dtype="int64", name="negative_ints")
        negative_floats = Series([-1.5, -2.7], dtype="float64", name="negative_floats")

        int_result = strategy.attributes_from_series(negative_ints)
        float_result = strategy.attributes_from_series(negative_floats)

        assert int_result == {"step": 1}
        assert float_result == {"step": 0.1}

    def test_handles_series_with_zero_values(self, strategy):
        """Test behavior with series containing zero values."""
        zeros_int = Series([0, 0, 0], dtype="int64", name="zeros_int")
        zeros_float = Series([0.0, 0.0], dtype="float64", name="zeros_float")

        int_result = strategy.attributes_from_series(zeros_int)
        float_result = strategy.attributes_from_series(zeros_float)

        assert int_result == {"step": 1}
        assert float_result == {"step": 0.1}

    def test_handles_empty_series(self, strategy):
        """Test behavior with empty numeric series."""
        empty_int = Series([], dtype="int64", name="empty_int")
        empty_float = Series([], dtype="float64", name="empty_float")

        int_result = strategy.attributes_from_series(empty_int)
        float_result = strategy.attributes_from_series(empty_float)

        assert int_result == {"step": 1}
        assert float_result == {"step": 0.1}

    def test_handles_series_with_nulls(self, strategy):
        """Test behavior with series containing null values."""
        int_with_nulls = Series(
            [1, None, 3, float("nan")], dtype="float64", name="int_nulls"
        )
        float_with_nulls = Series(
            [1.5, None, 3.7, float("nan")], dtype="float64", name="float_nulls"
        )

        int_result = strategy.attributes_from_series(int_with_nulls)
        float_result = strategy.attributes_from_series(float_with_nulls)

        # Both should be treated as float64 due to NaN handling
        assert int_result == {"step": 0.1}
        assert float_result == {"step": 0.1}


class TestNumberStrategyEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a NumberStrategy instance."""
        return NumberStrategy()

    def test_handles_large_integer_values(self, strategy):
        """Test handling of large integer values."""
        # Using literal values for int64 limits: max = 2^63 - 1, min = -2^63
        large_ints = Series(
            [9223372036854775807, -9223372036854775808, 0],
            dtype="int64",
            name="large_ints",
        )

        result = strategy.attributes_from_series(large_ints)

        assert result == {"step": 1}

    def test_handles_extreme_float_values(self, strategy):
        """Test handling of extreme float values."""
        # Using literal values for float64 limits
        extreme_floats = Series(
            [
                1.7976931348623157e308,  # max
                2.2250738585072014e-308,  # min
                2.220446049250313e-16,  # eps
                -1.7976931348623157e308,  # -max
            ],
            dtype="float64",
            name="extreme_floats",
        )

        result = strategy.attributes_from_series(extreme_floats)

        assert result == {"step": 0.1}

    def test_handles_scientific_notation_floats(self, strategy):
        """Test handling of floats in scientific notation."""
        scientific_floats = Series(
            [1e10, 1e-10, 2.5e5], dtype="float64", name="scientific"
        )

        result = strategy.attributes_from_series(scientific_floats)

        assert result == {"step": 0.1}

    def test_handles_mixed_positive_negative_zero(self, strategy):
        """Test handling of mixed positive, negative, and zero values."""
        mixed_values = Series([-100.5, 0.0, 100.5], dtype="float64", name="mixed")

        result = strategy.attributes_from_series(mixed_values)

        assert result == {"step": 0.1}

    def test_handles_single_value_series(self, strategy):
        """Test behavior with series containing only one value."""
        single_int = Series([42], dtype="int64", name="single_int")
        single_float = Series([3.14], dtype="float64", name="single_float")

        int_result = strategy.attributes_from_series(single_int)
        float_result = strategy.attributes_from_series(single_float)

        assert int_result == {"step": 1}
        assert float_result == {"step": 0.1}

    def test_handles_repeated_values(self, strategy):
        """Test behavior with series containing repeated values."""
        repeated_int = Series([5, 5, 5, 5], dtype="int64", name="repeated_int")
        repeated_float = Series([2.5, 2.5, 2.5], dtype="float64", name="repeated_float")

        int_result = strategy.attributes_from_series(repeated_int)
        float_result = strategy.attributes_from_series(repeated_float)

        assert int_result == {"step": 1}
        assert float_result == {"step": 0.1}

    def test_handles_inf_and_negative_inf(self, strategy):
        """Test handling of infinity values."""
        inf_series = Series(
            [float("inf"), float("-inf"), 1.0], dtype="float64", name="inf_values"
        )

        result = strategy.attributes_from_series(inf_series)

        assert result == {"step": 0.1}


class TestNumberStrategyBusinessLogic:
    """Test suite for business logic validation."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a NumberStrategy instance."""
        return NumberStrategy()

    def test_float_dtype_detection_uses_pandas_api(self, strategy):
        """Test that float dtype detection uses pandas API correctly."""
        float_series = Series([1.1, 2.2, 3.3], dtype="float64", name="test_float")

        with patch(
            "mlschema.strategies.app.number_strategy.api.types.is_float_dtype"
        ) as mock_is_float:
            mock_is_float.return_value = True

            result = strategy.attributes_from_series(float_series)

            mock_is_float.assert_called_once_with(float_series.dtype)
            assert result == {"step": 0.1}

    def test_integer_dtype_detection_uses_pandas_api(self, strategy):
        """Test that integer dtype detection uses pandas API correctly."""
        int_series = Series([1, 2, 3], dtype="int64", name="test_int")

        with patch(
            "mlschema.strategies.app.number_strategy.api.types.is_float_dtype"
        ) as mock_is_float:
            mock_is_float.return_value = False

            result = strategy.attributes_from_series(int_series)

            mock_is_float.assert_called_once_with(int_series.dtype)
            assert result == {"step": 1}

    def test_step_values_match_business_rules(self, strategy):
        """Test that step values match documented business rules."""
        # Business rule: For float → step = 0.1
        float_series = Series([1.0], dtype="float64")
        float_result = strategy.attributes_from_series(float_series)
        assert float_result["step"] == 0.1

        # Business rule: For int → step = 1
        int_series = Series([1], dtype="int64")
        int_result = strategy.attributes_from_series(int_series)
        assert int_result["step"] == 1

    def test_number_field_validation_fails_with_invalid_value(self):
        """Test that NumberField validation fails with invalid values."""
        strategy = NumberStrategy()

        # Try to create a field with min > max
        with pytest.raises(
            ValidationError,
        ):
            strategy.schema_cls(
                title="invalid_number",
                max=0.0,
                min=1.0,
            )

        # Try to create a field with min > value
        with pytest.raises(
            ValidationError,
        ):
            strategy.schema_cls(
                title="invalid_number",
                value=0.0,
                min=1.0,
            )

        # Try to create a field with max < value
        with pytest.raises(
            ValidationError,
        ):
            strategy.schema_cls(
                title="invalid_number",
                max=1.0,
                value=2.0,
            )


class TestNumberStrategyIntegration:
    """Integration tests for NumberStrategy with related components."""

    def test_integration_with_number_field(self):
        """Test that NumberStrategy integrates properly with NumberField."""
        strategy = NumberStrategy()

        # Create a test series
        series = Series([1, 2, 3], dtype="int64", name="test")
        attributes = strategy.attributes_from_series(series)

        # Verify the schema class can be instantiated with extracted attributes
        field_instance = strategy.schema_cls(title="test_number", **attributes)

        assert isinstance(field_instance, NumberField)
        assert field_instance.type == FieldTypes.NUMBER
        assert field_instance.title == "test_number"
        assert field_instance.step == 1

    def test_strategy_type_matches_field_type(self):
        """Test that strategy type name matches the field type."""
        strategy = NumberStrategy()
        field_instance = strategy.schema_cls(title="test", step=1)

        assert strategy.type_name == field_instance.type

    def test_extracted_step_works_with_number_field_validation(self):
        """Test that extracted step value works with NumberField validation."""
        strategy = NumberStrategy()

        # Test float series
        float_series = Series([1.5, 2.5], dtype="float64", name="prices")
        float_attributes = strategy.attributes_from_series(float_series)
        float_field = strategy.schema_cls(
            title="price", value=1.5, min=0.0, max=10.0, **float_attributes
        )

        assert float_field.step == 0.1
        assert float_field.value == 1.5

        # Test integer series
        int_series = Series([1, 2, 3], dtype="int64", name="counts")
        int_attributes = strategy.attributes_from_series(int_series)
        int_field = strategy.schema_cls(
            title="count", value=2, min=0, max=100, **int_attributes
        )

        assert int_field.step == 1
        assert int_field.value == 2

    def test_dtypes_consistency(self):
        """Test that dtypes tuple is immutable and consistent."""
        strategy1 = NumberStrategy()
        strategy2 = NumberStrategy()

        assert strategy1.dtypes == strategy2.dtypes
        assert strategy1.dtypes is not strategy2.dtypes  # Different instances
        assert isinstance(strategy1.dtypes, tuple)  # Immutable


class TestNumberStrategyErrorHandling:
    """Test suite for error handling and exceptional conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a NumberStrategy instance."""
        return NumberStrategy()

    def test_method_never_raises_exceptions(self, strategy):
        """Test that attributes_from_series method is robust against edge cases."""
        test_cases = [
            Series([], dtype="int64", name="empty"),
            Series([float("nan")], dtype="float64", name="only_nan"),
            Series([float("inf"), float("-inf")], dtype="float64", name="only_inf"),
            Series([0], dtype="int32", name="zero"),
            Series([9223372036854775807], dtype="int64", name="max_int"),
        ]

        for series in test_cases:
            # Should not raise any exception
            result = strategy.attributes_from_series(series)
            assert isinstance(result, dict)
            assert "step" in result

    def test_return_type_is_always_dict(self, strategy):
        """Test that method always returns a dictionary."""
        series = Series([1, 2, 3], dtype="int64", name="test")

        result = strategy.attributes_from_series(series)

        assert isinstance(result, dict)
        assert len(result) == 1
        assert "step" in result

    def test_step_value_is_always_numeric(self, strategy):
        """Test that step value is always numeric."""
        test_series = [
            Series([1], dtype="int64", name="int"),
            Series([1.0], dtype="float64", name="float"),
            Series([1], dtype="int32", name="int32"),
            Series([1.0], dtype="float32", name="float32"),
        ]

        for series in test_series:
            result = strategy.attributes_from_series(series)
            step_value = result["step"]
            assert isinstance(step_value, int | float)
            assert step_value > 0  # Step should always be positive


class TestNumberStrategyMocking:
    """Test suite using mocks to test internal behavior."""

    def test_pandas_api_is_called_correctly(self):
        """Test that pandas API is called with correct parameters."""
        strategy = NumberStrategy()

        # Create a mock series
        mock_series = Mock(spec=Series)
        mock_series.dtype = "float64"

        with patch(
            "mlschema.strategies.app.number_strategy.api.types.is_float_dtype"
        ) as mock_is_float:
            mock_is_float.return_value = True

            result = strategy.attributes_from_series(mock_series)

            mock_is_float.assert_called_once_with("float64")
            assert result == {"step": 0.1}

    def test_conditional_logic_float_path(self):
        """Test the conditional logic for float dtype path."""
        strategy = NumberStrategy()
        mock_series = Mock(spec=Series)

        with patch(
            "mlschema.strategies.app.number_strategy.api.types.is_float_dtype"
        ) as mock_is_float:
            mock_is_float.return_value = True

            result = strategy.attributes_from_series(mock_series)

            assert result == {"step": 0.1}

    def test_conditional_logic_integer_path(self):
        """Test the conditional logic for integer dtype path."""
        strategy = NumberStrategy()
        mock_series = Mock(spec=Series)

        with patch(
            "mlschema.strategies.app.number_strategy.api.types.is_float_dtype"
        ) as mock_is_float:
            mock_is_float.return_value = False

            result = strategy.attributes_from_series(mock_series)

            assert result == {"step": 1}

    def test_inheritance_chain_is_correct(self):
        """Test that NumberStrategy properly inherits from Strategy."""
        from mlschema.core.app.strategy import Strategy

        strategy = NumberStrategy()

        assert isinstance(strategy, Strategy)
        assert hasattr(strategy, "type_name")
        assert hasattr(strategy, "schema_cls")
        assert hasattr(strategy, "dtypes")
        assert hasattr(strategy, "attributes_from_series")


class TestNumberStrategyConstants:
    """Test suite for NumberStrategy constants and class attributes."""

    def test_supported_dtypes_are_numeric(self):
        """Test that all supported dtypes are numeric types."""
        strategy = NumberStrategy()

        numeric_prefixes = ["int", "float"]
        for dtype in strategy.dtypes:
            assert any(dtype.startswith(prefix) for prefix in numeric_prefixes)

    def test_type_name_constant(self):
        """Test that type name is consistent."""
        strategy = NumberStrategy()

        assert strategy.type_name == "number"
        assert strategy.type_name == FieldTypes.NUMBER.value

    def test_schema_class_constant(self):
        """Test that schema class is consistent."""
        strategy = NumberStrategy()

        assert strategy.schema_cls == NumberField
        assert issubclass(strategy.schema_cls, NumberField)

    def test_step_values_are_constants(self):
        """Test that step values are consistent constants."""
        strategy = NumberStrategy()

        # Test multiple calls return same values
        int_series = Series([1], dtype="int64")
        float_series = Series([1.0], dtype="float64")

        int_result1 = strategy.attributes_from_series(int_series)
        int_result2 = strategy.attributes_from_series(int_series)
        float_result1 = strategy.attributes_from_series(float_series)
        float_result2 = strategy.attributes_from_series(float_series)

        assert int_result1 == int_result2 == {"step": 1}
        assert float_result1 == float_result2 == {"step": 0.1}
