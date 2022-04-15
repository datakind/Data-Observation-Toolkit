-- public.pncview_expected_enrollments source

CREATE OR REPLACE VIEW public.pncview_expected_enrollments
AS SELECT DISTINCT ON (preg.patient_id) preg.uuid AS pregnancy_id,
    preg.patient_id,
    preg.patient_id AS patient_uuid,
    preg.reported_by,
    preg.reported_by_parent,
    preg.lmp,
    (preg.lmp + '294 days'::interval)::date AS expected_enrollment_date,
    (preg.lmp + '84 days'::interval)::date AS first_trimester_end,
    preg.reported
   FROM ancview_pregnancy preg
  WHERE preg.patient_id IS NOT NULL AND preg.patient_id <> ''::text AND NOT (preg.patient_id IN ( SELECT useview_postnatal_care.patient_id
           FROM useview_postnatal_care
          WHERE useview_postnatal_care.pregnancy_outcome = 'miscarriage'::text))
  ORDER BY preg.patient_id, preg.reported DESC;

-- Permissions

ALTER TABLE public.pncview_expected_enrollments OWNER TO full_access;
GRANT ALL ON TABLE public.pncview_expected_enrollments TO full_access;
GRANT SELECT ON TABLE public.pncview_expected_enrollments TO klipfolio;
GRANT SELECT ON TABLE public.pncview_expected_enrollments TO brac_access;