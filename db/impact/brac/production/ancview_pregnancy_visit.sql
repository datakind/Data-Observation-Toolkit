-- public.ancview_pregnancy_visit source

CREATE OR REPLACE VIEW public.ancview_pregnancy_visit
AS SELECT useview_visit.uuid,
    useview_visit.source_id AS pregnancy_id,
    useview_visit.patient_id,
    useview_visit.form,
    useview_visit.reported_by,
    useview_visit.reported_by_parent,
    useview_visit.danger_signs AS visit_with_danger_sign,
    useview_visit.reported
   FROM useview_visit
  WHERE useview_visit.visit_type = 'anc'::text;

-- Permissions

ALTER TABLE public.ancview_pregnancy_visit OWNER TO full_access;
GRANT ALL ON TABLE public.ancview_pregnancy_visit TO full_access;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO read_only;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO brac_access;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO klipfolio;