-- public.mnview_follow_up source

CREATE OR REPLACE VIEW public.mnview_follow_up
AS SELECT useview_malnutrition_follow_up.uuid,
    useview_malnutrition_follow_up.patient_id,
    'malnutrition_follow_up'::text AS form,
    useview_malnutrition_follow_up.form_source_id AS source_id,
    useview_malnutrition_follow_up.chw AS reported_by,
    useview_malnutrition_follow_up.chw_area AS reported_by_parent,
    useview_malnutrition_follow_up.reported,
    NULL::boolean AS is_attend_hf,
    NULL::boolean AS is_child_improving,
    NULL::boolean AS is_mn_cured
   FROM useview_malnutrition_follow_up
  WHERE useview_malnutrition_follow_up.patient_age_in_months >= 6 AND useview_malnutrition_follow_up.patient_age_in_months <= 60;

-- Permissions

ALTER TABLE public.mnview_follow_up OWNER TO muso_access;
GRANT ALL ON TABLE public.mnview_follow_up TO muso_access;
GRANT SELECT ON TABLE public.mnview_follow_up TO jyang;
GRANT SELECT ON TABLE public.mnview_follow_up TO idrissa;
GRANT SELECT ON TABLE public.mnview_follow_up TO diego;
GRANT SELECT ON TABLE public.mnview_follow_up TO klipfolio;
GRANT SELECT ON TABLE public.mnview_follow_up TO lassina;
GRANT SELECT ON TABLE public.mnview_follow_up TO britton;
GRANT SELECT ON TABLE public.mnview_follow_up TO agigo;