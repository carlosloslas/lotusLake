from setuptools import setup
from lotuslake import version

setup(name='lotuslake',
      version=version,
      description='Python tools for analysing a collection of Lotus simulations (output files)',
      url='https://github.com/carlosloslas/lotuslake',
      author='Carlos Losada',
      author_email='losadalastra.carlos@gmail.com',
      license='MIT',
      packages=['lotuslake'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)
