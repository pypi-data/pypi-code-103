from setuptools import setup, find_packages

setup(
    name='fast-machine-learning',
    version='0.0.2.1',
    description=(
        'fast-machine-learning'
    ),
    author='luktian',
    author_email='luktian@shu.edu.cn',
    maintainer='luktian',
    maintainer_email='luktian@shu.edu.cn',
    license='BSD License',
    packages=find_packages(exclude=[
        "tests", "*.tests", "*.tests.*", "tests.*", "__pycache__", "fml001.pyproj", 
        "fml001.pyproj.user", "joblibfile", "*.xlsx", "generator_sp.py",
        "catboost_info", "generate_df_from_xlsx.py"
        ]),
    data_files=[
        ('lib/site-packages/fml/feature_selection/exec',['fml/feature_selection/exec/mrmr']),
        ('lib/site-packages/fml/feature_selection/exec',['fml/feature_selection/exec/mrmr.exe']),
        ('lib/site-packages/fml/descriptors/dfs',['fml/descriptors/dfs/base_descriptor.df']),
        ('lib/site-packages/fml/descriptors/dfs',['fml/descriptors/dfs/ionic_radii.df']),
        ('lib/site-packages/fml/descriptors/dfs',['fml/descriptors/dfs/ionization.df']),
        ('lib/site-packages/fml/descriptors/dfs',['fml/descriptors/dfs/name.df']),
        ('lib/site-packages/fml/descriptors/dfs',['fml/descriptors/dfs/other_descriptor.df']),
        ('lib/site-packages/fml/descriptors/dfs',['fml/descriptors/dfs/str_bool_descriptor.df']),
        ],
    platforms=["windows"],
    python_requires=">=3.6",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'sklearn',
        'numpy',
        'pandas',
        'scipy',
        'shap',
        'deap',
        'hyperopt',
        'joblib',
        'pynput',
        'lightgbm',
        'catboost',
        'pyod',
        'matplotlib',
    ],
)