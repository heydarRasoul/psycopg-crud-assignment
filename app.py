from flask import Flask, jsonify, request
from db import create_all_tables
import psycopg2
import os


database_name = os.environ.get('DATABASE_NAME')
app_host = os.environ.get('APP_HOST')
app_port = os.environ.get('APP_PIRT')

conn = psycopg2.connect(f'dbname={database_name}')
cursor = conn.cursor()

app = Flask(__name__)

create_all_tables()

# create============
@app.route('/company', methods=["POST"])
def add_company():
    try:
        post_data = request.form if request.form else request.get_json()
        company_name = post_data.get('company_name')

        if not company_name:
            return jsonify({"message": "company_name is required."}), 400

        cursor.execute(
            """
            INSERT INTO Companies (company_name)
            VALUES (%s)
            RETURNING company_id, company_name
            """,
            (company_name,)
        )

        new_company = cursor.fetchone()
        conn.commit()

        if new_company:
            return jsonify({
                "message": f"{company_name} has been added.",
                "company": {
                    "company_id": new_company[0],
                    "company_name": new_company[1]
                }
            }), 201
        else:
            return jsonify({"message": f"{company_name} already exists."}), 409

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Company cannot be added.", "error": str(e)}), 500

@app.route('/category', methods=['POST'])
def create_category():
    try:
        post_data = request.form if request.form else request.get_json()
        category_name = post_data.get('category_name')

        if not category_name:
            return jsonify({"message": "category_name is a required field."}), 400

        cursor.execute("SELECT * FROM Categories WHERE category_name = %s", (category_name,))
        result = cursor.fetchone()
        if result:
            return jsonify({"message": f"{category_name} already exists."}), 409

        cursor.execute(
            "INSERT INTO Categories (category_name) VALUES (%s) RETURNING category_id, category_name",
            (category_name,)
        )
        new_category = cursor.fetchone()  
        conn.commit()

        category_dict = {
            "category_id": new_category[0],
            "category_name": new_category[1]
        }

        return jsonify({
            "message": f"{category_name} has been added to categories table.",
            "category": category_dict
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Category cannot be added.", "error": str(e)}), 500


@app.route('/product', methods=['POST'])
def add_product():
    try:
        post_data = request.form if request.form else request.get_json()

        product_name = post_data.get('product_name')
        company_id = post_data.get('company_id')
        price = post_data.get('price')
        description = post_data.get('description')
        active = post_data.get('active')

        if not product_name:
            return jsonify({"message": "product_name is a required field"}), 400

        cursor.execute("SELECT * FROM Products WHERE product_name = %s", (product_name,))
        result = cursor.fetchone()
        if result:
            return jsonify({"message": f"The {product_name} already exists."}), 409

        cursor.execute(
            """
            INSERT INTO Products (product_name, company_id, price, description, active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING product_id, company_id, product_name, price, description, active
            """,
            (product_name, company_id, price, description, active)
        )
        new_product = cursor.fetchone()  
        conn.commit()

        product_dict = {
            "product_id": new_product[0],
            "company_id": new_product[1],
            "product_name": new_product[2],
            "price": new_product[3],
            "description": new_product[4],
            "active": new_product[5]
        }

        return jsonify({
            "message": f"{product_name} has been added to products table.",
            "product": product_dict
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Product could not be added.", "error": str(e)}), 500


@app.route('/warranty', methods=['POST'])
def create_warranty():
    try:
        post_data = request.form if request.form else request.get_json()
        warranty_months = post_data.get('warranty_months')
        product_id = post_data.get('product_id')

        if not warranty_months:
            return jsonify({"message": "warranty_months is a required field."}), 400

        cursor.execute(
            """
            INSERT INTO Warranties (warranty_months, product_id)
            VALUES (%s, %s)
            RETURNING warranty_id, product_id, warranty_months
            """,
            (warranty_months, product_id)
        )
        new_warranty = cursor.fetchone() 
        conn.commit()

        warranty_dict = {
            "warranty_id": new_warranty[0],
            "product_id": new_warranty[1],
            "warranty_months": new_warranty[2]
        }

        return jsonify({
            "message": "Warranty has been added to warranties table.",
            "warranty": warranty_dict
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Warranty cannot be added .", "error": str(e)}), 500




@app.route('/product/category', methods=['POST'])
def create_pcx():
    try:
        post_data = request.form if request.form else request.get_json()

        product_id = post_data.get('product_id')
        category_id = post_data.get('category_id')

        if not product_id or not category_id:
            return jsonify({"message": "Both product_id and category_id are required."}), 400

        cursor.execute(
            """
            INSERT INTO ProductsCategoriesXref (product_id, category_id)
            VALUES (%s, %s)
            RETURNING product_id, category_id
            """,
            (product_id, category_id)
        )
        new_pcx = cursor.fetchone() 
        conn.commit()

        pcx_dict = {
            "product_id": new_pcx[0],
            "category_id": new_pcx[1]
        }

        return jsonify({
            "message": "ProductsCategoriesXref has been updated.",
            "pcx": pcx_dict
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({
            "message": "New association between a product and category cannot be added.",
            "error": str(e)
        }), 500

# read ================

@app.route('/companies', methods=['GET'])
def get_all_companies ():
    try:
        cursor.execute(""" 
        SELECT * FROM Companies;
        """)
        results = cursor.fetchall()

        if not results:
            return jsonify({"message":"companies table is empty"}),200

        companies_list =[]
       
        for result in results:
            company ={
                'company_id' : result[0],
                'company_name' : result[1],
            }
            companies_list.append(company)

        return jsonify({"message": "companies found","results": companies_list}),200
    
    except Exception as e:
        return jsonify({"message": "companies cannot be displayed", "error":str(e)}),500
     

@app.route('/categories', methods=['GET'])
def get_all_categories ():
    try:
        cursor.execute(""" 
        SELECT * FROM Categories;
        """)
        results = cursor.fetchall()

        if not results:
            return jsonify({"message":"categories table is empty"}),200

        category_list =[]
       
        for result in results:
            category ={
                'category_id': result[0],
                'category_name' : result[1]
            }
            category_list.append(category)

        return jsonify({"message": "categories found","results": category_list}),200
    
    except Exception as e:
        return jsonify({"message": "categories cant be display", "error":str(e)}),500
        

@app.route('/products', methods=['GET'])
def get_all_products():
    try:
        cursor.execute("""
            SELECT 
                p.product_id,
                p.product_name,
                p.price,
                p.description,
                p.active,
                w.warranty_months,
                c.category_id,
                c.category_name
            FROM Products p
            LEFT JOIN Warranties w ON p.product_id = w.product_id
            LEFT JOIN ProductsCategoriesXref pcx ON p.product_id = pcx.product_id
            LEFT JOIN Categories c ON pcx.category_id = c.category_id;
        """)
        results = cursor.fetchall()

        if not results:
            return jsonify({"message": "products table is empty"}), 200

        product_dict = {}
        for row in results:
            product_id = row[0]
            if product_id not in product_dict:
                product_dict[product_id] = {
                    "product_id": row[0],
                    "product_name": row[1],
                    "price": row[2],
                    "description": row[3],
                    "active": row[4],
                    "warranty_months": row[5],
                    "categories": []
                }

            if row[6] and row[7]:
                category = {
                    "category_id": row[6],
                    "category_name": row[7]
                }
                if category not in product_dict[product_id]["categories"]:
                    product_dict[product_id]["categories"].append(category)

        product_list = list(product_dict.values())

        return jsonify({"message": "products found", "results": product_list}), 200

    except Exception as e:
        return jsonify({"message": "products can't be displayed", "error": str(e)}), 500



@app.route('/products/active', methods=['GET'])
def get_active_products ():
    try:
        cursor.execute(""" 
        SELECT * FROM Products WHERE active =TRUE;
        """)
        results = cursor.fetchall()

        if not results:
            return jsonify({"message":"no active products found", "results":[]}),402

        product_list =[]
       
        for result in results:
            product ={
                'product_id' : result[0],
                'company_id' : result[1],
                'product_name' : result[2],
                'price': result[3],
                'description' : result[4],
                'active':result[5]
            }
            product_list.append(product)

        return jsonify({"message": "active products found","results": product_list}),200
    
    except Exception as e:
        return jsonify({"message": "active products cannot be displayed", "error":str(e)}),500
        


@app.route('/company/<company_id>', methods=['GET'])
def get_company_by_id (company_id):
    try:
        cursor.execute(""" 
        SELECT * FROM Companies WHERE company_id=%s
        """,(company_id,)
        )
        result = cursor.fetchone()

        if not result:
            return jsonify({"message":"company does not exist"}),404

        company = {
            "company_id": result[0],
            "company_name": result[1]
        }

        return jsonify({"message": "company found","result": company}),200
    
    except Exception as e:
        return jsonify({"message": "company cannot be displayed", "error": str(e)}),500
     

@app.route('/category/<category_id>', methods=['GET'])
def get_category_by_id(category_id):
    try:
        cursor.execute(""" 
        SELECT * FROM Categories WHERE category_id = %s
        """, (category_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "category does not exist"}), 404

        category = {
            "category_id": result[0],
            "category_name": result[1]
        }

        return jsonify({"message": "category found", "results": category}), 200
    
    except Exception as e:
        return jsonify({"message": "category cannot be displayed", "error": str(e)}), 500


@app.route('/product/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    try:
        cursor.execute("""
            SELECT 
                p.product_id,
                p.product_name,
                p.price,
                p.description,
                p.active,
                c.category_id,
                c.category_name
            FROM Products p
            LEFT JOIN ProductsCategoriesXref pcx ON p.product_id = pcx.product_id
            LEFT JOIN Categories c ON pcx.category_id = c.category_id
            WHERE p.product_id = %s;
        """, [product_id])

        results = cursor.fetchall()  

        if not results:
            return jsonify({"message": "product does not exist", "result": {}}), 404

        product = {
            "product_id": results[0][0],
            "product_name": results[0][1],
            "price": results[0][2],
            "description": results[0][3],
            "active": results[0][4],
            "categories": []
        }

        for row in results:
            if row[5] and row[6]: 
                category = {
                    "category_id": row[5],
                    "category_name": row[6]
                }
                if category not in product["categories"]:
                    product["categories"].append(category)

        return jsonify({"message": "product retrieved successfully", "result": product}), 200

    except Exception as e:
        return jsonify({"message": "product cannot be displayed", "error": str(e)}), 500


@app.route('/warranty/<warranty_id>', methods=['GET'])
def get_warranty_by_id(warranty_id):
    try:
        cursor.execute(""" 
        SELECT * FROM Warranties WHERE warranty_id = %s
        """, [warranty_id])
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "warranty does not exist"}), 404

        warranty = {
            "warranty_id": result[0],
            "product_id": result[1],
            "warranty_months": result[2]
        }

        return jsonify({"message": "warranty found", "results": warranty}), 200
    
    except Exception as e:
        return jsonify({"message": "warranty cannot be displayed", "error": str(e)}), 500


@app.route('/product/company/<company_id>', methods=['GET'])
def get_products_by_company (company_id):
    try:
        cursor.execute(""" 
        SELECT Products.*, Companies.company_name
        FROM Products
        JOIN Companies
        ON Products.company_id = Companies.company_id
        WHERE Companies.company_id=%s
        """,[company_id])
        results = cursor.fetchall()

        if not results:
            return jsonify({"message":"no products found for this company"}),200

        product_list =[]
       
        for result in results:
            product ={
                'product_id' : result[0],
                'company_id' : result[1],
                'product_name' : result[2],
                'price': result[3],
                'description' : result[4],
                'active':result[5],
                "company_name": result[6]
            }
            product_list.append(product)

        return jsonify({"message": "products found","results": product_list}),200
    
    except Exception as e:
        return jsonify({"message": "products cannot be displayed", "error":str(e)}),500
        

# UPDATE==============

@app.route('/company/<company_id>', methods=['PUT'])
def update_company_by_id (company_id):
    try:
        data = request.form if request.form else request.get_json()

        company_name = data.get('company_name')

        if not company_name:
            return jsonify({"message": "company_name is required"}), 400

        cursor.execute(""" 
        UPDATE Companies SET company_name =%s WHERE company_id = %s RETURNING *
        """,[company_name, company_id])

        updated = cursor.fetchone()
        if not updated:
            return jsonify({"message": "company not found"}), 404

        conn.commit()
        return jsonify({"message": "company updated successfully", "results": {
            "company_id": updated[0],
            "company_name": updated[1]
        }}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "company cannot be updated", "error": str(e)}), 500


@app.route('/category/<category_id>', methods=['PUT'])
def update_category_by_id(category_id):
    try:
        data = request.form if request.form else request.get_json()
        category_name = data.get('category_name')

        if not category_name:
            return jsonify({"message": "category_name is required"}), 400

        cursor.execute("""
            UPDATE Categories
            SET category_name = %s
            WHERE category_id = %s
            RETURNING *;
        """, [category_name, category_id])

        updated = cursor.fetchone()
        if not updated:
            return jsonify({"message": "category not found"}), 404

        conn.commit()
        return jsonify({"message": "category updated successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "category cannot be updated", "error": str(e)}), 500


@app.route('/product/<product_id>', methods=['PUT'])
def update_product_by_id(product_id):
    try:
        data = request.form if request.form else request.get_json()

        product_name = data.get('product_name')
        company_id = data.get('company_id')
        price = data.get('price')
        description = data.get('description')
        active = data.get('active')

        fields = []
        values = []

        if product_name is not None:
            fields.append("product_name = %s")
            values.append(product_name)
        if company_id is not None:
            fields.append("company_id = %s")
            values.append(company_id)
        if price is not None:
            fields.append("price = %s")
            values.append(price)
        if description is not None:
            fields.append("description = %s")
            values.append(description)
        if active is not None:
            fields.append("active = %s")
            values.append(active)

        if not fields:
            return jsonify({"message": "no fields to update"}), 400

        values.append(product_id)

        sql = f"UPDATE Products SET {', '.join(fields)} WHERE product_id = %s RETURNING *;"
        cursor.execute(sql, values)
        updated = cursor.fetchone()

        if not updated:
            return jsonify({"message": "product not found"}), 404

        conn.commit()

        product = {
            "product_id": updated[0],
            "company_id": updated[1],
            "product_name": updated[2],
            "price": updated[3],
            "description": updated[4],
            "active": updated[5]
        }

        return jsonify({"message": "product updated successfully", "results": product}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "product cannot be updated", "error": str(e)}), 500


@app.route('/warranty/<warranty_id>', methods=['PUT'])
def update_warranty_by_id(warranty_id):
    try:
        data = request.form if request.form else request.get_json()

        product_id = data.get('product_id')
        warranty_months = data.get('warranty_months')

        fields = []
        values = []

        if product_id is not None:
            fields.append("product_id = %s")
            values.append(product_id)
        if warranty_months is not None:
            fields.append("warranty_months = %s")
            values.append(warranty_months)

        if not fields:
            return jsonify({"message": "no fields to update"}), 400

        values.append(warranty_id)

        sql = f"UPDATE Warranties SET {', '.join(fields)} WHERE warranty_id = %s RETURNING *;"
        cursor.execute(sql, values)
        updated = cursor.fetchone()

        if not updated:
            return jsonify({"message": "warranty not found"}), 404

        conn.commit()

        warranty = {
            "warranty_id": updated[0],
            "product_id": updated[1],
            "warranty_months": updated[2]
        }

        return jsonify({"message": "warranty updated successfully", "results": warranty}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "warranty cannot be updated", "error": str(e)}), 500


# DELETE===============

@app.route('/company/delete/<company_id>', methods=['DELETE'])
def delete_company(company_id):
    try:
        cursor.execute("""
            DELETE FROM Companies
            WHERE company_id = %s;
        """, [company_id])

        if cursor.rowcount == 0:
            return jsonify({"message": "company not found"}), 404

        conn.commit()
        return jsonify({"message": "company and all related products deleted successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "company cannot be deleted", "error": str(e)}), 500


@app.route('/product/delete/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        cursor.execute("""
        DELETE FROM Products
        WHERE product_id = %s;
        """,[product_id])

        if cursor.rowcount == 0:
            return jsonify({"message": "product not found"}), 404

        conn.commit()
        return jsonify({"message": "product and all related warranty records deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": "product cannot be deleted", "error": str(e)}), 500


@app.route('/category/delete/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        cursor.execute("""
            DELETE FROM Categories
            WHERE category_id = %s;
        """, [category_id])

        if cursor.rowcount == 0:
            return jsonify({"message": "category not found"}), 404

        conn.commit()
        return jsonify({"message": "category and all related xref records deleted successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "category cannot be deleted", "error": str(e)}), 500


@app.route('/warranty/delete/<warranty_id>', methods=['DELETE'])
def delete_warranty(warranty_id):
    try:
        cursor.execute("""
            DELETE FROM Warranties
            WHERE warranty_id = %s;
        """, [warranty_id])

        if cursor.rowcount == 0:
            return jsonify({"message": "warranty not found"}), 404

        conn.commit()
        return jsonify({"message": "warranty deleted successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "warranty cannot be deleted", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host = app_host, port = app_port)