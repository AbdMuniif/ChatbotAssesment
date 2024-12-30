import mysql.connector
import fitz   


document = fitz.open("./2023-Double-Funnel.pdf")


text = ""


for page_num in range(document.page_count):
    page = document.load_page(page_num)  
    text += page.get_text("text")  

try:
    print("Connecting to database...")

  
    db_connection = mysql.connector.connect(
        host="database-1.cdwug8moe3tn.us-east-1.rds.amazonaws.com",
        user="admin",
        password="qwert12345",
        database="Database"
    )

    print("Database connected successfully")

   
    cursor = db_connection.cursor()

    cursor.execute("INSERT INTO ocr_text_table (extracted_text) VALUES (%s)", (text,))
    db_connection.commit()  
    print("Text saved to the database")

    
    cursor.execute("SELECT * FROM ocr_text_table ORDER BY timestamp DESC LIMIT 1;")
    result = cursor.fetchone()  

except mysql.connector.Error as err:
   
    print(f"Error with MySQL: {err}")
except Exception as e:
    
    print(f"An error occurred: {e}")
finally:
   
    if cursor:
        cursor.close()
    if db_connection:
        db_connection.close()
