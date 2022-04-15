INSERT INTO self_tests_dot.entity_categories VALUES('anc', 'antenatal care');

INSERT INTO self_tests_dot.configured_entities VALUES('b05f1f9c-2176-46b0-8e8f-d6690f696b9b', 'ancview_danger_sign', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}

select *
from {{ schema }}.ancview_danger_sign');


