from flask import flask, jsonify, request
from db import create_tables
import os


database_name = os.environ.get('DATABASE_NAME')
app_host = os.environ.get('APP_HOST')
app_port = os.environ.get('APP_PIRT')

conn = psycopg2.connection(f'dbname={database_name}')
cursor = conn.cursor()

app = Flask(__name__)

create_tables()

# create============

@app.route('/product', methods=['POST'])
def add_product ():
    post_data = request.form if request.form else request.get_json()

    product_name = post_data.get('product_name')
    company_id = post_data.get('company_id')
    price = post_data.get('price')
    description = post_data.get('description')
    active = post_data.get('active')

    if not product_name:
        return jsonify({"message": "product_name is a requiered field"}), 400

    result = cursor.execute(""" 
     SELECT * FROM Products WHERE product_name = %s 
    """, [product_name])
    result = cursor.fetchone()

    if result:
        return jsonify({"message": f"The {product_name} is already exists."}), 400

    try:

        cursor.execute(""" 
            INSERT INTO Products (product_name, company_id, price, description, active)
            VALUES (%s, %s ,%s, %s,%s)
        """,(product_name, company_id, price, description, active) )
        conn.commit()

    except:
        cursor.rollback()
        return jsonify ({"message": "Product could not be added."}),400

    return ({"messege": f'{product_name} has been added to products table.'}), 201


@app.route('/company', methods=["POST"])
def add_company ():
    post_data = request.form if request.form else request.get_json()

    company_name = post_data.get('company_name')

    if not company_name:
        return jsonify({"message": "coompany_name is required."})

    result = cursor.execute("""
        SELECT * FROM Companies WHERE company_name = %s
     """,[company_name])

    result = cursor.fetchone()

    if result:
        return jsonify({"message":f"{Company_name} is already exists."})

    try:
        cursor.execute(""" 
            INSERT INTO Companies (company_name)
            VALUES (%s)
        """,(company_name) )
        conn.commit()

    except:
        cursor.rollback()
        return jsonify({"message":"Company can not be added."})

    return jsonify({"messege": f'{company_name} has been added to companies table.'}),201


@app.route('/warranty', methods=['POST'])
def create_warranty ():
    post_data = request.form if request.form else request.get_json()

    warranty_months = post_data.get('warranty_months')
    product_id = post_data.get('product_id')

    if not product_months:
        return jsonify({"message":"warranty_months id a required field."}),400

    try:
        cursor.execute(""" 
            INSERT INTO Warranties (warranty_months, product_id)
            VALUES (%s, %s)
        """,(warranty_months, product_id) )
        conn.commit()

    except:
        cursor.rollback()
        return jsonify({"message":"Warranty can not be added."}),400

    return ({"messege": f 'Warranty has been added to warranties table.'}),201
    

@app.route('/category', methods=['POST'])
def create_category ():
    post_data = request.form if request.form else request.get_json()

    category_name = post_data.get('category_name')

    if not category_name:
        return jsonify({"message": "Category name is a required field."}),400

    result = cursor.execute(""" 
        SELECT * FROM Categories WHERE category_name=%s
    """,[category_name])

    result = cursor.fetchone()

    if result:
        return jsonify({"message": f"{category_name} is already exists."}),400

    try:
        cursor.execute(""" 
            INSERT INTO Categories (category_name)
            VALUES (%s)
        """,(category_name) )
        conn.commit()

    except:
        cursor.rollback()
        return jsonify({"message": "Category cant be added."}),400    
    return jsonify({"messege": f '{category_name} has been added to categories table.'}),201


@app.route('/product/category', methods=['POST'])
def create_pcx ():
    post_data = request.form if request.form else request.get_json()

    product_id = post_data.get('product_id')
    category_id = post_data.get('category_id')

    try:
        cursor.execute(""" 
            INSERT INTO ProductsCategoriesXref (product_id, category_id)
            VALUES (%s, %s)
        """,(product_id, category_id) )
        conn.commit()

    except:
         cursor.rollback()
        return jsonify({"message": "New association between a product and category cant be added."}),400
    return ({"messege": f' ProductsCategoriesXref has been updated.'}),201

