from setuptools import setup
setup(
  name = 'LinkToPy',
  packages = ['LinkToPy'], # this must be the same as the name above
  version = '0.2.4',
  description = 'A python wrapper for Ableton Link using TCP and Carabiner',
  author = 'Ben Yetton',
  author_email = 'bdyetton@gmail.com',
  url = 'https://github.com/bdyetton/LinkToPy', # use the URL to the github repo
  download_url = 'http://pypi.python.org/pypi/LinkToPy/', # I'll explain this in a second
  keywords = ['link','python','lighting' ,'serato', 'abelton'], # arbitrary keywords
  classifiers = [],
  install_requires=["edn_format >= 0.5.12"]
)
