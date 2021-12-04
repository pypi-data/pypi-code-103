import os

import img2pdf
import fitz
import click


def img_to_pdf(imgs, pdf_path, page_size, reverse, free):
    """
    转换图片为pdf格式并合并，为了保证无损转换，不支持有alpha通道的图片
    :param imgs: 图片地址列表，需要按合并顺序排列
    :param pdf_path: pdf文件的保存地址
    :param page_size: pdf文件的页面尺寸
    :param reverse: 是否反转页面尺寸，即长宽尺寸互换
    :param free: 是否自由尺寸，为True时忽略page_size和reverse
    :return:
    """
    if free:
        layout_fun = img2pdf.default_layout_fun
    else:
        if reverse:
            page_size = page_size[::-1]
        layout_fun = img2pdf.get_layout_fun(page_size)

    # 转换图片为pdf格式并合并到指定路径
    with open(pdf_path, 'wb') as f:
        f.write(img2pdf.convert(imgs, layout_fun=layout_fun))


def pdf_to_img(file_path, save_dir, scale, prefix, format):
    trans = fitz.Matrix(scale, scale)
    with fitz.open(file_path) as pdf:
        for pg in range(pdf.pageCount):
            page = pdf[pg]
            pix = page.get_pixmap(alpha=False, matrix=trans)
            img_name = prefix + '%s.' % str(pg+1).zfill(4) + format
            pix.save(os.path.join(save_dir, img_name))


def is_image(path):
    exts = ['.jpeg', '.jpg', '.png']
    return os.path.splitext(os.path.split(path)[1])[1].lower() in exts


def is_pdf(path):
    return os.path.splitext(os.path.split(path)[1])[1].lower() == '.pdf'


@click.group()
def cli():
    """快速合并或拆分pdf文件"""
    pass


@cli.command()
@click.argument(
    'path',
    nargs=-1,
    type=click.Path(exists=True, resolve_path=True),
    required=True
)
@click.option(
    '--out', '-o',
    type=click.Path(resolve_path=True),
    default='out.pdf',
    show_default=True,
    help='指定pdf输出文件地址'
)
@click.option(
    '--size', '-s',
    type=click.Choice(['A3', 'A4', 'A5', 'B4', 'B5']),
    default='A4',
    show_default=True,
    help='指定pdf输出文件每一页的固定尺寸'
)
@click.option(
    '--reverse', '-r',
    is_flag=True,
    default=False,
    help='反转页面的长和高，配合“--size”使用，添加该参数后页面为横向'
)
@click.option(
    '--free', '-f',
    is_flag=True,
    default=False,
    help='自由尺寸，添加该参数后“--size”和“--reverse”无效，每一页保持源图片的形状和尺寸'
)
def topdf(path, out, size, reverse, free):
    """将指定图片及指定文件夹中图片合并为一个pdf文件，文件夹中图片顺序按照文件名升序排列"""
    imgs = []
    for item in path:
        if os.path.isfile(item):
            if is_image(item):
                imgs.append(item)
            else:
                click.echo('Error：“{}”不支持该图片的格式'.format(item), err=True)
                return
        else:
            tem = []
            for _, _, files in os.walk(item):
                for file in files:
                    if is_image(file):
                        tem.append(os.path.join(item, file))
            if not len(tem):
                click.echo('Error：“{}”中没有支持的图片'.format(item), err=True)
                return
            tem.sort()
            for img in tem:
                imgs.append(img)
    click.echo('Info：{}'.format(imgs))

    if is_pdf(out):
        save_dir = os.path.split(out)[0]
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    else:
        click.echo('Error：“{}”不是pdf格式文件'.format(out), err=True)

    size_dic = {
        'A3': (img2pdf.mm_to_pt(297), img2pdf.mm_to_pt(420)),
        'A4': (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)),
        'A5': (img2pdf.mm_to_pt(148), img2pdf.mm_to_pt(210)),
        'B4': (img2pdf.mm_to_pt(257), img2pdf.mm_to_pt(364)),
        'B5': (img2pdf.mm_to_pt(182), img2pdf.mm_to_pt(257))
    }

    img_to_pdf(imgs, out, size_dic[size], reverse, free)
    click.echo('Info：{}：图片转pdf成功'.format(out))


@cli.command()
@click.argument(
    'path',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True
)
@click.option(
    '--out', '-o',
    type=click.Path(resolve_path=True),
    default='out/',
    show_default=True,
    help='指定图片输出文件夹地址'
)
@click.option(
    '--scale', '-s',
    type=click.FLOAT,
    default=2,
    show_default=True,
    help='指定输出图片的缩放比例'
)
@click.option(
    '--prefix', '-p',
    type=click.STRING,
    default='',
    show_default=True,
    help='每张图片的文件名前缀'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['jpeg', 'png']),
    default='jpeg',
    show_default=True,
    help='每张图片的文件格式'
)
def toimg(path, out, scale, prefix, format):
    """将单个pdf文件的每一页导出为图片"""
    if not is_pdf(path):
        click.echo('Error：“{}”不是pdf格式文件'.format(path), err=True)
        return
    if not os.path.exists(out):
        os.makedirs(out)
    pdf_to_img(path, out, scale, prefix, format)
    click.echo('Info：{}：pdf转图片成功'.format(out))


if __name__ == '__main__':
    cli()
