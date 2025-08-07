'''
Entity classes for representing GEDCOM data structures.
'''

from typing import Any, List, Dict
from typing import cast

from src import enums
from src import mappings


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
    
    def prune_data(self) -> Dict[str, Any]:
        '''
        Prunes keys that have empty values. An empty value
        is any value that contains `None`, `''`, `[]`, or `{}`.
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

        cleaned_data: Dict[str, Any] = {}
        for key, value in self._data.items():
            serialized_value = serialize(value)
            if serialized_value is not None:
                cleaned_data[key] = serialized_value

        return cleaned_data

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


class NamePiece(EntityContainer):
    '''
    A piece of a name, such as a surname or given name.
    '''
    def __init__(self):
        super().__init__({
            'surname': '',
            'prefix': '',
            'given': '',
            'nickname': '',
            'surnamePrefix': '',
            'suffix': ''
        })

    def set_surname(self, surname: str) -> None:
        self._data['surname'] = surname

    def set_prefix(self, prefix: str) -> None:
        self._data['prefix'] = prefix

    def set_given(self, given: str) -> None:
        self._data['given'] = given

    def set_nickname(self, nickname: str) -> None:
        self._data['nickname'] = nickname

    def set_surname_prefix(self, surname_prefix: str) -> None:
        self._data['surnamePrefix'] = surname_prefix

    def set_suffix(self, suffix: str) -> None:
        self._data['suffix'] = suffix


class Name(EntityContainer):
    '''
    The name of an individual, which can have multiple parts.
    '''

    def __init__(self, name_type: enums.NameType = enums.NameType.MAIN):
        super().__init__({
            'name': {
                'type': name_type,
                'value': '',
                'namePieces': NamePiece(),
                'nameNote': '',
                'nameSourceCitation': '',
            },
            'phoneticVariation': {
                'type': enums.PhoneticType.NONE,
                'value': '',
                'phoneticNamePieces': NamePiece(),
                'phoneticNote': '',
                'phoneticSourceCitation': '',
            },
            'romanizedVariation': {
                'type': enums.RomanizedType.NONE,
                'value': '',
                'romanizedNamePieces': NamePiece(),
                'romanizedNote': '',
                'romanizedSourceCitation': '',
            }
        })

    def set_name_type(self, name_type: enums.NameType) -> None:
        self._data['name']['type'] = name_type

    def set_name_value(self, value: str) -> None:
        self._data['name']['value'] = value
    
    def set_name_pieces(self, name_pieces: NamePiece) -> None:
        self._data['name']['namePieces'] = name_pieces
    
    def set_name_note(self, note: str) -> None:
        self._data['name']['nameNote'] = note
    
    def set_name_source_citation(self, citation: str) -> None:
        self._data['name']['nameSourceCitation'] = citation

    def set_phonetic_type(self, phonetic_type: enums.PhoneticType) -> None:
        self._data['phoneticVariation']['type'] = phonetic_type

    def set_phonetic_value(self, value: str) -> None:
        self._data['phoneticVariation']['value'] = value

    def set_phonetic_name_pieces(self, phonetic_name_pieces: NamePiece) -> None:
        self._data['phoneticVariation']['phoneticNamePieces'] = phonetic_name_pieces
    
    def set_phonetic_note(self, note: str) -> None:
        self._data['phoneticVariation']['phoneticNote'] = note
    
    def set_phonetic_source_citation(self, citation: str) -> None:
        self._data['phoneticVariation']['phoneticSourceCitation'] = citation

    def set_romanized_type(self, romanized_type: enums.RomanizedType) -> None:
        self._data['romanizedVariation']['type'] = romanized_type
    
    def set_romanized_value(self, value: str) -> None:
        self._data['romanizedVariation']['value'] = value

    def set_romanized_name_pieces(self, romanized_name_pieces: NamePiece) -> None:
        self._data['romanizedVariation']['romanizedNamePieces'] = romanized_name_pieces
    
    def set_romanized_note(self, note: str) -> None:
        self._data['romanizedVariation']['romanizedNote'] = note
    
    def set_romanized_source_citation(self, citation: str) -> None:
        self._data['romanizedVariation']['romanizedSourceCitation'] = citation


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
            'lineValue': '',            # The value of the line, if any
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
    
    def set_line_value(self, value: str) -> None:
        self._data['lineValue'] = value

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

    def set_type(self, attr_type: str) -> None:
        self._data['attribute']['type'] = attr_type

    def set_value(self, value: str) -> None:
        self._data['attribute']['value'] = value


class Individual(EntityContainer):
    '''
    An individual. Can reference multiple Name and Event instances.
    '''
    def __init__(self, cross_ref_id: str):
        super().__init__({
            'crossReferenceId': cross_ref_id,
            'individualRestrictionNotice': enums.Restriction.NONE,
            'names': [],
            'sex': enums.Sex.UNKNOWN,
            'isDead': False,
            'individualEvents': [],
            'individualAttributes': [],
            'childToFamilyLink': {
                'familyCrossReferenceId': '',
                'pedigreeLinkageType': enums.PedigreeLinkageType.NONE,
                'childLinkageStatus': enums.ChildLinkageStatus.NONE,
                'note': ''
            },
            'spouseToFamilyLink': {
                'familyCrossReferenceId': '',
                'note': ''
            },
            'parentOne': '',
            'parentTwo': '',
            'association': '',
            'submittedBy': '',
            'aliasCrossReferenceId': '',
            'ancestorResearchInterestCrossReferenceId': '',
            'descendantResearchInterestCrossReferenceId': '',
            'permanentFileNumber': '',
            'ancestralFileNumber': '',
            'userReference': {
                'number': '',
                'type': ''
            },
            'systemRecordId': '',
            'lastChanged': {
                'dateTime': '',
                'note': ''
            },
            'individualNote': '',
            'individualSourceCitation': '',
            'individualMultimediaLink': ''
        })
    
    def add_name(self, name: Name) -> None:
        self._data['names'].append(name)
    
    def add_individual_event(self, event: IndividualEvent) -> None:
        self._data['individualEvents'].append(event)
    
    def add_individual_attribute(self, attribute: Attribute) -> None:
        self._data['individualAttributes'].append(attribute)

    def set_cross_reference_id(self, cross_ref_id: str) -> None:
        self._data['crossReferenceId'] = cross_ref_id

    def set_individual_restriction_notice(self, restriction: enums.Restriction) -> None:
        self._data['individualRestrictionNotice'] = restriction

    def set_sex(self, sex: enums.Sex) -> None:
        self._data['sex'] = sex

    def set_is_dead(self, is_dead: bool) -> None:
        self._data['isDead'] = is_dead

    def set_parent_one(self, parent_one: str) -> None:
        self._data['parentOne'] = parent_one

    def set_parent_two(self, parent_two: str) -> None:
        self._data['parentTwo'] = parent_two

    def set_association(self, association: str) -> None:
        self._data['association'] = association

    def set_submitted_by(self, submitted_by: str) -> None:
        self._data['submittedBy'] = submitted_by

    def set_alias_cross_reference_id(self, alias_id: str) -> None:
        self._data['aliasCrossReferenceId'] = alias_id

    def set_ancestor_research_interest_cross_reference_id(self, ancestor_id: str) -> None:
        self._data['ancestorResearchInterestCrossReferenceId'] = ancestor_id

    def set_descendant_research_interest_cross_reference_id(self, descendant_id: str) -> None:
        self._data['descendantResearchInterestCrossReferenceId'] = descendant_id

    def set_permanent_file_number(self, file_number: str) -> None:
        self._data['permanentFileNumber'] = file_number

    def set_ancestral_file_number(self, file_number: str) -> None:
        self._data['ancestralFileNumber'] = file_number

    def set_system_record_id(self, record_id: str) -> None:
        self._data['systemRecordId'] = record_id

    def set_individual_note(self, note: str) -> None:
        self._data['individualNote'] = note

    def set_individual_source_citation(self, citation: str) -> None:
        self._data['individualSourceCitation'] = citation

    def set_individual_multimedia_link(self, link: str) -> None:
        self._data['individualMultimediaLink'] = link

    def set_child_to_family_link_family_cross_reference_id(self, family_cross_ref_id: str) -> None:
        self._data['childToFamilyLink']['familyCrossReferenceId'] = family_cross_ref_id

    def set_child_to_family_link_pedigree_linkage_type(self, pedigree_linkage_type: enums.PedigreeLinkageType) -> None:
        self._data['childToFamilyLink']['pedigreeLinkageType'] = pedigree_linkage_type

    def set_child_to_family_link_child_linkage_status(self, child_linkage_status: enums.ChildLinkageStatus) -> None:
        self._data['childToFamilyLink']['childLinkageStatus'] = child_linkage_status

    def set_child_to_family_link_note(self, note: str) -> None:
        self._data['childToFamilyLink']['note'] = note

    def set_spouse_to_family_link_family_cross_reference_id(self, family_cross_ref_id: str) -> None:
        self._data['spouseToFamilyLink']['familyCrossReferenceId'] = family_cross_ref_id

    def set_spouse_to_family_link_note(self, note: str) -> None:
        self._data['spouseToFamilyLink']['note'] = note

    def set_user_reference_number(self, number: str) -> None:
        self._data['userReference']['number'] = number

    def set_user_reference_type(self, ref_type: str) -> None:
        self._data['userReference']['type'] = ref_type

    def set_last_changed_date_time(self, date_time: str) -> None:
        self._data['lastChanged']['dateTime'] = date_time

    def set_last_changed_note(self, note: str) -> None:
        self._data['lastChanged']['note'] = note


class Date(EntityContainer):
    '''
    A date which can be parsed from a string.
    '''
    values: Dict[str, str] = {
        'day': '',
        'month': '',
        'year': '',
        'isBC': '',
    }

    def __init__(self):
        super().__init__({
            'calendar': enums.CalendarType.GREGORIAN,
            'type': enums.DateType.REGULAR,

            # Phrase Type
            'phrase': '',

            # Regular Type
            'approximationType': enums.DateApproximated.NONE,
            'day': '',
            'month': '',
            'year': '',
            'julianAlternativeYear': '',
            'isBC': 'N',

            # Period Type
            'fromDate': Date.values.copy(),
            'toDate': Date.values.copy(),
            
            # Range Type
            'before': Date.values.copy(),
            'after': Date.values.copy(),
            'between': {
                'start': Date.values.copy(),
                'end': Date.values.copy()
            }
        })
    
    def set_calendar(self, calendar: enums.CalendarType) -> None:
        self._data['calendar'] = calendar

    def get_calendar(self) -> enums.CalendarType:
        return enums.CalendarType(self._data['calendar'])
    
    def set_type(self, date_type: enums.DateType) -> None:
        self._data['type'] = date_type

    def get_type(self) -> enums.DateType:
        return enums.DateType(self._data['type'])

    def set_approximation(self, approx: enums.DateApproximated) -> None:
        self._data['approximationType'] = approx
    
    def set_regular_day(self, day: int) -> None:
        self._data['day'] = day

    def set_regular_month(self, month: enums.Month | enums.MonthHebrew | enums.MonthFrench) -> None:
        self._data['month'] = month

    def set_regular_year(self, year: int) -> None:
        self._data['year'] = year
    
    def set_regular_julian_alternative_year(self, year: int) -> None:
        self._data['julianAlternativeYear'] = year

    def set_regular_is_bc(self, is_bc: bool) -> None:
        self._data['isBC'] = 'Y' if is_bc else 'N'

    def set_phrase(self, phrase: str) -> None:
        self._data['phrase'] = phrase


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
    
    def add_event(self, event: FamilyEvent) -> None:
        self._data['events'].append(event)

    def add_child(self, child: Individual) -> None:
        self._data['children'].append(child)

    def set_cross_reference_id(self, cross_ref_id: str) -> None:
        self._data['crossReferenceId'] = cross_ref_id

    def set_parent_one(self, parent: Individual) -> None:
        self._data['parentOne'] = parent

    def set_parent_two(self, parent: Individual) -> None:
        self._data['parentTwo'] = parent

    def set_restriction_notice(self, restriction: enums.Restriction) -> None:
        self._data['restrictionNotice'] = restriction

    def set_number_of_children(self, number: str) -> None:
        self._data['numberOfChildren'] = number

    def set_submitted_by(self, submitted_by: str) -> None:
        self._data['submittedBy'] = submitted_by

    def set_system_record_id(self, record_id: str) -> None:
        self._data['systemRecordId'] = record_id

    def set_user_reference_number(self, number: str) -> None:
        self._data['userReference']['number'] = number

    def set_user_reference_type(self, ref_type: str) -> None:
        self._data['userReference']['type'] = ref_type

    def set_last_changed_date_time(self, date_time: str) -> None:
        self._data['lastChanged']['dateTime'] = date_time

    def set_last_changed_note(self, note: str) -> None:
        self._data['lastChanged']['note'] = note
