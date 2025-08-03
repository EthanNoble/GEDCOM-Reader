'''
Entity classes for representing GEDCOM data structures.
'''

import json
from typing import List, Dict, Any, Optional
from typing import cast
from datetime import datetime
from dateutil.parser import parse

from src import enums


class EntityContainer:
    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data
    
    def jsonify(self) -> str:
        '''
        Convert the container's data to json, and prune keys that have empty values.
        An empty value is any value that contains `None`, `''`, `[]`, or `{}`.
        '''
        def is_empty(value: Any) -> bool:
            if value is None:
                return True
            if isinstance(value, str) and value.strip() == '':
                return True
            if isinstance(value, (list, dict)) and not value:
                return True
            return False

        def serialize(value: Any) -> Any:
            if isinstance(value, EntityContainer):
                return {
                    k: v_ser for k, v in value.get_data().items()
                    if not is_empty(v_ser := serialize(v))
                } or None
            elif isinstance(value, dict):
                value_dict = cast(Dict[str, Any], value)
                return {
                    k: v_ser for k, v in value_dict.items()
                    if not is_empty(v_ser := serialize(v))
                } or None
            elif isinstance(value, list):
                value_list = cast(list[Any], value)
                return [
                    v_ser for v in value_list
                    if not is_empty(v_ser := serialize(v))
                ] or None

            return None if is_empty(value) else value

        cleaned_data = {}
        for key, value in self._data.items():
            serialized_value = serialize(value)
            if serialized_value is not None:
                cleaned_data[key] = serialized_value

        return json.dumps(cleaned_data, indent=4)

    def get_data(self) -> Dict[str, Any]:
        return self._data
    
    def __getitem__(self, key: str) -> Any:
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value


class Header(EntityContainer):
    '''
    The header of a GEDCOM file.
    '''
    def __init__(self):
        super().__init__({
            'SOUR': {
                'VERS': '',
                'NAME': '',
                'CORP': {
                    'NAME': '',
                    'ADDR': ''
                },
                'DATA': {
                    'NAME': '',
                    'DATE': '',
                    'COPR': ''
                }
            },
            'DEST': '',
            'DATE': '',
            'SUBM': '',
            'SUBN': '',
            'FILE': '',
            'COPR': '',
            'GEDC': {
                'VERS': '',
                'FORM': '',
            },
            'CHAR': {
                'VERS': '',
                'NAME': ''
            },
            'LANG': '',
            'PLAC': '',
            'NOTE': ''
        })


class Address:
    '''
    Represents an address.
    '''
    def __init__(self):
        self._addresses: List[str] = []
        self.city: str = ''
        self.state: str = ''
        self.postal: str = ''
        self.country: str = ''

    def jsonify(self) -> object:
        '''
        Returns a JSON serializable representation of the address.
        If no address is set, returns an empty string.
        Returns:
            JSON serializable object
        '''
        return {
            'addresses': list(addr for addr in self._addresses),
            'city': self.city,
            'state': self.state,
            'postal': self.postal,
            'country': self.country
        }

    def add_address(self, addr: str) -> None:
        '''
        Adds an address to the list of addresses.
        Args:
            addr (str): The address to add.
        '''
        self._addresses.append(addr)

    def __str__(self):
        parts: list[str] = []
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal:
            parts.append(self.postal)
        if self.country:
            parts.append(self.country)
        return ' '.join(parts)


class Place:
    '''
    Represents a place.
    '''
    def __init__(self):
        self.name: Optional[str] = None
        self.latitude: Optional[str] = None
        self.longitude: Optional[str] = None

    def jsonify(self) -> object:
        '''
        Returns a JSON serializable representation of the place.
        If no name, latitude, or longitude is set, returns an empty string.
        Returns:
            JSON serializable object or empty string
        '''
        if not self.name and not self.latitude and not self.longitude:
            return ''

        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude
        }


