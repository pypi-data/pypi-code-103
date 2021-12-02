import skitai

class TestUtils:
    def test_client (self, point = "/", approot = ".", numthreads = 1):
        # 2021. 4. 16
        # removed officially, this is used by only unittest
        from skitai.testutil import offline
        from skitai.testutil.offline import client
        app = self

        class Client (client.Client):
            def make_request (self, *args, **karg):
                request = client.Client.make_request (self, *args, **karg)
                return self.handle_request (request)

            def __enter__ (self):
                app.life_cycle ('before_mount', wasc)
                app.life_cycle ('mounted', wasc ())
                return self

            def __exit__ (self, type, value, tb):
                app.life_cycle ('before_umount', wasc ())
                app.life_cycle ('umounted', wasc)

        wasc = offline.activate ()
        offline.install_vhost_handler ()
        offline.mount (point, (app, approot))
        return Client ()

    def run (self, address = '127.0.0.1', port = 5000, mount = '/', pref = None):
        skitai.mount (mount, self, pref)
        skitai.run (address = address, port = port)
