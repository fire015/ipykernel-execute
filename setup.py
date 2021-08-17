from distutils.core import setup

setup(
    name='ipyrepl',
    version='1.0',
    description='Simple server and REPL to execute code inside ipykernel',
    install_requires=[
        'ipykernel', 'Flask'
    ],
)
