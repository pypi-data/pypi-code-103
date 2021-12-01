from typing import Optional

import click

from sym.flow.cli.commands.users.utils import get_or_prompt_service
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.api_operations import (
    Operation,
    OperationHelper,
    OperationSets,
    OperationType,
)
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models.user import User


@click.command(
    name="delete-identity",
    short_help="Delete an Identity for a User",
)
@click.argument("email", required=True, type=str)
@click.option(
    "--service-type",
    "_service_type",
    help="The type of service the identity is tied to",
)
@click.option(
    "--external-id",
    "_external_id",
    help="The identifier for the service",
)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def delete_identity(
    options: GlobalOptions,
    email: str,
    _service_type: Optional[str],
    _external_id: Optional[str],
) -> None:
    """For an existing Sym User, delete a single Identity such as an AWS SSO Principal UUID or a Slack User ID.

    \b
    Example:
        `symflow users delete-identity user@symops.io`

    """
    original_user = options.sym_api.get_user(email)
    service = get_or_prompt_service(options.sym_api, _service_type, _external_id)

    identity_to_delete = original_user.get_identity_from_key(service.service_key)
    if not identity_to_delete:
        click.secho(
            f"User has no identity for service {service.service_key}", fg="yellow"
        )

    new_identities = [i for i in original_user.identities if i != identity_to_delete]

    operations = OperationSets(
        update_user_ops=[],
        delete_identities_ops=[
            Operation(
                operation_type=OperationType.delete_identity,
                original_value=original_user,
                new_value=User(id=original_user.id, identities=new_identities),
            )
        ],
        delete_user_ops=[],
    )

    operation_helper = OperationHelper(options, operations)
    operation_helper.handle_delete_identities()
