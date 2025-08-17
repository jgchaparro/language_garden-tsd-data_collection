import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, insert

# Function to write data to the database
def add_to_database(tsd, ell):
    try:
        # Establish connection using Streamlit's connection
        conn = st.connection("neon_db", type="sql")

        # Define table metadata if not already defined globally or in a separate module
        # It's good practice to define your table schemas once.
        metadata = MetaData()
        dictionary_contributions = Table(
            "dictionary_contributions",
            metadata,
            Column("id", primary_key=True), # Assuming an auto-incrementing ID column
            Column("tsd", String),
            Column("ell", String),
        )

        # Create the insert statement
        stmt = insert(dictionary_contributions).values(tsd=tsd, ell=ell)

        # Execute the insert statement
        # Streamlit's connection object might not directly expose .execute() in the same way
        # as a raw SQLAlchemy engine connection. We'll use conn.session.execute()
        # assuming `st.connection` provides a session-like object.
        # If not, you might need to get the raw engine and then create a connection from it.
        with conn.session as session:
            session.execute(stmt)
            session.commit() # Commit the transaction

        st.success("Record added successfully! 🎉")
        st.write("Debug: Insert statement executed.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Debug: Exception details:", e)

# --- Streamlit App Layout ---
st.title("Tsakonian Dictionary App")
st.write("Enter a word and its translation to add it to the dictionary.")

# Create input fields and a button within a form for a clean submission process
with st.form("dictionary_form", clear_on_submit=True):
    # Input for Tsakonian word
    tsakonian = st.text_input(
        "Tsakonian", 
        placeholder="e.g., Κονὸν", 
        help="Enter the Tsakonian word or phrase here."
    )

    # Input for Greek word
    greek = st.text_input(
        "Greek", 
        placeholder="e.g., Καλό", 
        help="Enter the Greek translation here."
    )

    # Submission button
    submit_button = st.form_submit_button("Προσθήκη στο λεξικό")

# Handle button click
if submit_button:
    if tsakonian and greek:
        # Call the function to add data
        add_to_database(tsakonian, greek)
    else:
        st.warning("Please fill in both fields before submitting.")

# Optionally, display the current contents of the table
st.markdown("---")
st.subheader("Current Dictionary Entries")

# Use st.cache_data to cache the query results
@st.cache_data(ttl=600)
def get_data():
    conn = st.connection("neon_db", type="sql")
    result = conn.query("SELECT tsd, ell FROM dictionary_contributions;")
    # Ensure result is a pandas DataFrame
    if isinstance(result, list):
        return pd.DataFrame(result)
    return result

try:
    df = get_data()
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.info("No entries found yet. Add some using the form above!")