# 🧠 Agentic AI Platform for Data Management

A comprehensive Streamlit-based platform that leverages CrewAI agents to automate and orchestrate enterprise data management tasks across multiple databases. The platform provides intelligent data discovery, cataloging, processing, and insights generation through autonomous AI agents.

## 🚀 Features

### Core Capabilities
- **Multi-Phase Pipeline**: Automated discovery, cataloging, processing, and insights generation
- **Intelligent Agent System**: Modular CrewAI agents with domain-specific goals and tools
- **Multi-Database Support**: Execute operations across multiple SQLite databases simultaneously
- **Natural Language Querying**: Ask questions about your data in plain English
- **Automated Report Generation**: Create professional-grade reports with AI assistance
- **Visual Data Modeling**: Automatic ER diagram generation from database schemas
- **Data Product Management**: Organize and manage data products with configurable report suites

### User Interface
- **Interactive Web Dashboard**: Modern Streamlit interface with tabbed navigation
- **Real-time Progress Tracking**: Visual progress indicators during pipeline execution
- **Export Capabilities**: Download reports in Markdown format and diagrams as PNG
- **File Management**: Upload and manage multiple database files
- **Schema Visualization**: Interactive database schema exploration

## 📋 Prerequisites

- Python 3.8 or higher
- SQLite databases for analysis
- Required Python packages (see requirements.txt)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd agentic-data-platform
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration files:**
   - Ensure `config/agents.yaml` exists with agent configurations
   - Create `config/data_products.yaml` for data product definitions
   - Set up any required environment variables

## 🚀 Quick Start

1. **Launch the application:**
   ```bash
   streamlit run app.py
   ```

2. **Access the web interface:**
   - Open your browser and navigate to `http://localhost:8501`

3. **Upload your data:**
   - Go to the "Run Pipeline" tab
   - Upload one or more SQLite database files (.db format)

4. **Execute the pipeline:**
   - Select databases and choose a pipeline phase
   - Click "Execute" to run the agentic analysis

5. **Explore results:**
   - View results in the "Results" tab
   - Generate ER diagrams in the "ER Diagram" tab
   - Ask natural language questions in the "Ask in Natural Language" tab

## 📖 Usage Guide

### Tab Navigation

#### 📚 Overview
- Platform introduction and key features
- Usage instructions and expectations
- Architecture flow diagram
- Links to documentation and tutorials

#### 👥 Agents
- Directory of available CrewAI agents
- Agent roles, goals, and capabilities
- Tools and backstories for each agent

#### ▶️ Run Pipeline
- Upload SQLite database files
- Select databases for processing
- Choose pipeline phase (Discovery, Cataloging, Processing, Insights, or All)
- Execute agentic pipeline with real-time progress tracking

#### 📊 Results
- View pipeline execution results in JSON format
- Access generated Markdown summaries
- Download results for offline analysis

#### 🧬 ER Diagram
- Visualize database relationships
- Interactive entity-relationship diagrams
- Download diagrams as PNG files

#### 💬 Ask in Natural Language
- Query databases using natural language
- View generated SQL and explanations
- See query results in tabular format

#### 📝 Generate Report
- Create professional reports using AI agents
- Select from predefined report templates
- Configure report parameters
- Download reports in Markdown format

#### 📘 Docs
- Embedded documentation sections
- Quickstart guides and troubleshooting
- Agent directory and pipeline phase explanations

## 🏗️ Architecture

### Core Components

#### CrewAI Integration
- **DataManagementCrew**: Main orchestration class
- **Phase-based execution**: Discovery → Cataloging → Processing → Insights
- **Agent coordination**: Multi-agent collaboration with defined roles

#### Data Processing Pipeline
- **Schema extraction**: Automated database schema analysis
- **Quality assessment**: Data quality checks and observability
- **Metadata discovery**: Lineage and relationship identification
- **Insights generation**: AI-powered data insights

#### Configuration Management
- **PlatformConfig**: Centralized configuration handling
- **Data Products**: Configurable data product definitions
- **Agent Configuration**: YAML-based agent setup

