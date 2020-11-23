from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    reqs = fh.read().splitlines()

def local_scheme(version):
    return ""

def version_scheme(version):
    dist = version.distance
    v = ".".join([version.tag.base_version, str(dist)])
    return v

setup(
    name="ql",
    author="Louis Maddox",
    author_email="louismmx@gmail.com",
    description="spin.systems generator and driver",
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spin-systems/quill/",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
    ],
    include_package_data=True,
    use_scm_version={
        "version_scheme": version_scheme,
        "local_scheme": local_scheme,
    },
    setup_requires=["setuptools_scm"],
    install_requires=reqs,
    python_requires=">=3",
)
