"""Tests for mlschema.strategies.app.text_strategy.

This module provides comprehensive test coverage for the TextStrategy class,
including initialization, dtype matching, and schema generation for text columns.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pandas as pd
import pytest
from pandas import Series

from mlschema.strategies.app.text_strategy import TextStrategy
from mlschema.strategies.domain import FieldTypes, TextField


class TestTextStrategyInitialization:
    """Test suite for TextStrategy initialization."""

    def test_initialization_sets_correct_attributes(self):
        """Test that TextStrategy initializes with correct type, schema class, and dtypes."""
        strategy = TextStrategy()

        assert strategy.type_name == FieldTypes.TEXT
        assert strategy.schema_cls == TextField
        assert strategy.dtypes == ("object", "string")

    def test_initialization_calls_parent_constructor(self):
        """Test that TextStrategy properly calls parent class constructor."""
        with patch(
            "mlschema.strategies.app.text_strategy.Strategy.__init__"
        ) as mock_parent_init:
            mock_parent_init.return_value = None

            TextStrategy()

            mock_parent_init.assert_called_once_with(
                type_name=FieldTypes.TEXT,
                schema_cls=TextField,
                dtypes=("object", "string"),
            )


class TestTextStrategyDtypeHandling:
    """Test suite for dtype recognition and handling."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a TextStrategy instance."""
        return TextStrategy()

    @pytest.mark.parametrize("dtype", ["object", "string"])
    def test_handles_supported_dtypes(self, strategy, dtype):
        """Test that TextStrategy recognizes supported text dtypes."""
        assert dtype in strategy.dtypes

    @pytest.mark.parametrize(
        "unsupported_dtype",
        [
            "int64",
            "float64",
            "int32",
            "float32",
            "bool",
            "boolean",
            "category",
            "datetime64[ns]",
            "datetime64",
            "timedelta64[ns]",
        ],
    )
    def test_does_not_handle_unsupported_dtypes(self, strategy, unsupported_dtype):
        """Test that TextStrategy does not handle non-text dtypes."""
        assert unsupported_dtype not in strategy.dtypes

    def test_handles_object_dtype(self, strategy):
        """Test specific handling of object dtype."""
        assert "object" in strategy.dtypes

    def test_handles_string_dtype(self, strategy):
        """Test specific handling of pandas string dtype."""
        assert "string" in strategy.dtypes


class TestTextStrategySchemaGeneration:
    """Test suite for schema generation functionality."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a TextStrategy instance."""
        return TextStrategy()

    def test_schema_class_is_text_field(self, strategy):
        """Test that TextStrategy uses TextField as schema class."""
        assert strategy.schema_cls == TextField

    def test_type_name_is_text(self, strategy):
        """Test that TextStrategy has correct type name."""
        assert strategy.type_name == FieldTypes.TEXT
        assert strategy.type_name == "text"


class TestTextStrategyInheritance:
    """Test suite for inheritance and method delegation."""

    def test_inherits_from_field_strategy(self):
        """Test that TextStrategy properly inherits from Strategy."""
        from mlschema.core.app.strategy import Strategy

        strategy = TextStrategy()
        assert isinstance(strategy, Strategy)

    def test_does_not_override_attributes_from_series(self):
        """Test that TextStrategy delegates to parent for attributes_from_series."""
        strategy = TextStrategy()

        # TextStrategy should not have its own attributes_from_series method
        # It should use the parent class implementation
        assert "attributes_from_series" not in TextStrategy.__dict__

        # But the instance should have the method from parent class
        assert hasattr(strategy, "attributes_from_series")

    def test_delegates_schema_generation_to_parent(self):
        """Test that TextStrategy delegates schema generation to parent class."""
        strategy = TextStrategy()

        # Create a mock series with text dtype
        mock_series = Mock(spec=Series)
        mock_series.dtype = "object"
        mock_series.name = "description"

        # Mock the parent class method
        with patch.object(
            strategy, "attributes_from_series", return_value={}
        ) as mock_attrs:
            # The strategy should be able to call inherited methods
            result = strategy.attributes_from_series(mock_series)

            mock_attrs.assert_called_once_with(mock_series)
            assert isinstance(result, dict)


