import textwrap
import PIL.Image
import google.generativeai as genai
import sys
import pymongo
import json
from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
GOOGLE_API_KEY= 'AIzaSyBct0uTAWWkFETP-tSRrz9DyxEZDhWdP60'

image_id = 1

genai.configure(api_key=GOOGLE_API_KEY)

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

#For image input
image_path = sys.argv[1]
img = PIL.Image.open(image_path)
model = genai.GenerativeModel('gemini-1.5-flash')

#response = model.generate_content(img)

#to_markdown(response.text)

#For image and text
response = model.generate_content(["Describe the image", img], stream=True)
response.resolve()
print(type(to_markdown(response.text).data))


# Connect to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Access the database and collection
db = client["foodlabel"]
collection = db["predictions"]

# Example output from Gemini
gemini_output = {
    "image_id": "12345",
    "description": {
        "title": "Sunset",
        "tags": ["sunset", "sky", "nature"],
        "location": "Beach",
        "date_taken": "2024-07-10"
    }
}

# Convert the description to a JSON string if needed
#description_json = json.dumps(gemini_output["description"])

# Prepare the document to insert
document = {
    "image_id": image_id,
    "description": to_markdown(response.text).data
}

# Insert the document into the collection
result = collection.insert_one(document)

# Print the result of the insertion
print(f"Document inserted with _id: {result.inserted_id}")