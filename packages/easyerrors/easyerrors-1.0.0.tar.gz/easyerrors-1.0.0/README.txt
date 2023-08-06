This module allows you to easily test simple functions. All errors will be catched and showed to you gracefully.

Note that this module is incredibly basic and does not work with any kind of indented code, so e.g. for loops are not an option.

code examples:
```
>>> from easyerrors import test
>>> 
>>> @test
>>> def tryout(msg, num):
... 	print(msg, num)
...
>>> tryout('hey', 3)

Testing code inside function 'tryout':

-------- Test started! --------

>>> print(msg, num,)
hey 3


-------- Test ended! --------
```	

```
>>> from easyerrors import test
>>> 
>>> @test
>>> def tryout(msg, num):
... 	print(msg, num)
... 	print(invalidargument)
...
>>> tryout('hey', 3)

Testing code inside function 'tryout':

-------- Test started! --------

>>> print(msg, num)
hey 3

>>> print(incorrectargument)
Error: name 'incorrectargument' is not defined


-------- Test ended! --------

 Errors found:
  - name 'incorrectargument' is not defined
  
```