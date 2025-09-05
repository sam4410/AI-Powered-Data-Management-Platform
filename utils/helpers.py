# =============================================================================
# utils/helpers.py - Utility functions
# =============================================================================

"""
utils/helpers.py
Utility functions and helpers for the platform
"""
import sys
import os
import yaml
import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from models.data_models import DataProduct, PlatformConfig
from graphviz import Digraph

logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "DEBUG") -> None:
    """Setup logging configuration for the entire application"""
    log_format = '%(asctime)s - %(process)d - %(filename)s-%(name)s:%(lineno)d - %(levelname)s: %(message)s'

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.DEBUG),
        format=log_format,
        handlers=[
            logging.FileHandler('platform.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )

    # Suppress noisy third-party libraries (optional)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("graphviz").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    logging.debug("Logging setup complete.")

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {file_path}")
        return {}
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file {file_path}: {e}")
        return {}

def save_json_config(data: Dict[str, Any], file_path: str) -> bool:
    """Save data as JSON configuration file"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")
        return False

def create_data_products():
    """Create sample data product backlog"""
    data_products = [
        {
            "id": "DP-001",
            "name": "Customer 360 View",
            "report_suite": ["Customer Profile & Segmentation","Customer Lifetime Value (CLV) & Profitability", "Behavior & Engagement Analytics","Churn & Retention Insights","Customer Support & Experience Metrics","Loyalty & Referral Program Performance"],
            "description": "Complete customer profile with purchase history, engagement, CLV, experiences and preferences",
            "priority": "High",
            "status": "In Progress",
            "business_owner": "Marketing Team",
            "technical_owner": "Data Engineering",
            "expected_completion": "2024-12-31",
            "data_sources": ["customers", "orders", "sales", "products", "customer_interactions", "customer_support", "email_campaigns", "returns", "loyalty_program", "referrals"],
            "use_cases": ["Personalization", "Customer Segmentation", "Churn Prevention"]
        },
        {
            "id": "DP-002",
            "name": "Sales Performance Dashboard",
            "report_suite": ["Revenue & GMV Reports","Sales Conversion Funnel","Product Sales Performance","Sales by Channel & Campaign","Customer Acquisition & Retention Sales View","Regional & Fulfillment-Based Sales Insights"],
            "description": "Real-time sales metrics and performance tracking",
            "priority": "High",
            "status": "Planning",
            "business_owner": "Sales Team",
            "technical_owner": "Analytics Team",
            "expected_completion": "2024-11-30",
            "data_sources": ["customers", "sales", "products", "orders", "returns", "customer_interactions", "abandoned_carts", "campaigns", "shipping"],
            "use_cases": ["Performance Tracking", "Commission Calculation", "Forecasting"]
        },
        {
            "id": "DP-003",
            "name": "Inventory Optimization",
            "report_suite": ["Stock Availability & Health","Demand Forecasting & Seasonality","Inventory Turnover & Aging","Returns Impact on Inventory","Procurement & Replenishment Optimization","Warehouse-Level Inventory Insights"],
            "description": "Optimize inventory levels based on demand patterns",
            "priority": "Medium",
            "status": "Backlog",
            "business_owner": "Operations Team",
            "technical_owner": "Data Science",
            "expected_completion": "2025-01-31",
            "data_sources": ["inventory", "products", "sales", "orders", "campaigns", "returns", "vendors", "warehouses", "shipping"],
            "use_cases": ["Demand Forecasting", "Stock Optimization", "Supplier Management"]
        },
        {
            "id": "DP-004",
            "name": "Employee Performance Analytics",
            "report_suite": ["Fulfillment Center Workforce Productivity","Customer Support Performance","Sales & Category Manager KPIs","Attendance & Shift Adherence (Warehouse/Retail Staff)", "Training & Onboarding Effectiveness", "Performance-Based Incentive Insights"],
            "description": "Track and analyze employee performance metrics",
            "priority": "Medium",
            "status": "Backlog",
            "business_owner": "HR Team",
            "technical_owner": "Analytics Team",
            "expected_completion": "2025-02-28",
            "data_sources": ["shipping", "warehouses", "employees", "customer_support", "sales", "campaigns", "products"],
            "use_cases": ["Performance Review", "Promotion Planning", "Training Needs"]
        },
        {
            "id": "DP-005",
            "name": "Financial Reporting Suite",
            "report_suite": ["Profit & Loss Analysis","Cash Flow & Working Capital Reports","Sales & Revenue Accounting","Cost of Goods Sold (COGS) & Logistics Cost","Returns & Refunds Financial Impact","Tax & Compliance Reporting"],
            "description": "Comprehensive financial reports and analysis",
            "priority": "High",
            "status": "Planning",
            "business_owner": "Finance Team",
            "technical_owner": "Data Engineering",
            "expected_completion": "2024-12-15",
            "data_sources": ["sales", "products", "orders", "returns", "customers", "financial_transactions", "payments", "shipping"],
            "use_cases": ["Monthly Reports", "Budget Planning", "Cost Analysis"]
        }
    ]
    
    # Save to JSON file
    with open('ecommerce_data_products.json', 'w') as f:
        json.dump(data_products, f, indent=2)
    
    logger.info("eCommerce data products created")
    return data_products

def validate_configuration(config: PlatformConfig) -> List[str]:
    """Validate platform configuration"""
    errors = []
    
    if not config.openai_api_key:
        errors.append("OpenAI API key is required")
    
    if not os.path.exists(config.data_catalog_path):
        try:
            os.makedirs(config.data_catalog_path)
        except Exception as e:
            errors.append(f"Cannot create data catalog directory: {e}")
    
    if not os.path.exists(config.results_path):
        try:
            os.makedirs(config.results_path)
        except Exception as e:
            errors.append(f"Cannot create results directory: {e}")
    
    return errors

def create_directory_structure() -> None:
    """Create required directory structure"""
    directories = [
        "config",
        "tools",
        "models", 
        "utils",
        "data_catalog",
        "results",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        
        # Create __init__.py files for Python packages
        if directory in ["tools", "models", "utils"]:
            init_file = Path(directory) / "__init__.py"
            init_file.touch()

def format_execution_time(start_time: datetime, end_time: datetime) -> str:
    """Format execution time for display"""
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def extract_schema_info(db_path: str, db_alias: str = None) -> dict:
    logger = logging.getLogger(__name__)
    abs_path = Path(db_path).resolve()
    if not abs_path.exists():
        raise FileNotFoundError(f"Database file does not exist: {abs_path}")
    
    conn = sqlite3.connect(abs_path)
    cursor = conn.cursor()

    schema = {}
    db_label = db_alias or Path(db_path).stem  # e.g., 'customers_db'

    try:
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        for (table,) in tables:
            try:
                if not table.strip():
                    continue  # skip invalid table names

                cols = cursor.execute(f"PRAGMA table_info({table});").fetchall()
                col_info = [{"name": col[1], "type": col[2], "primary_key": str(bool(col[5]))} for col in cols]

                fks = cursor.execute(f"PRAGMA foreign_key_list({table});").fetchall()
                fk_info = [{"from": fk[3], "to_table": fk[2], "to_column": fk[4]} for fk in fks]

                schema[f"{db_label}.{table}"] = {
                    "columns": col_info,
                    "foreign_keys": fk_info
                }
            
            except Exception as table_error:
                logger.error(f"Error processing table `{table}` in `{db_path}`: {table_error}")

    except Exception as db_error:
        logger.error(f"Metadata extraction failed: {db_error}")

    conn.close()
    return schema