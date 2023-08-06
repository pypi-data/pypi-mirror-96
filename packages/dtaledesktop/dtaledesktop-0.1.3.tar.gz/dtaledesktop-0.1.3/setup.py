from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as infile:
        return infile.read()


classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
]

install_requires = [
    "dtale>=1.22.1",  # Earlier versions probably also work, just need to figure out how far back...
    "fastapi",
    "uvicorn[standard]",
    "aiofiles",
    "aiohttp",
    "typing_extensions",
    "pandas-profiling",
]

setup(
    name="dtaledesktop",
    version="0.1.3",
    description="Build a data visualization dashboard with simple snippets of python code",
    license="MIT",
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords=["dtale", "visualization", "pandas"],
    author="Phillip Dupuis",
    author_email="phillip_dupuis@alumni.brown.edu",
    url="https://github.com/phillipdupuis/dtale-desktop",
    install_requires=install_requires,
    packages=find_packages(),
    package_data={
        "dtale_desktop": [
            "frontend/build/*",
            "frontend/build/static/css/*",
            "frontend/build/static/js/*",
            "frontend/build/themes/*",
            "templates/*",
        ]
    },
    entry_points={
        "console_scripts": [
            "dtaledesktop = dtale_desktop.app:run",
            "dtaledesktop_open_browser = dtale_desktop.subprocesses:open_browser",
            "dtaledesktop_profile_report = dtale_desktop.subprocesses:build_profile_report",
        ]
    },
    classifiers=classifiers,
)
