import setuptools

#from setuptools.config import read_configuration
#conf_dict = read_configuration("C:/Program Files/Ramz Editions/Packaaging Examples/Aleatoryous 3/0.2/setup.cfg")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aleat3",
    version="0.2a3",
    author="Diego Ramirez",
    author_email="dr01191115@gmail.com",
    description="An aleatory syntaxes package. Third generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development"
    ],
    keywords="aleatory dice coin roulette python aleat",
    python_requires='>=3.6, <4',
    entry_points={
        "console_scripts": [
            "aleat3=aleat3.main:main",
            "aleat3_coin=aleat3.main:coin",
            "aleat3_dice=aleat3.main:dice",
            "aleat3_roulette=aleat3.main:roulette"
        ]
    },
    install_requires=["wheel>=0.36.0",
                      "setuptools>=50.3.1",
                      "pip>=21.0"]
)
