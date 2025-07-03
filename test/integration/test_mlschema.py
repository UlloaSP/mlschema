"""Integration tests for mlschema.mls.

This module provides comprehensive integration tests for the MLSchema class,
testing real usage scenarios without mocks, using actual pandas DataFrames
and field strategies.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest
from pandas import DataFrame, Series

from mlschema.core.app.field_registry import FieldRegistry
from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.core.domain.base_field import BaseField
from mlschema.mls import MLSchema
from mlschema.strategies.app import (
    BooleanStrategy,
    CategoryStrategy,
    DateStrategy,
    NumberStrategy,
    TextStrategy,
)


def parse_mlschema_json(json_string: str) -> dict:
    """Parse MLSchema JSON output which uses 'undefined' instead of 'null'."""
    # Replace 'undefined' with 'null' to make it valid JSON
    valid_json = json_string.replace("undefined", "null")
    return json.loads(valid_json)


# Custom test strategy for integration testing
class CustomField(BaseField):
    """Custom field type for testing."""

    type: str = "custom"
    unit: str | None = None
    custom_attr: str | None = None
    min_seconds: int | None = None
    max_seconds: int | None = None


class CustomStrategy(FieldStrategy):
    """Custom strategy for testing purposes."""

    def __init__(self) -> None:
        super().__init__(
            type_name="custom",
            schema_cls=CustomField,
            dtypes=("timedelta64[ns]",),
        )

    def attributes_from_series(self, series: Series) -> dict:
        """Add custom attributes for timedelta series."""
        return {
            "unit": "seconds",
            "custom_attr": "test_value",
            "min_seconds": int(series.min().total_seconds()) if not series.empty else 0,
            "max_seconds": int(series.max().total_seconds()) if not series.empty else 0,
        }


class AdvancedNumberField(BaseField):
    """Advanced number field with additional attributes."""

    type: str = "advanced_number"
    step: float | None = None
    mean: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    modified: bool | None = None


class AdvancedNumberStrategy(FieldStrategy):
    """Advanced number strategy with additional validation."""

    def __init__(self) -> None:
        super().__init__(
            type_name="advanced_number",
            schema_cls=AdvancedNumberField,
            dtypes=("float64",),
        )

    def attributes_from_series(self, series: Series) -> dict:
        """Add advanced attributes for numeric series."""
        clean_series = series.dropna()

        return {
            "step": 0.01,  # More precise step
            "mean": float(clean_series.mean()),
            "std": float(clean_series.std()),
            "min": float(clean_series.min()),
            "max": float(clean_series.max()),
        }


class TestMLSchemaIntegrationBasics:
    """Test basic MLSchema functionality with real data."""

    def test_initialization_with_default_strategies(self):
        """Test that MLSchema initializes correctly."""
        ml_schema = MLSchema()

        assert ml_schema.field_service is not None
        assert hasattr(ml_schema, "register")
        assert hasattr(ml_schema, "unregister")
        assert hasattr(ml_schema, "update")
        assert hasattr(ml_schema, "build")

    def test_register_and_build_with_built_in_strategies(self):
        """Test registering built-in strategies and building schema."""
        ml_schema = MLSchema()

        # Register all built-in strategies
        ml_schema.register(
            [
                BooleanStrategy(),
                NumberStrategy(),
                TextStrategy(),
                DateStrategy(),
                CategoryStrategy(),
            ]
        )

        # Create test DataFrame with various data types
        df = DataFrame(
            {
                "age": [25, 30, 35, 40],
                "name": ["Alice", "Bob", "Charlie", "Diana"],
                "salary": [50000.0, 60000.0, 70000.0, 80000.0],
                "is_active": [True, False, True, True],
                "join_date": pd.date_range("2020-01-01", periods=4, freq="YS"),
                "department": pd.Categorical(["IT", "HR", "IT", "Finance"]),
            }
        )

        result = ml_schema.build(df)

        # Verify result is valid JSON
        assert isinstance(result, str)
        # Should contain JSON data (will end with semicolon from field_service)
        json_data = parse_mlschema_json(result.rstrip(";"))
        assert "input" in json_data
        assert len(json_data["input"]) == 6  # 6 columns


class TestMLSchemaCustomStrategies:
    """Test MLSchema with custom strategies."""

    def test_register_custom_strategy(self):
        """Test registering a custom strategy."""
        ml_schema = MLSchema()
        custom_strategy = CustomStrategy()

        ml_schema.register(custom_strategy)

        # Create DataFrame with timedelta column
        df = DataFrame({"duration": pd.timedelta_range("1 day", periods=3, freq="D")})

        result = ml_schema.build(df)

        # Verify custom strategy was used
        json_data = parse_mlschema_json(result.rstrip(";"))
        field_schema = json_data["input"][0]

        assert field_schema["type"] == "custom"
        assert field_schema["unit"] == "seconds"
        assert field_schema["custom_attr"] == "test_value"
        assert "min_seconds" in field_schema
        assert "max_seconds" in field_schema

    def test_register_multiple_custom_strategies(self):
        """Test registering multiple custom strategies."""
        ml_schema = MLSchema()

        strategies = [
            CustomStrategy(),
            AdvancedNumberStrategy(),
            TextStrategy(),  # Built-in strategy
        ]

        ml_schema.register(strategies)

        # Create DataFrame that uses multiple strategies
        df = DataFrame(
            {
                "duration": pd.timedelta_range("1 day", periods=3, freq="D"),
                "score": [1.5, 2.7, 3.9],
                "comment": ["good", "excellent", "amazing"],
            }
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))

        assert len(json_data["input"]) == 3

        # Check each field type
        duration_schema = json_data["input"][0]
        score_schema = json_data["input"][1]
        comment_schema = json_data["input"][2]

        assert duration_schema["type"] == "custom"
        assert score_schema["type"] == "advanced_number"
        assert comment_schema["type"] == "text"

    def test_update_strategy(self):
        """Test updating an existing strategy."""
        ml_schema = MLSchema()

        # Register initial strategy
        initial_strategy = AdvancedNumberStrategy()
        ml_schema.register(initial_strategy)

        # Create a modified strategy with same type_name
        class ModifiedNumberField(BaseField):
            """Modified number field for testing."""

            type: str = "advanced_number"
            step: float | None = None
            modified: bool | None = None

        class ModifiedNumberStrategy(FieldStrategy):
            def __init__(self) -> None:
                super().__init__(
                    type_name="advanced_number",  # Same type name
                    schema_cls=ModifiedNumberField,
                    dtypes=("float64",),
                )

            def attributes_from_series(self, series: Series) -> dict:
                return {"step": 1.0, "modified": True}  # Different attributes

        updated_strategy = ModifiedNumberStrategy()
        ml_schema.update(updated_strategy)

        df = DataFrame({"score": [1.5, 2.7, 3.9]})
        result = ml_schema.build(df)

        json_data = parse_mlschema_json(result.rstrip(";"))
        field_schema = json_data["input"][0]

        # Should use updated strategy
        assert field_schema["step"] == 1.0
        assert field_schema["modified"] is True
        assert "mean" not in field_schema  # Old attribute removed

    def test_unregister_strategy(self):
        """Test unregistering a strategy."""
        ml_schema = MLSchema()

        # Register strategies
        custom_strategy = CustomStrategy()
        text_strategy = TextStrategy()

        ml_schema.register([custom_strategy, text_strategy])

        # Unregister custom strategy
        ml_schema.unregister(custom_strategy)

        # Create DataFrame that would use custom strategy
        df = DataFrame(
            {
                "duration": pd.timedelta_range("1 day", periods=3, freq="D"),
                "comment": ["test1", "test2", "test3"],
            }
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))

        # Duration should fall back to text strategy (if available)
        # or raise an error if no fallback
        duration_schema = json_data["input"][0]
        comment_schema = json_data["input"][1]

        # Custom strategy should no longer be used
        assert duration_schema["type"] == "text"  # Fallback
        assert comment_schema["type"] == "text"


class TestMLSchemaComplexDataFrames:
    """Test MLSchema with complex DataFrame scenarios."""

    def test_mixed_data_types_dataframe(self):
        """Test with DataFrame containing all supported data types."""
        ml_schema = MLSchema()

        # Register all strategies
        ml_schema.register(
            [
                BooleanStrategy(),
                NumberStrategy(),
                TextStrategy(),
                DateStrategy(),
                CategoryStrategy(),
            ]
        )

        # Create complex DataFrame
        df = DataFrame(
            {
                "id": range(1, 6),
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "age": [25, 30, 35, 40, 45],
                "salary": [50000.5, 60000.7, 70000.3, 80000.9, 90000.1],
                "is_manager": [False, True, False, True, False],
                "hire_date": pd.date_range("2020-01-01", periods=5, freq="6ME"),
                "department": pd.Categorical(["IT", "HR", "IT", "Finance", "IT"]),
                "comments": ["Good", None, "Excellent", "Average", "Outstanding"],
            }
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))

        assert len(json_data["input"]) == 8

        # Verify each field type
        schemas = json_data["input"]
        types = [schema["type"] for schema in schemas]

        expected_types = [
            "number",
            "text",
            "number",
            "number",
            "boolean",
            "date",
            "category",
            "text",
        ]
        assert types == expected_types

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        ml_schema = MLSchema()
        ml_schema.register(TextStrategy())

        # Empty DataFrame with columns
        df = DataFrame(columns=["name", "age"])

        with pytest.raises(ValueError):
            ml_schema.build(df)

    def test_dataframe_with_all_null_columns(self):
        """Test with DataFrame containing columns with all null values."""
        ml_schema = MLSchema()
        ml_schema.register([NumberStrategy(), TextStrategy()])

        df = DataFrame(
            {"null_numbers": [None, None, None], "null_text": [None, None, None]}
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))

        # Should still generate schemas
        assert len(json_data["input"]) == 2
        schemas = json_data["input"]

        # All should be marked as not required
        for schema in schemas:
            assert schema["required"] is False

    def test_large_dataframe(self):
        """Test with large DataFrame."""
        ml_schema = MLSchema()
        ml_schema.register([NumberStrategy(), TextStrategy(), BooleanStrategy()])

        # Create large DataFrame
        size = 10000
        df = DataFrame(
            {
                "id": range(size),
                "value": [i * 0.1 for i in range(size)],
                "category": [f"cat_{i % 100}" for i in range(size)],
                "flag": [i % 2 == 0 for i in range(size)],
            }
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))

        assert len(json_data["input"]) == 4

        # Verify performance - should complete without timeout
        schemas = json_data["input"]
        assert all("type" in schema for schema in schemas)


class TestMLSchemaEdgeCases:
    """Test MLSchema edge cases and error scenarios."""

    def test_strategy_conflict_resolution(self):
        """Test behavior when multiple strategies could handle same dtype."""
        ml_schema = MLSchema()

        # Register overlapping strategies using update to allow overwriting
        class AlternativeTextField(BaseField):
            """Alternative text field for testing."""

            type: str = "alternative_text"

        class AlternativeTextStrategy(FieldStrategy):
            def __init__(self) -> None:
                super().__init__(
                    type_name="alternative_text",
                    schema_cls=AlternativeTextField,
                    dtypes=("object",),  # Same as TextStrategy
                )

        text_strategy = TextStrategy()
        alt_strategy = AlternativeTextStrategy()

        ml_schema.register(text_strategy)

        # This should overwrite the first strategy using update
        ml_schema.update(alt_strategy)

        df = DataFrame({"text_col": ["a", "b", "c"]})
        result = ml_schema.build(df)

        json_data = parse_mlschema_json(result.rstrip(";"))
        schema = json_data["input"][0]

        # Should use the last registered strategy
        assert schema["type"] == "alternative_text"

    def test_unsupported_dtype_fallback(self):
        """Test fallback behavior for unsupported dtypes."""
        ml_schema = MLSchema()
        ml_schema.register(TextStrategy())  # Only text strategy

        # Create DataFrame with unsupported dtype
        df = DataFrame(
            {
                "complex_numbers": [1 + 2j, 3 + 4j, 5 + 6j],  # Complex numbers
                "text_col": ["a", "b", "c"],
            }
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))

        # Both should fall back to text strategy
        schemas = json_data["input"]
        assert all(schema["type"] == "text" for schema in schemas)

    def test_strategy_registration_order_independence(self):
        """Test that strategy registration order doesn't affect final schema."""
        # Create two MLSchema instances with strategies in different order
        ml_schema1 = MLSchema()
        ml_schema2 = MLSchema()

        strategies = [NumberStrategy(), TextStrategy(), BooleanStrategy()]

        ml_schema1.register(strategies)
        ml_schema2.register(list(reversed(strategies)))

        df = DataFrame(
            {"num": [1, 2, 3], "text": ["a", "b", "c"], "bool": [True, False, True]}
        )

        result1 = ml_schema1.build(df)
        result2 = ml_schema2.build(df)

        # Results should be identical
        assert result1 == result2

    def test_series_with_mixed_types_in_object_column(self):
        """Test handling of object columns with mixed types."""
        ml_schema = MLSchema()
        ml_schema.register([NumberStrategy(), TextStrategy()])

        df = DataFrame(
            {
                "mixed_col": [1, "text", 3.14, None, True]  # Mixed types
            }
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))
        schema = json_data["input"][0]

        # Should be classified as text (object dtype)
        assert schema["type"] == "text"


