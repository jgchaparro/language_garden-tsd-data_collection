import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, insert

# Function to write data to the database
def add_to_database(
        target_table_name: str,
        tsd: str,
        ell: str,
        author=None
    ):

    try:
        # Establish connection using Streamlit's connection
        conn = st.connection("neon_db", type="sql")

        # Define table metadata
        metadata = MetaData()
        
        # --- Define the dictionary table schema ---
        # No need to define 'id' column manually as it will be auto-incremented by PostgreSQL
        target_table = Table(
            target_table_name,
            metadata,
            Column("tsd", String),
            Column("ell", String),
            Column("author", String, nullable=True),
        )
        
        # Create the insert statement
        stmt = insert(target_table).values(tsd=tsd, ell=ell, author=author)

        # Execute the insert statement and commit the transaction
        with conn.session as session:
            session.execute(stmt)
            session.commit()

        st.success("Η εγγραφή προστέθηκε με επιτυχία! 🎉")

    except Exception as e:
        st.error(f"Παρουσιάστηκε σφάλμα: {e}")
        st.write("Debug: Λεπτομέρειες εξαίρεσης:", e)

# --- Streamlit App Layout ---
st.title("Προσθήκη στο Τσακώνικο Ψηφιακό Λεξικό & Αρχείο Κειμένων")
# st.write("Εισάγετε μια λέξη, πρόταση, ή κείμενο και τη μετάφρασή της/του.")

# --- Sidebar for Instructions ---
with st.sidebar:
    st.subheader("Οδηγίες")
    st.write(
        """
        Καλώς ήρθατε στη σελίδα προσωπικών συνεισφορών του Ψηφιακού Λεξικού και Αρχείου Κειμένων της Τσακωνικής Γλώσσας.
        """
    )
    st.markdown(
        """
        1) Συμπληρώστε τα παρακάτω πεδία: **Τσακώνικα**, **Ελληνικά** και **Συνεισφέρων**.
        2) Πατήστε το κουμπί **Προσθήκη**.
        3) Αν η εισαγωγή σας περιέχει μόνο μία λέξη, θα προστεθεί στο λεξικό. Αν περιέχει **περισσότερες από μία λέξεις** (π.χ. φράσεις ή κείμενα), θα προστεθεί στο αρχείο κειμένων.
        4) Οι υποβολές θα ελεγχθούν και θα προστεθούν.
        """
    )
    st.write(
        """
        Εκτιμούμε ιδιαίτερα τον χρόνο και την προσπάθειά σας για τον εμπλουτισμό και την αναζωογόνηση της Τσακωνικής γλώσσας! **Νιουμ' έμε ευχαριστούντε πρεσ̌ού!**.
        """
    )

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
    # Input for Tsakonian word/text
    tsakonian = st.text_area(
        "Τσακώνικα (λέξη, πρόταση ή κείμενο)",
        value=st.session_state.get("tsakonian_input", ""),
        placeholder='π.χ., "καλέ" (λέξη) ή "Κα ναμέρα, ένι θέου να βοηθήου" (πρόταση)',
        help="Εισάγετε την Τσακώνικη λέξη, πρόταση, ή κείμενο εδώ.",
    )

    # Initialize session state for tsakonian_input if it doesn't exist
    if "tsakonian_input" not in st.session_state:
        st.session_state.tsakonian_input = ""
    
    # Update session state when text_input changes
    st.session_state.tsakonian_input = tsakonian

    # Input for Greek word/text
    greek = st.text_area(
        "Ελληνικά (μετάφραση)",
        value=st.session_state.get("greek_input", ""),
        placeholder='π.χ., "καλός" (λέξη) ή "Καλημέρα, θέλω να βοηθήσω" (πρόταση)',
        help="Εισάγετε την Ελληνική μετάφραση εδώ."
    )
    
    # Initialize session state for greek_input if it doesn't exist
    if "greek_input" not in st.session_state:
        st.session_state.greek_input = ""

    # Update session state when text_input changes
    st.session_state.greek_input = greek

    # Submission button
    submit_button = st.form_submit_button("Προσθήκη")

# Handle button click
if submit_button:
    # Check if inputs are not empty after stripping whitespace
    tsakonian_stripped = tsakonian.strip()
    greek_stripped = greek.strip()

    if tsakonian_stripped and greek_stripped:
        # Check for spaces to determine if it's a single word or a text
        target_table = 'texts_contributions' if ' ' in tsakonian_stripped else 'dictionary_contributions'
        
        # Add the entry to the database
        add_to_database(target_table, tsakonian_stripped, greek_stripped, author)
        
    else:
        st.warning("Παρακαλώ συμπληρώστε όλα τα απαραίτητα πεδία πριν την υποβολή (Τσακώνικα και Ελληνικά).")

# --- Section for Top Contributors ---
st.markdown("---")
st.subheader("Κορυφαίοι Συνεισφέροντες")

# Use st.cache_data to cache the query results
@st.cache_data(ttl=600)
def get_top_contributors():
    conn = st.connection("neon_db", type="sql")
    # Query both tables and combine the results to get the total contributions
    result = conn.query("""
        SELECT author, COUNT(*) as n_contributions
        FROM (
            SELECT author FROM dictionary_contributions WHERE author IS NOT NULL
            UNION ALL
            SELECT author FROM texts_contributions WHERE author IS NOT NULL
        ) AS combined_contributions
        GROUP BY author
        ORDER BY n_contributions DESC
        LIMIT 10
        """)
    return result

# Button to load and display top contributors
if st.button("Εμφάνιση Κορυφαίων Συνεισφερόντων"):
    try:
        df = get_top_contributors()
        # Rename columns for display
        df.rename(columns={"author": "Συνεισφέρων", "n_contributions": "Αριθμός συνεισφορών"}, inplace=True)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.info("Δεν υπάρχουν ακόμα συνεισφορές. Προσθέστε μερικές χρησιμοποιώντας την παραπάνω φόρμα!")