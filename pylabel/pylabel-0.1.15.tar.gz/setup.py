from setuptools import setup

setup(
    name='pylabel',
    packages=['pylabel'],
    version='0.1.15',
    description='Transform, analyze, and visualize computer vision annotations.',
    url = 'https://github.com/pylabel-project/pylabel',
    author='PyLabel Project',
    license='MIT',
    install_requires=['pandas','bbox_visualizer','matplotlib','opencv-python','scikit-learn','jupyter_bbox_widget','pyyaml']
)