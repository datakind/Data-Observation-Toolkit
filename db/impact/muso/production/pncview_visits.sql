-- public.pncview_visits source

CREATE OR REPLACE VIEW public.pncview_visits
AS WITH delivery_cte AS (
         SELECT DISTINCT ON (useview_postnatal_followup.patient_id) useview_postnatal_followup.patient_id,
                CASE
                    WHEN useview_postnatal_followup.delivery_date IS NULL THEN useview_postnatal_followup.reported::date
                    WHEN useview_postnatal_followup.delivery_date = ''::text THEN useview_postnatal_followup.reported::date
                    ELSE useview_postnatal_followup.delivery_date::date
                END AS delivery_date,
            useview_postnatal_followup.reported::date AS first_pnc_visit_date,
                CASE
                    WHEN useview_postnatal_followup.where_give_birth = 'cscom'::text THEN true
                    WHEN useview_postnatal_followup.where_give_birth = 'csref'::text THEN true
                    WHEN useview_postnatal_followup.where_give_birth = 'hospital'::text THEN true
                    ELSE false
                END AS facility_delivery,
                CASE
                    WHEN useview_postnatal_followup.first_postnatal = 'yes'::text THEN 1
                    ELSE useview_postnatal_followup.follow_up_count::integer
                END AS follow_up_count
           FROM useview_postnatal_followup
          WHERE useview_postnatal_followup.first_postnatal = 'yes'::text OR useview_postnatal_followup.task_to_perform = 'follow_up'::text
          ORDER BY useview_postnatal_followup.patient_id, useview_postnatal_followup.reported
        ), days_between_cte AS (
         SELECT delivery_cte.patient_id,
            delivery_cte.first_pnc_visit_date,
            delivery_cte.delivery_date,
            delivery_cte.first_pnc_visit_date - delivery_cte.delivery_date AS days_between,
            (delivery_cte.first_pnc_visit_date - delivery_cte.delivery_date) <= 3 AS on_time,
            delivery_cte.facility_delivery
           FROM delivery_cte
        )
 SELECT pnc.uuid,
    pnc.patient_id,
    pnc.chw AS reported_by,
    chw.parent_uuid AS reported_by_parent,
    pnc.reported,
    pnc.reported::date AS pnc_visit_date,
    deliv.facility_delivery,
    deliv.delivery_date,
    pnc.danger_signs AS danger_sign,
        CASE
            WHEN pnc.first_postnatal = 'yes'::text THEN 1
            ELSE pnc.follow_up_count::integer
        END AS pnc_visit_number,
    (deliv.delivery_date + '42 days'::interval)::date AS pnc_period_end,
        CASE
            WHEN deliv.facility_delivery THEN true
            WHEN NOT deliv.facility_delivery AND deliv.on_time THEN true
            WHEN deliv.facility_delivery IS NULL THEN false
            ELSE false
        END AS first_visit_on_time,
    pnc.reported::date <= (deliv.delivery_date + '42 days'::interval)::date AS within_pnc_period
   FROM useview_postnatal_followup pnc
     JOIN contactview_metadata chw ON chw.uuid = pnc.chw
     LEFT JOIN days_between_cte deliv ON deliv.patient_id = pnc.patient_id
  WHERE (pnc.first_postnatal = 'yes'::text OR pnc.task_to_perform = 'follow_up'::text) AND pnc.close_out = 'false'::text AND pnc.first_postnatal <> 'yes'::text AND pnc.follow_up_count <> '1'::text
UNION ALL
 SELECT DISTINCT ON (pnc.patient_id) pnc.uuid,
    pnc.patient_id,
    pnc.chw AS reported_by,
    chw.parent_uuid AS reported_by_parent,
    pnc.reported,
    pnc.reported::date AS pnc_visit_date,
    deliv.facility_delivery,
    deliv.delivery_date,
    pnc.danger_signs AS danger_sign,
        CASE
            WHEN pnc.first_postnatal = 'yes'::text THEN 1
            ELSE pnc.follow_up_count::integer
        END AS pnc_visit_number,
    (deliv.delivery_date + '42 days'::interval)::date AS pnc_period_end,
        CASE
            WHEN deliv.facility_delivery THEN true
            WHEN NOT deliv.facility_delivery AND deliv.on_time THEN true
            WHEN deliv.facility_delivery IS NULL THEN false
            ELSE false
        END AS first_visit_on_time,
    pnc.reported::date <= (deliv.delivery_date + '42 days'::interval)::date AS within_pnc_period
   FROM useview_postnatal_followup pnc
     JOIN contactview_metadata chw ON chw.uuid = pnc.chw
     LEFT JOIN days_between_cte deliv ON deliv.patient_id = pnc.patient_id
  WHERE (pnc.first_postnatal = 'yes'::text OR pnc.task_to_perform = 'follow_up'::text) AND pnc.close_out = 'false'::text AND (pnc.first_postnatal = 'yes'::text OR pnc.follow_up_count = '1'::text);

-- Permissions

ALTER TABLE public.pncview_visits OWNER TO muso_access;
GRANT ALL ON TABLE public.pncview_visits TO muso_access;
GRANT SELECT ON TABLE public.pncview_visits TO klipfolio;