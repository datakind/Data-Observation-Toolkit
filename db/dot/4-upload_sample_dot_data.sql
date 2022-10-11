INSERT INTO dot.projects SELECT 'ScanProject1', 'Scan 1 project', true, 'public', null, '2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt';

-- entity categories
INSERT INTO dot.entity_categories VALUES('ALL', 'All flights');
INSERT INTO dot.entity_categories VALUES('ZAG', 'Zagreb airport flights');
INSERT INTO dot.entity_categories VALUES('ETH', 'Ethiopian Airlines');

-- configured entities - db views of the data we want to scan
INSERT INTO dot.configured_entities VALUES('ScanProject1','b05f1f9c-2176-46b0-8e8f-d6690f696b9c', 'all_flight_data', 'ALL', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.flight_data ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

INSERT INTO dot.configured_entities VALUES('ScanProject1','b05f1f9c-2176-46b0-8e8f-d6690f696b9b', 'zagreb_flight_data', 'ZAG', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.flight_data WHERE origin_airport=''Zagreb airport''    ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

INSERT INTO dot.configured_entities VALUES('ScanProject1','b05f1f9c-2176-46b0-8e8f-d6690f696b9b', 'ethiopia_airlines_data', 'ETH', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.flight_data WHERE airline=''Ethiopian Airlines''    ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

INSERT INTO dot.configured_entities VALUES('ScanProject1','b05f1f9c-2176-46b0-8e8f-d6690f696b9b', 'all_airports_data', 'ALL', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.airport_data   ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

INSERT INTO dot.configured_entities VALUES('ScanProject1','b05f1f9c-2176-46b0-8e8f-d6690f696b9c', 'airlines_data', 'ALL', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select DISTINCT airline
from {{ schema }}.flight_data   ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');


-- Note these UUIDs get reset by the trigger
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '549c0575-e64c-3605-85a9-70356a23c4d2', 'MISSING-1', 3,
'Origin airport is not null', '', '', 'ca4513fa-96e0-3a95-a1a8-7f0c127ea82a', 'not_null', 'origin_airport', '',
NULL, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '8aca2bee-9e95-3f8a-90e9-153714e05367', 'INCONSISTENT-1',
5, 'Price is not negative', '', '', 'ca4513fa-96e0-3a95-a1a8-7f0c127ea82a', 'not_negative_string_column', 'price', '',
'{"name": "price"}', '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '52d7352e-56ee-3084-9c67-e5ab24afc3a3', 'DUPLICATE-1',
3, 'Airport not unique', '', '', '7b689796-afde-3930-87be-ed8b7c7a0474', 'unique', 'airport', '', NULL,
'2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '935e6b61-b664-3eab-9d67-97c2c9c2bec0', 'INCONSISTENT-1',
3, 'Disallowed FP methods entered in form', '', '', 'ca4513fa-96e0-3a95-a1a8-7f0c127ea82a', 'accepted_values', 'stops',
'', $${"values": [ "1", "2", "3", "Non-stop"]}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '0cdc9702-91e0-3499-b6f0-4dec12ad0f08', 'ASSESS-1', 3,
'Flight with no airport record', '', '', 'ca4513fa-96e0-3a95-a1a8-7f0c127ea82a', 'relationships', 'origin_airport',
'', $${"name": "flight_with_no_airport", "to": "ref('dot_model__all_airports_data')", "field": "airport"}$$,
'2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '0cdc9702-91e0-3499-b6f0-4dec12ad0f18', 'BIAS-1', 6,
'Price outlier airlines', '', '', 'ca4513fa-96e0-3a95-a1a8-7f0c127ea82a', 'expect_similar_means_across_reporters',
'price', '', $${"key": "airline","quantity": "price","data_table": "dot_model__all_flight_data","id_column": "airline",
"target_table":"dot_model__airlines_data"}$$, '2022-01-19 20:00:00.000 -0500', '2022-01-19 20:00:00.000 -0500', 'Matt');

-- TODO Make duplicate forms generic
-- INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '36d33837-bd92-370a-963a-264a4d5b2bac', 'DUPLICATE-1',
-- 6, 'Duplicate flight record', '', '', 'ca4513fa-96e0-3a95-a1a8-7f0c127ea82a', 'possible_duplicate_forms', '', '',
-- $${"table_specific_reported_date": "departure_time", "table_specific_patient_uuid": "airline", "table_specific_uuid":
-- "uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Matt');

COMMIT;


