-- public.pncview_danger_sign source

CREATE OR REPLACE VIEW public.pncview_danger_sign
AS SELECT pnc.uuid,
    pnc.patient_id,
    patient.parent_uuid AS patient_parent_uuid,
    pnc.chw AS reported_by,
    chw.parent_uuid AS reported_by_parent,
    pnc.reported,
    'postnatal_followup'::text AS form,
        CASE
            WHEN pnc.first_postnatal = 'yes'::text THEN pnc.delivery_date::date
            ELSE pnc.reported::date
        END AS date_of_event
   FROM useview_postnatal_followup pnc
     LEFT JOIN contactview_metadata patient ON patient.uuid = pnc.patient_id
     LEFT JOIN contactview_metadata chw ON chw.uuid = pnc.chw
  WHERE pnc.danger_signs::boolean AND pnc.patient_id <> ''::text AND pnc.patient_id IS NOT NULL;

-- Permissions

ALTER TABLE public.pncview_danger_sign OWNER TO muso_access;
GRANT ALL ON TABLE public.pncview_danger_sign TO muso_access;
GRANT SELECT ON TABLE public.pncview_danger_sign TO klipfolio;