import setuptools

setuptools.setup(
    name="expy",
    version="0.1.0",
    url="https://github.com/jimmycallin/expy",

    author="Jimmy Callin",
    author_email="jimmy.callin@gmail.com",

    description="Made to ease reproducible scientific experiments.",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    test_suite='nose2.collector.collector',

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['pymysql']
)