class TestMLSchemaIntegrationErrorHandling:
    """Test error handling in integration scenarios."""

    def test_build_without_registered_strategies(self):
        """Test building schema without any registered strategies."""
        ml_schema = MLSchema()

        df = DataFrame({"col1": [1, 2, 3]})

        # Should raise error when no strategies are available
        with pytest.raises(RuntimeError):
            ml_schema.build(df)

    def test_invalid_custom_strategy_registration(self):
        """Test error handling for invalid strategy registration."""
        ml_schema = MLSchema()

        # Try to register non-strategy object
        with pytest.raises(AttributeError):
            ml_schema.register("not_a_strategy")  # type: ignore[arg-type]

    def test_strategy_that_raises_exception(self):
        """Test handling of strategies that raise exceptions."""

        class BuggyStrategy(FieldStrategy):
            def __init__(self) -> None:
                super().__init__(
                    type_name="buggy",
                    schema_cls=BaseField,
                    dtypes=("int64",),
                )

            def attributes_from_series(self, series: Series) -> dict:
                raise ValueError("Intentional error in strategy")

        ml_schema = MLSchema()
        ml_schema.register(BuggyStrategy())

        df = DataFrame({"num_col": [1, 2, 3]})

        # Should propagate the exception
        with pytest.raises(ValueError, match="Intentional error in strategy"):
            ml_schema.build(df)

    def test_duplicate_type_name_registration(self):
        """Test error when registering strategy with duplicate type_name."""
        ml_schema = MLSchema()

        # Register first strategy
        first_strategy = NumberStrategy()
        ml_schema.register(first_strategy)

        # Create another strategy with same type_name
        class DuplicateNumberStrategy(FieldStrategy):
            def __init__(self) -> None:
                super().__init__(
                    type_name="number",  # Same as NumberStrategy
                    schema_cls=BaseField,
                    dtypes=("int32",),  # Different dtype
                )

        duplicate_strategy = DuplicateNumberStrategy()

        # Should raise ValueError when trying to register duplicate type_name
        with pytest.raises(ValueError, match="Strategy 'number' already exists"):
            ml_schema.register(duplicate_strategy)

    def test_duplicate_dtype_registration(self):
        """Test error when registering strategy with duplicate dtype."""
        ml_schema = MLSchema()

        # Register first strategy
        first_strategy = NumberStrategy()
        ml_schema.register(first_strategy)

        # Create another strategy with overlapping dtype
        class OverlappingStrategy(FieldStrategy):
            def __init__(self) -> None:
                super().__init__(
                    type_name="overlapping_number",
                    schema_cls=BaseField,
                    dtypes=("int64",),  # Same dtype as NumberStrategy
                )

        overlapping_strategy = OverlappingStrategy()

        # Should raise ValueError when trying to register duplicate dtype
        with pytest.raises(
            ValueError, match="dtype 'int64' already linked to another strategy."
        ):
            ml_schema.register(overlapping_strategy)


