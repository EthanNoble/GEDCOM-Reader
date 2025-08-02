from typing import List
from typing import Optional
from dateutil.parser import parse
from datetime import datetime

import src.enums as enums

class Address:
    def __init__(self):
        self._addresses: List[str] = []
        self.city: str = ''
        self.state: str = ''
        self.postal: str = ''
        self.country: str = ''
    
    def jsonify(self):
        return {
            'addresses': [addr for addr in self._addresses],
            'city': self.city,
            'state': self.state,
            'postal': self.postal,
            'country': self.country
        }

    def add_address(self, addr: str) -> None:
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
    def __init__(self):
        self.name: Optional[str] = None
        self.latitude: Optional[str] = None
        self.longitude: Optional[str] = None
    
    def jsonify(self):
        if not self.name and not self.latitude and not self.longitude:
            return None
        
        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

class Event:
    def __init__(self, type: Optional[str] = None):
        self.type: Optional[str] = type
        self.date: Optional[Date] = None
        self.address: Optional[Address] = None
        self.place: Optional[Place] = None
        self.note: Optional[str] = None
    
    def jsonify(self):
        if not self.date and not self.address:
            return None
        
        return {
            'type': self.type,
            'date': self.date.jsonify() if self.date else None,
            'place': self.place.jsonify() if self.place else None,
            'address': self.address.jsonify() if self.address else None,
            'note': self.note
        }

class Date(object):
    def __init__(self, date: Optional[str] = None):
        self._raw_date_str: str = date
        self._date: Optional[datetime] = None
        if date:
            self._parse_date()
    
    def jsonify(self):
        return {
            'original': self._raw_date_str,
            'date': str(self) if self._date else None,
            'day': self.day(),
            'month': self.month(),
            'year': self.year()
        }

    def set_date(self, date: str):
        self._raw_date_str = date
        self._parse_date()
    
    def day(self) -> Optional[int]:
        return self._date.day if self._date else None
    
    def month(self) -> Optional[int]:
        return self._date.month if self._date else None
    
    def year(self) -> Optional[int]:
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

class Header(object):
    def __init__(self):
        self.source: Optional[str] = None
        self.date: Optional[Date] = None
        self.gedcom_version: Optional[str] = None
        self.submission: Optional[str] = None
        self.submitter: Optional[str] = None
    
    def jsonify(self):
        return {
            'source': self.source,
            'date': self.date.jsonify() if self.date else None,
            'gedcom_version': self.gedcom_version,
            'submission': self.submission,
            'submitter': self.submitter
        }

class Individual(object):
    class Name(object):
        def __init__(self, name_type: int = enums.NameType.MAIN):
            # Enum data.NameType
            self.type: int = name_type
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
        
        def jsonify(self):
            parts_list: List[str] = []
            if self.surname:
                parts_list.append({'type': 'Surname', 'value': self.surname})
            if self.prefix:
                parts_list.append({'type': 'Prefix', 'value': self.prefix})
            if self.given:
                parts_list.append({'type': 'Given', 'value': self.given})
            if self.nickname:
                parts_list.append({'type': 'Nickname', 'value': self.nickname})
            if self.surname_prefix:
                parts_list.append({'type': 'SurnamePrefix', 'value': self.surname_prefix})
            if self.suffix:
                parts_list.append({'type': 'Suffix', 'value': self.suffix})
                
            name_object: dict[str, Optional[str]] = {
                'type': enums.name_to_str[self.type.value],
                'name': ' '.join(self.unstructured_name_parts) if len(self.unstructured_name_parts) > 0 else None,
                'parts': parts_list if len(parts_list) > 0 else None
            }

            return name_object

    def __init__(self, id: Optional[str] = None):
        self.id: Optional[str] = id
        self.names: List[Individual.Name] = []
        self.sex: str = enums.Sex.U # Enum data.Sex
        self._events: List[Event] = []
        self.dead: bool = False

        self.parent1: Optional[Individual] = None
        self.parent2: Optional[Individual] = None
    
    def jsonify(self):
        return {
            'id': self.id,
            'names': [name.jsonify() for name in self.names] if len(self.names) > 0 else None,
            'sex': enums.sex_to_str[self.sex.value],
            'is_dead': self.dead,
            'events': [event.jsonify() for event in self._events] if len(self._events) > 0 else None,
        }
    
    def add_event(self, event: Event) -> None:
        self._events.append(event)
    
class Family(object):
    def __init__(self, id: Optional[str] = None):
        self.id: Optional[str] = id
        self.parent1: Optional[Individual] = None
        self.parent2: Optional[Individual] = None
        self._children: List[Individual] = []
    
    def jsonify(self):
        return {
            'id': self.id,
            'parent1': self.parent1.id if self.parent1 else None,
            'parent2': self.parent2.id if self.parent2 else None,
            'children': [child.id for child in self._children] if len(self._children) > 0 else None
        }

    def add_child(self, child: Individual) -> None:
        self._children.append(child)

class Record(object):
    def __init__(self, level: int):
        self.level: int = level
        self.tag: str = '' # Enum data.Tag
        self.line_value: str = ''

        self.cross_ref_id: str = ''
        self.cross_ref_ptr: str = ''

        self._ignorable = False

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
