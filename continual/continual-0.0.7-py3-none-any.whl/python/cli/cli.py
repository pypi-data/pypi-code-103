import typer
import os
import shutil
import yaml


from continual import continual as c
from continual.python.sdk.client import Client
from continual.python.cli import projects as Projects

from pathlib import Path
from typing import List
from enum import Enum

from continual.python.cli import (
    feature_sets,
    models,
    model_versions,
    experiments,
    projects,
    environments,
    organizations,
    users,
    featurestore_config,
    batch_predictions,
    promotions,
    changes,
    utils,
    events,
    reports,
    config,
    utils_dbt,
)
from continual.python.sdk.exceptions import AlreadyExistsError


# ************************#
# Define Typer Structure #
# ************************#

cli = typer.Typer(help="Continual – Operational AI. Simplified.")

cli.add_typer(feature_sets.app, name="feature-sets")
cli.add_typer(models.app, name="models")
cli.add_typer(model_versions.app, name="model-versions")
cli.add_typer(experiments.app, name="experiments")
cli.add_typer(promotions.app, name="promotions")
cli.add_typer(batch_predictions.app, name="batch-predictions")
cli.add_typer(projects.app, name="projects")
cli.add_typer(environments.app, name="environments")
cli.add_typer(organizations.app, name="organizations")
cli.add_typer(changes.app, name="changes")
cli.add_typer(users.app, name="users")
# cli.add_typer(ingestions.app, name="ingestions")
cli.add_typer(featurestore_config.app, name="warehouse-config", hidden=True)
cli.add_typer(events.app, name="events")
cli.add_typer(reports.app, name="report", hidden=True)
cli.add_typer(config.app, name="config")


class ContinualDemo(str, Enum):
    bankmarketing = "bank_marketing"
    kickstarter = "kickstarter"


class CloudDataWarehouse(str, Enum):
    snowflake = "snowflake"
    redshift = "redshift"
    bigquery = "bigquery"
    # synapse = "synapse"
    # sqlserver = "sqlserver"
    # firebolt = "firebolt"


@cli.command("login")
@utils.exit_on_error
def login(
    email: str = typer.Option(..., prompt=True, help="Email address."),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password."),
    project: str = typer.Option(None, help="Default project."),
    endpoint: str = typer.Option(
        None,
        envvar="CONTINUAL_ENDPOINT",
        help="Optional endpoint for private cloud installations.",
    ),
):
    """Log in to Continual.

    Logs in to Continual and saves the session information to
    ~/.continual/continual.yaml which is used by the SDK/CLI. All
    future commands will use th  e session information to authenticate
    and use the default project if not explicitly passed.
    """
    client = Client(endpoint=endpoint)
    user = client.login(email=email, password=password)
    if project is None:
        client.config.project = None
        projects = client.projects.list_all()
        i = 1
        proj_list = []
        if len(list(projects)) > 0:
            for project in projects:
                if i == 1:
                    typer.echo("Select default project:")
                project_id = project.name.split("/")[-1]
                proj_list.append(project.name)
                typer.echo(f" [{i}]: {project.display_name} ({project_id})")
                i += 1
            key = typer.prompt("Choice")
            client.config.project = proj_list[int(key) - 1]
            client.config.environment = "prod"
    else:
        client.config.project = project
        client.config.environment = "prod"
    client.config.save()
    typer.echo(f"🚀 Login successful.  Welcome to Continual, {user.full_name}.")


@cli.command("logout")
@utils.exit_on_error
def logout():
    """Log out of Continual.

    Logs out of the current session.
    """
    c.logout()
    typer.echo("👋 See you later, come back soon!")


