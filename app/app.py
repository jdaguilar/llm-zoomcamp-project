from flask import Flask, request, render_template
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from openai import OpenAI


app = Flask(__name__)


# Initialize necessary components
model = SentenceTransformer("all-mpnet-base-v2")
es_client = Elasticsearch('http://elasticsearch:9200')
client = OpenAI(
    base_url='http://ollama:11434/v1/',
    api_key='ollama',
)


def vector_elastic_search(vector_search_term):
    query = {
        "field": "text_vector",
        "query_vector": vector_search_term,
        "k": 5,
        "num_candidates": 10000,
    }

    response = es_client.search(
        index="file_directory",
        knn=query,
        source=["text", "chunk_id", "file_directory"]
    )

    result_docs = []

    for hit in response['hits']['hits']:
        result_docs.append(hit['_source'])

    return result_docs


def build_prompt(query, search_results):
    prompt_template = """
    You're a Apache Hudi Assistant. Answer the QUESTION based on the CONTEXT
    given from the Documentation.

    Use only the facts from the CONTEXT when answering the QUESTION.

    QUESTION: {question}

    CONTEXT:

    {context}
    """.strip()

    context = ""

    for doc in search_results:
        context = context + \
            f"file_directory: {doc['file_directory']}\n" + \
            f"chunk_id: {doc['chunk_id']}\nanswer: {doc['text']}\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


def llm(prompt):
    response = client.chat.completions.create(
        model='llama3.2:1b',
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def rag(query):
    vector_search_term = model.encode(query)
    search_results = vector_elastic_search(vector_search_term)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_query = request.form['query']
        answer = rag(user_query)
        return render_template('index.html', query=user_query, answer=answer)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
