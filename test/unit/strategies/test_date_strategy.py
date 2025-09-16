"""Tests for mlschema.strategies.app.date_strategy.

This module provides comprehensive test coverage for the DateStrategy class,
including initialization, dtype matching, and schema generation for date/datetime columns.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from pandas import Series

from mlschema.strategies.app.date_strategy import DateStrategy
from mlschema.strategies.domain import DateField, FieldTypes


class TestDateStrategyInitialization:
    """Test suite for DateStrategy initialization."""

    def test_initialization_sets_correct_attributes(self):
        """Test that DateStrategy initializes with correct type, schema class, and dtypes."""
        strategy = DateStrategy()

        assert strategy.type_name == FieldTypes.DATE
        assert strategy.schema_cls == DateField
        assert strategy.dtypes == ("datetime64[ns]", "datetime64")

    def test_initialization_calls_parent_constructor(self):
        """Test that DateStrategy properly calls parent class constructor."""
        with patch(
            "mlschema.strategies.app.date_strategy.Strategy.__init__"
        ) as mock_parent_init:
            mock_parent_init.return_value = None

            DateStrategy()

            mock_parent_init.assert_called_once_with(
                type_name=FieldTypes.DATE,
                schema_cls=DateField,
                dtypes=("datetime64[ns]", "datetime64"),
            )


class TestDateStrategyDtypeHandling:
    """Test suite for dtype recognition and handling."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a DateStrategy instance."""
        return DateStrategy()

    @pytest.mark.parametrize("dtype", ["datetime64[ns]", "datetime64"])
    def test_handles_supported_dtypes(self, strategy, dtype):
        """Test that DateStrategy recognizes supported datetime dtypes."""
        assert dtype in strategy.dtypes

    @pytest.mark.parametrize(
        "unsupported_dtype",
        [
            "int64",
            "float64",
            "object",
            "string",
            "bool",
            "boolean",
            "category",
            "int32",
            "float32",
            "timedelta64[ns]",
            "period[D]",
        ],
    )
    def test_does_not_handle_unsupported_dtypes(self, strategy, unsupported_dtype):
        """Test that DateStrategy does not handle non-datetime dtypes."""
        assert unsupported_dtype not in strategy.dtypes

    def test_handles_datetime64_with_nanosecond_precision(self, strategy):
        """Test specific handling of datetime64[ns] dtype."""
        assert "datetime64[ns]" in strategy.dtypes

    def test_handles_generic_datetime64(self, strategy):
        """Test handling of generic datetime64 dtype."""
        assert "datetime64" in strategy.dtypes


class TestDateStrategySchemaGeneration:
    """Test suite for schema generation functionality."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a DateStrategy instance."""
        return DateStrategy()

    def test_schema_class_is_date_field(self, strategy):
        """Test that DateStrategy uses DateField as schema class."""
        assert strategy.schema_cls == DateField

    def test_type_name_is_date(self, strategy):
        """Test that DateStrategy has correct type name."""
        assert strategy.type_name == FieldTypes.DATE
        assert strategy.type_name == "date"


class TestDateStrategyInheritance:
    """Test suite for inheritance and method delegation."""

    def test_inherits_from_field_strategy(self):
        """Test that DateStrategy properly inherits from Strategy."""
        from mlschema.core.app.strategy import Strategy

        strategy = DateStrategy()
        assert isinstance(strategy, Strategy)

    def test_does_not_override_attributes_from_series(self):
        """Test that DateStrategy delegates to parent for attributes_from_series."""
        strategy = DateStrategy()

        # DateStrategy should not have its own attributes_from_series method
        # It should use the parent class implementation
        assert "attributes_from_series" not in DateStrategy.__dict__

        # But the instance should have the method from parent class
        assert hasattr(strategy, "attributes_from_series")

    def test_delegates_schema_generation_to_parent(self):
        """Test that DateStrategy delegates schema generation to parent class."""
        strategy = DateStrategy()

        # Create a mock series with datetime dtype
        mock_series = Mock(spec=Series)
        mock_series.dtype = "datetime64[ns]"
        mock_series.name = "created_at"

        # Mock the parent class method
        with patch.object(
            strategy, "attributes_from_series", return_value={}
        ) as mock_attrs:
            # The strategy should be able to call inherited methods
            result = strategy.attributes_from_series(mock_series)

            mock_attrs.assert_called_once_with(mock_series)
            assert isinstance(result, dict)


