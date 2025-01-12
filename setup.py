from setuptools import setup, find_packages

setup(
    name="metaflow-diff",
    version="0.1.7",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "metaflow-diff=metaflow_diff.metaflow_diff:cli",
        ],
    },
    install_requires=[
        "metaflow",
        "click"
    ],
    author="Ville Tuulos",
    author_email="ville@outerbounds.co",
    description="See and apply diffs between the current working directory and a Metaflow run",
    python_requires=">=3.9",
    long_description = open("README.md").read(),
    long_description_content_type='text/markdown'
)
