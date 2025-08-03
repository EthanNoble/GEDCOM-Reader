'''
Entity classes for representing GEDCOM data structures.
'''

import json
from typing import Any, List, Dict
from typing import cast
from datetime import date
from dateutil.parser import parse

from src import enums


class EntityContainer:
    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data
    
    def jsonify(self) -> str:
        '''
        Serializes the container's data to json and prunes keys that have empty values.
        An empty value is any value that contains `None`, `''`, `[]`, or `{}`.
        Returns:
            str: The JSON serialized string
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
        '''
        Gets the data of this container. It is recomended to use the
        `jsonify` method of this container to retrieve the data instead.
        Returns:
            Dict[str, Any]: The container's data
        '''
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
            'source': {
                'version': '',
                'systemId': '',
                'productName': '',
                'corporation': {
                    'businessName': '',
                    'businessAddress': ''
                },
                'sourceData': {
                    'sourceName': '',
                    'publicationDate': '',
                    'sourceDataCopyright': ''
                }
            },
            'receivingSystem': '',
            'transmissionDate': '',
            'submittingTo': '',
            'submittedBy': '',
            'fileName': '',
            'gedcomFileCopyright': '',
            'gedcomFileMeta': {
                'version': '',
                'form': '',
            },
            'characterSet': {
                'version': '',
                'charSetType': ''
            },
            'language': '',
            'place': '',
            'note': ''
        })
    
    def set_source_version(self, value: str) -> None:
        self._data['source']['version'] = value

    def set_source_system_id(self, value: str) -> None:
        self._data['source']['systemId'] = value

    def set_source_product_name(self, value: str) -> None:
        self._data['source']['productName'] = value

    def set_source_corporation_business_name(self, value: str) -> None:
        self._data['source']['corporation']['businessName'] = value

    def set_source_corporation_business_address(self, address: EntityContainer) -> None:
        self._data['source']['corporation']['businessAddress'] = address

    def set_source_data_source_name(self, value: str) -> None:
        self._data['source']['sourceData']['sourceName'] = value

    def set_source_data_publication_date(self, date: EntityContainer) -> None:
        self._data['source']['sourceData']['publicationDate'] = date

    def set_source_data_copyright(self, value: str) -> None:
        self._data['source']['sourceData']['sourceDataCopyright'] = value

    def set_receiving_system(self, value: str) -> None:
        self._data['receivingSystem'] = value

    def set_transmission_date(self, date: EntityContainer) -> None:
        self._data['transmissionDate'] = date

    def set_submitting_to(self, value: str) -> None:
        self._data['submittingTo'] = value

    def set_submitted_by(self, value: str) -> None:
        self._data['submittedBy'] = value

    def set_file_name(self, value: str) -> None:
        self._data['fileName'] = value

    def set_gedcom_file_copyright(self, value: str) -> None:
        self._data['gedcomFileCopyright'] = value
    
    def set_gedcom_file_meta_version(self, value: str) -> None:
        self._data['gedcomFileMeta']['version'] = value

    def set_gedcom_file_meta_form(self, value: str) -> None:
        self._data['gedcomFileMeta']['form'] = value
    
    def set_character_set_version(self, value: str) -> None:
        self._data['characterSet']['version'] = value

    def set_character_set_type(self, value: str) -> None:
        self._data['characterSet']['charSetType'] = value

    def set_language(self, value: str) -> None:
        self._data['language'] = value

    def set_place(self, value: str) -> None:
        self._data['place'] = value

    def set_note(self, value: str) -> None:
        self._data['note'] = value


class Date(EntityContainer):
    '''
    A date which can be parsed from a string.
    '''
    def __init__(self, date_str: str):
        self._date: date = parse(date_str, fuzzy=True)

        super().__init__({
            # TODO: There will be more stuff to parse from a date
            'parsedDate': str(self),
        })

    def __str__(self):
        return self._date.strftime('%Y-%m-%d')


class Address(EntityContainer):
    '''
    An address.
    '''
    def __init__(self):
        super().__init__({
            'addressLines': [],
            'cityAddress': '',
            'stateAddress': '',
            'zipCode': '',
            'countryAddress': '',
            'phoneNumber': '',
            'emailAddress': '',
            'faxAddress': '',
            'webAddress': '',
        })

    def add_address_line(self, addr: str) -> None:
        self._data['addressLines'].append(addr)

    def set_city_address(self, city: str) -> None:
        self._data['cityAddress'] = city

    def set_state_address(self, state: str) -> None:
        self._data['stateAddress'] = state

    def set_zip_code(self, zip_code: str) -> None:
        self._data['zipCode'] = zip_code

    def set_country_address(self, country: str) -> None:
        self._data['countryAddress'] = country

    def set_phone_number(self, phone: str) -> None:
        self._data['phoneNumber'] = phone

    def set_email_address(self, email: str) -> None:
        self._data['emailAddress'] = email

    def set_fax_address(self, fax: str) -> None:
        self._data['faxAddress'] = fax

    def set_web_address(self, web: str) -> None:
        self._data['webAddress'] = web


class Place:
    '''
    A place.
    '''
    def __init__(self):
        self.name: str | None = None
        self.latitude: str | None = None
        self.longitude: str | None = None

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
            self.surname: str | None = None
            # From a NPFX sub record of NAME
            self.prefix: str | None = None
            # From a GIVN sub record of NAME
            self.given: str | None = None
            # From a NICK sub record of NAME
            self.nickname: str | None = None
            # From a SPFX sub record of NAME
            self.surname_prefix: str | None = None
            # From a NSFX sub record of NAME
            self.suffix: str | None = None

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

    def __init__(self, indi_id: str | None = None):
        self.indi_id: str | None = indi_id
        self.names: List[Individual.Name] = []
        self.sex: enums.Sex = enums.Sex.UNKNOWN
        self._events: List[Event] = []
        self.dead: bool = False

        self.parent1: Individual | None = None
        self.parent2: Individual | None = None

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
    def __init__(self, fam_id: str | None = None):
        self.fam_id: str | None = fam_id
        self.parent1: Individual | None = None
        self.parent2: Individual | None = None
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
            'children': [child.indi_id for child in self._children]
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
        self.individual: Individual | None = None

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
