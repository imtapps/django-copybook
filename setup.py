from setuptools import setup, find_packages

REQUIREMENTS = [
    'django',
]

from djcopybook import VERSION

setup(
    name="django-copybook",
    version=VERSION,
    author="Matthew J. Morrison",
    author_email="mattj.morrison@gmail.com",
    description="Convert Objects and Django models to/from fixed format records.",
    long_description=open('README.txt', 'r').read(),
    packages=find_packages(exclude=["example"],),
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS,
    test_suite='runtests.runtests',
    zip_safe=False,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
)
