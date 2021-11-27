import tarfile
import uuid
import docker


def extract_result_from_container_into_host(container_id, dst):
    client = docker.from_env()
    tmp_uuid = uuid.uuid4()

    container = client.containers.get(container_id)

    f = open(f'/tmp/{tmp_uuid}.tar', 'wb')
    bits, stat = container.get_archive('/data')
    print(stat)
    for chunk in bits:
        f.write(chunk)
    f.close()

    def members(tf):
        l = len("data/")
        for member in tf.getmembers():
            if member.path.startswith("data/"):
                member.path = member.path[l:]
                yield member

    with tarfile.open(f"/tmp/{tmp_uuid}.tar") as tar:
        tar.extractall(members=members(tar), path=dst)
