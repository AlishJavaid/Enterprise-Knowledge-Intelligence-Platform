Athenaeum: Enterprise Knowledge Intelligence Platform
A production-grade, dockerized Retrieval-Augmented Generation (RAG) system designed for secure, multi-format enterprise document reasoning.
# **1. Overview**

Athenaeum is a production-grade, Dockerized Retrieval-Augmented Generation (RAG) system designed for secure, multi-format enterprise document reasoning.

It addresses major challenges in corporate knowledge management, including data silos, LLM hallucinations, and high inference costs. Unlike basic ChatGPT wrappers, Athenaeum provides a custom Hybrid Search Engine, Air-Gapped Docker Deployment, Edge-Optimized Memory Architecture, and fully traceable citations.

# **2. Key Features**

## **2.1 Multi-Document Reasoning**

Athenaeum can synthesize information across multiple documents and file formats. For example, it can combine financial data from a CSV file with policy rules from a PDF to generate a comprehensive answer.

## **2.2 Hybrid Search with RRF**

The platform combines semantic vector search using pgvector with BM25 keyword matching. Reciprocal Rank Fusion (RRF) merges both search results to provide highly relevant context.

## **2.3 Edge-Optimized AI**

Athenaeum uses Fastembed with ONNX Runtime instead of heavy PyTorch-based embedding solutions. This reduces container memory usage and improves embedding performance, making the system suitable for CPU-only and resource-constrained environments.

## **2.4 Grounded Generation and Auto-Citations**

Every generated response is strictly grounded in retrieved document context. The interface provides clickable citation tags that allow users to trace answers back to their original source chunks.

## **2.5 Enterprise Security**

The system uses JWT-based authentication and Role-Based Access Control (RBAC). Users can only retrieve and interact with documents they are explicitly authorized to access.

## **2.6 Sub-Second Inference**

Athenaeum uses Groq's LPU infrastructure with the Llama 3.1 8B Instant model to provide fast conversational responses.

## **2.7 Air-Gapped Deployment**

AI models are downloaded and cached during the Docker image build process. This allows the application to operate without external network access at runtime, making it suitable for secure enterprise environments.

# **3. Architecture and Technology Stack**

| Component        | Technology                                  | Purpose                                                      |
| ---------------- | ------------------------------------------- | ------------------------------------------------------------ |
| **Backend API**  | FastAPI, Uvicorn                            | Asynchronous REST API, validation, and Swagger UI            |
| **Database**     | PostgreSQL + pgvector                       | Relational data storage and scalable vector indexing         |
| **Embeddings**   | Fastembed (ONNX)                            | Lightweight semantic embeddings using BAAI/bge-small-en-v1.5 |
| **LLM Provider** | Groq API                                    | Ultra-fast LLM inference using Llama 3.1 8B Instant          |
| **Ingestion**    | PyMuPDF, python-docx, BeautifulSoup, Pandas | Processing PDF, DOCX, HTML, and CSV files                    |
| **Frontend**     | Vanilla JavaScript, Custom CSS              | Interactive glassmorphism-based user interface               |
| **Deployment**   | Docker, Docker Compose                      | Reproducible and fully containerized deployment              |

# **4. Quick Start**

The basic requirements for running Athenaeum are:

1. Install and run **Docker Desktop**.
2. Obtain a free **Groq API Key**.
3. Configure the API key in the application's environment configuration.
4. Build and start the application using Docker Compose.
5. Access the Athenaeum interface and begin uploading enterprise documents.

# **5. Advanced Engineering Highlights**

## **5.1 Memory Optimization: ONNX vs. PyTorch**

Traditional RAG systems commonly use Sentence Transformers with PyTorch, which can significantly increase Docker image size and memory consumption.

Athenaeum replaces this approach with Fastembed and ONNX Runtime. The result is a lightweight embedding pipeline that can operate efficiently on CPU-only edge devices and enterprise containers with limited memory.

## **5.2 Air-Gapped Model Baking**

Enterprise environments may prevent containers from accessing external services such as Hugging Face during runtime.