class Event:
    '''
    Represents an event in a person's life.
    '''
    def __init__(self, event_type: str | None = None):
        self.event_type: str | None = event_type
        self.date: Date | None = None
        self.address: Address | None = None
        self.place: Place | None = None
        self.note: str | None = None

    def jsonify(self) -> object:
        '''
        Returns a JSON serializable representation of the event.
        If no date or address is set, returns an empty string.
        Returns:
            JSON serializable object or empty string
        '''
        if not self.date and not self.address:
            return ''

        return {
            'type': self.event_type,
            'date': self.date.jsonify() if self.date else None,
            'place': self.place.jsonify() if self.place else None,
            'address': self.address.jsonify() if self.address else None,
            'note': self.note
        }


class Date:
    '''
    Represents a date which can be parsed from a string.
    '''
    def __init__(self, date: str | None = None):
        self._raw_date_str: str | None = date
        self._date: Optional[datetime] = None
        if date:
            self._parse_date()

    def jsonify(self) -> object:
        '''
        Returns a JSON serializable representation of the date.
        If no date is set, returns None.
        Returns:
            JSON serializable object with original date string, date, day, month, and year
        '''
        if not self._raw_date_str or not self._date:
            return None

        return {
            'original': self._raw_date_str,
            'date': str(self) if self._date else None,
            'day': self.day(),
            'month': self.month(),
            'year': self.year()
        }

    def set_date(self, date: str):
        '''
        Sets the date from a string and parses it.
        Args:
            date (str): The date string to set.
        '''
        self._raw_date_str = date
        self._parse_date()

    def day(self) -> int | None:
        '''
        Returns the day of the month if the date is set, otherwise None.
        Returns:
            int | None: The day of the month or None if not set.
        '''
        return self._date.day if self._date else None

    def month(self) -> int | None:
        '''
        Returns the month of the year if the date is set, otherwise None.
        Returns:
            int | None: The month of the year or None if not set.
        '''
        return self._date.month if self._date else None

    def year(self) -> int | None:
        '''
        Returns the year if the date is set, otherwise None.
        Returns:
            int | None: The year or None if not set.
        '''
        return self._date.year if self._date else None

    def _parse_date(self) -> None:
        if not self._raw_date_str:
            return
        try:
            self._date = parse(self._raw_date_str, fuzzy=True)
        except ValueError:
            pass

    def __str__(self):
        return self._date.strftime('%Y-%m-%d') if self._date else ''


class Header:
    '''
    Represents the header of a GEDCOM file.
    '''
    def __init__(self):
        self.source: Optional[str] = None
        self.date: Optional[Date] = None
        self.gedcom_version: Optional[str] = None
        self.submission: Optional[str] = None
        self.submitter: Optional[str] = None

    def jsonify(self) -> object:
        '''
        Returns a JSON serializable representation of the header.
        Returns:
            JSON serializable object with source, date, gedcom_version, submission, and submitter
        '''

        return {
            'source': self.source,
            'date': self.date.jsonify() if self.date else None,
            'gedcom_version': self.gedcom_version,
            'submission': self.submission,
            'submitter': self.submitter
        }


