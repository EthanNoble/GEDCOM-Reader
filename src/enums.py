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
    METADATA = 2


class Form(StrEnum):
    LINEAGE_LINKED = 'LINEAGE-LINKED'


class Language(StrEnum):
    '''
    Supported languages.
    '''
    AFRIKAANS = 'Afrikaans'
    ALBANIAN = 'Albanian'
    ANGLO_SAXON = 'Anglo-Saxon'
    CATALAN = 'Catalan'
    CATALAN_SPN = 'Catalan_Spn'
    CZECH = 'Czech'
    DANISH = 'Danish'
    DUTCH = 'Dutch'
    ENGLISH = 'English'
    ESPERANTO = 'Esperanto'
    ESTONIAN = 'Estonian'
    FAROESE = 'Faroese'
    FINNISH = 'Finnish'
    FRENCH = 'French'
    GERMAN = 'German'
    HAWAIIAN = 'Hawaiian'
    HUNGARIAN = 'Hungarian'
    ICELANDIC = 'Icelandic'
    INDONESIAN = 'Indonesian'
    ITALIAN = 'Italian'
    LATVIAN = 'Latvian'
    LITHUANIAN = 'Lithuanian'
    NAVAHO = 'Navaho'
    NORWEGIAN = 'Norwegian'
    POLISH = 'Polish'
    PORTUGUESE = 'Portuguese'
    ROMANIAN = 'Romanian'
    SERBO_CROA = 'Serbo_Croa'
    SLOVAK = 'Slovak'
    SLOVENE = 'Slovene'
    SPANISH = 'Spanish'
    SWEDISH = 'Swedish'
    TURKISH = 'Turkish'
    WENDIC = 'Wendic'
    AMHARIC = 'Amharic'
    ARABIC = 'Arabic'
    ARMENIAN = 'Armenian'
    ASSAMESE = 'Assamese'
    BELORUSIAN = 'Belorusian'
    BENGALI = 'Bengali'
    BRAJ = 'Braj'
    BULGARIAN = 'Bulgarian'
    BURMESE = 'Burmese'
    CANTONESE = 'Cantonese'
    CHURCH_SLAVIC = 'Church-Slavic'
    DOGRI = 'Dogri'
    GEORGIAN = 'Georgian'
    GREEK = 'Greek'
    GUJARATI = 'Gujarati'
    HEBREW = 'Hebrew'
    HINDI = 'Hindi'
    JAPANESE = 'Japanese'
    KANNADA = 'Kannada'
    KHMER = 'Khmer'
    KONKANI = 'Konkani'
    KOREAN = 'Korean'
    LAHNDA = 'Lahnda'
    LAO = 'Lao'
    MACEDONIAN = 'Macedonian'
    MAITHILI = 'Maithili'
    MALAYALAM = 'Malayalam'
    MANDRIN = 'Mandrin'
    MANIPURI = 'Manipuri'
    MARATHI = 'Marathi'
    MEWARI = 'Mewari'
    NEPALI = 'Nepali'
    ORIYA = 'Oriya'
    PAHARI = 'Pahari'
    PALI = 'Pali'
    PANJABI = 'Panjabi'
    PERSIAN = 'Persian'
    PRAKRIT = 'Prakrit'
    PUSTO = 'Pusto'
    RAJASTHANI = 'Rajasthani'
    RUSSIAN = 'Russian'
    SANSKRIT = 'Sanskrit'
    SERB = 'Serb'
    TAGALOG = 'Tagalog'
    TAMIL = 'Tamil'
    TELUGU = 'Telugu'
    THAI = 'Thai'
    TIBETAN = 'Tibetan'
    UKRAINIAN = 'Ukrainian'
    URDU = 'Urdu'
    VIETNAMESE = 'Vietnamese'
    YIDDISH = 'Yiddish'


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


class PhoneticType(StrEnum):
    '''
    The type of phonetic variation for a name.
    '''
    NONE = ''
    HANGUL = 'hangul'
    KANA = 'kana'


class RomanizedType(StrEnum):
    '''
    The type of romanized variation for a name.
    '''
    NONE = ''
    PINYIN = 'pinyin'
    ROMAIJI = 'romaji'
    WADEGILES = 'wadegiles'


