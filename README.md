# 🧠 Agentic AI Platform for Data Management

A comprehensive AI-powered data management platform that leverages CrewAI agents to automate and orchestrate enterprise data management tasks. The platform combines intelligent autonomous agents with advanced analytics to provide data discovery, cataloging, processing, insights generation, and natural language interaction capabilities across multiple databases.

## 🚀 Key Features

### Intelligent Agent System
- **Multi-Phase Pipeline**: Automated discovery, cataloging, processing, and insights generation through coordinated AI agents
- **Modular CrewAI Agents**: Domain-specific agents with specialized goals, tools, and collaborative workflows
- **Agent Coordination**: Multi-agent collaboration with defined roles and task orchestration

### Data Management Capabilities
- **Multi-Database Support**: Execute operations across multiple SQLite databases simultaneously
- **Data Discovery & Cataloging**: Automatically discover, catalog, and organize data assets with intelligent metadata management
- **Data Processing & Insights**: Transform raw data into actionable insights with AI-powered analytics engines
- **Quality Assessment**: Comprehensive data quality checks, observability, and health monitoring

### Natural Language Interaction
- **NL2SQL Engine**: Interact with databases using natural language queries that translate to optimized SQL
- **Conversational Querying**: Ask questions about your data in plain English and receive structured results
- **Query Explanation**: View generated SQL with clear explanations of the logic

### Visual Data Modeling
- **ERD Generation**: Automatically generate comprehensive Entity-Relationship Diagrams from database schemas
- **Interactive Visualization**: Explore table relationships, keys, and schema structures
- **Export Capabilities**: Download diagrams as PNG files for documentation

### Report Generation & Data Products
- **AI-Assisted Report Creation**: Generate professional-grade reports using intelligent agents
- **Configurable Report Templates**: Pre-built templates across 5 comprehensive data product suites
- **Multiple Export Formats**: Download reports in Markdown format with planned PDF support

## 📊 Data Products & Report Templates

The platform implements fixed report templates organized under 5 comprehensive data product suites, providing immediate value across critical business functions:

### 1. Customer 360 View
Comprehensive customer intelligence for data-driven decision making.

- **Customer Profile & Segmentation** - Demographic analysis, behavioral clustering, and cohort identification
- **Customer Lifetime Value (CLV) & Profitability** - Revenue attribution, profitability metrics, and value prediction models
- **Behaviour & Engagement Analytics** - Interaction patterns, purchase frequency, and engagement scoring
- **Churn & Retention Insights** - Risk prediction, retention trends, and customer lifecycle analysis
- **Customer Support & Experience Metrics** - Ticket resolution, satisfaction scores, and service quality indicators
- **Loyalty & Referral Program Performance** - Program effectiveness, referral tracking, and reward redemption analytics

### 2. Sales Performance Dashboard
Real-time visibility into sales operations and revenue drivers.

- **Revenue & GMV Reports** - Top-line metrics, growth trends, and gross merchandise value analysis
- **Sales Conversion Funnel** - Stage-by-stage conversion tracking and bottleneck identification
- **Product Sales Performance** - SKU-level analysis, bestsellers, and underperforming products
- **Sales by Channel & Campaign** - Multi-channel attribution and marketing campaign effectiveness
- **Customer Acquisition & Retention Sales View** - New vs. repeat customer revenue and acquisition costs
- **Regional & Fulfillment-Based Sales Insights** - Geographic performance and fulfillment center analytics

### 3. Inventory Optimization
Intelligent inventory management for reduced costs and improved availability.

- **Stock Availability & Health** - Real-time stock levels, stockout alerts, and inventory health scores
- **Demand Forecasting & Seasonality** - Predictive demand models and seasonal trend analysis
- **Inventory Turnover & Aging** - Turnover ratios, aging reports, and slow-moving inventory identification
- **Returns Impact on Inventory** - Return rate analysis and inventory recovery tracking
- **Procurement & Replenishment Optimization** - Automated reorder recommendations and supplier performance
- **Warehouse-Level Inventory Insights** - Location-specific inventory distribution and efficiency metrics

### 4. Employee Performance Analytics
Data-driven workforce management and performance optimization.

- **Fulfillment Center Workforce Productivity** - Pick rates, pack rates, and operational efficiency metrics
- **Customer Support Performance** - Response times, resolution rates, and CSAT scores by agent
- **Sales & Category Manager KPIs** - Target achievement, pipeline management, and category performance
- **Attendance & Shift Adherence** - Punctuality tracking, shift coverage, and attendance patterns
- **Training & Onboarding Effectiveness** - Skill development tracking and onboarding completion rates
- **Performance-Based Incentive Insights** - Bonus calculations, commission tracking, and incentive program ROI

