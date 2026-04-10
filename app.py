import streamlit as st
import pandas as pd

from evaluator.compare import compare_models
from evaluator.metrics import basic_evaluation
from models.local_models import generate_with_lm_studio, generate_with_ollama
from models.openai_model import generate_with_openai
from utils.auth import authenticate_user, register_user
from utils.storage import save_results


st.set_page_config(page_title="LLM Evaluation System", layout="wide")


MODEL_OPTIONS = {
    "Cloud": {
        "OpenAI": generate_with_openai,
    },
    "Local": {
        "Ollama": generate_with_ollama,
        "LM Studio": generate_with_lm_studio,
    },
}


def initialize_state():
    defaults = {
        "authenticated_user": None,
        "auth_mode": "Login",
        "selected_provider_type": None,
        "selected_provider_name": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout():
    st.session_state.authenticated_user = None
    st.session_state.selected_provider_type = None
    st.session_state.selected_provider_name = None


def reset_model_selection():
    st.session_state.selected_provider_type = None
    st.session_state.selected_provider_name = None


def render_home():
    st.title("LLM Output Evaluation System")
    st.caption(
        "Sign in, choose how you want to run the model, and evaluate outputs with the existing scoring pipeline."
    )

    left, right = st.columns([1.3, 1])

    with left:
        st.subheader("Flow")
        st.markdown(
            """
            1. Create an account or log in
            2. Choose a cloud or local model path
            3. Pick `OpenAI`, `Ollama`, or `LM Studio`
            4. Run the evaluator on your prompt
            """
        )

    with right:
        st.subheader("Get Started")
        next_mode = st.radio(
            "Authentication",
            ("Login", "Sign Up"),
            index=0 if st.session_state.auth_mode == "Login" else 1,
            horizontal=True,
        )
        st.session_state.auth_mode = next_mode

    st.divider()


def render_auth_form():
    st.subheader(st.session_state.auth_mode)

    with st.form("auth_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button(st.session_state.auth_mode)

    if not submitted:
        return

    if st.session_state.auth_mode == "Sign Up":
        success, message = register_user(username, password)
        if success:
            st.success(message)
            st.session_state.auth_mode = "Login"
        else:
            st.error(message)
        return

    success, message = authenticate_user(username, password)
    if success:
        st.session_state.authenticated_user = username.strip()
        st.success(message)
        st.rerun()
    else:
        st.error(message)


def render_provider_selection():
    st.title("Choose Your Model Source")
    st.caption(f"Signed in as `{st.session_state.authenticated_user}`")

    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.write("Select whether you want to run the evaluator with a cloud model or a local model.")
    with top_right:
        if st.button("Log Out"):
            logout()
            st.rerun()

    provider_type = st.radio(
        "Model type",
        options=["Cloud", "Local"],
        index=0 if st.session_state.selected_provider_type != "Local" else 1,
        horizontal=True,
    )

    provider_name = st.radio(
        "Provider",
        options=list(MODEL_OPTIONS[provider_type].keys()),
        horizontal=True,
    )

    if provider_type == "Cloud":
        st.info("Cloud access is currently restricted to OpenAI.")
    else:
        st.info("Local access currently supports Ollama or LM Studio.")

    if st.button("Continue to Evaluator", type="primary"):
        st.session_state.selected_provider_type = provider_type
        st.session_state.selected_provider_name = provider_name
        st.rerun()


def run_selected_model(prompt):
    provider_type = st.session_state.selected_provider_type
    provider_name = st.session_state.selected_provider_name
    generator = MODEL_OPTIONS[provider_type][provider_name]
    return generator(prompt)


def render_evaluator():
    provider_type = st.session_state.selected_provider_type
    provider_name = st.session_state.selected_provider_name

    st.title("Run Evaluation")
    st.caption(
        f"User: `{st.session_state.authenticated_user}` | Path: `{provider_type}` | Provider: `{provider_name}`"
    )

    action_left, action_right = st.columns([1, 1])
    with action_left:
        if st.button("Back to Model Selection"):
            reset_model_selection()
            st.rerun()
    with action_right:
        if st.button("Log Out"):
            logout()
            st.rerun()

    prompt = st.text_area("Enter Prompt")

    if not st.button("Run Evaluation", type="primary"):
        return

    if not prompt.strip():
        st.warning("Enter a prompt before running the evaluator.")
        return

    try:
        output = run_selected_model(prompt)
    except Exception as exc:
        st.error(f"Unable to generate output from {provider_name}: {exc}")
        return

    metrics = basic_evaluation(output, prompt)
    result = {
        "user": st.session_state.authenticated_user,
        "provider_type": provider_type,
        "provider": provider_name,
        "model": provider_name,
        "prompt": prompt,
        "output": output,
        **metrics,
    }

    results = [result]
    save_results(results)

    df = pd.DataFrame(results)

    st.subheader("Output")
    st.dataframe(df, use_container_width=True)

    st.subheader("Evaluation Summary")
    comparison = compare_models(results)
    st.dataframe(comparison, use_container_width=True)


def main():
    initialize_state()

    if not st.session_state.authenticated_user:
        render_home()
        render_auth_form()
        return

    if not st.session_state.selected_provider_name:
        render_provider_selection()
        return

    render_evaluator()


if __name__ == "__main__":
    main()
