from src.file import File
import src.enums as enums

gedcom_file = File('/home/ethan/Desktop/GEDCOM-to-JSON/GedcomToJson/files/royal92.ged')
gedcom_file.jsonify(True, enums.JSONField.IND, enums.JSONField.FAM)