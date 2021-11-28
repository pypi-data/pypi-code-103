from setuptools import setup, find_packages
import glob

setup(
    name='gaelib',
    version='0.1.7',
    description='Google App Engine Library',
    author='Shantanu Mallik',
    license='MIT',
    packages=find_packages(where='.') + find_packages(exclude=("tests",)),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'wheel',
        'google-cloud-speech',
        'google-cloud-core',
        'grpcio',
        'google-api-core==1.17.0',
        'google-auth',
        'google-cloud-datastore',
        'requests',
        'google-cloud-logging',
        'inflect==2.1.0',
        'google-cloud-storage',
        'py-dateutil==2.2',
        'cryptography==2.9.2',
        'pyjwt==1.7.1',
        'hyper==0.7.0',
        'google-cloud-tasks==1.5.0',
        'googleapis_common_protos',
        'firebase-admin',
        'python-jose',
        'nose',
        'mock',
        'google-cloud',
        'click==7.1.2',
        'Flask==1.1.2',
        'Flask-Cors==3.0.9',
        'gunicorn==20.0.4',
        'itsdangerous==1.1.0',
        'Jinja2==2.11.2',
        'MarkupSafe==1.1.1',
        'python-dotenv==0.14.0',
        'six==1.15.0',
        'Werkzeug==1.0.1',
        'constants',
        'twilio'
    ],
    setup_requires=[
        'wheel'
    ]
)
