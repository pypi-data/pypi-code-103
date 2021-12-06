from pathlib import Path

import classification_model

PACKAGE_ROOT = Path(classification_model.__file__).resolve()

print(PACKAGE_ROOT)
