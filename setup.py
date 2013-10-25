from setuptools import setup, find_packages

setup(
    name="django-copybook",
    version='1.0.0',
    author="imtapps",
    author_email="webadmin@imtapps.com",
    description="Convert Objects and Django models to/from fixed format records.",
    url="https://github.com/imtapps/django-copybook",
    long_description=open('README.txt', 'r').read(),
    packages=find_packages(exclude=["example"],),
    install_requires=open('requirements/dist.txt').read(),
    zip_safe=False,
    classifiers=[
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
