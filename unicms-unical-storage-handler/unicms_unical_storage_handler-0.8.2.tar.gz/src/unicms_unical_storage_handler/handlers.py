import urllib

from django.conf import settings
from django.http import (HttpResponse,
                         Http404)
from django.template import Template, Context
from django.utils.translation import gettext_lazy as _

from cms.contexts.handlers import BaseContentHandler
from cms.contexts.models import WebPath
from cms.contexts.utils import contextualize_template, sanitize_path
from cms.pages.models import Page


class BaseStorageHandler(BaseContentHandler):
    template = "storage_base.html"

    def __init__(self, **kwargs):
        super(BaseStorageHandler, self).__init__(**kwargs)
        self.match_dict = self.match.groupdict()
        self.webpath = WebPath.objects.filter(site=self.website,
                                              parent=None,
                                              is_active=True)\
                                      .first()
        if self.webpath.site.pk not in settings.ALLOWED_UNICMS_SITES:
            raise Http404('Website not allowed to show this webpath')

        # only home page of allowed websites
        if not self.webpath or self.match_dict.get('webpath', '/') != self.webpath.fullpath: # pragma: no cover
            raise Http404('Unknown WebPath')

        self.page = Page.objects.filter(is_active=True,
                                        webpath=self.webpath).first()
        self.data = {'request': self.request,
                     'webpath': self.webpath,
                     'website': self.website,
                     'page': self.page,
                     'path': self.match_dict.get('webpath', '/'),
                     'handler': self
        }

    def as_view(self):
        ext_template_sources = contextualize_template(self.template,
                                                      self.page)
        template = Template(ext_template_sources)
        context = Context(self.data)
        return HttpResponse(template.render(context), status=200)

    @property
    def get_base_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        leaf = ('#', settings.CMS_STORAGE_ROOT_LABEL)
        return (leaf,)


class CdSListViewHandler(BaseStorageHandler):
    template = "storage_cdslist.html"

    def as_view(self):

        url_data = {}

        if settings.ALLOWED_CDS_COURSETYPES:
            url_data['coursetype'] = ",".join(settings.ALLOWED_CDS_COURSETYPES)

        params = urllib.parse.urlencode(url_data)
        self.data['url'] = f'{settings.CMS_STORAGE_CDS_API}?{params}'

        return super().as_view()

    @property
    def breadcrumbs(self):
        # leaf = (self.pub_context.url, getattr(self.pub_context.publication, 'title'))
        leaf = ('#', settings.CMS_STORAGE_CDS_LIST_LABEL)
        parent = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        return (parent, leaf)


class CdSInfoViewHandler(BaseStorageHandler):
    template = "storage_cdsinfo.html"

    def __init__(self, **kwargs):
        super(CdSInfoViewHandler, self).__init__(**kwargs)
        self.code = self.match_dict.get('code', '')

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_CDS_API}{self.code}/'
        return super().as_view()

    @property
    def parent_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_CDS_VIEW_PREFIX_PATH}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        # leaf = (self.pub_context.url, getattr(self.pub_context.publication, 'title'))
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        parent = (self.parent_url, settings.CMS_STORAGE_CDS_LIST_LABEL)
        leaf = ('#', self.code)
        return (root, parent, leaf)


class ActivityViewHandler(BaseStorageHandler):
    template = "storage_activity.html"

    def __init__(self, **kwargs):
        super(ActivityViewHandler, self).__init__(**kwargs)
        self.cdsid = self.match_dict.get('cdsid', '')
        self.code = self.match_dict.get('code', '')

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_ACTIVITY_API}{self.code}/'
        return super().as_view()

    @property
    def cdslist_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_CDS_VIEW_PREFIX_PATH}/'
        return sanitize_path(url)

    @property
    def cdsid_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_CDS_VIEW_PREFIX_PATH}/{self.cdsid}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        cdslist = (self.cdslist_url, settings.CMS_STORAGE_CDS_LIST_LABEL)
        cdsid = (self.cdsid_url, self.cdsid)
        activities = (self.cdsid_url, settings.CMS_STORAGE_ACTIVITIES_LABEL)
        leaf = ('#', self.code)
        return (root, cdslist, cdsid, activities, leaf)


