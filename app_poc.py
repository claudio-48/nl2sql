import psycopg2
from vanna.legacy.ollama import Ollama
from vanna.legacy.chromadb import ChromaDB_VectorStore

# Definiamo la classe Custom Vanna
class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

# Inizializzazione con modello Qwen2.5-Coder e ChromaDB locale
vn = MyVanna(config={
    'model': 'qwen2.5-coder:7b',
    'ollama_host': 'http://localhost:11434',
    'path': './vanna_chroma_db'  # Persistenza locale del Vector DB
})

# Connessione al tuo Postgres locale
vn.connect_to_postgres(
    host='localhost',
    dbname='nl2sql',
    user='claudio',        # Sostituisci con il tuo utente
    password='1234',    # Sostituisci con la tua password
    port=5432
)

print("Connessione a Postgres e Ollama completata con successo!")
