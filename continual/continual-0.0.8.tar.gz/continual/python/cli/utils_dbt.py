import typer
import yaml

from continual import continual as c
from continual.python.cli import utils

YAML_TEMPLATE = """
type: {{TYPE}}
name: {{NAME}}
{{ENTITY}}
{{TARGET}}
{{INDEX}}
{{TIME_INDEX}}
{{SPLIT}}
{{COLUMNS}}
{{EXCLUDED_COLUMNS}}
{{TRAINING_CONFIG}}
{{PREDICTION_CONFIG}}
{{PROMOTION_CONFIG}}
{{TABLE_OR_QUERY}}
"""

SQL_STUB_TEMPLATE = """
{{
  config(
    materialized = 'view',
    meta = {'continual.enabled' = False},
    )
}}
SELECT * from {{PRED_DB}}
"""

# def get_or_create_project(client, project_name, org_name, creds):
#     project = None
#     try:
#         project = client.projects.get(project_name)
#     except:
#         logger.debug("Project %s does not exist. Will try to create it." %project_name)

#     if project is None:
#         #create featurestore config
#         type = creds.type
#         #fs_name = "dbt_%s_%s" %(type, project_name)
#         if type == "snowflake":
#             fs_def = {
#                 "type":type,
#                 "host":creds.account,
#                 "database": creds.database,
#                 "warehouse": creds.warehouse,
#                 "username":creds.user,
#                 "password": creds.password
#             }
#             #client.featurestore_config.create(fs_name, fs_def)
#             try:
#                 if not "/" in org_name:
#                     org_name = "organizations/%s" %org_name
#                 project = client.projects.create(project_name, org_name, fs_def)
#                 logger.debug("Created project %s in org %s" %(project_name, org_name))
#             except:
#                 logger.info("Failed to create project for %s in org %s. Please double-check your dw connection credentails" %(project_name, org_name))
#                 raise
#         else:
#             logger.info("Cannot create new continual feature store definition. Unsupported type: %s" %type)
#             raise
#     return project

# builds yaml from template
def build_yaml(
    table_name,
    type,
    name,
    entity,
    index,
    time_index,
    target,
    column_config,
    split,
    training_config,
    prediction_config,
    promotion_config,
    excluded_columns,
):
    index_text = ""
    if index is not None:
        index_text = "index: %s" % index

    time_index_text = ""
    if time_index is not None:
        time_index_text = "time_index: %s" % time_index

    entity_text = ""
    if entity is not None:
        entity_text = "entity: %s" % entity

    target_text = ""
    if target is not None:
        target_text = "target: %s" % target

    split_text = ""
    if split is not None:
        split_text = "split: %s" % split

    training_text = ""
    if training_config is not None:
        training_text = "train:"
        for t in training_config:
            training_text = (
                training_text
                + """
    %s: %s
    """
                % (t, training_config[t])
            )

    prediction_text = ""
    if prediction_config is not None:
        prediction_text = "predict:"
        for p in prediction_config:
            prediction_text = (
                prediction_text
                + """
    %s: %s
    """
                % (p, prediction_config[p])
            )

    promotion_text = ""
    if promotion_config is not None:
        promotion_text = "promote:"
        for p in promotion_config:
            promotion_text = (
                promotion_text
                + """
    %s: %s
    """
                % (p, promotion_config[p])
            )

    column_text = ""
    if column_config is not None:
        column_text = "columns:"
        for col in column_config:
            column_text = (
                column_text
                + """
    - """
            )
            for field in col:
                column_text = (
                    column_text
                    + """%s: %s
      """
                    % (field, col[field])
                )

    excluded_text = ""
    if excluded_columns is not None:
        excluded_text = "exclude_columns:"
        for c in excluded_columns:
            excluded_text = (
                excluded_text
                + """
    - %s"""
                % (c)
            )

    source = "table"
    if type == "Model":
        source = "query"
        table_name = "select * from %s" % table_name

    # need to properly modify spacing in sql:
    yaml = (
        YAML_TEMPLATE.replace("{{TYPE}}", type)
        .replace("{{NAME}}", name)
        .replace("{{ENTITY}}", entity_text)
        .replace("{{TARGET}}", target_text)
        .replace("{{INDEX}}", index_text)
        .replace("{{TIME_INDEX}}", time_index_text)
        .replace("{{SPLIT}}", split_text)
        .replace("{{TRAINING_CONFIG}}", training_text)
        .replace("{{PREDICTION_CONFIG}}", prediction_text)
        .replace("{{PROMOTION_CONFIG}}", promotion_text)
        .replace("{{COLUMNS}}", column_text)
        .replace("{{EXCLUDED_COLUMNS}}", excluded_text)
        .replace("{{TABLE_OR_QUERY}}", "%s: %s" % (source, table_name))
    )
    return yaml


