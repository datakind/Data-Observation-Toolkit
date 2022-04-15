import pytest
from mock import patch
from .base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.configuration_utils import (  # pylint: disable=wrong-import-order
    _adapt_dbt_config_yaml,
    _adapt_credentials_yaml,
    _adapt_great_expectations_yaml,
    _create_config_file,
    get_dbt_config_custom_schema_output_objects,
)


class ConfigUtilsTest(BaseSelfTestClass):
    """Test Clase"""

    def test_profile_yaml(self):
        """test_profile"""
        db_credentials = {
            "type": "type",
            "host": "host",
            "user": "user",
            "pass": "pass",
            "port": 5433,
            "dbname": "dbname",
            "schema": "schema",
            "threads": 17,
        }
        input_lines = [
            "default:\n",
            "  target: dev\n",
            "  outputs:\n",
            "    dev:\n",
            "      type: postgres\n",
            "      host: dot_db\n",
            "      user: postgres\n",
            "      pass: password\n",
            "      port: 5432\n",
            "      dbname: dot_db\n",
            "      schema: public\n",
            "      threads: 4\n",
        ]
        lines = _adapt_credentials_yaml(db_credentials, input_lines)
        self.assertListEqual(
            lines,
            [
                "default:\n",
                "  target: dev\n",
                "  outputs:\n",
                "    dev:\n",
                "      type: type\n",
                "      host: host\n",
                "      user: user\n",
                "      pass: pass\n",
                "      port: 5433\n",
                "      dbname: dbname\n",
                "      schema: schema\n",
                "      threads: 17\n",
            ],
        )

    def test_adapt_dbt_config_yaml(self):
        """adapt dbt config"""
        input_lines = [
            "name: 'dbt_model_1'\n",
            "version: '0.0.1'\n",
            "\n",
            '# This setting configures which "profile" dbt uses for this project.\n',
            "profile: 'default'\n",
            "\n",
            "# These configurations specify where dbt should look for different types "
            "of files.\n",
            "# The `source-paths` config, for example, states that models in this "
            "project can be\n",
            '# found in the "models/" directory. You probably won\'t need to change '
            "these!\n",
            'model-paths: ["models"]  # here the tool sets the output to a '
            "project-dependent folder\n",
            'analysis-paths: ["analysis"]\n',
            'test-paths: ["tests"]  # here the tool sets the output  to a '
            "project-dependent folder\n",
            'seed-paths: ["data"]\n',
            'macro-paths: ["macros"]\n',
            'snapshot-paths: ["snapshots"]\n',
            "\n",
            'target-path: "target"  # directory which will store compiled SQL files\n',
            "clean-targets:         # directories to be removed by `dbt clean`\n",
            '  - "target"\n',
            '  - "dbt_modules"\n',
            "\n",
            "config-version: 2\n",
            "\n",
            "# Configuring models\n",
            "# Full documentation: https://docs.getdbt.com/docs/configuring-models\n",
            "\n",
            "# In this example config, we tell dbt to build all models in the example/ "
            "directory\n",
            "# as tables. These settings can be overridden in the individual model "
            "files\n",
            "# using the `{{ config(...) }}` macro.\n",
        ]
        expected = [
            "name: 'dbt_model_1'\n",
            "version: '0.0.1'\n",
            "\n",
            '# This setting configures which "profile" dbt uses for this project.\n',
            "profile: 'default'\n",
            "\n",
            "# These configurations specify where dbt should look for different types "
            "of files.\n",
            "# The `source-paths` config, for example, states that models in this "
            "project can be\n",
            '# found in the "models/" directory. You probably won\'t need to change '
            "these!\n",
            'model-paths: ["models/Muso"]\n',
            'analysis-paths: ["analysis"]\n',
            'test-paths: ["tests/Muso"]\n',
            'seed-paths: ["data"]\n',
            'macro-paths: ["macros"]\n',
            'snapshot-paths: ["snapshots"]\n',
            "\n",
            'target-path: "target"  # directory which will store compiled SQL files\n',
            "clean-targets:         # directories to be removed by `dbt clean`\n",
            '  - "target"\n',
            '  - "dbt_modules"\n',
            "\n",
            "config-version: 2\n",
            "\n",
            "# Configuring models\n",
            "# Full documentation: https://docs.getdbt.com/docs/configuring-models\n",
            "\n",
            "# In this example config, we tell dbt to build all models in the example/ "
            "directory\n",
            "# as tables. These settings can be overridden in the individual model "
            "files\n",
            "# using the `{{ config(...) }}` macro.\n",
        ]
        output_lines_1 = _adapt_dbt_config_yaml("Muso", input_lines)
        self.assertListEqual(output_lines_1, expected)

        output_lines_2 = _adapt_dbt_config_yaml(
            "Muso", input_lines, output_schema_suffix="tests"
        )
        self.assertListEqual(
            output_lines_2,
            expected
            + [
                "models:\n",
                "  dbt_model_1:\n",
                "    core:\n",
                "      +schema: 'tests'\n",
                "    test:\n",
                "      +schema: 'tests'\n",
            ],
        )

    def test_adapt_great_expectations_yaml(self):
        """adapt great expectations"""
        input_lines = [
            "# Welcome to Great Expectations! Always know what to expect from your "
            "data.\n",
            "#\n",
            "# Here you can define datasources, batch kwargs generators, integrations "
            "and\n",
            "# more. This file is intended to be committed to your repo. For help "
            "with\n",
            "# configuration please:\n",
            "#   - Read our docs: "
            "https://docs.greatexpectations.io/en/latest/reference/spare_parts/"
            "data_context_reference.html#configuration\n",
            "#   - Join our slack channel: http://greatexpectations.io/slack\n",
            "\n",
            "# config_version refers to the syntactic version of this config file, "
            "and is used in maintaining backwards compatibility\n",
            "# It is auto-generated and usually does not need to be changed.\n",
            "config_version: 2.0\n",
            "\n",
            "# Datasources tell Great Expectations where your data lives and how to "
            "get it.\n",
            "# You can use the CLI command `great_expectations datasource new` to "
            "help you\n",
            "# add a new datasource. Read more at https://docs.greatexpectations.io/"
            "en/latest/reference/core_concepts/datasource.html\n",
            "datasources:\n",
            "  mm:\n",
            "    module_name: great_expectations.datasource\n",
            "    data_asset_type:\n",
            "      module_name: custom_expectations.custom_dataset\n",
            "      class_name: CustomSqlAlchemyDataset\n",
            "    class_name: SqlAlchemyDatasource\n",
            "    credentials: ${mm}\n",
            "\n",
            "# This config file supports variable substitution which enables: "
            "1) keeping\n",
            "# secrets out of source control & 2) environment-based configuration "
            "changes\n",
            "# such as staging vs prod.\n",
            "#\n",
            "# When GE encounters substitution syntax (like `my_key: ${my_value}` or\n",
            "# `my_key: $my_value`) in the great_expectations.yml file, it will "
            "attempt\n",
            "# to replace the value of `my_key` with the value from an environment\n",
            "# variable `my_value` or a corresponding key read "
            "from this config file,\n",
            "# which is defined through the `config_variables_file_path`.\n",
            "# Environment variables take precedence over variables defined here.\n",
            "#\n",
            "# Substitution values defined here can be a simple (non-nested) value,\n",
            "# nested value such as a dictionary, or an environment variable "
            "(i.e. ${ENV_VAR})\n",
            "#\n",
            "#\n",
            "# https://docs.greatexpectations.io/en/latest/guides/how_to_guides/"
            "configuring_data_contexts/how_to_use_a_yaml_file_or_environment_"
            "variables_to_populate_credentials.html\n",
            "\n",
            "\n",
            "config_variables_file_path: uncommitted/config_variables.yml  "
            "# use here different data sources for different projects\n",
            "\n",
            "# The plugins_directory will be added to your python path for "
            "custom modules\n",
            "# used to override and extend Great Expectations.\n",
            "plugins_directory: plugins/\n",
            "\n",
            "stores:\n",
            "# Stores are configurable places to store things like Expectations, "
            "Validations\n",
            "# Data Docs, and more. These are for advanced users only - most users "
            "can simply\n",
            "# leave this section alone.\n",
            "#\n",
            "# Three stores are required: expectations, validations, and\n",
            "# evaluation_parameters, and must exist with a valid store entry. "
            "Additional\n",
            "# stores can be configured for uses such as data_docs, etc.\n",
            "  expectations_store:\n",
            "    class_name: ExpectationsStore\n",
            "    store_backend:\n",
            "      class_name: TupleFilesystemStoreBackend\n",
            "      base_directory: expectations/  # the tool changes this into a "
            "project-dependent directory\n",
            "\n",
            "  validations_store:\n",
            "    class_name: ValidationsStore\n",
            "    store_backend:\n",
            "      class_name: TupleFilesystemStoreBackend\n",
            "      base_directory: uncommitted/validations/  # the tool changes "
            "this into a project-dependent directory\n",
            "\n",
            "  evaluation_parameter_store:\n",
            "    # Evaluation Parameters enable dynamic expectations. "
            "Read more here:\n",
            "    # https://docs.greatexpectations.io/en/latest/reference/"
            "core_concepts/evaluation_parameters.html\n",
            "    class_name: EvaluationParameterStore\n",
            "\n",
            "## checkpoints are only available in GE 0.13\n",
            "#  checkpoint_store:\n",
            "#    class_name: CheckpointStore\n",
            "#    store_backend:\n",
            "#      class_name: TupleFilesystemStoreBackend\n",
            "#      suppress_store_backend_id: true\n",
            "#      base_directory: checkpoints/\n",
            "\n",
            "expectations_store_name: expectations_store\n",
            "validations_store_name: validations_store\n",
            "evaluation_parameter_store_name: evaluation_parameter_store\n",
            "## checkpoints are only available in GE 0.13\n",
            "#checkpoint_store_name: checkpoint_store\n",
            "\n",
            "data_docs_sites:\n",
            "  # Data Docs make it simple to visualize data quality in your project. "
            "These\n",
            "  # include Expectations, Validations & Profiles. The are built for all\n",
            "  # Datasources from JSON artifacts in the local repo including "
            "validations &\n",
            "  # profiles from the uncommitted directory. Read more at "
            "https://docs.greatexpectations.io/en/latest/reference/"
            "core_concepts/data_docs.html\n",
            "  local_site:\n",
            "    class_name: SiteBuilder\n",
            "    # set to false to hide how-to buttons in Data Docs\n",
            "    show_how_to_buttons: true\n",
            "    store_backend:\n",
            "      class_name: TupleFilesystemStoreBackend\n",
            "      base_directory: uncommitted/data_docs/local_site/\n",
            "    site_index_builder:\n",
            "      class_name: DefaultSiteIndexBuilder\n",
            "\n",
            "anonymous_usage_statistics:\n",
            "  data_context_id: dc39ad04-6ad8-4270-8071-60ee1ef81f56\n",
            "  enabled: true\n",
            "notebooks:\n",
            "## concurrency is only valid in GE 0.13\n",
            "#concurrency:\n",
            "#  enabled: false\n",
            "\n",
            "# validation_operators are deprecated in GE version 0.13\n",
            "# GE produces the following warning message\n",
            "#   You appear to be using a legacy capability with the latest config "
            "version (3.0).\n",
            "#   Your data context with this configuration version uses "
            "validation_operators, which are being deprecated.\n",
            "#       Please consult the V3 API migration guide "
            "https://docs.greatexpectations.io/docs/guides/miscellaneous/"
            "migration_guide#migrating-to-the-batch-request-v3-api\n",
            "#       and update your configuration to be compatible with the "
            "version number 3.\n",
            "#   (This message will appear repeatedly until your configuration "
            "is updated.)\n",
            "#\n",
            "# remove the following when checkpoints are properly used\n",
            "# https://legacy.docs.greatexpectations.io/en/0.13.26/guides/"
            "how_to_guides/validation/how_to_create_a_new_checkpoint.html\n",
            "# https://legacy.docs.greatexpectations.io/en/0.13.26/guides/"
            "how_to_guides/validation/how_to_run_a_checkpoint_in_python.html\n",
            "validation_operators:\n",
            "  action_list_operator:\n",
            "    class_name: ActionListValidationOperator\n",
            "    action_list:\n",
            "      - name: store_validation_result\n",
            "        action:\n",
            "          class_name: StoreValidationResultAction\n",
            "      - name: store_evaluation_params\n",
            "        action:\n",
            "          class_name: StoreEvaluationParametersAction\n",
            "      - name: update_data_docs\n",
            "        action:\n",
            "          class_name: UpdateDataDocsAction\n",
        ]
        output_lines = _adapt_great_expectations_yaml("Muso", input_lines)
        self.assertListEqual(
            output_lines,
            [
                "# Welcome to Great Expectations! Always know what to expect from your "
                "data.\n",
                "#\n",
                "# Here you can define datasources, batch kwargs generators, "
                "integrations and\n",
                "# more. This file is intended to be committed to your repo. For help "
                "with\n",
                "# configuration please:\n",
                "#   - Read our docs: https://docs.greatexpectations.io/en/latest/"
                "reference/spare_parts/data_context_reference.html#configuration\n",
                "#   - Join our slack channel: http://greatexpectations.io/slack\n",
                "\n",
                "# config_version refers to the syntactic version of this config file, "
                "and is used in maintaining backwards compatibility\n",
                "# It is auto-generated and usually does not need to be changed.\n",
                "config_version: 2.0\n",
                "\n",
                "# Datasources tell Great Expectations where your data lives and "
                "how to get it.\n",
                "# You can use the CLI command `great_expectations datasource new` to "
                "help you\n",
                "# add a new datasource. Read more at https://docs.greatexpectations"
                ".io/en/latest/reference/core_concepts/datasource.html\n",
                "datasources:\n",
                "  mm:\n",
                "    module_name: great_expectations.datasource\n",
                "    data_asset_type:\n",
                "      module_name: custom_expectations.custom_dataset\n",
                "      class_name: CustomSqlAlchemyDataset\n",
                "    class_name: SqlAlchemyDatasource\n",
                "    credentials: ${mm}\n",
                "\n",
                "# This config file supports variable substitution which enables: "
                "1) keeping\n",
                "# secrets out of source control & 2) environment-based configuration "
                "changes\n",
                "# such as staging vs prod.\n",
                "#\n",
                "# When GE encounters substitution syntax (like `my_key: ${my_value}` "
                "or\n",
                "# `my_key: $my_value`) in the great_expectations.yml file, "
                "it will attempt\n",
                "# to replace the value of `my_key` with the value from an "
                "environment\n",
                "# variable `my_value` or a corresponding key read from this "
                "config file,\n",
                "# which is defined through the `config_variables_file_path`.\n",
                "# Environment variables take precedence over variables defined "
                "here.\n",
                "#\n",
                "# Substitution values defined here can be a simple (non-nested) "
                "value,\n",
                "# nested value such as a dictionary, or an environment variable "
                "(i.e. ${ENV_VAR})\n",
                "#\n",
                "#\n",
                "# https://docs.greatexpectations.io/en/latest/guides/how_to_guides/"
                "configuring_data_contexts/"
                "how_to_use_a_yaml_file_or_environment_variables_to_populate_"
                "credentials.html\n",
                "\n",
                "\n",
                "config_variables_file_path: uncommitted/config_variables.yml  "
                "# use here different data sources for different projects\n",
                "\n",
                "# The plugins_directory will be added to your python path for "
                "custom modules\n",
                "# used to override and extend Great Expectations.\n",
                "plugins_directory: plugins/\n",
                "\n",
                "stores:\n",
                "# Stores are configurable places to store things like Expectations, "
                "Validations\n",
                "# Data Docs, and more. These are for advanced users only - "
                "most users can simply\n",
                "# leave this section alone.\n",
                "#\n",
                "# Three stores are required: expectations, validations, and\n",
                "# evaluation_parameters, and must exist with a valid store entry. "
                "Additional\n",
                "# stores can be configured for uses such as data_docs, etc.\n",
                "  expectations_store:\n",
                "    class_name: ExpectationsStore\n",
                "    store_backend:\n",
                "      class_name: TupleFilesystemStoreBackend\n",
                "      base_directory: expectations/Muso/\n",
                "\n",
                "  validations_store:\n",
                "    class_name: ValidationsStore\n",
                "    store_backend:\n",
                "      class_name: TupleFilesystemStoreBackend\n",
                "      base_directory: uncommitted/validations/Muso/\n",
                "\n",
                "  evaluation_parameter_store:\n",
                "    # Evaluation Parameters enable dynamic expectations. Read more "
                "here:\n",
                "    # https://docs.greatexpectations.io/en/latest/reference/"
                "core_concepts/evaluation_parameters.html\n",
                "    class_name: EvaluationParameterStore\n",
                "\n",
                "## checkpoints are only available in GE 0.13\n",
                "#  checkpoint_store:\n",
                "#    class_name: CheckpointStore\n",
                "#    store_backend:\n",
                "#      class_name: TupleFilesystemStoreBackend\n",
                "#      suppress_store_backend_id: true\n",
                "#      base_directory: checkpoints/\n",
                "\n",
                "expectations_store_name: expectations_store\n",
                "validations_store_name: validations_store\n",
                "evaluation_parameter_store_name: evaluation_parameter_store\n",
                "## checkpoints are only available in GE 0.13\n",
                "#checkpoint_store_name: checkpoint_store\n",
                "\n",
                "data_docs_sites:\n",
                "  # Data Docs make it simple to visualize data quality in your "
                "project. These\n",
                "  # include Expectations, Validations & Profiles. The are built "
                "for all\n",
                "  # Datasources from JSON artifacts in the local repo including "
                "validations &\n",
                "  # profiles from the uncommitted directory. Read more at "
                "https://docs.greatexpectations.io/en/latest/reference/core_concepts/"
                "data_docs.html\n",
                "  local_site:\n",
                "    class_name: SiteBuilder\n",
                "    # set to false to hide how-to buttons in Data Docs\n",
                "    show_how_to_buttons: true\n",
                "    store_backend:\n",
                "      class_name: TupleFilesystemStoreBackend\n",
                "      base_directory: uncommitted/data_docs/local_site/\n",
                "    site_index_builder:\n",
                "      class_name: DefaultSiteIndexBuilder\n",
                "\n",
                "anonymous_usage_statistics:\n",
                "  data_context_id: dc39ad04-6ad8-4270-8071-60ee1ef81f56\n",
                "  enabled: true\n",
                "notebooks:\n",
                "## concurrency is only valid in GE 0.13\n",
                "#concurrency:\n",
                "#  enabled: false\n",
                "\n",
                "# validation_operators are deprecated in GE version 0.13\n",
                "# GE produces the following warning message\n",
                "#   You appear to be using a legacy capability with the latest config "
                "version (3.0).\n",
                "#   Your data context with this configuration version uses "
                "validation_operators, which are being deprecated.\n",
                "#       Please consult the V3 API migration guide "
                "https://docs.greatexpectations.io/docs/guides/miscellaneous/"
                "migration_guide#migrating-to-the-batch-request-v3-api\n",
                "#       and update your configuration to be compatible with the "
                "version number 3.\n",
                "#   (This message will appear repeatedly until your configuration "
                "is updated.)\n",
                "#\n",
                "# remove the following when checkpoints are properly used\n",
                "# https://legacy.docs.greatexpectations.io/en/0.13.26/guides/"
                "how_to_guides/validation/how_to_create_a_new_checkpoint.html\n",
                "# https://legacy.docs.greatexpectations.io/en/0.13.26/guides/"
                "how_to_guides/validation/how_to_run_a_checkpoint_in_python.html\n",
                "validation_operators:\n",
                "  action_list_operator:\n",
                "    class_name: ActionListValidationOperator\n",
                "    action_list:\n",
                "      - name: store_validation_result\n",
                "        action:\n",
                "          class_name: StoreValidationResultAction\n",
                "      - name: store_evaluation_params\n",
                "        action:\n",
                "          class_name: StoreEvaluationParametersAction\n",
                "      - name: update_data_docs\n",
                "        action:\n",
                "          class_name: UpdateDataDocsAction\n",
            ],
        )

    @staticmethod
    def test_config_variables_yaml():
        """test config variables"""
        db_credentials = {
            "type": "type",
            "host": "host",
            "user": "user",
            "pass": "pass",
            "port": 5433,
            "dbname": "dbname",
            "schema": "schema",
            "threads": 17,
        }
        input_lines = [
            "# This config file supports variable substitution which enables: "
            "1) keeping\n",
            "# secrets out of source control & "
            "2) environment-based configuration changes\n",
            "# such as staging vs prod.\n",
            "#\n",
            "# When GE encounters substitution syntax (like `my_key: ${my_value}` or\n",
            "# `my_key: $my_value`) in the great_expectations.yml file, "
            "it will attempt\n",
            "# to replace the value of `my_key` with the value from an environment\n",
            "# variable `my_value` or a corresponding key read from this config "
            "file,\n",
            "# which is defined through the `config_variables_file_path`.\n",
            "# Environment variables take precedence over variables defined here.\n",
            "#\n",
            "# Substitution values defined here can be a simple (non-nested) value,\n",
            "# nested value such as a dictionary, "
            "or an environment variable (i.e. ${ENV_VAR})\n",
            "#\n",
            "#\n",
            "# https://docs.greatexpectations.io/en/latest/guides/how_to_guides/"
            "configuring_data_contexts/how_to_use_a_yaml_file_or_environment_"
            "variables_to_populate_credentials.html\n",
            "\n",
            "instance_id: 67616838-4d81-4db9-9e53-b8fdad70f331\n",
            "mm:\n",
            "  drivername: postgresql\n",
            "  host: dot_db\n",
            "  port: '5432'\n",
            "  username: postgres\n",
            "  password: password\n",
            "  database: dot_db\n",
        ]
        lines = _adapt_credentials_yaml(
            db_credentials,
            input_lines,
            translate_keys={
                "user": "username",
                "type": "drivername",
                "pass": "password",
                "dbname": "database",
            },
        )
        expected_lines = [
            "# This config file supports variable substitution which enables: "
            "1) keeping\n",
            "# secrets out of source control & "
            "2) environment-based configuration changes\n",
            "# such as staging vs prod.\n",
            "#\n",
            "# When GE encounters substitution syntax (like `my_key: ${my_value}` or\n",
            "# `my_key: $my_value`) in the great_expectations.yml file, "
            "it will attempt\n",
            "# to replace the value of `my_key` with the value from an environment\n",
            "# variable `my_value` or a corresponding key read from this config "
            "file,\n",
            "# which is defined through the `config_variables_file_path`.\n",
            "# Environment variables take precedence over variables defined here.\n",
            "#\n",
            "# Substitution values defined here can be a simple (non-nested) value,\n",
            "# nested value such as a dictionary, or an environment "
            "variable (i.e. ${ENV_VAR})\n",
            "#\n",
            "#\n",
            "# https://docs.greatexpectations.io/en/latest/guides/how_to_guides/"
            "configuring_data_contexts/how_to_use_a_yaml_file_or_environment_"
            "variables_to_populate_credentials.html\n",
            "\n",
            "instance_id: 67616838-4d81-4db9-9e53-b8fdad70f331\n",
            "mm:\n",
            "  drivername: type\n",
            "  host: host\n",
            "  port: 5433\n",
            "  username: user\n",
            "  password: pass\n",
            "  database: dbname\n",
        ]
        for r, e in zip(lines, expected_lines):
            r_clean = r.replace("\n", "")
            e_clean = e.replace("\n", "")
            assert (
                r_clean == e_clean
            ), f"\nresult  : '{r_clean}'\nexpected: '{e_clean}'\n"

    def test_create_config_file(self):
        """test create config"""

        def transformation(
            input_lines, replace_dict, **kwargs
        ):  # pylint: disable=unused-argument
            output_lines = []
            for line in input_lines:
                for k, v in replace_dict.items():
                    output_lines.append(line.replace(k, v))
            return output_lines

        # dot_config is a project file
        _create_config_file(
            "./self_tests/data/test_configuration_utils/dot_config.yml",
            "non_existing_path",
            "./self_tests/output/dot_config_1.yml",
            transform_example_file_function=transformation,
            replace_dict={"Muso_db": "x_db"},
        )
        # output file should be identical
        with open("./self_tests/output/dot_config_1.yml", "r") as f_out:
            with open(
                "./self_tests/data/test_configuration_utils/dot_config.yml", "r"
            ) as f_ref:
                output_lines = f_out.readlines()
                ref_lines = f_ref.readlines()
                self.assertListEqual(output_lines, ref_lines)

        # dot_config is an example file - transformations apply
        _create_config_file(
            "non_existing_path",
            "./self_tests/data/test_configuration_utils/dot_config.yml",
            "./self_tests/output/dot_config_2.yml",
            transform_example_file_function=transformation,
            replace_dict={"Muso_db": "x_db"},
        )
        # output file should be transformed
        with open("./self_tests/output/dot_config_2.yml", "r") as f_out:
            with open(
                "./self_tests/data/test_configuration_utils/dot_config.yml", "r"
            ) as f_ref:
                output_lines = f_out.readlines()
                ref_lines = f_ref.readlines()
                self.assertNotEqual(output_lines, ref_lines)
                output_lines_inverse_trans = transformation(
                    output_lines, {"x_db": "Muso_db"}
                )
                self.assertListEqual(output_lines_inverse_trans, ref_lines)

        # test with a finally function
        def finally_function(config_file_lines, final_config_file_name, **kwargs):
            config_file_lines_trans = transformation(
                config_file_lines, replace_dict=kwargs["inverse_replace_dict"]
            )
            with open(final_config_file_name, "w") as f:
                f.writelines(config_file_lines_trans)

        _create_config_file(
            "non_existing_path",
            "./self_tests/data/test_configuration_utils/dot_config.yml",
            "./self_tests/output/dot_config_3.yml",
            transform_example_file_function=transformation,
            finally_action=finally_function,
            replace_dict={"Muso_db": "x_db"},
            inverse_replace_dict={"x_db": "Muso_db"},
        )
        # output file should be identical
        # (transformed and then applied the inverse transform)
        with open("./self_tests/output/dot_config_3.yml", "r") as f_out:
            with open(
                "./self_tests/data/test_configuration_utils/dot_config.yml", "r"
            ) as f_ref:
                output_lines = f_out.readlines()
                ref_lines = f_ref.readlines()
                self.assertListEqual(output_lines, ref_lines)

    @staticmethod
    @patch("utils.configuration_utils._get_config_filename")
    def test_create_config_file_exception(
        mock_get_config_filename,
    ):  # pylint: disable=no-value-for-parameter
        """Test exceptions for create_config_file function"""

        def f(path):
            raise Exception

        mock_get_config_filename.side_effect = f
        with pytest.raises(Exception) as exec_info:
            _create_config_file(
                "non_existing_path",
                "./self_tests/data/test_configuration_utils/dot_config.yml",
                "./self_tests/output/dot_config_x.yml",
                transform_example_file_function=f,
                replace_dict={"Muso_db": "x_db"},
            )
        assert isinstance(exec_info.value, Exception)

    @staticmethod
    def test_dbt_config_custom_schema_output_objects():
        """test get_dbt_config_custom_schema_output_objects"""
        assert get_dbt_config_custom_schema_output_objects() == "tests"
        assert get_dbt_config_custom_schema_output_objects() == "tests"
        assert get_dbt_config_custom_schema_output_objects() == "tests"
