"""
Enhanced Test Data Setup for eCommerce Agentic Data Management Platform
Creates comprehensive sample data, databases, and test scenarios for all report groups
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
fake = Faker("en_US")

fake = Faker()
logger = logging.getLogger(__name__)

class EnhancedECommerceDataSetup:
    def __init__(self):
        self.db_path = "ecommerce_db.db"
        self.logger = logger

    def create_sample_databases(self):
        print("Creating comprehensive eCommerce database...")

        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"Removed existing database: {self.db_path}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create all tables
        self._create_customer_table(cursor)
        self._create_orders_table(cursor)
        self._create_products_table(cursor)
        self._create_sales_table(cursor)
        self._create_employees_table(cursor)
        self._create_departments_table(cursor)
        
        # Additional tables for comprehensive reporting
        self._create_customer_interactions_table(cursor)
        self._create_inventory_table(cursor)
        self._create_campaigns_table(cursor)
        self._create_customer_support_table(cursor)
        self._create_loyalty_program_table(cursor)
        self._create_returns_table(cursor)
        self._create_payments_table(cursor)
        self._create_shipping_table(cursor)
        self._create_warehouses_table(cursor)
        self._create_vendors_table(cursor)
        self._create_financial_transactions_table(cursor)
        self._create_customer_segments_table(cursor)
        self._create_product_reviews_table(cursor)
        self._create_abandoned_carts_table(cursor)
        self._create_email_campaigns_table(cursor)
        self._create_referrals_table(cursor)

        print("Populating data...")
        self._populate_departments(cursor)
        self._populate_warehouses(cursor)
        self._populate_vendors(cursor)
        self._populate_customers(cursor)
        self._populate_customer_segments(cursor)
        self._populate_products(cursor)
        self._populate_inventory(cursor)
        self._populate_employees(cursor)
        self._populate_campaigns(cursor)
        self._populate_orders(cursor)
        self._populate_sales(cursor)
        self._populate_payments(cursor)
        self._populate_shipping(cursor)
        self._populate_customer_interactions(cursor)
        self._populate_customer_support(cursor)
        self._populate_loyalty_program(cursor)
        self._populate_returns(cursor)
        self._populate_financial_transactions(cursor)
        self._populate_product_reviews(cursor)
        self._populate_abandoned_carts(cursor)
        self._populate_email_campaigns(cursor)
        self._populate_referrals(cursor)

        conn.commit()
        conn.close()
        print(f"Enhanced eCommerce database created at {self.db_path}")

    def _create_customer_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
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
                is_active BOOLEAN DEFAULT 1,
                age INTEGER,
                gender TEXT,
                acquisition_channel TEXT,
                lifecycle_stage TEXT,
                clv_score DECIMAL(10,2),
                churn_risk_score DECIMAL(3,2),
                preferred_category TEXT,
                communication_preference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def _create_customer_segments_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_segments (
                segment_id INTEGER PRIMARY KEY,
                segment_name TEXT NOT NULL,
                min_spend DECIMAL(10,2),
                max_spend DECIMAL(10,2),
                characteristics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def _create_orders_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date DATE NOT NULL,
                order_status TEXT NOT NULL,
                total_amount DECIMAL(10,2),
                discount_amount DECIMAL(10,2) DEFAULT 0,
                tax_amount DECIMAL(10,2) DEFAULT 0,
                shipping_amount DECIMAL(10,2) DEFAULT 0,
                net_amount DECIMAL(10,2),
                shipping_address TEXT,
                shipping_city TEXT,
                shipping_state TEXT,
                shipping_zip TEXT,
                payment_method TEXT,
                channel TEXT,
                campaign_id INTEGER,
                warehouse_id INTEGER,
                fulfillment_center TEXT,
                order_source TEXT,
                device_type TEXT,
                is_first_order BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns (campaign_id),
                FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
            )
        """)

    def _create_products_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                sku TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                brand TEXT,
                price DECIMAL(10,2),
                cost DECIMAL(10,2),
                margin DECIMAL(10,2),
                stock_quantity INTEGER,
                reorder_point INTEGER,
                safety_stock INTEGER,
                description TEXT,
                weight DECIMAL(8,2),
                dimensions TEXT,
                color TEXT,
                size TEXT,
                vendor_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                launch_date DATE,
                avg_rating DECIMAL(3,2),
                review_count INTEGER,
                return_rate DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id)
            )
        """)

    def _create_inventory_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id INTEGER PRIMARY KEY,
                product_id INTEGER,
                warehouse_id INTEGER,
                quantity_on_hand INTEGER,
                quantity_reserved INTEGER,
                quantity_available INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
            )
        """)

    def _create_sales_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2),
                total_price DECIMAL(10,2),
                discount_amount DECIMAL(10,2) DEFAULT 0,
                tax_amount DECIMAL(10,2) DEFAULT 0,
                sale_date DATE,
                salesperson_id INTEGER,
                commission DECIMAL(10,2),
                profit_margin DECIMAL(10,2),
                channel TEXT,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                FOREIGN KEY (salesperson_id) REFERENCES employees (employee_id)
            )
        """)

    def _create_employees_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY,
                employee_code TEXT UNIQUE,
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
                target_sales DECIMAL(10,2),
                actual_sales DECIMAL(10,2),
                commission_rate DECIMAL(3,2),
                work_location TEXT,
                shift TEXT,
                overtime_hours INTEGER DEFAULT 0,
                training_completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (department_id) REFERENCES departments (department_id),
                FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
            )
        """)

    def _create_departments_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY,
                department_name TEXT NOT NULL,
                budget DECIMAL(12,2),
                head_count INTEGER,
                location TEXT,
                manager_id INTEGER,
                cost_center TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
            )
        """)

    def _create_customer_interactions_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_interactions (
                interaction_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                interaction_type TEXT,
                channel TEXT,
                interaction_date TIMESTAMP,
                duration_minutes INTEGER,
                page_views INTEGER,
                clicks INTEGER,
                bounce_rate DECIMAL(3,2),
                device_type TEXT,
                session_id TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)

    def _create_campaigns_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                campaign_id INTEGER PRIMARY KEY,
                campaign_name TEXT NOT NULL,
                campaign_type TEXT,
                start_date DATE,
                end_date DATE,
                budget DECIMAL(10,2),
                spent DECIMAL(10,2),
                impressions INTEGER,
                clicks INTEGER,
                conversions INTEGER,
                revenue DECIMAL(10,2),
                roi DECIMAL(10,2),
                target_segment TEXT,
                channel TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def _create_customer_support_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_support (
                ticket_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                agent_id INTEGER,
                ticket_type TEXT,
                priority TEXT,
                status TEXT,
                subject TEXT,
                description TEXT,
                created_date TIMESTAMP,
                resolved_date TIMESTAMP,
                resolution_time_hours INTEGER,
                satisfaction_score INTEGER,
                first_contact_resolution BOOLEAN,
                escalated BOOLEAN DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                FOREIGN KEY (agent_id) REFERENCES employees (employee_id)
            )
        """)

    def _create_loyalty_program_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_program (
                loyalty_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                tier TEXT,
                points_earned INTEGER,
                points_redeemed INTEGER,
                points_balance INTEGER,
                tier_start_date DATE,
                tier_end_date DATE,
                lifetime_value DECIMAL(10,2),
                referral_count INTEGER,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)

    def _create_returns_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                return_id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_id INTEGER,
                customer_id INTEGER,
                return_date DATE,
                reason TEXT,
                condition TEXT,
                refund_amount DECIMAL(10,2),
                restockable BOOLEAN,
                processing_cost DECIMAL(10,2),
                approved_by INTEGER,
                status TEXT,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                FOREIGN KEY (approved_by) REFERENCES employees (employee_id)
            )
        """)

    def _create_payments_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY,
                order_id INTEGER,
                payment_method TEXT,
                payment_provider TEXT,
                amount DECIMAL(10,2),
                currency TEXT DEFAULT 'USD',
                payment_date TIMESTAMP,
                status TEXT,
                transaction_id TEXT,
                processing_fee DECIMAL(10,2),
                FOREIGN KEY (order_id) REFERENCES orders (order_id)
            )
        """)

    def _create_shipping_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipping (
                shipping_id INTEGER PRIMARY KEY,
                order_id INTEGER,
                carrier TEXT,
                tracking_number TEXT,
                ship_date DATE,
                delivery_date DATE,
                estimated_delivery DATE,
                shipping_cost DECIMAL(10,2),
                delivery_status TEXT,
                warehouse_id INTEGER,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
            )
        """)

    def _create_warehouses_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id INTEGER PRIMARY KEY,
                warehouse_name TEXT NOT NULL,
                location TEXT,
                capacity INTEGER,
                current_utilization DECIMAL(3,2),
                manager_id INTEGER,
                operational_cost DECIMAL(10,2),
                FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
            )
        """)

    def _create_vendors_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                vendor_id INTEGER PRIMARY KEY,
                vendor_name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                payment_terms TEXT,
                lead_time_days INTEGER,
                performance_score DECIMAL(3,2),
                total_orders INTEGER,
                total_value DECIMAL(12,2)
            )
        """)

    def _create_financial_transactions_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_transactions (
                transaction_id INTEGER PRIMARY KEY,
                transaction_type TEXT,
                amount DECIMAL(10,2),
                currency TEXT DEFAULT 'USD',
                transaction_date DATE,
                description TEXT,
                category TEXT,
                department_id INTEGER,
                reference_id TEXT,
                status TEXT,
                FOREIGN KEY (department_id) REFERENCES departments (department_id)
            )
        """)

    def _create_product_reviews_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_reviews (
                review_id INTEGER PRIMARY KEY,
                product_id INTEGER,
                customer_id INTEGER,
                rating INTEGER,
                review_text TEXT,
                review_date DATE,
                verified_purchase BOOLEAN,
                helpful_votes INTEGER,
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)

    def _create_abandoned_carts_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS abandoned_carts (
                cart_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                session_id TEXT,
                product_id INTEGER,
                quantity INTEGER,
                unit_price DECIMAL(10,2),
                abandoned_date TIMESTAMP,
                recovery_email_sent BOOLEAN DEFAULT 0,
                recovered BOOLEAN DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        """)

    def _create_email_campaigns_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_campaigns (
                email_campaign_id INTEGER PRIMARY KEY,
                campaign_id INTEGER,
                customer_id INTEGER,
                email_type TEXT,
                sent_date TIMESTAMP,
                opened BOOLEAN DEFAULT 0,
                clicked BOOLEAN DEFAULT 0,
                converted BOOLEAN DEFAULT 0,
                unsubscribed BOOLEAN DEFAULT 0,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (campaign_id),
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)

    def _create_referrals_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                referral_id INTEGER PRIMARY KEY,
                referrer_id INTEGER,
                referee_id INTEGER,
                referral_date DATE,
                referral_code TEXT,
                status TEXT,
                reward_amount DECIMAL(10,2),
                reward_redeemed BOOLEAN DEFAULT 0,
                FOREIGN KEY (referrer_id) REFERENCES customers (customer_id),
                FOREIGN KEY (referee_id) REFERENCES customers (customer_id)
            )
        """)

    # Population methods
    def _populate_departments(self, cursor):
        departments = [
            ('Sales', 500000, 25, 'New York', 'SALES001'),
            ('Marketing', 300000, 15, 'San Francisco', 'MKT001'),
            ('Engineering', 800000, 40, 'Seattle', 'ENG001'),
            ('HR', 200000, 8, 'Chicago', 'HR001'),
            ('Finance', 400000, 12, 'New York', 'FIN001'),
            ('Operations', 600000, 30, 'Dallas', 'OPS001'),
            ('Customer Service', 250000, 20, 'Austin', 'CS001'),
            ('Data Analytics', 350000, 18, 'Boston', 'DA001')
        ]
        cursor.executemany("""
            INSERT INTO departments (department_name, budget, head_count, location, cost_center)
            VALUES (?, ?, ?, ?, ?)
        """, departments)

    def _populate_warehouses(self, cursor):
        warehouses = [
            ('East Coast Hub', 'New York, NY', 50000, 0.75, 150000),
            ('West Coast Hub', 'Los Angeles, CA', 60000, 0.80, 180000),
            ('Central Hub', 'Chicago, IL', 45000, 0.70, 140000),
            ('South Hub', 'Atlanta, GA', 40000, 0.65, 130000),
            ('Northwest Hub', 'Seattle, WA', 35000, 0.60, 120000)
        ]
        cursor.executemany("""
            INSERT INTO warehouses (warehouse_name, location, capacity, current_utilization, operational_cost)
            VALUES (?, ?, ?, ?, ?)
        """, warehouses)

    def _populate_vendors(self, cursor):
        vendors = []
        for i in range(50):
            vendor = (
                f"Vendor {i+1}",
                fake.name(),
                fake.email(),
                fake.phone_number(),
                fake.address(),
                random.choice(['Net 30', 'Net 45', 'Net 60', 'COD']),
                random.randint(7, 30),
                round(random.uniform(3.0, 5.0), 2),
                random.randint(10, 500),
                round(random.uniform(50000, 1000000), 2)
            )
            vendors.append(vendor)
        cursor.executemany("""
            INSERT INTO vendors (vendor_name, contact_person, email, phone, address, payment_terms, lead_time_days, performance_score, total_orders, total_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, vendors)

    def _populate_customer_segments(self, cursor):
        segments = [
            ('Premium', 5000, 999999, 'High-value customers with frequent purchases'),
            ('Standard', 1000, 4999, 'Regular customers with moderate spending'),
            ('Basic', 0, 999, 'New or low-spending customers'),
            ('VIP', 10000, 999999, 'Top-tier customers with highest lifetime value')
        ]
        cursor.executemany("""
            INSERT INTO customer_segments (segment_name, min_spend, max_spend, characteristics)
            VALUES (?, ?, ?, ?)
        """, segments)

    def _populate_customers(self, cursor):
        customers = []
        segments = ['Premium', 'Standard', 'Basic', 'VIP']
        channels = ['Organic', 'Social Media', 'Email', 'Paid Search', 'Referral', 'Direct']
        lifecycle_stages = ['New', 'Active', 'Dormant', 'Churned', 'Reactivated']
        
        for i in range(15000):
            email = f"customer_{i}_{fake.email()}"
            customer = (
                fake.first_name(),
                fake.last_name(),
                email,
                fake.phone_number(),
                fake.street_address(),
                fake.city(),
                fake.state(),
                fake.zipcode(),
                "United States",  # Hardcoded country
                fake.date_between(start_date='-2y', end_date='today'),
                fake.date_between(start_date='-1y', end_date='today'),
                round(random.uniform(100, 15000), 2),
                random.choice(segments),
                random.choice([True, False]),
                random.randint(18, 75),
                random.choice(['M', 'F', 'Other']),
                random.choice(channels),
                random.choice(lifecycle_stages),
                round(random.uniform(500, 20000), 2),
                round(random.uniform(0.1, 0.9), 2),
                random.choice(['Electronics', 'Clothing', 'Home', 'Sports', 'Books']),
                random.choice(['Email', 'SMS', 'Phone', 'Mail'])
            )
            customers.append(customer)

        cursor.executemany("""
            INSERT INTO customers (
                first_name, last_name, email, phone, address, city, state, zip_code, country,
                registration_date, last_purchase_date, total_spent, customer_segment, is_active,
                age, gender, acquisition_channel, lifecycle_stage, clv_score, churn_risk_score,
                preferred_category, communication_preference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customers)

    def _populate_products(self, cursor):
        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Beauty', 'Toys', 'Automotive']
        brands = ['Apple', 'Samsung', 'Nike', 'Adidas', 'Sony', 'Generic', 'Dell', 'HP', 'Canon']
        colors = ['Red', 'Blue', 'Green', 'Black', 'White', 'Gray', 'Yellow', 'Pink']
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'One Size']
        
        products = []
        for i in range(2000):
            category = random.choice(categories)
            price = round(random.uniform(10, 2000), 2)
            cost = round(price * random.uniform(0.4, 0.7), 2)
            margin = price - cost
            
            product = (
                f"SKU{i:06d}",
                fake.catch_phrase(),
                category,
                f"{category} Sub",
                random.choice(brands),
                price,
                cost,
                margin,
                random.randint(0, 1000),
                random.randint(10, 100),
                random.randint(5, 50),
                fake.text(max_nb_chars=200),
                round(random.uniform(0.1, 50), 2),
                f"{random.randint(1, 50)}x{random.randint(1, 50)}x{random.randint(1, 50)}",
                random.choice(colors),
                random.choice(sizes),
                random.randint(1, 50),
                random.choice([True, False]),
                fake.date_between(start_date='-2y', end_date='today'),
                round(random.uniform(1.0, 5.0), 2),
                random.randint(0, 500),
                round(random.uniform(0.05, 0.25), 2)
            )
            products.append(product)
        cursor.executemany("""
            INSERT INTO products (sku, product_name, category, subcategory, brand, price, cost, margin, stock_quantity, reorder_point, safety_stock, description, weight, dimensions, color, size, vendor_id, is_active, launch_date, avg_rating, review_count, return_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products)

    def _populate_inventory(self, cursor):
        inventory = []
        for product_id in range(1, 2001):
            for warehouse_id in range(1, 6):
                on_hand = random.randint(0, 500)
                reserved = random.randint(0, min(on_hand, 50))
                available = on_hand - reserved
                
                inv_record = (
                    product_id,
                    warehouse_id,
                    on_hand,
                    reserved,
                    available
                )
                inventory.append(inv_record)
        cursor.executemany("""
            INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, quantity_reserved, quantity_available)
            VALUES (?, ?, ?, ?, ?)
        """, inventory)

    def _populate_employees(self, cursor):
        positions = ['Manager', 'Senior', 'Junior', 'Lead', 'Analyst', 'Coordinator', 'Specialist']
        locations = ['New York', 'San Francisco', 'Seattle', 'Chicago', 'Dallas', 'Austin', 'Boston']
        shifts = ['Morning', 'Afternoon', 'Evening', 'Night']
        
        employees = []
        for i in range(800):
            email = f"employee_{i}_{fake.email()}"
            salary = round(random.uniform(40000, 200000), 2)
            employee = (
                f"EMP{i:04d}",
                fake.first_name(),
                fake.last_name(),
                email,
                fake.phone_number(),
                random.randint(1, 8),
                random.choice(positions),
                fake.date_between(start_date='-5y', end_date='today'),
                salary,
                random.randint(1, 800) if random.random() > 0.3 else None,
                random.choice([True, False]),
                round(random.uniform(1.0, 5.0), 2),
                round(random.uniform(50000, 300000), 2),
                round(random.uniform(40000, 250000), 2),
                round(random.uniform(0.05, 0.15), 2),
                random.choice(locations),
                random.choice(shifts),
                random.randint(0, 20),
                random.choice([True, False])
            )
            employees.append(employee)
        cursor.executemany("""
            INSERT INTO employees (employee_code, first_name, last_name, email, phone, department_id, position, hire_date, salary, manager_id, is_active, performance_score, target_sales, actual_sales, commission_rate, work_location, shift, overtime_hours, training_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, employees)

    def _populate_campaigns(self, cursor):
        campaign_types = ['Email', 'Social Media', 'PPC', 'Display', 'Affiliate', 'Influencer']
        channels = ['Google Ads', 'Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'Email', 'YouTube']
        statuses = ['Active', 'Completed', 'Paused', 'Draft']
        
        campaigns = []
        for i in range(100):
            budget = round(random.uniform(1000, 50000), 2)
            spent = round(budget * random.uniform(0.1, 1.0), 2)
            impressions = random.randint(1000, 100000)
            clicks = random.randint(10, int(impressions * 0.05))
            conversions = random.randint(1, int(clicks * 0.1))
            revenue = round(conversions * random.uniform(50, 500), 2)
            roi = round((revenue - spent) / spent * 100, 2) if spent > 0 else 0
            
            campaign = (
                f"Campaign {i+1}",
                random.choice(campaign_types),
                fake.date_between(start_date='-1y', end_date='today'),
                fake.date_between(start_date='today', end_date='+30d'),
                budget,
                spent,
                impressions,
                clicks,
                conversions,
                revenue,
                roi,
                random.choice(['Premium', 'Standard', 'Basic', 'VIP']),
                random.choice(channels),
                random.choice(statuses)
            )
            campaigns.append(campaign)
        cursor.executemany("""
            INSERT INTO campaigns (campaign_name, campaign_type, start_date, end_date, budget, spent, impressions, clicks, conversions, revenue, roi, target_segment, channel, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, campaigns)

    def _populate_orders(self, cursor):
        """Generate realistic order data"""
        statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Returned']
        payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash', 'UPI', 'Wallet']
        channels = ['Website', 'Mobile App', 'Phone', 'Store', 'Marketplace']
        devices = ['Desktop', 'Mobile', 'Tablet']
        sources = ['Direct', 'Google', 'Facebook', 'Instagram', 'Email', 'Referral']
        
        orders = []
        for i in range(1, 25001):  # 25000 orders (1.67 orders per customer on average)
            order_date = fake.date_between(start_date='-2y', end_date='today')
            total_amount = round(random.uniform(25.0, 2500.0), 2)
            discount_amount = round(total_amount * random.uniform(0, 0.3), 2)
            tax_amount = round(total_amount * 0.08, 2)  # 8% tax
            shipping_amount = round(random.uniform(0, 50.0), 2)
            net_amount = total_amount - discount_amount + tax_amount + shipping_amount
            
            order = (
                i,  # order_id
                random.randint(1, 15000),  # customer_id (updated to match 15000 customers)
                order_date,
                random.choice(statuses),
                total_amount,
                discount_amount,
                tax_amount,
                shipping_amount,
                net_amount,
                fake.street_address(),
                fake.city(),
                fake.state(),
                fake.zipcode(),
                random.choice(payment_methods),
                random.choice(channels),
                random.randint(1, 50) if random.random() < 0.3 else None,  # campaign_id
                random.randint(1, 10),  # warehouse_id
                f"FC-{random.randint(1, 5)}",
                random.choice(sources),
                random.choice(devices),
                1 if random.random() < 0.2 else 0,  # is_first_order
                datetime.now() - timedelta(days=random.randint(0, 730)),
                datetime.now() - timedelta(days=random.randint(0, 30))
            )
            orders.append(order)
        
        cursor.executemany("""
            INSERT INTO orders (order_id, customer_id, order_date, order_status, total_amount,
                               discount_amount, tax_amount, shipping_amount, net_amount,
                               shipping_address, shipping_city, shipping_state, shipping_zip,
                               payment_method, channel, campaign_id, warehouse_id,
                               fulfillment_center, order_source, device_type, is_first_order,
                               created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, orders)
        print(f"Inserted {len(orders)} orders")

    def _populate_sales(self, cursor):
        """Generate sales data linked to orders"""
        sales = []
        channels = ['Website', 'Mobile App', 'Phone', 'Store', 'Marketplace']
        
        for order_id in range(1, 25001):  # Updated to match 25000 orders
            # Each order has 1-5 sales items
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                unit_price = round(random.uniform(10.0, 500.0), 2)
                quantity = random.randint(1, 10)
                total_price = unit_price * quantity
                discount_amount = round(total_price * random.uniform(0, 0.2), 2)
                tax_amount = round(total_price * 0.08, 2)
                
                sale = (
                    len(sales) + 1,  # sale_id
                    order_id,
                    random.randint(1, 1000),  # product_id
                    quantity,
                    unit_price,
                    total_price,
                    discount_amount,
                    tax_amount,
                    fake.date_between(start_date='-2y', end_date='today'),
                    random.randint(1, 100) if random.random() < 0.7 else None,  # salesperson_id
                    round(total_price * random.uniform(0.02, 0.15), 2),  # commission
                    round(random.uniform(0.1, 0.4), 2),  # profit_margin
                    random.choice(channels)
                )
                sales.append(sale)
        
        cursor.executemany("""
            INSERT INTO sales (sale_id, order_id, product_id, quantity, unit_price,
                              total_price, discount_amount, tax_amount, sale_date,
                              salesperson_id, commission, profit_margin, channel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sales)
        print(f"Inserted {len(sales)} sales records")

    def _populate_customer_interactions(self, cursor):
        """Generate customer interaction data"""
        interaction_types = ['Page View', 'Search', 'Add to Cart', 'Purchase', 'Support', 'Review']
        channels = ['Website', 'Mobile App', 'Email', 'Phone', 'Chat']
        devices = ['Desktop', 'Mobile', 'Tablet']
        
        interactions = []
        for i in range(1, 75001):  # 75000 interactions (5 per customer on average)
            interaction = (
                i,
                random.randint(1, 15000),  # customer_id (updated to match 15000 customers)
                random.choice(interaction_types),
                random.choice(channels),
                fake.date_time_between(start_date='-1y', end_date='now'),
                random.randint(1, 120),  # duration_minutes
                random.randint(1, 50),   # page_views
                random.randint(0, 20),   # clicks
                round(random.uniform(0.1, 0.9), 2),  # bounce_rate
                random.choice(devices),
                fake.uuid4()  # session_id
            )
            interactions.append(interaction)
        
        cursor.executemany("""
            INSERT INTO customer_interactions (interaction_id, customer_id, interaction_type,
                                             channel, interaction_date, duration_minutes,
                                             page_views, clicks, bounce_rate, device_type, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, interactions)
        print(f"Inserted {len(interactions)} customer interactions")

    def _populate_customer_support(self, cursor):
        """Generate customer support ticket data"""
        ticket_types = ['Technical', 'Billing', 'Shipping', 'Returns', 'Product Inquiry', 'Account']
        priorities = ['Low', 'Medium', 'High', 'Critical']
        statuses = ['Open', 'In Progress', 'Resolved', 'Closed', 'Escalated']
        
        tickets = []
        for i in range(1, 12001):  # 12000 tickets (0.8 tickets per customer)
            created_date = fake.date_time_between(start_date='-1y', end_date='now')
            resolved_date = created_date + timedelta(hours=random.randint(1, 168)) if random.random() < 0.8 else None
            
            ticket = (
                i,
                random.randint(1, 15000),  # customer_id (updated to match 15000 customers)
                random.randint(1, 50),    # agent_id
                random.choice(ticket_types),
                random.choice(priorities),
                random.choice(statuses),
                fake.sentence(nb_words=6),  # subject
                fake.text(max_nb_chars=500),  # description
                created_date,
                resolved_date,
                int((resolved_date - created_date).total_seconds() / 3600) if resolved_date else None,
                random.randint(1, 5) if resolved_date else None,  # satisfaction_score
                1 if random.random() < 0.7 else 0,  # first_contact_resolution
                1 if random.random() < 0.1 else 0   # escalated
            )
            tickets.append(ticket)
        
        cursor.executemany("""
            INSERT INTO customer_support (ticket_id, customer_id, agent_id, ticket_type,
                                        priority, status, subject, description, created_date,
                                        resolved_date, resolution_time_hours, satisfaction_score,
                                        first_contact_resolution, escalated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tickets)
        print(f"Inserted {len(tickets)} support tickets")

    def _populate_loyalty_program(self, cursor):
        """Generate loyalty program data"""
        tiers = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond']
        
        loyalty_records = []
        for i in range(1, 15001):  # 15000 loyalty records (1:1 mapping with customers)
            tier = random.choice(tiers)
            points_earned = random.randint(100, 50000)
            points_redeemed = random.randint(0, points_earned // 2)
            
            record = (
                i,
                i,  # customer_id (1:1 mapping with all 15000 customers)
                tier,
                points_earned,
                points_redeemed,
                points_earned - points_redeemed,  # points_balance
                fake.date_between(start_date='-2y', end_date='today'),
                fake.date_between(start_date='today', end_date='+1y'),
                round(random.uniform(100.0, 10000.0), 2),  # lifetime_value
                random.randint(0, 20)  # referral_count
            )
            loyalty_records.append(record)
        
        cursor.executemany("""
            INSERT INTO loyalty_program (loyalty_id, customer_id, tier, points_earned,
                                       points_redeemed, points_balance, tier_start_date,
                                       tier_end_date, lifetime_value, referral_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, loyalty_records)
        print(f"Inserted {len(loyalty_records)} loyalty program records")

    def _populate_returns(self, cursor):
        """Generate return data"""
        reasons = ['Defective', 'Wrong Size', 'Not as Described', 'Changed Mind', 'Damaged in Shipping']
        conditions = ['New', 'Like New', 'Good', 'Fair', 'Poor']
        statuses = ['Pending', 'Approved', 'Rejected', 'Processed', 'Completed']
        
        returns = []
        for i in range(1, 3001):  # 3000 returns (12% return rate)
            order_id = random.randint(1, 25000)  # Updated to match 25000 orders
            refund_amount = round(random.uniform(10.0, 500.0), 2)
            
            return_record = (
                i,
                order_id,
                random.randint(1, 1000),  # product_id
                random.randint(1, 15000),  # customer_id (updated to match 15000 customers)
                fake.date_between(start_date='-1y', end_date='today'),
                random.choice(reasons),
                random.choice(conditions),
                refund_amount,
                1 if random.random() < 0.8 else 0,  # restockable
                round(refund_amount * 0.1, 2),  # processing_cost
                random.randint(1, 50),  # approved_by
                random.choice(statuses)
            )
            returns.append(return_record)
        
        cursor.executemany("""
            INSERT INTO returns (return_id, order_id, product_id, customer_id, return_date,
                               reason, condition, refund_amount, restockable, processing_cost,
                               approved_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, returns)
        print(f"Inserted {len(returns)} returns")

    def _populate_payments(self, cursor):
        """Generate payment data"""
        payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'UPI', 'Wallet', 'Cash']
        providers = ['Stripe', 'PayPal', 'Square', 'Razorpay', 'Paytm', 'Bank']
        statuses = ['Pending', 'Completed', 'Failed', 'Refunded', 'Cancelled']
        
        payments = []
        for i in range(1, 25001):  # 25000 payments (one payment per order)
            payment = (
                i,
                i,  # order_id (updated to match 25000 orders)
                random.choice(payment_methods),
                random.choice(providers),
                round(random.uniform(25.0, 2500.0), 2),  # amount
                'USD',
                fake.date_time_between(start_date='-2y', end_date='now'),
                random.choice(statuses),
                fake.uuid4()[:20],  # transaction_id
                round(random.uniform(0.5, 25.0), 2)  # processing_fee
            )
            payments.append(payment)
        
        cursor.executemany("""
            INSERT INTO payments (payment_id, order_id, payment_method, payment_provider,
                                amount, currency, payment_date, status, transaction_id, processing_fee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, payments)
        print(f"Inserted {len(payments)} payments")

    def _populate_shipping(self, cursor):
        """Generate shipping data"""
        carriers = ['FedEx', 'UPS', 'DHL', 'USPS', 'Amazon Logistics', 'Local Courier']
        statuses = ['Pending', 'Picked Up', 'In Transit', 'Out for Delivery', 'Delivered', 'Exception']
        
        shipments = []
        for i in range(1, 22501):  # 22500 shipments (90% of orders)
            ship_date = fake.date_between(start_date='-2y', end_date='today')
            estimated_delivery = ship_date + timedelta(days=random.randint(1, 7))
            delivery_date = estimated_delivery + timedelta(days=random.randint(-1, 3)) if random.random() < 0.9 else None
            
            shipment = (
                i,
                i,  # order_id (updated to match scaled orders)
                random.choice(carriers),
                fake.bothify(text='??########'),  # tracking_number
                ship_date,
                delivery_date,
                estimated_delivery,
                round(random.uniform(5.0, 50.0), 2),  # shipping_cost
                random.choice(statuses),
                random.randint(1, 10)  # warehouse_id
            )
            shipments.append(shipment)
        
        cursor.executemany("""
            INSERT INTO shipping (shipping_id, order_id, carrier, tracking_number,
                                ship_date, delivery_date, estimated_delivery,
                                shipping_cost, delivery_status, warehouse_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, shipments)
        print(f"Inserted {len(shipments)} shipments")

    def _populate_financial_transactions(self, cursor):
        """Generate financial transaction data"""
        transaction_types = ['Revenue', 'Expense', 'Refund', 'Commission', 'Fee', 'Tax']
        categories = ['Sales', 'Marketing', 'Operations', 'HR', 'IT', 'Finance', 'Legal']
        statuses = ['Pending', 'Completed', 'Failed', 'Cancelled']
        
        transactions = []
        for i in range(1, 40001):  # 40000 transactions (increased for more financial data)
            transaction = (
                i,
                random.choice(transaction_types),
                round(random.uniform(-5000.0, 10000.0), 2),  # amount (negative for expenses)
                'USD',
                fake.date_between(start_date='-2y', end_date='today'),
                fake.sentence(nb_words=8),  # description
                random.choice(categories),
                random.randint(1, 10),  # department_id
                fake.bothify(text='REF-########'),  # reference_id
                random.choice(statuses)
            )
            transactions.append(transaction)
        
        cursor.executemany("""
            INSERT INTO financial_transactions (transaction_id, transaction_type, amount,
                                              currency, transaction_date, description,
                                              category, department_id, reference_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, transactions)
        print(f"Inserted {len(transactions)} financial transactions")

    def _populate_product_reviews(self, cursor):
        """Generate product review data"""
        reviews = []
        for i in range(1, 30001):  # 30000 reviews (2 per customer on average)
            review = (
                i,
                random.randint(1, 1000),  # product_id
                random.randint(1, 15000),  # customer_id (updated to match 15000 customers)
                random.randint(1, 5),     # rating
                fake.text(max_nb_chars=500),  # review_text
                fake.date_between(start_date='-2y', end_date='today'),
                1 if random.random() < 0.8 else 0,  # verified_purchase
                random.randint(0, 50)  # helpful_votes
            )
            reviews.append(review)
        
        cursor.executemany("""
            INSERT INTO product_reviews (review_id, product_id, customer_id, rating,
                                       review_text, review_date, verified_purchase, helpful_votes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, reviews)
        print(f"Inserted {len(reviews)} product reviews")

    def _populate_abandoned_carts(self, cursor):
        """Generate abandoned cart data"""
        carts = []
        for i in range(1, 7501):  # 7500 abandoned carts (0.5 per customer)
            cart = (
                i,
                random.randint(1, 15000),  # customer_id (updated to match 15000 customers)
                fake.uuid4(),  # session_id
                random.randint(1, 1000),  # product_id
                random.randint(1, 5),     # quantity
                round(random.uniform(10.0, 500.0), 2),  # unit_price
                fake.date_time_between(start_date='-6m', end_date='now'),
                1 if random.random() < 0.6 else 0,  # recovery_email_sent
                1 if random.random() < 0.2 else 0   # recovered
            )
            carts.append(cart)
        
        cursor.executemany("""
            INSERT INTO abandoned_carts (cart_id, customer_id, session_id, product_id,
                                       quantity, unit_price, abandoned_date,
                                       recovery_email_sent, recovered)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, carts)
        print(f"Inserted {len(carts)} abandoned carts")

    def _populate_email_campaigns(self, cursor):
        """Generate email campaign data"""
        email_types = ['Welcome', 'Promotional', 'Abandoned Cart', 'Order Confirmation', 'Newsletter', 'Reactivation']
        
        campaigns = []
        for i in range(1, 90001):  # 90000 email campaigns (6 per customer on average)
            campaign = (
                i,
                random.randint(1, 50),    # campaign_id
                random.randint(1, 15000),  # customer_id (updated to match 15000 customers)
                random.choice(email_types),
                fake.date_time_between(start_date='-1y', end_date='now'),
                1 if random.random() < 0.25 else 0,  # opened
                1 if random.random() < 0.05 else 0,  # clicked
                1 if random.random() < 0.02 else 0,  # converted
                1 if random.random() < 0.01 else 0   # unsubscribed
            )
            campaigns.append(campaign)
        
        cursor.executemany("""
            INSERT INTO email_campaigns (email_campaign_id, campaign_id, customer_id,
                                       email_type, sent_date, opened, clicked,
                                       converted, unsubscribed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, campaigns)
        print(f"Inserted {len(campaigns)} email campaigns")

    def _populate_referrals(self, cursor):
        """Generate referral data"""
        statuses = ['Pending', 'Completed', 'Expired', 'Cancelled']
        
        referrals = []
        for i in range(1, 2251):  # 2250 referrals (15% of customers referring)
            referral = (
                i,
                random.randint(1, 15000),  # referrer_id (updated to match 15000 customers)
                random.randint(1, 15000),  # referee_id (updated to match 15000 customers)
                fake.date_between(start_date='-1y', end_date='today'),
                fake.bothify(text='REF-########'),  # referral_code
                random.choice(statuses),
                round(random.uniform(5.0, 50.0), 2),  # reward_amount
                1 if random.random() < 0.7 else 0     # reward_redeemed
            )
            referrals.append(referral)
        
        cursor.executemany("""
            INSERT INTO referrals (referral_id, referrer_id, referee_id, referral_date,
                                 referral_code, status, reward_amount, reward_redeemed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, referrals)
        print(f"Inserted {len(referrals)} referrals")
        
def main():
    """Main function to execute the database setup"""
    print("=" * 60)
    print("eCommerce Agentic Data Management Platform")
    print("Enhanced Test Data Setup")
    print("=" * 60)
    print(f"Starting database setup at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize the data setup class
        setup = EnhancedECommerceDataSetup()
        
        # Create and populate the database
        print("Phase 1: Creating database structure and populating data...")
        setup.create_sample_databases()
        
        print()
        print("=" * 60)
        print("DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        # Display summary statistics
        print("\nSUMMARY OF GENERATED DATA:")
        print("-" * 40)
        print(f"📊 Orders:                    25,000")
        print(f"📈 Sales Records:             ~75,000+")
        print(f"👥 Customer Interactions:     75,000")
        print(f"🎫 Support Tickets:           12,000")
        print(f"🏆 Loyalty Records:           15,000")
        print(f"↩️  Returns:                   3,000")
        print(f"💳 Payments:                  25,000")
        print(f"📦 Shipments:                 22,500")
        print(f"💰 Financial Transactions:    40,000")
        print(f"⭐ Product Reviews:           30,000")
        print(f"🛒 Abandoned Carts:           7,500")
        print(f"📧 Email Campaigns:           90,000")
        print(f"🤝 Referrals:                 2,250")
        print("-" * 40)
        print(f"📁 Database file: {setup.db_path}")
        print(f"✅ Setup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nNEXT STEPS:")
        print("1. Use the generated database for testing your agentic platform")
        print("2. Run analytical queries on the comprehensive dataset")
        print("3. Test report generation across all 13 tables")
        print("4. Validate data relationships and integrity")
        
    except Exception as e:
        print(f"❌ ERROR: Database setup failed!")
        print(f"Error details: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    """Entry point for command line execution"""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ecommerce_setup.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Execute main function
    exit_code = main()
    sys.exit(exit_code)