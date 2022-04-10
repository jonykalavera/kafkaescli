
You would like to contribute to `kafkaescli`, thank you very much!

Here are a few tips and guidelines to help you in the process.

# State of mind

This is an open-source tool that I maintain during my free time, which I do not have much:

* I do what I can to give you some feedback (either a direct response or a message about my unavailability)
* everybody does her best while communicating but misunderstanding happens often when discussing asynchronously with textual message; let's speak friendly and welcome reformulation requests the best we can
* English is the language that we shall use to communicate, let's all be aware that English may not be our native language.

# Process

1. check in the issues (in the closed ones too) if the problem you are facing has already been mentionned, contribute to existing and matching issues before creating a new one
1. create a new issue if an existing one does not exist already and let's discuss the new feature you request or the bug you are facing.
Details about the way to reproduce a bug helps to fix it
1. fork the project
1. implement the feature or fix the bug.
Corresponding unit tests must be added or adapted according to what was discussed in the issue
1. create a pull-request and notify the library contributors (see the [Contributions](README.md#contributions) section)

All text files are expected to be encoded in UTF-8.

# Code practices

It takes time to write comprehensive guidelines.
To save time (my writing time and your reading time), I tried to make it short so my best advice is _go have a look at the production and test codes and try to follow the conventions you draw from what you see_ 🙂

## Unit tests

[[warning|TODO]]
| write initial tests

Pull requests must come with unit tests, either new ones (for feature addtitions), changed ones (for feature changes) or non-regression ones (for bug fixes).
Have a look at the [tests](tests/) folder and the ~~existing~~ to-be-written automated (not) tests scripts to see how they are organized:

* within the `tests` folder, the subfolders' structure follows the one of the `kafkaescli` production code
* it helps finding the best location to write the unit tests, and where to find the ones corresponding to a feature you want to understand better

This project ~~uses~~ will use the [pytest](https://docs.pytest.org) framework to run the whole tests suit.
It provides useful features like the parametrization of unit test functions and local mocking for example.

## Code styling

``` python
python_version = '3.10+' (could work with others. haven't tested)
# Use pythonesque features (list or dict comprehensions, generators) when possible and relevant.
# Use **type annotations**.
f'use f-strings to format strings, kafkaescli use Python {python_version}'
```

### Code formatting

use `black`. that's it.

#### Imports

use `isort`. that's it

I am looking forward to providing the linting settings and checks corresponding to these practices.

---

This document was ~~inspired~~ shamesly stolen from [py2puml](https://github.com/lucsorel/py2puml/). also some of the readme. Go check it out.
