from setuptools import setup

with open('C:\\Users\\James\\Desktop\\Simplesender\\Simplesender\\README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'Simplesender',
    version = '0.1.0.1',
    description = 'Webhook 을 이용해 채널에 메시지를 보냅니다.',
    author = '9Hundred100Five1',
    author_email = 'ohot2124@naver.com',
    url = 'https://github.com/9Hundred100Five1/simple-discordWebhook-sender',
    py_modules=  ['asyncio'],
    keywords = ['discord', 'discord.py', 'sWs', 'SimpleSender'],
    license='GPL-3.0',
    long_description = long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ]
)