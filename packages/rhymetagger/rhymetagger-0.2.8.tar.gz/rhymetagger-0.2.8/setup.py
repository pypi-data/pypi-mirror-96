from setuptools import setup
#from distutils.core import setup

with open(('README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'rhymetagger',
  long_description_content_type='text/markdown',
  long_description=long_description,
  #include_package_data = True,  
  packages = ['rhymetagger'],   
  version = '0.2.8',      
  license='MIT',        
  description = 'A simple collocation-driven recognition of rhymes',   
  author = 'Petr Plechac',                   
  author_email = 'plechac@ucl.cas.cz',      
  url = 'https://github.com/versotym/rhymetagger',
  download_url = 'https://github.com/versotym/rhymeTagger/archive/v0.2.tar.gz',
  keywords = ['poetry', 'rhyme', 'versification'],
  package_data={'rhymetagger': ['models/*.json']},
  #  data_files=[('models', ['models/cs.json', 'models/en.json', 'models/de.json', 'models/nl.json', 'models/es.json', 'models/ru.json'])], 
  install_requires=[           
          'ujson',
          'nltk',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',      
    'Topic :: Text Processing :: Linguistic',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.1',      
    'Programming Language :: Python :: 3.2',      
    'Programming Language :: Python :: 3.3',      
    'Programming Language :: Python :: 3.4',      
    'Programming Language :: Python :: 3.5',      
    'Programming Language :: Python :: 3.6',      
    'Programming Language :: Python :: 3.7',      
    'Programming Language :: Python :: 3.8',      
    'Programming Language :: Python :: 3.9',      
    'Programming Language :: Python :: 3.10',      
  ],
)
