-- public.fpview_follow_up source

CREATE OR REPLACE VIEW public.fpview_follow_up
AS SELECT NULL::text AS uuid,
    NULL::text AS source_id,
    NULL::text AS patient_id,
    NULL::text AS reported_by,
    NULL::text AS reported_by_parent,
    'fp_follow_up'::text AS form,
    NULL::date AS reported,
    NULL::boolean AS is_referral_case,
    NULL::boolean AS is_side_effect_reported,
    NULL::boolean AS is_confirm_received;

-- Permissions

ALTER TABLE public.fpview_follow_up OWNER TO muso_access;
GRANT ALL ON TABLE public.fpview_follow_up TO muso_access;
GRANT SELECT ON TABLE public.fpview_follow_up TO jyang;
GRANT SELECT ON TABLE public.fpview_follow_up TO klipfolio;
GRANT ALL ON TABLE public.fpview_follow_up TO idrissa;
GRANT SELECT ON TABLE public.fpview_follow_up TO diego;
GRANT SELECT ON TABLE public.fpview_follow_up TO lmalle;
GRANT SELECT ON TABLE public.fpview_follow_up TO agigo;
GRANT SELECT ON TABLE public.fpview_follow_up TO lassina;
GRANT SELECT ON TABLE public.fpview_follow_up TO britton;