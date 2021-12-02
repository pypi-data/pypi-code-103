import logging

from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


# list of website pks allowed to display the pages
ALLOWED_UNICMS_SITES = [1]


# base path
CMS_STORAGE_BASE_PATH = 'storage'

CMS_STORAGE_ACTIVITY_VIEW_PREFIX_PATH = 'activities'
CMS_STORAGE_ADDRESSBOOK_VIEW_PREFIX_PATH = 'addressbook'
CMS_STORAGE_APPLIED_RESEARCH_LINE_VIEW_PREFIX_PATH = 'applied-research-lines'
CMS_STORAGE_BASE_RESEARCH_LINE_VIEW_PREFIX_PATH = 'base-research-lines'
CMS_STORAGE_CDS_VIEW_PREFIX_PATH = 'cds'
CMS_STORAGE_LABORATORY_VIEW_PREFIX_PATH = 'laboratories'
CMS_STORAGE_PATENTS_VIEW_PREFIX_PATH = 'patents'
CMS_STORAGE_PUBLICATIONS_VIEW_PREFIX_PATH = 'publications'
CMS_STORAGE_RESEARCH_GROUP_VIEW_PREFIX_PATH = 'research-groups'
CMS_STORAGE_SPINOFF_VIEW_PREFIX_PATH = 'companies'
CMS_STORAGE_STRUCTURE_VIEW_PREFIX_PATH = 'structures'
CMS_STORAGE_THEACHER_VIEW_PREFIX_PATH = 'teachers'


# regexps
CMS_STORAGE_BASE_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})(/)?$' # noqa

CMS_STORAGE_ACTIVITY_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_CDS_VIEW_PREFIX_PATH})/(?P<cdsid>[a-z0-9\-]*)/{CMS_STORAGE_ACTIVITY_VIEW_PREFIX_PATH}/(?P<code>[a-z0-9\-]*)(/)?$' # noqa
CMS_STORAGE_ADDRESSBOOK_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_ADDRESSBOOK_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_ADDRESSBOOK_INFO_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_ADDRESSBOOK_VIEW_PREFIX_PATH})/(?P<code>[a-z0-9\-]*)(/)?$' # noqa
CMS_STORAGE_CDS_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_CDS_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_CDS_INFO_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_CDS_VIEW_PREFIX_PATH})/(?P<code>[a-z0-9\-]*)(/)?$' # noqa
CMS_STORAGE_LABORATORY_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_LABORATORY_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_LABORATORY_INFO_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_LABORATORY_VIEW_PREFIX_PATH})/(?P<code>[a-z0-9\-]*)(/)?$' # noqa
CMS_STORAGE_PATENTS_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_PATENTS_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_PUBLICATIONS_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_PUBLICATIONS_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_PUBLICATIONS_INFO_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/{CMS_STORAGE_PUBLICATIONS_VIEW_PREFIX_PATH}/(?P<code>[a-z0-9\-]*)(/)?$' # noqa
CMS_STORAGE_RESEARCH_GROUP_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_RESEARCH_GROUP_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_BASE_RESEARCH_LINE_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_BASE_RESEARCH_LINE_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_APPLIED_RESEARCH_LINE_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_APPLIED_RESEARCH_LINE_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_SPINOFF_URL_LIST_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_SPINOFF_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_SPINOFF_URL_INFO_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_SPINOFF_VIEW_PREFIX_PATH})/(?P<code>[a-z0-9\-]*)(/)?$' # noqa
CMS_STORAGE_STRUCTURE_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_STRUCTURE_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_STRUCTURE_INFO_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_STRUCTURE_VIEW_PREFIX_PATH})/(?P<code>[a-z0-9\-]*)(/)?$' # noqa
CMS_STORAGE_TEACHER_LIST_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_THEACHER_VIEW_PREFIX_PATH})(/)?$' # noqa
CMS_STORAGE_TEACHER_INFO_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_STORAGE_BASE_PATH})/({CMS_STORAGE_THEACHER_VIEW_PREFIX_PATH})/(?P<code>[a-z0-9\-]*)(/)?$' # noqa


CMS_STORAGE_HANDLERS_PATHS = [
                              CMS_STORAGE_BASE_URL_VIEW_REGEXP,
                              CMS_STORAGE_ACTIVITY_URL_VIEW_REGEXP,
                              CMS_STORAGE_ADDRESSBOOK_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_ADDRESSBOOK_INFO_URL_VIEW_REGEXP,
                              CMS_STORAGE_CDS_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_CDS_INFO_URL_VIEW_REGEXP,
                              CMS_STORAGE_LABORATORY_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_LABORATORY_INFO_URL_VIEW_REGEXP,
                              CMS_STORAGE_PATENTS_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_PUBLICATIONS_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_PUBLICATIONS_INFO_URL_VIEW_REGEXP,
                              CMS_STORAGE_RESEARCH_GROUP_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_BASE_RESEARCH_LINE_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_APPLIED_RESEARCH_LINE_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_SPINOFF_URL_LIST_VIEW_REGEXP,
                              CMS_STORAGE_SPINOFF_URL_INFO_VIEW_REGEXP,
                              CMS_STORAGE_STRUCTURE_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_STRUCTURE_INFO_URL_VIEW_REGEXP,
                              CMS_STORAGE_TEACHER_LIST_URL_VIEW_REGEXP,
                              CMS_STORAGE_TEACHER_INFO_URL_VIEW_REGEXP,
                              ]


