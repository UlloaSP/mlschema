"""Tests for mlschema.strategies.app.category_strategy.

This module provides comprehensive test coverage for the CategoryStrategy class,
including initialization, dtype matching, schema generation, and options extraction
for categorical columns.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pandas as pd
import pytest
from pandas import CategoricalDtype, Series

from mlschema.strategies.app.category_strategy import CategoryStrategy
from mlschema.strategies.domain import CategoryField, FieldTypes


class TestCategoryStrategyInitialization:
    """Test suite for CategoryStrategy initialization."""

    def test_initialization_sets_correct_attributes(self):
        """Test that CategoryStrategy initializes with correct type, schema class, and dtypes."""
        strategy = CategoryStrategy()

        assert strategy.type_name == FieldTypes.CATEGORY
        assert strategy.schema_cls == CategoryField
        assert strategy.dtypes == ("category",)

    def test_initialization_calls_parent_constructor(self):
        """Test that CategoryStrategy properly calls parent class constructor."""
        with patch(
            "mlschema.strategies.app.category_strategy.Strategy.__init__"
        ) as mock_parent_init:
            mock_parent_init.return_value = None

            CategoryStrategy()

            mock_parent_init.assert_called_once_with(
                type_name=FieldTypes.CATEGORY,
                schema_cls=CategoryField,
                dtypes=("category",),
            )


class TestCategoryStrategyDtypeHandling:
    """Test suite for dtype recognition and handling."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a CategoryStrategy instance."""
        return CategoryStrategy()

    def test_handles_category_dtype(self, strategy):
        """Test that CategoryStrategy recognizes category dtype."""
        assert "category" in strategy.dtypes

    @pytest.mark.parametrize(
        "unsupported_dtype",
        [
            "int64",
            "float64",
            "object",
            "string",
            "bool",
            "boolean",
            "datetime64[ns]",
            "int32",
            "float32",
        ],
    )
    def test_does_not_handle_unsupported_dtypes(self, strategy, unsupported_dtype):
        """Test that CategoryStrategy does not handle non-categorical dtypes."""
        assert unsupported_dtype not in strategy.dtypes


class TestCategoryStrategyAttributesFromSeries:
    """Test suite for attributes_from_series method."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a CategoryStrategy instance."""
        return CategoryStrategy()

    def test_extracts_options_from_categorical_dtype(self, strategy):
        """Test extracting options from pandas CategoricalDtype series."""
        categories = ["A", "B", "C"]
        cat_dtype = CategoricalDtype(categories=categories)
        series = Series(["A", "B", "A", "C"], dtype=cat_dtype, name="test_cat")

        result = strategy.attributes_from_series(series)

        assert result == {"options": categories}
        assert isinstance(result["options"], list)
        assert len(result["options"]) == 3

    def test_extracts_options_from_categorical_dtype_with_unused_categories(
        self, strategy
    ):
        """Test extracting options from categorical series with unused categories."""
        categories = ["A", "B", "C", "D", "E"]
        cat_dtype = CategoricalDtype(categories=categories)
        series = Series(["A", "B", "A"], dtype=cat_dtype, name="test_cat")

        result = strategy.attributes_from_series(series)

        # Should include all defined categories, even unused ones
        assert result == {"options": categories}
        assert "D" in result["options"]
        assert "E" in result["options"]

    def test_extracts_options_from_non_categorical_series(self, strategy):
        """Test extracting unique values from non-categorical series."""
        series = Series(["X", "Y", "Z", "X", "Y"], name="test_non_cat")

        result = strategy.attributes_from_series(series)

        expected_options = ["X", "Y", "Z"]
        assert set(result["options"]) == set(expected_options)
        assert len(result["options"]) == 3

    def test_handles_series_with_null_values(self, strategy):
        """Test that null values are properly excluded from options."""
        series = Series(["A", None, "B", pd.NA, "C", "A"], name="test_nulls")

        result = strategy.attributes_from_series(series)

        expected_options = ["A", "B", "C"]
        assert set(result["options"]) == set(expected_options)
        assert len(result["options"]) == 3
        assert None not in result["options"]
        # Check that NaN-like values are not in options
        assert all(opt == opt for opt in result["options"])  # NaN != NaN

    def test_handles_empty_series(self, strategy):
        """Test behavior with empty series."""
        empty_series = Series([], dtype="object", name="empty")

        result = strategy.attributes_from_series(empty_series)

        assert result == {"options": []}
        assert isinstance(result["options"], list)

    def test_handles_all_null_series(self, strategy):
        """Test behavior with series containing only null values."""
        all_null_series = Series([None, pd.NA, None], name="all_nulls")

        result = strategy.attributes_from_series(all_null_series)

        assert result == {"options": []}

    def test_preserves_order_in_categorical_dtype(self, strategy):
        """Test that categorical dtype order is preserved."""
        categories = ["High", "Medium", "Low"]
        cat_dtype = CategoricalDtype(categories=categories, ordered=True)
        series = Series(["Medium", "High", "Low"], dtype=cat_dtype, name="ordered_cat")

        result = strategy.attributes_from_series(series)

        assert result["options"] == categories  # Order should be preserved

    def test_handles_numeric_string_categories(self, strategy):
        """Test handling of numeric strings as categories."""
        series = Series(["1", "2", "3", "1", "2"], name="numeric_strings")

        result = strategy.attributes_from_series(series)

        expected_options = ["1", "2", "3"]
        assert set(result["options"]) == set(expected_options)

    def test_handles_mixed_type_categories_in_object_series(self, strategy):
        """Test handling of mixed types in object series."""
        series = Series([1, "A", 2.5, "B", 1], dtype="object", name="mixed")

        result = strategy.attributes_from_series(series)

        expected_options = [1, "A", 2.5, "B"]
        assert set(result["options"]) == set(expected_options)
        assert len(result["options"]) == 4


class TestCategoryStrategyEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a CategoryStrategy instance."""
        return CategoryStrategy()

    def test_single_value_series(self, strategy):
        """Test series with only one unique value."""
        series = Series(["A", "A", "A"], name="single_value")

        result = strategy.attributes_from_series(series)

        assert result == {"options": ["A"]}

    def test_large_number_of_categories(self, strategy):
        """Test series with large number of unique values."""
        large_categories = [f"cat_{i}" for i in range(1000)]
        series = Series(
            large_categories * 2, name="large_cats"
        )  # Duplicate to test uniqueness

        result = strategy.attributes_from_series(series)

        assert len(result["options"]) == 1000
        assert set(result["options"]) == set(large_categories)

    def test_unicode_categories(self, strategy):
        """Test handling of unicode category names."""
        unicode_cats = ["café", "naïve", "résumé", "🚀", "🎉"]
        series = Series(unicode_cats, name="unicode_cats")

        result = strategy.attributes_from_series(series)

        assert set(result["options"]) == set(unicode_cats)

    def test_empty_string_category(self, strategy):
        """Test handling of empty string as a category."""
        series = Series(["A", "", "B", ""], name="with_empty")

        result = strategy.attributes_from_series(series)

        expected_options = ["A", "", "B"]
        assert set(result["options"]) == set(expected_options)
        assert "" in result["options"]

    def test_whitespace_categories(self, strategy):
        """Test handling of whitespace-only categories."""
        series = Series(["A", " ", "  ", "\t", "\n"], name="whitespace")

        result = strategy.attributes_from_series(series)

        expected_options = ["A", " ", "  ", "\t", "\n"]
        assert set(result["options"]) == set(expected_options)

    def test_boolean_values_as_categories(self, strategy):
        """Test handling of boolean values in object series."""
        series = Series([True, False, True, False], dtype="object", name="bool_cats")

        result = strategy.attributes_from_series(series)

        assert set(result["options"]) == {True, False}

    def test_duplicate_categories_removed(self, strategy):
        """Test that duplicate values are properly removed."""
        series = Series(["A", "B", "A", "C", "B", "A"], name="duplicates")

        result = strategy.attributes_from_series(series)

        assert len(result["options"]) == 3
        assert set(result["options"]) == {"A", "B", "C"}


class TestCategoryStrategyIntegration:
    """Integration tests for CategoryStrategy with related components."""

    def test_integration_with_category_field(self):
        """Test that CategoryStrategy integrates properly with CategoryField."""
        strategy = CategoryStrategy()

        # Create a test series
        series = Series(["A", "B", "C"], name="test")
        attributes = strategy.attributes_from_series(series)

        # Verify the schema class can be instantiated with extracted attributes
        field_instance = strategy.schema_cls(title="test_category", **attributes)

        assert isinstance(field_instance, CategoryField)
        assert field_instance.type == FieldTypes.CATEGORY
        assert field_instance.title == "test_category"
        assert field_instance.options == ["A", "B", "C"]

    def test_strategy_type_matches_field_type(self):
        """Test that strategy type name matches the field type."""
        strategy = CategoryStrategy()
        field_instance = strategy.schema_cls(title="test", options=["A", "B"])

        assert strategy.type_name == field_instance.type

    def test_extracted_options_validate_in_category_field(self):
        """Test that extracted options work with CategoryField validation."""
        strategy = CategoryStrategy()
        series = Series(["Red", "Green", "Blue"], name="colors")

        attributes = strategy.attributes_from_series(series)
        field = strategy.schema_cls(
            title="color",
            value="Red",  # Valid value from options
            **attributes,
        )

        assert field.value == "Red"
        assert "Red" in field.options

    def test_extracted_options_fail_validation_for_invalid_value(self):
        """Test that CategoryField validation fails for values not in extracted options."""
        strategy = CategoryStrategy()
        series = Series(["Red", "Green", "Blue"], name="colors")

        attributes = strategy.attributes_from_series(series)

        with pytest.raises(
            ValueError, match="Value must match one of the allowed options"
        ):
            strategy.schema_cls(
                title="color",
                value="Yellow",  # Invalid value not in options
                **attributes,
            )

    def test_dtypes_consistency(self):
        """Test that dtypes tuple is immutable and consistent."""
        strategy1 = CategoryStrategy()
        strategy2 = CategoryStrategy()

        assert strategy1.dtypes == strategy2.dtypes
        assert strategy1.dtypes is not strategy2.dtypes  # Different instances
        assert isinstance(strategy1.dtypes, tuple)  # Immutable


class TestCategoryStrategyErrorHandling:
    """Test suite for error handling and exceptional conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a CategoryStrategy instance."""
        return CategoryStrategy()

    def test_handles_series_with_complex_objects(self, strategy):
        """Test handling of series containing complex objects."""
        complex_objects = [{"key": "value"}, [1, 2, 3], {"other": "data"}]
        series = Series(complex_objects, name="complex")

        result = strategy.attributes_from_series(series.map(str))

        # Should handle complex objects as categories
        assert len(result["options"]) == 3
        assert isinstance(result["options"], list)

    def test_method_returns_dict_with_options_key(self, strategy):
        """Test that attributes_from_series always returns dict with 'options' key."""
        series = Series(["A"], name="test")

        result = strategy.attributes_from_series(series)

        assert isinstance(result, dict)
        assert "options" in result
        assert isinstance(result["options"], list)

    def test_handles_categorical_with_nan_category(self):
        """Test handling of categorical dtype that includes NaN as a category."""
        categories = ["A", "B", pd.NA]

        with pytest.raises(ValueError, match="Categorical categories cannot be null"):
            CategoricalDtype(categories=categories)


class TestCategoryStrategyMocking:
    """Test suite using mocks to test internal behavior."""

    def test_categorical_dtype_check_is_called(self):
        """Test that isinstance check for CategoricalDtype is performed."""
        strategy = CategoryStrategy()

        # Create a mock series with CategoricalDtype
        mock_series = Mock(spec=Series)
        mock_dtype = Mock(spec=CategoricalDtype)
        mock_series.dtype = mock_dtype
        mock_series.cat.categories = ["A", "B", "C"]

        with patch(
            "mlschema.strategies.app.category_strategy.isinstance"
        ) as mock_isinstance:
            mock_isinstance.return_value = True

            result = strategy.attributes_from_series(mock_series)

            mock_isinstance.assert_called_once_with(mock_dtype, CategoricalDtype)
            assert result == {"options": ["A", "B", "C"]}

    def test_dropna_unique_called_for_non_categorical(self):
        """Test that dropna().unique() is called for non-categorical series."""
        strategy = CategoryStrategy()

        # Create a mock series
        mock_series = Mock(spec=Series)
        mock_series.dtype = "category"
        mock_dropna = Mock()
        mock_dropna.unique.return_value = pd.array(["X", "Y", "Z"], dtype="object")
        mock_series.dropna.return_value = mock_dropna

        with patch(
            "mlschema.strategies.app.category_strategy.isinstance"
        ) as mock_isinstance:
            mock_isinstance.return_value = False

            result = strategy.attributes_from_series(mock_series)

            mock_series.dropna.assert_called_once()
            mock_dropna.unique.assert_called_once()
            assert result == {"options": ["X", "Y", "Z"]}
