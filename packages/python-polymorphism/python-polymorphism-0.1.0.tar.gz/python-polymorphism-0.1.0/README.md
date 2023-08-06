# What this repository contains
#### A simple utility library that allow you to use OOP Like Polymorphic Function in python

## Installation: 

install the package
```
pip install python-polymorphism
```

## How to use

In a Class module

```python
from python_polymorphism import Poly

polymorphic = Poly()
class PolyClass():
    @polymorphic.this()
    def test_poly_fn(self, my_first_test_argument):
        return 'my_first_test_argument'
    
    @polymorphic.this()
    def test_poly_fn(self, my_second_test_argument):
        return 'my_second_test_argument'


print(PolyClass().test_poly_fn(my_first_test_argument=1)) # => 'my_first_test_argument'
print(PolyClass().test_poly_fn(my_second_test_argument=1)) # => 'my_second_test_argument'
```

### Constraints
* It works on python class only;
* The polymorphed function has to be called with kwargs;
* Default parameters do not help differentiate one function from another.
 