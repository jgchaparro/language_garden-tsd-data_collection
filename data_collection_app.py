import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, insert

# Function to write data to the database
def add_to_database(tsd, ell, author=None):
    try:
        # Establish connection using Streamlit's connection
        conn = st.connection("neon_db", type="sql")

        # Define table metadata if not already defined globally or in a separate module
        # It's good practice to define your table schemas once.
        metadata = MetaData()
        dictionary_contributions = Table(
            "dictionary_contributions",
            metadata,
            Column("tsd", String),
            Column("ell", String),
            Column("author", String, nullable=True),  # Assuming author is optional
            Column("id", primary_key=True), # Assuming an auto-incrementing ID column
        )

        # Create the insert statement
        stmt = insert(dictionary_contributions).values(tsd=tsd, ell=ell, author=author)

        # Execute the insert statement
        # Streamlit's connection object might not directly expose .execute() in the same way
        # as a raw SQLAlchemy engine connection. We'll use conn.session.execute()
        # assuming `st.connection` provides a session-like object.
        # If not, you might need to get the raw engine and then create a connection from it.
        with conn.session as session:
            session.execute(stmt)
            session.commit() # Commit the transaction

        st.success("Η εγγραφή προστέθηκε με επιτυχία! 🎉")

        st.session_state.tsakonian_input = ""  # Clear the input field after successful submission
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Debug: Exception details:", e)

# --- Streamlit App Layout ---
st.title("Προσθήκη λεξέων στο Τσακώνικο Ψηφιακό Λεξικό")
# st.write("Εισάγετε μια λέξη και τη μετάφρασή της για να την προσθέσετε στο λεξικό.")

# --- Sidebar for Instructions ---
with st.sidebar:
    st.subheader("Οδηγίες")
    st.write(
        """
        Καλώς ήρθατε στη σελίδα προσωπικών συνεισφορών του Ψηφιακού Λεξικού Τσακωνικής Γλώσσας.
        """
    )
    st.markdown(
        """
        1) Συμπληρώστε τα παρακάτω πεδία: **Τσακώνικα**, **Ελληνικά** και **Συνεισφέρων**.
        2) Πατήστε το κουμπί **Προσθήκη στο λεξικό**.
        3) Οι υποβολές θα ελεγχθούν και θα προστεθούν στο λεξικό.
        """
    )
    st.write(
        """
        Εκτιμούμε ιδιαίτερα τον χρόνο και την προσπάθειά σας για τον εμπλουτισμό και την αναζωογόνηση της Τσακωνικής γλώσσας!
        """
    )

# Buttons for special Tsakonian characters
# col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
# # Container for special character buttons
# cols = st.columns(8)
# chars = ["κ̔", "π̔", "τ̔", "σ̌", "ζ̌", "ν̇", "λ̣", "τ͡σ"]
# for i, char in enumerate(chars):
#     if cols[i].button(char, key=f"btn_{i}"):
#         st.session_state.tsakonian_input += char

# Input for Author
author = st.text_input(
    "Συνεισφέρων",
    value=st.session_state.get("author", ""),
    placeholder="π.χ., Νίκος Παπαδόπουλος",
    help="Εισάγετε το όνομά σας ή ένα ψευδώνυμο εδώ."
)

if author == "":
    author = None
else:
    st.session_state.author = author

# Create input fields and a button within a form for a clean submission process
with st.form("dictionary_form", clear_on_submit=True):
    # Input for Tsakonian word
    tsakonian = st.text_input(
        "Τσακώνικα",
        value=st.session_state.get("tsakonian_input", ""),
        placeholder="π.χ., καλέ",
        help="Εισάγετε την Τσακώνικη λέξη εδώ.",
    )

    # Initialize session state for tsakonian_input if it doesn't exist
    if "tsakonian_input" not in st.session_state:
        st.session_state.tsakonian_input = ""
    
    # Update session state when text_input changes
    st.session_state.tsakonian_input = tsakonian

    # Input for Greek word
    greek = st.text_input(
        "Ελληνικά",
        placeholder="π.χ., καλός",
        help="Εισάγετε την Ελληνική μετάφραση εδώ."
    )

    # Submission button
    submit_button = st.form_submit_button("Προσθήκη στο λεξικό")

    # Handle button click
if submit_button:
    if tsakonian and greek:
        st.session_state.tsakonian_input = ""  # Update session state
        add_to_database(tsakonian, greek, author)
    else:
        st.warning("Παρακαλώ συμπληρώστε όλα τα απαραίτητα πεδία πριν την υποβολή (Τσακώνικα και Ελληνικά).")

# Optionally, display the current contents of the table
st.markdown("---")
st.subheader("Top συνεισφέροντες στο λεξικό")

# Use st.cache_data to cache the query results
@st.cache_data(ttl=600)
def get_data():
    conn = st.connection("neon_db", type="sql")
    result = conn.query("""
                        SELECT author, COUNT(*) as αριθμός_συνεισφορών
                        FROM dictionary_contributions
                        WHERE author IS NOT NULL
                        GROUP BY author
                        ORDER BY αριθμός_συνεισφορών DESC
                        LIMIT 10
                        """)
    # Ensure result is a pandas DataFrame
    if isinstance(result, list):
        return pd.DataFrame(result)
    return result

try:
    df = get_data()
    df = df.rename(columns={"author": "Συνεισφέρων", "αριθμός_συνεισφορών": "Αριθμός συνεισφορών"}, inplace=True)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.info("No entries found yet. Add some using the form above!")