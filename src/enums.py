from enum import Enum
from typing import Optional

def key_is_in(s: str, enum_class: Enum) -> bool:
    return s in enum_class._member_map_

def val_is_in(s: str, enum_class: Enum) -> bool:
    return s in enum_class._value2member_map_

def key_of(value: str, enum_class: Enum) -> Optional[str]:
    return enum_class._value2member_map_[value] if val_is_in(value, enum_class) else None

def value_of(key: str, enum_class: Enum) -> Optional[str]:
    return enum_class._member_map_[key].value if key_is_in(key, enum_class) else None

months = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

class ByteOrderMark(Enum):
    '''
    Represents the byte order marks that might be present in a GEDCOM file.
    These are used to indicate the endianness of the file.
    '''
    _32_BIT_BIG_ENDIAN: int = 0
    _32_BIT_LITTLE_ENDIAN: int = 1
    _16_BIT_BIG_ENDIAN: int = 2
    _16_BIT_LITTLE_ENDIAN: int = 3
    _8_BIT: int = 4

class NoticeType(Enum):
    '''
    Represents the types of notices that can be generated during parsing.
    These types are used to indicate the severity of the notice.
    '''
    ERROR: int = 0
    WARNING: int = 1

class NameType(Enum):
    '''
    Represents the different types of names and individual might have.
    These types are defined in the GEDCOM 5.5.5 specification.
    '''
    MAIN: str = 'main'
    AKA: str = 'aka'
    BIRTH: str = 'birth'
    IMMIGRANT: str = 'immigrant'
    MAIDEN: str = 'maiden'
    MARRIED: str = 'married'

name_to_str = {
    'main': 'Main',
    'aka': 'Also Known As',
    'birth': 'Birth',
    'immigrant': 'Immigrant',
    'maiden': 'Maiden',
    'married': 'Married'
}

class Sex(Enum):
    '''
    Represents the sex of an individual in a GEDCOM file.
    These values are defined in the GEDCOM 5.5.5 specification.
    '''
    M: str = 'M'
    F: str = 'F'
    U: str = 'U'
    X: str = 'X'
    N: str = 'N'

sex_to_str = {
    'M': 'Male',
    'F': 'Female',
    'U': 'Unknown',
    'X': 'Intersex',
    'N': 'Not Record'
}

