INSERT INTO dot.projects (project_id,description,active,project_schema,contacts,date_added,date_modified,last_updated_by) VALUES
	 ('IccmRaw','Orinigal data provided by Medic',true,'public',NULL,'2021-12-06 19:00:00-05','2021-12-06 19:00:00-05','Jan Peter'),
	 ('GretelCtgan40','Synthetic data created with ctgan40',true,'public',NULL,'2021-12-06 19:00:00-05','2021-12-06 19:00:00-05','Jan Peter'),
	 ('Gretel_Lstm20','Synthetic data created with lstm20',true,'public',NULL,'2021-12-06 19:00:00-05','2021-12-06 19:00:00-05','Jan Peter'),
	 ('sdv_gaussian','Synthetic data created with sdv_gaussian',true,'public',NULL,'2021-12-06 19:00:00-05','2021-12-06 19:00:00-05','Jan Peter'),
	 ('sdv_copulagan','Synthetic data created with sdv copulagan',true,'public',NULL,'2021-12-06 19:00:00-05','2021-12-06 19:00:00-05','Jan Peter'),
	 ('sdv_ctgan','Synthetic data created with ctgan',true,'public',NULL,'2022-12-29 09:46:06.434809-05','2022-12-29 09:46:06.434809-05','Jan Peter'),
	 ('sdv_tvae','Synthetic data created with sdv_tvae',true,'public',NULL,'2021-12-06 19:00:00-05','2021-12-06 19:00:00-05','Jan Peter'),
	 ('ydata_gan_split','Synthetic data created with ydata_gan_split',true,'public',NULL,'2021-12-06 19:00:00-05','2021-12-06 19:00:00-05','Jan Peter');

INSERT INTO dot.entity_categories (entity_category,description) VALUES
	 ('iccm_raw_category','All iccm data provided by medic'),
	 ('GretelCtgan40_category','All iccm data created with ctgan40'),
	 ('Gretel_Lstm20_category','All iccm data created with lstm20'),
	 ('sdv_gaussian_category','All iccm data created with sdv_gaussian'),
	 ('sdv_copulagan_category','All iccm data created with sdv copulaga'),
	 ('sdv_ctgan_category','All iccm data created with sdv_ctgan'),
	 ('sdv_tvae_category','All iccm data created with sdv_tvae');
INSERT INTO dot.entity_categories (entity_category,description) VALUES
	 ('ydata_gan_split_category','All iccm data created with ydata_gan_split');

