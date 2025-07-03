"""Tests for mlschema.mls.

This module provides comprehensive test coverage for the MLSchema class,
including registration, unregistration, updating of field strategies,
and schema building from pandas DataFrames.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pandas as pd
import pytest
from pandas import DataFrame

from mlschema.core.app import FieldService, FieldStrategy
from mlschema.mls import MLSchema


class TestMLSchemaInitialization:
    """Test suite for MLSchema initialization."""

    def test_initialization_creates_field_service(self):
        """Test that MLSchema initializes with a FieldService instance."""
        ml_schema = MLSchema()

        assert hasattr(ml_schema, "field_service")
        assert isinstance(ml_schema.field_service, FieldService)

    def test_each_instance_has_separate_field_service(self):
        """Test that each MLSchema instance has its own FieldService."""
        ml_schema1 = MLSchema()
        ml_schema2 = MLSchema()

        assert ml_schema1.field_service is not ml_schema2.field_service

    @patch("mlschema.mls.FieldService")
    def test_initialization_calls_field_service_constructor(self, mock_field_service):
        """Test that MLSchema initialization calls FieldService constructor."""
        mock_instance = Mock()
        mock_field_service.return_value = mock_instance

        ml_schema = MLSchema()

        mock_field_service.assert_called_once()
        assert ml_schema.field_service == mock_instance


class TestMLSchemaRegister:
    """Test suite for register method."""

    def test_register_single_strategy(self):
        """Test registering a single field strategy."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        with patch.object(ml_schema.field_service, "register") as mock_register:
            ml_schema.register(mock_strategy)

            mock_register.assert_called_once_with(mock_strategy)

    def test_register_list_of_strategies(self):
        """Test registering a list of field strategies."""
        ml_schema = MLSchema()
        mock_strategy1 = Mock(spec=FieldStrategy)
        mock_strategy2 = Mock(spec=FieldStrategy)
        strategies: list[FieldStrategy] = [mock_strategy1, mock_strategy2]

        with patch.object(ml_schema.field_service, "register_all") as mock_register_all:
            ml_schema.register(strategies)

            mock_register_all.assert_called_once_with(strategies)

    def test_register_empty_list(self):
        """Test registering an empty list of strategies."""
        ml_schema = MLSchema()
        empty_list: list[FieldStrategy] = []

        with patch.object(ml_schema.field_service, "register_all") as mock_register_all:
            ml_schema.register(empty_list)

            mock_register_all.assert_called_once_with(empty_list)

    def test_register_single_strategy_in_list(self):
        """Test registering a list with a single strategy."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)
        single_strategy_list: list[FieldStrategy] = [mock_strategy]

        with patch.object(ml_schema.field_service, "register_all") as mock_register_all:
            ml_schema.register(single_strategy_list)

            mock_register_all.assert_called_once_with(single_strategy_list)

    def test_register_delegates_to_field_service(self):
        """Test that register method properly delegates to field service."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        # Mock the field service to verify delegation
        ml_schema.field_service = Mock(spec=FieldService)

        ml_schema.register(mock_strategy)

        ml_schema.field_service.register.assert_called_once_with(mock_strategy)

    def test_register_type_checking_behavior(self):
        """Test the type checking behavior in register method."""
        ml_schema = MLSchema()

        # Test with actual FieldStrategy mock
        strategy = Mock(spec=FieldStrategy)
        strategy_list: list[FieldStrategy] = [strategy]

        with (
            patch.object(ml_schema.field_service, "register") as mock_register,
            patch.object(ml_schema.field_service, "register_all") as mock_register_all,
        ):
            # Single strategy should call register
            ml_schema.register(strategy)
            mock_register.assert_called_once_with(strategy)

            # List should call register_all
            ml_schema.register(strategy_list)
            mock_register_all.assert_called_once_with(strategy_list)