### 5. Financial Report Suite
Comprehensive financial visibility and compliance reporting.

- **Profit & Loss Analysis** - Income statements, margin analysis, and profitability breakdowns
- **Cash Flow & Working Capital Reports** - Cash position tracking, receivables/payables, and liquidity metrics
- **Sales & Revenue Accounting** - Revenue recognition, deferred revenue, and sales reconciliation
- **Cost of Goods Sold (COGS) & Logistics Cost** - Direct costs, shipping expenses, and logistics efficiency
- **Returns & Refunds Financial Impact** - Return cost analysis and refund trend tracking
- **Tax & Compliance Reporting** - Tax liability calculations, regulatory reports, and audit trails

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
   - Generate reports using the "Generate Report" tab

## 📖 Usage Guide

### User Interface

The platform provides a modern Streamlit-based interface with tabbed navigation for intuitive interaction:

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
- Upload SQLite database files with drag-and-drop support
- Select databases for processing
- Choose pipeline phase (Discovery, Cataloging, Processing, Insights, or All)
- Execute agentic pipeline with real-time progress tracking
- Visual progress indicators during execution

#### 📊 Results
- View pipeline execution results in JSON format
- Access generated Markdown summaries
- Download results for offline analysis
- Review agent performance metrics

#### 🧬 ER Diagram
- Visualize database relationships and schema structures
- Interactive entity-relationship diagrams
- Download diagrams as PNG files for documentation
- Explore table relationships, primary keys, and foreign keys

#### 💬 Ask in Natural Language
- Query databases using conversational English
- View automatically generated SQL queries with explanations
- See query results in formatted tables
- Example queries: "Show me top 10 customers by revenue" or "What are sales trends?"

#### 📝 Generate Report
- Create professional reports using AI agents
- Select from predefined data product report templates
- Configure report parameters and data sources
- Download reports in Markdown format

#### 📘 Docs
- Embedded documentation sections
- Quickstart guides and troubleshooting tips
- Agent directory and pipeline phase explanations
- Best practices and usage patterns

## 🏗️ Architecture

### Core Components

#### CrewAI Integration
- **DataManagementCrew**: Main orchestration class coordinating agent activities
- **Phase-based Execution**: Structured workflow through Discovery → Cataloging → Processing → Insights
- **Agent Coordination**: Multi-agent collaboration with defined roles and dependencies
- **Task Delegation**: Intelligent task assignment based on agent capabilities

#### Data Processing Pipeline
- **Schema Extraction**: Automated database schema analysis and relationship mapping
- **Quality Assessment**: Data quality checks, completeness scoring, and observability metrics
- **Metadata Discovery**: Automated lineage tracking and relationship identification
- **Insights Generation**: AI-powered pattern recognition and anomaly detection

#### Configuration Management
- **PlatformConfig**: Centralized configuration handling for agents and data products
- **Data Products**: Configurable data product definitions with report templates
- **Agent Configuration**: YAML-based agent setup with roles, goals, and tools

### File Structure
```
├── app.py                      # Main Streamlit application
├── main.py                     # Core pipeline execution logic
├── crew.py                     # CrewAI crew definitions and orchestration
├── config/
│   ├── agents.yaml            # Agent configurations (roles, goals, tools)
│   └── data_products.yaml     # Data product and report definitions
├── models/
│   └── data_models.py         # Data model definitions and schemas
├── utils/
│   ├── helpers.py             # Utility functions and helpers
│   ├── report_generator.py    # Report generation utilities
│   ├── er_generator.py        # ER diagram generation logic
│   ├── quality_utils.py       # Data quality assessment utilities
│   └── data_products_loader.py # Data product configuration loader
├── tools/
│   └── analytics_tools.py     # Analytics and reporting tools for agents
├── assets/
│   └── agent_flow.png         # Architecture diagrams and visuals
├── docs/                      # Documentation files and guides
├── results/                   # Generated reports and pipeline outputs
└── uploaded_dbs/              # Uploaded database storage directory
```

## 🔧 Configuration

### Agent Configuration (config/agents.yaml)
Define agents with specific roles, goals, and tool access:

```yaml
agent_name:
  role: "Agent Role"
  goal: "Agent's primary objective"
  backstory: "Agent's background and context"
  tools: ["tool1", "tool2"]
```

### Data Products Configuration (config/data_products.yaml)
Configure data products with associated report templates:

```yaml
- name: "Product Name"
  description: "Product description"
  data_sources: ["source1", "source2"]
  report_suite: ["report1", "report2"]
```

## 🔍 Natural Language Querying

The NL2SQL engine supports intuitive natural language queries:

**Example Queries:**
- "Show me the top 10 customers by revenue"
- "What are the sales trends over the last 30 days?"
- "Which products have the highest return rates?"
- "Find customers who haven't purchased in the last 6 months"
- "What is the average order value by customer segment?"
- "List all products with inventory below reorder level"