class TeacherListViewHandler(BaseStorageHandler):
    template = "storage_teachers_list.html"

    def __init__(self, **kwargs):
        super(TeacherListViewHandler, self).__init__(**kwargs)

    def as_view(self):

        url_data = {}

        if settings.ALLOWED_TEACHER_ROLES:
            url_data['role'] = ",".join(settings.ALLOWED_TEACHER_ROLES)

        params = urllib.parse.urlencode(url_data)
        self.data['url'] = f'{settings.CMS_STORAGE_TEACHER_API}?{params}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_TEACHERS_LABEL)
        return (root, leaf)


class TeacherInfoViewHandler(BaseStorageHandler):
    template = "storage_teachers_info.html"

    def __init__(self, **kwargs):
        super(TeacherInfoViewHandler, self).__init__(**kwargs)
        self.code = self.match_dict.get('code', '')

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_TEACHER_API}{self.code}/'
        self.data['code'] = self.code
        return super().as_view()

    @property
    def parent_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_THEACHER_VIEW_PREFIX_PATH}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        parent = (self.parent_url, settings.CMS_STORAGE_TEACHERS_LABEL)
        leaf = ('#', self.code)
        return (root, parent, leaf)


class AddressbookListViewHandler(BaseStorageHandler):
    template = "storage_addressbook_list.html"

    def __init__(self, **kwargs):
        super(AddressbookListViewHandler, self).__init__(**kwargs)

    def as_view(self):

        url_data = {}

        if settings.ALLOWED_ADDRESSBOOK_ROLES:
            url_data['role'] = ",".join(settings.ALLOWED_ADDRESSBOOK_ROLES)
        if settings.ALLOWED_ADDRESSBOOK_STRUCTURE_ID:
            url_data['structure'] = ",".join(settings.ALLOWED_ADDRESSBOOK_STRUCTURE_ID)
        if settings.ALLOWED_STRUCTURE_TYPES:
            url_data['structuretypes'] = ",".join(settings.ALLOWED_STRUCTURE_TYPES)

        params = urllib.parse.urlencode(url_data)
        self.data['url'] = f'{settings.CMS_STORAGE_ADDRESSBOOK_API}?{params}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_ADDRESSBOOK_LABEL)
        return (root, leaf)


class AddressbookInfoViewHandler(BaseStorageHandler):
    template = "storage_addressbook_info.html"

    def __init__(self, **kwargs):
        super(AddressbookInfoViewHandler, self).__init__(**kwargs)
        self.code = self.match_dict.get('code', '')

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_ADDRESSBOOK_API}{self.code}/'
        return super().as_view()

    @property
    def parent_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_ADDRESSBOOK_VIEW_PREFIX_PATH}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        parent = (self.parent_url, settings.CMS_STORAGE_ADDRESSBOOK_LABEL)
        leaf = ('#', self.code)
        return (root, parent, leaf)


class StructureListViewHandler(BaseStorageHandler):
    template = "storage_structure_list.html"

    def __init__(self, **kwargs):
        super(StructureListViewHandler, self).__init__(**kwargs)

    def as_view(self):
        url_data = {}

        if settings.INITIAL_STRUCTURE_FATHER != '':
            url_data['father'] = settings.INITIAL_STRUCTURE_FATHER
        if settings.ALLOWED_STRUCTURE_TYPES:
            url_data['type'] = ",".join(settings.ALLOWED_STRUCTURE_TYPES)

        params = urllib.parse.urlencode(url_data)
        self.data['url'] = f'{settings.CMS_STORAGE_STRUCTURE_API}?{params}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_STRUCTURE_LABEL)
        return (root, leaf)


class StructureInfoViewHandler(BaseStorageHandler):
    template = "storage_structure_info.html"

    def __init__(self, **kwargs):
        super(StructureInfoViewHandler, self).__init__(**kwargs)
        self.code = self.match_dict.get('code', '')

    def as_view(self):
        self.data['code'] = self.code
        self.data['url'] = f'{settings.CMS_STORAGE_STRUCTURE_API}{self.code}/'
        return super().as_view()

    @property
    def parent_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_STRUCTURE_VIEW_PREFIX_PATH}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        parent = (self.parent_url, settings.CMS_STORAGE_STRUCTURE_LABEL)
        leaf = ('#', self.code)
        return (root, parent, leaf)


class LaboratoryListViewHandler(BaseStorageHandler):
    template = "storage_laboratory_list.html"

    def __init__(self, **kwargs):
        super(LaboratoryListViewHandler, self).__init__(**kwargs)

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_LABORATORY_API}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_LABORATORY_LABEL)
        return (root, leaf)