class TestMLSchemaUnregister:
    """Test suite for unregister method."""

    def test_unregister_strategy(self):
        """Test unregistering a field strategy."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        with patch.object(ml_schema.field_service, "unregister") as mock_unregister:
            ml_schema.unregister(mock_strategy)

            mock_unregister.assert_called_once_with(mock_strategy)

    def test_unregister_delegates_to_field_service(self):
        """Test that unregister method properly delegates to field service."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        # Mock the field service to verify delegation
        ml_schema.field_service = Mock(spec=FieldService)

        ml_schema.unregister(mock_strategy)

        ml_schema.field_service.unregister.assert_called_once_with(mock_strategy)

    def test_unregister_with_none_strategy(self):
        """Test unregister behavior with None strategy."""
        ml_schema = MLSchema()

        with patch.object(ml_schema.field_service, "unregister") as mock_unregister:
            ml_schema.unregister(None)  # type: ignore[arg-type]

            mock_unregister.assert_called_once_with(None)

    def test_unregister_nonexistent_strategy(self):
        """Test unregistering a strategy that was never registered."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        # This should delegate to field service without error
        with patch.object(ml_schema.field_service, "unregister") as mock_unregister:
            ml_schema.unregister(mock_strategy)

            mock_unregister.assert_called_once_with(mock_strategy)


class TestMLSchemaUpdate:
    """Test suite for update method."""

    def test_update_strategy(self):
        """Test updating a field strategy."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        with patch.object(ml_schema.field_service, "update") as mock_update:
            ml_schema.update(mock_strategy)

            mock_update.assert_called_once_with(mock_strategy)

    def test_update_delegates_to_field_service(self):
        """Test that update method properly delegates to field service."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        # Mock the field service to verify delegation
        ml_schema.field_service = Mock(spec=FieldService)

        ml_schema.update(mock_strategy)

        ml_schema.field_service.update.assert_called_once_with(mock_strategy)

    def test_update_with_none_strategy(self):
        """Test update behavior with None strategy."""
        ml_schema = MLSchema()

        with patch.object(ml_schema.field_service, "update") as mock_update:
            ml_schema.update(None)  # type: ignore[arg-type]

            mock_update.assert_called_once_with(None)

    def test_update_new_strategy(self):
        """Test updating a strategy that doesn't exist (should register as new)."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        # According to docstring, if strategy doesn't exist, it should be registered as new
        with patch.object(ml_schema.field_service, "update") as mock_update:
            ml_schema.update(mock_strategy)

            mock_update.assert_called_once_with(mock_strategy)


class TestMLSchemaBuild:
    """Test suite for build method."""

    def test_build_with_dataframe(self):
        """Test building schema from a DataFrame."""
        ml_schema = MLSchema()
        df = DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        expected_json = '{"schema": "data"}'

        with patch.object(
            ml_schema.field_service, "build", return_value=expected_json
        ) as mock_build:
            result = ml_schema.build(df)

            mock_build.assert_called_once_with(df)
            assert result == expected_json

    def test_build_delegates_to_field_service(self):
        """Test that build method properly delegates to field service."""
        ml_schema = MLSchema()
        df = DataFrame({"test": [1, 2, 3]})

        # Mock the field service to verify delegation
        ml_schema.field_service = Mock(spec=FieldService)
        ml_schema.field_service.build.return_value = '{"test": "json"}'

        result = ml_schema.build(df)

        ml_schema.field_service.build.assert_called_once_with(df)
        assert result == '{"test": "json"}'

    def test_build_with_empty_dataframe(self):
        """Test building schema from an empty DataFrame."""
        ml_schema = MLSchema()
        empty_df = DataFrame()
        expected_json = '{"fields": []}'

        with patch.object(
            ml_schema.field_service, "build", return_value=expected_json
        ) as mock_build:
            result = ml_schema.build(empty_df)

            mock_build.assert_called_once_with(empty_df)
            assert result == expected_json

    def test_build_return_type_is_string(self):
        """Test that build method returns a string (JSON)."""
        ml_schema = MLSchema()
        df = DataFrame({"test": [1, 2, 3]})

        with patch.object(
            ml_schema.field_service, "build", return_value='{"json": "string"}'
        ):
            result = ml_schema.build(df)

            assert isinstance(result, str)

    def test_build_with_complex_dataframe(self):
        """Test building schema from a complex DataFrame with various dtypes."""
        ml_schema = MLSchema()
        df = DataFrame(
            {
                "integers": [1, 2, 3],
                "floats": [1.1, 2.2, 3.3],
                "strings": ["a", "b", "c"],
                "booleans": [True, False, True],
                "dates": pd.date_range("2023-01-01", periods=3),
            }
        )
        expected_json = '{"complex": "schema"}'

        with patch.object(
            ml_schema.field_service, "build", return_value=expected_json
        ) as mock_build:
            result = ml_schema.build(df)

            mock_build.assert_called_once_with(df)
            assert result == expected_json


