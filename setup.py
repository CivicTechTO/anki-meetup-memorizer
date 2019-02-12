from setuptools import setup

setup(
    name='anki-meetup-memorizer',
    version='0.1',
    py_modules=['cli'],
    install_requires=[
        'Click',
        'meetup-api',
    ],
    dependency_links=[
        #'git+https://github.com/patcon/meetup-api.git@develop#egg=meetup-api',
    ],
    entry_points='''
        [console_scripts]
        anki-meetup-memorizer=cli:create_apkg
    ''',
)
