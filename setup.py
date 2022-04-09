from distutils.core import setup


setup(
    name='kafkaescli',
    version='0.1.0',
    packages=['kafkaescli'],
    entry_points={
        'console_scripts': ['kafkaescli = kafkaescli.infra.cli:app', 'kfk = kafkaescli.infra.cli:app']
    }
)