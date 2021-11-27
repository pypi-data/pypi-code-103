from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json

def print_structure(node, num_space=0):
    if not node['isFolder']:
        print('{} {} ({})'.format('-'*num_space, node['title'], node['id']))
    else:
        print('-'*num_space, node['title'])
    if node['children']:
        children = node['children']
        sort_keys = sorted(children.keys())
        for key in sort_keys:
            print_structure(children[key], num_space+1)

def paths_to_ids(node, parent_path=''):
    path = '{}/{}'.format(parent_path, node['title'])
    if not node['title']: # empty title indicates root
        path = ''
    if node['children']:
        children = node['children']
        sort_keys = sorted(children.keys())
        all_values = []
        for key in sort_keys:
            child = children[key]
            struct = paths_to_ids(child, path)
            all_values.extend(struct)
        return all_values
    elif not node['isFolder']:
        return [(path, node['id'])]
    else:
        return []

def paths_id_map_json(path_id_list):
    d = dict(path_id_list)
    return json.dumps(d, indent=4, sort_keys=True)

def main():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

    drive = GoogleDrive(gauth)
    file_list = drive.ListFile().GetList()

    all_files = [ (x['title'], 
                   x['id'],
                   x['parents'][0]['id'], 
                   x['parents'][0]['isRoot'], 
                   x['mimeType']=='application/vnd.google-apps.folder') 
                  for x in file_list]
    folders = [x for x in all_files if x[4]]
    root_id = [f for f in folders if f[3]][0][2]
    tmp = {'title': '', 'id': root_id, 'isFolder': True, 'children': {}}
    folder_structure = {'' : tmp}
    id2container = {root_id: tmp}

    for title, ident, parent_id, isRoot, isFolder in all_files:
        tmp = {'title': title, 'id': ident, 'isFolder': isFolder, 'children': {}}
        id2container[ident] = tmp

    for title, ident, parent_id, isRoot, isFolder in all_files:
        id2container[parent_id]['children'][title] = id2container[ident]

    pids = paths_to_ids(folder_structure[''])

    print("Drive structure:")
    print_structure(folder_structure[''])

    with open('drivepaths.json', 'w') as f:
        f.write(paths_id_map_json(pids))
    print("Generated drivepaths.json file to the current working directory.")

if __name__ == '__main__':
    main()
