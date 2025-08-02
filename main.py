from src.file import File
import src.enums as enums

gedcom_file = File('ABSOLUTE_PATH_TO_GEDCOM_FILE')
gedcom_file.jsonify(True, enums.JSONField.IND, enums.JSONField.FAM)