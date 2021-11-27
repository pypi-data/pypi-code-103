import os
import platform


class AppStyle:

    here = os.path.abspath(os.path.dirname(__file__))
    media = os.path.abspath(os.path.join(here, "media"))

    @classmethod
    def html_css(cls) -> str:
        with open(os.path.join(cls.media, "html.css")) as fid:
            return fid.read()

    @classmethod
    def load_stylesheet(cls) -> str:
        media = cls.media.replace("\\", "/")
        if platform.system().lower() == 'win32':
            import win32api
            # noinspection PyProtectedMember
            media = win32api.GetLongPathName(media).replace("\\", "/")
        style_path = os.path.join(media, "app.css").replace("\\", "/")

        with open(style_path) as fid:
            style = fid.read().replace("LOCAL_PATH", media)
            # print(style)

        if platform.system().lower() == 'darwin':  # see issue #12 on github
            mac_fix = '''
            QDockWidget::title
            {
                background-color: #31363b;
                text-align: center;
                height: 12px;
            }
            '''
            style += mac_fix

        return style
