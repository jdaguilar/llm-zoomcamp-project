"""DAG definition for the RAG pipeline."""

from datetime import datetime, timedelta
import subprocess

from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.decorators import task, task_group
from airflow.models.dag import DAG
from elasticsearch.exceptions import RequestError
from elasticsearch import Elasticsearch
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from sentence_transformers import SentenceTransformer


# Task partition an chunks
@task
def partition_and_chunk_html(filename, **kwargs):
    elements = partition_html(filename)
    chunks = chunk_by_title(
        elements,
        max_characters=10000,
        multipage_sections=False,
        combine_text_under_n_chars=10000,
    )
    return [chunk.to_dict() for chunk in chunks]


@task
def create_embeddings(chunks, **kwargs):
    model = SentenceTransformer("all-mpnet-base-v2")

    operations = []
    for i, doc in enumerate(chunks, 1):
        sample = {
            "text": doc["text"],
            "chunk_id": i,
            "file_directory": doc["metadata"]["file_directory"],
            "text_vector": model.encode(doc["text"]).tolist(),
        }
        operations.append(sample)
    return operations


@task
def index_to_elasticsearch(operations, **kwargs):
    es_client = Elasticsearch("http://elasticsearch:9200")
    index_name = "file_directory"

    # Create index (you might want to move this to a separate task)
    index_settings = {
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "chunk_id": {"type": "text"},
                "file_directory": {"type": "keyword"},
                "text_vector": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": True,
                    "similarity": "cosine",
                },
            }
        },
    }
    try:
        es_client.indices.create(index=index_name, body=index_settings)
    except RequestError as ex:
        if ex.error == 'resource_already_exists_exception':
            pass  # Index already exists. Ignore.

    for doc in operations:
        try:
            es_client.index(index=index_name, document=doc)
        except Exception as e:
            print(e)


@task
def list_files_to_xcom(**kwargs):
    command = "find /tmp/data/clean_docs -type f -name '*.html' | sort"
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)
    file_list = result.stdout.strip().split("\n")
    return file_list


# DAG default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@task_group()
def feed_rag(filename, **kwargs):

    # apply a partition and chunk
    partition_task = partition_and_chunk_html(filename=filename)

    embedding_task = create_embeddings(chunks=partition_task)

    index_to_es_task = index_to_elasticsearch(operations=embedding_task)

    partition_task >> embedding_task >> index_to_es_task


# Initialize DAG
with DAG(
    "hudi_assistant_dag",
    default_args=default_args,
    description="Apache Hudi Assistant DAG",
    schedule_interval="@weekly",
    catchup=False,
) as dag:
    # Dummy task to test the DAG
    dummy_task = DummyOperator(
        task_id="dummy_task",
    )

    # Download docs using bash operator
    download_docs = BashOperator(
        task_id="download_docs",
        bash_command="""
        export EFS_DIR=/tmp/data/docs

        wget -e robots=off --recursive --no-clobber --page-requisites \
        --html-extension --convert-links --restrict-file-names=windows \
        --domains hudi.apache.org --no-parent --accept=html \
        -P $EFS_DIR https://hudi.apache.org/docs/

        find $EFS_DIR -type d -name "*.html" -exec rm -rf {} +

        # remove directories starting with 0.
        find $EFS_DIR -type d -name "0.*" -exec rm -rf {} +
        """,
    )

    # Run Python File to clean HTML
    clean_html = BashOperator(
        task_id="clean_html",
        bash_command="""
        python /opt/airflow/dags/extra/scripts/clean_html.py
        """,
    )

    list_files = list_files_to_xcom()

    feed_hudi_rag = feed_rag.expand(filename=list_files)

    (dummy_task >> download_docs >> clean_html >> list_files >> feed_hudi_rag)
