import setuptools
from setuptools import setup

requirements = [
    'pysteamauth>=1.0.0',
    'aiofiles>=22.1.0',
    'cssselect>=1.1.0',
    'lxml>=4.9.1',
]


setup(
    name='pysteamlib',
    version='0.0.3',
    url='https://github.com/sometastycake/pysteamlib',
    license='MIT',
    author='Mike M',
    author_email='stopthisworldplease@outlook.com',
    description='Python Steam library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    zip_safe=False,
    python_requires='>=3.7',
    install_requires=requirements,
    setup_requires=requirements,
    include_package_data=True,
)