# read ================

@app.route('/companies', methods=['GET'])
def get_all_companies ():
    try:
        cursor.execute(""" 
        SELECT * FROM Companies;
        """)
        results = cursor.fetchall()

        if not results:
            return jsonify({"message":"Companies table is empty"}),404

        companies_list =[]
       
        for result in results:
            company ={
                'company_id' : result[0],
                'company_name' : result[1],
            }
            companies_list.append(company)

        return jsonify({"message": "Companies found","results": companies_list}),200
    
    except Exception as e:
        return jsonify({"message": "Companies cannot be displayed", "error":str(e)}),500
     


@app.route('/products', methods=['GET'])
def get_all_products ():
    try:
        cursor.execute(""" 
        SELECT * FROM Products;
        """)
        results = cursor.fetchall()

        if not results:
            return jsonify({"message":"Products table is empty"}),404

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

        return jsonify({"messsage": "products found","results": product_list}),200
    
    except Exception as e:
        return jsonify({"message": "Products cant be display", "error":str(e)}),500
        

@app.route('/categories', methods=['GET'])
def get_all_categories ():
    try:
        cursor.execute(""" 
        SELECT * FROM Categories;
        """)
        results = cursor.fetchall()

        if not results:
            return jsonify({"message":"Categories table is empty"}),400

        category_list =[]
       
        for result in results:
            category ={
                'category_id': result[0],
                'category_name' : result[1]
            }
            category_list.append(category)

        return jsonify({"message": "category found","results": category_list}),200
    
    except Exception as e:
        return jsonify({"message": "Categories cant be display", "error":str(e)}),500
        

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
            return jsonify({"message": "Products table is empty"}), 400

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
        return jsonify({"message": "Products can't be displayed", "error": str(e)}), 500



@app.route('/products/active', methods=['GET'])
def get_active_products ():
    try:
        cursor.execute(""" 
        SELECT * FROM Products WHERE active =%s;
        """,[bool(active)])
        results = cursor.fetchall()

        if not results:
            return jsonify({"message":"No active products found"}),404

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

        return jsonify({"message": "Active products found","results": product_list}),200
    
    except Exception as e:
        return jsonify({"message": "Active products cannot be displayed", "error":str(e)}),500
        


@app.route('/company/<company_id>', methods=['GET'])
def get_company_by_id (company_id):
    try:
        cursor.execute(""" 
        SELECT * FROM Companies WHERE company_id=%s
        """,[company_id])
        result = cursor.fetchone()

        if not result:
            return jsonify({"message":"Company does not exist"}),404

        return jsonify({"message": "Company found","result": result}),200
    
    except Exception as e:
        return jsonify({"message": "Company cannot be displayed", "error":str(e)}),500
     

@app.route('/category/<category_id>', methods=['GET'])
def get_category_by_id(category_id):
    try:
        cursor.execute(""" 
        SELECT * FROM Categories WHERE category_id = %s
        """, [category_id])
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "Category does not exist"}), 404

        category = {
            "category_id": result[0],
            "category_name": result[1]
        }

        return jsonify({"message": "Category found", "results": category}), 200
    
    except Exception as e:
        return jsonify({"message": "Category cannot be displayed", "error": str(e)}), 500


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

        results = cursor.fetchone()

        if not results:
            return jsonify({"message": "Product does not exist"}), 404

      
        product = {
            "product_id": results[0][0],
            "product_name": results[0][1],
            "price": results[0][2],
            "description": results[0][3],
            "active": results[0][4],
            "categories": []
        }

        for row in results:
            if row[6] and row[7]:
                category = {
                    "category_id": row[6],
                    "category_name": row[7]
                }
                if category not in product["categories"]:
                    product["categories"].append(category)

        return jsonify({"message": "Product found", "results": product}), 200

    except Exception as e:
        return jsonify({"message": "Product cannot be displayed", "error": str(e)}), 500


