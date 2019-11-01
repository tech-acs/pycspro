from transitions import Machine
import configparser
from collections import OrderedDict
import json


class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(OrderedDict, self).__setitem__(key, value)
    def keys(self):
        return super(OrderedDict, self).keys()


class DictionaryBuilder:
    ATTRIBUTE_TYPES = {
        'to_int': {'Start', 'Len', 'RecordTypeStart', 'RecordTypeLen', 'MaxRecords', 'RecordLen', 'Occurrences'}, 
        'strip_quotes_str': {'Name', 'Label', 'Note', 'Version', 'Positions', 'RecordTypeValue', 'ItemType', 'DataType'},
        'word_to_bool': {'ZeroFill', 'DecimalChar', 'Required'},
    }
    
    def __init__(self):
        self.tree = {}
        self.is_built = False
        
    def word_to_bool(self, arg):
        return arg == 'Yes'

    def pass_through(self, arg):
        return arg

    def strip_quotes_str(self, arg):
        return str(arg.strip("'"))
    
    def to_int(self, arg):
        return int(arg)

    def get_casting_function(self, key):
        for type, pool in self.ATTRIBUTE_TYPES.items():
            if key in pool:
                return type
            else:
                continue
        return 'pass_through'

    def flatten_and_cast_values(self, attributes):
        if attributes == None:
            return None
        else:
            attribs = []
            for attribute in attributes:
                key, value = attribute
                if (len(value) == 1 and key != 'Value'):
                    attribs.append(([key, getattr(self, self.get_casting_function(key), self.pass_through)(value[0])]))
                else:
                    attribs.append(attribute)
            return attribs
    
    def add_section(self, section_received, attributes):
        getattr(self, section_received, self.pass_through)(self.flatten_and_cast_values(attributes))
        
    # attributes will come as a list of tuples [('key', [values])]
    def dictionary_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Version': '',
            'RecordTypeStart': 1,
            'RecordTypeLen': 0,
            'Positions': 'Relative',
            'ZeroFill': True,
            'DecimalChar': False,
            'Languages': [],
            'Relation': [],
        }
        section.update(attributes)
        self.tree['Dictionary'] = section
        
    def level_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
        }
        section.update(attributes)
        self.tree['Dictionary']['Level'] = section

    def iditems_received(self, attributes):
        self.tree['Dictionary']['Level']['IdItems'] = []
        
    def item_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Len': 0,
            'ItemType': 'Item',
            'DataType': 'Numeric',
            'Occurrences': 1,
            'Decimal': 0,
            'DecimalChar': False,
            'ZeroFill': False,
            'OccurrenceLabel': [],
        }
        section.update(attributes)
        #self.tree['Dictionary']['Level']['IdItems'].append({'Item': section})
        self.tree['Dictionary']['Level']['IdItems'].append(section)
        
    def valueset_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Value': [],
        }
        section.update(attributes)
        #value_sets = self.tree['Dictionary']['Level']['IdItems'][-1]['Item'].get('ValueSets', [])
        value_sets = self.tree['Dictionary']['Level']['IdItems'][-1].get('ValueSets', [])
        value_sets.append(section)
        #self.tree['Dictionary']['Level']['IdItems'][-1]['Item']['ValueSets'] = value_sets
        self.tree['Dictionary']['Level']['IdItems'][-1]['ValueSets'] = value_sets
        
    def record_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'RecordTypeValue': '',
            'Required': False,
            'MaxRecords': 1,
            'RecordLen': 0,
            'OccurrenceLabel': []
        }
        section.update(attributes)
        records = self.tree['Dictionary']['Level'].get('Records', [])
        records.append(section)
        self.tree['Dictionary']['Level']['Records'] = records
        
    def record_item_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Len': 0,
            'ItemType': 'Item',
            'DataType': 'Numeric',
            'Occurrences': 1,
            'Decimal': 0,
            'DecimalChar': False,
            'ZeroFill': False,
            'OccurrenceLabel': [],
        }
        section.update(attributes)
        #items = self.tree['Dictionary']['Level']['Records'][-1]['Record'].get('Items', [])
        items = self.tree['Dictionary']['Level']['Records'][-1].get('Items', [])
        items.append(section)
        self.tree['Dictionary']['Level']['Records'][-1]['Items'] = items
        
    def record_valueset_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Value': [],
        }
        section.update(attributes)
        value_sets = self.tree['Dictionary']['Level']['Records'][-1]['Items'][-1].get('ValueSets', [])
        value_sets.append(section)
        self.tree['Dictionary']['Level']['Records'][-1]['Items'][-1]['ValueSets'] = value_sets

    def completed(self, attributes):
        self.is_built = True

class CSProDictionary(object):
    def __init__(self):
        self.builder = DictionaryBuilder()
        
    def build_dictionary(self, section, section_items):
        self.builder.add_section(self.state, section_items)

