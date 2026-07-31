"""Tests for bare entity_id normalization in test_parameters."""

from utils.configuration_utils import (
    prepare_test_parameters,
    to_bare_entity_id,
    to_dbt_ref,
    to_dbt_table,
)


class TestToBareEntityId:
    """to_bare_entity_id accepts bare, prefixed, and ref() forms."""

    def test_bare_id(self):
        assert to_bare_entity_id("all_airports_data") == "all_airports_data"

    def test_prefixed_table(self):
        assert to_bare_entity_id("dot_model__all_airports_data") == "all_airports_data"

    def test_dbt_ref_single_quotes(self):
        assert (
            to_bare_entity_id("ref('dot_model__all_airports_data')")
            == "all_airports_data"
        )

    def test_dbt_ref_double_quotes(self):
        assert (
            to_bare_entity_id('ref("dot_model__all_airports_data")')
            == "all_airports_data"
        )

    def test_empty_and_none(self):
        assert to_bare_entity_id(None) is None
        assert to_bare_entity_id("") is None
        assert to_bare_entity_id("   ") is None


class TestToDbtFormats:
    """Wrap bare/legacy values into DBT artifact forms."""

    def test_to_dbt_ref_from_bare(self):
        assert (
            to_dbt_ref("all_airports_data")
            == "ref('dot_model__all_airports_data')"
        )

    def test_to_dbt_ref_from_legacy_ref(self):
        assert (
            to_dbt_ref("ref('dot_model__all_airports_data')")
            == "ref('dot_model__all_airports_data')"
        )

    def test_to_dbt_table_from_bare(self):
        assert to_dbt_table("all_flight_data") == "dot_model__all_flight_data"

    def test_to_dbt_table_from_prefixed(self):
        assert (
            to_dbt_table("dot_model__all_flight_data") == "dot_model__all_flight_data"
        )


class TestPrepareTestParameters:
    """prepare_test_parameters adapts keys and entity formats per test type."""

    def test_relationships_bare_to(self):
        result = prepare_test_parameters(
            "relationships",
            {"to": "all_airports_data", "field": "airport", "name": "x"},
        )
        assert result["to"] == "ref('dot_model__all_airports_data')"
        assert result["field"] == "airport"

    def test_relationships_legacy_ref_to(self):
        result = prepare_test_parameters(
            "relationships",
            {
                "to": "ref('dot_model__all_airports_data')",
                "field": "airport",
            },
        )
        assert result["to"] == "ref('dot_model__all_airports_data')"

    def test_relationships_reference_alias(self):
        result = prepare_test_parameters(
            "relationships",
            {"reference": "ancview_pregnancy", "field": "uuid"},
        )
        assert "reference" not in result
        assert result["to"] == "ref('dot_model__ancview_pregnancy')"

    def test_expect_similar_means_bare_data_table(self):
        result = prepare_test_parameters(
            "expect_similar_means_across_reporters",
            {
                "key": "airline",
                "data_table": "all_flight_data",
                "target_table": "airlines_data",
            },
        )
        assert result["data_table"] == "dot_model__all_flight_data"
        assert result["target_table"] == "dot_model__airlines_data"

    def test_expect_similar_means_form_name_alias(self):
        result = prepare_test_parameters(
            "expect_similar_means_across_reporters",
            {"form_name": "iccmview_assessment", "key": "reported_by"},
        )
        assert "form_name" not in result
        assert result["data_table"] == "dot_model__iccmview_assessment"

    def test_other_test_type_unchanged(self):
        params = {"values": ["a", "b"]}
        assert prepare_test_parameters("accepted_values", params) == params

    def test_non_dict_passthrough(self):
        assert prepare_test_parameters("relationships", None) is None
        assert prepare_test_parameters("relationships", "") == ""