class TestMLSchemaRealWorldScenarios:
    """Test MLSchema with realistic data scenarios."""

    def test_customer_data_scenario(self):
        """Test with realistic customer data."""
        ml_schema = MLSchema()
        ml_schema.register(
            [
                NumberStrategy(),
                TextStrategy(),
                BooleanStrategy(),
                DateStrategy(),
                CategoryStrategy(),
            ]
        )

        # Realistic customer dataset
        df = DataFrame(
            {
                "customer_id": range(1000, 1010),
                "first_name": [
                    "John",
                    "Jane",
                    "Bob",
                    "Alice",
                    "Charlie",
                    "Diana",
                    "Eve",
                    "Frank",
                    "Grace",
                    "Henry",
                ],
                "last_name": [
                    "Doe",
                    "Smith",
                    "Johnson",
                    "Brown",
                    "Davis",
                    "Miller",
                    "Wilson",
                    "Moore",
                    "Taylor",
                    "Anderson",
                ],
                "age": [25, 34, 45, 28, 36, 42, 31, 29, 38, 44],
                "annual_income": [
                    45000.0,
                    67000.0,
                    89000.0,
                    52000.0,
                    74000.0,
                    81000.0,
                    58000.0,
                    49000.0,
                    92000.0,
                    76000.0,
                ],
                "is_premium": [
                    False,
                    True,
                    True,
                    False,
                    True,
                    True,
                    False,
                    False,
                    True,
                    True,
                ],
                "registration_date": pd.date_range("2020-01-01", periods=10, freq="ME"),
                "customer_segment": pd.Categorical(
                    [
                        "Bronze",
                        "Silver",
                        "Gold",
                        "Bronze",
                        "Silver",
                        "Gold",
                        "Bronze",
                        "Bronze",
                        "Gold",
                        "Silver",
                    ]
                ),
                "email": [f"user{i}@example.com" for i in range(10)],
            }
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))

        assert len(json_data["input"]) == 9

        # Verify realistic field types
        schemas = json_data["input"]
        field_types = {schema["title"]: schema["type"] for schema in schemas}

        expected_types = {
            "customer_id": "number",
            "first_name": "text",
            "last_name": "text",
            "age": "number",
            "annual_income": "number",
            "is_premium": "boolean",
            "registration_date": "date",
            "customer_segment": "category",
            "email": "text",
        }

        assert field_types == expected_types

    def test_time_series_data_scenario(self):
        """Test with time series data."""
        ml_schema = MLSchema()
        ml_schema.register(
            [
                DateStrategy(),
                NumberStrategy(),
                TextStrategy(),
            ]
        )

        # Time series dataset
        dates = pd.date_range("2023-01-01", periods=100, freq="D")
        df = DataFrame(
            {
                "timestamp": dates,
                "temperature": [20 + 10 * (i % 30) / 30 for i in range(100)],
                "humidity": [50 + 20 * ((i * 3) % 40) / 40 for i in range(100)],
                "location": ["Station_A"] * 50 + ["Station_B"] * 50,
            }
        )

        result = ml_schema.build(df)
        json_data = parse_mlschema_json(result.rstrip(";"))

        assert len(json_data["input"]) == 4

        # Check time series specific attributes
        schemas = json_data["input"]
        temp_schema = next(s for s in schemas if s["title"] == "temperature")

        # Should have numeric step attribute
        assert "step" in temp_schema
        assert temp_schema["type"] == "number"

    def test_multiple_instances_independence(self):
        """Test that multiple MLSchema instances are independent."""
        ml_schema1 = MLSchema()
        ml_schema2 = MLSchema()

        # Register different strategies to each instance
        ml_schema1.register(NumberStrategy())
        ml_schema2.register([NumberStrategy(), TextStrategy()])

        df = DataFrame({"num_col": [1, 2, 3], "text_col": ["a", "b", "c"]})

        # ml_schema1 should fail on text column (no text strategy)
        with pytest.raises(RuntimeError):
            ml_schema1.build(df)

        # ml_schema2 should succeed
        result2 = ml_schema2.build(df)
        json_data2 = parse_mlschema_json(result2.rstrip(";"))
        assert len(json_data2["input"]) == 2


