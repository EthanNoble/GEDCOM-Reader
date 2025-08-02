from typing import List
from typing import Optional
from typing import Callable
from typing import Any
import sys

import src.entity as entity
import src.enums as enums
import src.utils as utils

class ParseEngine:
    def __init__(self):
        self._error: Optional[str] = None
        self._warnings: List[str] = []

        self._top_level_references: dict[str, entity.Record] = {}
        self._indi_records: List[entity.Record] = []
        self._fam_records: List[entity.Record] = []

    def run(self, callback: Callable) -> Any:
        if not self._error:
            res: Any = callback()
            if not self._error:
                return res
            else:
                print(self.get_error(), end='', file=sys.stderr)
                sys.exit(1)
        return None

    def get_error(self) -> str:
        if self._error:
            return f'[ERROR] {self._error}\n'
        else:
            return ''

    def get_warnings(self) -> tuple[int, str]:
        warnings: str = ''
        for i, w in enumerate(self._warnings):
            warnings += f'[WARNING {i+1}] {w}\n'
        return (len(self._warnings), warnings)

    def parse_raw_lines(self, raw_file_lines: List[str]) -> Optional[List[entity.Record]]:
        parsed_records: List[entity.Record] = []

        stack: List[entity.Record] = []
        for i, line in enumerate(raw_file_lines):
            record: entity.Record = self.parse_raw_line(line, i+1)
            if not record:
                return None

            while len(stack) > 0 and stack[-1].level >= record.level:
                stack.pop()

            if len(stack) > 0:
                parent: entity.Record = stack[-1]
                parent.child_records.append(record)
            else:
                parsed_records.append(record)

            stack.append(record)

        return parsed_records

    def parse_raw_line(self, raw_line: str, line_num: int) -> Optional[entity.Record]:
        record: Optional[entity.Record] = None

        tokens: List[str] = raw_line.split()
        i: int = 0

        # First token must be a level
        if utils.is_valid_level(tokens[i]):
            record = entity.Record(level=int(tokens[i]))
        else:
            self._error = f'Invalid level {tokens[i]} in line {line_num}'
            return None

        i += 1

        # Check for optional cross reference id
        if utils.is_cross_ref_id(tokens[i]):
            cross_ref_id: str = tokens[i]
            if utils.is_valid_cross_ref_id(cross_ref_id):
                if cross_ref_id in self._top_level_references:
                    self._error = f'Duplicate cross reference id {cross_ref_id} in line {line_num}'
                    return None
                record.cross_ref_id = cross_ref_id
                # Found cross ref id, move on to next token
                i += 1
                # Add record to the lookup table that will
                # be used to resolve other records that have
                # a pointer referencing the cross ref id
                self._top_level_references[cross_ref_id] = record
            else:
                self._error = f'Invalid cross reference id {cross_ref_id} in line {line_num}'
                return None

        # Next token must be a tag
        allow_redefined: bool = True
        if utils.is_valid_tag(tokens[i]) or utils.is_user_defined_tag(tokens[i], allow_redefined):
            record.tag = tokens[i]
            match tokens[i]:
                case enums.Tag.INDI.value:
                    self._indi_records.append(record)
                case enums.Tag.FAM.value:
                    self._fam_records.append(record)
                case enums.Tag.HEAD.value:
                    self._header_record = record
                case _:
                    pass
        elif utils.is_obsolete_tag(tokens[i]):
            record.tag = tokens[i]
            self._warnings.append(f'Record ignored with the obsolete tag {tokens[i]} in line {line_num}')
            record._ignorable = True
        else:
            self._error = f'Invalid tag {tokens[i]} in line {line_num}'
            return None

        i += 1

        # Check for optional line value, read in the rest of the tokens if they exist
        while i < len(tokens):
            if (
                utils.is_cross_ref_id(tokens[i])
                and utils.is_valid_cross_ref_id(tokens[i])
            ):
                # Error if there is both a cross ref id and pointer
                if record.cross_ref_id:
                    self._error = f'Duplicate cross reference and pointer in line {line_num}'
                    return None
                record.cross_ref_ptr = tokens[i]
            elif utils.is_valid_line_value_token(tokens[i]):
                record.line_value += tokens[i]
                if i != len(tokens) - 1:
                    record.line_value += ' '
            else:
                self._error = f'Invalid text {tokens[i]} in line {line_num}'
                return None
            i += 1

        return record
    
    def parse_header(self) -> Optional[entity.Header]:
        return None

    def parse_fam_records(self) -> Optional[List[entity.Family]]:
        families: List[entity.Family] = []
        for record in self._fam_records:
            family: entity.Family = entity.Family(record.cross_ref_id)
            for child in record.child_records:
                pointer: str = child.cross_ref_ptr
                match child.tag:
                    case enums.Tag.HUSB.value | enums.Tag.WIFE.value | enums.Tag.CHIL.value:
                        if pointer in self._top_level_references:
                            referenced_record: entity.Record = self._top_level_references[pointer]
                            referenced_indi: entity.Individual = referenced_record.individual

                            if not referenced_indi:
                                self._error = f'The record \'{child}\' references an individual which does not exist'
                                return None
                            
                            if child.tag == enums.Tag.HUSB.value:
                                family.parent1 = referenced_indi
                            elif child.tag == enums.Tag.WIFE.value:
                                family.parent2 = referenced_indi
                            elif child.tag == enums.Tag.CHIL.value:
                                family.add_child(referenced_indi)
                        else:
                            self._error = f'The record \'{child}\' references a record which does not exist'
                            return None
                    case enums.Tag.MARR.value:
                        pass
                    case _:
                        pass
            families.append(family)
        return families

    def parse_indi_records(self) -> Optional[List[entity.Individual]]:
        individuals: List[entity.Individual] = []

        for record in self._indi_records:
            individual: entity.Individual = entity.Individual(record.cross_ref_id)
            for child in record.child_records:
                match child.tag:
                    case enums.Tag.NAME.value:
                        name: entity.Individual.Name = self._parse_personal_name_structure(child)
                        if not name:
                            self._error = f'Invalid name {child.line_value} for individual {record.cross_ref_id}'
                            return None
                        individual.names.append(name)
                    case enums.Tag.SEX.value:
                        if child.line_value == '':
                            individual.sex = enums.Sex.U
                        elif not enums.key_is_in(child.line_value, enums.Sex):
                            self._error = f'Invalid sex {child.line_value} for individual {record.cross_ref_id}'
                            return None
                        else:
                            individual.sex = enums.key_of(child.line_value, enums.Sex)
                    case item if item in enums.indi_event_type:
                        event: entity.Event = self.parse_event_detail_structure(child)
                        individual.add_event(event)
                    case _:
                        pass
            record.individual = individual
            individuals.append(individual)
        return individuals

    def _parse_personal_name_structure(self, record: entity.Record) -> Optional[entity.Individual.Name]:
        name: entity.Individual.Name = entity.Individual.Name()
        tokens: List[str] = record.line_value.split()
        
        if len(tokens) == 0:
            return None
        
        # Handling the case in which the surname
        # has spaces, i.e. '/Van Buren/'
        multi_token_surname: bool = False
        surname_tokens: List[str] = []
        for token in tokens:
            if utils.is_surname(token):
                name.unstructured_name_parts.append(token.strip('/'))
            elif token[0] == '/':
                multi_token_surname = True
                surname_tokens.append(token.lstrip('/'))
            elif token[len(token)-1] == '/':
                multi_token_surname = False
                surname_tokens.append(token.rstrip('/'))
                name.unstructured_name_parts.append(' '.join(surname_tokens))
            elif multi_token_surname:
                surname_tokens.append(token)
            else:
                name.unstructured_name_parts.append(token)
        
        if multi_token_surname:
            return None
        
        for child in record.child_records:
            match child.tag:
                case enums.Tag.TYPE.value:
                    if not enums.val_is_in(child.line_value, enums.NameType):
                        return None
                    name.type = enums.key_of(child.line_value, enums.NameType)
                case enums.Tag.NPFX.value:
                    name.prefix = child.line_value
                case enums.Tag.GIVN.value:
                    name.given = child.line_value
                case enums.Tag.NICK.value:
                    name.nickname = child.line_value
                case enums.Tag.SPFX.value:
                    name.surname_prefix = child.line_value
                case enums.Tag.SURN.value:
                    name.surname = child.line_value
                case enums.Tag.NSFX.value:
                    name.suffix = child.line_value
                case _:
                    pass
        
        return name

    def parse_event_detail_structure(self, record: entity.Record) -> entity.Event:
        event_type: str = enums.indi_event_type[record.tag] if not record.line_value else record.line_value
        event: entity.Event = entity.Event(event_type)
        for child in record.child_records:
            match child.tag:
                case enums.Tag.TYPE.value:
                    event.type = child.line_value
                case enums.Tag.DATE.value:
                    event.date = entity.Date(child.line_value)
                case enums.Tag.PLAC.value:
                    event.place = self.parse_place_structure(child)
                case enums.Tag.ADDR.value:
                    event.address = self.parse_address_structure(child)
                case enums.Tag.NOTE.value:
                    event.note = child.line_value
        return event

    def parse_place_structure(self, record: entity.Record) -> Optional[entity.Place]:
        place: entity.Place = entity.Place()
        place.name = record.line_value
        for child in record.child_records:
            match child.tag:
                case enums.Tag.LATI.value:
                    place.latitude = child.line_value
                case enums.Tag.LONG.value:
                    place.longitude = child.line_value
                case _:
                    pass
        return place

    def parse_address_structure(self, record: entity.Record) -> Optional[entity.Address]:
        address: entity.Address = entity.Address()
        for child in record.child_records:
            match child.tag:
                case enums.Tag.ADR1.value:
                    address.add_address(child.line_value)
                case enums.Tag.ADR2.value:
                    address.add_address(child.line_value)
                case enums.Tag.ADR3.value:
                    address.add_address(child.line_value)
                case enums.Tag.CITY.value:
                    address.city = child.line_value
                case enums.Tag.STAE.value:
                    address.state = child.line_value
                case enums.Tag.POST.value:
                    address.postal = child.line_value
                case enums.Tag.CTRY.value:
                    address.country = child.line_value
        return address
