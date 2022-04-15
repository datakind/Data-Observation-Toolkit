-- public.pncview_danger_sign source

CREATE OR REPLACE VIEW public.pncview_danger_sign
AS SELECT pnc.uuid,
    pnc.patient_id,
    pnc.reported_by,
    pnc.reported_by_parent,
    pnc.form,
        CASE
            WHEN pnc.delivery_date <> ''::text THEN pnc.delivery_date::date
            ELSE pnc.reported::date
        END AS date_of_event,
    pnc.reported
   FROM useview_postnatal_care pnc
  WHERE pnc.baby_danger_signs <> ''::text AND pnc.follow_up_count <> 'NaN'::text AND pnc.pregnancy_outcome <> 'miscarriage'::text AND pnc.patient_id <> ''::text AND pnc.patient_id IS NOT NULL;

-- Permissions

ALTER TABLE public.pncview_danger_sign OWNER TO full_access;
GRANT ALL ON TABLE public.pncview_danger_sign TO full_access;
GRANT SELECT ON TABLE public.pncview_danger_sign TO klipfolio;
GRANT SELECT ON TABLE public.pncview_danger_sign TO brac_access;