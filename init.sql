-- Database initialization script for Vanna AI Web Application
-- This script creates sample tables and data for testing

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(100),
    salary DECIMAL(10, 2),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sales table
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    sale_date DATE NOT NULL,
    customer_id INTEGER,
    employee_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data into users table
INSERT INTO users (username, email) VALUES
    ('john_doe', 'john.doe@example.com'),
    ('jane_smith', 'jane.smith@example.com'),
    ('bob_wilson', 'bob.wilson@example.com'),
    ('alice_brown', 'alice.brown@example.com'),
    ('charlie_davis', 'charlie.davis@example.com')
ON CONFLICT (username) DO NOTHING;

-- Insert sample data into employees table
INSERT INTO employees (first_name, last_name, email, department, salary, hire_date) VALUES
    ('John', 'Doe', 'john.doe@company.com', 'Engineering', 75000.00, '2022-01-15'),
    ('Jane', 'Smith', 'jane.smith@company.com', 'Marketing', 65000.00, '2022-02-20'),
    ('Bob', 'Wilson', 'bob.wilson@company.com', 'Sales', 70000.00, '2021-11-10'),
    ('Alice', 'Brown', 'alice.brown@company.com', 'Engineering', 80000.00, '2021-08-05'),
    ('Charlie', 'Davis', 'charlie.davis@company.com', 'HR', 60000.00, '2022-03-01')
ON CONFLICT (email) DO NOTHING;

-- Insert sample data into sales table
INSERT INTO sales (product_name, amount, sale_date, customer_id, employee_id) VALUES
    ('Laptop', 1200.00, '2024-01-15', 1, 3),
    ('Mouse', 25.00, '2024-01-16', 2, 3),
    ('Keyboard', 80.00, '2024-01-17', 3, 3),
    ('Monitor', 300.00, '2024-01-18', 1, 3),
    ('Headphones', 150.00, '2024-01-19', 4, 3)
ON CONFLICT DO NOTHING;

-- Insert sample data into orders table
INSERT INTO orders (customer_name, total_amount, status) VALUES
    ('Acme Corp', 1500.00, 'completed'),
    ('Tech Solutions', 800.00, 'processing'),
    ('Global Industries', 2200.00, 'pending'),
    ('Startup Inc', 450.00, 'completed'),
    ('Enterprise Ltd', 3200.00, 'processing')
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_salary ON employees(salary);
CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_amount ON sales(amount);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vanna_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vanna_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO vanna_user;
