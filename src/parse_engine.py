'''
This module provides the ParseEngine class for parsing GEDCOM files into structured Python objects.
'''

from typing import List
from typing import Optional
from typing import Callable
from typing import Any
import sys

from src import entity
from src import enums
from src import utils


class ParseEngine:
    '''
    ParseEngine is responsible for parsing GEDCOM file lines into structured entity records
    Attributes:
        _error (Optional[str]): Stores the latest error message encountered during parsing.
        _warnings (List[str]): Stores warning messages encountered during parsing.
        _top_level_references (dict[str, entity.Record]): Maps cross-reference IDs to their corresponding top-level records.
        _indi_records (List[entity.Record]): List of individual records parsed from the GEDCOM file.
        _fam_records (List[entity.Record]): List of family records parsed from the GEDCOM file.
    '''

    def __init__(self):
        self._error: str | None = None
        self._warnings: List[str] = []

        self._top_level_references: dict[str, entity.Record] = {}
        self._header: entity.Record | None = None
        self._indi_records: List[entity.Record] = []
        self._fam_records: List[entity.Record] = []

    def run(self, callback: Callable[[], Any]) -> Any:
        '''
        Executes the provided callback function and handles any errors that may occur during its execution.
        Args:
            callback (Callable[[], Any]): A function to execute that performs parsing.
        Returns:
            Any: The result of the callback function if no errors occur, otherwise exits the program with an error message.
        '''
        if not self._error:
            res: Any = callback()
            if not self._error:
                return res
            print(self.get_error(), end='', file=sys.stderr)
            sys.exit(1)
        return None

    def get_error(self) -> str:
        '''
        Returns the latest error message if any error has occurred.
        If no error has occurred, returns an empty string.
        Returns:
            str: The latest error message or an empty string if no error has occurred.
        '''
        if self._error:
            return f'[ERROR] {self._error}\n'
        return ''

    def get_warnings(self) -> tuple[int, str]:
        '''
        Returns the number of warnings and a formatted string containing all warning messages.
        If no warnings have occurred, returns 0 and an empty string.
        Returns:
            tuple[int, str]: A tuple containing the number of warnings and a formatted string of warnings.
            If no warnings exist, returns (0, '').
        '''
        warnings: str = ''
        for i, w in enumerate(self._warnings):
            warnings += f'[WARNING {i+1}] {w}\n'
        return (len(self._warnings), warnings)

    def parse_raw_lines(self, raw_file_lines: List[str]) -> List[entity.Record] | None:
        '''
        Parses a list of raw GEDCOM file lines into structured Record objects.
        Args:
            raw_file_lines (List[str]): List of raw lines from the GEDCOM file.
        Returns:
            List[entity.Record] | None: A list of parsed Record objects if successful, otherwise None if an error occurs.
        '''
        parsed_records: List[entity.Record] = []

        stack: List[entity.Record] = []
        for i, line in enumerate(raw_file_lines):
            record: entity.Record | None = self.parse_raw_line(line, i+1)
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

    def parse_raw_line(self, raw_line: str, line_num: int) -> entity.Record | None:
        '''
        Parses a single raw GEDCOM line into a Record object.
        Args:
            raw_line (str): The raw line from the GEDCOM file to parse.
            line_num (int): The line number in the GEDCOM file (for error reporting).
        Returns:
            entity.Record | None: The parsed Record object if the line is valid, otherwise None.
        '''

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
                    self._header = record
                case _:
                    pass
        elif utils.is_obsolete_tag(tokens[i]):
            record.tag = tokens[i]
            self._warnings.append(
                f'Record ignored with the obsolete tag {tokens[i]} in line {line_num}')
            record.ignorable = True
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

    def parse_header(self) -> entity.Header | None:
        '''
        Parses the header record from the GEDCOM file.
        Returns:
            entity.Header | None: A Header entity if parsing is successful, otherwise None if an error occurs.
        '''
        if self._header is None:
            self._error = 'No header record found at the beginning of the GEDCOM file'
            return None
        
        err_unrecognized: Callable[[str], str] = lambda tag: f'Unrecognized header tag \'{tag}\''
        err_date: Callable[[str], str] = lambda value: f'Invalid header value \'{value}\' for date record'

        header: entity.Header = entity.Header()
        for record in self._header.child_records:
            match record.tag:
                case enums.Tag.SOUR:
                    header.set_source_system_id(record.line_value)
                    for source_child in record.child_records:
                        match source_child.tag:
                            case enums.Tag.VERS:
                                header.set_source_version(source_child.line_value)
                            case enums.Tag.NAME:
                                header.set_source_product_name(source_child.line_value)
                            case enums.Tag.CORP:
                                header.set_source_corporation_business_name(source_child.line_value)
                                address: entity.Address | None = self.parse_address(source_child)
                                if address:
                                    header.set_source_corporation_business_address(address)
                                else:
                                    return None
                            case enums.Tag.DATA:
                                header.set_source_data_source_name(source_child.line_value)
                                for source_data_child in source_child.child_records:
                                    match source_data_child.tag:
                                        case enums.Tag.DATE:
                                            try:
                                                date: entity.Date = entity.Date(source_data_child.line_value)
                                                header.set_source_data_publication_date(date)
                                            except ValueError:
                                                self._error = err_date(source_data_child.line_value)
                                        case enums.Tag.COPR:
                                            header.set_source_data_copyright(source_data_child.line_value)
                                        case _:
                                            self._error = err_unrecognized(source_data_child.tag)
                                            return None
                            case _:
                                if not utils.is_user_defined_tag(source_child.tag, allow_redefined=True):
                                    self._error = err_unrecognized(source_child.tag)
                                    return None
                case enums.Tag.DATE:
                    try:
                        date: entity.Date = entity.Date(record.line_value)
                        header.set_transmission_date(date)
                    except ValueError:
                        self._error = err_date(record.line_value)
                case enums.Tag.SUBM | enums.Tag.SUBN:
                    # TODO: Link cross refs with their respective records
                    if utils.is_cross_ref_id(record.cross_ref_ptr) \
                    and utils.is_valid_cross_ref_id(record.cross_ref_ptr):
                        if record.tag == enums.Tag.SUBM:
                            header.set_submitting_to(record.cross_ref_ptr)
                        elif record.tag == enums.Tag.SUBN:
                            header.set_submitted_by(record.cross_ref_ptr)
                case enums.Tag.GEDC:
                    for child in record.child_records:
                        match child.tag:
                            case enums.Tag.VERS:
                                header.set_gedcom_file_meta_version(child.line_value)
                            case enums.Tag.FORM:
                                if child.line_value in enums.Form:
                                    header.set_gedcom_file_meta_form(child.line_value)
                            case _:
                                self._error = err_unrecognized(child.tag)
                                return None
                case enums.Tag.CHAR:
                    header.set_character_set_type(record.line_value)
                    for child in record.child_records:
                        match child.tag:
                            case enums.Tag.VERS:
                                header.set_character_set_version(child.line_value)
                            case _:
                                self._error = err_unrecognized(child.tag)
                                return None
                case enums.Tag.PLAC:
                    header.set_place(record.line_value)
                case enums.Tag.DEST:
                    header.set_receiving_system(record.line_value)
                case enums.Tag.FILE:
                    header.set_file_name(record.line_value)
                case enums.Tag.COPR:
                    header.set_gedcom_file_copyright(record.line_value)
                case enums.Tag.LANG:
                    header.set_language(record.line_value)
                case enums.Tag.NOTE:
                    header.set_note(record.line_value)
                case _:
                    self._error = err_unrecognized(record.tag)
                    return None
        
        return header
    
    def parse_address(self, record: entity.Record) -> entity.Address | None:
        '''
        Parses an address structure from a GEDCOM record and returns an Address object.
        Args:
            record (entity.Record): The GEDCOM record containing address-related child records.
        Returns:
            entity.Address | None: An Address object populated with parsed address data, or None if no address data is found.
        '''

        err_unrecognized: Callable[[str], str] = lambda tag: f'Unrecognized address tag \'{tag}\''

        address: entity.Address = entity.Address()
        for record in record.child_records:
            match record.tag:
                case enums.Tag.ADDR:
                    address.add_address_line(record.line_value)
                    # Set to false once first non-CONT tag is reached. Then
                    # if a subsequent non-connecting CONT tags are encountered,
                    # throw an error
                    appending_addr_cont = True
                    for addr_child in record.child_records:
                        match addr_child.tag:
                            case enums.Tag.CONT:
                                if not appending_addr_cont:
                                    self._error = f'Out of order CONT tags within address'
                                    return None
                                address.add_address_line(addr_child.line_value)
                            case enums.Tag.CITY:
                                address.set_city_address(addr_child.line_value)
                                appending_addr_cont = False
                            case enums.Tag.STAE:
                                address.set_state_address(addr_child.line_value)
                                appending_addr_cont = False
                            case enums.Tag.POST:
                                address.set_zip_code(addr_child.line_value)
                                appending_addr_cont = False
                            case enums.Tag.CTRY:
                                address.set_country_address(addr_child.line_value)
                                appending_addr_cont = False
                            case _:
                                self._error = err_unrecognized(addr_child.tag)
                                return None
                case enums.Tag.PHON:
                    address.set_phone_number(record.line_value)
                case enums.Tag.EMAIL:
                    address.set_email_address(record.line_value)
                case enums.Tag.FAX:
                    address.set_fax_address(record.line_value)
                case enums.Tag.WWW:
                    address.set_web_address(record.line_value)
                case _:
                    self._error = err_unrecognized(record.tag)
                    return None
                
        return address

    def parse_fam_records(self) -> List[entity.Family] | None:
        '''
        Parses family records and constructs a list of Family entities.
        Iterates over the family records, extracting references to individuals and associates
        them with the corresponding Family entity. If a referenced individual or record
        does not exist, sets an error message and returns None.
        Returns:
            List[entity.Family] | None: A list of Family entities if parsing is successful,
            otherwise None if an error occurs.
        '''

        families: List[entity.Family] = []
        for record in self._fam_records:
            family: entity.Family = entity.Family(record.cross_ref_id)
            for child in record.child_records:
                pointer: str = child.cross_ref_ptr
                match child.tag:
                    case enums.Tag.HUSB.value | enums.Tag.WIFE.value | enums.Tag.CHIL.value:
                        if pointer in self._top_level_references:
                            referenced_record: entity.Record = self._top_level_references[pointer]
                            referenced_indi: entity.Individual | None = referenced_record.individual

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

    def parse_indi_records(self) -> List[entity.Individual] | None:
        '''
        Parses individual (INDI) records and constructs a list of Individual entities.
        Iterates through the list of individual records, extracting and validating relevant information.
        Returns:
            List[entity.Individual] | None: A list of parsed Individual entities, or None if a parsing error occurs.
        '''

        individuals: List[entity.Individual] = []

        for record in self._indi_records:
            individual: entity.Individual = entity.Individual(
                record.cross_ref_id)
            for child in record.child_records:
                match child.tag:
                    case enums.Tag.NAME.value:
                        name: entity.Individual.Name | None = self._parse_personal_name_structure(child)
                        if not name:
                            self._error = f'Invalid name {child.line_value} for individual {record.cross_ref_id}'
                            return None
                        individual.names.append(name)
                    case enums.Tag.SEX.value:
                        if child.line_value == '':
                            individual.sex = enums.Sex.UNKNOWN
                        elif not child.line_value in enums.Sex:
                            self._error = f'Invalid sex {child.line_value} for individual {record.cross_ref_id}'
                            return None
                        else:
                            individual.sex = enums.Sex(child.line_value)
                    case item if item in enums.indi_event_type:
                        event: entity.Event = self.parse_event_detail_structure(
                            child)
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
                    if child.line_value not in enums.NameType:
                        return None
                    name.type = enums.NameType(child.line_value)
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
        '''
        Parses a GEDCOM event detail structure from a given record and returns an Event object.
        Args:
            record (entity.Record): The GEDCOM record representing the event and its details.
        Returns:
            entity.Event: An Event object populated with parsed event data.
        '''

        event_type: str = enums.indi_event_type[record.tag] if not record.line_value else record.line_value
        event: entity.Event = entity.Event(event_type)
        for child in record.child_records:
            match child.tag:
                case enums.Tag.TYPE.value:
                    event.event_type = child.line_value
                case enums.Tag.DATE.value:
                    event.date = entity.Date(child.line_value)
                case enums.Tag.PLAC.value:
                    event.place = self.parse_place_structure(child)
                case enums.Tag.ADDR.value:
                    event.address = self.parse_address_structure(child)
                case enums.Tag.NOTE.value:
                    event.note = child.line_value
                case _:
                    pass
        return event

    def parse_place_structure(self, record: entity.Record) -> entity.Place | None:
        '''
        Parses a place structure from a GEDCOM record.
        Args:
            record (entity.Record): The GEDCOM record containing place information.
        Returns:
            entity.Place | None: A place object populated with parsed data, or None if no place data is found.
        '''

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