@cli.command("checkout")
@utils.exit_on_error
def checkout(
    environment: str = typer.Argument(
        ...,
        envvar="CONTINUAL_ENVIRONMENT",
        help="Unique environment ID within a project.",
    ),
    project: str = typer.Option(None, envvar="CONTINUAL_PROJECT", help="Project ID."),
    strict: bool = typer.Option(False, help="Auto-format invalid environment IDs."),
    wait: bool = typer.Option(
        False, help="Wait for environment to be synced with the base environment."
    ),
):
    project, environment = utils.get_project_and_environment(project, environment)
    client = Client(project=project)

    project_name = client.config.project
    project_id = project_name.split("/")[-1]

    is_environment_invalid = (
        (
            not all(
                map(
                    lambda ch: ch.isdigit() or ch == "_" or ch.islower(),
                    list(environment),
                )
            )
        )
        or (environment[0] == "_")
        or (environment[-1] == "_")
    )
    if is_environment_invalid and strict:
        typer.secho(
            "Invalid environment ID provided. Only lowercased alphanumeric characters and the underscore character are allowed",
            fg="red",
        )
        exit(1)
    elif is_environment_invalid:
        if environment[0] == "_":
            environment = environment[1:]
        if environment[-1] == "_":
            environment = environment[:-1]

        formatted = ""
        for ch in list(environment):
            if (
                not ch.isalnum()
                and not ch == "_"
                and formatted[-1]
                and formatted[-1] != "_"
            ):
                formatted += "_"
            elif ch.isalnum():
                formatted += ch.lower()
        environment = formatted

    try:
        env = client.environments.create(id=environment, source=project_name)

        client.config.set_project(project, save=False)
        client.config.set_environment(environment, save=False)
        client.config.save()

        changes = env.changes.list(5)
        if not changes:
            typer.secho(
                f"Successfully created environment ({environment}). It is even with ({project_name}).",
                fg="green",
            )
            exit(0)

        push = changes[0]

        typer.secho(
            f"Creating environment ({environment}) and syncing with ({project_name}):",
            fg="blue",
        )

        utils.print_change(
            push,
            project_id,
            environment,
            f"Creating environment ({environment}): initial sync with ({project_name})",
        )

    except Exception as e:
        if isinstance(e, AlreadyExistsError):
            client.config.set_project(project, save=False)
            client.config.set_environment(environment, save=False)
            client.config.save()

            typer.secho(
                f"Switched active environment for project ({project_id}) to environment ({environment}).",
                fg="green",
            )
            exit(0)
        else:
            typer.secho(
                "Something went wrong while creating the environment. %s" % str(e),
                fg="red",
            )
            exit(1)


@cli.command("merge")
@utils.exit_on_error
def merge(
    from_environment: str = typer.Option(
        ..., "--from", help="Environment to merge changes from."
    ),
    to_environment: str = typer.Option(
        "prod", "--to", help="Environment to merge changes to. Defaults to production."
    ),
    project: str = typer.Option(None, help="Project ID.", envvar="CONTINUAL_PROJECT"),
    message: str = typer.Option(
        None, help="Optional message to provide context for your merge."
    ),
    plan_only: bool = typer.Option(
        False, "--plan-only", help="View the execution plan without applying changes."
    ),
):
    """Merge changes from one environment to another.

    Pushes all Models and Feature Sets from one environment (--from) into another
    environment (--to).
    """

    client = Client()
    project, from_environment_id = utils.get_project_and_environment(
        project, from_environment
    )
    project, to_environment_id = utils.get_project_and_environment(
        project, to_environment
    )

    if from_environment_id and from_environment == to_environment_id:
        typer.secho("Identical environments provided. Nothing to do.", fg="gray")
        exit(0)
    elif not from_environment_id:
        typer.secho("From environment (--from) got no value.", fg="red")
        exit(1)

    env_slug = utils.get_environment_name(project, to_environment_id)
    from_env_slug = utils.get_environment_name(project, from_environment_id)

    env = client.environments.get(env_slug)

    message = utils.get_message(
        message, f"Merge environment {from_environment_id} into {to_environment_id}"
    )

    push = env.changes.push(
        paths=[],
        resource=from_env_slug,
        message=message,
        trigger="CLI",
        plan_only=plan_only,
    )

    utils.print_change(push, project, to_environment_id, message)


