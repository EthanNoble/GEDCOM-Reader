'''
This module defines enums for parsing and interpreting GEDCOM files.
'''

from enum import Enum, StrEnum


class ByteOrderMark(Enum):
    '''
    Represents the byte order marks that might be present in a GEDCOM file.
    These are used to indicate the endianness of the file.
    '''
    NONE = 0
    BIG_ENDIAN_32_BIT = 1
    LITTLE_ENDIAN_32_BIT = 2
    BIG_ENDIAN_16_BIT = 3
    LITTLE_ENDIAN_16_BIT = 4
    BIT_8 = 5


class NoticeType(Enum):
    '''
    Represents the types of notices that can be generated during parsing.
    These types are used to indicate the severity of the notice.
    '''
    ERROR = 0
    WARNING = 1


class JSONField(Enum):
    '''
    Represents the fields that can be included in the JSON output.
    These fields correspond to the attributes of the entities in the GEDCOM file.
    '''
    IND = 0
    FAM = 1


class Form(StrEnum):
    LINEAGE_LINKED = 'LINEAGE-LINKED'


class NameType(StrEnum):
    '''
    Represents the different types of names and individual might have.
    These types are defined in the GEDCOM 5.5.5 specification.
    '''
    MAIN = 'main'
    AKA = 'aka'
    BIRTH = 'birth'
    IMMIGRANT = 'immigrant'
    MAIDEN = 'maiden'
    MARRIED = 'married'


class NamePartType(StrEnum):
    SURNAME = 'Surname'
    PREFIX = 'Prefix'
    GIVEN = 'Given'
    NICKNAME = 'Nickname'
    SURNAME_PREFIX = 'SurnamePrefix'
    SUFFIX = 'Suffix'


class Sex(StrEnum):
    '''
    Represents the sex of an individual in a GEDCOM file.
    These values are defined in the GEDCOM 5.5.5 specification.
    '''
    MALE = 'M'
    FEMALE = 'F'
    UNKNOWN = 'U'


class Restriction(StrEnum):
    '''
    The privacy restriction that can be applied to a record.
    '''
    NONE = ''
    PRIVACY = 'privacy'
    CONFIDENTIAL = 'confidential'
    LOCKED = 'locked'


class Tag(StrEnum):
    '''
    Represents the tags used in GEDCOM files.
    These tags are defined in the GEDCOM 5.5.5
    specification except for SSN and FSID.
    '''
    GEDC = 'GEDC'
    HEAD = 'HEAD'
    TRLR = 'TRLR'
    VERS = 'VERS'
    DEST = 'DEST'
    SOUR = 'SOUR'
    CORP = 'CORP'
    DATA = 'DATA'
    DATE = 'DATE'
    COMM = 'COMM'
    COPR = 'COPR'
    TIME = 'TIME'
    LANG = 'LANG'
    SUBM = 'SUBM'
    SUBN = 'SUBN'
    FILE = 'FILE'
    NOTE = 'NOTE'
    FAM = 'FAM'
    HUSB = 'HUSB'
    WIFE = 'WIFE'
    MARR = 'MARR'
    CHIL = 'CHIL'
    NCHI = 'NCHI'
    REFN = 'REFN'
    TYPE = 'TYPE'
    FONE = 'FONE'
    RIN = 'RIN'
    INDI = 'INDI'
    SEX = 'SEX'
    OBJE = 'OBJE'
    TITL = 'TITL'
    REPO = 'REPO'
    PLAC = 'PLAC'
    AGNC = 'AGNC'
    AUTH = 'AUTH'
    ABBR = 'ABBR'
    TEXT = 'TEXT'
    ADDR = 'ADDR'
    ADR1 = 'ADR1'
    ADR2 = 'ADR2'
    ADR3 = 'ADR3'
    CITY = 'CITY'
    STAE = 'STAE'
    POST = 'POST'
    COUN = 'COUN'
    PHON = 'PHON'
    EMAIL = 'EMAIL'
    FAX = 'FAX'
    WWW = 'WWW'
    ASSOC = 'ASSOC'
    RELA = 'RELA'
    CHAN = 'CHAN'
    FAMC = 'FAMC'
    PEDI = 'PEDI'
    CAUS = 'CAUS'
    AGE = 'AGE'
    ANUL = 'ANUL'
    CENS = 'CENS'
    DIV = 'DIV'
    DIVF = 'DIVF'
    ENGA = 'ENGA'
    MARB = 'MARB'
    MARC = 'MARC'
    MARL = 'MARL'
    MARS = 'MARS'
    RESI = 'RESI'
    EVEN = 'EVEN'
    CAST = 'CAST'
    DESC = 'DESC'
    EDUC = 'EDUC'
    IDNO = 'IDNO'
    NATI = 'NATI'
    NAME = 'NAME'
    RELN = 'RELN'
    OCCU = 'OCCU'
    POSS = 'POSS'
    RELI = 'RELI'
    FACT = 'FACT'
    BIRT = 'BIRT'
    CHR = 'CHR'
    DEAT = 'DEAT'
    BURI = 'BURI'
    CREM = 'CREM'
    ADOP = 'ADOP'
    BAPM = 'BAPM'
    BARM = 'BARM'
    BASM = 'BASM'
    CHRA = 'CHRA'
    CONF = 'CONF'
    CONT = 'CONT'
    FCOM = 'FCOM'
    NATU = 'NATU'
    EMIG = 'EMIG'
    IMMI = 'IMMI'
    PROB = 'PROB'
    WILL = 'WILL'
    GRAD = 'GRAD'
    RETI = 'RETI'
    NPFX = 'NPFX'
    GIVN = 'GIVN'
    NICK = 'NICK'
    SPFX = 'SPFX'
    SURN = 'SURN'
    NSFX = 'NSFX'
    ROMN = 'ROMN'
    MAP = 'MAP'
    LATI = 'LATI'
    LONG = 'LONG'
    PAGE = 'PAGE'
    ROLE = 'ROLE'
    CERT = 'CERT'
    MEDI = 'MEDI'
    FAMS = 'FAMS'
    CHAR = 'CHAR'
    FORM = 'FORM'
    CTRY = 'CTRY'
    CONC = 'CONC'
    PUBL = 'PUBL'
    ALIA = 'ALIA'
    SSN = 'SSN'
    FSID = 'FSID'


class ObsoleteTag(StrEnum):
    '''
    Represents tags that are no longer in use in GEDCOM files.
    These tags may still appear in older GEDCOM files.
    They are not used in the current GEDCOM 5.5.5 specification.
    '''
    SSN = 'SSN'
    FSID = 'FSID'


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

sex_to_str = {
    'M': 'Male',
    'F': 'Female',
    'U': 'Unknown',
    'X': 'Intersex',
    'N': 'Not Record'
}

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

name_to_str = {
    'main': 'Main',
    'aka': 'Also Known As',
    'birth': 'Birth',
    'immigrant': 'Immigrant',
    'maiden': 'Maiden',
    'married': 'Married'
}
