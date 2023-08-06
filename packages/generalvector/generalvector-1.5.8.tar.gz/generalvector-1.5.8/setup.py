

from setuptools import setup, find_namespace_packages
from pathlib import Path

setup(
    name="generalvector",
    author='Rickard "Mandera" Abraham',
    author_email="rickard.abraham@gmail.com",
    version="1.5.8",
    description="Simple immutable vectors.",
    long_description=(Path(__file__).parent / 'README.md').read_text(encoding='utf-8'),
    long_description_content_type="text/markdown",
    install_requires=[
        'generallibrary',
    ],
    url="https://github.com/ManderaGeneral/generalvector",
    license="mit",
    python_requires=">=3.8, <3.10",
    packages=find_namespace_packages(exclude=("build*", "dist*")),
    extras_require={},
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
)
