# DOT Configuration Guide (Adding Entities & Tests)

This guide explains how to add new entities (views/tables to monitor) and define tests. DOT caters to two distinct workflows depending on your technical expertise.

**Please pick the method that applies to you:**
- **Method A (The UI):** Using the Appsmith interface (Recommended for Data Analysts).
- **Method B (Raw SQL):** Writing and executing PostgreSQL INSERT statements directly (For Data Engineers/Advanced Users).

---

## UI Walkthrough Video (Method A)

Watch this recording to see a category, an entity, and a test created in the Appsmith UI. The written steps in the sections below are the procedure to follow.

**[Create entities and tests in the DOT UI](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6)**

The recording starts with the DOT UI already open and the containers already running. To reach that point, complete these steps first:

1. [The Not-So-Quick Start: Manual Docker Build](./deployment.md#the-not-so-quick-start-manual-docker-build)
2. [Setting up the DOT User Interface (Appsmith)](./deployment.md#setting-up-the-dot-user-interface-appsmith)

Chapters:

- [00:00 Video overview and goals](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6?t=0)
- [03:44 Find issues in demo data](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6?t=224)
- [06:55 Build a new entity](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6?t=415)
- [12:11 Run checks and generate results](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6?t=731). This chapter uses the manual pipeline. See [Manual Pipeline Execution](./execution.md#manual-pipeline-execution).
- [16:38 Create a new test](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6?t=998)
- [25:13 Debug failing test errors](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6?t=1513)
- [29:25 Fix naming and rerun](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6?t=1765)
- [32:51 Verify results and conclude](https://www.loom.com/share/d8a9b492a0a54546849b495c521783b6?t=1971)

---

## 1. Adding a New Entity

An entity represents a table or view in your database that you want to monitor. Once DOT knows about the entity, you can assign data quality rules (tests) to it.

### Method A: Using the Appsmith UI (Data Analysts)

Configuration lives in the top bar. Open **Configuration** to reach **Tests**, **Entities**, **Categories**, and **Projects**.

1. Open **Configuration** and choose **Entities**.
2. Click **Add entity**.
3. If the category does not exist yet, add it first from **Configuration** > **Categories**.
4. Complete the entity form and submit it.

### Method B: Using Raw SQL (Data Engineers)
You can define entities directly via SQL by inserting them into `dot.configured_entities`. This table requires the `entity_id`, `entity_category` (must exist in `dot.entity_categories`), and a Jinja-templated `entity_definition`.

```sql
INSERT INTO dot.configured_entities (
    project_id, 
    entity_id, 
    entity_category, 
    entity_definition, 
    date_added, 
    date_modified, 
    last_updated_by
) VALUES (
    'Project1', 
    'ancview_danger_sign', 
    'anc', 
    '{{ config(materialized=''view'') }}
{% set schema = <schema> %}

select *
from {{ schema }}.ancview_danger_sign',
    NOW(),
    NOW(),
    'admin'
);
```

The SQL for the entity definition can be more complex, combining data from multiple tables:

```sql
{{ config(materialized=''view'') }}
{% set schema = <schema> %}

select ap.*,
        ap.lmp as lmp_date,
        DATE_PART(''day'', reported - lmp) as days_since_lmp
from {{ schema }}.ancview_pregnancy ap
```

*(If you need a new category, first insert it into `dot.entity_categories`)*:

```sql
INSERT INTO dot.entity_categories VALUES('anc', 'antenatal care');
```

---

## 2. Configuring a Data Quality Test

Now that DOT recognizes the entity, let's assign a data quality rule.

### Method A: Using the Appsmith UI (Data Analysts)
1. Open **Configuration** in the top bar and choose **Tests**.
2. Click **Add test**.
3. Leave **On/Off** switched on to activate the test.
4. Select a **Project Id** (for example, `ScanProject1`).
5. Enter a **Description** (for example, `Origin airport is not null`).
6. Select a **Test Type** (for example, `not_null` or `unique`).
7. Select an **Entity Name** (for example, `all_flight_data`).
8. Select a **Scenario Id** (for example, `MISSING-1`).
9. Set **Priority**.
10. Scroll to complete the remaining fields, including **Impact** and any fields for the selected test type, then submit the form. 

### Method B: Using Raw SQL (Data Engineers)

Tests are defined in the `dot.configured_tests` table. Any insert or update will automatically call the database function `dot.test_validation` to ensure JSON test parameters are in the expected format.

> **Note:** In all of the following examples, the UUID in the insert statement will be replaced with an automatically generated one.

**1. `relationship`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', '0cdc9702-91e0-3499-b6f0-4dec12ad0f08', 'ASSESS-1', 3, '', '', '',
    'ancview_pregnancy', 'relationships', 'uuid', '',
    $${"name": "danger_signs_with_no_pregnancy", "to": "ancview_danger_sign", "field": "pregnancy_uuid"}$$,
    '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```

**2. `unique`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', '52d7352e-56ee-3084-9c67-e5ab24afc3a3', 'DUPLICATE-1', 3, '',
    '', '', 'ancview_pregnancy', 'unique', 'uuid', 'alternative index?', '',
    '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```

**3. `not_negative_string_column`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', '8aca2bee-9e95-3f8a-90e9-153714e05367', 'INCONSISTENT-1', 3,
    '', '', '', 'ancview_pregnancy', 'not_negative_string_column', 'patient_age_in_years', '',
    $${"name": "patient_age_in_years"}$$,
    '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```

**4. `not_null`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', '549c0575-e64c-3605-85a9-70356a23c4d2', 'MISSING-1', 3, '',
    '', '', 'ancview_pregnancy', 'not_null', 'patient_id', '', '',
    '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```

**5. `accepted_values`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', '935e6b61-b664-3eab-9d67-97c2c9c2bec0', 'INCONSISTENT-1', 3,
    '', '', '', 'ancview_pregnancy', 'accepted_values', 'fp_method_being_used', '',
    $${"values": ["oral mini-pill (progestogen)", "male condom", "female sterilization", "iud", "oral combination pill", "implants", "injectible"]}$$,
    '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```

**6. `possible_duplicate_forms`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', '7f78de0e-8268-3da6-8845-9a445457cc9a', 'DUPLICATE-1', 3, '',
    '', '', 'ancview_pregnancy', 'possible_duplicate_forms', '', '',
    $${"date_column": "delivery_date", "group_column": "patient_id", "id_column": "uuid"}$$,
    '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```

**7. `associated_columns_not_null`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', 'd74fc600-31c3-307d-9501-5b7f6b09aff5', 'MISSING-1', 3, '',
    '', '', 'ancview_pregnancy', 'associated_columns_not_null', 'diarrhea_dx', 'diarrhea diagnosis',
    $${"name": "diarrhea_dx_has_duration", "col_value": true, "associated_columns": ["max_symptom_duration"]}$$,
    '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```

**8. `expect_similar_means_across_reporters`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', '0cdc9702-91e0-3499-b6f0-4dec12ad0f08', 'BIAS-1', 3,
    'Test for miscalibrated thermometer', '', '', 'ancview_pregnancy',
    'expect_similar_means_across_reporters', 'child_temperature_pre_chw', '',
    '{"key": "reported_by", "quantity": "child_temperature_pre_chw", "data_table": "iccmview_assessment", "id_column": "reported_by"}',
    '2022-01-19 20:00:00.000 -0500', '2022-01-19 20:00:00.000 -0500', 'your-name');
```

**9. `expression_is_true`**
```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', '3081f033-e8f4-4f3b-aea8-36f8c5df05dc', 'INCONSISTENT-1', 3,
    'Wrong treatment/dosage arising from wrong age of children (WT-1)', '', '', 'ancview_pregnancy',
    'expression_is_true', '', '',
    $${"name": "t_under_24_months_wrong_dosage", "expression": "malaria_act_dosage is not null", "condition": "(patient_age_in_months<24) and (malaria_give_act is not null)"}$$,
    '2022-02-14 19:00:00.000 -0500', '2022-02-14 19:00:00.000 -0500', 'your-name');
```

**10. `custom_sql`**

Custom SQL queries require `primary_table` and `primary_table_id_field` to be specified within the SQL query itself:

```sql
INSERT INTO dot.configured_tests VALUES(
    TRUE, 'ScanProject1', 'c4a3da8f-32f4-4e9b-b135-354de203ca90', 'TREAT-1', 6,
    'Test for new family planning method (NFP-1)', '', '', 'ancview_pregnancy', 'custom_sql', '', '',
    format('{%s: %s}',
        to_json('query'::text),
        to_json($query$
            select
                a.patient_id,
                a.reported,
                a.fp_method_being_used,
                'dot_model__fpview_registration' as primary_table,
                'patient_id' as primary_table_id_field
            from {{ ref('dot_model__fpview_registration') }} a
                inner join (
                    select distinct
                        patient_id,
                        max(reported) reported
                    from {{ ref('dot_model__fpview_registration') }}
                    where fp_method_being_used in ('vasectomie','female sterilization')
                    group by patient_id
                ) b on a.patient_id = b.patient_id and a.reported > b.reported
                and fp_method_being_used not in ('vasectomie','female sterilization')
                and fp_method_being_used not like '%condom%'
        $query$::text)
    )::json,
    '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```

---

## 3. Activating and Deactivating Tests

You can quickly deactivate tests for debugging.

### Method A: Using the Appsmith UI
1. Open **Configuration** and choose **Tests**.
2. The **test_activated** column shows whether each test is on.
3. Click **Edit** on the test row.
4. Use the **On/Off** toggle, then submit the form.

### Method B: Using Raw SQL
Update the database directly:
```sql
UPDATE dot.configured_tests 
SET test_activated = FALSE 
WHERE test_id = 'your-test-uuid-here';
```

*(Once configured, head over to [execution.md](./execution.md) to learn how to run your pipeline and generate results).*
