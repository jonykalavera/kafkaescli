from distutils.core import setup


setup(
    name='kafkescli',
    version='0.1.0',
    packages=['kafkescli'],
    entry_points={
        'console_scripts': ['kafkescli = kafkescli.infra.cli:app']
    }
)