class Individual:
    '''
    Represents an individual in a GEDCOM file.
    '''
    class Name:
        '''
        Represents a name of an individual, which can have multiple parts.
        '''
        def __init__(self, name_type: enums.NameType = enums.NameType.MAIN):
            # Enum data.NameType
            self.type: enums.NameType = name_type
            # From the line value of a NAME record
            self.unstructured_name_parts: List[str] = []
            # From a SURN sub record of a NAME record
            self.surname: Optional[str] = None
            # From a NPFX sub record of NAME
            self.prefix: Optional[str] = None
            # From a GIVN sub record of NAME
            self.given: Optional[str] = None
            # From a NICK sub record of NAME
            self.nickname: Optional[str] = None
            # From a SPFX sub record of NAME
            self.surname_prefix: Optional[str] = None
            # From a NSFX sub record of NAME
            self.suffix: Optional[str] = None

        def jsonify(self) -> object:
            '''
            Returns a JSON serializable representation of the name.
            Returns:
                JSON serializable object with type, name, and parts
            '''
            parts_list: List[object] = []

            if self.surname:
                parts_list.append(
                    {'type': 'Surname', 'value': self.surname})

            if self.prefix:
                parts_list.append(
                    {'type': 'Prefix', 'value': self.prefix})

            if self.given:
                parts_list.append(
                    {'type': 'Given', 'value': self.given})

            if self.nickname:
                parts_list.append(
                    {'type': 'Nickname', 'value': self.nickname})

            if self.surname_prefix:
                parts_list.append(
                    {'type': 'SurnamePrefix', 'value': self.surname_prefix})

            if self.suffix:
                parts_list.append(
                    {'type': 'Suffix', 'value': self.suffix})

            return {
                'type': enums.name_to_str[self.type.value],
                'name': ' '.join(self.unstructured_name_parts) if len(self.unstructured_name_parts) > 0 else None,
                'parts': parts_list if len(parts_list) > 0 else None
            }

    def __init__(self, indi_id: Optional[str] = None):
        self.indi_id: Optional[str] = indi_id
        self.names: List[Individual.Name] = []
        self.sex: enums.Sex = enums.Sex.UNKNOWN
        self._events: List[Event] = []
        self.dead: bool = False

        self.parent1: Optional[Individual] = None
        self.parent2: Optional[Individual] = None

    def jsonify(self) -> object:
        '''
        Returns a JSON serializable representation of the individual.
        Returns:
            JSON serializable object
        '''
        return {
            'id': self.indi_id,
            'names': [name.jsonify() for name in self.names],
            'sex': enums.sex_to_str[self.sex.value],
            'is_dead': self.dead,
            'events': [event.jsonify() for event in self._events],
        }

    def add_event(self, event: Event) -> None:
        '''
        Adds an event to the individual's list of events.
        Args:
            event (Event): The event to add.
        '''
        self._events.append(event)


class Family:
    '''
    Represents a family in a GEDCOM file, which can have two parents and multiple children.
    '''
    def __init__(self, fam_id: Optional[str] = None):
        self.fam_id: Optional[str] = fam_id
        self.parent1: Optional[Individual] = None
        self.parent2: Optional[Individual] = None
        self._children: List[Individual] = []

    def jsonify(self) -> object:
        '''
        Returns a JSON serializable representation of the family.
        Returns:
            JSON serializable object with id, parent1, parent2, and children
        '''
        return {
            'id': self.fam_id,
            'parent1': self.parent1.indi_id if self.parent1 else None,
            'parent2': self.parent2.indi_id if self.parent2 else None,
            'children': [child.indi_id for child in self._children] if len(self._children) > 0 else None
        }

    def add_child(self, child: Individual) -> None:
        '''
        Adds a child to the family.
        Args:
            child (Individual): The child to add.'''
        self._children.append(child)


class Record:
    '''
    Represents a record in a GEDCOM file.
    '''
    def __init__(self, level: int):
        self.level: int = level
        self.tag: str = ''  # Enum data.Tag
        self.line_value: str = ''

        self.cross_ref_id: str = ''
        self.cross_ref_ptr: str = ''

        self.ignorable = False

        self.child_records: List[Record] = []
        # The individual built from this record if this record tag is INDI
        self.individual: Optional[Individual] = None

    def __str__(self):
        record_str = str(self.level) + ' '

        if self.cross_ref_id:
            record_str += self.cross_ref_id + ' '

        if self.tag:
            record_str += self.tag + ' '

        if self.line_value:
            record_str += self.line_value
        elif self.cross_ref_ptr:
            record_str += self.cross_ref_ptr

        return record_str
