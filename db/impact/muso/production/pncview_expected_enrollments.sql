-- public.pncview_expected_enrollments source

CREATE OR REPLACE VIEW public.pncview_expected_enrollments
AS WITH preg_cte AS (
         SELECT DISTINCT ON (preg.patient_id) preg.uuid AS pregnancy_id,
            preg.patient_id,
            preg.chw AS reported_by,
            preg.chw_area AS reported_by_parent,
            preg.lmp::date AS lmp,
            preg.lmp::date + '294 days'::interval AS mdd,
            preg.lmp::date + '84 days'::interval AS first_trimester_end,
            deliv.delivery_date,
            preg.reported_date AS reported,
            preg.s_why_close_out
           FROM useview_prenatal_followup preg
             JOIN contactview_metadata patient ON patient.uuid = preg.patient_id
             LEFT JOIN ancview_delivery deliv ON deliv.patient_id = preg.patient_id
          WHERE preg.patient_id IS NOT NULL AND preg.patient_id <> ''::text
          ORDER BY preg.patient_id, preg.reported_date DESC
        )
 SELECT preg_cte.pregnancy_id,
    preg_cte.patient_id,
    preg_cte.reported_by,
    preg_cte.reported_by_parent,
    preg_cte.lmp,
    preg_cte.mdd,
    preg_cte.first_trimester_end,
        CASE
            WHEN preg_cte.delivery_date IS NULL THEN preg_cte.mdd
            ELSE preg_cte.delivery_date::timestamp without time zone
        END AS expected_enrollment_date,
    preg_cte.reported
   FROM preg_cte
  WHERE preg_cte.s_why_close_out <> 'termination_of_pregnancy'::text;

-- Permissions

ALTER TABLE public.pncview_expected_enrollments OWNER TO muso_access;
GRANT ALL ON TABLE public.pncview_expected_enrollments TO muso_access;
GRANT SELECT ON TABLE public.pncview_expected_enrollments TO klipfolio;