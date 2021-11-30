from datetime import datetime

import pytest

from monite.services.mailer.schemas import (
    AddCustomTemplateSchema,
    BaseRequestCustomTemplateSchema,
    CustomTemplateDataSchema,
    SystemTemplateDataSchema,
    TemplateDataSchema,
)


@pytest.mark.asyncio
def test_add_custom_template():
    scheme = AddCustomTemplateSchema(
        language_code="DE", subject_template="Jinja", body_template="some body", template_name="hello@monite.com"
    )
    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_custom_template():
    scheme = CustomTemplateDataSchema(
        id=0,
        template_name="hello@monite.com",
        language_code="DE",
        subject_template="Jinja",
        body_template="some body",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_template_data():
    """
    This is a repetitive pattern and should be deleted
    """
    scheme = TemplateDataSchema(language="DE", subject_template="Jinja", body_template="some body")
    assert isinstance(scheme.dict(), dict)


@pytest.mark.asyncio
def test_system_template_data():

    base_template_scheme = BaseRequestCustomTemplateSchema(
        language_code="DE",
        subject_template="Jinja",
        body_template="some body",
    )

    template_scheme = TemplateDataSchema(language="DE", subject_template="Jinja", body_template="some body")

    scheme = SystemTemplateDataSchema(
        template_name="hello@monite.com",
        available_templates=[template_scheme],
    )

    assert isinstance(base_template_scheme.dict(), dict)
    assert isinstance(scheme.dict(), dict)
