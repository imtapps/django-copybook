from setuptools import setup

REQUIREMENTS = [
    'django',
]

setup(
    name="django-copybook",
    version='0.0.3',
    author="Matthew J. Morrison",
    author_email="mattj.morrison@gmail.com",
    description="Convert Django models to/from fixed format records.",
    long_description=open('README.txt', 'r').read(),
    packages=("djcopybook",),
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS,
    test_suite='runtests.runtests',
    zip_safe=False,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
