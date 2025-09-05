#!/usr/bin/env python3
"""
Test Data Setup for Agentic Data Management Platform
Creates sample data, databases, and test scenarios
"""

import os
import logging
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import random
from faker import Faker

# from utils.helpers import get_logger

fake = Faker()
logger = logging.getLogger(__name__)

class TestDataSetup:
    """Setup test data and environments for the platform"""
    
    def __init__(self):
        self.db_path = "test_data.db"
        self.logger = logger
        
    def create_sample_databases(self):
        """Create sample databases with realistic data"""
        self.logger.info("Creating sample databases...")
        
        # Create main database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        self._create_customer_table(cursor)
        self._create_orders_table(cursor)
        self._create_products_table(cursor)
        self._create_sales_table(cursor)
        self._create_employees_table(cursor)
        self._create_departments_table(cursor)
        
        # Populate with sample data
        self._populate_customers(cursor)
        self._populate_products(cursor)
        self._populate_departments(cursor)
        self._populate_employees(cursor)
        self._populate_orders(cursor)
        self._populate_sales(cursor)
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Sample database created at {self.db_path}")
    
    def _create_customer_table(self, cursor):
        """Create customer table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                registration_date DATE,
                last_purchase_date DATE,
                total_spent DECIMAL(10,2),
                customer_segment TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        """)
    
    def _create_orders_table(self, cursor):
        """Create orders table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date DATE NOT NULL,
                order_status TEXT NOT NULL,
                total_amount DECIMAL(10,2),
                shipping_address TEXT,
                shipping_city TEXT,
                shipping_state TEXT,
                shipping_zip TEXT,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)
    
    def _create_products_table(self, cursor):
        """Create products table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                brand TEXT,
                price DECIMAL(10,2),
                cost DECIMAL(10,2),
                stock_quantity INTEGER,
                description TEXT,
                weight DECIMAL(8,2),
                dimensions TEXT,
                color TEXT,
                size TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_sales_table(self, cursor):
        """Create sales table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2),
                total_price DECIMAL(10,2),
                discount_amount DECIMAL(10,2) DEFAULT 0,
                sale_date DATE,
                salesperson_id INTEGER,
                commission DECIMAL(10,2),
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                FOREIGN KEY (salesperson_id) REFERENCES employees (employee_id)
            )
        """)
    
    def _create_employees_table(self, cursor):
        """Create employees table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                department_id INTEGER,
                position TEXT,
                hire_date DATE,
                salary DECIMAL(10,2),
                manager_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                performance_score DECIMAL(3,2),
                FOREIGN KEY (department_id) REFERENCES departments (department_id),
                FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
            )
        """)
    
    def _create_departments_table(self, cursor):
        """Create departments table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY,
                department_name TEXT NOT NULL,
                budget DECIMAL(12,2),
                head_count INTEGER,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _populate_customers(self, cursor):
        """Populate customers table with sample data"""
        customers = []
        segments = ['Premium', 'Standard', 'Basic', 'VIP']
        
        for i in range(1000):
            customer = (
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.phone_number(),
                fake.address(),
                fake.city(),
                fake.state(),
                fake.zipcode(),
                fake.country(),
                fake.date_between(start_date='-2y', end_date='today'),
                fake.date_between(start_date='-1y', end_date='today'),
                round(random.uniform(100, 10000), 2),
                random.choice(segments),
                random.choice([True, False])
            )
            customers.append(customer)
        
        cursor.executemany("""
            INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code, country, registration_date, last_purchase_date, total_spent, customer_segment, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customers)
    
    def _populate_products(self, cursor):
        """Populate products table with sample data"""
        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Beauty']
        brands = ['Apple', 'Samsung', 'Nike', 'Adidas', 'Sony', 'Generic']
        colors = ['Red', 'Blue', 'Green', 'Black', 'White', 'Gray']
        sizes = ['S', 'M', 'L', 'XL', 'One Size']
        
        products = []
        for i in range(500):
            category = random.choice(categories)
            product = (
                fake.catch_phrase(),
                category,
                f"{category} Sub",
                random.choice(brands),
                round(random.uniform(10, 1000), 2),
                round(random.uniform(5, 500), 2),
                random.randint(0, 1000),
                fake.text(max_nb_chars=200),
                round(random.uniform(0.1, 50), 2),
                f"{random.randint(1, 50)}x{random.randint(1, 50)}x{random.randint(1, 50)}",
                random.choice(colors),
                random.choice(sizes),
                random.choice([True, False])
            )
            products.append(product)
        
        cursor.executemany("""
            INSERT INTO products (product_name, category, subcategory, brand, price, cost, stock_quantity, description, weight, dimensions, color, size, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products)
    
    def _populate_departments(self, cursor):
        """Populate departments table with sample data"""
        departments = [
            ('Sales', 500000, 25, 'New York'),
            ('Marketing', 300000, 15, 'San Francisco'),
            ('Engineering', 800000, 40, 'Seattle'),
            ('HR', 200000, 8, 'Chicago'),
            ('Finance', 400000, 12, 'New York'),
            ('Operations', 600000, 30, 'Dallas')
        ]
        
        cursor.executemany("""
            INSERT INTO departments (department_name, budget, head_count, location)
            VALUES (?, ?, ?, ?)
        """, departments)
    
    def _populate_employees(self, cursor):
        """Populate employees table with sample data"""
        positions = ['Manager', 'Senior', 'Junior', 'Lead', 'Analyst', 'Coordinator']
        employees = []
        
        for i in range(200):
            employee = (
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.phone_number(),
                random.randint(1, 6),  # department_id
                random.choice(positions),
                fake.date_between(start_date='-5y', end_date='today'),
                round(random.uniform(40000, 150000), 2),
                random.randint(1, 50) if random.random() > 0.3 else None,  # manager_id
                random.choice([True, False]),
                round(random.uniform(1.0, 5.0), 2)
            )
            employees.append(employee)
        
        cursor.executemany("""
            INSERT INTO employees (first_name, last_name, email, phone, department_id, position, hire_date, salary, manager_id, is_active, performance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, employees)
    
    def _populate_orders(self, cursor):
        """Populate orders table with sample data"""
        statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
        payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash']
        
        orders = []
        for i in range(2000):
            order = (
                random.randint(1, 1000),  # customer_id
                fake.date_between(start_date='-1y', end_date='today'),
                random.choice(statuses),
                round(random.uniform(50, 2000), 2),
                fake.address(),
                fake.city(),
                fake.state(),
                fake.zipcode(),
                random.choice(payment_methods)
            )
            orders.append(order)
        
        cursor.executemany("""
            INSERT INTO orders (customer_id, order_date, order_status, total_amount, shipping_address, shipping_city, shipping_state, shipping_zip, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, orders)
    
    def _populate_sales(self, cursor):
        """Populate sales table with sample data"""
        sales = []
        for i in range(5000):
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(10, 500), 2)
            total_price = quantity * unit_price
            discount = round(random.uniform(0, total_price * 0.2), 2)
            
            sale = (
                random.randint(1, 2000),  # order_id
                random.randint(1, 500),   # product_id
                quantity,
                unit_price,
                total_price - discount,
                discount,
                fake.date_between(start_date='-1y', end_date='today'),
                random.randint(1, 200),   # salesperson_id
                round(random.uniform(0, 100), 2)
            )
            sales.append(sale)
        
        cursor.executemany("""
            INSERT INTO sales (order_id, product_id, quantity, unit_price, total_price, discount_amount, sale_date, salesperson_id, commission)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sales)
    
    def create_data_quality_issues(self):
        """Introduce data quality issues for testing"""
        self.logger.info("Creating data quality issues for testing...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create duplicate customers
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code, country, registration_date, last_purchase_date, total_spent, customer_segment, is_active)
            SELECT first_name, last_name, email || '_dup', phone, address, city, state, zip_code, country, registration_date, last_purchase_date, total_spent, customer_segment, is_active
            FROM customers LIMIT 10
        """)
        
        # Create null values in important fields
        cursor.execute("""UPDATE customers SET email = NULL WHERE customer_id IN (SELECT customer_id FROM customers LIMIT 5)""")
        cursor.execute("""UPDATE products SET price = NULL WHERE product_id IN (SELECT product_id FROM products LIMIT 5)""")
        
        # Create inconsistent data
        cursor.execute("""UPDATE customers SET customer_segment = 'PREMIUM' WHERE customer_id IN (SELECT customer_id FROM customers WHERE customer_segment = 'Premium' LIMIT 5)""")
        
        conn.commit()
        conn.close()
        
        self.logger.info("Data quality issues created successfully")
    
    def create_sample_data_products(self):
        """Create sample data product backlog"""
        data_products = [
            {
                "id": 1,
                "name": "Customer 360 View",
                "description": "Complete customer profile with purchase history and preferences",
                "priority": "High",
                "status": "In Progress",
                "business_owner": "Marketing Team",
                "technical_owner": "Data Engineering",
                "expected_completion": "2024-12-31",
                "data_sources": ["customers", "orders", "sales"],
                "use_cases": ["Personalization", "Customer Segmentation", "Churn Prevention"]
            },
            {
                "id": 2,
                "name": "Sales Performance Dashboard",
                "description": "Real-time sales metrics and performance tracking",
                "priority": "High",
                "status": "Planning",
                "business_owner": "Sales Team",
                "technical_owner": "Analytics Team",
                "expected_completion": "2024-11-30",
                "data_sources": ["sales", "employees", "products"],
                "use_cases": ["Performance Tracking", "Commission Calculation", "Forecasting"]
            },
            {
                "id": 3,
                "name": "Inventory Optimization",
                "description": "Optimize inventory levels based on demand patterns",
                "priority": "Medium",
                "status": "Backlog",
                "business_owner": "Operations Team",
                "technical_owner": "Data Science",
                "expected_completion": "2025-01-31",
                "data_sources": ["products", "sales", "orders"],
                "use_cases": ["Demand Forecasting", "Stock Optimization", "Supplier Management"]
            },
            {
                "id": 4,
                "name": "Employee Performance Analytics",
                "description": "Track and analyze employee performance metrics",
                "priority": "Medium",
                "status": "Backlog",
                "business_owner": "HR Team",
                "technical_owner": "Analytics Team",
                "expected_completion": "2025-02-28",
                "data_sources": ["employees", "departments", "sales"],
                "use_cases": ["Performance Review", "Promotion Planning", "Training Needs"]
            },
            {
                "id": 5,
                "name": "Financial Reporting Suite",
                "description": "Comprehensive financial reports and analysis",
                "priority": "High",
                "status": "Planning",
                "business_owner": "Finance Team",
                "technical_owner": "Data Engineering",
                "expected_completion": "2024-12-15",
                "data_sources": ["orders", "sales", "departments"],
                "use_cases": ["Monthly Reports", "Budget Planning", "Cost Analysis"]
            }
        ]
        
        # Save to JSON file
        with open('sample_data_products.json', 'w') as f:
            json.dump(data_products, f, indent=2)
        
        self.logger.info("Sample data products created")
        return data_products
    
    def create_sample_queries(self):
        """Create sample natural language queries for testing Text2SQL"""
        queries = [
            "Show me the top 10 customers by total spending",
            "What are the sales for last month?",
            "List all products that are out of stock",
            "How many orders were placed yesterday?",
            "Show me the average order value by customer segment",
            "Which salesperson has the highest commission this quarter?",
            "What is the total revenue for each product category?",
            "Show me customers who haven't made a purchase in the last 90 days",
            "What are the top 5 best-selling products?",
            "How many employees are in each department?",
            "Show me orders with shipping address in California",
            "What is the conversion rate from orders to sales?",
            "List all premium customers with their contact information",
            "Show me the monthly sales trend for the last 12 months",
            "Which products have the highest profit margin?"
        ]
        
        # Save to JSON file
        with open('sample_queries.json', 'w') as f:
            json.dump(queries, f, indent=2)
        
        self.logger.info("Sample queries created")
        return queries
    
    def create_sample_reports(self):
        """Create sample report templates"""
        reports = [
            {
                "name": "Monthly Sales Report",
                "description": "Monthly sales performance across all channels",
                "schedule": "Monthly",
                "recipients": ["sales@company.com", "management@company.com"],
                "queries": [
                    "SELECT DATE_TRUNC('month', sale_date) as month, SUM(total_price) as revenue FROM sales GROUP BY month",
                    "SELECT p.category, SUM(s.total_price) as revenue FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY p.category"
                ],
                "visualizations": ["bar_chart", "line_chart", "pie_chart"]
            },
            {
                "name": "Customer Segmentation Report",
                "description": "Customer analysis by segment and behavior",
                "schedule": "Weekly",
                "recipients": ["marketing@company.com"],
                "queries": [
                    "SELECT customer_segment, COUNT(*) as count, AVG(total_spent) as avg_spending FROM customers GROUP BY customer_segment",
                    "SELECT customer_segment, COUNT(*) as active_customers FROM customers WHERE is_active = 1 GROUP BY customer_segment"
                ],
                "visualizations": ["pie_chart", "bar_chart"]
            },
            {
                "name": "Product Performance Report",
                "description": "Product sales and inventory analysis",
                "schedule": "Weekly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "queries": [
                    "SELECT p.product_name, SUM(s.quantity) as units_sold, SUM(s.total_price) as revenue FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY p.product_name ORDER BY revenue DESC",
                    "SELECT product_name, stock_quantity FROM products WHERE stock_quantity < 10"
                ],
                "visualizations": ["table", "bar_chart"]
            }
        ]
        
        # Save to JSON file
        with open('sample_reports.json', 'w') as f:
            json.dump(reports, f, indent=2)
        
        self.logger.info("Sample reports created")
        return reports

def setup_test_environment():
    """Main function to set up the complete test environment"""
    setup = TestDataSetup()
    
    try:
        # Create sample databases
        setup.create_sample_databases()
        
        # Introduce data quality issues
        setup.create_data_quality_issues()
        
        # Create sample data products
        setup.create_sample_data_products()
        
        # Create sample queries
        setup.create_sample_queries()
        
        # Create sample reports
        setup.create_sample_reports()
        
        print("✅ Test environment setup completed successfully!")
        print(f"📊 Database created: {setup.db_path}")
        print("📋 Sample data products: sample_data_products.json")
        print("🔍 Sample queries: sample_queries.json")
        print("📈 Sample reports: sample_reports.json")
        
    except Exception as e:
        print(f"❌ Error setting up test environment: {str(e)}")
        raise

if __name__ == "__main__":
    setup_test_environment()