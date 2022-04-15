-- public.pncview_actual_enrollments source

CREATE OR REPLACE VIEW public.pncview_actual_enrollments
AS WITH confirmed_deliveries_cte AS (
         SELECT DISTINCT ON (deliv_1.patient_id) deliv_1.uuid AS delivery_id,
            deliv_1.patient_id,
            deliv_1.reported_by,
            deliv_1.reported_by_parent,
                CASE
                    WHEN deliv_1.delivery_date = ''::text THEN NULL::text
                    ELSE deliv_1.delivery_date
                END AS delivery_date,
            deliv_1.reported AS delivery_form_submission,
            deliv_1.baby_danger_signs <> ''::text AS danger_sign_at_deliv,
            deliv_1.pregnancy_outcome,
            deliv_1.follow_up_count,
            deliv_1.health_facility_delivery = 'yes'::text AS facility_delivery,
            deliv_1.reported AS first_pnc_visit_date,
            deliv_1.reported AS first_pnc_form_submission,
            deliv_1.follow_up_method
           FROM useview_postnatal_care deliv_1
          WHERE deliv_1.patient_id IS NOT NULL AND deliv_1.patient_id <> ''::text AND deliv_1.follow_up_count = '1'::text AND (deliv_1.pregnancy_outcome = 'healthy'::text OR deliv_1.pregnancy_outcome = 'still_birth'::text OR deliv_1.pregnancy_outcome = ''::text OR deliv_1.pregnancy_outcome IS NULL)
          ORDER BY deliv_1.patient_id, deliv_1.reported
        )
 SELECT deliv.delivery_id,
    deliv.patient_id,
    deliv.reported_by,
    deliv.reported_by_parent,
    deliv.delivery_date::date AS delivery_date,
    deliv.danger_sign_at_deliv,
    deliv.facility_delivery,
        CASE
            WHEN deliv.facility_delivery THEN true
            WHEN NOT deliv.facility_delivery AND deliv.follow_up_method = 'in_person'::text AND (deliv.first_pnc_visit_date::date - deliv.delivery_date::date) <= 3 THEN true
            ELSE false
        END AS first_visit_on_time,
    deliv.delivery_form_submission,
    deliv.first_pnc_form_submission
   FROM confirmed_deliveries_cte deliv;

-- Permissions

ALTER TABLE public.pncview_actual_enrollments OWNER TO full_access;
GRANT ALL ON TABLE public.pncview_actual_enrollments TO full_access;
GRANT SELECT ON TABLE public.pncview_actual_enrollments TO klipfolio;
GRANT SELECT ON TABLE public.pncview_actual_enrollments TO brac_access;