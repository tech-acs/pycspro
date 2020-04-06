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
The library is simple to use and has only two classes. DictionaryParser and CaseParser.
There is also a medium article that explains, in considerable detail, how it works. You can find it here:

[Working With CSPro Data Using Python (Pandas)](https://medium.com/@nahomt/working-with-cspro-data-using-python-pandas-9a6161b84ffa?sk=5e19e932f9090a21432c716aac0e7401)

### DictionaryParser
This class receives a raw dictionary text and parses it into a Python dictionary which we can then manipulate to acomplish various tasks.

#### parse()
This method accepts the contents of a dictionary file (.dcf) and returns a dictionary object, which is basically a nested Python dictionary.
```python
from pycspro import DictionaryParser

raw_dictionary = open('CensusDictionary.dcf', 'r').read()
dictionary_parser = DictionaryParser(raw_dictionary)
parsed_dictionary = dictionary_parser.parse()
print(json.dumps(parsed_dictionary, indent=4))
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
This method accepts a record name and returns a dictionary where keys are the item names and the values are the item labels for all the items within the given record.
```json
{
    'H01_TYPE': 'Type of housing',
    'H02_WALL': 'Wall type',
    'H03_ROOF': 'Roof type',
    'H04_FLOOR': 'Floor type',
    'H05_ROOMS': 'Number of rooms',
    'H06_TENURE': 'Tenure'
}
```
This is useful for replacing the column labels in the Data Frame.
```python
housing = dfs['HOUSING']
housing.rename(columns = dictionary_parser.get_column_labels('HOUSING'))
```

#### get_value_labels()
This method accepts a record name and returns a dictionary where keys are the item names and the values are yet another dictionary. This dictionaries key-value paris are all the possible values and their respective labels.
```json
{
    'P02_REL': {1: 'Head', 2: 'Spouse', 3: 'Child', 4: 'Parent', 5: 'Other', 6: 'Nonrelative', 9: 'Not Reported'},
    'P03_SEX': {1: 'Male', 2: 'Female'}
}
```

This can be used to replace values by their more meaningful labels in a Data Frame.
```python
person = dfs['PERSON']
person.replace(dictionary_parser.get_value_labels('PERSON'))
```

### CaseParser
The CaseParser class is responsible for cutting up raw CSPro cases into tables by using a parsed dictionary (DictionaryParser). It produces a nested dictionary where each record is yet another dictionary. The resulting format is well suited to be converted into a Pandas Data Frame by using the from_dict method of the pandas DataFrame class.

During instantiation, you can also pass in a cutting_mask to the CaseParser class to specify only the columns (items) you are interested in. This can be useful when there are a large number of items in a record.
```python
cutting_mask = {
    'QUEST': ['PROVINCE', 'DISTRICT'],
    'PERSON': ['P03_SEX', 'P04_AGE', 'P11_LITERACY', 'P15_OCC'],
    'HOUSING': ['H01_TYPE', 'H05_ROOMS', 'H07_RENT', 'H08_TOILET', 'H13_PERSONS']
}
case_parser = CaseParser(parsed_dictionary, cutting_mask)
```

#### parse()
The parse method receives a list of cases and returns a nested dictionary of records.
```python
import pandas as pd
from pycspro import CaseParser

case_parser = CSProCaseParser(parsed_dictionary)
parsed_cases = case_parser.parse(cases) # where cases is a list of CSPro cases

# parsed_cases will be Python dictionary where the keys are the record names
# and values would be a dictionary with columns as keys and column values as a Python list
for table_name, table in parsed_cases.items():
    pd.DataFrame.from_dict(table)
```

## Live Demo
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/amestsantim/pycspro-example/master?filepath=Using%20pyCSPro.ipynb)

There is a Jupyter Notebook on Binder (great project!) that you can play with, in a live environment (in your browser) and see how easy it is to use this library. Please, take it for a spin!

## Syntax Checking
This library uses a finite state machine to check the syntax of dictionaries. However, in the current version, some simplifying assumptions were made.
These are:
Dictionaries are assumed to have only a single Level
SubItems are not considered and will cause an error if present

## Performance
When reading and loading cases directly from CSWeb's MySQL database, you should be passing in to the CaseParser about 50,000 cases at a time and then converting the result into a Pandas DataFrame. In the next iteration, send in another 50,000 cases and on return, convert to a DataFrame and append to the previous DataFrame. That way, you can grow your DataFrame to a large size without consuming a lot of memory.

## To Dos
Some edge cases such as SPECIAL values etc might not have been handled. If you run in to such edge cases, please submit an issue (or even better, a pull request) and hopefully, we will have them ironed out soon enough!

## License
MIT