from setuptools import setup
from setuptools import find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
   name='aucmedi',
   version='0.1.0',
   description='AUCMEDI - Framework for Automated Classification of Medical Images',
   url='https://github.com/frankkramer-lab/aucmedi',
   author='Dominik Müller',
   author_email='dominik.mueller@informatik.uni-augsburg.de',
   license='GPLv3',
   long_description=long_description,
   long_description_content_type="text/markdown",
   packages=find_packages(),
   python_requires='>=3.6',
   install_requires=['tensorflow>=2.3.0',
                     'keras-applications==1.0.8',
                     'numpy>=1.18.5',
                     'pillow==7.2.0',
                     'albumentations>=0.5.2',
                     'pandas>=1.1.4',
                     'scikit-learn',
                     'scikit-image>=0.17.2'],
   classifiers=["Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
                "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                "Operating System :: OS Independent",

                "Intended Audience :: Healthcare Industry",
                "Intended Audience :: Science/Research",

                "Topic :: Scientific/Engineering :: Artificial Intelligence",
                "Topic :: Scientific/Engineering :: Image Recognition",
                "Topic :: Scientific/Engineering :: Medical Science Apps."]
)
