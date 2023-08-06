import setuptools

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()
    git_requirements = [f.strip('\n') for f in requirements if 'git' in f]
    requirements = [f for f in requirements if 'git' not in f]

with open('README.md', 'r') as f:
    readme = f.read()

setuptools.setup(
    name="Cathub",
    version="0.1.7",
    url="https://github.com/SUNCAT-Center/CatHub",
    author="Kirsten Winther",
    author_email="winther@stanford.edu",

    description="Python API for the Surface Reactions database on Catalysis-Hub.org",
    long_description=readme,
    license='GPL-3.0',

    packages=[
        'cathub',
        'cathub.ase_tools'
    ],
    package_dir={'cathub': 'cathub'},
    entry_points={'console_scripts': ['cathub=cathub.cli:cli']},
    install_requires=requirements,
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Chemistry',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
