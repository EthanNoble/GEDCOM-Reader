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
            self.dump_messages()
            sys.exit(1)
        return None
    
    def dump_messages(self) -> None:
        print(self.get_warnings()[1], end='', file=sys.stderr)
        print(self.get_error(), end='', file=sys.stderr)

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
        for w in self._warnings:
            warnings += f'[WARNING] {w}\n'
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
        
        err_unrecognized: Callable[[str], str] = lambda tag: f'Unrecognized header tag {tag}'
        err_date: Callable[[str], str] = lambda value: f'Invalid header value {value} for date record'

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
                                                return None
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
                    if len(record.child_records) == 1 \
                        and record.child_records[0].tag == enums.Tag.FORM:
                        header.set_place_hierarchy(record.child_records[0].line_value.split(','))
                    else:
                        self._error = 'Invalid header PLAC.FORM record'
                        return None
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

        err_unrecognized: Callable[[str], str] = lambda tag: f'Unrecognized family tag {tag}'

        families: List[entity.Family] = []
        for record in self._fam_records:
            family: entity.Family = entity.Family(record.cross_ref_id)
            for child in record.child_records:
                child_pointer: str = child.cross_ref_ptr
                match child.tag:
                    case enums.Tag.RESN:
                        if child.line_value not in enums.Restriction:
                            self._error = f'Invalid restriction notice {child.line_value} for family {record.cross_ref_id}'
                            return None
                        family.set_restriction_notice(enums.Restriction(child.line_value))
                    case enums.Tag.ANUL \
                        | enums.Tag.CENS \
                        | enums.Tag.DIV \
                        | enums.Tag.DIVF \
                        | enums.Tag.ENGA \
                        | enums.Tag.MARB \
                        | enums.Tag.MARC \
                        | enums.Tag.MARR \
                        | enums.Tag.MARL \
                        | enums.Tag.MARS \
                        | enums.Tag.RESI \
                        | enums.Tag.EVEN:
                        pass
                    case enums.Tag.HUSB | enums.Tag.WIFE | enums.Tag.CHIL:
                        if child_pointer in self._top_level_references:
                            referenced_record: entity.Record = self._top_level_references[child_pointer]
                            referenced_indi: entity.Individual | None = referenced_record.individual

                            if not referenced_indi:
                                self._error = f'The record {child} references an individual which does not exist'
                                return None

                            if child.tag == enums.Tag.HUSB:
                                family.set_parent_one(referenced_indi)
                            elif child.tag == enums.Tag.WIFE:
                                family.set_parent_two(referenced_indi)
                                # if len(child.child_records) > 1:
                                #     self._error = f'The record {child} cannot have more than one child record'
                                #     return None
                                # elif len(child.child_records) == 1 and child.child_records[0].tag == enums.Tag.AGE:
                            elif child.tag == enums.Tag.CHIL:
                                family.add_child(referenced_indi)
                        else:
                            self._error = f'The record {child} references a record which does not exist'
                            return None
                    case enums.Tag.NCHI:
                        pass
                    case enums.Tag.SUBM:
                        pass
                    case enums.Tag.REFN:
                        pass
                    case enums.Tag.RIN:
                        pass
                    case _:
                        if not utils.is_user_defined_tag(child.tag, allow_redefined=True):
                            self._error = err_unrecognized(child.tag)
                            return None

            families.append(family)

        return families

    def parse_indi_records(self) -> List[entity.Individual] | None:
        '''
        Parses individual (INDI) records and constructs a list of Individual entities.
        Iterates through the list of individual records, extracting and validating relevant information.
        Returns:
            List[entity.Individual] | None: A list of parsed Individual entities, or None if a parsing error occurs.
        '''

        err_unrecognized: Callable[[str], str] = lambda tag: f'Unrecognized individual tag {tag}'
        err_date: Callable[[str], str] = lambda value: f'Invalid value {value} for individual date record'

        def parse_name_pieces(record: entity.Record) -> entity.NamePiece:
            name_piece: entity.NamePiece = entity.NamePiece()
            for child in record.child_records:
                match child.tag:
                    case enums.Tag.NPFX:
                        name_piece.set_prefix(child.line_value)
                    case enums.Tag.GIVN:
                        name_piece.set_given(child.line_value)
                    case enums.Tag.NICK:
                        name_piece.set_nickname(child.line_value)
                    case enums.Tag.SPFX:
                        name_piece.set_surname_prefix(child.line_value)
                    case enums.Tag.SURN:
                        name_piece.set_surname(child.line_value)
                    case enums.Tag.NSFX:
                        name_piece.set_suffix(child.line_value)
                    case _:
                        # No error when other tags are encountered since this
                        # is just looking for a subset of possible NAME record tags.
                        pass

            return name_piece

        individuals: List[entity.Individual] = []
        for record in self._indi_records:
            individual: entity.Individual = entity.Individual(record.cross_ref_id)
            for child in record.child_records:
                match child.tag:
                    case enums.Tag.NAME:
                        name: entity.Name = entity.Name()
                        line_value: str = child.line_value.replace('/', '')
                        name_pieces: entity.NamePiece = parse_name_pieces(child)
                        name.set_name_value(line_value)
                        name.set_name_pieces(name_pieces)
                        for name_child in child.child_records:
                            match name_child.tag:
                                case enums.Tag.TYPE:
                                    if name_child.line_value not in enums.NameType:
                                        self._error = f'Invalid name type {name_child.line_value} for individual {record.cross_ref_id}'
                                        return None
                                    name.set_name_type(enums.NameType(name_child.line_value))
                                case enums.Tag.NOTE:
                                    name.set_name_note(child.line_value)
                                case enums.Tag.SOUR:
                                    name.set_name_source_citation(child.cross_ref_ptr)
                                case enums.Tag.FONE:
                                    fone_name_pieces: entity.NamePiece = parse_name_pieces(name_child)
                                    name.set_phonetic_value(name_child.line_value)
                                    name.set_phonetic_name_pieces(fone_name_pieces)
                                    for phonetic_child in name_child.child_records:
                                        match phonetic_child.tag:
                                            case enums.Tag.TYPE:
                                                if phonetic_child.line_value not in enums.PhoneticType:
                                                    self._error = f'Invalid phonetic type {phonetic_child.line_value} for individual {record.cross_ref_id}'
                                                    return None
                                                name.set_phonetic_type(enums.PhoneticType(phonetic_child.line_value))
                                            case enums.Tag.NOTE:
                                                name.set_phonetic_note(phonetic_child.line_value)
                                            case enums.Tag.SOUR:
                                                name.set_phonetic_source_citation(phonetic_child.cross_ref_ptr)
                                            case _:
                                                if not utils.is_user_defined_tag(phonetic_child.tag, allow_redefined=True):
                                                    self._error = err_unrecognized(phonetic_child.tag)
                                                    return None
                                case enums.Tag.ROMN:
                                    romanized_name_pieces: entity.NamePiece = parse_name_pieces(name_child)
                                    name.set_romanized_value(name_child.line_value)
                                    name.set_romanized_name_pieces(romanized_name_pieces)
                                    for romanized_child in name_child.child_records:
                                        match romanized_child.tag:
                                            case enums.Tag.TYPE:
                                                if romanized_child.line_value not in enums.RomanizedType:
                                                    self._error = f'Invalid romanized type {romanized_child.line_value} for individual {record.cross_ref_id}'
                                                    return None
                                                name.set_romanized_type(enums.RomanizedType(romanized_child.line_value))
                                            case enums.Tag.NOTE:
                                                name.set_romanized_note(romanized_child.line_value)
                                            case enums.Tag.SOUR:
                                                name.set_romanized_source_citation(romanized_child.cross_ref_ptr)
                                            case _:
                                                if not utils.is_user_defined_tag(romanized_child.tag, allow_redefined=True):
                                                    self._error = err_unrecognized(romanized_child.tag)
                                                    return None
                                case _:
                                    # Do not error out on personal name pieces
                                    if name_child.tag in {
                                        enums.Tag.NPFX,
                                        enums.Tag.GIVN,
                                        enums.Tag.NICK,
                                        enums.Tag.SPFX,
                                        enums.Tag.SURN,
                                        enums.Tag.NSFX
                                    }:
                                        continue
                                    if not utils.is_user_defined_tag(name_child.tag, allow_redefined=True):
                                        self._error = err_unrecognized(name_child.tag)
                                        return None
                        individual.add_name(name)
                    case enums.Tag.SEX:
                        if child.line_value == '':
                            individual.set_sex(enums.Sex.UNKNOWN)
                        elif not child.line_value in enums.Sex:
                            self._error = f'Invalid sex {child.line_value} for individual {record.cross_ref_id}'
                            return None
                        else:
                            individual.set_sex(enums.Sex(child.line_value))
                    case tag if tag in enums.event_type_individual:
                        event: entity.IndividualEvent = entity.IndividualEvent()
                        event.set_explicit_event_type(enums.event_type_individual[enums.Tag(tag)])
                        event.set_line_value(child.line_value)

                        for event_child in child.child_records:
                            match event_child.tag:
                                case enums.Tag.TYPE:
                                    event.set_generic_event_type(event_child.line_value)
                                case enums.Tag.DATE:
                                    date: entity.Date | None = self.parse_date(event_child)
                                    if not date:
                                        # Set error
                                        return None
                                    event.set_event_date(date)
                                case enums.Tag.PLAC:
                                    pass
                                case enums.Tag.ADDR:
                                    address: entity.Address | None = self.parse_address(event_child)
                                    if not address:
                                        return None
                                    event.set_event_address(address)
                                case enums.Tag.AGNC:
                                    pass
                                case enums.Tag.RELI:
                                    pass
                                case enums.Tag.CAUS:
                                    pass
                                case enums.Tag.RESN:
                                    pass
                                case enums.Tag.NOTE:
                                    pass # TODO: Note
                                case enums.Tag.SOUR:
                                    pass # TODO: Source
                                case enums.Tag.OBJE:
                                    pass # TODO: Multimedia
                                case _:
                                    if not utils.is_user_defined_tag(event_child.tag, allow_redefined=True):
                                        self._error = err_unrecognized(event_child.tag)
                                        return None

                        individual.add_individual_event(event)
                    case _:
                        pass

            record.individual = individual
            individuals.append(individual)
        return individuals

    def parse_date(self, record: entity.Record) -> entity.Date | None:
        '''
        Parses a date from a GEDCOM record.
        Returns:
            entity.Date | None: A Date object if parsing is successful, otherwise None if an error occurs.
        '''

        def strip_and_set_calendar_type() -> str | None:
            at_count: int = record.line_value.count('@')
            if at_count == 1:
                self._error = f'Invalid date record {record}, expected two @ symbols for calendar type'
                return None
            # If there are two @ symbols, it indicates a calendar type
            # The format is expected to be: @<calendar_type>@ <date>
            # where <calendar_type> is one of the enums.CalendarType values
            # and <date> is the actual date string.
            if at_count == 2:
                l = record.line_value.index('@')
                if l != 0:
                    self._error = f'Invalid date record {record}, expected @<CALENDAR>@ <date>'
                    return None
                r = record.line_value.rindex('@')

                calendar: str = record.line_value[l:r+1]
                if calendar not in enums.CalendarType:
                    self._error = f'Unknown calendar type {calendar} for date record {record}'
                    return None
                
                date.set_calendar(enums.CalendarType(calendar))
                # Remove calendar type from line value
                return record.line_value.replace(calendar, '').lstrip()
            
            # No calendar type specified, return the line value as is
            return record.line_value

        def determine_date_type(tokens: List[str]) -> enums.DateType | None:
            if len(tokens) == 0:
                return None
            
            token_one: str = tokens[0].upper().rstrip('.')
            token_two: str = tokens[1].upper().rstrip('.') if len(tokens) > 1 else ''

            if token_one in enums.DatePeriod:
                return enums.DateType.PERIOD

            if token_one in enums.DateRange:
                if token_one == enums.DateRange.BET and 'AND' not in tokens:
                    self._error = f'Invalid date record {record}, "BET" requires "AND" to separate two dates'
                    return None
                if token_two == 'AND':
                    # If the second token is "AND", then it is invalid
                    self._error = f'Invalid date record {record}, "AND" must separate two dates'
                    return None
                return enums.DateType.RANGE

            if token_one in enums.DateApproximated:
                return enums.DateType.APPROXIMATED

            if token_one == 'INT':
                # "INT" is a special case for a regular date with
                # a date phrase enclosed between parentheses
                return enums.DateType.REGULAR

            if token_one == '(':
                if tokens[-1] != ')':
                    self._error = f'Invalid date record {record}, expected closing parenthesis for date phrase'
                    return None
                # If the first token is an opening parenthesis, it indicates a date phrase
                return enums.DateType.PHRASE
            
            # If no special tokens are found, treat it as a regular date
            return enums.DateType.REGULAR
        
        date: entity.Date = entity.Date()
        warning_date: entity.Date = entity.Date()
        warning_date.set_type(enums.DateType.PHRASE)

        # Retrieve calendar type if specified, defaulted to Gregorian if not
        date_line_value: str | None = strip_and_set_calendar_type()
        if not date_line_value:
            return None
        
        tokens: List[str] = date_line_value.split()
        if len(tokens) == 0:
            self._error = f'Invalid date record {record}, no date value provided'
            return None

        # Determine the type of date based on the tokens
        date_type: enums.DateType | None = determine_date_type(tokens)
        if not date_type:
            # If an error occurred within determine_date_type, it will have already set the error message
            # TODO: Abstract this 'short-circuit' error handling into a separate class-level function
            self._error = self._error if self._error else f'Unable to determine the type of date for the record {record}'
            return None
        date.set_type(date_type)

        # Parse the date_line_value based on the calendar type
        match date.get_calendar():
            case enums.CalendarType.GREGORIAN:
                if date.get_type() == enums.DateType.REGULAR:
                    if len(tokens) == 1:
                        year: str = tokens[0]
                        if 'B.C.' in year or 'BC' in year:
                            year = utils.strip_BC(year)
                            date.set_regular_is_bc(True)
                        else:
                            date.set_regular_is_bc(False)

                        year_slash_count = year.count('/')
                        if year_slash_count == 0:
                            if not year.isdigit():
                                self._warnings.append(f'Invalid year {year} for date record {record}')
                                warning_date.set_phrase(date_line_value)
                                return warning_date
                            date.set_regular_year(int(year))
                        elif year_slash_count == 1:
                            # If the year contains a slash, it contains a julian alt year
                            parts = year.split('/')
                            if not parts[0].isdigit():
                                self._warnings.append(f'Invalid year {parts[0]} for date record {record}')
                                warning_date.set_phrase(date_line_value)
                                return warning_date
                            date.set_regular_year(int(parts[0]))

                            if not parts[1].isdigit():
                                self._warnings.append(f'Invalid julian alternative {parts[1]} for date record {record}')
                                warning_date.set_phrase(date_line_value)
                                return warning_date
                            date.set_regular_julian_alternative_year(int(parts[1]))
                        else:
                            # If the year contains more than one slash, it is invalid
                            self._error = f'Invalid year {year} for date record {record}, expected at most one slash'
                            return None
                    elif len(tokens) == 2:
                        if tokens[1] == 'B.C.' or tokens[1] == 'BC':
                            year: str = tokens[0]
                            date.set_regular_is_bc(True)
                        else:
                            month: str = tokens[0].upper().strip('.')
                            year: str = tokens[1]
                            if month not in enums.Month:
                                self._warnings.append(f'Invalid month {month} for date record {record}')
                                warning_date.set_phrase(date_line_value)
                                return warning_date
                            date.set_regular_month(enums.Month(month))
                            date.set_regular_is_bc(False)

                        if not year.isdigit():
                            self._warnings.append(f'Invalid year {year} for date record {record}')
                            warning_date.set_phrase(date_line_value)
                            return warning_date
                        date.set_regular_year(int(year))
                    elif len(tokens) == 3:
                        day: str = tokens[0]
                        month: str = tokens[1].upper().strip('.')
                        year: str = tokens[2]

                        if not day.isdigit():
                            self._warnings.append(f'Invalid day {day} for date record {record}')
                            warning_date.set_phrase(date_line_value)
                            return warning_date
                        date.set_regular_day(int(day))

                        if not year.isdigit():
                            self._warnings.append(f'Invalid year {year} for date record {record}')
                            warning_date.set_phrase(date_line_value)
                            return warning_date
                        date.set_regular_year(int(year))

                        if month not in enums.Month:
                            self._warnings.append(f'Invalid month {month} for date record {record}')
                            warning_date.set_phrase(date_line_value)
                            return warning_date
                        date.set_regular_month(enums.Month(month))

            case enums.CalendarType.JULIAN:
                # TODO: Implement Julian calendar parsing
                pass
            case enums.CalendarType.HEBREW:
                # TODO: Implement Hebrew calendar parsing
                pass
            case enums.CalendarType.FRENCH:
                # TODO: Implement French calendar parsing
                pass
            case enums.CalendarType.ROMAN:
                # TODO: Implement Roman calendar parsing
                pass
            case enums.CalendarType.UNKNOWN:
                # TODO: Implement Unknown calendar parsing
                pass
            case _:
                self._error = f'Unknown calendar type {date.get_calendar()} for date record {record}'

        # if str(record) == '2 DATE @#DHEBREW@ 14 NISAN 5701':exit()
        # for record in record.child_records:
        #     match record.tag:
        #         case enums.Tag.DATE:
        #             pass
        #         case enums.Tag.CALN:
        #             pass
        #         case _:
        #             self._error = f'Unrecognized date tag {record.tag}'
        #             return None

        return date

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
