class Verdict:
    def __init__(self, short_name, name, return_code):
        self.short_name = short_name
        self.name = name
        self.return_code = return_code
    def to_string(self):
        return self.short_name + ': ' + self.name

Correct = Verdict('AC', 'All Correct', 0)
WrongAnswer = Verdict('WA', 'Wrong Answer', 1)
PresentationError = Verdict('PE', 'PresentationError', 2)

class Response:
    def __init__(self, verdict, message=''):
        self.verdict = verdict
        self.message = message
    def to_string(self):
        ret = self.verdict.to_string()
        if self.message != '':
            ret = ret + '\n' + self.message
        return ret
