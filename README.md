# pyCSPro
Python library for parsing CSPro dictionaries and cases.

## Install
pip:
```bash
pip install pycspro
```

git:
```bash
git clone https://github.com/amestsantim/pycspro
cd pycspro
python setup.py install
```

## Usage

### DictionaryParser
This class receives a raw dictionary text and parses it into a Python dictionary which we can then manipulate to acomplish various tasks.

#### parse()
Read dictionary file (.dcf) and returns a dictionary object, which is basically a nested Python dictionary.
```python
from pycspro import DictionaryParser

raw_dictionary = open('CensusDictionary.dcf', 'r').read()
dictionary_parser = DictionaryParser(raw_dict)
parsed_dictionary = dictionary_parser.parse()
print(json.dumps(parsed_dict, indent=4))
```

```json
{
    "Dictionary": {
        "Name": "CEN2000",
        "Label": "Popstan Census",
        "Note": "",
        "Version": "CSPro 7.2",
        "RecordTypeStart": 1,
        "RecordTypeLen": 1,
        "Positions": "Relative",
        "ZeroFill": true,
        "DecimalChar": false,
        "Languages": [],
        "Relation": [],
        "Level": {
            "Name": "QUEST",
            "Label": "Questionnaire",
            "Note": "",
            "IdItems": [
                {
                    "Name": "PROVINCE",
                    "Label": "Province",
                    "Note": "",
                    "Len": 2,
                    "ItemType": "Item",
                    "DataType": "Numeric",
                    "Occurrences": 1,
                    "Decimal": 0,
                    "DecimalChar": false,
                    "ZeroFill": true,
                    "OccurrenceLabel": [],
                    "Start": 2,
                    "ValueSets": [
                        {
                            "Name": "PROV_VS1",
                            "Label": "Province",
                            "Note": "",
                            "Value": [
                                "1;Artesia",
                                "2;Copal",
                                "3;Dari",
                                "4;Eris",
                                "5;Girda",
                                "6;Hali",
                                "7;Kerac",
                                "8;Lacuna",
                                "9;Laya",
                                "10;Lira",
                                "11;Matanga",
                                "12;Patan",
                                "13;Rift",
                                "14;Terra",
                                "15;Tumar"
                            ]
                        }
                    ]
                },
                ...
```

#### get_column_labels()

#### get_value_labels()

### CaseParser
Describe

#### parse()
Describe
```python
import pandas as pd
from pycspro import CaseParser

case_parser = CSProCaseParser(parsed_dictionary)
parsed_cases = case_parser.parse(cases) # where cases is a list of CSPro cases
# parsed_cases will be Python dictionary where the keys are the record names
# and values would be a dictionary with columns as keys and column values as a Python list
```

## Syntax Checking
This library uses a finite state machine to check the syntax of dictionaries. However, in the current version, some simplifying assumptions were made.
These are:
Dictionaries are assumed to have only a single Level
SubItems are not considered and will cause an error if present

## Performance
When reading and loading cases directly from CSWeb's MySQL database, you should be passing in to the CaseParser about 50,000 cases at a time and then converting the result into a Pandas DataFrame. In the next iteration, send in another 50,000 cases and on return, convert to a DataFrame and append to the previous DataFrame. That way, you can grow your DataFrame to a large size without consuming a lot of memory.

## License
MIT