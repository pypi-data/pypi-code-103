"""GraphQL queries as strings

"""

from .fragments import (  # noqa: F401
    FRAGMENT_LOG,
    FRAGMENT_LOG_CONNECTION,
)

from .queries import (  # noqa: F401
    QUERY_ALL_LOGS,
    QUERY_LOG,
)

from .mutations import (  # noqa: F401
    MUTATION_CREATE_LOG,
    MUTATION_DELETE_LOG,
)
