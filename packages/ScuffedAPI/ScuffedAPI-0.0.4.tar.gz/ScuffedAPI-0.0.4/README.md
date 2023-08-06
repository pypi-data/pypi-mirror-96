# ScuffedAPI
Python wrapper for ScuffedAPI. Modified To Work For ScuffedAPI

[![Requires: Python 3.x](https://img.shields.io/pypi/pyversions/ScuffedAPI.svg)](https://pypi.org/project/ScuffedAPI/)
[![ScuffedAPI Version: 0.0.3](https://img.shields.io/pypi/v/ScuffedAPI.svg)](https://pypi.org/project/ScuffedAPI/)

## Installing:
### Synchronous:
Windows: ``py -3 -m pip install ScuffedAPI``<br>
Linux/macOS: ``python3 -m pip install ScuffedAPI``

### Asynchronous:
Windows: ``py -3 -m pip install AsyncScuffedAPI``<br>
Linux/macOS: ``python3 -m pip install AsyncScuffedAPI``

## Example:
```
import ScuffedAPI

API = ScuffedAPI.getSkinId("storm")
print(API)
```

This would output:<br>
```Playlist_DADBRO_Squads```
