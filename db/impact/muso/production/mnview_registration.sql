-- public.mnview_registration source

CREATE OR REPLACE VIEW public.mnview_registration
AS SELECT useview_patient_assessment.uuid,
    'patient_assessment'::text AS form,
    useview_patient_assessment.patient_id,
    useview_patient_assessment.reported_by,
    useview_patient_assessment.reported_by_parent,
    useview_patient_assessment.reported,
    lower(useview_patient_assessment.nutri_color_shakir) = ANY (ARRAY['red'::text, 'yellow'::text]) AS has_malnutrition,
    useview_patient_assessment.patient_age_in_months,
    lower(useview_patient_assessment.nutri_color_shakir) = 'red'::text OR lower(useview_patient_assessment.s_ref_danger_sign_red_shakir_strip) = 'yes'::text AS is_referred_to_hf,
    lower(useview_patient_assessment.nutri_color_shakir) = 'red'::text AS has_severe_malnutrition,
    lower(useview_patient_assessment.nutri_color_shakir) = 'yellow'::text AS has_moderate_malnutrition,
    lower(useview_patient_assessment.nutri_color_shakir) = 'green'::text AS has_no_malnutrition
   FROM useview_patient_assessment
  WHERE useview_patient_assessment.nutri_color_shakir IS NOT NULL AND useview_patient_assessment.patient_age_in_months >= 6 AND useview_patient_assessment.patient_age_in_months <= 60;

-- Permissions

ALTER TABLE public.mnview_registration OWNER TO muso_access;
GRANT ALL ON TABLE public.mnview_registration TO muso_access;
GRANT SELECT ON TABLE public.mnview_registration TO jyang;
GRANT SELECT ON TABLE public.mnview_registration TO idrissa;
GRANT SELECT ON TABLE public.mnview_registration TO diego;
GRANT SELECT ON TABLE public.mnview_registration TO klipfolio;
GRANT SELECT ON TABLE public.mnview_registration TO lassina;
GRANT SELECT ON TABLE public.mnview_registration TO britton;
GRANT SELECT ON TABLE public.mnview_registration TO agigo;