import asyncio
import base64
import importlib.machinery
import os
import pint
import random
import sys
import tempfile
import uuid
import xlsxwriter
from bs4 import BeautifulSoup
from cefpython3 import cefpython as cef
from pyppeteer import launch

def __generate_choices_html(prob, choices):
    '''Generate HTML of choices'''
    
    choice_format = None
    if choices and 'choices' in choices:
        if 'choice_format' in choices:
            choice_format = choices['choice_format']
        choices = choices['choices']
    else:
        choices = None
    
    html = ''    
    if choices:
        ans = get_answers(prob)
        if type(ans) != list:
            ans = [ans]
        html = '<ol type="A">\n'
        for choice in choices:
            if choice in ans:
                html += '<li class="answer">'
            else:
                html += '<li>'
            html += '<span>'
            if choice_format:
                if hasattr(ans[0], 'magnitude'):
                    _ = choice_format.format(choice.magnitude)
                    _ += '{:~L}'.format(choice.units)
                    html += '$ ' + _ + ' $'
                else:
                    html += choice_format.format(choice)
            else:
                html += choice
            html += '<span></li>\n'
        html += '</ol>'
    return html

def __generate_problem_div(soup, prob_state_html, choices_html):
    '''Generate BeautifulSoup div tag object for problem'''
    
    div = soup.new_tag('div')
    div['class'] = 'problem'
    div.append(BeautifulSoup(prob_state_html + '<br>' + choices_html,
                             'html.parser'))
    return div

def __generate_problem_statement_html(prob, PROBLEM):
    '''Generate HTML of problem statement'''
    
    html = PROBLEM.__doc__
    givens = get_givens(prob)
    if givens:
        html = html.format(**givens)
    return html

def __generate_assessment_soup(ind, PROBLEM, CHOICES, template, css,
                               highlight_answers):
    '''Generate BeautifulSoup object for assessment'''
    
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), template)).read(), 'html.parser')
    
    link = soup.new_tag('link')
    link['rel'] = 'stylesheet'
    link['href'] = 'teepy.css'
    soup.html.head.insert(1, link)
    
    if css is not None:
        link = soup.new_tag('link')
        link['rel'] = 'stylesheet'
        link['href'] = css
        soup.html.head.insert(2, link)
    
    if highlight_answers:
        style = soup.new_tag('style')
        style.string = 'li.answer > span {background-color: #D9EAD3;}'
        soup.html.head.append(style)
    
    main = soup.find(id = 'main')

    prob = PROBLEM(ind)
    choices = CHOICES(ind)
    prob_state_html = __generate_problem_statement_html(prob, PROBLEM)
    choices_html = __generate_choices_html(prob, choices)
        
    div = __generate_problem_div(soup, prob_state_html, choices_html)
    main.append(div)
    
    for image in soup.findAll('img'):
        image['src'] = os.path.abspath(image['src'])
    
    return soup

def display(ind, PROBLEM, CHOICES, template = 'teepy.html',
            css = None, highlight_answers = True, print_HTML = False):
    '''Display rendered PROBLEM function with CHOICES'''
    
    soup = __generate_assessment_soup(ind, PROBLEM, CHOICES, template, css,
                                      highlight_answers)
    
    html = soup.prettify()
    
    if print_HTML:
        print(html)
    
    temp = tempfile.NamedTemporaryFile(prefix = 'teepy_',
                                       suffix = '.html',
                                       mode = 'w',
                                       encoding = 'utf-8')
    temp.write(html)
    temp.seek(0)
    temp_filename = temp.name.replace(os.sep, '/')
    
    settings = {'cache_path': tempfile.gettempdir(),
                'remote_debugging_port': -1} # disables "DevTools listening ..." message
    sys.excepthook = cef.ExceptHook
    cef.Initialize(settings = settings)
    cef.CreateBrowserSync(url = 'file:///' + temp_filename,
                          window_title = 'TEEPY - Tech Engineering Exam in Python')
    cef.MessageLoop()
    cef.Shutdown()
    temp.close()


