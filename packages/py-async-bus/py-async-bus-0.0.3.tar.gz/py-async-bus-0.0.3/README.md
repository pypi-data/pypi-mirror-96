# Py Async Bus

A simple async event bus in Python

Installing
----------

Install with **pip**:

```sh
$ pip install py-async-bus
```


Usage
----------

```py
from async_bus import EventBus

bus = EventBus()

@bus.subscribe('event_name')
async def subscriber(param):
    print(param)


bus.emit('event_name', param='test_param')
```

### Disable subscriber

If you want to disable subscribers while testing for example, you can set the env `ASYNC_BUS_ENABLE_SUBSCRIBERS` to false.

```sh
$ ASYNC_BUS_ENABLE_SUBSCRIBERS=false python -m unittest
```

Tests
----------
```sh
$ python -m unittest
```
