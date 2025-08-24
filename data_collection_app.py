import streamlit as st
import pandas as pd
from src.utils import add_to_database, get_top_contributors, orthographic_norms_explanation

### App layout ###
st.title("Προσθήκη στο Τσακώνικο Ψηφιακό Λεξικό & Αρχείο Κειμένων")

## Sidebar ##
with st.sidebar:
    st.subheader("Οδηγίες")
    st.write(
        """
        Καλώς ήρθατε στη σελίδα προσωπικών συνεισφορών του Ψηφιακού Λεξικού και Αρχείου Κειμένων της Τσακωνικής Γλώσσας.
        """
    )
    st.markdown(
        """
        1) Διαβάστε προσεκτικά τους ορθογραφικούς κανόνες που εξηγούνται στο τμήμα **Ορθογραφικοί κανόνες** στο πάνω μέρος της σελίδας. **Σας παρακαλούμε να ακουλουθήσετε είτε την ορθογραφία του Κωστάκη είτε του Μαρνέρη** για τεχνικούς λόγους.
        2) Συμπληρώστε τα παρακάτω πεδία: **Τσακώνικα**, **Ελληνικά** και **Συνεισφέρων**.
        3) Πατήστε το κουμπί **Προσθήκη**.
        4) Οι υποβολές θα ελεγχθούν και θα προστεθούν.
        """
    )

    # Αν η εισαγωγή σας περιέχει μόνο μία λέξη, θα προστεθεί στο λεξικό. Αν περιέχει **περισσότερες από μία λέξεις** (π.χ. φράσεις ή κείμενα), θα προστεθεί στο αρχείο κειμένων.

    st.write(
        """
        Εκτιμούμε ιδιαίτερα τον χρόνο και την προσπάθειά σας για τον εμπλουτισμό και την αναζωογόνηση της Τσακωνικής γλώσσας! **Νιουμ' έμε ευχαριστούντε πρεσ̌ού!**.
        """
    )

## Tabs ##
tabs = st.tabs(["Προσθήκη κειμένων", "Ορθογραφικοί κανόνες"])

# Data input tab
with tabs[0]:
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

    # Create form
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
        submit_button = st.form_submit_button("Προσθήκη", type="primary")

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

    # Button to load and display top contributors
    if st.button("Εμφάνιση Κορυφαίων Συνεισφερόντων"):
        try:
            df = get_top_contributors()
            # Rename columns for display
            df.rename(columns={"author": "Συνεισφέρων", "n_contributions": "Αριθμός συνεισφορών"}, inplace=True)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.info("Δεν υπάρχουν ακόμα συνεισφορές. Προσθέστε μερικές χρησιμοποιώντας την παραπάνω φόρμα!")

## Orthographic norms tab ##
with tabs[1]:
    st.markdown(orthographic_norms_explanation)