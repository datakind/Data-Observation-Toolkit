-- public.pncview_actual_enrollments source

CREATE OR REPLACE VIEW public.pncview_actual_enrollments
AS WITH confirmed_deliveries_cte AS (
         SELECT DISTINCT ON (deliv_1.patient_id) deliv_1.uuid AS delivery_id,
            deliv_1.patient_id,
            deliv_1.chw AS reported_by,
            chw.parent_uuid AS reported_by_parent,
            deliv_1.delivery_date,
            deliv_1.reported AS delivery_form_submission,
            deliv_1.danger_signs AS danger_sign_at_deliv,
            deliv_1.follow_up_count,
                CASE
                    WHEN deliv_1.where_give_birth = 'cscom'::text THEN true
                    WHEN deliv_1.where_give_birth = 'csref'::text THEN true
                    WHEN deliv_1.where_give_birth = 'hospital'::text THEN true
                    ELSE false
                END AS facility_delivery,
            deliv_1.follow_up_count AS first_pnc_visit_number,
            deliv_1.reported AS first_pnc_visit_date,
            deliv_1.reported AS first_pnc_form_submission,
            deliv_1.task_to_perform
           FROM useview_postnatal_followup deliv_1
             JOIN contactview_metadata chw ON chw.uuid = deliv_1.chw
          WHERE deliv_1.patient_id IS NOT NULL AND deliv_1.patient_id <> ''::text AND deliv_1.first_postnatal = 'yes'::text
          ORDER BY deliv_1.patient_id, deliv_1.reported
        )
 SELECT deliv.delivery_id,
    deliv.patient_id,
    deliv.reported_by,
    deliv.reported_by_parent,
    deliv.delivery_date,
    deliv.danger_sign_at_deliv,
    deliv.facility_delivery,
        CASE
            WHEN deliv.facility_delivery THEN true
            WHEN NOT deliv.facility_delivery AND (deliv.first_pnc_visit_date::date - deliv.delivery_date::date) <= 3 THEN true
            ELSE false
        END AS first_visit_on_time,
    deliv.delivery_form_submission,
    deliv.first_pnc_form_submission
   FROM confirmed_deliveries_cte deliv;

-- Permissions

ALTER TABLE public.pncview_actual_enrollments OWNER TO muso_access;
GRANT ALL ON TABLE public.pncview_actual_enrollments TO muso_access;
GRANT SELECT ON TABLE public.pncview_actual_enrollments TO klipfolio;