### File Structure
```
├── app.py                      # Main Streamlit application
├── main.py                     # Core pipeline execution
├── crew.py                     # CrewAI crew definitions
├── config/
│   ├── agents.yaml            # Agent configurations
│   └── data_products.yaml     # Data product definitions
├── models/
│   └── data_models.py         # Data model definitions
├── utils/
│   ├── helpers.py             # Utility functions
│   ├── report_generator.py    # Report generation utilities
│   ├── er_generator.py        # ER diagram generation
│   ├── quality_utils.py       # Data quality utilities
│   └── data_products_loader.py # Data product configuration loader
├── tools/
│   └── analytics_tools.py     # Analytics and reporting tools
├── assets/
│   └── agent_flow.png         # Architecture diagrams
├── docs/                      # Documentation files
├── results/                   # Generated reports and outputs
└── uploaded_dbs/              # Uploaded database storage
```

## 🔧 Configuration

### Agent Configuration (config/agents.yaml)
```yaml
agent_name:
  role: "Agent Role"
  goal: "Agent's primary objective"
  backstory: "Agent's background and context"
  tools: ["tool1", "tool2"]
```

### Data Products Configuration (config/data_products.yaml)
```yaml
- name: "Product Name"
  description: "Product description"
  data_sources: ["source1", "source2"]
  report_suite: ["report1", "report2"]
```

## 📊 Report Templates

The platform supports various report types:
- **Customer Analytics**: Customer behavior and segmentation
- **Sales Performance**: Revenue analysis and trends
- **Data Quality**: Data health and completeness reports
- **Operational Insights**: Process efficiency and performance

## 🔍 Natural Language Querying

The platform supports natural language queries such as:
- "Show me the top 10 customers by revenue"
- "What are the sales trends over the last 30 days?"
- "Which products have the highest return rates?"
- "Find customers who haven't purchased in the last 6 months"

## 🚦 Pipeline Phases

### Discovery Phase
- Database connection and validation
- Schema discovery and mapping
- Initial data profiling

### Cataloging Phase
- Metadata extraction and organization
- Data lineage identification
- Quality assessment

### Processing Phase
- Data transformation and cleaning
- Business rule application
- Enrichment and enhancement

### Insights Phase
- Pattern recognition and analysis
- Anomaly detection
- Recommendation generation

## 📈 Monitoring and Logging

The application includes comprehensive logging:
- Debug-level logging for detailed troubleshooting
- Process tracking with timestamps
- Error handling and recovery mechanisms
- Performance monitoring

## 🔒 Security Considerations

- SQLite databases are stored locally in the `uploaded_dbs/` directory
- No external database connections required
- Session-based state management
- File validation for uploaded databases

## 🚀 Upcoming Features

- **Multi-agent parallel execution**: Enhanced performance through parallelization
- **Role-based dashboards**: Specialized views for business and technical teams
- **PDF export**: Professional report formatting
- **Email notifications**: Real-time alerts and updates
- **Agent performance scoring**: Reliability and efficiency metrics

## 🛠️ Development

### Running in Development Mode
```bash
streamlit run app.py --logger.level=debug
```

### Adding New Agents
1. Define agent in `config/agents.yaml`
2. Implement agent logic in `crew.py`
3. Add required tools to the tools directory

### Adding New Report Templates
1. Update `utils/report_templates.py`
2. Add template configuration to data products
3. Test report generation workflow

## 🐛 Troubleshooting

### Common Issues

**Database Upload Fails**
- Ensure files are valid SQLite databases (.db extension)
- Check file permissions and size limits

**Pipeline Execution Errors**
- Verify agent configurations in `config/agents.yaml`
- Check database connectivity and schema validity
- Review logs for detailed error messages

**Report Generation Issues**
- Ensure data product configuration is correct
- Verify template definitions and parameters
- Check database schema compatibility

### Debug Mode
Enable debug logging by setting the logging level to DEBUG in the application configuration.

## 📝 License

[Add your license information here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For support and questions:
- Check the embedded documentation in the "Docs" tab
- Review troubleshooting guides
- Submit issues through the repository issue tracker

## 🔗 Links

- [CrewAI Documentation](https://docs.crewai.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

*Built with ❤️ using CrewAI and Streamlit*