def push_paths(
    paths: List[str],
    client: Client,
    message: str = "",
    plan_only: bool = False,
    purge: bool = False,
    force: bool = False,
    trigger: str = "CLI",
    resource: str = "",
    train_all: bool = False,
    train_none: bool = False,
    update_all: bool = False,
    profile_none: bool = False,
):
    return client.changes.push(
        paths=paths,
        plan_only=plan_only,
        purge=purge,
        update_all=force or update_all,
        message=message,
        trigger=trigger,
        resource=resource,
        train_all=train_all,
        train_none=train_none,
        profile_none=profile_none,
    )


def push_continual(
    paths: List[str],
    client: Client,
    project: str,
    environment: str = "",
    plan_only: bool = False,
    purge: bool = False,
    force: bool = False,
    message: str = "",
    resource: str = "",
    train_all: bool = False,
    train_none: bool = False,
    update_all: bool = False,
    profile_none: bool = False,
):
    project, environment = utils.get_project_and_environment(project, environment)

    # typer path type is PosixPath, which our SDK doesn't expect. Only works w/ strings or list of strings.
    paths = [str(path) for path in paths]
    typer.secho("Pushing path(s) %s into Continual" % str(paths), fg="blue")
    try:
        push = push_paths(
            paths=paths,
            client=client,
            message=message,
            plan_only=plan_only,
            purge=purge,
            force=force,
            resource=resource,
            train_all=train_all,
            train_none=train_none,
            update_all=update_all,
            profile_none=profile_none,
        )
        utils.print_change(push, project, environment, message)
    except Exception as e:
        typer.secho(
            "Failed to push path(s) %s into Continual: %s" % (str(paths), str(e)),
            fg="blue",
        )


def push_dbt(
    client: Client,
    project: str,
    dbt_project_dir: str = "",
    plan_only: bool = False,
    purge: bool = False,
    force: bool = False,
    message: str = "",
    dbt_profiles_dir: str = "",
    dbt_target: str = "",
    dbt_profile: str = "",
    continual_dir: str = "",
    resource: str = "",
    train_all: bool = False,
    train_none: bool = False,
    update_all: bool = False,
    profile_none: bool = False,
):

    dbt_project = "%s/dbt_project.yml" % dbt_project_dir
    # get manifest file
    try:
        with open(dbt_project, "r") as file:
            typer.secho("Detected dbt project. Fetching manifest...", fg="blue")
            text = yaml.load(file, Loader=yaml.FullLoader)
            dbt_target_dir = text.get("target-path", "target")  # default is target
            if not dbt_profile:
                dbt_profile = text.get("profile")
            manifest_file = "%s/%s/manifest.json" % (dbt_project_dir, dbt_target_dir)
            typer.secho(
                "Successfully read manifest file at %s\n" % (manifest_file), fg="green"
            )
    except Exception as e:
        typer.secho(
            "Failed to open dbt project file: %s. Please re-run the command from a dbt project director or use --project-dir to pass in the path to the directory: %s"
            % (dbt_project, str(e)),
            fg="red",
        )
        exit(1)

    # get/create env from dbt target
    try:
        typer.secho(
            "Creating/Retrieving Continual Environment in project %s from dbt target %s in profile %s "
            % (project, dbt_target, dbt_profile),
            fg="blue",
        )
        env_name = utils_dbt.get_or_create_env(
            client, dbt_profiles_dir, dbt_target, dbt_profile
        )
        # reinstatiate client w/ env
        client = Client(project=env_name)
        env = client.environments.get(env_name)
        typer.secho(
            "Successfully created/retrieved environment %s\n" % (env_name), fg="green"
        )
    except Exception as e:
        typer.secho(
            "Unable to get or create environment for target %s and profile %s: %s"
            % (dbt_target, dbt_profile, str(e)),
            fg="red",
        )
        exit(1)

    # need prediction db prefix for stubs
    pred_db_prefix = utils_dbt.get_pred_db_prefix(env)
    # process manifest
    try:
        typer.secho("Processing manifest...", fg="blue")
        with open(manifest_file, "r") as file:
            text = yaml.load(file, Loader=yaml.FullLoader)
            # process manifest, save yamls to dbt target dir, we can then push those
            if continual_dir:
                yaml_dir = continual_dir
            else:
                yaml_dir = "%s/continual" % dbt_target_dir
            paths, stubs = utils_dbt.process_manifest(
                text,
                dbt_project_dir,
                yaml_dir,
                pred_db_prefix,
            )
            typer.secho(
                "Successfully processed manifest and generated continual yamls in %s/%s\n"
                % (dbt_project_dir, yaml_dir),
                fg="green",
            )
    except Exception as e:
        typer.secho(
            "Failed to process manifest file %s: %s" % (manifest_file, str(e)), fg="red"
        )
        exit(1)

    #  we could create project here, but it's a bit awkward for dbt users. Why?
    ## to create a project we'd have to know the organization. And not the name, but the ID.
    ## expecting them to annotate that is probably more of a hassle than just creating a project in the UI.
    ## once project is created we can add env w/o worrying aobut orgs.
    if len(paths) > 0:
        try:
            typer.secho("Pushing path(s) %s into Continual" % str(paths), fg="blue")
            paths = [str(path) for path in paths]
            push = push_paths(
                paths=paths,
                client=client,
                message=message,
                plan_only=plan_only,
                purge=purge,
                force=force,
                resource=resource,
                train_all=train_all,
                train_none=train_none,
                update_all=update_all,
                profile_none=profile_none,
            )
            project_id = project.split("/")[-1]
            environment_id = env.name.split("@")[-1]
            utils.print_change(push, project_id, environment_id, message)
            if stubs:
                utils_dbt.save_stubs(stubs)
            typer.secho("Successfully pushed all dbt models found!", fg="green")
        except Exception as e:
            typer.secho("Failed to push paths %s: %s" % (str(paths, str(e))), fg="red")

    else:
        typer.secho(
            "No dbt models found with appropriate continual configuration. Make sure models are annotated with meta tags appropriately and continual is not disabled on the project level.",
            fg="red",
        )


