-- public.iccmview_assessment source

CREATE OR REPLACE VIEW public.iccmview_assessment
AS WITH assess_cte AS (
         SELECT useview_assessment_old.uuid,
            useview_assessment_old.formname AS form,
            useview_assessment_old.patient_id,
                CASE
                    WHEN useview_assessment_old.patient_age_in_months = ''::text THEN 0
                    ELSE useview_assessment_old.patient_age_in_months::integer
                END AS patient_age_in_months,
            useview_assessment_old.chw AS reported_by,
            useview_assessment_old.chw_area AS reported_by_parent,
            useview_assessment_old.reported,
            useview_assessment_old.has_danger_sign = 'yes'::text AS danger_sign,
                CASE
                    WHEN useview_assessment_old.malaria_tdr_result = 'pos'::text THEN true
                    ELSE false
                END AS malaria_dx,
                CASE
                    WHEN useview_assessment_old.diarrhea_stools_a_day = 'yes'::text THEN true
                    ELSE false
                END AS diarrhea_dx,
                CASE
                    WHEN useview_assessment_old.fast_breathing = 'true'::text THEN true
                    ELSE false
                END AS pneumonia_dx,
                CASE
                    WHEN useview_assessment_old.when_illness = 'c_when_illness_1'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_1'::text OR useview_assessment_old.when_illness = 'c_when_illness_2'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_1'::text OR useview_assessment_old.when_illness = 'c_when_illness_3'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_1'::text OR useview_assessment_old.when_illness = 'c_when_illness_4'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_1'::text OR useview_assessment_old.when_illness = 'c_when_illness_1'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_2'::text OR useview_assessment_old.when_illness = 'c_when_illness_2'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_2'::text OR useview_assessment_old.when_illness = 'c_when_illness_3'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_2'::text OR useview_assessment_old.when_illness = 'c_when_illness_1'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_3'::text OR useview_assessment_old.when_illness = 'c_when_illness_2'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_3'::text OR useview_assessment_old.when_illness = 'c_when_illness_3'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_3'::text OR useview_assessment_old.when_illness = 'c_when_illness_1'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_4'::text OR useview_assessment_old.when_illness = 'c_when_illness_2'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_4'::text OR useview_assessment_old.when_illness = 'c_when_illness_3'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_4'::text THEN 'within_24'::text
                    WHEN useview_assessment_old.when_illness = 'c_when_illness_5'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_1'::text OR useview_assessment_old.when_illness = 'c_when_illness_6'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_1'::text OR useview_assessment_old.when_illness = 'c_when_illness_4'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_2'::text OR useview_assessment_old.when_illness = 'c_when_illness_5'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_2'::text OR useview_assessment_old.when_illness = 'c_when_illness_4'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_3'::text OR useview_assessment_old.when_illness = 'c_when_illness_5'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_3'::text OR useview_assessment_old.when_illness = 'c_when_illness_4'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_4'::text OR useview_assessment_old.when_illness = 'c_when_illness_5'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_4'::text THEN 'within_25_to_48'::text
                    WHEN useview_assessment_old.when_illness = 'c_when_illness_7'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_1'::text OR useview_assessment_old.when_illness = 'c_when_illness_6'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_2'::text OR useview_assessment_old.when_illness = 'c_when_illness_7'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_2'::text OR useview_assessment_old.when_illness = 'c_when_illness_6'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_3'::text OR useview_assessment_old.when_illness = 'c_when_illness_7'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_3'::text OR useview_assessment_old.when_illness = 'c_when_illness_6'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_4'::text OR useview_assessment_old.when_illness = 'c_when_illness_7'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_4'::text THEN 'within_49_to_72'::text
                    WHEN useview_assessment_old.when_illness = 'c_when_illness_8'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_1'::text OR useview_assessment_old.when_illness = 'c_when_illness_8'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_2'::text OR useview_assessment_old.when_illness = 'c_when_illness_8'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_3'::text OR useview_assessment_old.when_illness = 'c_when_illness_8'::text AND useview_assessment_old.assessment_time = 'c_assessment_time_4'::text THEN 'beyond_72'::text
                    ELSE NULL::text
                END AS max_symptom_duration,
            'unknown'::text AS max_symptom_type,
                CASE
                    WHEN useview_assessment_old.refer_to_cscom = 'true'::text OR useview_assessment_old.accompany_to_cscom = 'true'::text THEN true
                    ELSE false
                END AS fu_ref_rec,
                CASE
                    WHEN useview_assessment_old.malaria_tdr_result = 'pos'::text AND useview_assessment_old.accompany_to_cscom = 'false'::text AND useview_assessment_old.refer_to_cscom = 'false'::text OR useview_assessment_old.diarrhea_stools_a_day = 'yes'::text OR useview_assessment_old.fast_breathing = 'true'::text OR useview_assessment_old.symptom_cough <> ''::text THEN true
                    ELSE false
                END AS fu_tx_rec,
                CASE
                    WHEN useview_assessment_old.malaria_tdr_result = 'pos'::text AND useview_assessment_old.accompany_to_cscom = 'false'::text AND useview_assessment_old.refer_to_cscom = 'false'::text OR useview_assessment_old.diarrhea_stools_a_day = 'yes'::text OR useview_assessment_old.fast_breathing = 'true'::text OR useview_assessment_old.symptom_cough <> ''::text THEN true
                    ELSE false
                END AS fu_tx_needed_during_ax,
                CASE
                    WHEN useview_assessment_old.ari_give_amox = 'yes'::text OR useview_assessment_old.diarrhea_give_ors = 'yes'::text OR useview_assessment_old.diarrhea_give_zinc = 'yes'::text OR useview_assessment_old.malaria_give_act = 'yes'::text THEN true
                    ELSE false
                END AS fu_tx_given_during_ax,
            useview_assessment_old.how_child_found
           FROM useview_assessment_old
          WHERE useview_assessment_old.symptom_fever <> ''::text OR useview_assessment_old.tdr_done = 'yes'::text OR useview_assessment_old.symptom_cough <> ''::text OR useview_assessment_old.ari_have_cough = 'yes'::text OR useview_assessment_old.treat_malaria = 'true'::text OR useview_assessment_old.diarrhea_stools_a_day = 'yes'::text OR useview_assessment_old.treat_diarrhea = 'true'::text OR useview_assessment_old.treat_ari = 'true'::text OR useview_assessment_old.malaria_tdr_result = 'pos'::text OR useview_assessment_old.fast_breathing = 'true'::text
        )
 SELECT assess_cte.uuid,
    assess_cte.form,
    assess_cte.patient_id,
    assess_cte.reported_by,
    assess_cte.reported_by_parent,
    assess_cte.reported,
    assess_cte.danger_sign,
    assess_cte.malaria_dx,
    assess_cte.diarrhea_dx,
    assess_cte.pneumonia_dx,
    assess_cte.max_symptom_duration,
    assess_cte.max_symptom_type,
    assess_cte.max_symptom_duration = 'within_24'::text AS within_24,
    assess_cte.max_symptom_duration = 'within_25_to_48'::text AS within_25_to_48,
    assess_cte.max_symptom_duration = 'within_49_to_72'::text AS within_49_to_72,
    assess_cte.max_symptom_duration = 'within_24'::text OR assess_cte.max_symptom_duration = 'within_25_to_48'::text OR assess_cte.max_symptom_duration = 'within_49_to_72'::text AS within_72,
    assess_cte.max_symptom_duration = 'beyond_72'::text AS beyond_72,
    assess_cte.fu_ref_rec OR assess_cte.fu_tx_rec AS fu_rec,
    assess_cte.fu_ref_rec,
    assess_cte.fu_tx_rec,
    assess_cte.fu_tx_needed_during_ax,
    assess_cte.fu_tx_given_during_ax
   FROM assess_cte
  WHERE assess_cte.patient_age_in_months >= 2 AND assess_cte.patient_age_in_months < 60 AND assess_cte.form = 'patient_assessment'::text;

-- Permissions

ALTER TABLE public.iccmview_assessment OWNER TO muso_access;
GRANT ALL ON TABLE public.iccmview_assessment TO muso_access;
GRANT SELECT ON TABLE public.iccmview_assessment TO jyang;
GRANT SELECT ON TABLE public.iccmview_assessment TO klipfolio;
GRANT ALL ON TABLE public.iccmview_assessment TO idrissa;
GRANT SELECT ON TABLE public.iccmview_assessment TO diego;
GRANT SELECT ON TABLE public.iccmview_assessment TO lmalle;
GRANT SELECT ON TABLE public.iccmview_assessment TO agigo;
GRANT SELECT ON TABLE public.iccmview_assessment TO lassina;
GRANT SELECT ON TABLE public.iccmview_assessment TO britton;