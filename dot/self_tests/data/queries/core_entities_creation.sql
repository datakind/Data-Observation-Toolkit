INSERT INTO self_tests_dot.projects SELECT 'Muso', 'Muso project', true, 'public', null, '2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt';

INSERT INTO self_tests_dot.entity_categories VALUES('anc', 'antenatal care');

INSERT INTO self_tests_dot.configured_entities VALUES('Muso','b05f1f9c-2176-46b0-8e8f-d6690f696b9b', 'ancview_danger_sign', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}

select *
from {{ schema }}.ancview_danger_sign','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');


