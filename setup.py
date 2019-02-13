from setuptools import setup

setup(
    name='anki-meetup-memorizer',
    version='0.1',
    py_modules=['cli'],
    install_requires=[
        'Click',
        'meetup-api',
        'decorator',
    ],
    entry_points='''
        [console_scripts]
        anki-meetup-memorizer=cli:create_apkg
    ''',
)
