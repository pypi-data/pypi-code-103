from docutils import nodes


def element_path(pathstr):
    return [c.strip() for c in pathstr.split('.')]

def list_of_elementpath(pathliststr):
    paths = [p.strip() for p in pathliststr.split(',')]
    return [element_path(p) for p in  paths]

def list_of_person_and_share(persons_and_their_shares):
    '''Breaks "group.person_a:70, group.person_b:10" into [(["group", "person_a"], 70), (["group", "person_b"], 70)]
    '''
    ret = []
    for person_and_share in persons_and_their_shares.split(','):
        person_path, sharestr = person_and_share.split(':')
        ret.append((element_path(person_path), int(sharestr)))
    return ret

def get_document_title(docname, doctree):
    for section in doctree.traverse(nodes.section):
        break
    else:
        raise Exception(f'{docname}: no <section> found')
    for title in section.traverse(nodes.title):
        return title.astext()
    else:
        raise Exception(f'{docname}: first <section> has no <title>')

def make_reference(text, from_docname, to_docname, app):
    ref = nodes.reference()
    ref['refuri'] = app.builder.get_relative_uri(from_=from_docname, to=to_docname)
    ref += nodes.Text(text)
    return ref