def push_quickstart(
    paths: List[str],
    client: Client,
    project: str = "",
    environment: str = "",
    plan_only: bool = False,
    purge: bool = False,
    force: bool = False,
    message: str = "",
    resource: str = "",
    train_all: bool = False,
    train_none: bool = False,
    update_all: bool = False,
    profile_none: bool = False,
):
    project, environment = utils.get_project_and_environment(project, environment)

    local_project = os.path.join(os.getcwd(), project)
    if os.path.exists(local_project):
        paths = [local_project]
        push = push_paths(
            paths=paths,
            client=client,
            message=message,
            plan_only=plan_only,
            purge=purge,
            force=force,
            resource=resource,
            train_all=train_all,
            train_none=train_none,
            update_all=update_all,
            profile_none=profile_none,
        )
        utils.print_change(push, project, environment, message)
    else:
        typer.secho(
            "No paths detected and no local project found %s. Please try `continual push` again while providing path arguments."
            % str(local_project),
            fg="red",
        )


@cli.command("push")
@utils.exit_on_error
def push(
    paths: List[Path] = typer.Argument(
        None, exists=True, dir_okay=True, help="Path to YAML files or directories."
    ),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment Name"),
    plan_only: bool = typer.Option(
        False, "--plan-only", help="Display plan only. Do not execute."
    ),
    purge: bool = typer.Option(
        False,
        "--purge",
        help="Delete existing resources not found in pushed configuration.",
    ),
    force: bool = typer.Option(
        False, "--force", help="Force update. Same as --update-all."
    ),
    message: str = typer.Option("", help="Push message."),
    resource: str = typer.Option(
        "", help="Project, Environment, Feature Set, or Model resource name to push."
    ),
    train_all: bool = typer.Option(
        False, "--train-all", help="Train all models in the project."
    ),
    train_none: bool = typer.Option(
        False,
        "--train-none",
        "--no-train",
        help="Do not train Models. NOTE: --train-all will override this option.",
    ),
    update_all: bool = typer.Option(False, "--update-all", help="Force update."),
    profile_none: bool = typer.Option(
        False,
        "--profile-none",
        "--no-profile",
        help="Do not profile resources. NOTE: --train-all will override this option.",
    ),
    dbt_project_dir: Path = typer.Option(
        str(Path.cwd()), "--project-dir", help="dbt project directory", hidden=True
    ),
    dbt_profiles_dir: Path = typer.Option(
        str(os.path.join(Path.home(), ".dbt")),
        "--profiles-dir",
        help="dbt profiles directory",
        hidden=True,
    ),
    dbt_profile: str = typer.Option(
        None,
        "--profile",
        help="dbt profile. Overides profile found in dbt_project.yml",
        hidden=True,
    ),
    dbt_target: str = typer.Option(
        None,
        "--target",
        help="dbt target. Overrides target found in profiles.yml.",
        hidden=True,
    ),
    continual_dir: str = typer.Option(
        None,
        help="directory within dbt project to save continual yaml files. Defaults to ./<target-path>/continual/",
        hidden=True,
    ),
):
    """Push changes to project.

    Pushes all feature set definitions to the project and executes
    the resulting change plan.  The PATHS can be a list of specific feature sets
    or folders of feature set definitions.

    By default, any changed feature sets are reingested and models are
    retrained and promoted.  No feature sets or models are deleted unless
    --purge is passsed. For fine-grained control over the created plan,
    pass additional flags to your push command.
    """

    project, environment = utils.get_project_and_environment(project, environment)
    client = Client(project="%s@%s" % (project, environment))

    message = utils.get_message(
        message, "Pushing path(s) %s from CLI." % str([path.name for path in paths])
    )

    if len(paths) > 0:  # do normal continual stuff
        push_continual(
            paths=paths,
            client=client,
            project=project,
            environment=environment,
            plan_only=plan_only,
            purge=purge,
            force=force,
            message=message,
            resource=resource,
            train_all=train_all,
            train_none=train_none,
            update_all=update_all,
            profile_none=profile_none,
        )
    elif os.path.exists(
        "%s/dbt_project.yml" % dbt_project_dir
    ):  # we are using dbt project, do dbt integration
        push_dbt(
            client=client,
            project=project,
            dbt_project_dir=dbt_project_dir,
            plan_only=plan_only,
            purge=purge,
            force=force,
            message=message,
            dbt_profiles_dir=dbt_profiles_dir,
            dbt_target=dbt_target,
            dbt_profile=dbt_profile,
            continual_dir=continual_dir,
            resource=resource,
            train_all=train_all,
            train_none=train_none,
            update_all=update_all,
            profile_none=profile_none,
        )
    else:  # try to use quickstart hack
        push_quickstart(paths, client, project, plan_only, purge, force, message)


