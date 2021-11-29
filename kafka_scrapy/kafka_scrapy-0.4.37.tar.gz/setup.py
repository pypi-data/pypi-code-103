from setuptools import setup, find_packages

setup(
    name="kafka_scrapy",
    packages=['kafka_scrapy'],
    version='0.4.37',
    description="kafka-based components for Scrapy.",
    author="kong",
    author_email='tomngp@163.com',
    url="https://github.com/kwx1996/kafka_scrapy",
    download_url='https://github.com/kwx1996/kafka_scrapy/archive/master.zip',
    classifiers=[],
    install_requires=[
        'twisted',
        'scrapy',
        'redis',
        'confluent_kafka'
    ]
)
