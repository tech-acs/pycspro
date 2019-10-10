# pycspro
Python bindings for [Jsonic](https://github.com/rohanrhu/jsonic) JSON reader library.

## Install
PIP:
```bash
pip install pycspro
```

Git:
```bash
git clone https://github.com/amestsantim/pycspro
cd pycspro
python setup.py install
```

## Usage

### Import
```python
import jsonic
```

### Types and Functions

#### Function: from_file
Read file and returns `Jsonic()` object.
```python
root = jsonic.from_file("file.json")
```

#### Type: Jsonic
```python
root = jsonic.Jsonic("[1, 2, 3, 4]")
```

##### Member: Jsonic.type
Type member is useable for checking object and array types. Except object and array types, you will get regular python `str`, `float`, `bool` or `jsonic.Null` object.

###### Type Checking
###### Types
`jsonic.TYPE_OBJECT`<br>
`jsonic.TYPE_ARRAY`

`Jsonic.type` is useable for objects or arrays. Object and array values returns as `Jsonic()` objects. Null values returns as `Jsonic.Null` object. Otherwise it returns as regular python types.

##### Member: Jsonic.version
Version of python-jsonic.

##### Member: Jsonic.json
JSON String.

##### Type: Jsonic.Null
JSON Null type.

##### Method: root()
Returns JSON root's value if `root.type` is not an array or object. Otherwise it returns None.
```python
root = jsonic.Jsonic("1234")
print(root.root()) # 1234

root = jsonic.Jsonic("\"foo\"")
print(root.root()) # foo

root = jsonic.Jsonic("true")
print(root.root()) # True

root = jsonic.Jsonic("null")
print(root.root()) # jsonic.Null

root = jsonic.Jsonic("{}")
print(root.root()) # None
print(root.type) # jsonic.TYPE_OBJECT

root = jsonic.Jsonic("[]")
print(root.root()) # None
print(root.type) # jsonic.TYPE_ARRAY
```

#####  Method: len()
Gets length of array.

#####  Method: key(key)
Returns the key's value.

#####  Method: item(index)
Returns item of an index on array.

#### Method: iterItem(index=0)
Iterates array item from last iterated item times index.

```python
root = jsonic.Jsonic("[1, 2, 3, 4]")
print(array.iterItem()) # 1
print(array.iterItem()) # 2
print(array.iterItem(1)) # 4
print(array.iterItem()) # None
array.reset()
print(array.iterItem()) # 1
```

#### Method: iterKey(key)
Iterates object key from last iterated object.
```python
root = jsonic.Jsonic("{\"a\": 1, \"b\": 2, \"c\": 3, \"d\": 4}")
print(array.iterKey("a")) # 1
print(array.iterKey("b")) # 2
print(array.iterKey("c")) # 3
print(array.iterKey("b")) # None
array.reset()
print(array.iterKey("b")) # 2
```

#### Method: reset()
Resets iteration current.

## Example
An example for reading JSON data

```python
import jsonic

root = jsonic.from_file("heroes.json")

print("Root Type: %d" % root.type)
print("Squad: %s" % root.iterKey("squadName"))
print("Hometown: %s" % root.iterKey("homeTown"))
print("Formed: %d" % root.iterKey("formed"))
print("Active: %d" % root.iterKey("active"))

members = root.iterKey("members")

print("Members: (%d total)" % members.len())
while True:
    member = members.iterItem()
    if not member: break

    name = member.iterKey("name")
    age = member.iterKey("age")
    powers = member.iterKey("powers")

    print("\tName: %s" % name)
    print("\tAge: %s" % age)
    print("\tPowers (%d total):" % powers.len())
    while True:
        power = powers.iterItem()
        if not power:break

        print("\t\t%s" % power)

    print()
```

Example JSON (heroes.json):
```json
{
    "squadName": "Super hero squad",
    "homeTown": "Metro City",
    "formed": 2016,
    "secretBase": "Super tower",
    "active": true,
    "members": [
    {
        "name": "Molecule Man",
        "age": 29,
        "secretIdentity": "Dan Jukes",
        "powers": [
            "Radiation resistance",
            "Turning tiny",
            "Radiation blast"
        ]
    },
    {
        "name": "Madame Uppercut",
        "age": 39,
        "secretIdentity": "Jane Wilson",
        "powers": [
            "Million tonne punch",
            "Damage resistance",
            "Superhuman reflexes"
        ]
    },
    {
        "name": "Eternal Flame",
        "age": 1000000,
        "secretIdentity": "Unknown",
        "powers": [
            "Immortality",
            "Heat Immunity",
            "Inferno",
            "Teleportation",
            "Interdimensional travel"
        ]
    }
    ]
}
```

## Syntax Checking
This library does not check JSON syntax, so you may get `SIGSEGV` or maybe infinite loops for **corrupt JSONs**. Likewise in some cases of corrupt JSONs, it would work as properly.

## Performance
There are some example JSONs and reading examples in `examples/` folder for profiling the performance.

## C Library
You can use [Jsonic](https://github.com/rohanrhu/jsonic) JSON reader library for C/C++.

## License
MIT