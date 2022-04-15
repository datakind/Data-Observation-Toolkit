-- public.ancview_danger_sign source

CREATE OR REPLACE VIEW public.ancview_danger_sign
AS WITH danger_sign_cte AS (
         SELECT ancview_pregnancy.uuid,
            ancview_pregnancy.form,
            ancview_pregnancy.patient_id,
            ancview_pregnancy.uuid AS pregnancy_uuid,
            ancview_pregnancy.reported_by,
            ancview_pregnancy.reported
           FROM ancview_pregnancy
          WHERE ancview_pregnancy.danger_sign_at_reg
        UNION ALL
         SELECT ancview_pregnancy_visit.uuid,
            ancview_pregnancy_visit.form,
            ancview_pregnancy_visit.patient_id,
            ancview_pregnancy_visit.pregnancy_uuid,
            ancview_pregnancy_visit.reported_by,
            ancview_pregnancy_visit.reported
           FROM ancview_pregnancy_visit
          WHERE ancview_pregnancy_visit.danger_signs
        )
 SELECT danger_sign.uuid,
    danger_sign.form,
        CASE
            WHEN danger_sign.pregnancy_uuid IS NULL THEN ( SELECT p.uuid
               FROM ancview_pregnancy p
              WHERE p.reported <= danger_sign.reported AND p.patient_id = danger_sign.patient_id
              ORDER BY p.reported DESC
             LIMIT 1)
            ELSE danger_sign.pregnancy_uuid
        END AS pregnancy_uuid,
    danger_sign.patient_id,
    person.uuid AS patient_uuid,
    person.parent_uuid AS patient_parent_uuid,
    danger_sign.reported_by,
    danger_sign.reported
   FROM danger_sign_cte danger_sign
     JOIN contactview_person person ON danger_sign.patient_id = person.uuid;

-- Permissions

ALTER TABLE public.ancview_danger_sign OWNER TO muso_access;
GRANT ALL ON TABLE public.ancview_danger_sign TO muso_access;
GRANT SELECT ON TABLE public.ancview_danger_sign TO britton;
GRANT SELECT ON TABLE public.ancview_danger_sign TO lassina;
GRANT SELECT ON TABLE public.ancview_danger_sign TO agigo;
GRANT SELECT ON TABLE public.ancview_danger_sign TO lmalle;
GRANT SELECT ON TABLE public.ancview_danger_sign TO klipfolio;
GRANT ALL ON TABLE public.ancview_danger_sign TO idrissa;
GRANT SELECT ON TABLE public.ancview_danger_sign TO diego;
GRANT SELECT ON TABLE public.ancview_danger_sign TO jyang;