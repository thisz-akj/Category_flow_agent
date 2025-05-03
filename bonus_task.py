import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, jaccard_score, classification_report
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

LABELS = ["AAT", "BPA", "DCA", "EFA", "NDA", "OIA", "PSI", "SPI"]

def binarize(labels):
    return [int(label in labels) for label in LABELS]

@st.cache_data
def load_data():
    df = pd.read_csv("attack_incident_updated.csv")
    df["category_flow"] = df["category_flow"].apply(eval)
    df["llm_suggestion_1.5"] = df["llm_suggestion_1.5"].apply(eval)
    df["llm_suggestion_2.0"] = df["llm_suggestion_2.0"].apply(eval)
    df["y_true"] = df["category_flow"].apply(binarize)
    df["y_pred_1.5"] = df["llm_suggestion_1.5"].apply(binarize)
    df["y_pred_2.0"] = df["llm_suggestion_2.0"].apply(binarize)
    return df

data = load_data()

# Sidebar Navigation
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", [
    "Classify Incident", 
    "Model Evaluation", 
    "Data Explorer", 
    "LLM Comparison", 
    "Annotation Tool",
    "Error Analysis"
])

# Page 1: Classify Incident
if page == "Classify Incident":
    st.title("Classify a New Incident")

    model_version = st.selectbox("Select Gemini Model Version", ["1.5", "2.0"])
    model_name = "gemini-1.5-pro" if model_version == "1.5" else "gemini-2.0-flash"

    incident_text = st.text_area("Enter Incident Description")

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

    if st.button("Classify Incident") and incident_text:
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)
        prompt = f"{CATEGORY_PROMPT}\n\nIncident:\n{incident_text}"
        response = llm.invoke([HumanMessage(content=prompt)])
        try:
            categories = json.loads(response.content.strip())
        except json.JSONDecodeError:
            import re
            match = re.search(r'\[(.*?)\]', response.content)
            if match:
                items = match.group(1).replace('"', '').split(',')
                categories = [item.strip() for item in items]
            else:
                categories = ["UNMAPPED"]

        st.success("Predicted Categories:")
        st.write(categories)

# Page 2: Model Evaluation
elif page == "Model Evaluation":
    st.title("Model Evaluation Dashboard")

    model_choice = st.radio("Select Model Version to Evaluate", ["1.5", "2.0"])
    y_true = np.array(data["y_true"].tolist())
    y_pred = np.array(data[f"y_pred_{model_choice}"].tolist())

    st.metric("Micro F1", f"{f1_score(y_true, y_pred, average='micro'):.3f}")
    st.metric("Macro F1", f"{f1_score(y_true, y_pred, average='macro'):.3f}")
    st.metric("Jaccard (Micro)", f"{jaccard_score(y_true, y_pred, average='micro'):.3f}")

    st.subheader("Per-Label F1 Scores")
    f1s = f1_score(y_true, y_pred, average=None)
    df_f1 = pd.DataFrame({"Label": LABELS, "F1 Score": f1s})
    chart = alt.Chart(df_f1).mark_bar().encode(x="Label", y="F1 Score")
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Classification Report")
    report = classification_report(y_true, y_pred, target_names=LABELS, output_dict=True)
    st.dataframe(pd.DataFrame(report).transpose())

