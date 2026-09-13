-- 1. Staff table
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- 2. Menu items
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price NUMERIC(6, 2) NOT NULL CHECK (price >= 0),
    active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. Ingredients (stock cannot go negative)
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    stock_quantity NUMERIC(10, 2) NOT NULL CHECK (stock_quantity >= 0),
    reorder_threshold NUMERIC(10, 2) NOT NULL CHECK (reorder_threshold >= 0)
);

-- 4. Recipes (Associative table: menu_items <-> ingredients)
CREATE TABLE recipes (
    menu_item_id INT NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
    ingredient_id INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity_required NUMERIC(10, 2) NOT NULL CHECK (quantity_required > 0),
    PRIMARY KEY (menu_item_id, ingredient_id)
);

-- 5. Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    staff_id INT NOT NULL REFERENCES staff(id),
    order_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'completed'
);

-- 6. Order items (Associative table: orders <-> menu_items)
CREATE TABLE order_items (
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INT NOT NULL REFERENCES menu_items(id),
    quantity INT NOT NULL CHECK (quantity > 0),
    subtotal NUMERIC(8, 2) NOT NULL CHECK (subtotal >= 0),
    PRIMARY KEY (order_id, menu_item_id)
);

-- Seed Data
INSERT INTO staff (name, role, email) VALUES
('Baha Eddine', 'Cashier', 'baha@counterstock.local'),
('Shift Lead', 'Manager', 'lead@counterstock.local');

INSERT INTO ingredients (id, name, unit, stock_quantity, reorder_threshold) VALUES
(1, 'Burger Bun', 'pcs', 30.00, 10.00),
(2, 'Beef Patty', 'pcs', 25.00, 10.00),
(3, 'Cheddar Slice', 'pcs', 20.00, 5.00),
(4, 'Bratwurst Sausage', 'pcs', 15.00, 5.00),
(5, 'French Fries (Frozen)', 'g', 5000.00, 1000.00),
(6, 'Cola 0.33l', 'can', 40.00, 12.00);

ALTER SEQUENCE ingredients_id_seq RESTART WITH 7;

INSERT INTO menu_items (id, name, category, price, active) VALUES
(1, 'Cheeseburger', 'Burger', 5.50, TRUE),
(2, 'Bratwurst', 'Grill', 3.50, TRUE),
(3, 'Pommes', 'Sides', 2.50, TRUE),
(4, 'Cola 0.33l', 'Drinks', 2.00, TRUE);

ALTER SEQUENCE menu_items_id_seq RESTART WITH 5;

-- Recipes linking menu items to ingredients
INSERT INTO recipes (menu_item_id, ingredient_id, quantity_required) VALUES
(1, 1, 1.00),     -- Cheeseburger: 1 Bun
(1, 2, 1.00),     -- Cheeseburger: 1 Patty
(1, 3, 1.00),     -- Cheeseburger: 1 Cheddar
(2, 4, 1.00),     -- Bratwurst: 1 Sausage
(3, 5, 200.00),   -- Pommes: 200g Fries
(4, 6, 1.00);     -- Cola: 1 Can
