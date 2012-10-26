#/usr/bin/env python
import codecs
import os
import sys

from setuptools import setup, find_packages

if 'publish' in sys.argv:
    os.system('python setup.py sdist upload')
    sys.exit()

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

# Load package meta from the pkgmeta module without loading imagekit.
pkgmeta = {}
execfile(os.path.join(os.path.dirname(__file__),
         'imagekit', 'pkgmeta.py'), pkgmeta)

setup(
    name='django-imagekit',
    version=pkgmeta['__version__'],
    description='Automated image processing for Django models.',
    long_description=read(os.path.join(os.path.dirname(__file__), 'README.rst')),
    author='Justin Driscoll',
    author_email='justin@driscolldev.com',
    maintainer='Bryan Veloso',
    maintainer_email='bryan@revyver.com',
    license='BSD',
    url='http://github.com/jdriscoll/django-imagekit/',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    tests_require=[
        'nose==1.2.1',
        'nose-progressive==1.3',
        'django-nose==1.1',
    ],
    install_requires=[
        'django-appconf>=0.5',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ],
)
