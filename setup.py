from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='http_logging',
      version='0.2',
      description='Better HTTP Log Handler',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
      ],
      keywords='http logging syslog server',
      url='https://bitbucket.org/eiwa_dev/nostradamus',
      author='Juan I Carrano <jc@eiwa.ag>',
      author_email='jc@eiwa.ag',
      license='Proprietary',
      packages=['http_logging'],
      include_package_data=True,
      zip_safe=True
    )