@cli.command("run")
@utils.exit_on_error
def run(
    project: str = typer.Option("", help="Continual Project ID."),
    plan_only: bool = typer.Option(
        False, "--plan-only", help="Display plan only. Do not execute."
    ),
    purge: bool = typer.Option(
        False,
        "--purge",
        help="Delete existing resources not found in pushed configuration.",
    ),
    force: bool = typer.Option(False, "--force", help="Force update"),
    message: str = typer.Option("", help="Push message."),
    dbt_project_dir: Path = typer.Option(
        str(Path.cwd()), "--project-dir", help="dbt project directory"
    ),
    dbt_profiles_dir: Path = typer.Option(
        str(os.path.join(Path.home(), ".dbt")),
        "--profiles-dir",
        help="dbt profiles directory",
    ),
    dbt_profile: str = typer.Option(
        None, "--profile", help="dbt profile. Overides profile found in dbt_project.yml"
    ),
    dbt_target: str = typer.Option(
        None, "--target", help="dbt target. Overrides target found in profiles.yml."
    ),
    continual_dir: str = typer.Option(
        None,
        help="directory within dbt project to save continual yaml files. Defaults to ./<target-path>/continual/",
    ),
    resource: str = typer.Option(
        "", help="Project, Environment, Feature Set, or Model resource name to push."
    ),
    train_all: bool = typer.Option(
        False, "--train-all", help="Train all models in the project."
    ),
    train_none: bool = typer.Option(
        False,
        "--train-none",
        "--no-train",
        help="Do not train Models. NOTE: --train-all will override this option.",
    ),
    update_all: bool = typer.Option(False, "--update-all", help="Force update."),
    profile_none: bool = typer.Option(
        False,
        "--profile-none",
        "--no-profile",
        help="Do not profile resources. NOTE: --train-all will override this option.",
    ),
):
    """Execute Continual on a dbt project.

    Constructs Continual yaml files from dbt models and pushes features and models into Continual.

    Several dbt parameters are supported: --profile, --target, --project-dir, --profiles-dir
    """

    project = utils.get_project(project)
    # skip environment processing, will infer from dbt target
    client = Client(project=project)

    message = utils.get_message(
        message, "Pushing dbt project %s from the CLI." % dbt_project_dir
    )

    push_dbt(
        client,
        project,
        dbt_project_dir,
        plan_only,
        purge,
        force,
        message,
        dbt_profiles_dir,
        dbt_target,
        dbt_profile,
        continual_dir,
        resource,
        train_all,
        train_none,
        profile_none,
        update_all,
    )


