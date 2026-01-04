-- ====================================================================
-- MINGOS RESTAURANT DATABASE - SQL QUERIES FOR REPORT
-- ====================================================================

-- ====================================================================
-- 1. LIST OF ALL TABLES CREATED
-- ====================================================================
SHOW TABLES;

-- ====================================================================
-- 2. TABLE CREATION QUERIES (All Tables)
-- ====================================================================

-- Note: Django creates these automatically via migrations, but here are the equivalent SQL statements

-- Table 1: mingos_supplier
CREATE TABLE mingos_supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(200),
    gst_number VARCHAR(20),
    status VARCHAR(20)
);

-- Table 2: mingos_ingredient
CREATE TABLE mingos_ingredient (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL,
    current_stock_qty DECIMAL(10, 2) DEFAULT 0,
    safety_stock_qty DECIMAL(10, 2) DEFAULT 0,
    reorder_level DECIMAL(10, 2) DEFAULT 0,
    is_perishable TINYINT(1) DEFAULT 0,
    status VARCHAR(20)
);

-- Table 3: mingos_menucategory
CREATE TABLE mingos_menucategory (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(200)
);

-- Table 4: mingos_menuitem
CREATE TABLE mingos_menuitem (
    menu_item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    is_available TINYINT(1) DEFAULT 1,
    spice_level VARCHAR(20),
    is_vegetarian TINYINT(1) DEFAULT 0,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES mingos_menucategory(category_id) ON DELETE SET NULL
);

-- Table 5: mingos_supplieringredient
CREATE TABLE mingos_supplieringredient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES mingos_supplier(supplier_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES mingos_ingredient(ingredient_id) ON DELETE CASCADE,
    UNIQUE KEY (supplier_id, ingredient_id)
);

-- Table 6: mingos_purchaseorder
CREATE TABLE mingos_purchaseorder (
    po_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    order_date DATE NOT NULL,
    received_date DATE,
    expected_delivery_date DATE,
    total_amount DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20),
    FOREIGN KEY (supplier_id) REFERENCES mingos_supplier(supplier_id) ON DELETE PROTECT
);

-- Table 7: mingos_purchaseorderline
CREATE TABLE mingos_purchaseorderline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_order_id INT NOT NULL,
    line_no INT NOT NULL,
    ingredient_id INT NOT NULL,
    ordered_qty DECIMAL(10, 2) NOT NULL,
    received_qty DECIMAL(10, 2) DEFAULT 0,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (purchase_order_id) REFERENCES mingos_purchaseorder(po_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES mingos_ingredient(ingredient_id) ON DELETE PROTECT,
    UNIQUE KEY (purchase_order_id, line_no)
);

-- Table 8: mingos_recipe
CREATE TABLE mingos_recipe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    menu_item_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity_required DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (menu_item_id) REFERENCES mingos_menuitem(menu_item_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES mingos_ingredient(ingredient_id) ON DELETE CASCADE,
    UNIQUE KEY (menu_item_id, ingredient_id)
);

-- Table 9: mingos_customerorder
CREATE TABLE mingos_customerorder (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_datetime DATETIME NOT NULL,
    order_type VARCHAR(20) DEFAULT 'DINE_IN',
    order_status VARCHAR(20) DEFAULT 'PENDING',
    payment_mode VARCHAR(50),
    total_amount DECIMAL(10, 2) DEFAULT 0
);

-- Table 10: mingos_orderitem
CREATE TABLE mingos_orderitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_order_id) REFERENCES mingos_customerorder(order_id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES mingos_menuitem(menu_item_id) ON DELETE PROTECT,
    UNIQUE KEY (customer_order_id, menu_item_id)
);


-- ====================================================================
-- 3. TABLE POPULATION QUERIES (Sample Data for at least 3 tables)
-- ====================================================================

-- Populate Table 1: mingos_menucategory
INSERT INTO mingos_menucategory (name, description) VALUES 
('Appetizers', 'Starters and light bites'),
('Main Course', 'Rice and curry dishes'),
('Beverages', 'Drinks and refreshments'),
('Desserts', 'Sweet treats');

-- Populate Table 2: mingos_menuitem
INSERT INTO mingos_menuitem (name, price, is_available, spice_level, is_vegetarian, category_id) VALUES
('Chicken Biryani', 250.00, 1, 'Medium', 0, 2),
('Paneer Tikka', 180.00, 1, 'Mild', 1, 1),
('Mutton Curry', 320.00, 1, 'Hot', 0, 2),
('Veg Fried Rice', 150.00, 1, 'Mild', 1, 2),
('Samosa', 60.00, 1, 'Medium', 1, 1),
('Mango Lassi', 80.00, 1, NULL, 1, 3),
('Gulab Jamun', 70.00, 1, NULL, 1, 4);

-- Populate Table 3: mingos_ingredient
INSERT INTO mingos_ingredient (name, unit_of_measure, current_stock_qty, safety_stock_qty, reorder_level, is_perishable) VALUES
('Basmati Rice', 'kg', 50.00, 10.00, 15.00, 0),
('Chicken', 'kg', 25.00, 5.00, 8.00, 1),
('Paneer', 'kg', 15.00, 3.00, 5.00, 1),
('Onion', 'kg', 30.00, 5.00, 10.00, 1),
('Tomato', 'kg', 20.00, 5.00, 8.00, 1),
('Ginger-Garlic Paste', 'kg', 5.00, 1.00, 2.00, 1),
('Cooking Oil', 'litre', 20.00, 3.00, 5.00, 0),
('Spices Mix', 'kg', 10.00, 2.00, 3.00, 0),
('Yogurt', 'kg', 12.00, 2.00, 4.00, 1),
('Mango Pulp', 'kg', 8.00, 2.00, 3.00, 1);

