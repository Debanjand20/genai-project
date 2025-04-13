import os
import streamlit as st
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings

DATA_DIR = "data"

@st.cache_resource
def load_knowledge_base():
    """Loads documents from the data directory and creates a FAISS index."""
    docs = []
    doc_metadata = {}

    try:
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".txt"):
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    docs.append(Document(page_content=content, metadata={"source": filename}))
                    doc_metadata[filename.replace('.txt', '')] = content

        if not docs:
            st.error(f"No .txt files found in the '{DATA_DIR}' directory.")
            return None, None

        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(docs)

        try:
            # Use HuggingFace Embeddings instead of OpenAI
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store = FAISS.from_documents(split_docs, embeddings)
            st.success("Knowledge Base loaded and indexed.")
            return vector_store, doc_metadata

        except Exception as e:
            st.error(f"Failed to initialize embeddings or FAISS: {e}")
            return None, doc_metadata

    except FileNotFoundError:
        st.error(f"Error: The directory '{DATA_DIR}' was not found.")
        return None, None
    except Exception as e:
        st.error(f"An error occurred loading the knowledge base: {e}")
        return None, None

def query_knowledge_base(vector_store, query, k=2):
    """Queries the vector store for relevant documents."""
    if vector_store:
        try:
            results = vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            st.error(f"Error querying knowledge base: {e}")
            return []
    return []

# Initialize KB globally (cached)
vector_store, raw_docs_content = load_knowledge_base()
