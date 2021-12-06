import os
import uuid
from urllib.parse import urljoin
from jupyter_server.auth.login import LoginHandler


class PiLabLoginHandler(LoginHandler):
    """Pi Lab login
    """

    def _render(self, message=None):
        ns = dict(
            status_code=401,
            status_message='认证失败',
            message='登陆失败, 请检查token 是否为正确的 auth_key',
            exception='登陆失败',
        )
        html = self.render_template('error.html', **ns)
        self.write(html)

    def get(self):
        next_url = self.get_argument('next', default=self.base_url)
        next_url = urljoin(self.base_url, next_url)
        next_url = next_url.replace("//", "/")
        # self.log.info('base url: {}'.format(self.base_url))
        # self.log.info('next url: {}'.format(next_url))
        if self.current_user:
            # self._redirect_safe(next_url)
            self.log.info('已认证')
            self.log.info('next: {}'.format(next_url))
            self.redirect(next_url)
        else:
            # 获取pi server key
            pi_auth_key_from_url = self.get_argument('token', default='')
            pi_auth_key_from_env = os.environ.get('PI_AUTH_KEY', '')
            self.log.info('pi_auth_key from env: {}'.format(
                pi_auth_key_from_env))
            if (not pi_auth_key_from_env) or (pi_auth_key_from_url == pi_auth_key_from_env):
                self.log.info('认证通过')
                self.log.info('next: {}'.format(next_url))
                self.set_login_cookie(self, uuid.uuid4().hex)
                self.redirect(next_url)

            else:
                self.log.info('认证失败')
                self._render()