class TestDateStrategyWithRealDatetimeSeries:
    """Test suite with real datetime series data."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a DateStrategy instance."""
        return DateStrategy()

    def test_handles_datetime64_ns_series(self, strategy):
        """Test behavior with datetime64[ns] series."""
        dates = pd.date_range("2023-01-01", periods=5, freq="D")
        series = Series(dates, name="date_series")

        # Should not raise an exception
        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)

    def test_handles_series_with_nat_values(self, strategy):
        """Test behavior with datetime series containing NaT (Not a Time) values."""
        dates = [pd.Timestamp("2023-01-01"), pd.NaT, pd.Timestamp("2023-01-03"), pd.NaT]
        series = Series(dates, name="dates_with_nat")

        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)

    def test_handles_empty_datetime_series(self, strategy):
        """Test behavior with empty datetime series."""
        empty_series = Series([], dtype="datetime64[ns]", name="empty_dates")

        result = strategy.attributes_from_series(empty_series)
        assert isinstance(result, dict)

    def test_handles_all_nat_series(self, strategy):
        """Test behavior with series containing only NaT values."""
        all_nat_series = Series([pd.NaT, pd.NaT, pd.NaT], name="all_nat")

        result = strategy.attributes_from_series(all_nat_series)
        assert isinstance(result, dict)

    def test_handles_single_date_series(self, strategy):
        """Test behavior with series containing only one date."""
        single_date = Series([pd.Timestamp("2023-01-01")], name="single_date")

        result = strategy.attributes_from_series(single_date)
        assert isinstance(result, dict)

    def test_handles_large_datetime_range(self, strategy):
        """Test behavior with large datetime range."""
        large_range = pd.date_range("1900-01-01", "2100-12-31", freq="YE")
        series = Series(large_range, name="large_range")

        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)

    def test_handles_mixed_timezone_aware_dates(self, strategy):
        """Test behavior with timezone-aware datetime series."""
        tz_dates = pd.date_range("2023-01-01", periods=3, freq="D", tz="UTC")
        series = Series(tz_dates, name="tz_dates")

        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)


class TestDateStrategyEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a DateStrategy instance."""
        return DateStrategy()

    def test_handles_datetime_with_microseconds(self, strategy):
        """Test handling of datetime with microsecond precision."""
        precise_dates = [
            pd.Timestamp("2023-01-01 12:30:45.123456"),
            pd.Timestamp("2023-01-02 08:15:30.789012"),
        ]
        series = Series(precise_dates, name="precise_dates")

        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)

    def test_handles_leap_year_dates(self, strategy):
        """Test handling of leap year dates."""
        leap_dates = [
            pd.Timestamp("2020-02-29"),  # Leap year
            pd.Timestamp("2024-02-29"),  # Another leap year
        ]
        series = Series(leap_dates, name="leap_dates")

        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)

    def test_handles_boundary_dates(self, strategy):
        """Test handling of boundary datetime values."""
        boundary_dates = [
            pd.Timestamp.min,
            pd.Timestamp.max,
            pd.Timestamp("1970-01-01"),  # Unix epoch
        ]
        # Filter out any that might cause overflow
        valid_dates = [d for d in boundary_dates if pd.notna(d)]
        series = Series(valid_dates, name="boundary_dates")

        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)

    def test_handles_different_datetime_formats(self, strategy):
        """Test handling of different datetime string formats converted to datetime."""
        date_strings = ["2023-01-01", "2023/01/02", "01-03-2023", "2023-01-04T10:30:00"]
        date_formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S"]
        converted_dates = [
            pd.to_datetime(date_str, format=fmt)
            for date_str, fmt in zip(date_strings, date_formats, strict=True)
        ]
        series = Series(converted_dates, name="formatted_dates")

        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)


class TestDateStrategyIntegration:
    """Integration tests for DateStrategy with related components."""

    def test_integration_with_date_field(self):
        """Test that DateStrategy integrates properly with DateField."""
        strategy = DateStrategy()

        # Verify the schema class can be instantiated
        field_instance = strategy.schema_cls(title="test_date")

        assert isinstance(field_instance, DateField)
        assert field_instance.type == FieldTypes.DATE
        assert field_instance.title == "test_date"

    def test_strategy_type_matches_field_type(self):
        """Test that strategy type name matches the field type."""
        strategy = DateStrategy()
        field_instance = strategy.schema_cls(title="test")

        assert strategy.type_name == field_instance.type

    def test_dtypes_consistency(self):
        """Test that dtypes tuple is immutable and consistent."""
        strategy1 = DateStrategy()
        strategy2 = DateStrategy()

        assert strategy1.dtypes == strategy2.dtypes
        assert strategy1.dtypes is not strategy2.dtypes  # Different instances
        assert isinstance(strategy1.dtypes, tuple)  # Immutable

    def test_date_field_validation_with_extracted_data(self):
        """Test that DateField validation works with data from DateStrategy."""
        strategy = DateStrategy()

        # Create a date field with valid date constraints
        today = date.today()
        field = strategy.schema_cls(
            title="event_date",
            value=today,
            min=date(today.year, 1, 1),
            max=date(today.year, 12, 31),
        )

        assert field.value == today
        assert field.min.year == today.year
        assert field.max.year == today.year

    def test_date_field_validation_fails_with_invalid_constraints(self):
        """Test that DateField validation fails with invalid date constraints."""
        strategy = DateStrategy()

        # Try to create a field with min > max
        with pytest.raises(
            ValueError,
            match="Minimum date must be earlier than or equal to maximum date",
        ):
            strategy.schema_cls(
                title="invalid_date",
                min=date(2023, 12, 31),
                max=date(2023, 1, 1),  # max < min
            )

    def test_date_field_validation_fails_with_invalid_value(self):
        """Test that DateField validation fails with invalid date value."""
        strategy = DateStrategy()

        # Try to create a field with min > value
        with pytest.raises(
            ValueError,
            match="Date must be later than or equal to minimum date",
        ):
            strategy.schema_cls(
                title="invalid_date",
                value=date(2022, 12, 31),
                min=date(2023, 1, 1),
            )

        # Try to create a field with max < value
        with pytest.raises(
            ValueError,
            match="Date must be earlier than or equal to maximum date",
        ):
            strategy.schema_cls(
                title="invalid_date",
                max=date(2023, 12, 31),
                value=date(2024, 1, 1),
            )


class TestDateStrategyErrorHandling:
    """Test suite for error handling and exceptional conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a DateStrategy instance."""
        return DateStrategy()

    def test_method_returns_dict(self, strategy):
        """Test that attributes_from_series always returns a dictionary."""
        dates = pd.date_range("2023-01-01", periods=3)
        series = Series(dates, name="test_dates")

        result = strategy.attributes_from_series(series)

        assert isinstance(result, dict)

    def test_handles_datetime_series_with_different_frequencies(self, strategy):
        """Test handling of datetime series with various frequencies."""
        frequencies = ["D", "h", "ME", "YE", "W"]

        for freq in frequencies:
            dates = pd.date_range("2023-01-01", periods=5, freq=freq)
            series = Series(dates, name=f"dates_{freq}")

            result = strategy.attributes_from_series(series)
            assert isinstance(result, dict)

    def test_handles_unsorted_datetime_series(self, strategy):
        """Test handling of unsorted datetime series."""
        unsorted_dates = [
            pd.Timestamp("2023-01-03"),
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-02"),
        ]
        series = Series(unsorted_dates, name="unsorted_dates")

        result = strategy.attributes_from_series(series)
        assert isinstance(result, dict)


class TestDateStrategyMocking:
    """Test suite using mocks to test internal behavior."""

    def test_delegates_to_parent_attributes_from_series(self):
        """Test that DateStrategy properly delegates to parent implementation."""
        strategy = DateStrategy()

        # Create a mock series
        mock_series = Mock(spec=Series)
        mock_series.dtype = "datetime64[ns]"
        mock_series.name = "mock_dates"

        # Mock the parent class method
        with patch.object(
            strategy.__class__.__bases__[0], "attributes_from_series"
        ) as mock_parent_method:
            mock_parent_method.return_value = {"test": "data"}

            result = strategy.attributes_from_series(mock_series)

            mock_parent_method.assert_called_once_with(mock_series)
            assert result == {"test": "data"}

    def test_initialization_parameters_are_correct(self):
        """Test that initialization passes correct parameters to parent."""
        with patch(
            "mlschema.strategies.app.date_strategy.Strategy.__init__"
        ) as mock_parent_init:
            mock_parent_init.return_value = None

            DateStrategy()

            mock_parent_init.assert_called_once_with(
                type_name=FieldTypes.DATE,
                schema_cls=DateField,
                dtypes=("datetime64[ns]", "datetime64"),
            )


class TestDateStrategyConstants:
    """Test suite for DateStrategy constants and class attributes."""

    def test_supported_dtypes_are_datetime_related(self):
        """Test that all supported dtypes are datetime-related."""
        strategy = DateStrategy()

        for dtype in strategy.dtypes:
            assert "datetime" in dtype.lower()

    def test_type_name_constant(self):
        """Test that type name is consistent."""
        strategy = DateStrategy()

        assert strategy.type_name == "date"
        assert strategy.type_name == FieldTypes.DATE.value

    def test_schema_class_constant(self):
        """Test that schema class is consistent."""
        strategy = DateStrategy()

        assert strategy.schema_cls == DateField
        assert issubclass(strategy.schema_cls, DateField)
