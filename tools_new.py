from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import json
import re
import os

from llm import llm

load_dotenv()

search = TavilySearchResults(k=5)

def search_tool_func(query: str) -> dict:
    
    results = search.invoke({"query": query})
    
    if not results:
        return {
            "article_title": "No articles found.",
            "article_url": "No URL",
            "incident_summary": "No articles found.",
            "llm_suggestion": ["NDA"],
        }
    
    top_article = results[0]
    title = top_article.get("title", "No Title")
    url = top_article.get("url", "No URL")
    body = top_article.get("content", "")[:3000]  

    summarization_prompt = f"""
Given the following article content:
\"\"\"{body}\"\"\"

Please provide a neutral and clear paraphrased summary in 2–6 sentences that includes:
- Method of attack (how the attack was carried out)
- Target (who or what was affected)
- Consequence (what was the outcome of the attack)
- Broader impact (if any) (e.g., potential future risks or lessons learned)

The summary should be neutral and not directly copy content from the article, but instead be an accurate paraphrase.
"""
    summary_response = llm.invoke(summarization_prompt)
    summary = summary_response.content.strip()

    
    category_prompt = f"""
Here are official category definitions:
- DCA: Digital compromise or access
- OIA: Operational infrastructure attack
- BPA: Biological/physical/health impact
- NDA: Natural disaster
- EFA: Economic/financial attack
- SPI: Socio-political influence
- PSI: Physical Security & Infrastructure Attacks
- AAT: Emerging and Advanced Technology Attacks

Given this incident summary:
\"\"\"{summary}\"\"\"

Output ONLY a valid JSON list of category codes (e.g. ["DCA", "OIA"]) that best describes the sequence of impacts.
Do NOT explain or include any other text. Respond only with valid JSON.
"""
    llm_raw_category = llm.invoke(category_prompt).content.strip()

    # Parsing JSON 
    try:
        llm_suggestion = json.loads(llm_raw_category)
        if not isinstance(llm_suggestion, list) or not all(isinstance(c, str) for c in llm_suggestion):
            raise ValueError("Invalid JSON structure")
    except Exception:
        llm_suggestion = re.findall(r'\b(DCA|OIA|BPA|NDA|EFA|SPI)\b', llm_raw_category)
        if not llm_suggestion:
            llm_suggestion = ["could not parse suggestion"]

    
    category_flow = list(dict.fromkeys(llm_suggestion))



    return {
        "article_title": title,
        "article_url": url,
        "incident_summary": summary,
        "llm_suggestion": category_flow,  
    }

search_summarize_tool = Tool(
    name="SearchAndSummarizeIncident",
    func=search_tool_func,
    description="Given a cyber incident query, searches online, summarizes the top article, and suggests impact categories."
)
