-- public.hhview_visits source

CREATE OR REPLACE VIEW public.hhview_visits
AS (
         SELECT upr.reported,
            upr.reported_by_parent,
            cvp.parent_uuid AS household_id
           FROM useview_patient_record upr
             JOIN contactview_person cvp ON upr.patient_id = cvp.patient_id
        UNION ALL
         SELECT useview_place_record.reported,
            useview_place_record.reported_by_parent,
            useview_place_record.place_id AS household_id
           FROM useview_place_record
) UNION
 SELECT contactview_metadata.reported::timestamp without time zone AS reported,
    contactview_metadata.parent_uuid AS reported_by_parent,
    contactview_metadata.uuid AS household_id
   FROM contactview_metadata
  WHERE contactview_metadata.type = 'clinic'::text;

-- Permissions

ALTER TABLE public.hhview_visits OWNER TO full_access;
GRANT ALL ON TABLE public.hhview_visits TO full_access;
GRANT SELECT ON TABLE public.hhview_visits TO klipfolio;
GRANT SELECT ON TABLE public.hhview_visits TO brac_access;