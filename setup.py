from setuptools import find_packages, setup
import re

with open("requirements.txt", "r") as f:
    requirements = []
    for line in f.read().split("\n"):
        m = re.match("git\+https://www.github.com/[^/]+/([^/]+)@[^/]+", line)
        if m:
            requirements.append(f"{m[1]} @ {line.strip()}")
        else:
            requirements.append(line.strip())

setup(
    name='ypricemagic',
    packages=find_packages(),
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        "local_scheme": "no-local-version",
        "version_scheme": "python-simplified-semver",
    },
    description='Use this tool to extract historical on-chain price data from an archive node. Shoutout to @bantg and @nymmrx for their awesome work on yearn-exporter that made this library possible.',
    author='BobTheBuidler',
    author_email='bobthebuidlerdefi@gmail.com',
    url='https://github.com/BobTheBuidler/ypricemagic',
    license='MIT',
    install_requires=requirements,
    setup_requires=[
        'setuptools_scm',
    ],
)