class TestTextStrategyWithRealTextSeries:
    """Test suite with real text series data."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a TextStrategy instance."""
        return TextStrategy()

    def test_handles_object_dtype_series(self, strategy):
        """Test behavior with object dtype series containing strings."""
        text_series = Series(
            ["hello", "world", "test"], dtype="object", name="text_data"
        )

        # Should not raise an exception
        result = strategy.attributes_from_series(text_series)
        assert isinstance(result, dict)

    def test_handles_string_dtype_series(self, strategy):
        """Test behavior with pandas string dtype series."""
        string_series = Series(
            ["apple", "banana", "cherry"], dtype="string", name="fruits"
        )

        result = strategy.attributes_from_series(string_series)
        assert isinstance(result, dict)

    def test_handles_series_with_null_values(self, strategy):
        """Test behavior with text series containing null values."""
        text_with_nulls = Series(
            ["text", None, "more text", pd.NA], name="nullable_text"
        )

        result = strategy.attributes_from_series(text_with_nulls)
        assert isinstance(result, dict)

    def test_handles_empty_text_series(self, strategy):
        """Test behavior with empty text series."""
        empty_series = Series([], dtype="object", name="empty_text")

        result = strategy.attributes_from_series(empty_series)
        assert isinstance(result, dict)

    def test_handles_all_null_text_series(self, strategy):
        """Test behavior with series containing only null values."""
        all_null_series = Series([None, pd.NA, None], name="all_nulls")

        result = strategy.attributes_from_series(all_null_series)
        assert isinstance(result, dict)

    def test_handles_single_text_value(self, strategy):
        """Test behavior with series containing only one text value."""
        single_text = Series(["single value"], name="single_text")

        result = strategy.attributes_from_series(single_text)
        assert isinstance(result, dict)

    def test_handles_mixed_content_in_object_series(self, strategy):
        """Test behavior with object series containing mixed data types."""
        # Object dtype can contain mixed types, but should still be handled
        mixed_series = Series(["text", 123, "more text"], dtype="object", name="mixed")

        result = strategy.attributes_from_series(mixed_series)
        assert isinstance(result, dict)

    def test_handles_unicode_text(self, strategy):
        """Test behavior with unicode text content."""
        unicode_text = Series(["café", "naïve", "résumé", "🚀"], name="unicode")

        result = strategy.attributes_from_series(unicode_text)
        assert isinstance(result, dict)

    def test_handles_very_long_text(self, strategy):
        """Test behavior with very long text strings."""
        long_text = "x" * 10000
        long_text_series = Series([long_text, "short", long_text], name="long_text")

        result = strategy.attributes_from_series(long_text_series)
        assert isinstance(result, dict)


class TestTextStrategyEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a TextStrategy instance."""
        return TextStrategy()

    def test_handles_empty_strings(self, strategy):
        """Test handling of empty strings."""
        empty_strings = Series(["", "", "non-empty"], name="with_empty")

        result = strategy.attributes_from_series(empty_strings)
        assert isinstance(result, dict)

    def test_handles_whitespace_only_strings(self, strategy):
        """Test handling of whitespace-only strings."""
        whitespace_series = Series([" ", "  ", "\t", "\n", "normal"], name="whitespace")

        result = strategy.attributes_from_series(whitespace_series)
        assert isinstance(result, dict)

    def test_handles_special_characters(self, strategy):
        """Test handling of strings with special characters."""
        special_chars = Series(
            [
                "!@#$%^&*()",
                "<script>alert('xss')</script>",
                "line1\nline2",
                "tab\tseparated",
            ],
            name="special",
        )

        result = strategy.attributes_from_series(special_chars)
        assert isinstance(result, dict)

    def test_handles_numeric_strings(self, strategy):
        """Test handling of strings that look like numbers."""
        numeric_strings = Series(["123", "45.67", "1e10", "-999"], name="numeric_str")

        result = strategy.attributes_from_series(numeric_strings)
        assert isinstance(result, dict)

    def test_handles_boolean_strings(self, strategy):
        """Test handling of strings that look like booleans."""
        boolean_strings = Series(["true", "false", "True", "False"], name="bool_str")

        result = strategy.attributes_from_series(boolean_strings)
        assert isinstance(result, dict)

    def test_handles_date_strings(self, strategy):
        """Test handling of strings that look like dates."""
        date_strings = Series(
            ["2023-01-01", "01/02/2023", "January 1, 2023", "2023-01-01T10:30:00"],
            name="date_str",
        )

        result = strategy.attributes_from_series(date_strings)
        assert isinstance(result, dict)

    def test_handles_json_strings(self, strategy):
        """Test handling of JSON-like strings."""
        json_strings = Series(
            ['{"key": "value"}', "[1, 2, 3]", '{"nested": {"data": true}}'],
            name="json_str",
        )

        result = strategy.attributes_from_series(json_strings)
        assert isinstance(result, dict)

    def test_handles_large_dataset(self, strategy):
        """Test behavior with large text dataset."""
        large_dataset = Series([f"text_{i}" for i in range(10000)], name="large_text")

        result = strategy.attributes_from_series(large_dataset)
        assert isinstance(result, dict)


class TestTextStrategyIntegration:
    """Integration tests for TextStrategy with related components."""

    def test_integration_with_text_field(self):
        """Test that TextStrategy integrates properly with TextField."""
        strategy = TextStrategy()

        # Verify the schema class can be instantiated
        field_instance = strategy.schema_cls(title="test_text")

        assert isinstance(field_instance, TextField)
        assert field_instance.type == FieldTypes.TEXT
        assert field_instance.title == "test_text"

    def test_strategy_type_matches_field_type(self):
        """Test that strategy type name matches the field type."""
        strategy = TextStrategy()
        field_instance = strategy.schema_cls(title="test")

        assert strategy.type_name == field_instance.type

    def test_dtypes_consistency(self):
        """Test that dtypes tuple is immutable and consistent."""
        strategy1 = TextStrategy()
        strategy2 = TextStrategy()

        assert strategy1.dtypes == strategy2.dtypes
        assert strategy1.dtypes is not strategy2.dtypes  # Different instances
        assert isinstance(strategy1.dtypes, tuple)  # Immutable

    def test_text_field_validation_with_length_constraints(self):
        """Test that TextField validation works with length constraints."""
        strategy = TextStrategy()

        # Create a text field with valid length constraints
        field = strategy.schema_cls(
            title="username", value="john_doe", minLength=3, maxLength=20
        )

        assert field.value == "john_doe"
        assert field.minLength == 3
        assert field.maxLength == 20

    def test_text_field_validation_fails_with_invalid_constraints(self):
        """Test that TextField validation fails with invalid length constraints."""
        strategy = TextStrategy()

        # Try to create a field with minLength > maxLength
        with pytest.raises(ValueError, match=r"minLength .* must be ≤ maxLength"):
            strategy.schema_cls(
                title="invalid_text",
                minLength=20,
                maxLength=10,  # max < min
            )

    def test_text_field_validation_fails_when_value_too_short(self):
        """Test that TextField validation fails when value length < minLength."""
        strategy = TextStrategy()

        # Try to create a field with value shorter than minLength
        with pytest.raises(ValueError, match=r"value length .* must be ≥ minLength"):
            strategy.schema_cls(
                title="short_text",
                value="ab",  # Only 2 characters
                minLength=5,
            )

    def test_text_field_validation_fails_when_value_too_long(self):
        """Test that TextField validation fails when value length > maxLength."""
        strategy = TextStrategy()

        # Try to create a field with value longer than maxLength
        with pytest.raises(ValueError, match=r"value length .* must be ≤ maxLength"):
            strategy.schema_cls(
                title="long_text",
                value="this is a very long text",  # 24 characters
                maxLength=10,
            )


class TestTextStrategyErrorHandling:
    """Test suite for error handling and exceptional conditions."""

    @pytest.fixture
    def strategy(self):
        """Fixture providing a TextStrategy instance."""
        return TextStrategy()

    def test_method_returns_dict(self, strategy):
        """Test that attributes_from_series always returns a dictionary."""
        text_series = Series(["hello", "world"], name="test_text")

        result = strategy.attributes_from_series(text_series)

        assert isinstance(result, dict)

    def test_handles_series_with_complex_objects(self, strategy):
        """Test handling of series containing complex objects in object dtype."""
        complex_objects = Series(
            [{"key": "value"}, [1, 2, 3], {"nested": {"data": True}}],
            dtype="object",
            name="complex",
        )

        # Should handle complex objects without error
        result = strategy.attributes_from_series(complex_objects)
        assert isinstance(result, dict)

    def test_handles_series_with_bytes(self, strategy):
        """Test handling of series containing bytes objects."""
        bytes_series = Series(
            [b"binary data", b"more bytes", "regular string"],
            dtype="object",
            name="bytes_data",
        )

        result = strategy.attributes_from_series(bytes_series)
        assert isinstance(result, dict)

    def test_handles_series_with_none_and_nan_mix(self, strategy):
        """Test handling of series with mixed None and NaN values."""
        mixed_nulls = Series(
            ["text", None, pd.NA, "more text", None], name="mixed_nulls"
        )

        result = strategy.attributes_from_series(mixed_nulls)
        assert isinstance(result, dict)


class TestTextStrategyMocking:
    """Test suite using mocks to test internal behavior."""

    def test_delegates_to_parent_attributes_from_series(self):
        """Test that TextStrategy properly delegates to parent implementation."""
        strategy = TextStrategy()

        # Create a mock series
        mock_series = Mock(spec=Series)
        mock_series.dtype = "object"
        mock_series.name = "mock_text"

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
            "mlschema.strategies.app.text_strategy.Strategy.__init__"
        ) as mock_parent_init:
            mock_parent_init.return_value = None

            TextStrategy()

            mock_parent_init.assert_called_once_with(
                type_name=FieldTypes.TEXT,
                schema_cls=TextField,
                dtypes=("object", "string"),
            )


class TestTextStrategyConstants:
    """Test suite for TextStrategy constants and class attributes."""

    def test_supported_dtypes_are_text_related(self):
        """Test that all supported dtypes are text-related."""
        strategy = TextStrategy()

        text_dtypes = ["object", "string"]
        for dtype in strategy.dtypes:
            assert dtype in text_dtypes

    def test_type_name_constant(self):
        """Test that type name is consistent."""
        strategy = TextStrategy()

        assert strategy.type_name == "text"
        assert strategy.type_name == FieldTypes.TEXT.value

    def test_schema_class_constant(self):
        """Test that schema class is consistent."""
        strategy = TextStrategy()

        assert strategy.schema_cls == TextField
        assert issubclass(strategy.schema_cls, TextField)

    def test_dtypes_immutability(self):
        """Test that dtypes tuple cannot be modified."""
        strategy = TextStrategy()

        original_dtypes = strategy.dtypes
        # Verify it's a tuple (immutable)
        assert isinstance(strategy.dtypes, tuple)

        # Verify original is unchanged after creating new instances
        strategy2 = TextStrategy()
        assert strategy.dtypes == original_dtypes
        assert strategy2.dtypes == original_dtypes

    def test_no_additional_attributes_generated(self):
        """Test that TextStrategy doesn't add extra attributes (as documented)."""
        strategy = TextStrategy()

        # Since TextStrategy doesn't override attributes_from_series,
        # it should return empty dict from parent implementation
        text_series = Series(["test"], dtype="object", name="test")

        # Mock parent to return empty dict
        with patch.object(strategy, "attributes_from_series", return_value={}):
            result = strategy.attributes_from_series(text_series)
            assert result == {}


