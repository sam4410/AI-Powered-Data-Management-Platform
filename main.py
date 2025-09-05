import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from crew import DataManagementCrew
from models.data_models import DataProduct, PlatformConfig
from utils.helpers import setup_logging, create_data_products
from utils.report_generator import generate_markdown_summary
from dotenv import load_dotenv
load_dotenv(override=True)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Starting main.py")

def run():
    """Main execution function"""
    try:
        logger.info("=== Starting Multi-DB Agentic Data Management Platform ===")

        # Set all database URLs
        os.environ["DATABASE_URLS"] = ",".join([
            "sqlite:///databases/ecommerce_db.db"
        ])

        # Initialize configuration
        config = PlatformConfig()

        # Create sample data products
        data_products = create_data_products()

        # Initialize the crew manager
        crew_manager = DataManagementCrew(config)
        logger.info("Crew created")

        # Prepare shared inputs
        crew_inputs = {
            "data_products": [dp.to_dict() for dp in data_products],
            "config": config.to_dict(),
            "execution_mode": "multi_db"
        }

        all_results = {}

        # Run each phase
        logger.info("Executing Data Discovery Phase...")
        discovery_result = crew_manager.run_data_discovery(crew_inputs)
        all_results["data_discovery"] = discovery_result

        logger.info("Executing Data Cataloging Phase...")
        cataloging_result = crew_manager.run_data_cataloging(crew_inputs)
        all_results["data_cataloging"] = cataloging_result

        logger.info("Executing Data Processing Phase...")
        processing_result = crew_manager.run_data_processing(crew_inputs)
        all_results["data_processing"] = processing_result

        logger.info("Executing Insights Generation Phase...")
        insights_result = crew_manager.run_insights_generation(crew_inputs)
        all_results["insights_generation"] = insights_result

        # Save structured results to file
        results_path = Path("results") / "platform_execution_results.json"
        results_path.parent.mkdir(exist_ok=True)
        with open(results_path, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)

        # Save Markdown summary
        summary_path = generate_markdown_summary(str(results_path))
        logger.info(f"📄 Markdown summary saved to: {summary_path}")
        print(f"\nMarkdown Summary created at: {summary_path}")

        # Print clean final report
        print("\n=== Final Summary Report ===")
        for phase, db_results in all_results.items():
            print(f"\n{phase.upper()} RESULTS:")
            for entry in db_results:
                db = entry.get("db")
                print(f"  📂 DB: {db}")
                if "error" in entry:
                    print(f"Error: {entry['error']}")
                else:
                    result_summary = str(entry.get("result"))[:500]
                    print(f"Output Snippet:\n{result_summary}\n")

        logger.info("Multi-DB pipeline execution completed. Results saved.")
        return all_results

    except Exception as e:
        logger.error(f"Platform execution failed: {e}")
        raise
        
def main():
    """Legacy main function for backward compatibility"""
    return run()