class TestMLSchemaIntegration:
    """Integration tests for MLSchema with multiple operations."""

    def test_register_then_build_workflow(self):
        """Test the complete workflow of registering strategies and building schema."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)
        df = DataFrame({"test": [1, 2, 3]})

        with (
            patch.object(ml_schema.field_service, "register") as mock_register,
            patch.object(
                ml_schema.field_service, "build", return_value='{"test": "schema"}'
            ) as mock_build,
        ):
            # Register strategy
            ml_schema.register(mock_strategy)

            # Build schema
            result = ml_schema.build(df)

            # Verify both operations were called
            mock_register.assert_called_once_with(mock_strategy)
            mock_build.assert_called_once_with(df)
            assert result == '{"test": "schema"}'

    def test_register_update_unregister_workflow(self):
        """Test registering, updating, and unregistering strategies."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        with (
            patch.object(ml_schema.field_service, "register") as mock_register,
            patch.object(ml_schema.field_service, "update") as mock_update,
            patch.object(ml_schema.field_service, "unregister") as mock_unregister,
        ):
            # Register
            ml_schema.register(mock_strategy)

            # Update
            ml_schema.update(mock_strategy)

            # Unregister
            ml_schema.unregister(mock_strategy)

            # Verify all operations were called
            mock_register.assert_called_once_with(mock_strategy)
            mock_update.assert_called_once_with(mock_strategy)
            mock_unregister.assert_called_once_with(mock_strategy)

    def test_multiple_strategies_registration(self):
        """Test registering multiple strategies in different ways."""
        ml_schema = MLSchema()
        strategy1 = Mock(spec=FieldStrategy)
        strategy2 = Mock(spec=FieldStrategy)
        strategy3 = Mock(spec=FieldStrategy)

        with (
            patch.object(ml_schema.field_service, "register") as mock_register,
            patch.object(ml_schema.field_service, "register_all") as mock_register_all,
        ):
            # Register single strategies
            ml_schema.register(strategy1)
            ml_schema.register(strategy2)

            # Register list of strategies
            ml_schema.register([strategy3])

            # Verify calls
            assert mock_register.call_count == 2
            mock_register_all.assert_called_once_with([strategy3])


class TestMLSchemaErrorHandling:
    """Test suite for error handling and edge cases."""

    def test_register_with_invalid_type(self):
        """Test registering with invalid type (not FieldStrategy or list)."""
        ml_schema = MLSchema()

        # This should still delegate to field service, which will handle the error
        with patch.object(ml_schema.field_service, "register") as mock_register:
            ml_schema.register("invalid_strategy")  # type: ignore[arg-type]

            mock_register.assert_called_once_with("invalid_strategy")

    def test_build_with_none_dataframe(self):
        """Test building schema with None DataFrame."""
        ml_schema = MLSchema()

        with patch.object(ml_schema.field_service, "build") as mock_build:
            ml_schema.build(None)  # type: ignore[arg-type]

            mock_build.assert_called_once_with(None)

    def test_field_service_exceptions_propagate(self):
        """Test that exceptions from field service are properly propagated."""
        ml_schema = MLSchema()
        mock_strategy = Mock(spec=FieldStrategy)

        # Mock field service to raise an exception
        with patch.object(
            ml_schema.field_service, "register", side_effect=ValueError("Test error")
        ):
            with pytest.raises(ValueError, match="Test error"):
                ml_schema.register(mock_strategy)

    def test_build_exceptions_propagate(self):
        """Test that build exceptions are properly propagated."""
        ml_schema = MLSchema()
        df = DataFrame({"test": [1, 2, 3]})

        # Mock field service to raise an exception during build
        with patch.object(
            ml_schema.field_service, "build", side_effect=RuntimeError("Build error")
        ):
            with pytest.raises(RuntimeError, match="Build error"):
                ml_schema.build(df)


