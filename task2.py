import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import re

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

#giving option to select model
gemini_version = input("Enter Gemini version (1.5, 2.0): ").strip()
if gemini_version == "2.0":
    model_name = "gemini-2.0-flash"
elif gemini_version == "1.5":
    model_name = "gemini-1.5-flash"
else:
    raise ValueError("Invalid version. Please choose 1.5 or 2.0.")

llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)

CATEGORY_PROMPT = """
What is an Attack?
An attack is any materialized incident that disrupts, degrades, or compromises the stability, security, or functionality of a target. This includes human actions (e.g., deliberate acts, errors) and non-human factors (e.g., disasters, failures). Only actualized risks are considered.

Category Definitions:
- AAT: Emerging & Advanced Technology Attacks
- BPA: Biological & Pandemic Attacks
- DCA: Digital & Cyber Attacks
- EFA: Economic & Financial Attacks
- NDA: Natural Disaster Attacks
- OIA: Operational & Industrial Attacks
- PSI: Physical Security & Infrastructure Attacks
- SPI: Socio-Political & Influence Attacks

You are a classification assistant. Based on the given incident, return all applicable category codes in a JSON list format (e.g., ["DCA", "OIA"]). Respond ONLY with the list.
"""


incident = input("\nEnter the incident description:\n")


prompt = f"{CATEGORY_PROMPT}\n\nIncident:\n{incident}"


response = llm.invoke([HumanMessage(content=prompt)])

#getting the json file
try:
    predicted = json.loads(response.content.strip())
except json.JSONDecodeError:
    match = re.search(r'\[(.*?)\]', response.content)
    if match:
        items = match.group(1).replace('"', '').split(',')
        predicted = [item.strip() for item in items]
    else:
        predicted = ["UNMAPPED"]


print("\n=== Classification Result ===")
print(f"Predicted Categories: {predicted}")
