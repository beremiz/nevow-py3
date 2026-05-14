#!/usr/bin/python

_MINIMUM_TWISTED_VERSION = "13.0"

from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name='Nevow',
        version="0.14.5",
        packages=find_packages(),
        include_package_data=True,
        author='Divmod, Inc.',
        author_email='support@divmod.org',
        maintainer='Twisted Matrix Labs',
        maintainer_email='twisted-web@twistedmatrix.com',
        description='Web Application Construction Kit',
        url='https://github.com/twisted/nevow',
        license='MIT',
        platforms=["any"],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Framework :: Twisted",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Software Development :: Libraries",
            ],
        package_data={
                'formless': [
                    'freeform-default.css'
                    ],
                },
        install_requires=[
            # Nevow builds on Twisted Web's HTTP server.  It also uses various
            # other generally useful pieces of Twisted (such as its logging system,
            # not to mention reactors and Deferreds).
            #
            # That dependency will be expressed here with a version range including
            # only those versions of Twisted against which Nevow's continuous
            # integration system is configured to actually test.  This ensures any
            # combination allowed by this declaration has been tested and found to
            # work.
            "twisted>=" + _MINIMUM_TWISTED_VERSION,
            ],
        zip_safe=False,
    )
