
## Task 1: LLM-Assisted Dataset Creation

### Objective
Build a high-quality labeled dataset of real-world cyber-physical incidents using LLM-assisted data collection and human-in-the-loop validation.

### Workflow

#### 1. Query Design
- Created 50 queries covering diverse attack vectors and sectors.
- Examples:
  - `"Ransomware attack on utility systems"`
  - `"Quantum computer breach on encrypted data"`

#### 2. Automated Data Collection
- Developed `tools.py` using:
  - `LangChain`
  - `TavilySearchResults`
  - `Gemini 2.0 Flash` and `Gemini 1.5 Flash`
- For each query:
  - Perform web search.
  - Parse title, summary, and URL.
  - Use Gemini to:
    - Generate incident summary.
    - Suggest relevant category codes.
- Output dataset for different models saved in:
  - `labeled_dataset_gemini1.5.json`
  - `labeled_dataset_gemini2.0.json`

#### 3. Human Review & Labeling
- Reviewed every article.
- Reordered, added, or removed category codes based on deeper reading.
- Justification notes added for every decision.

#### Category Code Definitions
| Code | Meaning |
|------|---------|
| DCA  | Digital Compromise or Access |
| OIA  | Operational Infrastructure Attack |
| BPA  | Biological/Physical/Health Impact |
| NDA  | Natural Disaster |
| EFA  | Economic/Financial Attack |
| SPI  | Socio-Political Influence |
| PSI  | Physical Security & Infrastructure |
| AAT  | Advanced & Emerging Technology Attack |

**Folder Structure**

├ task1.py                        # Main script to generate the labeled dataset

├ tools_new.py                   # Contains search and LLM summarization logic

├ llm.py                         # LLM initialization using Google Gemini

├ requirements.txt               # List of all required Python packages

├.env                           # API keys (GOOGLE_API_KEY, TAVILY_API_KEY)

├ labeled_dataset2.0.json        # Output JSON file with summaries and categories

├ labeled_dataset1.5.json        # Output JSON file with summaries and categories

Use: python task1.py

### **note**: For all tasks requirements1.txt will be sufficient. Install all dependencies before running any task. 


#### Final Output Format
```json
{
  "article_title": "Ransomware hits city water plant",
  "article_url": "https://example.com/ransomware-attack",
  "incident_summary": "...",
  "category_flow(human labeled)": ["DCA", "OIA", "BPA"],
  "llm_suggestion": ["DCA", "OIA"],
  "Note": "LLM missed BPA due to halted water treatment and contamination risks."
}
```


## Task 2: Category Flow Mapping Agent Using Gemini API

Task 2 involved building a Python-based AI agent that classifies incident descriptions into predefined attack categories. The agent utilizes Google’s Gemini models (version 1.5 and 2.0) for inference and includes a robust evaluation framework comparing model outputs against manually labeled ground truth using selected metrics.

### Functionality

•	Input: A textual incident description.

•	Prompt: Contains formal definitions of “Attack” and all 8 category codes

•	Output: All applicable category codes strictly in JSON list format.

•	Model Selection: Users can choose between gemini-1.5-flash and gemini-2.0-flash per run.

**Evaluation Metrics**

To evaluate how closely the predicted category flow matches the ground truth, the following metrics were used:

a. F1 Score (Micro & Macro)

b. Jaccard Similarity Score (Micro & Macro)


![image](https://github.com/user-attachments/assets/464eea42-9b27-48e4-97f2-864290095b86)




### Folder Structure:

 |---task2.py                           # Main script
   
 |---.env                               # Contains API key
 
 |---Model_evaluation.ipynb             #do model analysis
 
 |--- final_dataset_g2.0.json           #the self validated final dataset of dataset created in task1 of 2.0 output
 
 |--- final_dataset_g1.5.json           #the self validated final dataset of dataset created in task1 of 1.5 output
 
 |---attack_incident_updated.csv        # created during model evaluation

Use: python task2.py


## Bonus Task: Streamlit App

### Design & Structure Rationale 

**1.	Modular Page Design (Sidebar Navigation):**
Cleanly separates core functionalities—classification, evaluation, exploration, and annotation—into independent modules for focused workflows and easier debugging.
**2.	Efficient Data Handling:**
Uses @st.cache_data to efficiently load and preprocess CSV data once, while early binarization of multi-label categories enables fast metric computation and evaluation.
**3.	LLM Integration (Classify Incident):**
Provides structured prompts with strict response formats and fallback parsing to ensure consistent and reliable outputs from Gemini LLMs across versions.
**4.	Visual & Metric-Driven Evaluation (Model Evaluation, LLM Comparison):**
Leverages micro/macro F1, Jaccard index, and classification reports alongside Altair/Seaborn visualizations to offer both granular and aggregated performance insights.
**5.	Exploratory Features (Data Explorer, Annotation Tool):**
Enables intuitive filtering, mismatch analysis, and human-in-the-loop annotation for continuous dataset refinement and transparent model inspection.
**6.	Error Analysis:**
Delivers per-label error breakdowns and surfacing of misclassified samples via graphs and tables to identify and address model weaknesses or data issues.

### Folder Strucuture:

  ├--bonus_task.py                          #streamlit file

  ├-- .env                                  # your Google API key

  ├--attack_incident_updated.csv            # the dataset used in the app generated by model_evaluation.py

  ├--Annotation_tool_output.csv             # created after annotations

Use: streamlit run bonus_task.py

### Output:

Page1:

![image](https://github.com/user-attachments/assets/f31b8294-2062-4078-94ee-3126484663d7)

![image](https://github.com/user-attachments/assets/51910b7e-ed35-48c9-8b0d-c9eca27f5369)

Page2:


![image](https://github.com/user-attachments/assets/d172c839-8016-4eab-bbc1-737d35353660)

![image](https://github.com/user-attachments/assets/a907f5f6-8c0c-4b17-b4da-a78257a95978)

![image](https://github.com/user-attachments/assets/8b1a665b-9250-4a48-9bb3-e717012176c2)


Page3:


![image](https://github.com/user-attachments/assets/594d548d-37e4-4aa7-b09a-711733a006ad)

![image](https://github.com/user-attachments/assets/fa099683-c5f0-4bed-8f02-2da40ce9373a)


Page4:


![image](https://github.com/user-attachments/assets/8d4a4542-7ca8-4ce5-a784-a1258ed50690)

Page5:


![image](https://github.com/user-attachments/assets/bbea1b67-c677-4e17-911c-53a29eaa80f2)

Page6:


![image](https://github.com/user-attachments/assets/56f02c5d-a7a6-4751-819c-adc406ae9649)


![image](https://github.com/user-attachments/assets/ff71ae78-9ff6-4ea0-a2a1-2e1490eddd34)





