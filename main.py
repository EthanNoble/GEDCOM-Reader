from src.file import File
import src.enums as enums

gedcom_file = File('')
json_str = gedcom_file.jsonify(enums.JSONField.IND, enums.JSONField.FAM)
with open('', 'w') as fp:
    fp.write(json_str)