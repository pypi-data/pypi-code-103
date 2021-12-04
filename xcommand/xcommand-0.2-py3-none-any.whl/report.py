import os
import re
import glob

import click
import win32com.client


class Word:
    def __init__(self, path, visible):
        try:
            self.app = win32com.client.DispatchEx('kwps.Application')
        except Exception:
            self.app = win32com.client.DispatchEx('Word.Application')
        self.app.DisplayAlerts = False
        self.app.Visible = visible
        self.doc = self.app.Documents.Open(os.path.abspath(path))

    def close(self):
        self.doc.Close()
        self.app.Quit()

    def save(self, path):
        self.doc.SaveAs(os.path.abspath(path))

    @property
    def text(self):
        content = self.doc.Content.Text
        others = ''
        for shape in self.doc.Shapes:
            try:
                others = others + shape.TextFrame.TextRange.Text
            except:
                pass
        for section in self.doc.Sections:
            for i in range(1, 4):
                others = others + section.Headers(i).Range.Text + section.Footers(i).Range.Text
                for shape in section.Headers(i).Shapes:
                    try:
                        others = others + shape.TextFrame.TextRange.Text
                    except:
                        pass
                for shape in section.Footers(i).Shapes:
                    try:
                        others = others + shape.TextFrame.TextRange.Text
                    except:
                        pass
        return content, others

    @property
    def targets(self):
        content = re.findall(r'({{ (.+?)/(.+?) }})', self.text[0])
        others = re.findall(r'({{ (.+?)/(.+?) }})', self.text[1])
        return list(set(content)), list(set(others))

    def replace_text(self, key, value, full=0):
        self.doc.Content.Find.Execute(key, True, False, False, False, False, True, 1, True, value, 2)
        if not full:
            return

        for shape in self.doc.Shapes:
            try:
                shape.TextFrame.TextRange.Find.Execute(key, True, False, False, False, False, True, 1, True, value, 2)
            except:
                pass
        for section in self.doc.Sections:
            for i in range(1, 4):
                section.Headers(i).Range.Find.Execute(key, True, False, False, False, False, True, 1, True, value, 2)
                section.Footers(i).Range.Find.Execute(key, True, False, False, False, False, True, 1, True, value, 2)
                for shape in section.Headers(i).Shapes:
                    try:
                        shape.TextFrame.TextRange.Find.Execute(key, True, False, False, False, False, True, 1, True, value, 2)
                    except:
                        pass
                for shape in section.Footers(i).Shapes:
                    try:
                        shape.TextFrame.TextRange.Find.Execute(key, True, False, False, False, False, True, 1, True, value, 2)
                    except:
                        pass

    def select_text(self, text):
        self.app.Selection.SetRange(0, 0)
        return self.app.Selection.Find.Execute(FindText=text, Wrap=True, Format=True)

    def paste(self):
        return self.app.Selection.PasteAndFormat(Type=19)

    def set_width(self, width=340.157471):
        index = self.doc.InlineShapes.Count
        shape = self.doc.InlineShapes(index)
        ratio = shape.Height / shape.Width
        height = ratio * width
        shape.Width = width
        shape.Height = height


class Excel:
    def __init__(self, path, visible):
        try:
            self.app = win32com.client.DispatchEx('ket.Application')
        except Exception:
            self.app = win32com.client.DispatchEx('Excel.Application')
        self.app.DisplayAlerts = False
        self.app.Visible = visible
        self.doc = self.app.Workbooks.Open(os.path.abspath(path))
        self.sheets = {}

    def close(self):
        self.doc.Close()
        self.app.Quit()

    def get_sheet(self, name):
        sheet = self.sheets.get(name)
        if sheet is None:
            sheet = self.doc.Worksheets(name)
            self.sheets[name] = sheet
        return sheet

    def get_value(self, sht, index):
        return self.get_sheet(sht).Range(index).Text

    def copy_chart(self, sht, index):
        return self.get_sheet(sht).ChartObjects(index).Copy()

    def copy_shape(self, sht, index):
        return self.get_sheet(sht).Shapes(index).Copy()


def parse(word, excel, out, visible):
    """
    解析word文件中的特殊字符，在excel文件中寻找指定内容替换，生成新的word文档并保存到指定地址
    :param word: word模板地址
    :param excel: excel数据源地址
    :param out: 输出word文档地址
    :param visible: 指定运行过程中office软件窗口的可见性
    :return:
    """
    word = Word(word, visible)
    excel = Excel(excel, visible)

    targets = word.targets
    for index, item in enumerate(targets):
        for target in item:
            text, sht, ind = target
            try:
                if re.match(r'^[a-z]+[0-9]+$', ind, re.I) is not None:
                    word.replace_text(text, excel.get_value(sht, ind), index)
                elif re.match(r'^c:(.+)$', ind) is not None:
                    chart = re.match(r'^c:(.+)$', ind).group(1)
                    excel.copy_chart(sht, chart)
                    if word.select_text(text):
                        word.paste()
                        word.set_width()
                    else:
                        click.echo('Info：{}：“{}”替换失败'.format(out, text))
                elif re.match(r'^s:(.+)$', ind) is not None:
                    shape = re.match(r'^s:(.+)$', ind).group(1)
                    excel.copy_shape(sht, shape)
                    if word.select_text(text):
                        word.paste()
                        word.set_width()
                    else:
                        click.echo('Info：{}：“{}”替换失败'.format(out, text))
                else:
                    click.echo('Info：{}：“{}”替换失败'.format(out, text))
            except Exception:
                click.echo('Info：{}：“{}”替换失败'.format(out, text))
    word.save(out)

    word.close()
    excel.close()
    click.echo('Info：{}：报告生成成功'.format(out))


@click.group()
def cli():
    """报告相关工具，可极大提高出报告或其他模板式word文档的效率"""
    pass


@cli.command()
@click.option(
    '--template', '-t',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help='必要参数，指定word模板文件地址'
)
@click.option(
    '--file', '-f',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help='指定excel数据文件地址，与-d参数必须二选一'
)
@click.option(
    '--dir', '-d',
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help='指定excel数据文件夹地址，与-f参数必须二选一，此模式下最终的word输出文档名与excel数据文件名一致'
)
@click.option(
    '--out', '-o',
    type=click.Path(resolve_path=True),
    help=r'指定word输出文件或文件夹地址。当选择-f参数时，默认为“./out.docx”；当选择-d参数时，默认为“./out/”'
)
@click.option(
    '--hide', '-h',
    is_flag=True,
    default=False,
    help='隐藏运行过程中office软件窗口'
)
def genrpt(template, file, dir, out, hide):
    """根据word模板自动读取excel中指定数据生成报告文档"""
    if not template:
        click.echo('Error：缺少必要参数“--template”', err=True)
        return
    if file and dir:
        click.echo('Error：“--file”与“--dir”只能二选一', err=True)
        return
    if file:
        if not out:
            out = 'out.docx'
        parse(template, file, out, not hide)
    elif dir:
        if not out:
            out = 'out/'
        if not os.path.exists(out):
            os.makedirs(out)
        for excel in glob.glob(os.path.join(dir, '*.xlsx')):
            name = os.path.splitext(os.path.split(excel)[1])[0]
            parse(template, excel, os.path.join(out, name + '.docx'), not hide)
    else:
        click.echo('Error：“--file”与“--dir”必须二选一', err=True)


if __name__ == '__main__':
    cli()
    # import time
    # start = time.time()
    # parse('../huaxing.docx', '../data/huaxing.xlsx', '../out.docx', False)
    # print(time.time()-start)