class LaboratoryInfoViewHandler(BaseStorageHandler):
    template = "storage_laboratory_info.html"

    def __init__(self, **kwargs):
        super(LaboratoryInfoViewHandler, self).__init__(**kwargs)
        self.code = self.match_dict.get('code', '')

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_LABORATORY_API}{self.code}/'
        return super().as_view()

    @property
    def parent_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_LABORATORY_VIEW_PREFIX_PATH}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        parent = (self.parent_url, settings.CMS_STORAGE_LABORATORY_LABEL)
        leaf = ('#', self.code)
        return (root, parent, leaf)


class ResearchGroupListViewHandler(BaseStorageHandler):
    template = "storage_research_group_list.html"

    def __init__(self, **kwargs):
        super(ResearchGroupListViewHandler, self).__init__(**kwargs)

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_RESEARCH_GROUP_API}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_RESEARCH_GROUP_LABEL)
        return (root, leaf)


class BaseResearchLineListViewHandler(BaseStorageHandler):
    template = "storage_base_research_line_list.html"

    def __init__(self, **kwargs):
        super(BaseResearchLineListViewHandler, self).__init__(**kwargs)

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_BASE_RESEARCH_LINE_API}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_BASE_RESEARCH_LINE_LABEL)
        return (root, leaf)


class AppliedResearchLineListViewHandler(BaseStorageHandler):
    template = "storage_applied_research_line_list.html"

    def __init__(self, **kwargs):
        super(AppliedResearchLineListViewHandler, self).__init__(**kwargs)

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_APPLIED_RESEARCH_LINE_API}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_APPLIED_RESEARCH_LINE_LABEL)
        return (root, leaf)


class PublicationsListViewHandler(BaseStorageHandler):
    template = "storage_publications_list.html"

    def __init__(self, **kwargs):
        super(PublicationsListViewHandler, self).__init__(**kwargs)

    def as_view(self):
        url_data = {}

        params = urllib.parse.urlencode(url_data)
        self.data['url'] = f'{settings.CMS_STORAGE_PUBLICATIONS_API}?{params}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_PUBLICATIONS_LABEL)
        return (root, leaf)


class PublicationsInfoViewHandler(BaseStorageHandler):
    template = "storage_publications_info.html"

    def __init__(self, **kwargs):
        super(PublicationsInfoViewHandler, self).__init__(**kwargs)
        self.code = self.match_dict.get('code', '')

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_PUBLICATIONS_API}{self.code}/'
        return super().as_view()

    @property
    def parent_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_PUBLICATIONS_VIEW_PREFIX_PATH}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        parent = (self.parent_url, settings.CMS_STORAGE_PUBLICATIONS_LABEL)
        leaf = ('#', self.code)
        return (root, parent, leaf)


class PatentsListViewHandler(BaseStorageHandler):
    template = "storage_patents_list.html"

    def __init__(self, **kwargs):
        super(PatentsListViewHandler, self).__init__(**kwargs)

    def as_view(self):
        self.data['url'] = f'{settings.CMS_STORAGE_PATENTS_API}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_PATENTS_LABEL)
        return (root, leaf)


class SpinoffListViewHandler(BaseStorageHandler):
    template = "storage_spinoff_list.html"

    def __init__(self, **kwargs):
        super(SpinoffListViewHandler, self).__init__(**kwargs)

    def as_view(self):
        url_data = {}
        params = urllib.parse.urlencode(url_data)
        self.data['url'] = f'{settings.CMS_STORAGE_SPINOFF_API}?{params}'
        return super().as_view()

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        leaf = ('#', settings.CMS_STORAGE_SPINOFF_LABEL)
        return (root, leaf)


class SpinoffInfoViewHandler(BaseStorageHandler):
    template = "storage_spinoff_info.html"

    def __init__(self, **kwargs):
        super(SpinoffInfoViewHandler, self).__init__(**kwargs)
        self.code = self.match_dict.get('code', '')

    def as_view(self):
        self.data['code'] = self.code
        self.data['url'] = f'{settings.CMS_STORAGE_SPINOFF_API}{self.code}/'
        return super().as_view()

    @property
    def parent_url(self):
        url = f'{self.webpath.get_full_path()}/{settings.CMS_STORAGE_BASE_PATH}/{settings.CMS_STORAGE_SPINOFF_VIEW_PREFIX_PATH}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        root = (self.get_base_url, settings.CMS_STORAGE_ROOT_LABEL)
        parent = (self.parent_url, settings.CMS_STORAGE_SPINOFF_LABEL)
        leaf = ('#', self.code)
        return (root, parent, leaf)
