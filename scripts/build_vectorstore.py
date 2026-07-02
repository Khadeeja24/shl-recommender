import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retriever import build_vectorstore

if __name__ == "__main__":
    print("Building ChromaDB vector store from catalog...")
    build_vectorstore()
    print("Done! Ready to run the agent.")