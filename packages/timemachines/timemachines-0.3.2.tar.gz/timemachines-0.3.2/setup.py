import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="timemachines",
    version="0.3.2",
    description="Evaluation and standardization of popular time series and tuning packages.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/microprediction/timemachines",
    author="microprediction",
    author_email="pcotton@intechinvestments.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["timemachines",
              "timemachines.skaters",
              "timemachines.skaters.divine",
              "timemachines.skaters.dlm",
              "timemachines.skaters.flux",
              "timemachines.skaters.pmd",
              "timemachines.skaters.proph",
              "timemachines.skaters.simple",
              "timemachines.skatertools",
              "timemachines.skatertools.comparison",
              "timemachines.skatertools.components",
              "timemachines.skatertools.composition",
              "timemachines.skatertools.data",
              "timemachines.skatertools.evaluation",
              "timemachines.skatertools.tuning",
              "timemachines.skatertools.utilities",
              "timemachines.skatertools.visualization"],
    test_suite='pytest',
    tests_require=['pytest','microprediction'],
    include_package_data=True,
    install_requires=["wheel","pathlib","numpy>=1.19.5","pandas","importlib-metadata>=1.7.0",
                      "microconventions>0.5.0","getjson","convertdate","lunarcalendar","holidays",
                      "sklearn","scipy","funcy","tdigest",
                      "divinity","pmdarima","pydlm","tdigest","fbprophet",
                      "momentum","humpday"],
    entry_points={
        "console_scripts": [
            "timemachines=timemachines.__main__:main",
        ]
    },
)
