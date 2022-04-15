-- public.iccmview_assessment_follow_up source

CREATE OR REPLACE VIEW public.iccmview_assessment_follow_up
AS SELECT fu.uuid,
    fu.form,
    fu.patient_id,
    fu.reported_by,
    fu.reported_by_parent,
    fu.reported,
    fu.form_source_id AS source_id,
    source.form AS source_type,
        CASE
            WHEN source.form = 'assessment'::text THEN fu.form_source_id
            ELSE NULL::text
        END AS original_assessment_id,
    fu.follow_up_type = 'refer_only'::text OR fu.follow_up_type = 'treat_refer'::text AS fu_ref,
    fu.patient_improved = 'yes'::text OR fu.patient_better = 'cured'::text OR fu.patient_better = 'still_recovering'::text AS patient_condition_improved,
        CASE
            WHEN fu.patient_improved <> ''::text OR fu.patient_better <> ''::text THEN true
            ELSE false
        END AS patient_condition_reported,
    fu.follow_up_method = 'in_person'::text AS in_person,
    fu.patient_health_facility_visit = 'yes'::text AS facility_attended,
    fu.follow_up_type = 'treat'::text OR fu.follow_up_type = 'treat_refer'::text AS treatment_confirmed,
    fu.referral_follow_up_needed = 'true'::text AS new_fu_ref_rec,
    fu.follow_up_count,
    fu.danger_signs <> ''::text AS danger_sign
   FROM useview_assessment_follow_up fu
     JOIN iccmview_assessment source ON fu.form_source_id = source.uuid
  WHERE fu.patient_age_in_months >= 2 AND fu.patient_age_in_months < 60;

-- Permissions

ALTER TABLE public.iccmview_assessment_follow_up OWNER TO full_access;
GRANT ALL ON TABLE public.iccmview_assessment_follow_up TO full_access;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO brac_access;
GRANT SELECT ON TABLE public.iccmview_assessment_follow_up TO klipfolio;