from tika import parser
import pyrebase
import json

def extract_pages_from_pdf(pdf_path, pages):
    rawText = parser.from_file(pdf_path, xmlContent=True)
    rawList = rawText['content'].splitlines()

    extracted_text = []
    add = False
    current_page = 0

    for line in rawList:
        if add and "</div>" not in line:
            extracted_text.append(line.replace("<p>", "").replace("</p>", "").replace("<p />", ""))
        if '<div class="page"><p />' in line:
            current_page += 1
            if current_page in pages:
                add = True
                extracted_text.append("Page " + str(current_page) + ":")
            else:
                add = False
        if "</div>" in line:
            add = False

    return extracted_text

def ingredients(text):
    add = False
    ingredients = []
    str = ""
    upload = []
    name = ""
    
    for line in text:
        line = line.lower()
        if "name:" in line:
            name = line.replace("recipe name: ", "").replace("amp;", "").upper()
        if "Ingredients" in line.title():
            add = True
        if "Contains:" in line.title():
            ingredients.append(str)
            str = ""
        if "ALLERGEN WARNING:" in line.upper():
            add = False
            ingredients.append(str)
            upload = ingredients[-2:]
            upload_to_firebase(name, upload)
            str = ""
            upload = []
        if add and "Page" not in line:
            str += line.replace("ingredients: ", "").replace("contains: ", "")
            
    return ingredients


def upload_to_firebase(name, data):
    global db
    db.child("menu").child(name).set(data)

pdf_path = 'Menus/Menu_1.pdf'
config_file = "config.json"
with open(config_file) as configfile:
    config = json.load(configfile)
firebase = pyrebase.initialize_app(config)
db = firebase.database()
pages_to_extract = list(map(int, input("Pages you want to extract: ").split(',')))
series = input("Do you want to select pages in range or individual? (r/i): ")
if series == 'r':
    start, end = pages_to_extract[0], pages_to_extract[1]
    pages_to_extract = list(range(start, end+1))
extracted_text = extract_pages_from_pdf(pdf_path, pages_to_extract)
data = ingredients(extracted_text)