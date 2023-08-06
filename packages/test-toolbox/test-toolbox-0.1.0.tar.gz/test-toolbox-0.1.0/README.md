# Python Test Toolbox

A toolbox for testing Python code.

Comes in handy when testing asynchronous code, such as database or network access for example.

## Usage

Use `retry_until_returns_value(..)` in the following way:

```python
from test_toolbox import retry_until_returns_value


def do_something() -> bool:
    import random
    true_or_false = bool(random.getrandbits(1))
    return true_or_false


retry_until_returns_value(do_something, True, timeout=10)
```

Use `retry_until_pass_without_exception(..)` in the following way:

```python
from test_toolbox import retry_until_pass_without_exception


def do_something() -> None:
    import random
    is_error = bool(random.getrandbits(1))
    if is_error:
        raise Exception("Something went wrong!")


retry_until_pass_without_exception(do_something, timeout=10)
```
