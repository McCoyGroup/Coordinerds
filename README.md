# Psience

Psience is a set of core scientific packages written by the McCoy group for the McCoy group to handle interesting scientific problems, like DVR, managing potential and dipole surfaces, VPT2, normal mode analysis, etc.

We're working on [documenting the package](https://mccoygroup.github.io/References/Documentation/Psience.html), but writing good documentation takes more time than writing good code.

### Installation & Requirements

Psience is written in pure python.
We make use of `numpy`, `scipy`, and `matplotlib`, as well as our `McUtils` package, but have worked to avoid any dependencies beyond those four.

It is unlikely that Psience will even find its way onto PyPI, so the best thing to do is install from GitHub via `git clone`. The `master` branch _should_ be stable. Other branches are intended to be development branches. 

### Contributing

If you'd like to help out with this, we'd love contributions.
The easiest way to get started with it is to try it out.
When you find bugs, please [report them](https://github.com/McCoyGroup/Psience/issues/new?title=Bug%20Found:&labels=bug). 
If there are things you'd like added [let us know](https://github.com/McCoyGroup/Psience/issues/new?title=Feature%20Request:&labels=enhancement), and we'll try to help you get the context you need to add them yourself.
One of the biggest places where people can help out, though, is in improving the quality of the documentation.
As you try things out, add them as examples, either to the [main page](https://mccoygroup.github.io/References/Documentation/Psience.html#examples) or to a [child page](https://mccoygroup.github.io/References/Documentation/Psience/Molecools/Molecule/Molecule.html#examples).
You can also edit the docstrings in the code to add context, explanation, argument types, return types, etc.