# standpy
Cross-Platform Python Standby Lock

## Usage
```python
from standpy import StandbyLock, standby_lock

## For code blocks
with StandbyLock():
    ## do something
    do_something()
## System waited without going idle.

## In function calls
@standby_lock
def foo(*args, **kwargs):
    return bar(*args, **kwargs)

## System will wait for `foo` to return.
foo()
```