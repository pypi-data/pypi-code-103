from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join
from .course_handler import CourseBackendHandler, PlatformCourseBackendHandler


def setup_handlers(server_app: ServerApp):
    base_url = server_app.web_app.settings['base_url']

    handlers = [
        # 平台内容创建
        # (url_path_join(base_url, '/say_hi'), CourseBackendHandler),

        # 平台内存创建者创建课程说明
        (url_path_join(base_url, '/say_hi'), CourseBackendHandler),

        # 普通用户学习课程
        (url_path_join(base_url, '/platform-course/(?P<platform_course_id>\w+)/view/(?P<lesson_id>\w+)'),
         PlatformCourseBackendHandler),
    ]
    server_app.web_app.add_handlers('.*$', handlers)
