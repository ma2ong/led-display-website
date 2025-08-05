import sqlite3
import os

# Change to admin directory
os.chdir('admin')

# Connect to database
conn = sqlite3.connect('led_admin.db')
cursor = conn.cursor()

# Clear all image references that point to non-existent files
cursor.execute("UPDATE products SET images = '' WHERE images LIKE 'assets/products/%'")

# Set the one product that has an uploaded image
cursor.execute("UPDATE products SET images = 'assets/products/tu_ffee3e21.png' WHERE id = 1")

# Commit changes
conn.commit()
conn.close()

print("Database updated successfully!")
print("All non-existent image references have been cleared.")