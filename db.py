from flask import Blueprint

import psycopg2
import os


database_name = os.environ.get('DATABASE_NAME')
app_host = os.environ.get('APP_HOST')
app_port = os.environ.get('APP_PORT')

conn = psycopg2.connect(f'dbname={database_name}')
cursor = conn.cursor()

def create_all_tables():
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS Companies(
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Products (
    product_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id) ON DELETE CASCADE,
    product_name VARCHAR UNIQUE NOT NULL,
    price INT,
    description VARCHAR,
    active BOOLEAN DEFAULT TRUE
    );

    CREATE TABLE IF NOT EXISTS Categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR UNIQUE NOT NULL 
    );

    CREATE TABLE IF NOT EXISTS Warranties (
    warranty_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    warranty_months VARCHAR NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ProductsCategoriesXref (
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    category_id INT REFERENCES categories(category_id) ON DELETE CASCADE
    )

    """)

    conn.commit()