class DictionaryParser:
    def __init__(self, raw_dictionary):
        self.parsed_dictionary = None
        # If present, remove BOM.
        # BOM is the character code (such as U+FEFF) at the beginning of a data stream
        # that is used to define the byte order and encoding form.
        # https://www.tutorialspoint.com/Unicode-Byte-Order-Mark-BOM-character-in-HTML5-document
        self.raw_dictionary = raw_dictionary.replace('\ufeff', '').replace('\u00ef', '').replace('\u00bb', '').replace('\u00bf', '')
        
    def parse(self):
        model = CSProDictionary()
        states = ['empty', 'dictionary_received', 'level_received', 'iditems_received', 'item_received', 
                  'valueset_received', 'record_received', 'record_item_received', 'record_valueset_received', 'completed']
        transitions = [
            {'trigger': 'Dictionary', 'source': 'empty', 'dest': 'dictionary_received'},
            {'trigger': 'Level', 'source': 'dictionary_received', 'dest': 'level_received'},
            {'trigger': 'IdItems', 'source': 'level_received', 'dest': 'iditems_received'},
            {'trigger': 'Item', 'source': 'iditems_received', 'dest': 'item_received'},
            {'trigger': 'Item', 'source': 'item_received', 'dest': 'item_received'},
            {'trigger': 'ValueSet', 'source': 'item_received', 'dest': 'valueset_received'},
            {'trigger': 'ValueSet', 'source': 'valueset_received', 'dest': 'valueset_received'},
            {'trigger': 'Item', 'source': 'valueset_received', 'dest': 'item_received'},
            {'trigger': 'Record', 'source': 'valueset_received', 'dest': 'record_received'},
            {'trigger': 'Record', 'source': 'item_received', 'dest': 'record_received'},
            {'trigger': 'Item', 'source': 'record_received', 'dest': 'record_item_received'},
            {'trigger': 'Item', 'source': 'record_item_received', 'dest': 'record_item_received'},
            {'trigger': 'ValueSet', 'source': 'record_item_received', 'dest': 'record_valueset_received'},
            {'trigger': 'ValueSet', 'source': 'record_valueset_received', 'dest': 'record_valueset_received'},
            {'trigger': 'Item', 'source': 'record_valueset_received', 'dest': 'record_item_received'},
            {'trigger': 'Record', 'source': 'record_item_received', 'dest': 'record_received'},
            {'trigger': 'Record', 'source': 'record_valueset_received', 'dest': 'record_received'},
            {'trigger': 'EOF', 'source': 'record_valueset_received', 'dest': 'completed'},
            {'trigger': 'EOF', 'source': 'record_item_received', 'dest': 'completed'}
        ]

        parser_machine = Machine(model=model, states=states, transitions=transitions, 
                                 initial='empty', after_state_change='build_dictionary')

        section_parser = configparser.RawConfigParser(strict=False, dict_type=MultiOrderedDict)
        # Maintain case as is in the incoming text. Without this option set, 
        # it will convert to lower case
        section_parser.optionxform = str
        section_separator = '\n\n' # Dictionary files tend to have this
        if self.raw_dictionary.find('\r\n\r\n') != -1: 
            section_separator = '\r\n\r\n' # but csweb db dictionaries have this
        sectioned_dictionary = self.raw_dictionary.split(section_separator)
        
        try:
            for section in sectioned_dictionary:
                section_parser.clear()
                section_parser.read_string(section)
                section_name = section_parser.sections()[0]
                items = section_parser.items(section_name)
                model.trigger(section_name, section_name, items)
            model.trigger('EOF', None, None)
        except Exception as err:
            return "Parsing error. " + str(err)

        self.parsed_dictionary = model.builder.tree if model.builder.is_built else None
        return self.parsed_dictionary
    
    def get_column_labels(self, record_name):
        if self.parsed_dictionary is not None:
            record = list(filter(lambda r: r['Name'] == record_name, self.parsed_dictionary['Dictionary']['Level']['Records']))
            if len(record) > 0:
                items = record[0]['Items']
                return dict(list(
                    map(lambda i: (i['Name'], i['Label']), items)
                ))
            else:
                return None
        else:
            return None
    
    def cast(self, value, item):
        if item['DataType'] == 'Numeric' and value != '':
            try:
                value = float(value) if item['Decimal'] else int(value)
            except ValueError:
                pass
        else:
            value = str(value)
        return value
    
    def get_value_labels(self, record_name, desired_columns = None):
        if self.parsed_dictionary is not None:
            record = list(filter(lambda r: r['Name'] == record_name, self.parsed_dictionary['Dictionary']['Level']['Records']))
            value_labels = {}
            if len(record) > 0:
                items = record[0]['Items']
                for item in items:
                    if desired_columns is not None and item['Name'] not in desired_columns:
                        continue
                    valuesets = item.get('ValueSets', None)
                    if valuesets is not None:
                        values = valuesets[0]['Value']
                        # Handle these conditions separately
                        # value = 1;Male, value = 0:120, value = 1:49;Line number, value = '   ';N/A
                        dictified = []
                        for value in values:
                            if value.find(';') != -1:
                                v, l = (value.split(';', maxsplit = 1))
                                if v.find(':') == -1:
                                    try:
                                        dictified.append((self.cast(v, item), l))
                                    except:
                                        pass
                            
                        value_labels[item['Name']] = dict(dictified)        
                return value_labels
            else:
                return None
            
        else:
            return None