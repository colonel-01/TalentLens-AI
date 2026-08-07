import os
from groq import Groq
from dotenv import load_dotenv
import pymupdf


load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("groq api key key not initialisedd properly")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"



#extracting from the resume pdf , if the pdf is image this will fail , for that we need ocr fall back else it works best 
def extract_text(pdf_path):
    doc = pymupdf.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text

resume_text = extract_text("data/res.pdf")

# print(resume_text)

#designing the ticket
from pydantic import BaseModel
from typing import List

class Resume(BaseModel):
    name:str
    education:List[str]
    skills:List[str]
    projects:List[str]
    achievements:List[str]

schema=Resume.model_json_schema()
response_format={
    "type" : "json_object"
}

system_prompt=f"""
    you are an expert resume parser.
    extract information from the resume.
    Return only valid json  .
    schema : {schema}
"""
    
messages=[{
    "role":"system",
    "content":system_prompt
},{
    "role":"user",
    "content":resume_text
}]

response=client.chat.completions.create(model=model,messages=messages,temperature=1,response_format=response_format)
raw_json=response.choices[0].message.content    

import json
data_file=json.loads(raw_json)

resume=Resume(**data_file)
print(resume)