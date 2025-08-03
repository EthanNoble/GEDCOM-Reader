'''
This file is part of the GEDCOM-Reader project.
'''

from src.file import File
from src import enums

gedcom_file = File('/home/ethan/Desktop/files/NobleFamilyTree.ged')
print(gedcom_file._header.jsonify())
# json_str = gedcom_file.jsonify(enums.JSONField.IND, enums.JSONField.FAM)
# with open('NobleFamilyTree.json', 'w', encoding='utf-8') as fp:
#     fp.write(json_str)