def generate_choices(N, ans, step, min_val = None, max_val = None):
    '''Generate N numeric choices given answers ans, and step size
step.

min_val and max_val not yet implemented.
'''
    
    if type(ans) != list:
        ans = [ans]
    correct_ind = random.randint(0, N - 1)
    choices = []
    if hasattr(ans[0], 'magnitude'):
        ureg = pint.UnitRegistry()
        Q_ = ureg.Quantity
        for i in range(0, N):
            choices.append(Q_(ans[0].magnitude - (N - i)*step, ans[0].units))
        choices.append(ans[0])
        for i in range(1, N + 1):
            choices.append(Q_(ans[0].magnitude + i*step, ans[0].units))
    else:
        for i in range(0, N):
            choices.append(ans[0] - (N - i)*step)
        choices.append(ans[0])
        for i in range(1, N + 1):
            choices.append(ans[0] + i*step)
    
    choices = choices[N - correct_ind:-correct_ind - 1]
    return choices

def get_answers(prob):
    '''Get answer(s) of PROBLEM function'''
    
    ans = None
    if prob:
        ans = prob['answer']
        if type(ans) != list:
            ans = [ans]
    return ans

def get_givens(prob):
    '''Get given of PROBLEM function'''
    
    givens = None
    if prob and 'given' in prob:
        givens = prob['given']
    return givens







