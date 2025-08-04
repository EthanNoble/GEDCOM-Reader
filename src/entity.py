'''
Entity classes for representing GEDCOM data structures.
'''

import json
from typing import Any, List, Dict
from typing import cast
from datetime import date
from dateutil.parser import parse

from src import enums


class Record:
    '''
    A record line.
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
            if isinstance(value, dict):
                value_dict = cast(Dict[str, Any], value)
                return {
                    k: v_ser for k, v in value_dict.items()
                    if not is_empty(v_ser := serialize(v))
                } or None
            if isinstance(value, list):
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
    The header of a GEDCOM file, which contains metadata of the file.
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
            'placeRecordHierarchy': [],
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

    def set_source_data_publication_date(self, pub_date: EntityContainer) -> None:
        self._data['source']['sourceData']['publicationDate'] = pub_date

    def set_source_data_copyright(self, value: str) -> None:
        self._data['source']['sourceData']['sourceDataCopyright'] = value

    def set_receiving_system(self, value: str) -> None:
        self._data['receivingSystem'] = value

    def set_transmission_date(self, trans_date: EntityContainer) -> None:
        self._data['transmissionDate'] = trans_date

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

    def set_place_hierarchy(self, hierarchies: List[str]) -> None:
        self._data['placeRecordHierarchy'] = hierarchies

    def set_note(self, value: str) -> None:
        self._data['note'] = value


class Name(EntityContainer):
    '''
    The name of an individual, which can have multiple parts.
    '''
    def __init__(self, name_type: enums.NameType = enums.NameType.MAIN):
        super().__init__({
            'nameType': name_type,
            'lineValueName': '',
            'structuredParts': [
                {'type':       'Surname', 'value': ''},
                {'type':        'Prefix', 'value': ''},
                {'type':         'Given', 'value': ''},
                {'type':      'Nickname', 'value': ''},
                {'type': 'SurnamePrefix', 'value': ''},
                {'type':        'Suffix', 'value': ''},
            ]
        })
    def set_name_type(self, name_type: enums.NameType) -> None:
        self._data['nameType'] = name_type
    def set_line_value_name(self, value: str) -> None:
        self._data['lineValueName'] = value
    def set_structured_part(self, part_type: enums.NamePartType, value: str) -> None:
        for part in self._data['structuredParts']:
            if part['type'] == part_type.value:
                part['value'] = value
                break


class Place(EntityContainer):
    '''
    A place.
    '''
    def __init__(self):
        super().__init__({
            'name': '',
            'hierarchy': []
        })
    
    def add_hierarchy(self, item: str) -> None:
        self._data['hierarchy'].append(item)

    def set_name(self, name: str) -> None:
        self._data['name'] = name


class Event(EntityContainer):
    def __init__(self, data: Dict[str, Any] = {}):
        super().__init__(data | {
            'explicitEventType': '',    # This is the event record tag
            'genericEventType': '',     # User given with TYPE if explicitEventType is EVEN or FACT
            'eventDate': '',
            'eventPlace': '',
            'eventAddress': '',
            'responsibleAgency': '',
            'religiousAffiliation': '',
            'eventCause': '',
            'eventRestrictionNotice': enums.Restriction.NONE,
            'eventNote': '',
            'eventSourceCitation': '',
            'eventMultimediaLink': ''
        })

    def set_explicit_event_type(self, value: str) -> None:
        self._data['explicitEventType'] = value

    def set_generic_event_type(self, value: str) -> None:
        self._data['genericEventType'] = value

    def set_event_date(self, event_date: str | EntityContainer) -> None:
        self._data['eventDate'] = event_date

    def set_event_place(self, place: Place) -> None:
        self._data['eventPlace'] = place

    def set_event_address(self, address: EntityContainer) -> None:
        self._data['eventAddress'] = address

    def set_responsible_agency(self, agency: str) -> None:
        self._data['responsibleAgency'] = agency

    def set_religious_affiliation(self, affiliation: str) -> None:
        self._data['religiousAffiliation'] = affiliation

    def set_cause_of_event(self, cause: str) -> None:
        self._data['eventCause'] = cause

    def set_restriction_notice(self, restriction: enums.Restriction) -> None:
        self._data['eventRestrictionNotice'] = restriction

    def set_event_note(self, note: str) -> None:
        self._data['eventNote'] = note

    def set_source_citation(self, citation: str) -> None:
        self._data['eventSourceCitation'] = citation

    def set_multimedia_link(self, link: str) -> None:
        self._data['eventMultimediaLink'] = link


class IndividualEvent(Event):
    '''
    An event in an individual's life.
    '''
    def __init__(self):
        super().__init__({
            'ageAtEvent': '',
            'childOfFamilyCrossReferenceId': '',
            'adoptedByCrossReferenceId': ''
        })

    def set_age_at_event(self, age: str) -> None:
        self._data['ageAtEvent'] = age

    def set_child_of_family_cross_reference_id(self, cross_ref_id: str) -> None:
        self._data['childOfFamilyCrossReferenceId'] = cross_ref_id

    def set_adopted_by_cross_reference_id(self, cross_ref_id: str) -> None:
        self._data['adoptedByCrossReferenceId'] = cross_ref_id


class FamilyEvent(Event):
    '''
    An event in a family.
    '''
    def __init__(self):
        super().__init__({
            'parentOneAgeAtEvent': '',
            'parentTwoAgeAtEvent': '',
        })

    def set_parent_one_age_at_event(self, age: str) -> None:
        self._data['parentOneAgeAtEvent'] = age

    def set_parent_two_age_at_event(self, age: str) -> None:
        self._data['parentTwoAgeAtEvent'] = age


class Attribute(Event):
    '''
    An attribute of an individual.
    '''
    def __init__(self):
        super().__init__({
            'attribute': {
                'type': '',
                'value': ''
            },
        })


class Individual(EntityContainer):
    '''
    An individual. Can reference multiple Name and Event instances.
    '''
    def __init__(self, cross_ref_id: str):
        super().__init__({
            'crossReferenceId': cross_ref_id,
            'restrictionNotice': enums.Restriction.NONE,
            'names': [],
            'sex': enums.Sex.UNKNOWN,
            'isDead': False,
            'events': [],
            'attributes': [],
            'parentOne': '',
            'parentTwo': '',
        })
    
    def add_event(self, event: IndividualEvent) -> None:
        self._data['events'].append(event)

    def add_attribute(self, event: Attribute) -> None:
        self._data['attributes'].append(event)

    def add_name(self, name: Name) -> None:
        self._data['names'].append(name)

    def set_cross_reference_id(self, cross_ref_id: str) -> None:
        self._data['crossReferenceId'] = cross_ref_id

    def set_sex(self, sex: enums.Sex) -> None:
        self._data['sex'] = sex

    def set_is_dead(self, is_dead: bool) -> None:
        self._data['isDead'] = is_dead

    def set_parent_one(self, parent_one: str) -> None:
        self._data['parentOne'] = parent_one

    def set_parent_two(self, parent_two: str) -> None:
        self._data['parentTwo'] = parent_two


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


class Family(EntityContainer):
    '''
    A family. Can reference two parents and multiple children (Individual instances).
    '''
    def __init__(self, cross_ref_id: str | None = None):
        super().__init__({
            'crossReferenceId': cross_ref_id,
            'restrictionNotice': enums.Restriction.NONE,
            'events': [],
            'parentOne': '',
            'parentTwo': '',
            'children': [],
            'numberOfChildren': '',
            'submittedBy': '',
            'userReference': {
                'number': '',
                'type': ''
            },
            'systemRecordId': '',
            'lastChanged': {
                'dateTime': '',
                'note': ''
            }
        })

    def add_child(self, child: Individual) -> None:
        self._data['children'].append(child)

    def set_cross_reference_id(self, cross_ref_id: str) -> None:
        self._data['crossReferenceId'] = cross_ref_id

    def set_parent_one(self, parent_one: str) -> None:
        self._data['parentOne'] = parent_one

    def set_parent_two(self, parent_two: str) -> None:
        self._data['parentTwo'] = parent_two