# takes continual config and return yaml text. Only used if continual.enabled is not False
def generate_yaml(continual_configs, name, table_name):
    type = continual_configs.get("continual.type", None)
    name = continual_configs.get(
        "continual.name", name
    )  # allow config overwrite of name
    entity = continual_configs.get("continual.entity", None)
    index = continual_configs.get("continual.index", None)
    time_index = continual_configs.get("continual.time_index", None)
    split = continual_configs.get("continual.split", None)
    target = continual_configs.get("continual.target", None)
    columns = continual_configs.get("continual.columns", None)
    excluded_columns = continual_configs.get("continual.excluded_columns", None)
    training_config = continual_configs.get("continual.training_config", None)
    prediction_config = continual_configs.get("continual.prediction_config", None)
    promotion_config = continual_configs.get("continual.promotion_config", None)
    excluded_columns = continual_configs.get("continual.excluded_columns", None)
    yaml_text = None
    try:
        if (type is None) or (name is None) or (index is None):
            raise Exception(
                "Insufficient inputs. Required configurations missing: continual_name: %s, continual_type: %s, continual_index: %s"
                % (name, type, index)
            )
        if type.lower() == "model":
            if target is None:
                raise Exception(
                    "Insufficient inputs. Model requires a target but none is provided."
                )
            else:
                yaml_text = build_yaml(
                    table_name,
                    "Model",
                    name,
                    entity,
                    index,
                    time_index,
                    target,
                    columns,
                    split,
                    training_config,
                    prediction_config,
                    promotion_config,
                    excluded_columns,
                )
        elif type.lower() == "featureset":
            yaml_text = build_yaml(
                table_name,
                "FeatureSet",
                name,
                entity,
                index,
                time_index,
                target,
                columns,
                split,
                training_config,
                prediction_config,
                promotion_config,
                excluded_columns,
            )
        else:
            typer.secho(
                "continual_type (%s) unrecognized. Must be Either 'Model' or 'FeatureSet'."
                % type,
                fg="red",
            )
            raise Exception("Unsupported Continual Type.")

    except Exception as e:
        typer.secho(
            "\t Failed to build yaml for dbt model %s: %s" % (name, str(e)), fg="red"
        )

    return yaml_text


# generates model stub
def generate_model_stub(pred_db):
    stub_sql = SQL_STUB_TEMPLATE.replace("{{PRED_DB}}", pred_db)
    return stub_sql


def save_stubs(stubs):
    for (path, text) in stubs:
        with open(path, "w+") as f:
            f.write(text)


# processes nodes & generate yaml files
def process_node(node, dbt_project_dir, pred_db_prefix):
    # if we got to this point, we know we have at least continual.type, so continual_config has to be non-null
    keys = node.get("meta").copy()
    keys.update(
        node.get("config").get("meta")
    )  # model-level config should override project-level config
    continual_config = {k: v for k, v in keys.items() if k.startswith("continual.")}
    table_name = node.get("relation_name")
    name = node.get("name")

    ### do all the yaml processing from dbt-continual plugin
    ### only process node if continual is not disabled
    continual_enabled = continual_config.get(
        "continual.enabled", True
    )  # defaults to true
    if continual_enabled:
        try:
            yaml_text = generate_yaml(continual_config, name, table_name)
            stub_path = None
            stub_text = None
            if (continual_config.get("continual.type").lower() == "model") and (
                continual_config.get("continual.create_stub") == True
            ):
                pred_db = "%s.model_%s" % (pred_db_prefix, name)
                stub_text = generate_model_stub(pred_db)
                stub_path = "%s/%s" % (dbt_project_dir, node.get("original_file_path"))
                stub_path = stub_path.replace(".sql", "_predictions.sql")
            return ((name, yaml_text), (stub_path, stub_text))
        except Exception as e:
            typer.secho(
                "Failed to generate yaml for model %s: %s" % (name, str(e)), fg="red"
            )
            return None
    else:
        return None


# proceses manifest file, builds yaml files and saves them to target dir
def process_manifest(manifest_text, dbt_project_dir, yaml_dir, pred_db_prefix):
    nodes = manifest_text.get("nodes")
    paths = []
    stubs = []
    if nodes:
        # we only care about model nodes
        model_nodes = {
            k: v for (k, v) in nodes.items() if v.get("resource_type") == "model"
        }
        if model_nodes:
            # must have a continual.type (featureset or model) set or we can't do anything with it
            continual_nodes = {
                k: v
                for (k, v) in model_nodes.items()
                if v.get("config").get("meta").get("continual.type") is not None
            }  # this is maybe not safe
            yamls = []
            for k, v in continual_nodes.items():
                # create continual yaml
                (continual_yaml, stub) = process_node(
                    v, dbt_project_dir, pred_db_prefix
                )
                if continual_yaml:
                    yamls.append(continual_yaml)
                if stub[0] and stub[1]:
                    stubs.append(stub)
            if len(yamls) > 0:
                # save yamls to dbt target dir
                target_dir = "%s/%s" % (dbt_project_dir, yaml_dir)
                paths = utils.save_yamls(yamls, target_dir)
    return (paths, stubs)