@app.route('/warranty/<warranty_id>', methods=['GET'])
def get_warranty_by_id(warranty_id):
    try:
        cursor.execute(""" 
        SELECT * FROM Warranties WHERE warranty_id = %s
        """, [warranty_id])
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "Warranty does not exist"}), 404

        warranty = {
            "warranty_id": result[0],
            "product_id": result[1],
            "warranty_months": result[2]
        }

        return jsonify({"message": "Warranty found", "results": Warranty}), 200
    
    except Exception as e:
        return jsonify({"message": "Warranty cannot be displayed", "error": str(e)}), 500


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
            return jsonify({"message":"No products found for this company"}),404

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

        return jsonify({"message": "Products found","results": product_list}),200
    
    except Exception as e:
        return jsonify({"message": "Products cannot be displayed", "error":str(e)}),500
        

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
            return jsonify({"message": "Company not found"}), 404

        conn.commit()
        return jsonify({"message": "Company updated successfully", "results": {
            "company_id": updated[0],
            "company_name": updated[1]
        }}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Company cannot be updated", "error": str(e)}), 500


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
            return jsonify({"message": "Category not found"}), 404

        conn.commit()
        return jsonify({"message": "Category updated successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Category cannot be updated", "error": str(e)}), 500


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
            return jsonify({"message": "No fields to update"}), 400

        values.append(product_id)

        sql = f"UPDATE Products SET {', '.join(fields)} WHERE product_id = %s RETURNING *;"
        cursor.execute(sql, values)
        updated = cursor.fetchone()

        if not updated:
            return jsonify({"message": "Product not found"}), 404

        conn.commit()

        product = {
            "product_id": updated[0],
            "company_id": updated[1],
            "product_name": updated[2],
            "price": updated[3],
            "description": updated[4],
            "active": updated[5]
        }

        return jsonify({"message": "Product updated successfully", "results": product}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Product cannot be updated", "error": str(e)}), 500


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
            return jsonify({"message": "No fields to update"}), 400

        values.append(warranty_id)

        sql = f"UPDATE Warranties SET {', '.join(fields)} WHERE warranty_id = %s RETURNING *;"
        cursor.execute(sql, values)
        updated = cursor.fetchone()

        if not updated:
            return jsonify({"message": "Warranty not found"}), 404

        conn.commit()

        warranty = {
            "warranty_id": updated[0],
            "product_id": updated[1],
            "warranty_months": updated[2]
        }

        return jsonify({"message": "Warranty updated successfully", "results": warranty}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Warranty cannot be updated", "error": str(e)}), 500


# DELETE===============

@app.route('/company/delete/<company_id>', methods=['DELETE'])
def delete_company(company_id):
    try:
        cursor.execute("""
            DELETE FROM Companies
            WHERE company_id = %s;
        """, [company_id])

        if cursor.rowcount == 0:
            return jsonify({"message": "Company not found"}), 404

        conn.commit()
        return jsonify({"message": "Company and all related products deleted successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Company cannot be deleted", "error": str(e)}), 500


@app.route('/product/delete/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        cursor.execute("""
        DELETE FROM Products
        WHERE product_id = %s;
        """,[product_id])

        if cursor.rowcount == 0:
            return jsonify({"message": "Product not found"}), 404

        conn.commit()
        return jsonify({"message": "Product and all related warranty records deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Product cannot be deleted", "error": str(e)}), 500


@app.route('/category/delete/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        cursor.execute("""
            DELETE FROM Categories
            WHERE category_id = %s;
        """, [category_id])

        if cursor.rowcount == 0:
            return jsonify({"message": "Category not found"}), 404

        conn.commit()
        return jsonify({"message": "Category and all related xref records deleted successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Category cannot be deleted", "error": str(e)}), 500


@app.route('/warranty/delete/<warranty_id>', methods=['DELETE'])
def delete_warranty(warranty_id):
    try:
        cursor.execute("""
            DELETE FROM Warranties
            WHERE warranty_id = %s;
        """, [warranty_id])

        if cursor.rowcount == 0:
            return jsonify({"message": "Warranty not found"}), 404

        conn.commit()
        return jsonify({"message": "Warranty deleted successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Warranty cannot be deleted", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host = app_host, port = app_port)