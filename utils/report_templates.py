# utils/report_templates.py

import json

def create_report_templates():
    """Create improved report templates that map to actual database queries"""
    reports = {
        "Customer 360 View": [
            {
                "name": "Customer Profile & Segmentation",
                "description": "Comprehensive report on customer demographics, segmentation and lifecycle stages",
                "type": "customer_profile_report",
                "schedule": "Monthly",
                "recipients": ["sales@company.com", "management@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_products": True,
                    "include_segments": True
                },
                "queries": [
                    """
                    -- Customer demographics by location, age, gender
                    SELECT country, state, AVG(age) AS avg_age, COUNT(*) AS customer_count 
                    FROM customers GROUP BY country, state;
                    """,
                    """
                    -- Customer segmentation
                    SELECT customer_segment, COUNT(*) AS num_customers 
                    FROM customers GROUP BY customer_segment;
                    """,
                    """
                    -- Lifecycle stage
                    SELECT lifecycle_stage, COUNT(*) AS count 
                    FROM customers GROUP BY lifecycle_stage;
                    """
                ],
                "visualizations": ["bar_chart", "line_chart", "pie_chart", "map"]
            },
            {
                "name": "Customer Lifetime Value (CLV) & Profitability", 
                "description": "Customer analysis by CLV, and profitability",
                "type": "customer_clv_report",
                "schedule": "Monthly",
                "recipients": ["marketing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_activity": True,
                    "segment_analysis": True
                },
                "queries": [
                    """
                    -- CLV by acquisition channel
                    SELECT acquisition_channel, AVG(clv_score) AS avg_clv 
                    FROM customers GROUP BY acquisition_channel
                    """,
                    """
                    -- High vs low value customers
                    SELECT
                    CASE
                    WHEN clv_score >= 5000 THEN 'High Value'
                    WHEN clv_score >= 1000 THEN 'Medium Value'
                    ELSE 'Low Value' END AS value_segment, COUNT(*) AS customer_count 
                    FROM customers GROUP BY value_segment;
                    """,
                    """
                    -- Net margin per customer
                    SELECT c.customer_id, c.first_name, SUM(s.total_price - p.cost * s.quantity) AS net_margin
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    JOIN orders o ON s.order_id = o.order_id
                    JOIN customers c ON o.customer_id = c.customer_id
                    GROUP BY c.customer_id;
                    """
                ],
                "visualizations": ["pie_chart", "bar_chart", "scatter_plot"]
            },
            {
                "name": "Behavior & Engagement Analytics",
                "description": "Analysis includes customer behavior and engagement metrics",
                "type": "customer_behavior_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Interaction by device and channel
                    SELECT device_type, channel, COUNT(*) AS interactions
                    FROM customer_interactions
                    GROUP BY device_type, channel;
                    """,
                    """
                    -- Email engagement by cohort
                    SELECT strftime('%Y-%m', sent_date) AS cohort, COUNT(*) AS emails_sent,
                            SUM(opened) AS opened, SUM(clicked) AS clicked
                    FROM email_campaigns
                    GROUP BY cohort;
                    """,
                    """
                    -- Product view to purchase conversion
                    SELECT product_id,
                           COUNT(DISTINCT CASE WHEN interaction_type = 'Page View' THEN session_id END) AS views,
                           COUNT(DISTINCT CASE WHEN interaction_type = 'Purchase' THEN session_id END) AS purchases,
                           ROUND(1.0 * COUNT(DISTINCT CASE WHEN interaction_type = 'Purchase' THEN session_id END) /
                                       NULLIF(COUNT(DISTINCT CASE WHEN interaction_type = 'Page View' THEN session_id END), 0), 2) AS conversion_rate
                    FROM customer_interactions
                    GROUP BY product_id;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Churn & Retention Insights",
                "description": "Analysis includes customer churn and retention metrics",
                "type": "customer_churn_retention_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Churn risk by segment
                    SELECT customer_segment, AVG(churn_risk_score) AS avg_churn_risk
                    FROM customers
                    GROUP BY customer_segment;
                    """,
                    """
                    -- Retention by acquisition source
                    SELECT acquisition_channel,
                           COUNT(*) AS total_customers,
                           SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS retained_customers,
                           ROUND(100.0 * SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS retention_rate
                    FROM customers
                    GROUP BY acquisition_channel;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Customer Support & Experience Metrics",
                "description": "Analysis includes customer experience with customer support metrics",
                "type": "customer_support_experience_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Ticket resolution and volume
                    SELECT agent_id, COUNT(*) AS tickets_handled,
                           AVG(resolution_time_hours) AS avg_resolution_time
                    FROM customer_support
                    GROUP BY agent_id;
                    """,
                    """
                    -- CSAT trend
                    SELECT strftime('%Y-%m', created_date) AS month, AVG(satisfaction_score) AS avg_csat
                    FROM customer_support
                    WHERE satisfaction_score IS NOT NULL
                    GROUP BY month;
                    """,
                    """
                    -- Returns/refunds per customer
                    SELECT customer_id, COUNT(*) AS total_returns, SUM(refund_amount) AS total_refunded
                    FROM returns
                    GROUP BY customer_id;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Loyalty & Referral Program Performance",
                "description": "Analysis includes loyalty and referral program performance metrics",
                "type": "loyalty_refferal_program_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Loyalty tier distribution
                    SELECT tier, COUNT(*) AS customers_in_tier
                    FROM loyalty_program
                    GROUP BY tier;
                    """,
                    """
                    -- Referral acquisition
                    SELECT r.status, COUNT(*) AS total_referrals
                    FROM referrals r
                    GROUP BY r.status;
                    """,
                    """
                    -- Rewards redemption
                    SELECT tier, SUM(points_earned) AS total_earned, SUM(points_redeemed) AS total_redeemed
                    FROM loyalty_program
                    GROUP BY tier;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            }],
        "Sales Performance Dashboard": [
            {
                "name": "Revenue & GMV Reports",
                "description": "Comprehensive report on revenue eaner and gross margin",
                "type": "revenue_margin_report",
                "schedule": "Daily",
                "recipients": ["sales@company.com", "management@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_products": True,
                    "include_segments": True
                },
                "queries": [
                    """
                    -- Daily/weekly/monthly GMV
                    SELECT strftime('%Y-%m-%d', order_date) AS day, SUM(total_amount) AS daily_gmv
                    FROM orders
                    GROUP BY day
                    ORDER BY day DESC;
                    """,
                    """
                    -- Revenue by category
                    SELECT p.category, SUM(s.total_price) AS revenue
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY p.category
                    ORDER BY revenue DESC;
                    """,
                    """
                    -- Returns-adjusted revenue
                    SELECT
                        strftime('%Y-%m', o.order_date) AS month,
                        SUM(o.net_amount) AS gross_revenue,
                        IFNULL(SUM(r.refund_amount), 0) AS total_refunds,
                        SUM(o.net_amount) - IFNULL(SUM(r.refund_amount), 0) AS net_revenue
                    FROM orders o
                    LEFT JOIN returns r ON o.order_id = r.order_id
                    GROUP BY month
                    ORDER BY month DESC;
                    """
                ],
                "visualizations": ["bar_chart", "line_chart", "pie_chart", "map"]
            },
            {
                "name": "Sales Conversion Funnel", 
                "description": "Report for sales conversion funnel",
                "type": "sales_conversion_funnel_report",
                "schedule": "Weekly",
                "recipients": ["marketing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_activity": True,
                    "segment_analysis": True
                },
                "queries": [
                    """
                    -- Funnel counts from customer_interactions + abandoned carts + orders
                    SELECT
                      COUNT(DISTINCT ci.session_id) FILTER (WHERE ci.interaction_type = 'Page View') AS site_visits,
                      COUNT(DISTINCT ci.session_id) FILTER (WHERE ci.interaction_type = 'Add to Cart') AS product_views,
                      COUNT(DISTINCT ac.session_id) AS cart_additions,
                      COUNT(DISTINCT o.order_id) AS completed_orders
                    FROM customer_interactions ci
                    LEFT JOIN abandoned_carts ac ON ci.session_id = ac.session_id
                    LEFT JOIN orders o ON ci.customer_id = o.customer_id;
                    """,
                    """
                    -- Abandoned cart analysis
                    SELECT
                      COUNT(*) AS total_abandoned,
                      SUM(recovered) AS recovered_carts,
                      ROUND(100.0 * SUM(recovered) / COUNT(*), 2) AS recovery_rate
                    FROM abandoned_carts;
                    """,
                    """
                    -- Conversion by device/channel
                    SELECT device_type, channel,
                           COUNT(DISTINCT o.order_id) AS orders,
                           COUNT(DISTINCT c.customer_id) AS unique_customers
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.customer_id
                    GROUP BY device_type, channel;
                    """
                ],
                "visualizations": ["pie_chart", "bar_chart", "scatter_plot"]
            },
            {
                "name": "Product Sales Performance",
                "description": "Analysis includes product sales performance metrics",
                "type": "product_sales_performance_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Top-selling SKUs
                    SELECT p.sku, p.product_name, SUM(s.quantity) AS units_sold, SUM(s.total_price) AS total_revenue
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY p.product_id
                    ORDER BY units_sold DESC
                    LIMIT 10;
                    """,
                    """
                    -- Sales by product category
                    SELECT p.category, COUNT(DISTINCT s.sale_id) AS total_sales, SUM(s.total_price) AS revenue
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY p.category;
                    """,
                    """
                    -- Bundled vs single item (based on order ID having multiple products)
                    SELECT
                      CASE WHEN COUNT(s.product_id) > 1 THEN 'Bundle' ELSE 'Single' END AS order_type,
                      COUNT(DISTINCT s.order_id) AS order_count
                    FROM sales s
                    GROUP BY s.order_id;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Sales by Channel & Campaign",
                "description": "Analysis includes sales metrics by channel and campaigns",
                "type": "sales_by_channel_campaign_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Sales by source/channel
                    SELECT o.channel, COUNT(DISTINCT o.order_id) AS orders, SUM(o.net_amount) AS revenue
                    FROM orders o
                    GROUP BY o.channel
                    ORDER BY revenue DESC;
                    """,
                    """
                    -- Promo/campaign performance
                    SELECT c.campaign_name, c.channel, COUNT(o.order_id) AS orders,
                           SUM(o.net_amount) AS revenue, c.spent, c.revenue AS campaign_revenue,
                           ROUND((c.revenue - c.spent) / NULLIF(c.spent, 0), 2) AS roi
                    FROM campaigns c
                    LEFT JOIN orders o ON c.campaign_id = o.campaign_id
                    GROUP BY c.campaign_id
                    ORDER BY roi DESC;
                    """,
                    """
                    -- Campaign ROI by segment
                    SELECT c.target_segment, AVG(c.roi) AS avg_roi
                    FROM campaigns c
                    GROUP BY c.target_segment
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Customer Acquisition & Retention Sales View",
                "description": "Analysis includes customer acquisition and retention metrics",
                "type": "customer_acquisition_retention_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- New vs returning customer revenue
                    SELECT is_first_order,
                           COUNT(order_id) AS total_orders,
                           SUM(net_amount) AS total_revenue
                    FROM orders
                    GROUP BY is_first_order;
                    """,
                    """
                    -- First purchase trends
                    SELECT strftime('%Y-%m', registration_date) AS cohort,
                           COUNT(*) FILTER (WHERE is_active = 1) AS active_customers,
                           COUNT(*) AS total_customers
                    FROM customers
                    GROUP BY cohort;
                    """,
                    """
                    -- Repeat purchase rate
                    SELECT
                      COUNT(DISTINCT customer_id) FILTER (WHERE order_count > 1) * 1.0 / COUNT(DISTINCT customer_id) AS repeat_purchase_rate
                    FROM (
                      SELECT customer_id, COUNT(*) AS order_count
                      FROM orders
                      GROUP BY customer_id
                    ) sub;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Regional & Fulfillment-Based Sales Insights",
                "description": "Analysis includes regional and fulfillment based performance metrics",
                "type": "regional_fulfillment_sales_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Sales by fulfillment center
                    SELECT fulfillment_center, SUM(net_amount) AS revenue, COUNT(*) AS orders
                    FROM orders
                    GROUP BY fulfillment_center;
                    """,
                    """
                    -- Regional promotion performance
                    SELECT o.shipping_state, c.campaign_name, SUM(o.net_amount) AS regional_revenue
                    FROM orders o
                    JOIN campaigns c ON o.campaign_id = c.campaign_id
                    GROUP BY o.shipping_state, c.campaign_name;
                    """,
                    """
                    -- SLA impact: delayed vs on-time delivery
                    SELECT
                      CASE
                        WHEN julianday(delivery_date) > julianday(estimated_delivery) THEN 'Delayed'
                        ELSE 'On-Time'
                      END AS sla_status,
                      COUNT(*) AS deliveries
                    FROM shipping
                    WHERE delivery_date IS NOT NULL
                    GROUP BY sla_status;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            }],
        "Inventory Optimization": [
            {
                "name": "Stock Availability & Health",
                "description": "Comprehensive report on revenue eaner and gross margin",
                "type": "stock_health_report",
                "schedule": "Daily",
                "recipients": ["sales@company.com", "management@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_products": True,
                    "include_segments": True
                },
                "queries": [
                    """
                    -- Real-time stock levels by SKU
                    SELECT p.sku, p.product_name, i.quantity_available, i.warehouse_id
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id
                    ORDER BY i.quantity_available ASC;
                    """,
                    """
                    -- Stockout and overstock alerts
                    SELECT
                      p.product_name,
                      i.quantity_available,
                      p.reorder_point,
                      p.safety_stock,
                      CASE
                        WHEN i.quantity_available = 0 THEN 'Stockout'
                        WHEN i.quantity_available < p.reorder_point THEN 'Below Reorder Point'
                        WHEN i.quantity_available > p.safety_stock * 2 THEN 'Overstock'
                        ELSE 'Normal'
                      END AS stock_status
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id;
                    """,
                    """
                    -- Safety stock compliance
                    SELECT
                      p.product_name,
                      i.quantity_available,
                      p.safety_stock,
                      CASE
                        WHEN i.quantity_available < p.safety_stock THEN 'Non-Compliant'
                        ELSE 'Compliant'
                      END AS compliance_status
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id;
                    """
                ],
                "visualizations": ["bar_chart", "line_chart", "pie_chart", "map"]
            },
            {
                "name": "Demand Forecasting & Seasonality", 
                "description": "Report for sales conversion funnel",
                "type": "demand_forecasting_report",
                "schedule": "Weekly",
                "recipients": ["marketing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_activity": True,
                    "segment_analysis": True
                },
                "queries": [
                    """
                    -- Monthly sales volume (can be input for ML forecasting)
                    SELECT strftime('%Y-%m', s.sale_date) AS month, s.product_id, p.product_name, SUM(s.quantity) AS total_sold
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY month, s.product_id
                    ORDER BY month DESC;
                    """,
                    """
                    -- Seasonal trends by category
                    SELECT
                      p.category,
                      strftime('%m', s.sale_date) AS month,
                      SUM(s.quantity) AS units_sold
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY p.category, month
                    ORDER BY p.category, month;
                    """,
                    """
                    -- Campaign event stock projection (compare campaign period sales vs stock)
                    SELECT
                      p.product_name,
                      i.quantity_available,
                      SUM(s.quantity) AS campaign_demand
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    JOIN inventory i ON p.product_id = i.product_id
                    JOIN orders o ON s.order_id = o.order_id
                    JOIN campaigns c ON o.campaign_id = c.campaign_id
                    WHERE s.sale_date BETWEEN c.start_date AND c.end_date
                    GROUP BY p.product_id
                    ORDER BY campaign_demand DESC;
                    """
                ],
                "visualizations": ["pie_chart", "bar_chart", "scatter_plot"]
            },
            {
                "name": "Inventory Turnover & Aging",
                "description": "Analysis includes product sales performance metrics",
                "type": "inventory_turnover_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Inventory velocity by product
                    SELECT
                      p.product_name,
                      SUM(s.quantity) AS total_units_sold,
                      AVG(i.quantity_available) AS avg_stock,
                      ROUND(SUM(s.quantity) * 1.0 / NULLIF(AVG(i.quantity_available), 0), 2) AS turnover_ratio
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    JOIN inventory i ON p.product_id = i.product_id
                    GROUP BY p.product_id;
                    """,
                    """
                    -- Aging inventory
                    SELECT
                      p.product_name,
                      julianday('now') - julianday(p.launch_date) AS age_days,
                      i.quantity_available
                    FROM products p
                    JOIN inventory i ON p.product_id = i.product_id
                    WHERE i.quantity_available > 0
                    ORDER BY age_days DESC;
                    """,
                    """
                    -- Days on hand
                    SELECT
                      p.product_name,
                      i.quantity_available,
                      AVG(s.quantity) AS avg_daily_sales,
                      ROUND(i.quantity_available / NULLIF(AVG(s.quantity), 0), 2) AS days_on_hand
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id
                    JOIN sales s ON p.product_id = s.product_id
                    WHERE s.sale_date >= date('now', '-30 days')
                    GROUP BY p.product_id;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Returns Impact on Inventory",
                "description": "Analysis includes sales metrics by channel and campaigns",
                "type": "returns_impact_on_inventory_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Restockable returns by product
                    SELECT
                      p.product_name,
                      COUNT(r.return_id) AS return_count,
                      SUM(CASE WHEN r.restockable = 1 THEN 1 ELSE 0 END) AS restockable_returns
                    FROM returns r
                    JOIN products p ON r.product_id = p.product_id
                    GROUP BY r.product_id;
                    """,
                    """
                    -- Refund rate by SKU
                    SELECT
                      p.sku,
                      COUNT(r.return_id) AS total_returns,
                      SUM(r.refund_amount) AS total_refunded,
                      ROUND(SUM(r.refund_amount) / COUNT(r.return_id), 2) AS avg_refund,
                      p.return_rate
                    FROM returns r
                    JOIN products p ON r.product_id = p.product_id
                    GROUP BY r.product_id;
                    """,
                    """
                    -- Returns effect on inventory planning
                    SELECT
                      p.product_name,
                      SUM(r.refund_amount) AS total_refund_loss,
                      COUNT(r.return_id) FILTER (WHERE r.restockable = 0) AS unusable_returns
                    FROM returns r
                    JOIN products p ON r.product_id = p.product_id
                    GROUP BY p.product_id
                    ORDER BY total_refund_loss DESC;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Procurement & Replenishment Optimization",
                "description": "Analysis includes regional and fulfillment based performance metrics",
                "type": "procurement_replenishment_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Reorder alerts
                    SELECT p.product_name, i.quantity_available, p.reorder_point
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id
                    WHERE i.quantity_available < p.reorder_point;
                    """,
                    """
                    -- Vendor fulfillment performance
                    SELECT v.vendor_name, COUNT(p.product_id) AS products_supplied,
                           AVG(v.performance_score) AS avg_score
                    FROM vendors v
                    JOIN products p ON v.vendor_id = p.vendor_id
                    GROUP BY v.vendor_id
                    ORDER BY avg_score DESC;
                    """,
                    """
                    -- Inventory ROI
                    SELECT
                      p.product_name,
                      p.cost,
                      AVG(s.total_price / s.quantity) AS avg_sales_price,
                      ROUND((AVG(s.total_price / s.quantity) - p.cost) / p.cost * 100, 2) AS roi_percent
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY p.product_id
                    ORDER BY roi_percent DESC;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Warehouse-Level Inventory Insights",
                "description": "Analysis includes regional and fulfillment based performance metrics",
                "type": "warehouse_level_inventory_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Inventory distribution
                    SELECT w.warehouse_name, SUM(i.quantity_available) AS total_stock
                    FROM inventory i
                    JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                    GROUP BY w.warehouse_id;
                    """,
                    """
                    -- Picking/packing efficiency (proxy via shipment volume)
                    SELECT w.warehouse_name, COUNT(s.shipping_id) AS shipments
                    FROM shipping s
                    JOIN warehouses w ON s.warehouse_id = w.warehouse_id
                    GROUP BY w.warehouse_id
                    ORDER BY shipments DESC;
                    """,
                    """
                    -- Stock transfer potential (imbalanced inventory)
                    SELECT
                      p.product_name,
                      i.warehouse_id,
                      i.quantity_available
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id
                    WHERE i.quantity_available > (SELECT AVG(quantity_available) FROM inventory WHERE product_id = i.product_id) * 1.5
                    ORDER BY i.quantity_available DESC;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            }],
        "Employee Performance Analytics": [
            {
                "name": "Fulfillment Center Workforce Productivity",
                "description": "Comprehensive report on revenue eaner and gross margin",
                "type": "fulfillment_center_workforce_report",
                "schedule": "Daily",
                "recipients": ["sales@company.com", "management@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_products": True,
                    "include_segments": True
                },
                "queries": [
                    """
                    -- Orders picked/packed per employee (based on shipping records)
                    SELECT e.employee_id, e.first_name || ' ' || e.last_name AS employee_name,
                           COUNT(s.shipping_id) AS orders_handled
                    FROM shipping s
                    JOIN warehouses w ON s.warehouse_id = w.warehouse_id
                    JOIN employees e ON w.manager_id = e.employee_id
                    GROUP BY e.employee_id
                    ORDER BY orders_handled DESC;
                    """,
                    """
                    -- SLA adherence: shipping delay (dispatch time vs estimate)
                    SELECT
                      s.order_id,
                      s.ship_date,
                      s.estimated_delivery,
                      julianday(s.estimated_delivery) - julianday(s.ship_date) AS estimated_days,
                      julianday(s.delivery_date) - julianday(s.ship_date) AS actual_days,
                      CASE
                        WHEN s.delivery_date <= s.estimated_delivery THEN 'On-Time'
                        ELSE 'Delayed'
                      END AS sla_status
                    FROM shipping s
                    WHERE s.delivery_date IS NOT NULL;
                    """,
                    """
                    -- Shift-wise performance summary
                    SELECT e.shift, COUNT(s.shipping_id) AS shipments
                    FROM shipping s
                    JOIN warehouses w ON s.warehouse_id = w.warehouse_id
                    JOIN employees e ON w.manager_id = e.employee_id
                    GROUP BY e.shift
                    ORDER BY shipments DESC;
                    """
                ],
                "visualizations": ["bar_chart", "line_chart", "pie_chart", "map"]
            },
            {
                "name": "Customer Support Performance", 
                "description": "Report for sales conversion funnel",
                "type": "customer_support_performance_report",
                "schedule": "Weekly",
                "recipients": ["marketing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_activity": True,
                    "segment_analysis": True
                },
                "queries": [
                    """
                    -- Tickets resolved per agent
                    SELECT cs.agent_id, e.first_name || ' ' || e.last_name AS agent_name,
                           COUNT(cs.ticket_id) AS resolved_tickets
                    FROM customer_support cs
                    JOIN employees e ON cs.agent_id = e.employee_id
                    WHERE cs.status IN ('Resolved', 'Closed')
                    GROUP BY cs.agent_id;
                    """,
                    """
                    -- First Contact Resolution (FCR) rate
                    SELECT
                      AVG(CASE WHEN first_contact_resolution = 1 THEN 1.0 ELSE 0 END) * 100 AS fcr_rate
                    FROM customer_support;
                    """,
                    """
                    -- CSAT & NPS by agent/team
                    SELECT cs.agent_id, AVG(cs.satisfaction_score) AS avg_csat, COUNT(cs.ticket_id) AS tickets_handled
                    FROM customer_support cs
                    GROUP BY cs.agent_id
                    ORDER BY avg_csat DESC;
                    """
                ],
                "visualizations": ["pie_chart", "bar_chart", "scatter_plot"]
            },
            {
                "name": "Sales & Category Manager KPIs",
                "description": "Analysis includes product sales performance metrics",
                "type": "sales_and_category_manager_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Revenue managed per salesperson
                    SELECT e.employee_id, e.first_name || ' ' || e.last_name AS name,
                           SUM(s.total_price) AS total_sales
                    FROM sales s
                    JOIN employees e ON s.salesperson_id = e.employee_id
                    GROUP BY e.employee_id
                    ORDER BY total_sales DESC;
                    """,
                    """
                    -- Campaign success metrics by manager (using campaign ROI)
                    SELECT e.employee_id, e.first_name || ' ' || e.last_name AS manager_name,
                           AVG(c.roi) AS avg_campaign_roi
                    FROM campaigns c
                    JOIN employees e ON e.employee_id = c.campaign_id % 50 + 1 -- Simulated mapping
                    GROUP BY e.employee_id
                    ORDER BY avg_campaign_roi DESC;
                    """,
                    """
                    -- SKU onboarding and pricing spread by brand manager
                    SELECT p.brand, COUNT(DISTINCT p.product_id) AS products_onboarded,
                           ROUND(MAX(p.price) - MIN(p.price), 2) AS price_range
                    FROM products p
                    GROUP BY p.brand
                    ORDER BY products_onboarded DESC;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Attendance & Shift Adherence (Warehouse/Retail Staff)",
                "description": "Analysis includes sales metrics by channel and campaigns",
                "type": "attendance_and shift_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Absenteeism trends (inferred from missing shipping assignments or low shift counts)
                    SELECT e.shift, COUNT(*) FILTER (WHERE e.overtime_hours = 0) AS zero_overtime_count,
                           AVG(e.overtime_hours) AS avg_overtime
                    FROM employees e
                    GROUP BY e.shift;
                    """,
                    """
                    -- Late punch-ins and break compliance proxy (not tracked directly, inferred from training + performance)
                    SELECT e.employee_id, e.first_name || ' ' || e.last_name AS name,
                           e.training_completed, e.performance_score
                    FROM employees e
                    WHERE e.training_completed = 0 AND e.performance_score < 2.5;
                    """,
                    """
                    -- Overtime vs output
                    SELECT e.employee_id, e.overtime_hours, e.performance_score,
                           ROUND(e.performance_score / NULLIF(e.overtime_hours, 0), 2) AS performance_per_hour
                    FROM employees e
                    WHERE e.overtime_hours > 0
                    ORDER BY performance_per_hour DESC;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Training & Onboarding Effectiveness",
                "description": "Analysis includes regional and fulfillment based performance metrics",
                "type": "training_and_onboarding_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Ramp-up time (hire date to performance milestone)
                    SELECT e.employee_id, e.hire_date,
                           julianday('now') - julianday(e.hire_date) AS days_since_hired,
                           e.performance_score
                    FROM employees e
                    WHERE e.training_completed = 1;
                    """,
                    """
                    -- Post-training performance lift (compare trained vs untrained)
                    SELECT training_completed,
                           AVG(performance_score) AS avg_score
                    FROM employees
                    GROUP BY training_completed;
                    """,
                    """
                    -- Certification/compliance completion
                    SELECT COUNT(*) AS total_employees,
                           SUM(training_completed) AS certified,
                           ROUND(SUM(training_completed) * 1.0 / COUNT(*) * 100, 2) AS certification_rate
                    FROM employees;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Performance-Based Incentive Insights",
                "description": "Analysis includes regional and fulfillment based performance metrics",
                "type": "performance_based_incentive_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Incentive eligibility by performance
                    SELECT employee_id, performance_score,
                           CASE
                             WHEN performance_score >= 4.0 THEN 'Eligible for Bonus'
                             WHEN performance_score >= 3.0 THEN 'Consider for Bonus'
                             ELSE 'Not Eligible'
                           END AS incentive_status
                    FROM employees;
                    """,
                    """
                    -- Realized vs planned payout
                    SELECT employee_id,
                           commission_rate,
                           actual_sales * commission_rate AS realized_commission,
                           target_sales * commission_rate AS planned_commission
                    FROM employees
                    WHERE commission_rate IS NOT NULL
                    ORDER BY realized_commission DESC;
                    """,
                    """
                    -- Incentives vs customer satisfaction
                    SELECT cs.agent_id, AVG(cs.satisfaction_score) AS avg_csat, e.commission_rate
                    FROM customer_support cs
                    JOIN employees e ON cs.agent_id = e.employee_id
                    GROUP BY cs.agent_id
                    ORDER BY avg_csat DESC;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            }],
        "Financial Reporting Suite": [
            {
                "name": "Profit & Loss Analysis",
                "description": "Comprehensive report on revenue eaner and gross margin",
                "type": "profit_loss_report",
                "schedule": "Daily",
                "recipients": ["sales@company.com", "management@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_products": True,
                    "include_segments": True
                },
                "queries": [
                    """
                    -- P&L by product category
                    SELECT
                      p.category,
                      SUM(s.total_price) AS revenue,
                      SUM(p.cost * s.quantity) AS cogs,
                      SUM(s.total_price) - SUM(p.cost * s.quantity) AS gross_profit
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY p.category
                    ORDER BY gross_profit DESC;
                    """,
                    """
                    -- Net margin after returns, promotions, logistics
                    SELECT
                      o.order_id,
                      o.net_amount AS revenue,
                      IFNULL(r.refund_amount, 0) AS returns,
                      o.discount_amount + o.shipping_amount AS expenses,
                      o.net_amount - IFNULL(r.refund_amount, 0) - (o.discount_amount + o.shipping_amount) AS net_margin
                    FROM orders o
                    LEFT JOIN returns r ON o.order_id = r.order_id;
                    """,
                    """
                    -- Profitability by customer segment
                    SELECT
                      c.customer_segment,
                      SUM(s.total_price) AS revenue,
                      SUM(p.cost * s.quantity) AS cost,
                      SUM(s.total_price - p.cost * s.quantity) AS profit
                    FROM sales s
                    JOIN orders o ON s.order_id = o.order_id
                    JOIN customers c ON o.customer_id = c.customer_id
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY c.customer_segment
                    ORDER BY profit DESC;
                    """
                ],
                "visualizations": ["bar_chart", "line_chart", "pie_chart", "map"]
            },
            {
                "name": "Cash Flow & Working Capital Reports", 
                "description": "Report for sales conversion funnel",
                "type": "cash_flow_working_capital_report",
                "schedule": "Weekly",
                "recipients": ["marketing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_activity": True,
                    "segment_analysis": True
                },
                "queries": [
                    """
                    -- Cash flow from operations (weekly)
                    SELECT strftime('%Y-%W', transaction_date) AS week,
                           SUM(CASE WHEN transaction_type = 'Revenue' THEN amount ELSE 0 END) AS inflow,
                           SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END) AS outflow,
                           SUM(amount) AS net_cash_flow
                    FROM financial_transactions
                    GROUP BY week
                    ORDER BY week DESC;
                    """,
                    """
                    -- Inventory financing and payment cycle proxy
                    SELECT
                      p.product_name,
                      AVG(p.cost) AS avg_cost,
                      AVG(s.total_price / s.quantity) AS avg_sale_price,
                      ROUND((AVG(s.total_price / s.quantity) - AVG(p.cost)) * 30, 2) AS estimated_monthly_margin
                    FROM products p
                    JOIN sales s ON p.product_id = s.product_id
                    GROUP BY p.product_id;
                    """,
                    """
                    -- Refund cash outflow
                    SELECT
                      strftime('%Y-%m', return_date) AS month,
                      SUM(refund_amount) AS total_refunded
                    FROM returns
                    GROUP BY month
                    ORDER BY month DESC;
                    """
                ],
                "visualizations": ["pie_chart", "bar_chart", "scatter_plot"]
            },
            {
                "name": "Sales & Revenue Accounting",
                "description": "Analysis includes product sales performance metrics",
                "type": "sales_and_revenue_accounting_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Bookings vs billings vs realized revenue
                    SELECT
                      strftime('%Y-%m', o.order_date) AS month,
                      COUNT(DISTINCT o.order_id) AS bookings,
                      COUNT(DISTINCT p.payment_id) FILTER (WHERE p.status = 'Completed') AS billings,
                      SUM(p.amount) FILTER (WHERE p.status = 'Completed') AS revenue
                    FROM orders o
                    LEFT JOIN payments p ON o.order_id = p.order_id
                    GROUP BY month;
                    """,
                    """
                    -- Payment method distribution
                    SELECT payment_method, COUNT(*) AS total_transactions, SUM(amount) AS total_value
                    FROM payments
                    GROUP BY payment_method
                    ORDER BY total_value DESC;
                    """,
                    """
                    -- Marketplace vs owned-site revenue
                    SELECT
                      channel,
                      SUM(net_amount) AS revenue
                    FROM orders
                    GROUP BY channel
                    ORDER BY revenue DESC;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Cost of Goods Sold (COGS) & Logistics Cost",
                "description": "Analysis includes sales metrics by channel and campaigns",
                "type": "COGS_logistics_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- COGS by product line
                    SELECT p.category, SUM(p.cost * s.quantity) AS total_cogs
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY p.category
                    ORDER BY total_cogs DESC;
                    """,
                    """
                    -- Fulfillment/shipping cost per order
                    SELECT o.order_id, s.shipping_cost
                    FROM shipping s
                    JOIN orders o ON s.order_id = o.order_id;
                    """,
                    """
                    -- Packaging and delivery cost trends
                    SELECT strftime('%Y-%m', ship_date) AS month,
                           AVG(s.shipping_cost) AS avg_shipping_cost
                    FROM shipping s
                    GROUP BY month
                    ORDER BY month DESC;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Returns & Refunds Financial Impact",
                "description": "Analysis includes regional and fulfillment based performance metrics",
                "type": "returns_and_refunds_impact_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- Value and volume of returns
                    SELECT strftime('%Y-%m', return_date) AS month,
                           COUNT(*) AS num_returns,
                           SUM(refund_amount) AS refund_value
                    FROM returns
                    GROUP BY month
                    ORDER BY month DESC;
                    """,
                    """
                    -- Over-refund or leakage risk
                    SELECT return_id, refund_amount, processing_cost,
                           CASE
                             WHEN refund_amount > 100 THEN 'High Risk'
                             WHEN refund_amount > 50 THEN 'Medium Risk'
                             ELSE 'Low Risk'
                           END AS refund_risk
                    FROM returns;
                    """,
                    """
                    -- Fraudulent return detection proxy (frequent high refunds)
                    SELECT customer_id, COUNT(*) AS num_returns,
                           SUM(refund_amount) AS total_refunded
                    FROM returns
                    GROUP BY customer_id
                    HAVING COUNT(*) > 5 AND SUM(refund_amount) > 500;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            },
            {
                "name": "Tax & Compliance Reporting",
                "description": "Analysis includes regional and fulfillment based performance metrics",
                "type": "tax_and_compliance_report", 
                "schedule": "Monthly",
                "recipients": ["operations@company.com", "purchasing@company.com"],
                "parameters": {
                    "days_back": 30,
                    "include_categories": True
                },
                "queries": [
                    """
                    -- GST/VAT reports by state (assuming 8% tax on orders)
                    SELECT shipping_state,
                           SUM(tax_amount) AS total_tax_collected
                    FROM orders
                    GROUP BY shipping_state
                    ORDER BY total_tax_collected DESC;
                    """,
                    """
                    -- Marketplace TDS/TCS reconciliation proxy
                    SELECT o.channel, SUM(p.processing_fee) AS platform_fee
                    FROM orders o
                    JOIN payments p ON o.order_id = p.order_id
                    WHERE o.channel IN ('Marketplace')
                    GROUP BY o.channel;
                    """,
                    """
                    -- E-invoice compliance (inferred from order + payment status)
                    SELECT o.order_id, p.status, p.transaction_id
                    FROM orders o
                    JOIN payments p ON o.order_id = p.order_id
                    WHERE p.status = 'Completed'
                    ORDER BY o.order_date DESC
                    LIMIT 100;
                    """
                ],
                "visualizations": ["table", "bar_chart", "heatmap"]
            }]
        }
    
    return reports
