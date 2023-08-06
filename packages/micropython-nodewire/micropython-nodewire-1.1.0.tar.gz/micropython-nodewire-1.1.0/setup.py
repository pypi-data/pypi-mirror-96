from setuptools import setup
# https://python-packaging.readthedocs.io/en/latest/minimal.html
# python setup.py sdist upload
# python -m twine upload dist/*

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='micropython-nodewire',
      version='1.1.0',
      description='NodeWire',
      long_description=readme(),
      url='http://www.nodewire.org',
      author='Ahmad Sadiq',
      author_email='sadiq.a.ahmad@gmail.com',
      license='BSD',
      packages=['nodewire'],
      scripts=['bin/nw_script.py', 'bin/nw_client.py'],
      install_requires=[
            'inspect'
      ],
      zip_safe=False)