# Page 3: Data Explorer
elif page == "Data Explorer":
    st.title("Data Explorer")

    search = st.text_input("Search by Title, Summary, or Keyword")
    filtered = data[data[["incident_name", "incident_summary"]].apply(lambda x: x.astype(str).str.contains(search, case=False).any(), axis=1)] if search else data

    st.subheader("Filter Options")
    selected_label = st.multiselect("Filter by True Category Label", LABELS)
    if selected_label:
        filtered = filtered[filtered["category_flow"].apply(lambda x: any(lbl in x for lbl in selected_label))]

    st.subheader("LLM Prediction Match Filter")
    match_option = st.radio("Filter by Prediction Match", ["All", "Only Matches", "Only Mismatches"])
    if match_option == "Only Matches":
        filtered = filtered[filtered["llm_suggestion_1.5"] == filtered["llm_suggestion_2.0"]]
    elif match_option == "Only Mismatches":
        filtered = filtered[filtered["llm_suggestion_1.5"] != filtered["llm_suggestion_2.0"]]

    st.subheader("Incidents Table")
    st.dataframe(filtered[["incident_id", "incident_name", "incident_summary", "category_flow", "llm_suggestion_1.5", "llm_suggestion_2.0"]], use_container_width=True)

    st.subheader("Label Distribution")
    label_counts = pd.Series([lbl for sublist in filtered["category_flow"] for lbl in sublist]).value_counts()
    st.bar_chart(label_counts)

   

# Page 4: LLM Comparison
elif page == "LLM Comparison":
    st.title("Gemini 1.5 vs 2.0 Comparison")

    mismatches = data[data["llm_suggestion_1.5"] != data["llm_suggestion_2.0"]]
    st.write(f"Total Mutual Mismatches: {len(mismatches)}")

    mismatches_1_5 = data[data["category_flow"] != data["llm_suggestion_1.5"]]
    mismatches_2_0 = data[data["category_flow"] != data["llm_suggestion_2.0"]]

    st.metric("Mismatch Count (Gemini 1.5)", len(mismatches_1_5))
    st.metric("Mismatch Count (Gemini 2.0)", len(mismatches_2_0))

    st.subheader("Detailed Comparison Table")
    data["is_1.5_correct"] = data["category_flow"] == data["llm_suggestion_1.5"]
    data["is_2.0_correct"] = data["category_flow"] == data["llm_suggestion_2.0"]
    comparison_summary = data[["incident_id", "incident_name", "category_flow", "llm_suggestion_1.5", "llm_suggestion_2.0", "is_1.5_correct", "is_2.0_correct"]]
    st.dataframe(comparison_summary, use_container_width=True)

# Page 5: Annotation Tool
elif page == "Annotation Tool":
    st.title("Annotation Tool")
    idx = st.number_input("Select Incident Index to Edit", 0, len(data)-1, 0)
    st.write(f"**Title**: {data.loc[idx, 'incident_name']}")
    st.write(f"**Summary**: {data.loc[idx, 'incident_summary']}")
    st.write(f"**True Label**: {data.loc[idx, 'category_flow']}")
    new_pred = st.text_input("New prediction for Gemini 2.0 (comma separated)")
    if st.button("Update"):
        try:
            parsed = [x.strip() for x in new_pred.split(',') if x.strip() in LABELS]
            data.at[idx, 'llm_suggestion_2.0'] = parsed
            data.to_csv("Annotation_tool_output.csv", index=False)
            st.success("Updated Successfully")
        except:
            st.error("Invalid Format")

# Page 6: Error Analysis
elif page == "Error Analysis":
    st.title("Error Analysis")

    model_choice = st.selectbox("Choose Model Version", ["1.5", "2.0"])
    y_true = np.array(data["y_true"].tolist())
    y_pred = np.array(data[f"y_pred_{model_choice}"].tolist())

    st.subheader("Heatmap of Label Errors")
    error_matrix = (np.array(y_true) - np.array(y_pred))
    error_counts = np.sum(error_matrix != 0, axis=0)

    fig, ax = plt.subplots()
    sns.barplot(x=LABELS, y=error_counts, ax=ax)
    ax.set_title("Label-wise Error Count")
    ax.set_ylabel("Count")
    ax.set_xlabel("Labels")
    st.pyplot(fig)

    st.subheader("Sample Misclassifications")
    mismatches = data[(data["y_true"] != data[f"y_pred_{model_choice}"])]
    st.dataframe(mismatches[["incident_id", "incident_name", "category_flow", f"llm_suggestion_{model_choice}"]], use_container_width=True)
