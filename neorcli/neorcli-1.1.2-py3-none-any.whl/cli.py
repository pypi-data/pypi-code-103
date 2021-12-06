"""
Cli interface to update services

Usage:
    neor-cli.py [options] update <service_id> --tag <tag> [--branch <branch>]
    neor-cli.py [options] update-mass <base_service_id> <services> [<services>...] --tag <tag> [--branch <branch>]

Options:
    -h --help     Show this screen.
    -t --token    Token to use for authentication.
"""
import argparse

from .api import APIClient

parser = argparse.ArgumentParser(description='Neor CLI')
subparsers = parser.add_subparsers(dest='command', help='sub-command help')

parser.add_argument('-t', '--token', help='Token to use for authentication.')

update_parser = subparsers.add_parser('update', help='Update a service')

update_parser.add_argument('service_id', help='Service ID to update')
update_parser.add_argument('--tag', help='Tag to update')
update_parser.add_argument('--branch', help='Branch to update. use tag if no branch is selected', required=False)

mass_update_parser = subparsers.add_parser('update-mass', help='Update a mass of services')

mass_update_parser.add_argument('base_service_id', help='Service to use as base for mass update')
mass_update_parser.add_argument('services', nargs='+', help='Services to update')
mass_update_parser.add_argument('--tag', help='Tag to update')
mass_update_parser.add_argument('--branch', help='Branch to update. use tag if no branch is selected', required=False)

token = None
client = APIClient(token)


def handle_update(args):
    service = client.fetch_service(args.service_id)
    image = client.fetch_image(service['image_id'])
    image_id = client.create_image(args.tag, image, branch=args.branch or args.tag)['id']
    client.patch_service(args.service_id, image_id)
    client.create_pipeline(service['project_id'], [args.service_id], [image_id])
    print(f"{service['name']} service begins to update")


def handle_mass_update(args):
    base_service = client.fetch_service(args.base_service_id)
    base_image = client.fetch_image(base_service['image_id'])
    new_base_image_id = client.create_image(args.tag, base_image, branch=args.branch or args.tag)['id']
    client.patch_service(args.base_service_id, new_base_image_id)
    services = [
        base_service['id']
    ]
    images = []
    for service_id in args.services:
        service = client.fetch_service(service_id)
        image = client.fetch_image(service['image_id'])
        if image['id'] == base_image['id']:
            new_image_id = new_base_image_id
        else:
            new_image_id = client.create_image(
                args.tag,
                image,
                base_image_id=new_base_image_id,
                branch=args.branch or args.tag
            )['id']
            images.append(new_image_id)
        client.patch_service(service_id, new_image_id)
        services.append(service_id)
    client.create_pipeline(base_service['project_id'], services, images, base_image_id=new_base_image_id)
    print(f"{len(services)} services begins to update")


handlers = {
    'update': handle_update,
    'update-mass': handle_mass_update
}


def main():
    args = parser.parse_args()

    global token
    token = args.token

    global client
    client = APIClient(token)

    if args.token is None:
        print('You must provide a token')
        return

    handlers[args.command](args)


if __name__ == '__main__':
    main()
