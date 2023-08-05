#!/usr/bin/env python

from contextlib import suppress
from glob import glob
from setuptools import setup, Command
import os
import shutil
import subprocess

from c10_tools.version import version


class BaseCommand(Command):
    description = ''
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class Build(BaseCommand):
    description = 'compile tools to standalone binaries'
    scripts = [
        'allbus.py',
        'c10.py',
        'c10_dmp1553.py',
        'c10_dump_pcap.py',
        'c10_errcount.py',
        'c10_events.py',
        'c10_from_pcap.py',
        'c10_grep.py',
        'c10_headers.py',
        'c10_reindex.py',
        'c10_timefix.py',
        'c10_validator.py',
        'c10_wrap_pcap.py',
        'copy.py',
        'dump.py',
        'stat.py',
    ]

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        env = os.environ.copy()
        env['PYTHONOPTIMIZE'] = '1'
        for f in self.scripts:
            f = 'c10_tools/' + f
            name, _ = os.path.splitext(os.path.basename(f))
            if name.startswith('c10_'):
                name = name.replace('_', '-')
            elif not name.startswith('c10'):
                name = 'c10-' + name
            print(f'Building {name}')
            subprocess.run([
                'pyinstaller', f, '-n', name],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=env)


class Clean(BaseCommand):
    description = 'cleanup .spec files and build/dist directories'

    CLEAN_FILES = '''
        build dist *.pyc *.tgz *.egg-info __pycache__ dependencies
        htmlcov MANIFEST coverage.xml junit*.xml *.spec
    '''

    def run(self):
        here = os.path.abspath(os.path.dirname(__file__))
        for path_spec in self.CLEAN_FILES.split():
            abs_paths = glob(os.path.normpath(os.path.join(here, path_spec)))
            for path in abs_paths:
                print('removing %s' % os.path.relpath(path))
                if os.path.isdir(path):
                    shutil.rmtree(path, True)
                else:
                    with suppress(os.error):
                        os.remove(path)


setup(
    name='c10-tools',
    cmdclass={
        'clean': Clean,
        'build_scripts': Build,
    },
    entry_points={
        'console_scripts': [
            'c10-allbus=c10_tools.allbus:wrapper',
            'c10-copy=c10_tools.copy:wrapper',
            'c10-dmp1553=c10_tools.c10_dmp1553:main',
            'c10-dump=c10_tools.c10_dump:main',
            'c10-dump-pcap=c10_tools.c10_dump_pcap:main',
            'c10-errcount=c10_tools.c10_errcount:main',
            'c10-events=c10_tools.c10_events:main',
            'c10-from-pcap=c10_tools.c10_from_pcap:main',
            'c10-grep=c10_tools.c10_grep:main',
            'c10-reindex=c10_tools.c10_reindex:main',
            'c10-stat=c10_tools.stat:wrapper',
            'c10-timefix=c10_tools.c10_timefix:main',
            'c10-validator=c10_tools.c10_validator:main',
            'c10-wrap-pcap=c10_tools.c10_wrap_pcap:main',
            'c10=c10_tools.c10:main',
        ],
    },
    version=version,
    description='Various tools for managing IRIG 106 Chapter 10/11 data',
    author='Micah Ferrill',
    author_email='ferrillm@avtest.com',
    packages=['c10_tools'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/atac/c10-tools',
    python_requires='>=py3.6',
    install_requires=[
        'dask[bag,delayed,distributed,dataframe]>=2.23',
        'docopt>=0.6.2',
        'dpkt>=1.9.3',
        'pychapter10>=1.0.4',
        'tqdm>=4.48.2',
        's3fs>=0.5.2',
        'termcolor>=1.1.0',
        'matplotlib>=3.3.4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
