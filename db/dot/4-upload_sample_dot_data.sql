INSERT INTO dot.projects SELECT 'ScanProject1', 'Scan 1 project', true, 'public', null, '2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt';

-- entity categories
INSERT INTO dot.entity_categories VALUES('ALL', 'All flights');
INSERT INTO dot.entity_categories VALUES('ZAG', 'Zagreb airport flights');
INSERT INTO dot.entity_categories VALUES('ETH', 'Ethiopian Airlines');

-- configured entities - db views of the data we want to scan
INSERT INTO dot.configured_entities VALUES('ScanProject1', 'all_flight_data', 'ALL', 'select *
from public.flight_data ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

INSERT INTO dot.configured_entities VALUES('ScanProject1', 'zagreb_flight_data', 'ZAG', 'select *
from public.flight_data WHERE origin_airport=''Zagreb airport''    ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

INSERT INTO dot.configured_entities VALUES('ScanProject1', 'ethiopia_airlines_data', 'ETH', 'select *
from public.flight_data WHERE airline=''Ethiopian Airlines''    ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

INSERT INTO dot.configured_entities VALUES('ScanProject1', 'all_airports_data', 'ALL', 'select *
from public.airport_data   ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

INSERT INTO dot.configured_entities VALUES('ScanProject1', 'airlines_data', 'ALL', 'select DISTINCT(airline)
from public.flight_data   ','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');


-- Note these UUIDs get reset by the trigger
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '549c0575-e64c-3605-85a9-70356a23c4d2', 'MISSING-1', 3,
'Origin airport is not null', '', '', 'all_flight_data', 'not_null', 'origin_airport', '',
NULL, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '8aca2bee-9e95-3f8a-90e9-153714e05367', 'INCONSISTENT-1',
5, 'Price is not negative', '', '', 'all_flight_data', 'not_negative_string_column', 'price', '',
'{"name": "price"}', '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '52d7352e-56ee-3084-9c67-e5ab24afc3a3', 'DUPLICATE-1',
3, 'Airport not unique', '', '', 'all_airports_data', 'unique', 'airport', '', NULL,
'2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '935e6b61-b664-3eab-9d67-97c2c9c2bec0', 'INCONSISTENT-1',
3, 'Disallowed FP methods entered in form', '', '', 'all_flight_data', 'accepted_values', 'stops',
'', $${"values": [ "1", "2", "3", "Non-stop"]}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '0cdc9702-91e0-3499-b6f0-4dec12ad0f08', 'ASSESS-1', 3,
'Flight with no airport record', '', '', 'all_flight_data', 'relationships', 'origin_airport',
'', $${"name": "flight_with_no_airport", "to": "ref('dot_model__all_airports_data')", "field": "airport"}$$,
'2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '0cdc9702-91e0-3499-b6f0-4dec12ad0f18', 'BIAS-1', 6,
'Price outlier airlines', '', '', 'all_flight_data', 'expect_similar_means_across_reporters',
'price', '', $${"key": "airline","quantity": "price","data_table": "dot_model__all_flight_data","id_column": "airline",
"target_table":"dot_model__airlines_data"}$$, '2022-01-19 20:00:00.000 -0500', '2022-01-19 20:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '36d33837-bd92-370a-963a-264a4d5b2bac', 'DUPLICATE-1',
6, 'Duplicate flight record', '', '', 'all_flight_data', 'possible_duplicate_forms', '', '',
$${"table_specific_reported_date": "departure_time", "table_specific_patient_uuid": "airline", "table_specific_uuid":
"uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Matt');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', 'c4a3da8f-32f4-4e9b-b135-354de203ca90', 'TREAT-1',
5, 'Number of stops has a reasonable value', '', '', 'all_flight_data', 'custom_sql', '', '',
format('{%s: %s}',
    to_json('query'::text),
    to_json($query$
        select
            distinct uuid,
            'dot_model__all_flight_data' as primary_table,
            'uuid' as primary_table_id_field
          from {{ ref('dot_model__all_flight_data') }}
         where CAST(REGEXP_REPLACE(COALESCE(stops,'0'), '[^0-9]+', '0', 'g') as INTEGER) > 5
    $query$::text)
)::json,
'2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Lorenzo');

INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '3081f033-e8f4-4f3b-aea8-36f8c5df05dc', 'INCONSISTENT-1',
8, 'Price is a positive number for direct flights', '', '', 'all_flight_data', 'expression_is_true',
'', '', $${"name": "t_direct_flights_positive_price", "expression": "price is not null and price > 0",
"condition": "stops = 'non-stop'"}$$, '2022-12-10 19:00:00.000 -0500', '2022-12-10 19:00:00.000 -0500', 'Lorenzo');

COMMIT;


