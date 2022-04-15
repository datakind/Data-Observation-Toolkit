-- public.pncview_visits source

CREATE OR REPLACE VIEW public.pncview_visits
AS SELECT pnc.uuid,
    pnc.patient_id,
    pnc.form,
    pnc.reported_by,
    pnc.reported_by_parent,
    pnc.reported::date AS pnc_visit_date,
    deliv.facility_delivery,
    deliv.delivery_date,
    pnc.baby_danger_signs <> ''::text AS visit_with_danger_sign,
    pnc.follow_up_count AS pnc_visit_number,
    (deliv.delivery_date + '42 days'::interval)::date AS pnc_period_end,
        CASE
            WHEN deliv.facility_delivery THEN true
            WHEN NOT deliv.facility_delivery AND deliv.first_visit_on_time THEN true
            WHEN deliv.facility_delivery IS NULL THEN false
            ELSE false
        END AS first_visit_on_time,
    pnc.reported::date <= (deliv.delivery_date + '42 days'::interval)::date AS within_pnc_period,
    pnc.reported
   FROM useview_postnatal_care pnc
     LEFT JOIN pncview_actual_enrollments deliv ON deliv.patient_id = pnc.patient_id
  WHERE pnc.follow_up_count <> 'NaN'::text AND pnc.pregnancy_outcome <> 'miscarriage'::text AND pnc.patient_id <> ''::text AND pnc.patient_id IS NOT NULL AND pnc.follow_up_method = 'in_person'::text
  ORDER BY pnc.patient_id, pnc.reported;

-- Permissions

ALTER TABLE public.pncview_visits OWNER TO full_access;
GRANT ALL ON TABLE public.pncview_visits TO full_access;
GRANT SELECT ON TABLE public.pncview_visits TO klipfolio;
GRANT SELECT ON TABLE public.pncview_visits TO brac_access;