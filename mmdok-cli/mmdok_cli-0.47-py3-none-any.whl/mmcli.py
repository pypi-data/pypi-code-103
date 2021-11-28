import cmd2, getpass, json, os, pprint
from mmcli.helper import help
from mmcli.mmclient import MMClient

mmclient = MMClient('https://v84wxfpyu8.execute-api.eu-north-1.amazonaws.com/prod')

class MMCli(cmd2.Cmd):
    def do_server(self, line):
        server = input('Server:')
        mmclient.set_server(server)

    def do_register(self, line):
        email = input('   Email:')
        password = getpass.getpass('Password:')
        hasGroup = None
        while hasGroup!='Y' and hasGroup!='N':
            hasGroup = input('Belong to a group[Y|N]:')
        success = mmclient.register(email, password, hasGroup=='Y')
        if success: print('Registration succeded. An email will be sent to you for confirmation.')
        else: print('Registration failed')
        
    def do_login(self, line):
        email = input('   Email:')
        password = getpass.getpass('Password:')
        success = mmclient.login(email, password)
        if success: print('Login succeded')
        else: print('Login failed')

    def do_reset_password(self, line):
        email = input('   Email:')
        success = mmclient.forgot_password(email)
        if not success:
            print('Failed to signal forgotten password')
            return
        password = getpass.getpass('Password:')
        code = input('Code:')
        success = mmclient.reset_password(email, password, code)
        if success: print('Password reset')
        else: print('Failed to reset password')

    def do_search(self, line):
        filter = input('Filter: ')
        sort = input('Sort: ')
        fr = input('From: ')
        to = input('Number: ')
        range = {}
        if fr.isnumeric() and to.isnumeric() and to>fr: 
            range = '{"from":' + fr + ', "to":' + to + '}'
        #filter = '{"doctype":"kunddokument", "kundnummer":"AAA"}'
        #sort = '{"kundnummer":1}'
        #range = '{"from":0, "to":3}'
        r = mmclient.search(filter, sort, range) #{"doctype":"kunddokument", "kundnummer":"AAA141414"}
        pprint.pprint(r.json())

    def do_count(self, line):
        r = mmclient.count()
        pprint.pprint(r.json())
    
    def do_types(self, line):
        response = mmclient.types()
        pprint.pprint(response.json())

    def do_upload(self, line):
        print('Provide a document id if it is a new version, leave empty for new document')
        id = input('Docid: ')
        doctype = input('Välj dokumenttyp: ')
        data = {}
        metadata = input('Metadata: ')
        path = input('Path to files: ').strip()
        data['metadata'] = metadata
        data['filename'] = os.path.basename(path)
        data['mimetype'] = 'application/pdf'
        data['doctype'] = doctype
        print(data)
        isOk, r = mmclient.upload(data, path, id)    
        print(isOk)
        print(r) 

    """
    curl -H "Content-Type: application/json" -d '{"directory":"/data/docs","doctype":"Faktura",
    "documents":[{"file":"dummy.pdf","metadata":{"Fakturanr":"123456"}}]}' 
    http://localhost:3001/documents
    """
    def do_batch(self, line):
        documents = []
        doctype = input('Document type: ')
        directory = input('Source folder: ').strip()
        print('Insert the documents, finish with an empty file name: ')
        while True:
            filename = input('Filename: ')
            if not filename: break
            metadata = input('Metadata: ')
            documents.append({"file":filename, "metadata":json.dumps(metadata)})
        o = {"doctype":doctype, "directory":directory, "documents":documents}
        s = json.dumps(o)
        print(s)

    def do_view(self, line):
        id = input('Documentid: ')
        isOk, r = mmclient.view(id)
        if not isOk: print(r)

    def do_download(self, line):
        id = input('Documentid: ')
        path = input('Path: ')
        isOk, r = mmclient.download(id, path)
        if not isOk: print(r)

    def do_metadata(self, line):
        id = input('Documentid: ')
        isOk, r = mmclient.metadata(id)
        if not isOk: print(r)

    def do_audit(self, line):
        id = input('Documentid: ')
        isOk, r = mmclient.audit(id)
        if not isOk: print(r)

    def do_update(self, line):
        id = input('Documentid: ')
        metadata = input('Metadata: ')
        rsp = mmclient.update(id, metadata)
        print(rsp.content)

    def do_delete(self, line):
        id = input('Documentid: ')
        rsp = mmclient.delete(id)
        print(rsp.content)  

    def do_help(self, line):
        help(line)

    def do_quit(self, line):
        return True

def run():
    MMCli().cmdloop()

if __name__ == '__main__':
    MMCli(persistent_history_file="~/.mmcli_history").cmdloop()
