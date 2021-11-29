TR_PREFIX = '@C'
SECTIONS_SEPARATOR = ' - '
MAIN_CASE_TEMPLATE_NAME = 'Test Case (Steps)'

SKIP_FIELDS = [
    'custom_ui_type',
    'custom_platform'
]
PRIORITY_REPLACE = {
    'Critical': ['regression'],
    'High': ['sanity'],
    'Medium': ['smoke'],
    'Low': []
}

REPLACE_TAGS = {
    'to be automated': 'to_automate',
    'productivity': 'tablet',
    'mobile': 'phone'
}

# ------Validate features--------

VALIDATE_FEATURES = True
NO_TAG_IN_FEATURE_HEADER = True
ONE_OF_TAGS = [
    ['@to_automate', '@automated', '@manual'],
    ['@smoke', '@critical', '@regression']
]
AT_LEAST_ONE = [
    ['@phone', '@tablet']
]
