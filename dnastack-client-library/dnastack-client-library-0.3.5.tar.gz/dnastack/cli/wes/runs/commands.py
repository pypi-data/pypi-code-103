import click
from ...auth import get_oauth_token
from ...utils import get_auth_params, get_config
from dnastack.client import *


@click.group()
@click.pass_context
def runs(ctx):
    pass


@runs.command("execute")
@click.pass_context
@click.option("-u", "--workflow-url", required=True)
@click.option("-a", "--attachment", required=False, multiple=True, default=[])
@click.option("--inputs-file", required=False, default=None)
@click.option("-e", "--engine-parameter", required=False, default=None)
@click.option("--engine-parameters-file", required=False, default=None)
@click.option("-t", "--tag", required=False, default=None)
@click.option("--tags-file", required=False, default=None)
def runs_execute(
    ctx: click.Context,
    workflow_url,
    attachment,
    inputs_file,
    engine_parameter,
    engine_parameters_file,
    tag,
    tags_file,
):
    engine_param = None
    tag_param = None
    oauth_token = get_oauth_token(ctx, wallet_url=get_config(ctx, "wes.wallet.url"))
    auth_params = get_auth_params(ctx, service="wes", use_default=True)

    if engine_parameter:
        engine_param = __parse_key_value_param(engine_parameter, "engine-parameter")

    if tag:
        tag_param = __parse_key_value_param(tag, "tag")

    try:
        result = wes_client.submit_workflow(
            get_config(ctx=ctx, var_path="wes.url"),
            workflow_url,
            oauth_token,
            auth_params,
            attachment,
            inputs_file,
            engine_param,
            engine_parameters_file,
            tag_param,
            tags_file,
        )

        if "error_code" in result.keys():
            raise Exception(f"Workflow failed with exception: {result['msg'].strip()}")

        click.echo(json.dumps(result, indent=4))
    except Exception as e:
        click.secho(f"Unable to execute {workflow_url}: {e}", fg="red")
        sys.exit(1)


def __parse_key_value_param(parameter, param_name):
    param_key_value = parameter.split("=")

    if len(param_key_value) != 2:
        click.secho(
            f"Invalid format for {param_name}. Must be a single key-value pair in the format K=V",
            fg="red",
        )
        sys.exit(1)

    return json.dumps({param_key_value[0].strip(): param_key_value[1].strip()})


@runs.command("list")
@click.pass_context
@click.option("-s", "--page-size", required=False, default=20, type=int)
@click.option("-t", "--page-token", required=False, default=None)
@click.option("--all", is_flag=True, required=False)
def runs_list(ctx, page_size, page_token, all):
    oauth_token = get_oauth_token(ctx, wallet_url=get_config(ctx, "wes.wallet.url"))
    auth_params = get_auth_params(ctx, service="wes", use_default=False)

    try:
        if all:
            response = wes_client.get_list_of_workflows_executed(
                get_config(ctx=ctx, var_path="wes.url"),
                oauth_token,
                auth_params,
                None,
                None,
            )
        else:
            response = wes_client.get_list_of_workflows_executed(
                get_config(ctx=ctx, var_path="wes.url"),
                oauth_token,
                auth_params,
                page_size,
                page_token,
            )

        click.echo(
            json.dumps(
                response,
                indent=4,
            )
        )

        if response.get("next_page_token", None) is not None:
            click.echo("wes runs list --page-token " + response["next_page_token"])

    except Exception as e:
        click.secho(f"Unable to list runs: {e}", fg="red")
        sys.exit(1)