-- Populate Table 4: mingos_supplier
INSERT INTO mingos_supplier (name, phone, email, address, gst_number, status) VALUES
('Fresh Foods Suppliers', '9876543210', 'contact@freshfoods.com', '123 Market Street, Mumbai', 'GST123456', 'ACTIVE'),
('Spice World', '9876543211', 'sales@spiceworld.com', '456 Spice Lane, Delhi', 'GST234567', 'ACTIVE'),
('Dairy Fresh', '9876543212', 'info@dairyfresh.com', '789 Dairy Road, Pune', 'GST345678', 'ACTIVE');

-- Populate Table 5: mingos_customerorder
INSERT INTO mingos_customerorder (order_datetime, order_type, order_status, payment_mode, total_amount) VALUES
(NOW(), 'DINE_IN', 'SERVED', 'Cash', 500.00),
(NOW() - INTERVAL 1 HOUR, 'TAKEAWAY', 'SERVED', 'Card', 330.00),
(NOW() - INTERVAL 2 HOUR, 'ONLINE', 'PREPARING', 'UPI', 450.00),
(NOW() - INTERVAL 3 HOUR, 'DINE_IN', 'SERVED', 'Cash', 760.00);


-- ====================================================================
-- 4. DATA RETRIEVAL QUERIES (At least 5 queries for your project)
-- ====================================================================

-- Query 1: Get all menu items with their categories and prices
SELECT 
    mc.name AS category_name,
    mi.name AS menu_item,
    mi.price,
    mi.spice_level,
    CASE WHEN mi.is_vegetarian = 1 THEN 'Veg' ELSE 'Non-Veg' END AS type,
    CASE WHEN mi.is_available = 1 THEN 'Available' ELSE 'Not Available' END AS availability
FROM mingos_menuitem mi
LEFT JOIN mingos_menucategory mc ON mi.category_id = mc.category_id
ORDER BY mc.name, mi.price DESC;

-- Query 2: Get ingredients that are running low (below reorder level)
SELECT 
    ingredient_id,
    name,
    current_stock_qty,
    reorder_level,
    unit_of_measure,
    (reorder_level - current_stock_qty) AS shortage_qty,
    CASE WHEN is_perishable = 1 THEN 'Yes' ELSE 'No' END AS perishable
FROM mingos_ingredient
WHERE current_stock_qty < reorder_level
ORDER BY (reorder_level - current_stock_qty) DESC;

-- Query 3: Get recipe details for a specific menu item (e.g., Chicken Biryani)
SELECT 
    mi.name AS dish_name,
    ing.name AS ingredient_name,
    r.quantity_required,
    ing.unit_of_measure,
    ing.current_stock_qty AS available_stock
FROM mingos_recipe r
JOIN mingos_menuitem mi ON r.menu_item_id = mi.menu_item_id
JOIN mingos_ingredient ing ON r.ingredient_id = ing.ingredient_id
WHERE mi.name = 'Chicken Biryani'
ORDER BY r.quantity_required DESC;

-- Query 4: Get sales summary by order type
SELECT 
    order_type,
    COUNT(*) AS total_orders,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_order_value,
    MIN(total_amount) AS min_order,
    MAX(total_amount) AS max_order
FROM mingos_customerorder
WHERE order_status = 'SERVED'
GROUP BY order_type
ORDER BY total_revenue DESC;

-- Query 5: Get top 5 best selling menu items
SELECT 
    mi.name AS menu_item,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.line_amount) AS total_revenue,
    COUNT(DISTINCT oi.customer_order_id) AS number_of_orders,
    AVG(oi.unit_price) AS avg_price
FROM mingos_orderitem oi
JOIN mingos_menuitem mi ON oi.menu_item_id = mi.menu_item_id
GROUP BY mi.menu_item_id, mi.name
ORDER BY total_quantity_sold DESC
LIMIT 5;

-- Query 6 (BONUS): Get supplier details with ingredients they supply
SELECT 
    s.name AS supplier_name,
    s.phone,
    s.email,
    GROUP_CONCAT(i.name SEPARATOR ', ') AS ingredients_supplied
FROM mingos_supplier s
LEFT JOIN mingos_supplieringredient si ON s.supplier_id = si.supplier_id
LEFT JOIN mingos_ingredient i ON si.ingredient_id = i.ingredient_id
WHERE s.status = 'ACTIVE'
GROUP BY s.supplier_id, s.name, s.phone, s.email
ORDER BY s.name;

-- Query 7 (BONUS): Get total inventory value (if you add purchase prices)
SELECT 
    name AS ingredient,
    current_stock_qty AS stock,
    unit_of_measure AS unit,
    CASE WHEN is_perishable = 1 THEN 'Perishable' ELSE 'Non-Perishable' END AS type
FROM mingos_ingredient
ORDER BY current_stock_qty DESC;
