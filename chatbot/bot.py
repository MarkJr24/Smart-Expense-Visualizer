import os
import streamlit as st
from chatbot.query_handler import handle_query
from chatbot.query_handler import test_ai_connectivity
from chatbot.voice_input import capture_voice_input
from chatbot.charts import draw_category_chart
from utils.helpers import load_data


def chatbot_tab() -> None:
    """Render the chatbot UI inside a tab/section of the main app."""
    st.subheader("💬 Smart Expense Chatbot")

    # Indicate whether AI is enabled
    ai_key = os.getenv("OPENAI_API_KEY")
    try:
        if not ai_key:
            ai_key = st.secrets.get("OPENAI_API_KEY")  # type: ignore[attr-defined]
    except Exception:
        pass
    if ai_key:
        ai_status = test_ai_connectivity()
        st.caption(ai_status)
    else:
        st.caption("AI responses: disabled (using rule-based answers)")

    mode = st.radio(
        "Choose Input Mode:",
        ["Text", "Voice"],
        horizontal=True,
        key="chatbot_mode",
    )

    # --- Voice or Text Input + Header actions
    header_l, header_r = st.columns([5, 1])
    with header_l:
        user_input = None
        if mode == "Text":
            user_input = st.text_input("Ask about your expenses:", key="chatbot_text")
        else:
            if st.button("🎙️ Speak Now", key="chatbot_speak"):
                with st.spinner("Listening... please speak now"):
                    user_input = capture_voice_input()
                st.markdown(f"**You said:** {user_input}")
    with header_r:
        st.write("")
        if st.button("Clear chat", key="chatbot_clear"):
            for k in [
                "chatbot_last_input",
                "chatbot_last_response",
                "chatbot_text",
            ]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    # --- Quick suggestions / keywords (deduplicated across panels)
    st.markdown("**Try these prompts:**")
    suggestions = [
        "total spent",
        "food expenses",
        "top category",
        "travel spend",
        "show last 5 expenses",
        "compare food vs travel",
    ]
    shown_prompts = set()
    cols = st.columns(3)
    j = 0
    for prompt in suggestions:
        plow = prompt.strip().lower()
        if plow in shown_prompts or not plow:
            continue
        if cols[j % 3].button(prompt, key=f"chat_suggest_{j}"):
            user_input = prompt
        shown_prompts.add(plow)
        j += 1

    # Dynamic suggestions based on your data (top categories)
    try:
        df = load_data()
        if df is not None and not df.empty and "Category" in df.columns:
            top_categories = (
                df["Category"].astype(str).str.title().value_counts().index.tolist()[:6]
            )
            if top_categories:
                st.markdown("**Based on your data:**")
                dcols = st.columns(3)
                k = 0
                for cat in top_categories:
                    prompt = f"{str(cat).strip().lower()} expenses"
                    plow = prompt
                    if plow in shown_prompts or not plow:
                        continue
                    if dcols[k % 3].button(prompt, key=f"chat_dyn_{k}"):
                        user_input = prompt
                    shown_prompts.add(plow)
                    k += 1
    except Exception:
        pass

    # More suggestions expander
    with st.expander("More suggestions"):
        more_prompts = [
            "largest expense",
            "smallest expense",
            "average daily spend",
            "monthly total for August 2025",
            "spend in July 2025",
            "expenses between 2025-07-01 and 2025-07-15",
            "summarize last 10 expenses",
        ]
        # Add all categories as prompts too (data-driven)
        try:
            if df is not None and not df.empty and "Category" in df.columns:
                all_cats = (
                    df["Category"].astype(str).str.title().dropna().unique().tolist()
                )
                more_prompts.extend([f"{str(c).strip().lower()} expenses" for c in all_cats])
        except Exception:
            pass

        ecols = st.columns(3)
        local_seen = set()
        m = 0
        for prompt in more_prompts:
            plow = str(prompt).strip().lower()
            if not plow or plow in shown_prompts or plow in local_seen:
                continue
            if ecols[m % 3].button(prompt, key=f"chat_more_{m}"):
                user_input = prompt
            shown_prompts.add(plow)
            local_seen.add(plow)
            m += 1

    if not ai_key:
        st.info(
            "AI is off, so the chatbot understands simple keywords like 'total spent', "
            "'food expenses', and 'top category'."
        )

    # --- Response
    if user_input:
        # Persist the last interaction so it remains visible after reruns
        st.session_state["chatbot_last_input"] = user_input
        with st.spinner("Thinking..."):
            response = handle_query(user_input)
        st.session_state["chatbot_last_response"] = response
        st.markdown(f"**Bot:** {response}")

    # Show last interaction if present and no new input this run
    if not user_input and "chatbot_last_response" in st.session_state:
        st.markdown(
            f"**You said:** {st.session_state.get('chatbot_last_input','')}"
        )
        st.markdown(f"**Bot:** {st.session_state['chatbot_last_response']}")

    # --- Show Chart Button
    if st.button("📊 Show Category-wise Chart", key="chatbot_chart"):
        fig = draw_category_chart()
        if fig:
            st.pyplot(fig)
        else:
            st.warning("No data available to show chart.")


if __name__ == "__main__":
    # Allow running this module standalone for quick testing
    st.set_page_config(page_title="Smart Expense Chatbot")
    chatbot_tab()