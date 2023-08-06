# pylint: disable = C0111
from setuptools import find_packages, setup

with open("README.md", "r") as f:
    DESCRIPTION = f.read()

setup(name="paperai",
      version="1.7.0",
      author="NeuML",
      description="AI-powered literature discovery and review engine for medical/scientific papers",
      long_description=DESCRIPTION,
      long_description_content_type="text/markdown",
      url="https://github.com/neuml/paperai",
      project_urls={
          "Documentation": "https://github.com/neuml/paperai",
          "Issue Tracker": "https://github.com/neuml/paperai/issues",
          "Source Code": "https://github.com/neuml/paperai",
      },
      license="Apache 2.0: http://www.apache.org/licenses/LICENSE-2.0",
      packages=find_packages(where="src/python"),
      package_dir={"": "src/python"},
      keywords="search embedding machine-learning nlp covid-19 medical scientific papers",
      python_requires=">=3.6",
      entry_points={
          "console_scripts": [
              "paperai = paperai.shell:main",
          ],
      },
      install_requires=[
          "html2markdown>=0.1.7",
          "mdv>=1.7.4",
          "networkx>=2.4",
          "PyYAML>=5.3",
          "regex>=2020.5.14",
          "txtai>=2.0.0",
          "txtmarker>=1.0.0"
      ],
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Scientific/Engineering :: Artificial Intelligence",
          "Topic :: Software Development",
          "Topic :: Text Processing :: Indexing",
          "Topic :: Utilities"
      ])
