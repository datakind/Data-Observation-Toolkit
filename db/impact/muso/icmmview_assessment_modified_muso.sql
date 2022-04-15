/* ----------------------------- iccmview_assessment ---------------------------- */
CREATE OR REPLACE VIEW iccmview_assessment_modified_muso AS
 WITH assess_CTE AS
(
-- 2018-06-07 remove 's_' from the beginning on field name according to what have been updated in useview_assessment
SELECT
	uuid,
	formname AS form,
	patient_id,
	CASE
		WHEN patient_age_in_months = '' THEN 0::int
		ELSE patient_age_in_months::int
	END AS patient_age_in_months,
	chw AS reported_by,
	chw_area AS reported_by_parent,
	reported,
	has_danger_sign = 'true' AS danger_sign,
	CASE
		WHEN malaria_tdr_result = 'pos' THEN TRUE
		ELSE FALSE
	END AS malaria_dx,
	CASE
		WHEN diarrhea_stools_a_day = 'yes' THEN TRUE
		ELSE FALSE
	END AS diarrhea_dx,
	CASE
		WHEN fast_breathing = 'true' THEN TRUE
		ELSE FALSE
	END AS pneumonia_dx,
	CASE
		WHEN
		(when_illness = 'c_when_illness_1' AND assessment_time = 'c_assessment_time_1')
		OR (when_illness = 'c_when_illness_2' AND assessment_time = 'c_assessment_time_1')
		OR (when_illness = 'c_when_illness_3' AND assessment_time = 'c_assessment_time_1')
		OR (when_illness = 'c_when_illness_4' AND assessment_time = 'c_assessment_time_1')
		OR (when_illness = 'c_when_illness_1' AND assessment_time = 'c_assessment_time_2')
		OR (when_illness = 'c_when_illness_2' AND assessment_time = 'c_assessment_time_2')
		OR (when_illness = 'c_when_illness_3' AND assessment_time = 'c_assessment_time_2')
		OR (when_illness = 'c_when_illness_1' AND assessment_time = 'c_assessment_time_3')
		OR (when_illness = 'c_when_illness_2' AND assessment_time = 'c_assessment_time_3')
		OR (when_illness = 'c_when_illness_3' AND assessment_time = 'c_assessment_time_3')
		OR (when_illness = 'c_when_illness_1' AND assessment_time = 'c_assessment_time_4')
		OR (when_illness = 'c_when_illness_2' AND assessment_time = 'c_assessment_time_4')
		OR (when_illness = 'c_when_illness_3' AND assessment_time = 'c_assessment_time_4')
		THEN 'within_24'

		WHEN
		(when_illness = 'c_when_illness_5' AND assessment_time = 'c_assessment_time_1')
		OR (when_illness = 'c_when_illness_6' AND assessment_time = 'c_assessment_time_1')
		OR (when_illness = 'c_when_illness_4' AND assessment_time = 'c_assessment_time_2')
		OR (when_illness = 'c_when_illness_5' AND assessment_time = 'c_assessment_time_2')
		OR (when_illness = 'c_when_illness_4' AND assessment_time = 'c_assessment_time_3')
		OR (when_illness = 'c_when_illness_5' AND assessment_time = 'c_assessment_time_3')
		OR (when_illness = 'c_when_illness_4' AND assessment_time = 'c_assessment_time_4')
		OR (when_illness = 'c_when_illness_5' AND assessment_time = 'c_assessment_time_4')
		THEN 'within_25_to_48'

		WHEN
		(when_illness = 'c_when_illness_7' AND assessment_time = 'c_assessment_time_1')
		OR (when_illness = 'c_when_illness_6' AND assessment_time = 'c_assessment_time_2')
		OR (when_illness = 'c_when_illness_7' AND assessment_time = 'c_assessment_time_2')
		OR (when_illness = 'c_when_illness_6' AND assessment_time = 'c_assessment_time_3')
		OR (when_illness = 'c_when_illness_7' AND assessment_time = 'c_assessment_time_3')
		OR (when_illness = 'c_when_illness_6' AND assessment_time = 'c_assessment_time_4')
		OR (when_illness = 'c_when_illness_7' AND assessment_time = 'c_assessment_time_4')
		THEN 'within_49_to_72'

		WHEN
		(when_illness = 'c_when_illness_8' AND assessment_time = 'c_assessment_time_1')
		OR (when_illness = 'c_when_illness_8' AND assessment_time = 'c_assessment_time_2')
		OR (when_illness = 'c_when_illness_8' AND assessment_time = 'c_assessment_time_3')
		OR (when_illness = 'c_when_illness_8' AND assessment_time = 'c_assessment_time_4')
		THEN 'beyond_72'

	END AS max_symptom_duration,
	'unknown'::text AS max_symptom_type,

	CASE
		WHEN refer_to_cscom = 'true' OR accompany_to_cscom = 'true'THEN TRUE
		ELSE FALSE
	END AS fu_ref_rec, /* we are counting these both as referrals */
	CASE
		WHEN (malaria_tdr_result = 'pos' AND accompany_to_cscom = 'false' AND refer_to_cscom = 'false')
				OR diarrhea_stools_a_day = 'yes'
				OR fast_breathing = 'true'
				OR symptom_cough <> ''
				THEN TRUE
		ELSE FALSE
	END AS fu_tx_rec,
	CASE
		WHEN (malaria_tdr_result = 'pos' AND accompany_to_cscom = 'false' AND refer_to_cscom = 'false')
				OR diarrhea_stools_a_day = 'yes'
				OR fast_breathing = 'true'
				OR symptom_cough <> ''
				THEN TRUE
		ELSE FALSE
	END AS fu_tx_needed_during_ax,
	CASE
		WHEN ari_give_amox = 'yes'
			OR diarrhea_give_ors = 'yes'
			OR diarrhea_give_zinc = 'yes'
			OR malaria_give_act = 'yes'
		THEN TRUE
		ELSE FALSE
	END AS fu_tx_given_during_ax,
	how_child_found,

	-- added columns to impact views
	symptom_cough <> '' as cough,
	treat_malnutrition = 'true' as treat_malnutrition,
	ref_danger_sign_red_shakir_strip = 'yes' as muac_strip_color_red,
	symptom_fever <> '' as fever,
	patient_sex,
	-- TBD family_uuid would be the household_id
	-- end added columns to impact views
	-- temperature columns for testing measurement bias
	child_temperature,
	child_temperature_pre_chw,
	child_temperature_pre_chw_retake
FROM
	useview_assessment
WHERE
	-- explicit cast to integer
	-- patient_age_in_months::integer >=2
	-- AND patient_age_in_months::integer < 60
--	AND
	--(child_temperature_pre_chw > 38	/* listing out all symptoms now according to what i can grab from use-view...but cough should be added too */
	symptom_fever <> ''
	OR tdr_done = 'yes'
	OR symptom_cough <> ''
	OR ari_have_cough = 'yes'
	OR treat_malaria = 'true'
	OR diarrhea_stools_a_day = 'yes'
	OR treat_diarrhea = 'true'
	OR treat_ari = 'true'
	OR malaria_tdr_result = 'pos'
	OR fast_breathing = 'true'
	--nutri_color_shakir <> 'yellow' /* right now i'm just excluding malnutrition symptoms, versus requiring inclusion of others */
)
SELECT
	uuid,
	form,
	patient_id,
	reported_by,
	reported_by_parent,
	reported,
	danger_sign,
	malaria_dx,
	diarrhea_dx,
	pneumonia_dx,
	max_symptom_duration,
	max_symptom_type,
	max_symptom_duration = 'within_24' AS within_24,
	max_symptom_duration = 'within_25_to_48' AS within_25_to_48,
	max_symptom_duration = 'within_49_to_72' AS within_49_to_72,
	(max_symptom_duration = 'within_24'
		OR max_symptom_duration = 'within_25_to_48'
		OR max_symptom_duration = 'within_49_to_72'
	)AS within_72,
	max_symptom_duration = 'beyond_72' AS beyond_72,
	(fu_ref_rec OR fu_tx_rec) AS fu_rec,
	fu_ref_rec,
	fu_tx_rec,
	fu_tx_needed_during_ax,
	fu_tx_given_during_ax,
	-- added columns to impact views
	cough,
	treat_malnutrition,
	muac_strip_color_red,
	patient_age_in_months,
	fever,
	patient_sex
	child_temperature,
	child_temperature_pre_chw,
	child_temperature_pre_chw_retake
	-- TBD family_uuid would be the household_id
	-- end added columns to impact views
FROM
	assess_CTE
WHERE
	patient_age_in_months >=2
	AND patient_age_in_months <60
	AND form = 'patient_assessment'
;