class Tag(Enum):
    '''
    Represents the tags used in GEDCOM files.
    These tags are defined in the GEDCOM 5.5.5
    specification except for SSN and FSID.
    '''
    GEDC: str = 'GEDC'
    HEAD: str = 'HEAD'
    TRLR: str = 'TRLR'
    VERS: str = 'VERS'
    DEST: str = 'DEST'
    SOUR: str = 'SOUR'
    CORP: str = 'CORP'
    DATA: str = 'DATA'
    DATE: str = 'DATE'
    COMM: str = 'COMM'
    COPR: str = 'COPR'
    TIME: str = 'TIME'
    LANG: str = 'LANG'
    SUBM: str = 'SUBM'
    FILE: str = 'FILE'
    NOTE: str = 'NOTE'
    FAM: str = 'FAM'
    HUSB: str = 'HUSB'
    WIFE: str = 'WIFE'
    MARR: str = 'MARR'
    CHIL: str = 'CHIL'
    NCHI: str = 'NCHI'
    REFN: str = 'REFN'
    TYPE: str = 'TYPE'
    FONE: str = 'FONE'
    RIN: str = 'RIN'
    INDI: str = 'INDI'
    SEX: str = 'SEX'
    OBJE: str = 'OBJE'
    TITL: str = 'TITL'
    REPO: str = 'REPO'
    PLAC: str = 'PLAC'
    AGNC: str = 'AGNC'
    AUTH: str = 'AUTH'
    ABBR: str = 'ABBR'
    TEXT: str = 'TEXT'
    ADDR: str = 'ADDR'
    ADR1: str = 'ADR1'
    ADR2: str = 'ADR2'
    ADR3: str = 'ADR3'
    CITY: str = 'CITY'
    STAE: str = 'STAE'
    POST: str = 'POST'
    COUN: str = 'COUN'
    PHON: str = 'PHON'
    EMAIL: str = 'EMAIL'
    FAX: str = 'FAX'
    WWW: str = 'WWW'
    ASSOC: str = 'ASSOC'
    RELA: str = 'RELA'
    CHAN: str = 'CHAN'
    FAMC: str = 'FAMC'
    PEDI: str = 'PEDI'
    CAUS: str = 'CAUS'
    AGE: str = 'AGE'
    ANUL: str = 'ANUL'
    CENS: str = 'CENS'
    DIV: str = 'DIV'
    DIVF: str = 'DIVF'
    ENGA: str = 'ENGA'
    MARB: str = 'MARB'
    MARC: str = 'MARC'
    MARL: str = 'MARL'
    MARS: str = 'MARS'
    RESI: str = 'RESI'
    EVEN: str = 'EVEN'
    CAST: str = 'CAST'
    DESC: str = 'DESC'
    EDUC: str = 'EDUC'
    IDNO: str = 'IDNO'
    NATI: str = 'NATI'
    NAME: str = 'NAME'
    RELN: str = 'RELN'
    OCCU: str = 'OCCU'
    POSS: str = 'POSS'
    RELI: str = 'RELI'
    FACT: str = 'FACT'
    BIRT: str = 'BIRT'
    CHR: str = 'CHR'
    DEAT: str = 'DEAT'
    BURI: str = 'BURI'
    CREM: str = 'CREM'
    ADOP: str = 'ADOP'
    BAPM: str = 'BAPM'
    BARM: str = 'BARM'
    BASM: str = 'BASM'
    CHRA: str = 'CHRA'
    CONF: str = 'CONF'
    CONT: str = 'CONT'
    FCOM: str = 'FCOM'
    NATU: str = 'NATU'
    EMIG: str = 'EMIG'
    IMMI: str = 'IMMI'
    PROB: str = 'PROB'
    WILL: str = 'WILL'
    GRAD: str = 'GRAD'
    RETI: str = 'RETI'
    NPFX: str = 'NPFX'
    GIVN: str = 'GIVN'
    NICK: str = 'NICK'
    SPFX: str = 'SPFX'
    SURN: str = 'SURN'
    NSFX: str = 'NSFX'
    ROMN: str = 'ROMN'
    MAP: str = 'MAP'
    LATI: str = 'LATI'
    LONG: str = 'LONG'
    PAGE: str = 'PAGE'
    ROLE: str = 'ROLE'
    CERT: str = 'CERT'
    MEDI: str = 'MEDI'
    FAMS: str = 'FAMS'
    CHAR: str = 'CHAR'
    FORM: str = 'FORM'
    CTRY: str = 'CTRY'
    CONC: str = 'CONC'
    PUBL: str = 'PUBL'
    ALIA: str = 'ALIA'
    SSN: str = 'SSN'
    FSID: str = 'FSID'

class ObsoleteTag(Enum):
    '''
    Represents tags that are no longer in use in GEDCOM files.
    These tags may still appear in older GEDCOM files.
    They are not used in the current GEDCOM 5.5.5 specification.
    '''
    SSN: str = 'SSN'
    FSID: str = 'FSID'

indi_event_type = {
    Tag.BIRT.value: 'Birth',
    Tag.DEAT.value: 'Death',
    Tag.BURI.value: 'Burial',
    Tag.CREM.value: 'Cremation',
    Tag.NATU.value: 'Naturalization',
    Tag.EMIG.value: 'Emigration',
    Tag.IMMI.value: 'Immigration',
    Tag.ADOP.value: 'Adoption',
    Tag.BAPM.value: 'Baptism',
    Tag.BARM.value: 'Bar Mitzvah',
    Tag.BASM.value: 'Bas Mitzvah',
    Tag.CHRA.value: 'Christening',
    Tag.CONF.value: 'Confirmation',
    Tag.FCOM.value: 'First Communion',
    Tag.CENS.value: 'Census',
    Tag.PROB.value: 'Probate',
    Tag.WILL.value: 'Will',
    Tag.GRAD.value: 'Graduation',
    Tag.RETI.value: 'Retirement',
    Tag.CHR.value: 'Adult Christening',
    Tag.EVEN.value: ''
}

class JSONField(Enum):
    '''
    Represents the fields that can be included in the JSON output.
    These fields correspond to the attributes of the entities in the GEDCOM file.
    '''
    IND: int = 0
    FAM: int = 1