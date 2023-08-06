Fluid JSON-RPC
==============

Turn any function _signatures_ into JSON-RPC requests.

``` python
import requests

from fluid import JSONRPC


dispatcher = JSONRPC(url="")
dispatcher.session = requests.Session()

@dispatcher.dispatch(name="methodName")
def method_name(foo: str, bar: int):
    pass

...

result = method_name(foo="value", bar=1)

"""
The call above will make a POST request on the URL with the parameters passed:

{
  "id": 0,
  "jsonrpc": "2.0",
  "method": "methodName",
  "params": {
      "foo": "value",
      "bar": 1
  }
}
"""
```