import setuptools

setuptools.setup(
    name="pyresult",
    version="0.1.0",
    url="https://github.com/jimmycallin/pyresult",

    author="Jimmy Callin",
    author_email="jimmy.callin@gmail.com",

    description="Made to ease reproducible results.",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ]
)
