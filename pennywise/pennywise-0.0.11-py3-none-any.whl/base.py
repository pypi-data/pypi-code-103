import os
import docker


class Tool:

    def __init__(self, image, prefix_cmd):
        self.image = image
        self.prefix_cmd = prefix_cmd

        self.client = docker.from_env()
        self.new_cmd = []
        self.volumes = None
        self.container = None

    def run(self, cmd, current_dir):
        self.build_cmd(cmd)
        self.build_volumes(current_dir)
        self.run_container()
        self.patch_logs(current_dir)

    def build_cmd(self, cmd):
        for i in cmd:
            if i.startswith("/"):
                self.new_cmd.append("/host" + os.path.abspath(i))
            elif i.startswith("./"):
                self.new_cmd.append("/host" + os.path.abspath(i))
            elif i.startswith("../"):
                self.new_cmd.append("/host" + os.path.abspath(i))
            else:
                self.new_cmd.append(i)

    def build_volumes(self, current_dir):
        self.volumes = {
            '/': {'bind': '/host', 'mode': 'rw'},
            current_dir: {'bind': '/data', 'mode': 'rw'},
        }

    def run_container(self):
        try:
            self.client.images.get(self.image)
        except docker.errors.ImageNotFound:
            print(f"- It looks like it's your first time running this command!")
            print(f"- pennywise will download the image ({self.image}) so it can shapeshift")
            print(f"- This can take some time...")
            self.client.images.pull(self.image)

        new_cmd = ' '.join(self.new_cmd)
        self.container = self.client.containers.run(
            self.image,
            f"{self.prefix_cmd} {new_cmd}",
            detach=True,
            volumes=self.volumes,
            user="1000:1000"
        )

    def patch_logs(self, current_dir):
        for line in self.container.logs(stream=True):
            line = line.strip().decode()
            # line = line.replace("/data", current_dir)
            # line = line.replace("/host", "")
            print(line)
