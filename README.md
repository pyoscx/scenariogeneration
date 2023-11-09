![Python](https://github.com/pyoscx/scenariogeneration/actions/workflows/python.yml/badge.svg?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# scenariogeneration

The Python scenariogeneration package is a collection of libraries for generating OpenSCENARIO (.xosc) and OpenDRIVE (.xodr) XML files.

This combined package (which includes the former pyoscx, pyodrx) can be used to jointly generate OpenSCENARIO based scenarios with interlinked OpenDRIVE based road network maps. Nevertheless, it is still possible to separately generate OpenSCENARIO or OpenDRIVE files by using only a subset of the provided functionality.

The package consists of the __scenario_generator__ module and two Python subpackages, __xosc__ (OpenSCENARIO) and __xodr__ (OpenDRIVE), together with some support functionality for auto generation with parametrization as well as easy viewing with [esmini](https://github.com/esmini/esmini).

The user documentation can be found [here](https://pyoscx.github.io/), the API documentation [here](https://pyoscx.github.io/scenariogeneration/index.html) and the change log in [release_notes.md](https://github.com/pyoscx/scenariogeneration/blob/main/release_notes.md)

Please note that this is not an official implementation of either OpenSCENARIO or OpenDRIVE.

## Coverage

As of V0.11.0, the coverage of the modules varies:
- The xosc module has full coverage of OpenSCENARIO V1.0.0, and most of V1.1.0 and V1.2.0, if something is missing please raise an issue or make a pull request.
- The xodr module has coverage of basic roads, junctions, signals, and objects, based on OpenDrive (V 1.7.1).

For more details se xodr_coverage.txt and xosc_missing_features.txt

## Getting Started

```
pip install scenariogeneration
```
then run any of the examples provided

### Prerequisites

Been tested with Python >3.6.9.
With Python versions <3.7 the order of certain xml-elements might not be the same between generations.

### Installing

```
pip install scenariogeneration
```

## Usage

Please see the user guide for more information: https://pyoscx.github.io/

### Running with esmini

Esmini can be used to visualize the generated scenarios. Visit https://github.com/esmini/esmini and follow the "Binaries and demos" section.
Your scenarios can be visualized directly by making use of *esmini* in the following way:

```
from scenariogeneration import esmini

def Scenario(ScenarioGenerator): ...


if __name__ == "__main__":
    s = Scenario()

    esmini(s,esminipath ='path to esmini', index_to_run = 'first')
```
where *index_to_run* can be 'first', 'random', 'middle' or an integer, and esmini will run that scenario/road for you.

## Related work

### esmini

[esmini](https://github.com/esmini/esmini) is a basic OpenSCENARIO player

### clothoids

[pyclothoids](https://github.com/phillipd94/pyclothoids), used for construction and optimization of clothoids geometries

### blender implementation

[blender + scenariogeneration](https://github.com/johschmitz/blender-driving-scenario-creator)

## Authors

See [AUTHORS](https://github.com/pyoscx/scenariogeneration/blob/main/AUTHORS) file

## Data formats

The wrappers is based on the OpenSCENARIO and OpenDRIVE standards.

[OpenDRIVE](https://www.asam.net/standards/detail/opendrive/)

describes the static content of a scenario, like the road, lanes, signs and so on.

[OpenSCENARIO](https://www.asam.net/standards/detail/openscenario/)

describes the dynamic content on top of a road network, e.g. traffic maneuvers, weather conditions, and so on.

