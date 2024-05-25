import sqlite3
import streamlit as st

# Initialize the SQLite database
conn = sqlite3.connect('fridge.db')
c = conn.cursor()

# Create a table for products if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )
''')
conn.commit()

# Function to add a product to the database
def add_product(name, quantity):
    c.execute('INSERT INTO products (name, quantity) VALUES (?, ?)', (name, quantity))
    conn.commit()

# Function to get all products from the database
def get_all_products():
    c.execute('SELECT * FROM products')
    return c.fetchall()

# Function to update a product's name or quantity
def update_product(product_id, name, quantity):
    c.execute('UPDATE products SET name = ?, quantity = ? WHERE id = ?', (name, quantity, product_id))
    conn.commit()

# Function to delete a product from the database
def delete_product(product_id):
    c.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()

# Streamlit UI
st.title("Fridge Inventory")

# Input form to add a new product
with st.form(key='add_product_form'):
    name = st.text_input("Product Name")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    add_button = st.form_submit_button("Add Product")

    if add_button:
        if name:
            add_product(name, quantity)
            st.success(f"Added {name} ({quantity}) to the fridge.")
        else:
            st.error("Please enter a product name.")

# Display all products
products = get_all_products()

st.subheader("Products in the Fridge")
for product in products:
    st.write(f"{product[0]}. {product[1]} - {product[2]}")

    # Edit form for each product
    with st.form(key=f'edit_form_{product[0]}'):
        new_name = st.text_input("New Name", value=product[1])
        new_quantity = st.number_input("New Quantity", min_value=1, step=1, value=product[2])
        update_button = st.form_submit_button("Update")

        if update_button:
            update_product(product[0], new_name, new_quantity)
            st.success(f"Updated product {product[0]}.")

    # Button to delete the product
    if st.button(f"Delete {product[1]}", key=f'delete_button_{product[0]}'):
        delete_product(product[0])
        st.success(f"Deleted product {product[1]}.")

# Close the database connection
conn.close()
