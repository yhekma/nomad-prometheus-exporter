from setuptools import setup, find_packages

setup(
    name='nomad-exporter',
    packages=find_packages(),
    scripts=['exporter.py'],
    install_requires=[
        'prometheus_client>=0.2.0',
        'python-nomad>=0.8.0',
    ]
)