Athenaeum solves this problem by downloading and caching the required model weights during the Docker build process. The final Docker image therefore contains the required AI model locally and does not need external model downloads at runtime.

## **5.3 Reciprocal Rank Fusion**

Vector search is highly effective for semantic similarity but may struggle with exact identifiers such as error codes, product IDs, or policy numbers.

Keyword search, on the other hand, is effective for exact matches but may fail to understand synonyms and semantic relationships.

Athenaeum performs both searches and combines their rankings using **Reciprocal Rank Fusion (RRF)**. This produces a stronger and more reliable context set for the LLM.

# **6. Security and Access Control**

Athenaeum is designed for enterprise environments where document confidentiality is essential.

The platform implements:

1. **JWT-based authentication**
2. **Role-Based Access Control (RBAC)**
3. **Document-level authorization**
4. **Restricted retrieval based on user permissions**
5. **Grounded responses based only on authorized documents**

This ensures that users cannot retrieve information from documents they are not permitted to access.

# **7. Deployment Architecture**

The complete system is containerized using **Docker and Docker Compose**.

The architecture consists of:

1. **Frontend** – Provides the interactive document and chat interface.
2. **FastAPI Backend** – Handles authentication, document processing, retrieval, and generation.
3. **PostgreSQL + pgvector** – Stores document metadata, chunks, embeddings, and relational data.
4. **Fastembed + ONNX Runtime** – Generates lightweight semantic embeddings.
5. **Hybrid Search Engine** – Performs vector and keyword retrieval followed by RRF.
6. **Groq LLM** – Generates grounded responses using the retrieved context.

# **8. End-to-End Workflow**

The Athenaeum workflow follows these steps:

1. **User Authentication** – The user logs into the platform using secure authentication.
2. **Document Upload** – Authorized users upload PDF, DOCX, HTML, or CSV files.
3. **Document Parsing** – The appropriate parser extracts text and structured information.
4. **Chunking** – Documents are divided into manageable context chunks.
5. **Embedding Generation** – Fastembed generates vector embeddings for each chunk.
6. **Database Storage** – Chunks, metadata, permissions, and embeddings are stored in PostgreSQL.
7. **User Query** – The user asks a question through the conversational interface.
8. **Hybrid Retrieval** – The system performs semantic vector search and BM25 keyword search.
9. **RRF Ranking** – Results from both search methods are combined using Reciprocal Rank Fusion.
10. **Context Construction** – The most relevant authorized chunks are provided to the LLM.
11. **Grounded Generation** – The LLM generates an answer based strictly on the retrieved context.
12. **Citation Generation** – The UI displays source citations linked to the relevant document chunks.
13. **Final Response** – The user receives a fast, traceable, and context-grounded answer.

# **9. Advantages of Athenaeum**

Athenaeum provides several advantages over basic RAG implementations:

* **Multi-format document support**
* **Multi-document reasoning**
* **Hybrid semantic and keyword retrieval**
* **Reduced memory consumption**
* **CPU-friendly embedding generation**
* **Air-gapped deployment capability**
* **Enterprise authentication and authorization**
* **Traceable citations**
* **Fast LLM inference**
* **Fully Dockerized deployment**
* **Scalable PostgreSQL-based vector storage**

# **10. License**

Athenaeum was developed as a **6th-Semester Capstone Project (CS-610)** and is available under the **MIT License**.

# **11. Acknowledgments**

Athenaeum acknowledges the following technologies and organizations that contributed to the project:

* **FastAPI** for the high-performance asynchronous web framework.
* **pgvector** for native vector search capabilities within PostgreSQL.
* **Groq** for fast LLM inference.
* **Qdrant/Fastembed** for lightweight ONNX-based embedding models.

# **12. Conclusion**

Athenaeum is a secure, production-oriented Enterprise RAG platform that combines hybrid information retrieval, lightweight AI inference, document-level security, grounded generation, and automatic citations.

By integrating **FastAPI, PostgreSQL, pgvector, Fastembed, ONNX Runtime, Docker, and Groq**, Athenaeum provides an efficient and scalable solution for organizations that need to securely interact with their proprietary knowledge while maintaining accuracy, traceability, and deployment flexibility.
