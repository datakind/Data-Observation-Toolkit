-- public.ancview_pregnancy_visit source

CREATE OR REPLACE VIEW public.ancview_pregnancy_visit
AS SELECT anc.uuid,
    anc.formname AS form,
    anc.source_id AS pregnancy_uuid,
    anc.danger_signs = 'true'::text AS danger_signs,
    anc.patient_id,
    person.doc #>> '{parent,_id}'::text[] AS patient_parent_uuid,
    anc.chw AS reported_by,
    anc.reported_date AS reported
   FROM useview_prenatal_followup anc
     JOIN couchdb person ON ((person.doc ->> 'type'::text) = 'person'::text OR (person.doc ->> 'contact_type'::text) = 'person'::text) AND anc.patient_id = (person.doc ->> '_id'::text)
  WHERE anc.close_out = 'false'::text;

-- Permissions

ALTER TABLE public.ancview_pregnancy_visit OWNER TO muso_access;
GRANT ALL ON TABLE public.ancview_pregnancy_visit TO muso_access;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO jyang;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO klipfolio;
GRANT ALL ON TABLE public.ancview_pregnancy_visit TO idrissa;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO diego;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO lmalle;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO agigo;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO lassina;
GRANT SELECT ON TABLE public.ancview_pregnancy_visit TO britton;