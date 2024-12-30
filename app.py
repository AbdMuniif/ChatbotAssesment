import mysql.connector
import streamlit as st
from langchain_community.llms import LlamaCpp
import re



def fetch_text_from_db():
    db_connection = None  
    cursor = None  
    try:
       
        db_connection = mysql.connector.connect(
            host="database-1.cdwug8moe3tn.us-east-1.rds.amazonaws.com",
            user="admin",
            password="qwert12345",
            database="Database"
        )

        cursor = db_connection.cursor()
        
        cursor.execute("SELECT extracted_text FROM ocr_text_table ORDER BY timestamp DESC LIMIT 1;")
        result = cursor.fetchone()

        
        if result:
            return result[0]
        else:
            print("No text found in the database.")
            return None
        
    except mysql.connector.Error as err:
        print(f"Error with MySQL: {err}")
        return None
    finally:
        
        if cursor is not None:
            cursor.close()
        if db_connection is not None:
            db_connection.close()


def preprocess_text(extracted_text, chunk_size=512):
    
    cleaned_text = re.sub(r'\s+', '', extracted_text).strip()
    cleaned_text = re.sub(r'[^\x00-\x7f]+', '', cleaned_text)
    cleaned_text = cleaned_text.lower()

    
    words = cleaned_text.split()
    chunks = [
        ''.join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]
    return chunks


def llama2_response(extracted_text, user_query):
    model_path = r"./Model/Llama-3.2.gguf"

    llama_llm = LlamaCpp(model_path=model_path, verbose=True, n_ctx=9999)

    # Define a structured prompt template
    prompt_template = """
    You are an intelligent assistant tasked with providing accurate answers strictly based on the context provided below. 
    Your role is to:
    1. Understand the given context thoroughly.
    2. Respond to the user's question clearly and concisely, without including any information outside the provided context.
    3. Avoid making assumptions or adding unnecessary details beyond what is explicitly stated in the context.

    Context: {context}

    Question: {question}

Answer:

    """

    chunks = preprocess_text(extracted_text)
    responses = []

    for chunk in chunks:
        prompt = prompt_template.format(context=chunk, question=user_query)
        response = llama_llm.predict(prompt)
        responses.append(response)

    # Combine the responses from all chunks
    full_response = ' '.join(responses)
    return full_response.strip()


st.title("OCR Chatbot with Llama2 Model")

# Fetch the extracted text from the database
extracted_text = fetch_text_from_db()

# Input field for the user's query
user_query = st.text_input("Ask any question based on the 2023-Double-Funnel.pdf:")

if st.button("Get response"):
    if user_query.strip():
        st.subheader("Chatbot Response")
        response = llama2_response(extracted_text, user_query)
        st.write(response)
    else:
        st.error("Please enter a valid query.")