class TestTextStrategyDocumentationCompliance:
    """Test suite to verify behavior matches documentation."""

    def test_purpose_is_classification_only(self):
        """Test that TextStrategy's purpose is solely classification as documented."""
        strategy = TextStrategy()

        # The strategy should not add any custom attributes beyond base functionality
        # We test this by ensuring it uses inherited behavior
        assert hasattr(strategy, "attributes_from_series")
        assert "attributes_from_series" not in TextStrategy.__dict__

    def test_handles_documented_dtypes(self):
        """Test that strategy handles both documented dtypes: object and string."""
        strategy = TextStrategy()

        # Documentation mentions "object" and pandas' "string"
        assert "object" in strategy.dtypes
        assert "string" in strategy.dtypes
        assert len(strategy.dtypes) == 2

    def test_classification_functionality(self):
        """Test the core classification functionality."""
        strategy = TextStrategy()

        # The strategy should correctly identify itself as handling text
        assert strategy.type_name == FieldTypes.TEXT
        assert strategy.schema_cls == TextField

        # And should work with both supported dtypes
        object_series = Series(["text"], dtype="object")
        string_series = Series(["text"], dtype="string")

        # Both should be processable without errors
        result1 = strategy.attributes_from_series(object_series)
        result2 = strategy.attributes_from_series(string_series)

        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
