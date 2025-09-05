# 🔄 Understanding Pipeline Phases

Your data journey is broken down into four intelligent, AI-driven pipeline stages — each powered by specialized agents.

---

## 1. 🧭 Discovery Phase

**Goal**: Understand the structure, content, and behavior of your databases.

**Key Activities**:
- Schema introspection
- Sample-based data profiling
- Entity identification
- Initial process flow mapping

**Agents Involved**:
- **Data Research Agent**: Profiles tables, columns, and distributions
- **Process Understanding Agent**: Infers high-level flows between datasets

**Outcome**: A baseline understanding of what data exists and how it might relate.

---

## 2. 🗂️ Cataloging Phase

**Goal**: Create a clean, validated catalog of your data assets with lineage context.

**Key Activities**:
- Metadata extraction (columns, data types, constraints)
- Foreign key and relationship detection
- Table- and column-level lineage tracking
- Consolidated integration insights

**Agents Involved**:
- **Metadata Validation Agent**: Ensures schema is accurate and consistent
- **Data Lineage Agent**: Traces data transformations and joins
- **Integration Agent**: Aligns datasets from different sources or DBs

**Outcome**: A machine-readable, validated data catalog enriched with lineage.

---

## 3. 🛡️ Processing Phase

**Goal**: Assess and improve the quality, performance, and observability of your data.

**Key Activities**:
- Rule-based data quality checks (nulls, ranges, duplicates)
- Data anomaly and drift detection
- Indexing and query performance profiling
- Monitoring configurations (e.g., freshness, volume thresholds)

**Agents Involved**:
- **Data Quality Agent**: Applies predefined quality rules
- **Observability Agent**: Tracks long-term behavior or schema drift
- **Performance Tuning Agent**: Suggests DB optimizations

**Outcome**: A health report of your data system and performance tuning guidance.

---

## 4. 📊 Insights Generation Phase

**Goal**: Turn raw data into actionable insights and human-readable narratives.

**Key Activities**:
- Natural language question parsing
- SQL generation using schema awareness
- Query execution and response formatting
- Business reporting and data storytelling

**Agents Involved**:
- **Text2SQL Agent**: Converts natural language to optimized SQL
- **Reports Generation Agent**: Creates formatted summaries and charts
- **Caching Agent** *(optional)*: Speeds up repeated queries

**Outcome**: Actionable insights in plain English, charts, and query-ready data extracts.

---

## 🧠 Phase Independence

Each phase can be executed independently depending on your goals:

- Want to validate your schema? ➤ Run only **Cataloging**
- Need insights from clean data? ➤ Run **Discovery + Insights**
- Running daily health checks? ➤ Run **Processing** alone

Agents are smart enough to handle one phase or all in sequence.

---

🔁 *Phase execution can be chained or triggered conditionally using logic or metadata signals in future enhancements.*