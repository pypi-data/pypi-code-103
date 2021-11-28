from pathlib import Path

import regression_model

PACKAGE_ROOT = Path(regression_model.__file__).resolve()

print(PACKAGE_ROOT)
