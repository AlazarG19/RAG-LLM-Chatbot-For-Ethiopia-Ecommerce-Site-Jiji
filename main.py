import streamlit as st
import time

# Setting up title and Necessary Inputs
st.title("Jiji Web Scrapper LLM")
st.text("Enter the item you want answers to:")

# Input for entering Item Name
item = st.text_input("Enter Item Name")
if st.button("Scrape Jiji"):
    if item:
        st.write("Scraping the Jiji For the Required Information...")

        # Store the Location of Scrapped Item in Streamlit session state
        st.session_state.scrapped_data = "Items Obtained"
if "scrapped_data" in st.session_state :
    # Display the Scrapped Data in an expandable text box
    with st.expander("View Obtained Information"):
        st.text_area("Obtained Information", "cleaned_content", height=300)

print(st.session_state)

# Step 2: Ask Questions About the Scrapped Data
if "scrapped_data" in st.session_state:
    parse_description = st.text_area("Ask Your Question Down Below")
    show_parsing = True

    if st.button("Parse Content"):
        print("parse content")
        if parse_description:
            if show_parsing:
                st.write("Parsing the content...")
            time.sleep(2)
            show_parsing = False
            st.write("parsed_result")
            st.write("parsed_result2")