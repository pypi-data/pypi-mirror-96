import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="foolish-auth",
    version="1.1.0",
    author="Xujia Li",
    author_email="lixujia.cn@gmail.com",
    description="a authentication app for projects behind API gateway witch has authentication on API",
    long_description=long_description,
    url="https://github.com/lixujia/FoolishAuth",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    keywords='Django Authenticate Foolish',
    packages=setuptools.find_packages(exclude=['test', 'manage.py', 'db.sqlite3', 'TestApp', 'TestApp/migrations']),
    install_requires=['Django>=3.1.0', 'djangorestframework>=3.12.0'],
)
