# 🚀 Quickstart Guide

Welcome to the **Agentic AI Platform for Data Management** — an autonomous, multi-agent system designed to streamline enterprise data workflows across multiple databases.

---

## 🧠 What This Platform Does

- Automates **data discovery, cataloging, quality checks, and insights generation**
- Uses **CrewAI agents** to delegate specific tasks like profiling, metadata validation, and report generation
- Supports **multi-database execution** and **natural language analysis**

---

## 🔧 System Requirements

- Python 3.9+
- Streamlit
- crewai, crewai-tools
- SQLite (.db) files as input

> Make sure to place your `.db` files locally or upload them via the app interface.

---

## 🛠️ How to Use the Platform

1. **Launch the App**
   ```bash
   streamlit run app.py

2. **Explore the Overview Tab**
- Learn about the platform, use cases, and architecture
- See agent roles and interaction flow

3. **Upload Your Database**
- Go to the "▶️ Run Pipeline" tab
- Upload one or more .db files (SQLite format)

4. **Select Phase & Execute**
- Choose a specific pipeline phase or run all
- Monitor live progress bars for execution
- View results as structured JSON and Markdown summaries

🔍 Example Use Case
Imagine you upload a database of customer transactions. Here's what happens:
- The Data Research Agent profiles tables and fields
- The Metadata Validation Agent ensures schema consistency
- The Lineage Agent maps relationships between tables
- The Text2SQL Agent lets you ask natural questions like:

"Which product had the highest sales in Q2?"

📁 Output Files
- results/platform_execution_results.json — structured phase-wise output
- results/results_summary.md — human-readable report
- View results directly in the 📊 Results tab

🧩 Tips
- For best results, include schema and at least 100 rows of sample data
- Use consistent naming for columns (e.g., user_id, created_at)
- Check the “📘 Docs” tab for help on each agent and troubleshooting

🔄 Reset or Retry
- Re-upload your DBs to run on new files
- Rerun only failed phases or specific DBs without repeating all work

💡 Need More?
- Explore the Pipeline Phases: https://your-docs-url.com/phases
- Browse Agent Details: https://your-docs-url.com/agents
- Fix common issues in Troubleshooting: https://your-docs-url.com/help

Happy Data Managing! 🎉