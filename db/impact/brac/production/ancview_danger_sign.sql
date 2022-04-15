-- public.ancview_danger_sign source

CREATE OR REPLACE VIEW public.ancview_danger_sign
AS WITH danger_sign_cte AS (
         SELECT ancview_pregnancy.uuid,
            ancview_pregnancy.form,
            ancview_pregnancy.patient_id,
            ancview_pregnancy.uuid AS pregnancy_id,
            ancview_pregnancy.reported_by,
            ancview_pregnancy.reported_by_parent,
            ancview_pregnancy.reported
           FROM ancview_pregnancy
          WHERE ancview_pregnancy.danger_sign_at_reg
        UNION ALL
         SELECT useview_visit.uuid,
            useview_visit.form,
            useview_visit.patient_id,
            useview_visit.source_id AS pregnancy_id,
            useview_visit.reported_by,
            useview_visit.reported_by_parent,
            useview_visit.reported
           FROM useview_visit
          WHERE useview_visit.visit_type = 'anc'::text AND useview_visit.danger_signs
        )
 SELECT danger_sign_cte.uuid,
    danger_sign_cte.form,
    danger_sign_cte.pregnancy_id,
    danger_sign_cte.patient_id,
    danger_sign_cte.reported_by,
    danger_sign_cte.reported_by_parent,
    danger_sign_cte.reported
   FROM danger_sign_cte;

-- Permissions

ALTER TABLE public.ancview_danger_sign OWNER TO full_access;
GRANT ALL ON TABLE public.ancview_danger_sign TO full_access;
GRANT SELECT ON TABLE public.ancview_danger_sign TO brac_access;
GRANT SELECT ON TABLE public.ancview_danger_sign TO klipfolio;