from setuptools import setup, find_packages, find_namespace_packages

setup(
    name='anki-meetup-memorizer',
    version='0.1',
    # Look for anki package in anki/anki
    package_dir={'anki': 'anki/anki'},
    packages=find_packages() + find_packages('anki', include=['anki','anki.*']),
    include_package_data=True,
    install_requires=[
        'Click',
        'meetup-api',
        'decorator',
    ],
    # TODO: Fetch meetup-api from custom fork.
    entry_points={
        'console_scripts': [
            'anki-meetup-memorizer=anki_meetup_memorizer.cli:create_apkg',
        ],
    }
)
