import os
pkg_root=os.path.dirname(__file__)
pkg_data_dir=pkg_root+'/data'
pkg_templates_dir=pkg_data_dir+'/templates'

class PkgData:
    class Paths:
        example=pkg_data_dir+'/example'
class TemplatePaths:
    python_package=pkg_templates_dir+'/python_package'
    wkmake_file_path=pkg_templates_dir+'/wkmake.yaml'