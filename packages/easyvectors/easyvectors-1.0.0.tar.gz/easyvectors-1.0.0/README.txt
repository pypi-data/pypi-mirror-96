This module makes working with vectors (or other tuple-ish things) much more convinient. \n
It introduces a new datatype (actually a class) called Vector which is a lot like tuples. \n \n
These vectors can contain from 1 to 4 dimensions (x, y, z, t) and these can be called and changed easily. \n
The addition (and subtraction, multiplication and so on) of a vector, integer, float or list to another vector is as easy as working with integers and floats. See below, or example.py for examples. \n
No more annoying iteration and inefficient code whilts working with tuples thanks to this module! \n

```
>>> from vectors import *
>>> myvector = Vector(1,2,3)
>>>
>>> print(myvector)
(1, 2, 3)
>>> print(myvector.x)
1
>>> print(myvector[0])
1
>>> print(myvector.type)
'vector3'
>>> print(vtype(myvector))
'vector3'
>>>
>>> myvector += 1
(2, 3, 4)
>>>
>>> othervector = Vector(4, 5, 6)
>>>
>>> myvector + othervector
(6, 7, 10)
>>> myvector / [3, 2, 0.5]
(2, 3.5, 20)
>>>
>>> mytuple = unv(myvector)
>>> print(mytuple, type(mytuple))
(2, 3.5, 20), <class 'tuple'>
```