class DateType(StrEnum):
    REGULAR = 'regular'
    PERIOD = 'period'
    RANGE = 'range'
    APPROXIMATED = 'approximated'
    PHRASE = 'phrase'


class DateRange(StrEnum):
    NONE = ''
    BEF = 'BEF'
    AFT = 'AFT'
    BET = 'BET'


class DatePeriod(StrEnum):
    FROM = 'FROM'
    TO = 'TO'


class DateApproximated(StrEnum):
    NONE = ''
    ABT = 'ABT'
    CAL = 'CAL'
    EST = 'EST'


class CalendarType(StrEnum):
    GREGORIAN = '@#DGREGORIAN@'
    JULIAN = '@#DJULIAN@'
    HEBREW = '@#DHEBREW@'
    FRENCH = '@#DFRENCH R@'
    ROMAN = '@#DROMAN@'
    UNKNOWN = '@#DUNKNOWN@'


class Month(StrEnum):
    JAN = 'JAN'
    FEB = 'FEB'
    MAR = 'MAR'
    APR = 'APR'
    MAY = 'MAY'
    JUN = 'JUN'
    JUL = 'JUL'
    AUG = 'AUG'
    SEP = 'SEP'
    OCT = 'OCT'
    NOV = 'NOV'
    DEC = 'DEC'


class MonthHebrew(StrEnum):
    TSH = 'TSH'
    CSH = 'CSH'
    KSL = 'KSL'
    TVT = 'TVT'
    SHV = 'SHV'
    ADR = 'ADR'
    ADS = 'ADS'
    NSN = 'NSN'
    IYR = 'IYR'
    SVN = 'SVN'
    TMZ = 'TMZ'
    AAV = 'AAV'
    ELL = 'ELL'


class MonthFrench(StrEnum):
    VEND = 'VEND'
    BRUM = 'BRUM'
    FRIM = 'FRIM'
    NIVO = 'NIVO'
    PLUV = 'PLUV'
    VENT = 'VENT'
    GERM = 'GERM'
    FLOR = 'FLOR'
    PRAI = 'PRAI'
    MESS = 'MESS'
    THER = 'THER'
    FRUC = 'FRUC'
    COMP = 'COMP'


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


class PedigreeLinkageType(StrEnum):
    '''
    The type of pedigree linkage for a child in a family.
    '''
    NONE = ''
    ADOPTED = 'adopted'
    BIRTH = 'birth'
    FOSTER = 'foster'
    SEALING = 'sealing'


class ChildLinkageStatus(StrEnum):
    '''
    The status of a child in a family.
    '''
    NONE = ''
    CHALLENGED = 'challenged'
    DISPROVEN = 'disproven'
    PROVEN = 'proven'


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
    RESN = 'RESN'
    BLES = 'BLES'
    ORDN = 'ORDN'
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


event_type_individual = {
    Tag.EVEN: '',
    Tag.BIRT: 'Birth',
    Tag.CHR: 'Adult Christening',
    Tag.DEAT: 'Death',
    Tag.BURI: 'Burial',
    Tag.CREM: 'Cremation',
    Tag.ADOP: 'Adoption',
    Tag.NATU: 'Naturalization',
    Tag.EMIG: 'Emigration',
    Tag.IMMI: 'Immigration',
    Tag.BAPM: 'Baptism',
    Tag.BARM: 'Bar Mitzvah',
    Tag.BASM: 'Bas Mitzvah',
    Tag.BLES: 'Bles',
    Tag.CHRA: 'Christening',
    Tag.CONF: 'Confirmation',
    Tag.FCOM: 'First Communion',
    Tag.ORDN: 'Ord',
    Tag.CENS: 'Census',
    Tag.PROB: 'Probate',
    Tag.WILL: 'Will',
    Tag.GRAD: 'Graduation',
    Tag.RETI: 'Retirement'
}

event_type_family = {}

name_to_str = {
    'main': 'Main',
    'aka': 'Also Known As',
    'birth': 'Birth',
    'immigrant': 'Immigrant',
    'maiden': 'Maiden',
    'married': 'Married'
}
