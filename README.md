# Apache Hudi Assistant

## 📝 Project Overview

Apache Hudi Assistant is a Retrieval-Augmented Generation (RAG) system designed to provide responses to questions about Apache Hudi. This project leverages the Apache Hudi documentation as its knowledge base, offering users accurate and context-aware information about Apache Hudi's features, configurations, and best practices.

### 🎯 Key Features:

- RAG-based question-answering system

- Apache Hudi documentation as the knowledge base

- Automatic ingestion pipeline for processing and indexing documentation

- Web-based user interface for interaction

- Elasticsearch for vector search

- Airflow as orchestration tool

## 🚀 Problem Statement

Apache Hudi defines itself like a "streaming data lake platform". It has a lot of features that converts it in a powerful tool, but at the same time its very complex and challenging to understand and take advantage of all its potential features. 

Hudi users need quick and accurate answers to their questions about Hudi's functionality, configuration options, and also the best practices. So, The Apache Hudi Assistant tries to be a solution for the needs of people who works every day with it.

## 🛠️ Technologies Used

- **LLM:** Ollama (llama3.2:1b model)

- **Vector Database:** Elasticsearch

- **Orchestration:** Apache Airflow

- **Web UI:** Flask

- **Embedding Model:** Sentence Transformers (all-mpnet-base-v2)

- **Data Processing:** Unstructured, BeautifulSoup

## 🏗️ Architecture

The Apache Hudi Assistant consists of several components working together:

1. **Data Ingestion:** Airflow DAG download the Apache Hudi's Documentation from the website. All downloaded files are in HTML format.

2. **Data Cleaning:** The downloaded files are cleaned using a python script which uses `BeautifulSoup` to remove unnecessary elements fron the HTML file (like scripts and styles).

3. **Data Chunking:** All cleaned files are chunked in a fixed size (that's not optimal, to be improved in the future). In this task the library `unstructured` is used.

4. **Embedding Generation:** `Sentence Transformers` model creates vector embeddings for each chunk.

5. **Indexing:** Processed chunks and their embeddings are indexed in `Elasticsearch`.

6. **Query Processing:** User queries are embedded and used to retrieve relevant context from Elasticsearch.

7. **Response Generation:** Retrieved context and user query are sent to the LLM to generate a response.

8. **Web Interface:** A Flask-based web application allows users to interact with the system.

## 🔧 Setup and Installation

**Prerequisites:** 

- Docker and Docker Compose

- Git

### Steps to Run

1. Clone the repository:

    ```
    git clone git@github.com:jdaguilar/llm-zoomcamp-project.git
    ```

2. Start the Docker containers:

    ```
    docker compose up -d
    ```

3. Access the Airflow web interface at http://localhost:8080 and trigger the RAG pipeline DAG to process the documentation. The DAG name is `hudi_assistant_dag`

4. Once the pipeline is complete, access the Apache Hudi Assistant web interface at http://localhost:5000.

    > [!IMPORTANT]  
    > You must wait DAG complete all task before use the Web App.
    >
    >The first time you ask to the Hudi Assistant, it will try to download Llama3 model, so the first answer could be slow to retrieve.
