from setuptools import find_packages, setup

setup(
    name='gen-cli',
    version='1.0.0',
    py_modules=['model_generator', 'main_schema_gen', 'schema_validate'],
    entry_points={
        'console_scripts': [
            'gen-cli = app.cli:main',
        ],
    },
    packages=find_packages(),
)
