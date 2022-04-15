-- public.hhview_visits source

CREATE OR REPLACE VIEW public.hhview_visits
AS SELECT uhc_visits_aggregate.reported_day AS reported,
    uhc_visits_aggregate.reported_by_parent,
    uhc_visits_aggregate.family_uuid AS household_id
   FROM ( SELECT useview_home_visit.reported_by_parent,
            useview_home_visit.patient_id AS family_uuid,
            COALESCE(NULLIF(useview_home_visit.visited_date, ''::text)::date, date_trunc('day'::text, useview_home_visit.reported)::date) AS reported_day
           FROM useview_home_visit
          WHERE useview_home_visit.c_choose_date IS NOT NULL
        UNION
         SELECT uhc_visits.reported_by_parent,
            contact.parent_uuid AS family_uuid,
            uhc_visits.reported_day
           FROM ( SELECT COALESCE(NULLIF(useview_home_visit.visited_date, ''::text)::date, date_trunc('day'::text, useview_home_visit.reported)::date) AS reported_day,
                    useview_home_visit.patient_id,
                    useview_home_visit.reported_by_parent
                   FROM useview_home_visit
                  WHERE useview_home_visit.c_choose_date IS NULL
                UNION
                 SELECT date_trunc('day'::text, useview_assessment_old.reported)::date AS reported_day,
                    useview_assessment_old.patient_id,
                    useview_assessment_old.chw_area AS reported_by_parent
                   FROM useview_assessment_old
                  WHERE useview_assessment_old.how_child_found = 'home_visit'::text
                UNION
                 SELECT date_trunc('day'::text, useview_pregnancy_family_planning.reported)::date AS reported_day,
                    useview_pregnancy_family_planning.patient_id,
                    useview_pregnancy_family_planning.reported_by_parent
                   FROM useview_pregnancy_family_planning
                  WHERE useview_pregnancy_family_planning.s_reg_how_found = 'during_home_visit'::text
                UNION
                 SELECT date_trunc('day'::text, useview_family_planning_men.reported)::date AS reported_day,
                    useview_family_planning_men.patient_id,
                    useview_family_planning_men.reported_by_parent
                   FROM useview_family_planning_men
                  WHERE useview_family_planning_men.reg_how_found = 'during_home_visit'::text) uhc_visits
             JOIN contactview_metadata contact ON contact.uuid = uhc_visits.patient_id) uhc_visits_aggregate
UNION
 SELECT contactview_metadata.reported::date AS reported,
    contactview_metadata.parent_uuid AS reported_by_parent,
    contactview_metadata.uuid AS household_id
   FROM contactview_metadata
  WHERE contactview_metadata.type = 'clinic'::text OR contactview_metadata.contact_type = 'c50_family'::text;

-- Permissions

ALTER TABLE public.hhview_visits OWNER TO muso_access;
GRANT ALL ON TABLE public.hhview_visits TO muso_access;
GRANT SELECT ON TABLE public.hhview_visits TO klipfolio;