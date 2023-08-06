## jSona

##### JSON Format handler with bulit-in json module

Error tolerances are added to bulit-in json module.

Because those kind of works are really annoying.

---


### Installation

```code
pip3 install jSona-master/
```

---

### Projects

jSona have two major functions

* load : Loads data from json format file.

* save : Saves to json format file.

* loads, dumps : Equals loads and dumps functions in json module.

---

### Examples

* Script

```python
# from jSona import save, load
from pprint import pprint as pp
from jSona import save, load

sample_data = {'hello':['world', 'everyone~']}
save("sample.json", sample_data, cry=True)

load_data = load("sample.json", cry=True)
pp(load_data)
```

* Outputs

```python
SAVE SUCCESS TO [ sample.json ]
LOAD SUCCESS FROM [ sample.json ]
{'hello': ['world', 'everyone~']}
```

---


### Notices

###### Unauthorized distribution and commercial use are strictly prohibited without the permission of the original author and the related module.
