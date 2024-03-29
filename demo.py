import mysql.connector
import pandas as pd
import streamlit as st
from langchain import OpenAI, LLMChain
from langchain.prompts import load_prompt

# Define function to execute MySQL query
def execute_mysql_query(sql):
    connection_params = {
        'user': 'sql6690576',
        'password': 'cmiie8J5uu',
        'host': 'sql6.freesqldatabase.com',
        'database': 'sql6690576',
        'port': 3306,
    }

    try:
        print("Executing SQL query:", sql)
        conn = mysql.connector.connect(**connection_params)
        cur = conn.cursor()
        cur.execute(sql)
        query_results = cur.fetchall()
        column_names = [col[0] for col in cur.description]
        data_frame = pd.DataFrame(query_results, columns=column_names)
        return data_frame

    except mysql.connector.Error as e:
        print("MySQL Error:", e)
        return None

    finally:
        try:
            cur.close()
        except:
            pass

        try:
            conn.close()
        except:
            pass

# Streamlit setup
st.title("AI SQL Assistant")
user_input = st.text_input("Enter your query")
tab_titles = ["Result", "Query"]
tabs = st.tabs(tab_titles)




# Load OpenAI API key from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Load prompt template
prompt_template = load_prompt('tpch_prompt.yaml')


llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, openai_api_key=OPENAI_API_KEY)
sql_generation_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)

# Main functionality
if user_input:
    sql_query = sql_generation_chain(user_input)
    if 'text' in sql_query:
        generated_sql = sql_query['text']
        with tabs[1]:
            st.write("Generated SQL Query:")
            st.code(generated_sql)

        try:
            if st.button("Execute Query"):
                result = execute_mysql_query(generated_sql)
                if result is not None:
                    with tabs[0]:
                        st.write("Execution Result:")
                        st.write(result)
                else:
                    with tabs[0]:
                        st.write("No result returned from the database.")
        except Exception as e:
            with tabs[0]:
                st.write(f"Error executing SQL query: {e}")