CMS_STORAGE_APP_REGEXP_URLPATHS = {
    'unicms_unical_storage_handler.handlers.BaseStorageHandler' : CMS_STORAGE_BASE_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.ActivityViewHandler' : CMS_STORAGE_ACTIVITY_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.AddressbookListViewHandler' : CMS_STORAGE_ADDRESSBOOK_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.AddressbookInfoViewHandler' : CMS_STORAGE_ADDRESSBOOK_INFO_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.CdSListViewHandler' : CMS_STORAGE_CDS_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.CdSInfoViewHandler' : CMS_STORAGE_CDS_INFO_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.LaboratoryListViewHandler': CMS_STORAGE_LABORATORY_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.LaboratoryInfoViewHandler' : CMS_STORAGE_LABORATORY_INFO_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.PatentsListViewHandler' : CMS_STORAGE_PATENTS_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.PublicationsListViewHandler': CMS_STORAGE_PUBLICATIONS_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.PublicationsInfoViewHandler': CMS_STORAGE_PUBLICATIONS_INFO_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.ResearchGroupListViewHandler': CMS_STORAGE_RESEARCH_GROUP_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.BaseResearchLineListViewHandler': CMS_STORAGE_BASE_RESEARCH_LINE_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.AppliedResearchLineListViewHandler': CMS_STORAGE_APPLIED_RESEARCH_LINE_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.SpinoffListViewHandler': CMS_STORAGE_SPINOFF_URL_LIST_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.SpinoffInfoViewHandler' : CMS_STORAGE_SPINOFF_URL_INFO_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.StructureListViewHandler': CMS_STORAGE_STRUCTURE_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.StructureInfoViewHandler' : CMS_STORAGE_STRUCTURE_INFO_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.TeacherListViewHandler' : CMS_STORAGE_TEACHER_LIST_URL_VIEW_REGEXP,
    'unicms_unical_storage_handler.handlers.TeacherInfoViewHandler' : CMS_STORAGE_TEACHER_INFO_URL_VIEW_REGEXP,
}


# cms_storage APIs (ref: https://storage.unical.it)
CMS_STORAGE_BASE_API = 'https://storage.portale.unical.it/api/ricerca/'

CMS_STORAGE_ACADEMICYEARS_API = f'{CMS_STORAGE_BASE_API}academicyears/'
CMS_STORAGE_ACTIVITY_API = f'{CMS_STORAGE_BASE_API}activities/'
CMS_STORAGE_ADDRESSBOOK_API = f'{CMS_STORAGE_BASE_API}addressbook/'
CMS_STORAGE_APPLIED_RESEARCH_LINE_API = f'{CMS_STORAGE_BASE_API}appliedresearchlines/'
CMS_STORAGE_BASE_RESEARCH_LINE_API = f'{CMS_STORAGE_BASE_API}baseresearchlines/'
CMS_STORAGE_CDS_API = f'{CMS_STORAGE_BASE_API}cds/'
CMS_STORAGE_COMMUNITYTYPES_API = f'{CMS_STORAGE_BASE_API}publicationscommunitytypes/'
CMS_STORAGE_DEGREETYPES_API = f'{CMS_STORAGE_BASE_API}degreetypes/'
CMS_STORAGE_DEPARTMENTSFILTER_API = f'{CMS_STORAGE_BASE_API}departmentsfilter/'
CMS_STORAGE_ERC0LIST_API = f'{CMS_STORAGE_BASE_API}erc0list/'
CMS_STORAGE_ERC1LIST_API = f'{CMS_STORAGE_BASE_API}erc1list/'
CMS_STORAGE_INFRASTRUCTURES_API = f'{CMS_STORAGE_BASE_API}infrastructures/'
CMS_STORAGE_LABORATORY_API = f'{CMS_STORAGE_BASE_API}laboratories/'
CMS_STORAGE_LABORATORIES_AREAS_API = f'{CMS_STORAGE_BASE_API}laboratoriesareas/'
CMS_STORAGE_LABORATORIES_SCOPES_API = f'{CMS_STORAGE_BASE_API}laboratories-scopes/'
CMS_STORAGE_PATENTS_API = f'{CMS_STORAGE_BASE_API}patents/'
CMS_STORAGE_PUBLICATIONS_API = f'{CMS_STORAGE_BASE_API}publications/'
CMS_STORAGE_RESEARCH_GROUP_API = f'{CMS_STORAGE_BASE_API}researchgroups/'
CMS_STORAGE_ROLES_API = f'{CMS_STORAGE_BASE_API}roles/'
CMS_STORAGE_SPINOFF_API = f'{CMS_STORAGE_BASE_API}companies/'
CMS_STORAGE_STRUCTURE_API = f'{CMS_STORAGE_BASE_API}structures/'
CMS_STORAGE_STRUCTUREFILTER_API = f'{CMS_STORAGE_BASE_API}structuresfilter/'
CMS_STORAGE_STRUCTUREFUNCTIONS_API = f'{CMS_STORAGE_BASE_API}functions/'
CMS_STORAGE_STRUCTURETYPES_API = f'{CMS_STORAGE_BASE_API}structuretypes/'
CMS_STORAGE_TEACHER_API = f'{CMS_STORAGE_BASE_API}teachers/'
CMS_STORAGE_TECHAREAS_API = f'{CMS_STORAGE_BASE_API}tech-areas/'


