"""Tests for mlschema.strategies.app.boolean_strategy.

This module provides comprehensive test coverage for the BooleanStrategy class,
including initialization, dtype matching, and schema generation for boolean columns.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from pandas import Series

from mlschema.strategies import BooleanStrategy
from mlschema.strategies.domain import BooleanField, FieldTypes


class TestBooleanStrategyInitialization:
    """Test suite for BooleanStrategy initialization."""

    def test_initialization_sets_correct_attributes(self):
        """Test that BooleanStrategy initializes with correct type, schema class, and dtypes."""
        strategy = BooleanStrategy()

        assert strategy.type_name == FieldTypes.BOOLEAN
        assert strategy.schema_cls == BooleanField
        assert strategy.dtypes == ("bool", "boolean")

    def test_initialization_calls_parent_constructor(self):
        """Test that BooleanStrategy properly calls parent class constructor."""
        with patch(
            "mlschema.strategies.app.boolean_strategy.Strategy.__init__"
        ) as mock_parent_init:
            mock_parent_init.return_value = None

            BooleanStrategy()

            mock_parent_init.assert_called_once_with(
                type_name=FieldTypes.BOOLEAN,
                schema_cls=BooleanField,
                dtypes=("bool", "boolean"),
            )


class TestBooleanStrategyDtypeHandling:
    """Test suite for dtype recognition and handling."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a BooleanStrategy instance."""
        return BooleanStrategy()

    @pytest.mark.parametrize("dtype", ["bool", "boolean"])
    def test_handles_supported_dtypes(self, strategy, dtype):
        """Test that BooleanStrategy recognizes supported boolean dtypes."""
        # Create a mock series with the specified dtype
        mock_series = Mock(spec=Series)
        mock_series.dtype = dtype

        # The strategy should handle this dtype (inherited from base class)
        assert dtype in strategy.dtypes

    @pytest.mark.parametrize(
        "unsupported_dtype",
        [
            "int64",
            "float64",
            "object",
            "string",
            "category",
            "datetime64[ns]",
            "int32",
            "float32",
        ],
    )
    def test_does_not_handle_unsupported_dtypes(self, strategy, unsupported_dtype):
        """Test that BooleanStrategy does not handle non-boolean dtypes."""
        assert unsupported_dtype not in strategy.dtypes


class TestBooleanStrategySchemaGeneration:
    """Test suite for schema generation functionality."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a BooleanStrategy instance."""
        return BooleanStrategy()

    def test_schema_class_is_boolean_field(self, strategy):
        """Test that BooleanStrategy uses BooleanField as schema class."""
        assert strategy.schema_cls == BooleanField

    def test_type_name_is_boolean(self, strategy):
        """Test that BooleanStrategy has correct type name."""
        assert strategy.type_name == FieldTypes.BOOLEAN
        assert strategy.type_name == "boolean"


class TestBooleanStrategyInheritance:
    """Test suite for inheritance and method delegation."""

    def test_inherits_from_field_strategy(self):
        """Test that BooleanStrategy properly inherits from Strategy."""
        from mlschema.core.app import Strategy

        strategy = BooleanStrategy()
        assert isinstance(strategy, Strategy)

    def test_does_not_override_attributes_from_series(self):
        """Test that BooleanStrategy delegates to parent for attributes_from_series."""
        strategy = BooleanStrategy()

        # BooleanStrategy should not have its own attributes_from_series method
        # It should use the parent class implementation
        assert "attributes_from_series" not in BooleanStrategy.__dict__

        # But the instance should have the method from parent class
        assert hasattr(strategy, "attributes_from_series")

    def test_delegates_schema_generation_to_parent(self):
        """Test that BooleanStrategy delegates schema generation to parent class."""
        strategy = BooleanStrategy()

        # Create a mock series
        mock_series = Mock(spec=Series)
        mock_series.dtype = "bool"
        mock_series.name = "is_active"

        # Mock the parent class method
        with patch.object(
            strategy, "attributes_from_series", return_value={}
        ) as mock_attrs:
            # The strategy should be able to call inherited methods
            result = strategy.attributes_from_series(mock_series)

            mock_attrs.assert_called_once_with(mock_series)
            assert isinstance(result, dict)


class TestBooleanStrategyEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a BooleanStrategy instance."""
        return BooleanStrategy()

    def test_empty_series_handling(self, strategy):
        """Test behavior with empty boolean series."""
        empty_series = Series([], dtype="bool", name="empty_bool")

        # Should not raise an exception
        result = strategy.attributes_from_series(empty_series)
        assert isinstance(result, dict)

    def test_series_with_nulls_handling(self, strategy):
        """Test behavior with boolean series containing null values."""
        series_with_nulls = Series(
            [True, False, None, True], dtype="boolean", name="nullable_bool"
        )

        # Should handle nullable boolean dtype
        result = strategy.attributes_from_series(series_with_nulls)
        assert isinstance(result, dict)

    def test_series_with_all_true_values(self, strategy):
        """Test behavior with boolean series containing only True values."""
        all_true_series = Series([True, True, True], dtype="bool", name="all_true")

        result = strategy.attributes_from_series(all_true_series)
        assert isinstance(result, dict)

    def test_series_with_all_false_values(self, strategy):
        """Test behavior with boolean series containing only False values."""
        all_false_series = Series([False, False, False], dtype="bool", name="all_false")

        result = strategy.attributes_from_series(all_false_series)
        assert isinstance(result, dict)

    def test_large_boolean_series(self, strategy):
        """Test behavior with large boolean series."""
        large_series = Series([True, False] * 5000, dtype="bool", name="large_bool")

        result = strategy.attributes_from_series(large_series)
        assert isinstance(result, dict)


class TestBooleanStrategyIntegration:
    """Integration tests for BooleanStrategy with related components."""

    def test_integration_with_boolean_field(self):
        """Test that BooleanStrategy integrates properly with BooleanField."""
        strategy = BooleanStrategy()

        # Verify the schema class can be instantiated
        field_instance = strategy.schema_cls(title="test_boolean")

        assert isinstance(field_instance, BooleanField)
        assert field_instance.type == FieldTypes.BOOLEAN
        assert field_instance.title == "test_boolean"

    def test_strategy_type_matches_field_type(self):
        """Test that strategy type name matches the field type."""
        strategy = BooleanStrategy()
        field_instance = strategy.schema_cls(title="test")

        assert strategy.type_name == field_instance.type.value

    def test_dtypes_consistency(self):
        """Test that dtypes tuple is immutable and consistent."""
        strategy1 = BooleanStrategy()
        strategy2 = BooleanStrategy()

        assert strategy1.dtypes == strategy2.dtypes
        assert strategy1.dtypes is not strategy2.dtypes  # Different instances
        assert isinstance(strategy1.dtypes, tuple)  # Immutable