@cli.command("quickstart")
@utils.exit_on_error
def quickstart(
    email: str = typer.Option(..., prompt=True, help="Email address."),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password."),
    project: str = typer.Option(None, help="Project ID."),
    demo: ContinualDemo = typer.Option("bank_marketing", help="Demo to create."),
    endpoint: str = typer.Option(
        None,
        envvar="CONTINUAL_ENDPOINT",
        help="Optional endpoint for private cloud installations.",
    ),
    create_project: bool = typer.Option(
        False,
        help="Create Project in Continual? Use only if project does not already exist.",
    ),
    org: str = typer.Option(None, help="Org Name. Use only if creating a project"),
    feature_store: str = typer.Option(
        None, help="Feature Store config name. Use only if creating a project"
    ),
):
    """Initializes a Continual demo project.

    This quick start will:

    1. Log you into Continual.

    2. Create project folder locally with sample yaml.

    3. Optionally creates project in Continual.

    4. Seed demo CSVs into project data warehouse.

    This is meant for demonstration purposes and is not recommended for production use cases.
    """
    login(email=email, password=password, project=project, endpoint=endpoint)
    project_id = utils.get_project(project)
    c = Client(project=project_id)

    try:
        c.projects.get(project_id)
    except:
        if create_project:
            Projects.create(project=project_id, org=org, feature_store=feature_store)
        else:
            typer.secho(
                "Error: project %s doesn't exist. You can optionally create it by using the '--create-project' flag. Otherwise, please create the project in the Continual Web UI."
                % project_id,
                fg="red",
            )
            raise typer.Exit(code=1)

    p = c.projects.get(project_id)
    local_path = os.path.join(os.getcwd(), project_id)
    demo_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        "examples",
        demo.value,
    )

    if not os.path.exists(local_path):
        os.mkdir(local_path)

    for demo_file in os.listdir(demo_path):
        if ".yaml" in demo_file:
            shutil.copy(os.path.join(demo_path, demo_file), local_path)
        if ".csv" in demo_file:
            typer.secho(
                "Seeding project database with file %s. This may take a few minutes..."
                % demo_file,
                fg="blue",
            )
            (schema, db) = p.seed(os.path.join(demo_path, demo_file))
            typer.secho(
                "Created database table %s in schema %s" % (db, schema), fg="green"
            )

    typer.secho(
        "Created folder %s with %s demo files. You may begin building models by executing: "
        % (local_path, demo.value),
        fg="green",
    )
    typer.secho("\t continual push %s" % local_path, fg="blue")


if __name__ == "__main__":
    cli()
