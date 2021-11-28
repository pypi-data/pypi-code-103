from django.test import TestCase
from feincms.module.page.models import Page

from .models import PageButtonContent


class ButtonContentTest(TestCase):
    def setUp(self):
        self.page = Page.objects.create(title="Home", slug="home", override_url="/")

    def test_primary(self):
        content = PageButtonContent.objects.create(
            parent=self.page,
            region="main",
            url="http://example.com",
            style="btn-primary",
            title="TEST",
        )

        html = content.render(kwargs={"context": {}})

        self.assertHTMLEqual(
            html,
            '<a href="http://example.com" class="btn btn-primary">TEST</a>',
        )

    def test_align_center(self):
        content = PageButtonContent.objects.create(
            parent=self.page,
            region="main",
            url="http://example.com",
            style="btn-default",
            title="TEST2",
            align="center",
        )

        html = content.render(kwargs={"context": {}})

        self.assertHTMLEqual(
            html,
            '<p class="text-center btn-center-wrapper">'
            '<a href="http://example.com" class="btn btn-default">TEST2</a>'
            "</p>",
        )
