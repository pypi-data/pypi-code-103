import os
import shutil
import json
import tornado
from urllib.parse import urljoin
from .base_handler import BackendAPIHandler

FILE_NAME = 'Notebook.ipynb'


class CourseBackendHandler(BackendAPIHandler):

    @tornado.web.authenticated
    def get(self, course_id, lesson_id):
        self.finish(json.dumps({
            "data": "Hello endpoint!"
        }))


class PlatformCourseBackendHandler(BackendAPIHandler):
    """
    平台课程
    """

    def __init__(self, application, request) -> None:
        super().__init__(application, request)
        self.work_dir = os.path.abspath(os.path.curdir)
        self.log.info('work_dir: {}'.format(self.work_dir))
        self.workspace = 'course'
        self.log.info('workspace: {}'.format(self.work_dir))
        self.jupyter_lab_base_url = os.environ.get('PI_VRI_DOMAIN', None)
        assert self.jupyter_lab_base_url, '未设置 env "PI_VRI_DOMAIN"'
        self.folder = None
        self.file_path = None

    def feach_data(self, platform_course_id, lesson_id):
        self.log.info('下载 .ipynb 文件...')
        api_url = 'api/course/platform/courses/{platform_course_id}/lessons/{lesson_id}/content?reset'.format(
            platform_course_id=platform_course_id, lesson_id=lesson_id
        )
        res = self.api_request('GET', api_url)
        ipynb_content = res['content']['content']
        self.folder = os.path.join(
            'platform-course', 'course-{}/lesson-{}'.format(platform_course_id, lesson_id))
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder)
        self.file_path = os.path.join(self.folder, FILE_NAME)
        self.abs_file_path = os.path.join(self.work_dir, self.file_path)
        with open(self.abs_file_path, 'w') as f:
            json.dump(json.loads(ipynb_content), f)

        self.log.info('下载 数据集 文件...')

    def get_redirect_url(self):
        redirect_url = urljoin(self.jupyter_lab_base_url, 'lab/workspaces/{workspace}/tree/{file_path}'.format(
            workspace=self.workspace, file_path=self.file_path))
        return redirect_url

    @tornado.web.authenticated
    def get(self, platform_course_id, lesson_id):
        self.feach_data(platform_course_id, lesson_id)
        redirect_url = self.get_redirect_url()
        self.redirect(redirect_url)

    @tornado.web.authenticated
    def post(self, platform_course_id, lesson_id):
        pass
