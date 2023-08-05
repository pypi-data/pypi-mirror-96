
About
-----

Attributee is a Python 3 library for declarative object initialization. Input arguments are defined as class attributes and are automatically processed when creating an object. It is in a way similar to Django ORM or some other ORMs, but the main purpose of this library is to simplify parsing input arguments to object constructors. 

The library is a work-in-progress, I am adding stuff that I consider useful for my other projects.

Simple use case
---------------

```
from attributee import Attributee, String, Float

class Model(Attributee):

    # Simply list the attributes of the object ...

    name = String(default="noname")
    value1 = Float()
    value2 = Float(default=0, val_min=-10, val_max=10)

    # ... no constructor needed


# default arguments assigned
model1 = Model(value1=10)

# automatic type conversion where possible
model2 = Model(value1=10, value2="5")

```

Documentation
-------------

I am working on it.

Authors
-------

Luka Čehovin Zajc

License
-------

The library is available under the [simplified BSD license](LICENSE.md).