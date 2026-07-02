import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.retriever import build_vectorstore

if __name__ == "__main__":
    build_vectorstore()