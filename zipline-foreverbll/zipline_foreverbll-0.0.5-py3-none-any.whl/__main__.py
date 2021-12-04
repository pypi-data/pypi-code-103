import argparse
import os
import signal
import socket
import sys
import time

import foreverbull_core.logger
from foreverbull_core.broker import Broker
from foreverbull_core.models.service import Instance

from app.app import Application

parser = argparse.ArgumentParser(prog="zipline-foreverbull")
parser.add_argument("--broker-url", help="URL of broker")
parser.add_argument("--local-host", help="Local Address")
parser.add_argument("--service-id", help="Service ID")
parser.add_argument("--instance-id", help="Instance ID")


def get_broker(args: argparse.Namespace) -> Broker:
    if args.broker_url:
        broker_url = args.broker_url
    else:
        broker_url = os.environ.get("BROKER_URL", "127.0.0.1:8080")
    if args.local_host:
        local_host = args.local_host
    else:
        local_host = os.environ.get("LOCAL_HOST", socket.gethostbyname(socket.gethostname()))

    return Broker(broker_url, local_host)


def get_service_id(args: argparse.Namespace) -> str:
    if args.service_id:
        service_id = args.service_id
    else:
        service_id = os.environ.get("SERVICE_ID")
        if service_id is None:
            raise SystemExit("missing service-id")
    return service_id


def get_instance_id(args: argparse.Namespace) -> str:
    if args.instance_id:
        instance_id = args.instance_id
    else:
        instance_id = os.environ.get("INSTANCE_ID")
        if instance_id is None:
            raise SystemExit("missing instance-id")
    return instance_id


def run_application(application: Application):
    application.broker.mark_as_online()
    application.start()
    try:
        while application.running:
            time.sleep(1)
    except KeyboardInterrupt:
        application.stop()
    application.broker.mark_as_offline()
    application.join()


def parse_args_and_get_instance_broker(*input_args):
    args = parser.parse_args(*input_args)
    broker = get_broker(args)
    service_id = get_service_id(args)
    instance_id = get_instance_id(args)
    instance = Instance(
        id=instance_id,
        service_id=service_id,
        host=broker.socket_config.host,
        port=broker.socket_config.port,
        listen=True,
        online=True,
    )
    return instance, broker


if __name__ == "__main__":
    foreverbull_core.logger.Logger().configure()
    instance, broker = parse_args_and_get_instance_broker(sys.argv[1:])
    application = Application(broker)
    application.broker.http.service.update_instance(instance)
    signal.signal(signal.SIGTERM, application.stop)
    run_application(application)
    instance.online = False
    instance.listen = False
    application.broker.http.service.update_instance(instance)
