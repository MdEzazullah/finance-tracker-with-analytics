-- ============================================
-- Personal Finance Tracker - Database Schema
-- ============================================

-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS finance_tracker;
USE finance_tracker;

-- Step 2: Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    type ENUM('income', 'expense') NOT NULL
);

-- Step 4: Transactions table (linked to users and categories)
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    date DATE NOT NULL,
    description VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Step 5: Budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    monthly_limit DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Step 6: Starter categories (so the app has data to work with immediately)
INSERT INTO categories (name, type) VALUES
('Salary', 'income'),
('Freelance', 'income'),
('Food', 'expense'),
('Rent', 'expense'),
('Transport', 'expense'),
('Entertainment', 'expense'),
('Utilities', 'expense');

-- Step 7: Verify (optional - run manually to check)
-- SHOW TABLES;
-- DESCRIBE transactions;