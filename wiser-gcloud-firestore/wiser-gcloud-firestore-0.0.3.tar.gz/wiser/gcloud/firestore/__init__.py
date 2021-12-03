try:
    import pkg_resources

    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil

    __path__ = pkgutil.extend_path(__path__, __name__)

from wiser.gcloud.firestore.services import Firestore
from wiser.gcloud.firestore.types import (
    FirestoreQuery,
    FirestoreQueryDirection,
    FirestoreQueryCondition,
    FirestoreQueryBuilder,
    FirestoreDocumentBuilder,
    FirestoreDocument,
    FirestoreCollectionBuilder,
    FirestoreCollection,
)

__all__ = [
    "Firestore",
    "FirestoreDocument",
    "FirestoreDocumentBuilder",
    "FirestoreQueryBuilder",
    "FirestoreQueryCondition",
    "FirestoreQueryDirection",
    "FirestoreQuery",
    "FirestoreCollection",
    "FirestoreCollectionBuilder",
]
