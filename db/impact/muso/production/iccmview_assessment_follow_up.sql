-- public.iccmview_assessment_follow_up source

CREATE OR REPLACE VIEW public.iccmview_assessment_follow_up
AS SELECT fu.uuid,
    fu.formname AS form,
    fu.patient_id,
    fu.chw AS reported_by,
    fu.chw_area AS reported_by_parent,
    fu.reported,
    fu.form_source_id AS source_id,
    fm.formname AS source_type,
        CASE
            WHEN fm.formname = 'patient_assessment'::text THEN fu.form_source_id
            WHEN fm.formname = 'treatment_follow_up'::text THEN tx.form_source_id
            ELSE NULL::text
        END AS original_assessment_id,
    true AS fu_ref,
        CASE
            WHEN fu.how_disease_progressing = 'improved'::text OR fu.how_disease_progressing = 'cured'::text THEN true
            ELSE false
        END AS patient_condition_improved,
    true AS patient_condition_reported,
    true AS in_person,
    false AS facility_attended,
    false AS treatment_confirmed
   FROM useview_referral_follow_up fu
     JOIN form_metadata fm ON fu.form_source_id = fm.uuid
     LEFT JOIN useview_treatment_follow_up tx ON fu.form_source_id = tx.uuid
     LEFT JOIN form_metadata fm_tx ON tx.form_source_id = fm_tx.uuid
  WHERE fu.patient_age_in_months >= 2 AND fu.patient_age_in_months < 60 AND fu.task_to_perform = 'follow_up'::text AND fu.formname = 'referral_followup_under_5'::text AND (fm_tx.formname = 'patient_assessment'::text OR fm.formname = 'patient_assessment'::text)
UNION ALL
 SELECT fu.uuid,
    fu.formname AS form,
    fu.patient_id,
    fu.chw AS reported_by,
    fu.chw_area AS reported_by_parent,
    fu.reported,
    fu.form_source_id AS source_id,
    fm.formname AS source_type,
        CASE
            WHEN fm.formname = 'patient_assessment'::text THEN fu.form_source_id
            WHEN fm.formname = 'treatment_follow_up'::text THEN tx.form_source_id
            ELSE NULL::text
        END AS original_assessment_id,
    false AS fu_ref,
        CASE
            WHEN fu.s_how_disease_progressing = 'improved'::text OR fu.s_how_disease_progressing = 'cured'::text THEN true
            ELSE false
        END AS patient_condition_improved,
    true AS patient_condition_reported,
    true AS in_person,
    NULL::boolean AS facility_attended,
    NULL::boolean AS treatment_confirmed
   FROM useview_treatment_follow_up fu
     JOIN form_metadata fm ON fu.form_source_id = fm.uuid
     LEFT JOIN useview_treatment_follow_up tx ON fu.form_source_id = tx.uuid
     LEFT JOIN form_metadata fm_tx ON tx.form_source_id = fm_tx.uuid
  WHERE fu.patient_age_in_months >= 2 AND fu.patient_age_in_months < 60 AND (fm_tx.formname = 'patient_assessment'::text OR fm.formname = 'patient_assessment'::text);

-- Permissions

ALTER TABLE public.iccmview_assessment_follow_up OWNER TO muso_access;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO public;
GRANT ALL ON TABLE public.iccmview_assessment_follow_up TO muso_access;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO jyang;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO idrissa;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO diego;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO klipfolio;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO britton;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO agigo;