import requests
import json
from collections import defaultdict

class Gerrit:

    def __init__(self, base_url, project_name, branch='master'):
        self.base_url = base_url
        self.project_name = project_name
        self.branch = branch
        self.use_auth = False

    def with_auth(self, username, http_password):
        """
        On how to create the http_password:
        https://stackoverflow.com/questions/35361276/gerrit-authentication-required
        or the README.md
        """
        self.username = username
        self.password = http_password
        self.use_auth = True
        return self

    ###

    def fetch_change(self, change_id):
        path = f'/a/changes/{self.project_name}~{self.branch}~{change_id}/'
        return self._get(path)

    def create_comments(self, change_id,  file, line_range, comment, revision_id='current'):
        '''
        line_range is a tuble with (start, end)
        '''

        if isinstance(line_range, int):
            start_line = line_range
            end_line = line_range
        else:
            start_line = line_range[0]
            end_line = line_range[1]

        path = f'/a/changes/{self.project_name}~{self.branch}~{change_id}/revisions/{revision_id}/drafts'
        return self._put(path, params={
            'path': file,
            # line: 2
            'range': {
                'start_line': start_line,
                'end_line': end_line,
                # start_character,
                # end_character
            },
            'message': comment,
            'unresolved': True
        })

    def send_review(self, change_id, review, revision_id='current'):
        path = f'/a/changes/{change_id}/revisions/{revision_id}/review'
        params = {
            'tag': 'jenkins',
            'message': review.message,
            'labels': {
                'Code-Review': review.rating
            },
            'comments': review.comments
        }
        return self._post(path, params)

    ###

    def _post(self, path, params):
        url = self.base_url + path
        res = requests.post(
            url=url,
            json=params,
            auth=(self.username, self.password) if self.use_auth else None,
            headers={'Accept': 'application/json'}
        )
        res = res.content.decode()
        # see https://gerrit-review.googlesource.com/Documentation/rest-api.html#output
        XSSI_prefix = ")]}'\n"
        res = res[len(XSSI_prefix):]
        res = json.loads(res)
        return res

    def _put(self, path, params):
        url = self.base_url + path
        res = requests.put(
            url=url,
            json=params,
            auth=(self.username, self.password) if self.use_auth else None,
            headers={'Accept': 'application/json'}
        )
        res = res.content.decode()
        # see https://gerrit-review.googlesource.com/Documentation/rest-api.html#output
        XSSI_prefix = ")]}'\n"
        res = res[len(XSSI_prefix):]
        res = json.loads(res)
        return res

    def _get(self, path):
        url = self.base_url + path
        res = requests.get(
            url=url,
            auth=(self.username, self.password) if self.use_auth else None,
            headers={'Accept': 'application/json'},
        )
        res = res.content.decode()
        # see https://gerrit-review.googlesource.com/Documentation/rest-api.html#output
        XSSI_prefix = ")]}'\n"
        res = res[len(XSSI_prefix):]
        res = json.loads(res)
        return res


class Review:

    def __init__(self, message=''):
        self.message = message
        self.rating = -1
        self._comments = defaultdict(list)

    def comment(self, file, line_range, message):
        '''
        line_range is a tuble with (start, end)
        '''
        if isinstance(line_range, int):
            start_line = line_range
            end_line = line_range
        else:
            start_line = line_range[0]
            end_line = line_range[1]

        self._comments[file].append({
            'message': message,
            'range': {
                'start_line': start_line,
                'end_line': end_line,
                # 'start_character': 0,
                # 'end_character': 20
            },
            'unresolved': True
        })

    @property
    def comments(self):
        return dict(self._comments)