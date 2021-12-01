from typing import Optional

import click
import inquirer

from sym.flow.cli.commands.users.utils import get_or_prompt_service
from sym.flow.cli.errors import MissingIdentityValueError
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.api_operations import (
    Operation,
    OperationHelper,
    OperationSets,
    OperationType,
)
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models.service import SYM_CLOUD_KEY
from sym.flow.cli.models.user import CSVMatcher, Identity, User


@click.command(
    name="update-identity", short_help="Update a User's identity for a specific service"
)
@click.argument("email", required=True, type=str)
@click.option("--new-value", "_new_value", help="The new identity value", type=str)
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
def update_identity(
    options: GlobalOptions,
    email: str,
    _new_value: Optional[str],
    _service_type: Optional[str],
    _external_id: Optional[str],
) -> None:
    """For an existing Sym User, update a single Identity such as an AWS SSO Principal UUID or a Slack User ID.

    \b
    Example:
        `symflow users update-identity user@symops.io`
    """

    api = options.sym_api

    user_to_update = api.get_user(email)
    service = get_or_prompt_service(api, _service_type, _external_id)

    new_identity_value = _new_value or inquirer.text(message="New value?")

    if not new_identity_value:
        raise MissingIdentityValueError(email)

    new_identity = Identity(
        service=service,
        matcher=CSVMatcher(service=service, value=new_identity_value).to_dict(),
    )
    sym_identity = user_to_update.get_identity_from_key(SYM_CLOUD_KEY)

    operations = OperationSets(
        # Don't need to send in all of the existing ones,
        # just the identity to update and the Sym identity to identify the user
        update_user_ops=[
            Operation(
                operation_type=OperationType.update_user,
                original_value=None,
                new_value=User(
                    id=user_to_update.id, identities=[new_identity, sym_identity]
                ),
            )
        ],
        delete_identities_ops=[],
        delete_user_ops=[],
    )

    operation_helper = OperationHelper(options, operations)
    operation_helper.handle_update_users()
