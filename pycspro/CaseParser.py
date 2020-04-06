import functools

class CaseParser:
    def __init__(self, parsed_dictionary, cutting_mask = {}):
        self.parsed_dictionary = parsed_dictionary
        self.cutting_mask = cutting_mask
        self.is_multi_rec_type = self.parsed_dictionary['Dictionary']['RecordTypeLen'] > 0
        self.rec_type_start = self.parsed_dictionary['Dictionary']['RecordTypeStart']
        self.rec_type_len = self.parsed_dictionary['Dictionary']['RecordTypeLen']
        self.main_table_name = self.parsed_dictionary['Dictionary']['Level']['Name']
        self.iditems_columns = self.make_iditems_columns()
        self.cutters = self.make_cutters()
        
    def make_column_tuples(self, items):
        return list(map(lambda item: tuple([
                                            item['Name'], 
                                            item['Start'], 
                                            item['Len'],
                                            item['DataType'],
                                            item['DecimalChar']]), items))
        
    def make_iditems_columns(self):
        return self.make_column_tuples(self.parsed_dictionary['Dictionary']['Level']['IdItems'])
        
    def make_caseid_column_cutter(self):
        span = functools.reduce(lambda accumulator, y: accumulator + y[2], self.iditems_columns, 0)
        return [tuple(['CASE_ID', self.iditems_columns[0][1], span, 'Alpha', False])]
    
    def make_cutters(self):
        # columns is [('Name', 'Start', 'Len', 'DataType', 'DecimalChar'), ...]
        caseid_column_cutter = self.make_caseid_column_cutter()
        cutters = {}
        questionnaire = self.parsed_dictionary['Dictionary']['Level']['Name']
        columns = self.iditems_columns
        if questionnaire in self.cutting_mask:
            desired_columns = self.cutting_mask[questionnaire]
            columns = list(filter(lambda column: column[0] in desired_columns, columns))
        cutters[self.parsed_dictionary['Dictionary']['Level']['Name']] = {
            'marker': None,
            'columns': caseid_column_cutter + columns,
        }
        for record in self.parsed_dictionary['Dictionary']['Level']['Records']:
            columns = self.make_column_tuples(record['Items'])
            if record['Name'] in self.cutting_mask:
                desired_columns = self.cutting_mask[record['Name']]
                columns = list(filter(lambda column: column[0] in desired_columns, columns))
            cutters[record['Name']] = {
                'marker': record['RecordTypeValue'],
                'columns': caseid_column_cutter + columns,
            }
        return cutters
        
    def cut_columns(self, record, table, column_cutters):
        for column_cutter in column_cutters:
            column_name, start, span, data_type, decimal = column_cutter
            column_data = table.get(column_name, [])
            value = record[(start - 1) : (start - 1) + span].strip()
            if data_type == 'Numeric' and value != '':
                try:
                    value = float(value) if decimal else int(value)
                except ValueError:
                    pass
            else:
                value = str(value)
            column_data.append(value)
            table[column_name] = column_data
        return table
    
    def parse(self, cases):
        if isinstance(cases, list):
            tables = {}
            categories = {
                self.main_table_name: self.tables_builder(tables, self.main_table_name)
            }
            next(categories[self.main_table_name])
            for case in cases:
                if case.strip() == '':
                    continue
                records = case.split('\n')
                categories[self.main_table_name].send(records[0])
                for record in records:
                    marker = record[(self.rec_type_start - 1) : (self.rec_type_start - 1) + self.rec_type_len]
                    record_name = list(filter(lambda k: self.cutters[k]['marker'] == marker, self.cutters))[0]
                    if categories.get(record_name, None) is None:
                        categories[record_name] = self.tables_builder(tables, record_name)
                        next(categories[record_name])
                    categories[record_name].send(record)
            for _, category in categories.items():
                category.send(None)
            return tables
        else:
            return None
    
    def tables_builder(self, tables, name):
        while True:
            cutter = self.cutters[name]
            tables[name] = yield from self.table_builder(cutter)
            
    def table_builder(self, cutter):
        table = {}
        while True:
            record = yield
            if record is None:
                break
            table = self.cut_columns(record, table, cutter['columns'])
        return table