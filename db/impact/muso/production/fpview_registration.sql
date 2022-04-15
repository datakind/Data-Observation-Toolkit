-- public.fpview_registration source

CREATE OR REPLACE VIEW public.fpview_registration
AS SELECT useview_pregnancy_family_planning.uuid,
    useview_pregnancy_family_planning.patient_id,
    useview_pregnancy_family_planning.patient_age AS patient_age_in_years,
    useview_pregnancy_family_planning.reported_by,
    useview_pregnancy_family_planning.reported_by_parent,
    useview_pregnancy_family_planning.reported,
    useview_pregnancy_family_planning.counseled_on_planning AS is_counseled,
    useview_pregnancy_family_planning.referral AS is_referred_to_hf,
    useview_pregnancy_family_planning.previous_fp_method IS NULL OR useview_pregnancy_family_planning.previous_fp_method = ''::text AND useview_pregnancy_family_planning.agreed_to_fp AS is_new_to_fp,
    get_english_translation(useview_pregnancy_family_planning.previous_fp_method) <> ''::text AND lower(get_english_translation(useview_pregnancy_family_planning.previous_fp_method)) <> lower(get_english_translation(useview_pregnancy_family_planning.fp_method)) AS is_switch_fp,
    get_english_translation(useview_pregnancy_family_planning.previous_fp_method) <> ''::text AND lower(get_english_translation(useview_pregnancy_family_planning.previous_fp_method)) = lower(get_english_translation(useview_pregnancy_family_planning.fp_method)) AS is_continue_previous_fp,
    NOT useview_pregnancy_family_planning.referral AND useview_pregnancy_family_planning.fp_method_given = 'yes'::text AS is_receive_contraceptive_by_chw,
    get_english_translation(useview_pregnancy_family_planning.fp_method) AS fp_method_being_used
   FROM useview_pregnancy_family_planning
  WHERE lower(useview_pregnancy_family_planning.patient_sex) = 'female'::text AND (useview_pregnancy_family_planning.s_reg_urine_result = 'positive'::text OR useview_pregnancy_family_planning.s_reg_why_not_urine_test = 'mother_already_pregnant'::text) IS NOT TRUE;

-- Permissions

ALTER TABLE public.fpview_registration OWNER TO muso_access;
GRANT ALL ON TABLE public.fpview_registration TO muso_access;
GRANT SELECT ON TABLE public.fpview_registration TO jyang;
GRANT SELECT ON TABLE public.fpview_registration TO klipfolio;
GRANT ALL ON TABLE public.fpview_registration TO idrissa;
GRANT SELECT ON TABLE public.fpview_registration TO diego;
GRANT SELECT ON TABLE public.fpview_registration TO lmalle;
GRANT SELECT ON TABLE public.fpview_registration TO agigo;
GRANT SELECT ON TABLE public.fpview_registration TO lassina;
GRANT SELECT ON TABLE public.fpview_registration TO britton;