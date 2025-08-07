'''
This file is part of the GEDCOM-Reader project.
'''

from src.file import File
from src.enums import JSONField

gedcom_file = File('/home/ethan/Desktop/gedcoms/royalty/Ptolemaic+Dynasty.ged')
json_str = gedcom_file.jsonify(JSONField.IND)
with open('test.json', 'w', encoding='utf-8') as fp:
    fp.write(json_str)
