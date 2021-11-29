# Global variables

# ENVIRONMENT = 'development'
ENVIRONMENT = 'production'

if ENVIRONMENT == 'production':
    HUB_API_ROOT = "https://api.ultralytics.com/"
    REPO_URL = "https://github.com/ultralytics/yolov5.git"
    REPO_BRANCH = "master"
    BY_PASS_LOGIN = False
else:
    HUB_API_ROOT = "http://127.0.0.1:5000/"
    # REPO_URL = "https://github.com/KalenMike/yolov5.git"
    # REPO_BRANCH = "feature/pip-package-clone"
    REPO_URL = "https://github.com/ultralytics/yolov5.git"
    REPO_BRANCH = "master"
    BY_PASS_LOGIN = False