def get_datastore(profiles_file, dbt_profile, dbt_target):
    # get profile connetion info
    datastore = None
    try:
        with open(profiles_file, "r") as file:
            text = yaml.load(file, Loader=yaml.FullLoader)
            target_config = text.get(dbt_profile).get("outputs").get(dbt_target)
            type = target_config.get("type")

            # consider not updating user/pass
            if type.lower() == "snowflake":
                config = {
                    # "host" : target_config.get("account"),
                    # "username" : target_config.get("user"),
                    # "password" : target_config.get("password"),
                    "database": target_config.get("database"),
                    "db_schema": target_config.get("schema"),
                    # "warehouse" : target_config.get("warehouse"),
                    # "role" : target_config.get("role",None),
                }
                datastore = {"type": type, "snowflake": config}
            elif type.lower() == "redshift":
                config = {
                    # "host" : target_config.get("host"),
                    # "username" : target_config.get("user"),
                    # "password" : target_config.get("password"),
                    "database": target_config.get("dbname"),
                    "db_schema": target_config.get("schema"),
                    # "port" : target_config.get("port"),
                }
                datastore = {"type": type, "redshift": config}
            elif type.lower() == "bigquery":
                config = {
                    # "auth_file_name" : target_config.get("project"),
                    "dataset": target_config.get("dataset")
                    or target_config.get("schema"),
                    # "auth_file" : target_config.get("keyfile_json"),
                }
                datastore = {"type": type, "big_query": config}
            else:  # not supported
                typer.secho(
                    "DataStore type %s is not supported by continual at this time."
                    % type,
                    fg="red",
                )
    except:
        pass
    return datastore


def get_default_target(profiles_file, dbt_profile):
    dbt_target = None
    try:
        with open(profiles_file, "r") as file:
            text = yaml.load(file, Loader=yaml.FullLoader)
            dbt_target = text.get(dbt_profile).get("target")
    except:
        typer.secho(
            "No default target found for profile '%s' in profiles file %s. Ensure your profile name is valid and either add a default target for your profile or pass in a target via --target"
            % (dbt_profile, profiles_file),
            fg="red",
        )
        exit(1)

    return dbt_target


# get or create environment
def get_or_create_env(client, dbt_profiles_dir, dbt_target, dbt_profile):
    profiles_file = "%s/profiles.yml" % (dbt_profiles_dir)

    # if no target passed in, use what is the default in the profiles.yml file for the given profile
    # if no default is set, the following errors an exits
    if not dbt_target:
        dbt_target = get_default_target(profiles_file, dbt_profile)

    # get or create env
    env = None
    if dbt_target is not None:
        try:
            env = client.environments.get(dbt_target)
        # doesn't exist, so we'll create it
        except:
            try:
                data_store = get_datastore(profiles_file, dbt_profile, dbt_target)
                env = client.environments.create(
                    dbt_target, data_store=data_store, source=client.config.project
                )
            except Exception as e:
                typer.secho(
                    "Failed to create environment for dbt target %s: %s"
                    % (dbt_target, str(e)),
                    fg="red",
                )
                exit(1)

    return env.name  # should never be None


def get_environment_datastore_type(env):
    type = env.data_store.type
    if type is None or len(type) == 0:
        type = c.projects.get(env.id.split("@")[0]).data_store.type
    return type


def get_pred_db_prefix(e):
    type = get_environment_datastore_type(e)
    if type.lower() == "snowflake":
        # return ("%s.%s" %(e.data_store.snowflake.database,e.data_store.snowflake.schema))
        return "%s.%s" % (
            e.data_store.snowflake.database,
            e.name.split("/")[1].split("@")[0],
        )  # remove when schema is supported in data store and replace with above line
    elif type.lower() == "redshift":
        # return ("%s.%s" %(e.data_store.redshift.database,e.data_store.redshift.schema))
        return "%s.%s" % (
            e.data_store.redshift.database,
            e.name.split("/")[1].split("@")[0],
        )
    elif type.lower() == "bigquery":
        return "%s" % (e.data_store.big_query.dataset)
    else:  # not supported
        typer.secho(
            "Datastore type %s is not supported by continual at this time." % type,
            fg="red",
        )
        return None