INSERT INTO dot.configured_entities (project_id,entity_id,entity_name,entity_category,entity_definition,date_added,date_modified,last_updated_by) VALUES
	 ('IccmRaw','61b6c6b1-b61d-3aba-99c4-89d41be279fd','reporters_data','iccm_raw_category','{{ config(materialized=''view'') }} {% set schema = <schema> %} select DISTINCT reported_by from {{ schema }}.iccm_assessment_raw
','2022-12-23 10:42:29.297286-05','2022-12-23 10:43:34.04292-05','false'),
	 ('IccmRaw','9f80ae8a-0155-32ae-85b2-ecd2aa72c048','all_appointments_raw_data','iccm_raw_category','{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.iccm_assessment_raw  ','2022-12-23 03:20:50.938753-05','2022-12-27 11:28:15.377211-05','false'),
	 ('GretelCtgan40','d6e35183-c158-3897-a015-f72497de2923','all_appointments_gretel_ctgan40_data','GretelCtgan40_category','{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.gretel_ctgan40_sample  ','2022-12-27 15:12:46.29229-05','2022-12-27 15:44:58.864621-05','false'),
	 ('GretelCtgan40','a39cc3ba-84ee-3add-99af-5c3bd4d9d5ea','reporters_gretel_ctgan40_data','GretelCtgan40_category','{{ config(materialized=''view'') }} {% set schema = <schema> %} select DISTINCT reported_by from {{ schema }}.gretel_ctgan40_sample
','2022-12-27 15:12:46.29229-05','2022-12-27 15:47:05.415279-05','false'),
	 ('Gretel_Lstm20','e0ca54a1-e1cf-3b16-96f3-c4c07f93992c','reporters_gretel_lstm20_data','Gretel_Lstm20_category','{{ config(materialized=''view'') }} {% set schema = <schema> %} select DISTINCT reported_by from {{ schema }}.gretel_lstm20_sample
','2022-12-28 06:25:32.240357-05','2022-12-28 06:25:32.240357-05','false');
INSERT INTO dot.configured_entities (project_id,entity_id,entity_name,entity_category,entity_definition,date_added,date_modified,last_updated_by) VALUES
	 ('Gretel_Lstm20','5dace138-7f1c-3f42-8962-6a8030df71fc','all_appointments_gretel_lstm20_data','Gretel_Lstm20_category','{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.gretel_lstm20_sample  ','2022-12-28 06:25:32.240357-05','2022-12-28 06:34:11.479454-05','false'),
	 ('sdv_gaussian','47e60711-2ccb-3154-b8ea-a6faa745a9ad','reporters_sdv_gaussian_data','sdv_gaussian_category','{{ config(materialized=''view'') }} {% set schema = <schema> %} select DISTINCT reported_by from {{ schema }}.sdv_gaussian_sample
','2022-12-28 07:33:02.581454-05','2022-12-28 07:33:02.581454-05','false'),
	 ('sdv_gaussian','ab57a994-32fc-3df7-8a7b-96e416995ed2','all_appointments_sdv_gaussian_data','sdv_gaussian_category','{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.sdv_gaussian_sample  ','2022-12-28 07:33:02.581454-05','2022-12-28 07:33:02.581454-05','false'),
	 ('sdv_copulagan','4b957b48-c7f7-37e7-9d06-2dfcdb912469','reporters_sdv_copulagan_data','sdv_copulagan_category','{{ config(materialized=''view'') }} {% set schema = <schema> %} select DISTINCT reported_by from {{ schema }}.sdv_copulagan_sample','2022-12-28 07:53:06.778554-05','2022-12-29 09:43:11.133735-05','false'),
	 ('sdv_copulagan','a012e38a-4372-3460-ba75-d1765af28d04','all_appointments_sdv_copulagan_data','sdv_copulagan_category','{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.sdv_copulagan_sample','2022-12-28 07:54:48.65321-05','2022-12-29 09:43:25.062233-05','false'),
	 ('sdv_ctgan','a4e0c835-dc90-3228-9ce4-ff8da1d0f8f3','reporters_sdv_ctgan_data','sdv_ctgan_category','{{ config(materialized=''view'') }} {% set schema = <schema> %} select DISTINCT reported_by from {{ schema }}.sdv_ctgan_sample
','2022-12-29 09:51:19.685365-05','2022-12-29 09:51:19.685365-05','false'),
	 ('sdv_ctgan','16039628-341c-3e52-9be3-97afd7c19cdd','all_appointments_sdv_ctgan_data','sdv_ctgan_category','{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.sdv_ctgan_sample  ','2022-12-29 09:51:19.685365-05','2022-12-29 09:51:19.685365-05','false'),
	 ('sdv_tvae','7a250bae-2224-3575-991b-ddb4fca1fdbf','reporters_sdv_tvae_data','sdv_tvae_category','{{ config(materialized=''view'') }} {% set schema = <schema> %} select DISTINCT reported_by from {{ schema }}.sdv_tvae_sample
','2022-12-29 09:57:45.355049-05','2022-12-29 09:57:45.355049-05','false'),
	 ('sdv_tvae','76a8618f-6675-32ab-97da-11ce11d8f027','all_appointments_sdv_tvae_data','sdv_tvae_category','{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.sdv_tvae_sample  ','2022-12-29 09:57:45.355049-05','2022-12-29 09:57:45.355049-05','false'),
	 ('ydata_gan_split','df8e0294-612b-3772-9209-227862768f30','reporters_ydata_gan_split_data','ydata_gan_split_category','{{ config(materialized=''view'') }} {% set schema = <schema> %} select DISTINCT reported_by from {{ schema }}.ydata_gan_split_sample
','2022-12-29 10:02:34.217053-05','2022-12-29 10:02:34.217053-05','false');
INSERT INTO dot.configured_entities (project_id,entity_id,entity_name,entity_category,entity_definition,date_added,date_modified,last_updated_by) VALUES
	 ('ydata_gan_split','fb41cd3f-d290-3f84-b95b-8d1233dfc95d','all_appointments_ydata_gan_split_data','ydata_gan_split_category','{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.ydata_gan_split_sample  ','2022-12-29 10:02:34.217053-05','2022-12-29 10:02:34.217053-05','false');

INSERT INTO dot.configured_tests (test_activated,project_id,test_id,scenario_id,priority,description,impact,proposed_remediation,entity_id,test_type,column_name,column_description,test_parameters,date_added,date_modified,last_updated_by) VALUES
	 (true,'IccmRaw','c38a0948-b07c-39ce-83b4-33191bd3d268','DUPLICATE-1',4,'Test for duplicates in appointments of iccm raw','','','9f80ae8a-0155-32ae-85b2-ecd2aa72c048','possible_duplicate_forms','',NULL,'{"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "reported"}','2022-12-23 05:11:46.828562-05','2022-12-27 11:28:15.377211-05','false');
INSERT INTO dot.configured_tests (test_activated,project_id,test_id,scenario_id,priority,description,impact,proposed_remediation,entity_id,test_type,column_name,column_description,test_parameters,date_added,date_modified,last_updated_by) VALUES
	 (true,'IccmRaw','cc5d8407-8e89-34f0-800f-aa36e497ca98','BIAS-1',4,'Thermometer miscalibrated','','','9f80ae8a-0155-32ae-85b2-ecd2aa72c048','expect_similar_means_across_reporters','child_temperature',NULL,'{"key": "reported_by", "quantity": "child_temperature", "id_column": "reported_by", "data_table": "dot_model__all_appointments_raw_data", "target_table": "dot_model__reporters_data"}','2022-12-23 10:21:07.924794-05','2022-12-27 11:28:15.377211-05','false'),
	 (true,'IccmRaw','6dec93b6-627a-3ec8-952f-5009fd1569b3','INCONSISTENT-1',8,'Wrong treatment/dosage arising from wrong age of children','','','9f80ae8a-0155-32ae-85b2-ecd2aa72c048','expression_is_true','','','{"name": "t_under_24_months_wrong_dosage", "condition": "(within_24 is true) and (malaria_act_dosage is true)", "expression": "malaria_act_dosage is null"}','2022-12-23 11:02:48.433503-05','2022-12-27 11:43:26.860198-05','Jan Peter '),
	 (true,'GretelCtgan40','d69ffc0e-84eb-3a03-b3c6-92596879e4f0','DUPLICATE-1',4,'Test for duplicates in appointments of iccm gretel ctgan 40','','','d6e35183-c158-3897-a015-f72497de2923','possible_duplicate_forms','',NULL,'{"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "reported"}','2022-12-27 15:27:45.137947-05','2022-12-27 15:44:58.864621-05','false'),
	 (true,'GretelCtgan40','71991d72-0ae8-36df-808b-4f045c9983cb','BIAS-1',4,'Thermometer miscalibrated','','','d6e35183-c158-3897-a015-f72497de2923','expect_similar_means_across_reporters','child_temperature',NULL,'{"key": "reported_by", "quantity": "child_temperature", "id_column": "reported_by", "data_table": "dot_model__all_appointments_gretel_ctgan40_data", "target_table": "dot_model__reporters_gretel_ctgan40_data"}','2022-12-27 15:29:41.744241-05','2022-12-27 15:44:58.864621-05','false'),
	 (true,'GretelCtgan40','32c987e0-c839-37d9-9c36-3b2491881081','INCONSISTENT-1',8,'Wrong treatment/dosage arising from wrong age of children','','','d6e35183-c158-3897-a015-f72497de2923','expression_is_true','','','{"name": "t_under_24_months_wrong_dosage", "condition": "(within_24 is true) and (malaria_act_dosage is true)", "expression": "malaria_act_dosage is null"}','2022-12-27 15:29:41.744241-05','2022-12-27 15:44:58.864621-05','Jan Peter'),
	 (true,'Gretel_Lstm20','a83342d4-5e50-3874-85f9-819547841930','DUPLICATE-1',4,'Test for duplicates in appointments of iccm gretel lstm 20','','','5dace138-7f1c-3f42-8962-6a8030df71fc','possible_duplicate_forms','',NULL,'{"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "reported"}','2022-12-28 06:29:13.904455-05','2022-12-28 06:34:11.479454-05','false'),
	 (true,'Gretel_Lstm20','fa80d336-94b5-3bda-86e3-744abe200a6a','BIAS-1',4,'Thermometer miscalibrated','','','5dace138-7f1c-3f42-8962-6a8030df71fc','expect_similar_means_across_reporters','child_temperature',NULL,'{"key": "reported_by", "quantity": "child_temperature", "id_column": "reported_by", "data_table": "dot_model__all_appointments_gretel_lstm20_data", "target_table": "dot_model__reporters_gretel_lstm20_data"}','2022-12-28 06:29:22.165741-05','2022-12-28 06:34:11.479454-05','false'),
	 (true,'Gretel_Lstm20','431990f2-a60a-320f-ab13-2d25725b9864','INCONSISTENT-1',8,'Wrong treatment/dosage arising from wrong age of children','','','5dace138-7f1c-3f42-8962-6a8030df71fc','expression_is_true','','','{"name": "t_under_24_months_wrong_dosage", "condition": "(within_24 is true) and (malaria_act_dosage is true)", "expression": "malaria_act_dosage is null"}','2022-12-28 06:29:22.165741-05','2022-12-28 06:34:11.479454-05','Jan Peter'),
	 (true,'sdv_gaussian','6a61c5bb-304a-3d1f-9afd-17bced0c68f6','DUPLICATE-1',4,'Test for duplicates in appointments of iccm sdv_gaussiann','','','ab57a994-32fc-3df7-8a7b-96e416995ed2','possible_duplicate_forms','',NULL,'{"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "reported"}','2022-12-28 07:36:57.416694-05','2022-12-28 07:36:57.416694-05','false'),
	 (true,'sdv_gaussian','202a3ccf-e223-3f7f-a609-b8494e6b585f','BIAS-1',4,'Thermometer miscalibrated','','','ab57a994-32fc-3df7-8a7b-96e416995ed2','expect_similar_means_across_reporters','child_temperature',NULL,'{"key": "reported_by", "quantity": "child_temperature", "id_column": "reported_by", "data_table": "dot_model__all_appointments_sdv_gaussian_data", "target_table": "dot_model__reporters_sdv_gaussian_data"}','2022-12-28 07:36:57.416694-05','2022-12-28 07:36:57.416694-05','false'),
     (true,'sdv_gaussian','fb681b36-5a17-30ca-aba6-bd1d5411c753','INCONSISTENT-1',8,'Wrong treatment/dosage arising from wrong age of children','','','ab57a994-32fc-3df7-8a7b-96e416995ed2','expression_is_true','','','{"name": "t_under_24_months_wrong_dosage", "condition": "(within_24 is true) and (malaria_act_dosage is true)", "expression": "malaria_act_dosage is null"}','2022-12-28 07:36:57.416694-05','2022-12-28 07:36:57.416694-05','Jan Peter');
INSERT INTO dot.configured_tests (test_activated,project_id,test_id,scenario_id,priority,description,impact,proposed_remediation,entity_id,test_type,column_name,column_description,test_parameters,date_added,date_modified,last_updated_by) VALUES
	 (true,'sdv_copulagan','fcb926ad-b433-3d21-8cb4-d52c5e256729','DUPLICATE-1',4,'Test for duplicates in appointments of iccm sdv copulagan','','','a012e38a-4372-3460-ba75-d1765af28d04','possible_duplicate_forms','',NULL,'{"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "reported"}','2022-12-28 07:56:23.887111-05','2022-12-29 09:43:25.062233-05','false'),
	 (true,'sdv_copulagan','36248b21-39b2-3851-b1e2-c79072b98a5b','BIAS-1',4,'Thermometer miscalibrated','','','a012e38a-4372-3460-ba75-d1765af28d04','expect_similar_means_across_reporters','child_temperature',NULL,'{"key": "reported_by", "quantity": "child_temperature", "id_column": "reported_by", "data_table": "dot_model__all_appointments_sdv_copulagan_data", "target_table": "dot_model__reporters_sdv_copulagan_data"}','2022-12-28 07:56:23.887111-05','2022-12-29 09:43:25.062233-05','false'),
	 (true,'sdv_copulagan','e6366003-3606-3c75-902d-6e4011b638ac','INCONSISTENT-1',8,'Wrong treatment/dosage arising from wrong age of children','','','a012e38a-4372-3460-ba75-d1765af28d04','expression_is_true','','','{"name": "t_under_24_months_wrong_dosage", "condition": "(within_24 is true) and (malaria_act_dosage is true)", "expression": "malaria_act_dosage is null"}','2022-12-28 07:56:23.887111-05','2022-12-29 09:43:25.062233-05','Jan Peter'),
	 (true,'sdv_ctgan','fa6b0a17-72dc-31cf-9a32-2cf930695d74','BIAS-1',4,'Thermometer miscalibrated','','','16039628-341c-3e52-9be3-97afd7c19cdd','expect_similar_means_across_reporters','child_temperature',NULL,'{"key": "reported_by", "quantity": "child_temperature", "id_column": "reported_by", "data_table": "dot_model__all_appointments_sdv_ctgan_data", "target_table": "dot_model__reporters_sdv_ctgan_data"}','2022-12-29 09:52:24.446091-05','2022-12-29 09:52:24.446091-05','false'),
	 (true,'sdv_ctgan','460d033b-3706-3d1b-ad79-b8bd39678919','INCONSISTENT-1',8,'Wrong treatment/dosage arising from wrong age of children','','','16039628-341c-3e52-9be3-97afd7c19cdd','expression_is_true','','','{"name": "t_under_24_months_wrong_dosage", "condition": "(within_24 is true) and (malaria_act_dosage is true)", "expression": "malaria_act_dosage is null"}','2022-12-29 09:52:24.446091-05','2022-12-29 09:52:24.446091-05','Jan Peter'),
	 (true,'sdv_ctgan','bfa49073-cf0b-32b6-97b0-3977eb7f421e','DUPLICATE-1',4,'Test for duplicates in appointments of iccm ctgan','','','16039628-341c-3e52-9be3-97afd7c19cdd','possible_duplicate_forms','',NULL,'{"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "reported"}','2022-12-28 07:56:23.887111-05','2022-12-29 09:43:25.062233-05','false'),
	 (true,'sdv_tvae','d88e5cf6-db7b-3eae-9e97-e97fad014f9d','BIAS-1',4,'Thermometer miscalibrated','','','76a8618f-6675-32ab-97da-11ce11d8f027','expect_similar_means_across_reporters','child_temperature',NULL,'{"key": "reported_by", "quantity": "child_temperature", "id_column": "reported_by", "data_table": "dot_model__all_appointments_sdv_tvae_data", "target_table": "dot_model__reporters_sdv_tvae_data"}','2022-12-29 09:58:19.311602-05','2022-12-29 09:58:19.311602-05','false'),
	 (true,'sdv_tvae','d615472d-c22f-3f04-985d-5c17ab9d22dd','INCONSISTENT-1',8,'Wrong treatment/dosage arising from wrong age of children','','','76a8618f-6675-32ab-97da-11ce11d8f027','expression_is_true','','','{"name": "t_under_24_months_wrong_dosage", "condition": "(within_24 is true) and (malaria_act_dosage is true)", "expression": "malaria_act_dosage is null"}','2022-12-29 09:58:19.311602-05','2022-12-29 09:58:19.311602-05','Jan Peter'),
	 (true,'sdv_tvae','974e035e-e47e-3806-9723-eeb3f866fdf9','DUPLICATE-1',4,'Test for duplicates in appointments of iccm sdv_tvae','','','76a8618f-6675-32ab-97da-11ce11d8f027','possible_duplicate_forms','',NULL,'{"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "reported"}','2022-12-28 07:56:23.887111-05','2022-12-29 09:43:25.062233-05','false'),
	 (true,'ydata_gan_split','7758755e-a906-36d2-b76b-a357bfdff1bf','BIAS-1',4,'Thermometer miscalibrated','','','fb41cd3f-d290-3f84-b95b-8d1233dfc95d','expect_similar_means_across_reporters','child_temperature',NULL,'{"key": "reported_by", "quantity": "child_temperature", "id_column": "reported_by", "data_table": "dot_model__all_appointments_ydata_gan_split_data", "target_table": "dot_model__reporters_ydata_gan_split_data"}','2022-12-29 10:03:10.529718-05','2022-12-29 10:03:10.529718-05','false'),
	 (true,'ydata_gan_split','487ba03d-f022-3253-8aea-448fb99e8d18','INCONSISTENT-1',8,'Wrong treatment/dosage arising from wrong age of children','','','fb41cd3f-d290-3f84-b95b-8d1233dfc95d','expression_is_true','','','{"name": "t_under_24_months_wrong_dosage", "condition": "(within_24 is true) and (malaria_act_dosage is true)", "expression": "malaria_act_dosage is null"}','2022-12-29 10:03:10.529718-05','2022-12-29 10:03:10.529718-05','Jan Peter'),
	 (true,'ydata_gan_split','fcb926ad-b433-3d21-8cb4-d52c5e256730','DUPLICATE-1',4,'Test for duplicates in appointments of iccm ydata_gan_split','','','fb41cd3f-d290-3f84-b95b-8d1233dfc95d','possible_duplicate_forms','',NULL,'{"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "reported"}','2022-12-28 07:56:23.887111-05','2022-12-29 09:43:25.062233-05','false');
