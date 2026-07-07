import streamlit as st
from pathlib import Path
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
load_dotenv()

from blogboard.graph.graph import graph

st.set_page_config(page_title="BlogBoard", page_icon="📝", layout="wide")

st.title("📝 BlogBoard — AI Blog Generator")
st.caption("Multi-agent pipeline: Topic selection → Writing → Validation")


def today_ist() -> str:
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%Y-%m-%d")


# ── Sidebar controls ──────────────────────────────
st.sidebar.header("Settings")
mode = st.sidebar.radio("Mode", ["Regular blog", "AI News"])
dry_run = st.sidebar.checkbox("Dry run (no LLM calls)", value=False)
date_str = st.sidebar.text_input("Date (YYYY-MM-DD)", value=today_ist())

generate_btn = st.sidebar.button("🚀 Generate Article", type="primary")

# ── Run pipeline with visible agent steps ─────────
if generate_btn:
    st.session_state.pop("viewing", None)

    step1 = st.empty()
    step2 = st.empty()
    step3 = st.empty()

    step1.info("🔎 **TopicAgent** — selecting a fresh topic...")
    initial_state = {"date": date_str, "dry_run": dry_run}
    if mode == "AI News":
        initial_state["domain"] = "ainews"

    config = {"configurable": {"thread_id": "streamlit-run"}}
    try:
        step2.info("✍️ **WriterAgent** — drafting the article...")
        final_state = graph.invoke(initial_state, config=config)
        step3.info("✅ **ValidatorAgent** — reviewing draft quality...")

        step1.success("🔎 TopicAgent — done")
        step2.success("✍️ WriterAgent — done")
        step3.success("✅ ValidatorAgent — approved")

        st.session_state["final_state"] = final_state
    except Exception as e:
        st.error(f"Failed: {e}")

# ── Show result ───────────────────────────────────
if "final_state" in st.session_state and "viewing" not in st.session_state:
    fs = st.session_state["final_state"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Domain", fs.get("domain", "?"))
    col2.metric("Title", fs.get("title", fs.get("topic", "?")))
    col3.metric("Read time", fs.get("read_time", "?"))

    md_path = fs.get("md_path")
    content = None
    domain = fs.get("domain", "")
    slug = fs.get("slug", "")
    local_guess = Path("local_storage/blogs") / domain / f"{slug}.md"

    if md_path and Path(md_path).exists():
        content = Path(md_path).read_text(encoding="utf-8")
    elif local_guess.exists():
        content = local_guess.read_text(encoding="utf-8")
    elif dry_run:
        st.info("Dry run — no file was written. Preview only.")
        st.json(fs)

    if content:
        st.markdown("---")
        st.download_button(
            "⬇️ Download as Markdown",
            data=content,
            file_name=f"{slug or 'article'}.md",
            mime="text/markdown",
        )
        st.markdown(content)

# ── Browse past articles ──────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Past Articles")
storage_dir = Path("local_storage/blogs")
if storage_dir.exists():
    for domain_dir in storage_dir.iterdir():
        if domain_dir.is_dir():
            for md_file in domain_dir.glob("*.md"):
                if st.sidebar.button(f"{domain_dir.name}/{md_file.stem}", key=str(md_file)):
                    st.session_state["viewing"] = md_file

if "viewing" in st.session_state:
    st.markdown("---")
    col_a, col_b = st.columns([6, 1])
    col_a.subheader(f"📄 {st.session_state['viewing'].stem}")
    if col_b.button("✕ Close"):
        del st.session_state["viewing"]
        st.rerun()
    else:
        content = st.session_state["viewing"].read_text(encoding="utf-8")
        st.download_button(
            "⬇️ Download as Markdown",
            data=content,
            file_name=st.session_state["viewing"].name,
            mime="text/markdown",
        )
        st.markdown(content)