import streamlit as st
import time
from scrapper.scrapper import WebScraper
from llm.main import GeminiEmbeddingHandler
from vector_db.main import ProductDatabase
import os
from dotenv import load_dotenv
import pandas as pd
# Load environment variables from the home directory
load_dotenv()


# Setting up title and Necessary Inputs
st.title("Jiji Web Scrapper LLM")
st.text("Enter the item you want answers to:")

# Input for entering Item Name
item = st.text_input("Enter Item Name")
if st.button("Scrape Jiji"):
    if item:
        st.write("Scraping Jiji For the Required Information...")
        scraper = WebScraper(executable_path="./scrapper/chromedriver.exe",download_path=os.getenv("SCRAPPED_LOCATION"))
        url = f"https://jiji.com.et/search?query={item}"
        scraper.navigate_to(url)

        # Optional: Scroll down for a certain duration
        scraper.scroll_down(5)  # Scroll down for 10 seconds

        # Scrape data with the specified class name
        scraper.scrape_data(class_name="masonry-item",item_name =item )  # Replace with the actual class name

        # Store the Location of Scrapped Item in Streamlit session state
        download_path = os.getenv("SCRAPPED_LOCATION")
        st.session_state.scrapped_data = f"{download_path}/data.csv"

        handler = GeminiEmbeddingHandler(api_key=os.getenv("GOOGLE_API_KEY"))

        # Example of importing data in chunks
        chunks = handler.import_data_in_chunks(st.session_state.scrapped_data, 100)

        # Generate embeddings for a chunk of documents
        for chunk in chunks:
            document_embeddings = handler.get_embeddings_for_documents(chunk["Full"].to_list())
        # Instantiate the ProductDatabase
        db = ProductDatabase(host=os.getenv("HOST"),  # Use a string to specify the host
            port=os.getenv("PORT"),
            grpc_port=os.getenv("GRPC_PORT"),)
        try:
            # Connect to Weaviate
            db.connect()
            
            # Create the Product collection if it doesn't exist
            db.create_product_collection()
            
            # Add products with embeddings from chunks of data
            db.add_products_with_embeddings(chunks, handler.get_embeddings_for_documents)
            
            # Batch insert products into the Weaviate database
            db.batch_insert_products()

        finally:
            # Close the connection
            db.close_connection()

        st.session_state.finished_scrapping = True

if "finished_scrapping" in st.session_state :
    # Display the Scrapped Data in an expandable text box
    with st.expander("View Obtained Information"):
        df = pd.read_csv(st.session_state.scrapped_data)
        st.dataframe(df)
        # st.text_area("Obtained Information", "cleaned_content", height=300)

print(st.session_state)

# Step 2: Ask Questions About the Scrapped Data
if "finished_scrapping" in st.session_state:
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