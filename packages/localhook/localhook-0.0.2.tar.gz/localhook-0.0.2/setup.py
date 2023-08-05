from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name="localhook",
    version="0.0.2",
    url="https://github.com/kekayan/localhook",
    author="Kekayan Nanthakumar",
    author_email="kekayan.nanthakumar@gmail.com",
    description="Receive webhooks to your Terminal",
    long_description=long_description,
    long_description_content_type='text/markdown', 
    packages=find_packages(),
    py_modules=["localhook"],
    install_requires=[
        "pyngrok>=5.0.2",
        "Flask==1.1.2",
        "PyYAML>=5.3.1",
        "rich",
        "waitress",
        "click",
    ],
    entry_points="""
            [console_scripts]
            localhook=localhook:start
    """,
)