class TestFieldRegistryNormalizeDtype:
    """Test the _normalize_dtype method covering all branches."""

    def test_normalize_dtype_with_numpy_dtype(self):
        """Test _normalize_dtype with numpy dtype objects."""
        registry = FieldRegistry()

        # Test with various numpy dtypes
        int_dtype = np.dtype("int64")
        float_dtype = np.dtype("float64")
        bool_dtype = np.dtype("bool")
        object_dtype = np.dtype("object")

        # Should return dtype.name for numpy dtypes
        assert registry._normalize_dtype(int_dtype) == "int64"
        assert registry._normalize_dtype(float_dtype) == "float64"
        assert registry._normalize_dtype(bool_dtype) == "bool"
        assert registry._normalize_dtype(object_dtype) == "object"

    def test_normalize_dtype_with_pandas_extension_dtype(self):
        """Test _normalize_dtype with pandas extension dtypes."""
        registry = FieldRegistry()

        # Test with pandas extension dtypes
        categorical_dtype = pd.CategoricalDtype(["A", "B", "C"])

        # Should return dtype.name for extension dtypes
        assert registry._normalize_dtype(categorical_dtype) == "category"

        # Test with other extension dtypes if available
        if hasattr(pd, "StringDtype"):
            string_dtype = pd.StringDtype()
            assert registry._normalize_dtype(string_dtype) == "string"

    def test_normalize_dtype_with_string(self):
        """Test _normalize_dtype with string inputs."""
        registry = FieldRegistry()

        # Test with string dtype names
        assert registry._normalize_dtype("int64") == "int64"
        assert registry._normalize_dtype("float64") == "float64"
        assert registry._normalize_dtype("object") == "object"
        assert registry._normalize_dtype("bool") == "bool"
        assert registry._normalize_dtype("datetime64[ns]") == "datetime64[ns]"
        assert registry._normalize_dtype("timedelta64[ns]") == "timedelta64[ns]"

    def test_normalize_dtype_with_other_types(self):
        """Test _normalize_dtype with other non-dtype types."""
        registry = FieldRegistry()

        # Test with other types that should be converted to string
        assert registry._normalize_dtype(42) == "42"
        assert registry._normalize_dtype(3.14) == "3.14"
        assert registry._normalize_dtype(True) == "True"
        assert registry._normalize_dtype(["list"]) == "['list']"
        assert registry._normalize_dtype({"dict": "value"}) == "{'dict': 'value'}"

    def test_normalize_dtype_edge_cases(self):
        """Test _normalize_dtype with edge cases."""
        registry = FieldRegistry()

        # Test with None (should convert to string)
        assert registry._normalize_dtype(None) == "None"

        # Test with empty string
        assert registry._normalize_dtype("") == ""

        # Test with complex numpy dtypes
        complex_dtype = np.dtype("complex128")
        assert registry._normalize_dtype(complex_dtype) == "complex128"

        # Test with structured numpy dtype (has .names that is not None)
        structured_dtype = np.dtype([("x", "f4"), ("y", "i4")])
        result = registry._normalize_dtype(structured_dtype)
        assert isinstance(result, str)
        assert "x" in result and "y" in result

        # Test edge case: object with .name but .names is None
        class MockDtypeWithNullNames:
            def __init__(self):
                self.name = "mock_dtype"
                self.names = None  # This is the edge case

        mock_dtype = MockDtypeWithNullNames()
        assert registry._normalize_dtype(mock_dtype) == "mock_dtype"

        # Test edge case: object with .name but no .names attribute
        class MockDtypeWithoutNames:
            def __init__(self):
                self.name = "mock_dtype_no_names"

        mock_dtype_no_names = MockDtypeWithoutNames()
        assert registry._normalize_dtype(mock_dtype_no_names) == "mock_dtype_no_names"
