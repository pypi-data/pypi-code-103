from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin

# pylint:disable=invalid-name
@dataclass
class AssessmentsStatisticsDTO:
    """
    ---
    properties:
        total:
            type: integer
            description: 
                Total number of assessments run since the customer account
                was created in Cloudrail.
        ci:
            type: integer
            description: 
                Of the total number of assessments, this is the those that
                were run with origin == 'ci'.
        workstation:
            type: integer
            description: 
                Of the total number of assessments, this is the those that
                were run with origin == 'ci'.
    """
    total: int = 0
    ci: int = 0
    workstation: int = 0

@dataclass
class CustomerStatisticsDTO(DataClassJsonMixin):
    """
    ---
    properties:
        accounts:
            type: integer
            description: 
                The number of cloud accounts added in Cloudrail.
    """
    accounts: int = 0
    assessments: AssessmentsStatisticsDTO = AssessmentsStatisticsDTO()

@dataclass
class CustomerDTO(DataClassJsonMixin):
    """
    ---
    properties:
        id:
            type: string
            description: 
                The customer's ID, this is auto-generated
                upon initial creation of the customer account within
                Cloudrail (first sign up).
        external_id:
            type: string
            description: 
                When connecting with AWS accounts, Cloudrail will always
                use the same external ID to assume a role. This ID
                is unique per Cloudrail customer.
        role_name:
            type: string
            description: 
                When connecting with AWS accounts, Cloudrail will always
                use the same role name when assuming a role. This role name
                is unique per Cloudrail customer.
        created_at:
            type: string
            description:
                The date when the customer was first created.
        cloudformation_url:
            type: string
            description:
                This is used internally to speed up the generation
                of CloudFormation templates.
        cloudformation_template_url:
            type: string
            description: 
                This is used internally to speed up the generation
                of CloudFormation templates.
        gcp_identity_terraform_url:
            type: string
            description:
                This is used to register cloudrail on GCP on-boarding process via terraform.
    """
    id: str
    external_id: str
    role_name: str
    created_at: str
    cloudformation_url: str
    cloudformation_template_url: str
    gcp_identity_terraform_url: str
    statistics: CustomerStatisticsDTO = CustomerStatisticsDTO()
