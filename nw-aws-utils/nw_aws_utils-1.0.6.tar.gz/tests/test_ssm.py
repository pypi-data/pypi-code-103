# encoding: utf-8
import pytest
from aws_utils import env_or_ssm
from aws_utils.exceptions import SsmError

def test_env_or_ssm():
    """This test must be run with access to Newsworthy SSM params
    """
    param = env_or_ssm("EXTERNAL_DATA_JWT_TOKEN", "EXTERNAL_DATA_JWT_TOKEN")
    assert param is not None

def test_env_or_ssm_non_existing():
    with pytest.raises(SsmError):
        param = env_or_ssm("NO_EXISTING", "NO_EXISTING")

    param = env_or_ssm("NO_EXISTING", "NO_EXISTING", required=False)
    assert param is None

def test_env_or_ssm_with_region():
    param = env_or_ssm("EXTERNAL_DATA_JWT_TOKEN", "EXTERNAL_DATA_JWT_TOKEN",
                       aws_region="eu-central-1")
    assert param is not None
