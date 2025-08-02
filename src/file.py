from typing import List
from typing import Optional
import io
import errno
import sys
import os
import json

from src.parse_engine import ParseEngine
import src.entity as entity
import src.enums as enums

class File(object):
    '''
    Represents a GEDCOM file and provides methods to JSONify the information.
    Initializing the class will parse the GEDCOM file and methods like `jsonify`
    will convert the parsed data into JSON format. 
    '''
    def __init__(self, filepath: str):
        self.filepath: str = filepath
        self._byte_order_mark: Optional[enums.ByteOrderMark] = None

        self._raw_file_lines: List[str] = []
        self._load_from_file()

        self._engine: ParseEngine = ParseEngine()

        self._records: List[entity.Record] = self._engine.run(lambda: self._engine.parse_raw_lines(self._raw_file_lines))

        self._header: entity.Header = self._engine.run(self._engine.parse_header)
        self._individuals: List[entity.Individual] = self._engine.run(self._engine.parse_indi_records)
        self._families: List[entity.Family] = self._engine.run(self._engine.parse_fam_records)

    def jsonify(self, to_file=False, *fields: enums.JSONField) -> str:
        '''
        Converts the parsed GEDCOM data into a JSON string. This is stored in a file with
        the filename passed in during initialization (i.e. royal92.ged is jsonified to royal92.json).
        Without providing `fields`, the JSON string will contain all information parsed. If
        any `fields` are provided, it will only include those specified fields.
        '''
        json_obj: dict[str, str] = {}

        if len(fields) == 0 or enums.JSONField.IND in fields:
            json_obj['individuals'] = [indi.jsonify() for indi in self._individuals] if len(self._individuals) > 0 else None
        if len(fields) == 0 or enums.JSONField.FAM in fields:
            json_obj['families'] = [fam.jsonify() for fam in self._families] if len(self._families) > 0 else None

        if not to_file:
            json_str = json.dumps(json_obj)
            return json_str
        else:
            json_str = json.dumps(json_obj, indent=4)
            try:
                # TODO: Implement system agnostic file path handling
                json_file_path: str = self.filepath.rstrip('.ged') + '.json'
                with open(json_file_path, mode='w', encoding='utf-8') as fp:
                    fp.write(json_str)
            except IOError as e:
                if e.errno == errno.ENOENT:
                    print(
                        f'No such a file or directory (errno: {e.errno}): {self.filepath}',
                        file=sys.stderr
                    )
                    sys.exit(os.EX_OSFILE)
                else:
                    print(
                        f'Cannot open file (errno: {e.errno}): {self.filepath}',
                        file=sys.stderr
                    )
                    sys.exit(os.EX_OSFILE)

    def print_individuals(self) -> None:
        '''
        Prints all individuals parsed from the GEDCOM file.
        '''
        for individual in self._individuals:
            print(individual)
            print('')

    def print_records(self, show_hierarchy: bool = False) -> None:
        '''
        Prints all records parsed from the GEDCOM file as it would appear in the original file.
        If `show_hierarchy` is True, it will print each line with a number of leading spaces equal
        to the level value of the record.
        '''
        for record in self._records:
            self._print_records_helper(record, 0, show_hierarchy)

    def _print_records_helper(self, record: entity.Record, level: int, show_hierarchy: bool) -> None:
        if show_hierarchy:
            print(' ' * level, end='')
        print(record)
        for child in record.child_records:
            self._print_records_helper(child, level + 1, show_hierarchy)

    def _load_from_file(self) -> None:
        try:
            path: str = self.filepath
            with open(path, mode='r', encoding='utf-8') as fp:
                self._strip_byte_order_mark(fp)
                for line in fp:
                    self._raw_file_lines.append(line.rstrip('\n\r'))
        except IOError as e:
            if e.errno == errno.ENOENT:
                print(
                    f'No such a file or directory (errno: {e.errno}): {self.filepath}',
                    file=sys.stderr
                )
                sys.exit(os.EX_OSFILE)
            else:
                print(
                    f'Cannot open file (errno: {e.errno}): {self.filepath}',
                    file=sys.stderr
                )
                sys.exit(os.EX_OSFILE)

    def _strip_byte_order_mark(self, fp: io.TextIOWrapper) -> None:
        bom: bytes = fp.read(1).encode('utf-8')
        if bom == b'\xef\xbb\xbf':
            self._byte_order_mark = enums.ByteOrderMark._32_BIT_LITTLE_ENDIAN
        elif bom == b'\x00\x00\xfe\xff':
            self._byte_order_mark = enums.ByteOrderMark._32_BIT_BIG_ENDIAN
        elif bom == b'\xff\xfe':
            self._byte_order_mark = enums.ByteOrderMark._16_BIT_LITTLE_ENDIAN
        elif bom == b'\xfe\xff':
            self._byte_order_mark = enums.ByteOrderMark._16_BIT_BIG_ENDIAN
        elif bom == b'\x00':
            self._byte_order_mark = enums.ByteOrderMark._8_BIT
        else:
            self._byte_order_mark = None
            fp.seek(0)

gedcom_file = File('/home/ethan/Desktop/GEDCOM-to-JSON/GedcomToJson/files/pres2020.ged')
gedcom_file.jsonify(True, enums.JSONField.IND, enums.JSONField.FAM)