The engine automatically translates these queries into optimized SQL and provides clear explanations of the generated logic.

## 🚦 Pipeline Phases

### Discovery Phase
- Database connection validation and health checks
- Schema discovery and structural mapping
- Initial data profiling and statistics collection
- Relationship identification between entities

### Cataloging Phase
- Metadata extraction and organization
- Data lineage identification and documentation
- Quality assessment and scoring
- Business glossary creation

### Processing Phase
- Data transformation and standardization
- Business rule application and validation
- Data enrichment and enhancement
- Quality issue remediation

### Insights Phase
- Pattern recognition and trend analysis
- Anomaly detection and alerting
- Recommendation generation
- Predictive analytics and forecasting

## 🎯 Key Benefits

- **Democratized Data Access**: Enable non-technical users to query databases using natural language
- **Accelerated Insights**: Pre-built report templates deliver immediate value across critical business functions
- **Unified Data View**: Centralized catalog of all data assets with automated discovery and classification
- **Improved Decision Making**: AI-powered analytics surface hidden patterns and actionable insights
- **Reduced Time to Value**: Get from data to decisions faster with automated processing and reporting
- **Autonomous Operations**: Intelligent agents handle complex data management tasks with minimal human intervention
- **Scalable Architecture**: Process multiple databases simultaneously with coordinated agent workflows

## 📈 Monitoring and Logging

The application includes comprehensive monitoring capabilities:
- Debug-level logging for detailed troubleshooting
- Process tracking with timestamps and duration metrics
- Error handling and recovery mechanisms
- Agent performance monitoring and success metrics
- Real-time progress indicators in the UI

## 🔒 Security Considerations

- SQLite databases are stored locally in the `uploaded_dbs/` directory
- No external database connections required
- Session-based state management for user interactions
- File validation for uploaded databases
- Secure handling of sensitive data in reports

## 🚀 Upcoming Features

- **Multi-agent Parallel Execution**: Enhanced performance through agent parallelization
- **Role-based Dashboards**: Specialized views for business and technical teams
- **PDF Export**: Professional report formatting with charts and visualizations
- **Email Notifications**: Real-time alerts and scheduled report delivery
- **Agent Performance Scoring**: Reliability and efficiency metrics for optimization
- **Advanced Connectors**: Support for PostgreSQL, MySQL, and cloud data warehouses
- **API Access**: RESTful API for programmatic access to platform capabilities

## 🛠️ Development

### Running in Development Mode
```bash
streamlit run app.py --logger.level=debug
```

### Adding New Agents
1. Define agent configuration in `config/agents.yaml`
2. Implement agent logic and tasks in `crew.py`
3. Add required tools to the `tools/` directory
4. Test agent interactions and outputs

### Adding New Report Templates
1. Update report template definitions in data products configuration
2. Add template logic to `utils/report_generator.py`
3. Configure data source requirements
4. Test report generation workflow with sample data

### Extending NL2SQL Capabilities
1. Add new query patterns to the NL2SQL engine
2. Enhance SQL generation logic for complex queries
3. Update query explanation templates
4. Test with diverse natural language inputs

## 🐛 Troubleshooting

### Common Issues

**Database Upload Fails**
- Ensure files are valid SQLite databases with `.db` extension
- Check file permissions and size limits
- Verify database is not corrupted

**Pipeline Execution Errors**
- Verify agent configurations in `config/agents.yaml`
- Check database connectivity and schema validity
- Review logs in debug mode for detailed error messages
- Ensure all required tools are properly configured

**Report Generation Issues**
- Ensure data product configuration is correct in `config/data_products.yaml`
- Verify template definitions and parameters
- Check database schema compatibility with report requirements
- Review agent logs for generation failures

**NL2SQL Query Failures**
- Verify database schema is properly discovered
- Check for ambiguous column or table names
- Review generated SQL for syntax issues
- Ensure query complexity is within engine capabilities

### Debug Mode
Enable debug logging by setting the logging level to DEBUG in the application configuration or launch with:
```bash
streamlit run app.py --logger.level=debug
```

## 📝 License

[Add your license information here]

## 🤝 Contributing

We welcome contributions to improve the platform:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Submit a pull request with a detailed description

## 📞 Support

For support and questions:
- Check the embedded documentation in the "Docs" tab
- Review troubleshooting guides in this README
- Submit issues through the repository issue tracker
- Join our community discussions

## 🔗 Links

- [CrewAI Documentation](https://docs.crewai.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

*Built with ❤️ using CrewAI, Streamlit, and advanced AI technologies to transform data complexity into business clarity through intelligent automation and natural language interaction.*
