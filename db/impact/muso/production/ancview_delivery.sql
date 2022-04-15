-- public.ancview_delivery source

CREATE OR REPLACE VIEW public.ancview_delivery
AS SELECT DISTINCT ON (deliv.patient_id) deliv.uuid,
    'postnatal_followup'::text AS form,
    ( SELECT p.uuid
           FROM ancview_pregnancy p
          WHERE p.reported <= deliv.reported AND p.patient_id = deliv.patient_id
          ORDER BY p.reported DESC
         LIMIT 1) AS pregnancy_uuid,
    true AS delivered,
        CASE
            WHEN deliv.delivery_date IS NULL THEN deliv.reported::date
            WHEN deliv.delivery_date = ''::text THEN deliv.reported::date
            ELSE deliv.delivery_date::date
        END AS delivery_date,
    'healthy'::text AS pregnancy_outcome,
    deliv.where_give_birth AS delivery_code,
        CASE
            WHEN deliv.where_give_birth IS NULL OR deliv.where_give_birth = ''::text THEN NULL::boolean
            WHEN deliv.where_give_birth = 'cscom'::text OR deliv.where_give_birth = 'csref'::text OR deliv.where_give_birth = 'hospital'::text THEN true
            ELSE false
        END AS at_health_facility,
        CASE
            WHEN deliv.where_give_birth IS NULL OR deliv.where_give_birth = ''::text THEN NULL::boolean
            WHEN deliv.where_give_birth = 'cscom'::text OR deliv.where_give_birth = 'csref'::text OR deliv.where_give_birth = 'hospital'::text THEN true
            ELSE false
        END AS with_skilled_care,
    deliv.patient_id,
    person.parent_uuid AS patient_parent_uuid,
    deliv.chw AS reported_by,
    deliv.reported
   FROM useview_postnatal_followup deliv
     JOIN contactview_person person ON deliv.patient_id = person.uuid
  WHERE deliv.patient_id IS NOT NULL AND deliv.patient_id <> ''::text AND deliv.first_postnatal = 'yes'::text
  ORDER BY deliv.patient_id, deliv.reported;

-- Permissions

ALTER TABLE public.ancview_delivery OWNER TO muso_access;
GRANT ALL ON TABLE public.ancview_delivery TO muso_access;
GRANT SELECT ON TABLE public.ancview_delivery TO britton;
GRANT SELECT ON TABLE public.ancview_delivery TO lassina;
GRANT SELECT ON TABLE public.ancview_delivery TO agigo;
GRANT SELECT ON TABLE public.ancview_delivery TO lmalle;
GRANT SELECT ON TABLE public.ancview_delivery TO klipfolio;
GRANT ALL ON TABLE public.ancview_delivery TO idrissa;
GRANT SELECT ON TABLE public.ancview_delivery TO diego;
GRANT SELECT ON TABLE public.ancview_delivery TO jyang;