import html
import tomd
from bs4 import BeautifulSoup


def to_markdown(html_text):
    if not html_text:
        return ""

    html_text = html_text.replace("$$$", "$")
    # html_text = html_text.replace("&thinsp;", " ")
    html_text = html_text.replace(" ", " ") # &thinsp;
    soup = BeautifulSoup(html_text, 'html.parser')

    # img tag must be inside <p> tag
    imgs = soup.select("img")
    if imgs:
        for img in imgs:
            if "alt" in img:
                img.string = img['alt']
            del img['style']
            del img['alt']
            new_tag = soup.new_tag('p')
            img.wrap(new_tag)

    bold = soup.select('.tex-font-style-bf')
    for tag in bold:
        tag.name = 'strong'
        tag.attrs = {}
    tt = soup.select('.tex-font-style-tt')
    for tag in tt:
        tag.name = 'code'
        tag.attrs = {}
    tt = soup.select('.tex-font-style-it')
    for tag in tt:
        tag.name = 'i'
        tag.attrs = {}

    # convert subscript and superscript to latext
    #  *...*<sub class="lower-index">*...*
    #  *...*<sub class="upper-index">*...*
    subscripts = soup.select('sub')
    for subscript in subscripts:
        print(str(subscript))
    supper_scripts = soup.select('sup')
    for supper_script in supper_scripts:
        print(str(supper_script))

    res = tomd.convert(html.unescape(soup.decode())).strip()


    return res
