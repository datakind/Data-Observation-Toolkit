import sqlalchemy as sa
from great_expectations.data_asset import DataAsset
from great_expectations.dataset import SqlAlchemyDataset

import pandas as pd
import numpy as np


class CustomSqlAlchemyDataset(SqlAlchemyDataset):
    """
    Extension of SqlAlchemyDataset including custom expectations for the DOT
    """

    _data_asset_type = "CustomSqlAlchemyDataset"

    @DataAsset.expectation(
        [
            "quantity",
            "key",
            "data_table",
            "schema_core",
            "threshold",
            "samples",
            "id_column",
        ]
    )
    def expect_similar_means_across_reporters(  # pylint: disable=too-many-arguments
        self,
        quantity,
        key,
        data_table,
        schema_core,
        target_table,  # The data being checked (eg prices for airlines) will be different to target table (eg airlines)
        # original schema for data, not needed for this expectation:
        schema_source,  # pylint: disable=unused-argument
        threshold=0.01,
        samples=10000,
        id_column="uuid"
    ):
        """Compares distributions of measurements across CHWs to detect ouliers.
        This expectation produces warnings rather than pointing out errors due to its
        statistical nature.
        See Notebooks/NS-8.0-Bootstrap-Anomaly-Test.ipynb"""

        rows = sa.select([sa.column(quantity), sa.column(key)]).select_from(
            sa.Table(data_table, self._table.metadata, schema=schema_core)
        )

        def get_bs_p_scores(
            table, col, grouping_key, N_samp
        ):  # pylint: disable=invalid-name
            group = (
                table.dropna(subset=[col])
                .groupby(grouping_key)[col]
                .agg(["mean", "std", "count"])
            )
            np.random.seed(42)
            bs = np.random.choice(
                table[col].dropna(), size=(group.shape[0], N_samp)
            )  # pylint: disable=invalid-name

            def bootstrap_p(g):  # pylint: disable=invalid-name
                return (g["mean"] < bs[: int(g["count"]), :].mean(axis=0)).mean()

            group["bs_p_score"] = group.apply(bootstrap_p, axis=1)
            return group

        rows = pd.read_sql(rows, self.engine)

        temp = get_bs_p_scores(rows, quantity, key, samples)

        low = temp[temp["bs_p_score"] > (1 - threshold / temp.shape[0])]
        high = temp[temp["bs_p_score"] < (threshold / temp.shape[0])]

        outside = pd.concat([low, high])

        return {
            "success": len(outside) == 0,
            # TODO We should add more information here, pass back mean, variance for example
            "result": {
                "observed_value": len(outside) / len(temp),
                "element_count": len(temp),
                "unexpected_list": outside.index.to_list(),
                "table": target_table,
                "id_column": id_column,
                "short_name": f"chv_different_{data_table}_{quantity}_distribution",
            },
        }

    @DataAsset.expectation(
        ["patient_key", "time_key", "first_form_name", "second_form_name"]
    )
    def expect_proper_form_sequence_across_tables(  # pylint: disable=too-many-arguments, too-many-locals
        self,
        patient_key,
        time_key,
        first_form_name,
        second_form_name,
        maximum_days=-1,
        minimum_days=-80,
    ):
        """custom expectation"""
        first_rows = sa.select(
            [sa.column(patient_key), sa.column(time_key)]
        ).select_from(sa.Table(first_form_name, self._table.metadata))

        second_rows = sa.select(
            [sa.column("uuid"), sa.column(patient_key), sa.column(time_key)]
        ).select_from(sa.Table(second_form_name, self._table.metadata))

        first_rows = pd.read_sql(first_rows, self.engine)
        second_rows = pd.read_sql(second_rows, self.engine)

        first_series = first_rows.groupby(patient_key)[time_key].agg(
            lambda x: list(x)  # pylint: disable=unnecessary-lambda
        )  # deliveries
        second_series = second_rows.groupby(patient_key)[time_key, "uuid"].agg(
            lambda x: list(x)  # pylint: disable=unnecessary-lambda
        )  # pregnancy follow-ups

        joined = second_series.join(
            first_series.to_frame(), how="left", lsuffix="second"
        )

        breaks = []
        breaking_dates = []
        failing_uuids = []
        for i, r in joined.iterrows():  # pylint: disable=invalid-name
            if r[time_key] is np.nan:
                continue
            for date in r[time_key]:
                for uuid, f_date in zip(r["uuid"], r[time_key + "second"]):
                    differences = (pd.to_datetime(date) - pd.to_datetime(f_date)).days
                    if -1 > differences > -80:
                        breaks.append(i)
                        breaking_dates.append(f_date)
                        failing_uuids.append(uuid)
                        break

        return {
            "success": len(breaks) == 0,
            "result": {
                "observed_value": len(breaks) / len(joined),
                "element_count": len(joined),
                "unexpected_list": failing_uuids,
                "table": second_form_name,
                "id_column": "uuid",
                "short_name": f"improper_{second_form_name}_sequence",
            },
        }

    @DataAsset.expectation(["form_name", "patient_key", "unpack_key", "key"])
    def immunization_opv_given_too_early(self, form_name, patient_key, unpack_key, key):
        """
        notebooks/MT - Immunization Exploration
        Patients are given OPV 1, 2, or 3 immunizations too early

        Parameters
        ----------
        form_name
        patient_key
        unpack_key
        key

        Returns
        -------

        """
        df = sa.select(["*"]).select_from(  # pylint: disable=invalid-name
            sa.Table(form_name, self._table.metadata)
        )  # pylint: disable=invalid-name

        df = pd.read_sql(df, self.engine)

        col_list = list(df.columns)
        remove_list = []
        i = 0
        while i < len(col_list):
            if df[col_list[i]].isnull().all() is True:
                # print(col_list[i],'-->',df[col_list[i]].isnull().all())
                remove_list.append(col_list[i])
            i += 1

        df = df.drop(remove_list, axis=1)

        df_sub = df[[key, patient_key, unpack_key, "patient_date_of_birth", "reported"]]

        i = 0
        count = 0
        all_temps = []
        while i < len(df_sub):
            if df_sub[unpack_key][i] is not None:
                try:
                    df_temp = rapidjson.loads(df_sub[unpack_key][i])
                    uuid = df_sub[key][i]
                    if isinstance(df_temp, list):
                        for d in df_temp:  # pylint: disable=invalid-name
                            d[key] = uuid
                            all_temps.append(d)
                    else:
                        df_temp[key] = uuid
                        all_temps.append(df_temp)
                except:
                    count += 1
            i += 1
        df_sub2 = pd.DataFrame(all_temps)

        df_sub2 = pd.merge(
            df_sub[[key, "reported", patient_key, "patient_date_of_birth"]],
            df_sub2,
            on="uuid",
            how="left",
        )
        df_sub2["immunization_date"] = pd.to_datetime(df_sub2["immunization_date"])
        df_sub2["patient_date_of_birth"] = pd.to_datetime(
            df_sub2["patient_date_of_birth"], errors="coerce", format="%Y-%m-%d"
        )
        df_sub2["days_old"] = (
            df_sub2["immunization_date"] - df_sub2["patient_date_of_birth"]
        ).dt.days

        df_imm = df_sub2[
            (df_sub2["vaccines"].str.contains("opv"))
            | (df_sub2["vaccines_other"].str.contains("opv"))
        ]
        df_imm["opv0_given"] = np.where(
            (df_imm["vaccines"].str.contains("opv0"))
            | (df_imm["vaccines_other"].str.contains("opv0")),
            1,
            0,
        )
        df_imm["opv1_given"] = np.where(
            (df_imm["vaccines"].str.contains("opv1"))
            | (df_imm["vaccines_other"].str.contains("opv1")),
            1,
            0,
        )
        df_imm["opv2_given"] = np.where(
            (df_imm["vaccines"].str.contains("opv2"))
            | (df_imm["vaccines_other"].str.contains("opv2")),
            1,
            0,
        )
        df_imm["opv3_given"] = np.where(
            (df_imm["vaccines"].str.contains("opv3"))
            | (df_imm["vaccines_other"].str.contains("opv3")),
            1,
            0,
        )
        df_imm = df_imm.drop_duplicates()

        df_imm = df_imm[
            [
                "patient_uuid",
                "patient_date_of_birth",
                "immunization_date",
                "opv0_given",
                "opv1_given",
                "opv2_given",
                "opv3_given",
                "days_old",
            ]
        ]
        df_imm = df_imm.drop_duplicates()

        df_imm_0 = df_imm[df_imm["opv0_given"] == 1]
        df_imm_0 = df_imm_0.groupby(["patient_uuid", "opv0_given"], as_index=False).agg(
            {"days_old": "min"}
        )
        df_imm_0 = df_imm_0.rename(columns={"days_old": "days_old0"})

        df_imm_1 = df_imm[df_imm["opv1_given"] == 1]
        df_imm_1 = df_imm_1.groupby(["patient_uuid", "opv1_given"], as_index=False).agg(
            {"days_old": "min"}
        )
        df_imm_1 = df_imm_1.rename(columns={"days_old": "days_old1"})

        df_imm_2 = df_imm[df_imm["opv2_given"] == 1]
        df_imm_2 = df_imm_2.groupby(["patient_uuid", "opv2_given"], as_index=False).agg(
            {"days_old": "min"}
        )
        df_imm_2 = df_imm_2.rename(columns={"days_old": "days_old2"})

        df_imm_3 = df_imm[df_imm["opv3_given"] == 1]
        df_imm_3 = df_imm_3.groupby(["patient_uuid", "opv3_given"], as_index=False).agg(
            {"days_old": "min"}
        )
        df_imm_3 = df_imm_3.rename(columns={"days_old": "days_old3"})

        df_imm_v2 = pd.merge(df_imm_0, df_imm_1, on="patient_uuid", how="outer")
        df_imm_v2 = pd.merge(df_imm_v2, df_imm_2, on="patient_uuid", how="outer")
        df_imm_v2 = pd.merge(df_imm_v2, df_imm_3, on="patient_uuid", how="outer")
        # immunizations for polio given too soon
        df_imm_v2["error"] = np.where(
            (df_imm_v2["opv1_given"] == 1) & (df_imm_v2["days_old1"] < 35),
            1,
            (
                np.where(
                    (df_imm_v2["opv2_given"] == 1) & (df_imm_v2["days_old2"] < 63),
                    1,
                    (
                        np.where(
                            (df_imm_v2["opv3_given"] == 1)
                            & (df_imm_v2["days_old3"] < 91),
                            1,
                            0,
                        )
                    ),
                )
            ),
        )

        output = df_imm_v2[df_imm_v2["error"] == 1]
        unexp = list(output["patient_uuid"].unique())

        return {
            "success": len(unexp) == 0,
            "result": {
                "unexpected_list": unexp,
                "table": form_name,
                "id_column": patient_key,
                "short_name": f"OPV123_given_too_early_in_{form_name}",
            },
        }

    @DataAsset.expectation(["form_name"])
    def fake_expectation_for_test_purposes(
        self,
        form_name: str,
        schema_core: str,
        # original schema for data, not needed for this expectation:
        schema_source: str,  # pylint: disable=unused-argument
    ) -> dict:
        """
        Fake expectation for test purpuses. The test takes the first 5 rows of the
        entity and considers them failed rows

            Parameters
            ----------
            form_name: str
                entity name for the test
            schema_core: str
                name of the schema for dbt entities
            schema_source: str
                name of the schema for impact views

            Returns
            -------
            output : dict
                contains the keys
                - success: bool
                - results:
                    - unexpected_list: list of elements that have failed
                    - table: table name
                    - ...
        """
        df = sa.select(["*"]).select_from(  # pylint: disable=invalid-name
            sa.Table(
                form_name,
                self._table.metadata,
                schema=schema_core,
            )
        )

        df = pd.read_sql(df, self.engine)

        return {
            "success": False,
            "result": {
                "unexpected_list": list(df.head()["reported_by_parent"].unique()),
                "table": form_name,
                "id_column": "reported_by_parent",
                "short_name": f"fake_expectation_for_test_purposes_in_{form_name}",
            },
        }