# labels (for breadcrumbs and page title)
CMS_STORAGE_ACTIVITIES_LABEL = _("Teachings")
CMS_STORAGE_ADDRESSBOOK_LABEL = _("Persons")
CMS_STORAGE_APPLIED_RESEARCH_LINE_LABEL = _("Applied research lines")
CMS_STORAGE_BASE_RESEARCH_LINE_LABEL = _("Base research lines")
CMS_STORAGE_CDS_LIST_LABEL = _("Study courses")
CMS_STORAGE_LABORATORY_LABEL = _("Laboratories")
CMS_STORAGE_PATENTS_LABEL = _("Patents")
CMS_STORAGE_PUBLICATIONS_LABEL = _("Publications")
CMS_STORAGE_RESEARCH_GROUP_LABEL = _("Research groups")
CMS_STORAGE_ROOT_LABEL = _("Data storage")
CMS_STORAGE_SPINOFF_LABEL = _("Companies")
CMS_STORAGE_STRUCTURE_LABEL = _("Structures")
CMS_STORAGE_TEACHERS_LABEL = _("Teachers")


# API filters
ALLOWED_CDS_COURSETYPES = []
ALLOWED_CDS_LANGUAGES = ['ita', 'eng']
ALLOWED_CDS_JOINT_DEGREES = [
    {'COD': 'N', 'name': _("No")},
    {'COD': 'S', 'name': _("Joint title")},
    {'COD': 'D', 'name': _("Double title")}
]


ALLOWED_ADDRESSBOOK_ROLES = []
ALLOWED_ADDRESSBOOK_STRUCTURE_ID = []
ALLOWED_STRUCTURE_TYPES = []
ALLOWED_TEACHER_ROLES = []


# CDSINFO FIELDS TO SHOW
CDS_INFO_FIELDS = ['CdSGoals', 'CdSAccess', 'CdSAdmission',
                   'CdSProfiles', 'CdSFinalTest', 'CdSFinalTestMode',
                   'CdSSatisfactionSurvey']


# FIELDS TO HIDE IN BLOCKS
ADDRESSBOOK_INFO_NOT_SHOW = ['ID', 'Name', 'Role',
                             'RoleDescription', 'StructureTypeCOD',
                             'TeacherCVFull', 'TeacherCVShort']
TEACHER_INFO_NOT_SHOW = ['TeacherID', 'TeacherDepartmentID',
                         'TeacherLastName', 'TeacherFirstName',
                         'TeacherRole', 'TeacherRoleDescription',
                         'TeacherCVFull']

STRUCTURE_INFO_NOT_SHOW = ['StructureId', 'StructureCod', 'StructureFatherId', 'StructureTypeCOD',
                           'StructurePersonnelFunctions',]

LABORATORY_INFO_NOT_SHOW = ['LaboratoryId', 'CompletionReferentId',
                            'ScientificDirectorId', 'DepartmentReferentId',
                            'LaboratoryErc1Cod', 'LaboratoryErc0Cod',
                            'ResearchPersonnelID', 'TechPersonnelID',
                            'LaboratoryName',
                            'LaboratoryScope', 'LaboratoryLogo',
                            'LaboratoryResearchPersonnel',
                            'LaboratoryTechPersonnel', 'LaboratoryOfferedServices',
                            'LaboratoryServicesScope', 'LaboratoryTeachingScope',
                            'LaboratoryResearchScope', 'LaboratoryActivities',
                            'CompletionReferentName', 'TechPersonnelRole',
                            'ExtraDepartments','LaboratoryEquipment',
                            'Interdepartmental', 'DepartmentReferentCod']

PUBLICATIONS_INFO_NOT_SHOW = ['PublicationId', 'PublicationAbstract',
                              'PublicationTitle', 'PublicationCommunity',
                              'PublicationCollection', 'PublicationReferenceAuthor',
                              'Publication', 'PublicationLabel', 'PublicationUrl']

INITIAL_STRUCTURE_FATHER = ''

SPINOFF_INFO_NOT_SHOW = ['SpinoffId', 'SpinoffImage', 'SpinoffTechAreaId',
                         'IsSpinoff', 'IsStartup', 'SpinoffAgencyName',
                         'SpinoffUnicalReferentId', 'SpinoffDescription']

# ALMALAUREA Link
ALMALAUREA_LINK = 'http://statistiche.almalaurea.it/universita/statistiche/trasparenza?codicione='
