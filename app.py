import streamlit as st
import pandas as pd

from models.mock_models import model_a, model_b
from evaluator.metrics import basic_evaluation
from evaluator.compare import compare_models
from utils.storage import save_results

st.set_page_config(page_title="LLM Evaluation System", layout="wide")

st.title("🧠 LLM Output Evaluation System V1")

# Input section
prompt = st.text_area("Enter Prompt")

if st.button("Run Evaluation"):
    results = []

    models = {
        "Model_A": model_a,
        "Model_B": model_b
    }

    for name, func in models.items():
        output = func(prompt)
        metrics = basic_evaluation(output, prompt)

        result = {
            "model": name,
            "prompt": prompt,
            "output": output,
            **metrics
        }

        results.append(result)

    # Save results
    save_results(results)

    df = pd.DataFrame(results)

    st.subheader("📄 Outputs")
    st.dataframe(df)

    st.subheader("📊 Comparison")
    comparison = compare_models(results)
    st.dataframe(comparison)