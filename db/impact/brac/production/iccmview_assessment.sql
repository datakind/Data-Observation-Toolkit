-- public.iccmview_assessment source

CREATE OR REPLACE VIEW public.iccmview_assessment
AS SELECT assess.uuid,
    assess.form,
    assess.patient_id,
    assess.reported_by,
    assess.reported_by_parent,
    assess.reported,
    assess.danger_signs <> ''::text AS danger_sign,
    assess.diagnosis_fever ~~ 'malaria%'::text AS malaria_dx,
    assess.diagnosis_diarrhea ~~ 'diarrhea%'::text AS diarrhea_dx,
    assess.diagnosis_cough ~~ 'pneumonia%'::text AS pneumonia_dx,
    GREATEST(assess.fever_duration, assess.diarrhea_duration, assess.coughing_duration) = 1 AS within_24,
    GREATEST(assess.fever_duration, assess.diarrhea_duration, assess.coughing_duration) = 2 AS within_25_to_48,
    GREATEST(assess.fever_duration, assess.diarrhea_duration, assess.coughing_duration) = 3 AS within_49_to_72,
    GREATEST(assess.fever_duration, assess.diarrhea_duration, assess.coughing_duration) <= 3 AND GREATEST(assess.fever_duration, assess.diarrhea_duration, assess.coughing_duration) <> 0 AS within_72,
    GREATEST(assess.fever_duration, assess.diarrhea_duration, assess.coughing_duration) > 3 AS beyond_72,
    assess.referral_follow_up = 'true'::text OR assess.treatment_follow_up = 'true'::text AS fu_rec,
    assess.referral_follow_up = 'true'::text AS fu_ref_rec,
    assess.treatment_follow_up = 'true'::text AS fu_tx_rec,
        CASE
            WHEN (assess.diagnosis_fever = 'malaria1'::text OR assess.diagnosis_fever = 'malaria2'::text) AND assess.patient_age_in_months >= 4 OR assess.diagnosis_cough = 'pneumonia1'::text OR assess.diagnosis_cough = 'pneumonia2b'::text OR assess.diagnosis_cough = 'pneumonia2c'::text OR assess.diagnosis_diarrhea <> ''::text AND assess.patient_age_in_months >= 6 OR assess.diagnosis_diarrhea <> ''::text AND assess.patient_age_in_months >= 2 THEN true
            ELSE false
        END AS fu_tx_needed_during_ax,
    false AS fu_tx_given_during_ax
   FROM useview_assessment assess
  WHERE assess.patient_age_in_months >= 2 AND assess.patient_age_in_months < 60 AND (assess.patient_coughs = 'yes'::text OR assess.patient_diarrhea = 'yes'::text OR assess.patient_fever = 'yes'::text OR assess.danger_signs <> ''::text)
  ORDER BY assess.uuid;

-- Permissions

ALTER TABLE public.iccmview_assessment OWNER TO full_access;
GRANT ALL ON TABLE public.iccmview_assessment TO full_access;
GRANT SELECT ON TABLE public.iccmview_assessment TO klipfolio;
GRANT SELECT ON TABLE public.iccmview_assessment TO brac_access;