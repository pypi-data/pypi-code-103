# -*- coding: utf-8 -*-
from xltmpl.xlsxtemplate import XlsxTemplate
from xltmpl.xlstemplate import XlsTemplate


class XlTemplate:
    def __init__(self, tmpl_path: str, save_path: str, apply_styles=True, place_holder='{{}}'):
        self._obj = None
        self.tmpl_path = tmpl_path
        self.save_path = save_path
        self.apply_styles = apply_styles
        self.place_holder = place_holder

        if self.tmpl_path.endswith('.xls'):
            if self.save_path.endswith('.xlsx'):
                self.save_path = self.save_path.rstrip('x')
        elif self.tmpl_path.endswith('.xlsx'):
            if self.save_path.endswith('.xls'):
                self.save_path = self.save_path + 'x'
        else:
            pass

    def __enter__(self):
        if self.tmpl_path.endswith('.xlsx'):
            self._obj = XlsxTemplate(self.tmpl_path, self.save_path, self.apply_styles, self.place_holder)
        elif self.tmpl_path.endswith('.xls'):
            self._obj = XlsTemplate(self.tmpl_path, self.save_path, self.apply_styles, self.place_holder)
        else:
            TypeError('{} not be allowed'.format(self.tmpl_path.split('.'[-1])))
        return self._obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._obj.__exit__(exc_type, exc_val, exc_tb)

    def create_template(self):
        if self.tmpl_path.endswith('.xlsx'):
            return XlsxTemplate(self.tmpl_path, self.save_path, self.apply_styles, self.place_holder)
        elif self.tmpl_path.endswith('.xls'):
            return XlsTemplate(self.tmpl_path, self.save_path, self.apply_styles, self.place_holder)
        else:
            TypeError('{} not be allowed'.format(self.tmpl_path.split('.'[-1])))


if __name__ == '__main__':
    pass