class begin:
    '''The begin class for TEEPy.

    The main entry point for the TEEPy library. It is the class that
    provides all the available methods to interactive with TEEPy when
    acting as the assessment creator.'''
    
    def __init__(self, n_forms = 1, n_inds = 1,
                 template = 'teepy.html', css = None):
        self.css = css
        self.cwd = os.path.dirname(__file__)
        self.key = []
        self.keys = []
        self.pts_correct = []
        self.pts_corrects = []
        self.pts_incorrect = []
        self.pts_incorrects = []
        self.n_forms = n_forms
        self.n_inds = n_inds
        self.refid = []
        self.refids = []
        self.stack = []
        self.template = os.path.join(self.cwd, template)
        
    class define_section:
        def __init__(self, shuffle = False):
            self.stack = []
            self.shuffle = shuffle
        
        def HTML(self, HTML):
            structure = {'type': 'HTML', 'HTML': HTML}
            self.ac_stack.append(structure)

        def problem(self, filename, pts_correct, pts_incorrect = -0, min_height = None):
            structure = {'type': 'problem',
                         'filename': filename,
                         'pts_correct': pts_correct,
                         'pts_incorrect': pts_incorrect,
                         'min_height': min_height,
                         'uuid': str(uuid.uuid4())}
            self.stack.append(structure)

        def new_page(self):
            HTML_str = '<div class="page_break">&nbsp;</div>'
            self.HTML(HTML_str)
        
        def section(self, section):
            self.stack.append({'type': 'section',
                               'stack': getattr(section, 'stack'),
                               'shuffle': getattr(section, 'shuffle')})
    
    def HTML(self, HTML):
        structure = {'type': 'HTML', 'HTML': HTML}
        self.stack.append(structure)
    
    def form_number(self):
        return '{unique_form_number_goes_here}'
    
    def problem(self, filename, pts_correct, pts_incorrect = 0, min_height = None):
        structure = {'type': 'problem',
                     'filename': filename,
                     'pts_correct': pts_correct,
                     'pts_incorrect': pts_incorrect,
                     'min_height': min_height,
                     'uuid': str(uuid.uuid4())}
        self.stack.append(structure)

    def new_page(self):
        HTML_str = '<div class="page_break">&nbsp;</div>'
        self.HTML(HTML_str)
        
    def section(self, section):
        self.stack.append({'type': 'section',
                           'stack': getattr(section, 'stack'),
                           'shuffle': getattr(section, 'shuffle')})
    
    
    
    
    
    def __generate_problem_statement_html(self, prob, PROBLEM):
        '''Generate HTML of problem statement'''
        
        html = PROBLEM.__doc__
        givens = get_givens(prob)
        if givens:
            html = html.format(**givens)
        return html
    
    def __generate_choices_html(self, prob, choices):
        '''Generate HTML of choices'''
        
        choice_format = None
        if choices and 'choices' in choices:
            if 'choice_format' in choices:
                choice_format = choices['choice_format']
            choices = choices['choices']
        else:
            choices = None
        
        html = ''    
        if choices:
            ans = get_answers(prob)
            if type(ans) != list:
                ans = [ans]
            html = '<ol type="A">\n'
            for choice in choices:
                if choice in ans:
                    html += '<li class="answer">'
                else:
                    html += '<li>'
                html += '<span>'
                if choice_format:
                    if hasattr(ans[0], 'magnitude'):
                        _ = choice_format.format(choice.magnitude)
                        _ += '{:~L}'.format(choice.units)
                        html += '$ ' + _ + ' $'
                    else:
                        html += choice_format.format(choice)
                else:
                    html += choice
                html += '<span></li>\n'
            html += '</ol>'
        return html
        
    
    def __generate_problem_data(self, filename, uuid, ind):
        
        filename, fileext = os.path.splitext(filename)
        m = importlib.machinery.SourceFileLoader('mymodule', filename + '.py').load_module()

        qid = self.uuids.index(uuid)
        
        prob = m.PROBLEM(ind)
        choices = m.CHOICES(ind)
        
        ans = get_answers(prob)
        answer_letters = []
        if choices and 'choices' in choices:
            for ic, c in enumerate(choices['choices']):
                if c in ans:
                    answer_letters.append(chr(ord('@') + ic + 1))
            answer_letters.sort()
        
        problem_statement_html = self.__generate_problem_statement_html(prob, m.PROBLEM)
        choices_html = self.__generate_choices_html(prob, choices)
        
        html = problem_statement_html + '<br>' + choices_html
        
        return {'html': html,
                'answer_letters': '|'.join(answer_letters),
                'refid': '|'.join([str(ind + 1), str(qid + 1)])}
    
    def __flatten_stack(self, stack):
        for s in stack:
            if s['type'] == 'section':
                self.__flatten_stack(s['stack'])
            else:
                self.flat_stack.append(s)

    def __html_to_pdf(self, html, filename):
        async def main():
            browser = await launch()
            page = await browser.newPage()
            await page.setContent(html)
            try:
                await page.waitForSelector('#MathJax-Element-1-Frame')
                await page.waitFor(100)
            except:
                pass
            await page.pdf(path = filename, margin = {'top': '0.5in',
                                                      'right': '0.5in',
                                                      'bottom': '0.5in',
                                                      'left': '0.5in'})
            await browser.close()

        asyncio.get_event_loop().run_until_complete(main())

    def __process_section(self, stack, html = '', ind = None, pid = None):
        section_soup = BeautifulSoup('', 'html.parser')
        
        for s in stack:
            if s['type'] == 'HTML':
                section_soup.append(BeautifulSoup(s['HTML'], 'html.parser'))
            elif s['type'] == 'section':
                _ = s['stack']
                if s['shuffle']:
                    _ = random.sample(s['stack'], len(s['stack']))
                html, pid = self.__process_section(_, pid = pid)
                section_soup.append(BeautifulSoup(html, 'html.parser'))
            elif s['type'] == 'problem':
                if ind is None:
                    ind = random.sample(range(0, self.n_inds), 1)[0]
                prob_data = self.__generate_problem_data(s['filename'], s['uuid'], ind)
                
                self.key.append(prob_data['answer_letters'])
                self.pts_correct.append(s['pts_correct'])
                self.pts_incorrect.append(s['pts_incorrect'])
                self.refid.append(prob_data['refid'])
                
                div = section_soup.new_tag('div')
                div['class'] = 'problem'
                if s['min_height']:
                    div['style'] ='min-height: ' + str(s['min_height']) + 'in;>'
                span = section_soup.new_tag('span')
                span['class'] = 'problem_number'
                span.string = str(pid)
                div.append(span)
                
                span = section_soup.new_tag('span')
                span['class'] = 'problem_worth'
                span.string = str(s['pts_correct'])
                div.append(span)
                
                div.append(BeautifulSoup(prob_data['html'], 'html.parser'))
                section_soup.append(div)
                pid += 1
        html = str(section_soup)
        return [html, pid]

    def __process_stack(self, stack, highlight_answers = False, ind = None, pid = None):
        
        soup = BeautifulSoup(open(self.template).read(), 'html.parser')
        
        style = soup.new_tag('style')
        with open(os.path.join(self.cwd, 'teepy.css'), 'r') as fh:
            style.string = fh.read()
        soup.html.head.insert(1, style)
        
        if self.css is not None:
            link = soup.new_tag('link')
            link['rel'] = 'stylesheet'
            link['href'] = css
            soup.html.head.insert(2, link)
        
        if highlight_answers:
            style = soup.new_tag('style')
            style.string = 'li.answer > span {background-color: #D9EAD3;}\n'
