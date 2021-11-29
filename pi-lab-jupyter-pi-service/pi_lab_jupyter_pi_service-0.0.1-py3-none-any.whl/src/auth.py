import os
import uuid
from jupyter_server.auth.login import LoginHandler


class PiLabLoginHandler(LoginHandler):
    """Pi Lab login
    """

    def _render(self, message=None):
        ns = dict(
            status_code=500,
            status_message='无效token',
            message='登陆失败',
            exception='登陆失败',
        )
        html = self.render_template('error.html', **ns)
        self.write(html)

    def get(self):
        next_url = self.get_argument('next', default=self.base_url)
        next_url = self.base_url + next_url
        next_url = next_url.replace("//", "/")
        self.log.info('base url: {}'.format(self.base_url))
        self.log.info('next url: {}'.format(next_url))
        if self.current_user:
            # self._redirect_safe(next_url)
            self.log.info('current user jump:{}'.format(next_url))
            self.redirect(next_url)
        else:
            # 获取pi server key
            pi_auth_key_from_url = self.get_argument('token', default='')
            pi_auth_key_from_env = os.environ.get('PI_AUTH_KEY', '')
            self.log.info('pi_auth_key from url: {}'.format(
                pi_auth_key_from_url))
            self.log.info('pi_auth_key from env: {}'.format(
                pi_auth_key_from_env))

            if (not pi_auth_key_from_env) or (pi_auth_key_from_url == pi_auth_key_from_env):
                self.log.info('auth pass')
                self.set_login_cookie(self, uuid.uuid4().hex)
                self.redirect(next_url)

            else:
                # 失败跳转
                # self.log.info('go to render...')
                self._render()