class TestMLSchemaDocumentationCompliance:
    """Test suite to verify behavior matches documentation."""

    def test_class_docstring_example_workflow(self):
        """Test the example workflow from the class docstring."""
        # This test verifies that the documented example would work
        ml_schema = MLSchema()

        # Mock DataFrame creation
        df = DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "salary": [50000.0, 60000.0, 70000.0],
            }
        )

        # Mock the build method to return example JSON
        expected_json = '{"fields": [{"name": "name", "type": "text"}, {"name": "age", "type": "number"}]}'

        with patch.object(ml_schema.field_service, "build", return_value=expected_json):
            result = ml_schema.build(df)

            assert isinstance(result, str)
            assert result == expected_json

    def test_register_method_documentation(self):
        """Test that register method behavior matches documentation."""
        ml_schema = MLSchema()

        # Documentation says it accepts FieldStrategy or list[FieldStrategy]
        single_strategy = Mock(spec=FieldStrategy)
        strategy_list: list[FieldStrategy] = [
            Mock(spec=FieldStrategy),
            Mock(spec=FieldStrategy),
        ]

        with (
            patch.object(ml_schema.field_service, "register") as mock_register,
            patch.object(ml_schema.field_service, "register_all") as mock_register_all,
        ):
            # Single strategy
            ml_schema.register(single_strategy)
            mock_register.assert_called_with(single_strategy)

            # List of strategies
            ml_schema.register(strategy_list)
            mock_register_all.assert_called_with(strategy_list)

    def test_update_method_documentation(self):
        """Test that update method behavior matches documentation."""
        ml_schema = MLSchema()
        strategy = Mock(spec=FieldStrategy)

        # Documentation says: "If the strategy doesn't exist, it's registered as new"
        with patch.object(ml_schema.field_service, "update") as mock_update:
            ml_schema.update(strategy)

            mock_update.assert_called_once_with(strategy)

    def test_build_method_documentation(self):
        """Test that build method behavior matches documentation."""
        ml_schema = MLSchema()
        df = DataFrame({"test": [1, 2, 3]})

        # Documentation says it returns "JSON serialized schema"
        with patch.object(
            ml_schema.field_service, "build", return_value='{"serialized": "json"}'
        ):
            result = ml_schema.build(df)

            assert isinstance(result, str)  # Should be JSON string
            # Should be valid JSON format (at least syntactically)
            assert result.startswith("{") or result.startswith("[")


class TestMLSchemaStateManagement:
    """Test suite for state management and instance isolation."""

    def test_independent_instances(self):
        """Test that MLSchema instances are independent."""
        ml_schema1 = MLSchema()
        ml_schema2 = MLSchema()

        strategy1 = Mock(spec=FieldStrategy)
        strategy2 = Mock(spec=FieldStrategy)

        # Mock field services independently
        with (
            patch.object(ml_schema1.field_service, "register") as mock_register1,
            patch.object(ml_schema2.field_service, "register") as mock_register2,
        ):
            ml_schema1.register(strategy1)
            ml_schema2.register(strategy2)

            # Each instance should only receive its own strategy
            mock_register1.assert_called_once_with(strategy1)
            mock_register2.assert_called_once_with(strategy2)

    def test_field_service_persistence(self):
        """Test that field service persists across method calls."""
        ml_schema = MLSchema()
        original_service = ml_schema.field_service

        strategy = Mock(spec=FieldStrategy)
        df = DataFrame({"test": [1, 2, 3]})

        # Perform multiple operations
        with (
            patch.object(ml_schema.field_service, "register"),
            patch.object(ml_schema.field_service, "build", return_value="{}"),
        ):
            ml_schema.register(strategy)
            ml_schema.build(df)

            # Field service should remain the same instance
            assert ml_schema.field_service is original_service

    def test_method_chaining_compatibility(self):
        """Test that methods could potentially support chaining (return self)."""
        ml_schema = MLSchema()
        strategy = Mock(spec=FieldStrategy)

        # Current implementation doesn't return self, but test that methods complete
        with (
            patch.object(ml_schema.field_service, "register"),
            patch.object(ml_schema.field_service, "update"),
            patch.object(ml_schema.field_service, "unregister"),
        ):
            # These should complete without error
            result1 = ml_schema.register(strategy)
            result2 = ml_schema.update(strategy)
            result3 = ml_schema.unregister(strategy)

            # Current implementation returns None
            assert result1 is None
            assert result2 is None
            assert result3 is None