#             style.string += '@media print {\n'
#             style.string += '\tbody {\n'
#             style.string += '\t\tbackground-color: #D9EAD3 !important;\n'
#             style.string += '\t\t-webkit-print-color-adjust: exact;\n'
#             style.string += '\t}\n'
#             style.string += '}'
            soup.html.head.append(style)
        
        main = soup.find(id = 'main')
        
        if pid is None:
            pid = 1
        
        for s in stack:
            if s['type'] == 'HTML':
                main.append(BeautifulSoup(s['HTML'], 'html.parser'))
            elif s['type'] == 'section':
                _ = s['stack']
                if s['shuffle']:
                    _ = random.sample(s['stack'], len(s['stack']))
                html, pid = self.__process_section(_, pid = pid)
                main.append(BeautifulSoup(html, 'html.parser'))
            elif s['type'] == 'problem':
                if ind is None:
                    ind = random.sample(range(0, self.n_inds), 1)[0]
                prob_data = self.__generate_problem_data(s['filename'], s['uuid'], ind)
                
                self.key.append(prob_data['answer_letters'])
                self.pts_correct.append(s['pts_correct'])
                self.pts_incorrect.append(s['pts_incorrect'])
                self.refid.append(prob_data['refid'])
                
                div = soup.new_tag('div')
                div['class'] = 'problem'
                if s['min_height']:
                    div['style'] ='min-height: ' + str(s['min_height']) + 'in;>'
                span = soup.new_tag('span')
                span['class'] = 'problem_number'
                span.string = str(pid)
                div.append(span)
                
                span = soup.new_tag('span')
                span['class'] = 'problem_worth'
                span.string = str(s['pts_correct'])
                div.append(span)
                
                div.append(BeautifulSoup(prob_data['html'], 'html.parser'))
                main.append(div)
                pid += 1
        
        for image in soup.findAll('img'):
            filepath, ext = os.path.splitext(os.path.abspath(image['src']))
            img64 = ''
            with open(filepath + ext, 'rb') as img:
                img64 = base64.b64encode(img.read()).decode('utf-8')
            
            image['src'] = 'data:image/' + ext.replace('.', '') + ';base64,' + img64
        
        html = str(soup)
        
        return html
    
    def generate(self, output_dir = './forms/',
                 output_file = './data.xlsx', output_HTML = False,
                 output_PDF = True, output_REFs = True):
        self.flat_stack = []
        self.__flatten_stack(self.stack)
        self.uuids = []
        for fs in self.flat_stack:
            if fs['type'] == 'problem':
                self.uuids.append(fs['uuid'])
        
        if output_REFs:
            for ind in range(0, self.n_inds):
                ref = 'REF_' + str(ind + 1).zfill(4)
                
                print('Generating', ref, '... ', end = '')
                
                html = self.__process_stack(self.flat_stack, highlight_answers = True, ind = ind)
                html = html.replace('{unique_form_number_goes_here}', ref)
                
                self.key = []
                self.pts_correct = []
                self.pts_incorrect = []
                self.refid = []
                
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                if output_HTML:
                    with open(os.path.join(output_dir, ref + '.html'), 'w') as fh:
                        fh.write(html)
                if output_PDF:
                    self.__html_to_pdf(html, os.path.join(output_dir, ref + '.pdf'))
                
                print('Done!')
        
        forms = random.sample(range(1000, 10000), self.n_forms)
        for n_form in range(1, self.n_forms + 1):
            form_str = str(forms[n_form - 1]).zfill(4)
            
            print(str(n_form) + '. Generating Form', form_str, '... ', end = '')
            
            html = self.__process_stack(self.stack)
            html = html.replace('{unique_form_number_goes_here}', form_str)
            
            self.keys.append({'form': form_str, 'values': self.key})
            self.pts_corrects.append({'form': form_str, 'values': self.pts_correct})
            self.pts_incorrects.append({'form': form_str, 'values': self.pts_incorrect})
            self.refids.append({'form': form_str, 'values': self.refid})
            
            self.key = []
            self.pts_correct = []
            self.pts_incorrect = []
            self.refid = []
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            if output_HTML:
                with open(os.path.join(output_dir, 'form_' + form_str + '.html'), 'w') as fh:
                    fh.write(html)
            if output_PDF:
                self.__html_to_pdf(html, os.path.join(output_dir, 'form_' + form_str + '.pdf'))
            
            print('Done!')
        
        keys = sorted(self.keys, key = lambda x: x['form'])
        pts_corrects = sorted(self.pts_corrects, key = lambda x: x['form'])
        pts_incorrects = sorted(self.pts_incorrects, key = lambda x: x['form'])
        refids = sorted(self.refids, key = lambda x: x['form'])
        
        self.keys = []
        self.pts_corrects = []
        self.pts_incorrect = []
        self.refids = []
        
        if not output_file.endswith('.xlsx'):
            output_file += '.xlsx'
            
        wb = xlsxwriter.Workbook(output_file)
        ws_key = wb.add_worksheet('key')
        ws_pts_correct = wb.add_worksheet('pts_correct')
        ws_pts_incorrect = wb.add_worksheet('pts_incorrect')
        ws_refid = wb.add_worksheet('refid')
        
        ws_key.write(0, 0, 'form')
        ws_pts_correct.write(0, 0, 'form')
        ws_pts_incorrect.write(0, 0, 'form')
        ws_refid.write(0, 0, 'form')
        
        for ic, data in enumerate(keys[0]['values']):
            ws_key.write(0, ic + 1, ic + 1)
            ws_pts_correct.write(0, ic + 1, ic + 1)
            ws_pts_incorrect.write(0, ic + 1, ic + 1)
            ws_refid.write(0, ic + 1, ic + 1)
        
        for ir, data in enumerate(keys):
            ws_key.write(ir + 1, 0, keys[ir]['form'])
            ws_pts_correct.write(ir + 1, 0, pts_corrects[ir]['form'])
            ws_pts_incorrect.write(ir + 1, 0, pts_incorrects[ir]['form'])
            ws_refid.write(ir + 1, 0, refids[ir]['form'])
            for ic, val in enumerate(keys[ir]['values']):
                ws_key.write(ir + 1, ic + 1, keys[ir]['values'][ic])
                ws_pts_correct.write(ir + 1, ic + 1, pts_corrects[ir]['values'][ic])
                ws_pts_incorrect.write(ir + 1, ic + 1, pts_incorrects[ir]['values'][ic])
                ws_refid.write(ir + 1, ic + 1, refids[ir]['values'][ic])
        wb.close()
        
        return None