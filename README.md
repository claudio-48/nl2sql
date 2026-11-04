# 📊 Proof of Concept (PoC) - NL2SQL Assistant Locale per DW Vendite

Un assistente di **Natural Language to SQL (NL2SQL)** privato, locale progettato per consentire l'interrogazione in linguaggio naturale di un Data Warehouse aziendale di vendite (PostgreSQL).

Il sistema è basato sull'orchestratore RAG **Vanna.ai**, un LLM locale (**Qwen2.5-Coder 7B** tramite **Ollama**), **ChromaDB** come Vector Database locale e un'interfaccia **Streamlit** reattiva e contestuale.

---

## 🌟 Caratteristiche Principali

* **Privacy & Sicurezza Totale (100% On-Premise):** Nessun invio di dati aziendali o query verso API o servizi cloud esterni.
* **LLM di Codice Specializzato:** Utilizzo del modello `qwen2.5-coder:7b` via Ollama per la massima accuratezza nella generazione di SQL Postgres nativo.
* **Addestramento RAG Multilivello:** Combinazione di DDL dello schema a stella, commenti del database PostgreSQL, regole aziendali esplicite e query Few-Shot per ridurre al minimo le allucinazioni.
* **Vista Denormalizzata (`mis_dw`):** Semplificazione delle JOIN complesse per velocizzare e rendere deterministica la generazione SQL.
* **Interfaccia Web Conversazionale (Streamlit):**
  * Supporto per **memoria conversazionale di sessione** (domande sequenziali di approfondimento).
  * **Grafici dinamici con Plotly Express**.
  * **Soglia di sicurezza visiva:** Disabilitazione automatica dei grafici per set di risultati superiori a 8 righe per preservare la leggibilità.

---

## 🏗️ Architettura del Sistema

```
┌──────────────────────────────────────────────────────────┐
│             Streamlit UI / OpenACS Target                │
└──────────────────────────┬───────────────────────────────┘
                           │ (Prompt dell'utente)
                           ▼
┌──────────────────────────────────────────────────────────┐
│                   Vanna.ai Framework                     │
│  ┌───────────────────────┐   ┌────────────────────────┐  │
│  │   ChromaDB (Local)    │   │ Ollama (qwen2.5-coder) │  │
│  │  Vector Search (RAG)  │   │  Local LLM Inference   │  │
│  └───────────────────────┘   └────────────────────────┘  │
└──────────────────────────┬───────────────────────────────┘
                           │ (SQL Generato)
                           ▼
┌──────────────────────────────────────────────────────────┐
│             PostgreSQL Data Warehouse (DW)               │
│               - Star Schema (Dimensioni & Fatti)         │
│               - Vista Denormalizzata `mis_dw`            │
└──────────────────────────────────────────────────────────┘
```

---

## 📋 Requisiti di Sistema

* **OS:** Linux (testato su Debian 13 Trixie)
* **Python:** 3.10 o superiore
* **Database:** PostgreSQL 14+ con Data Warehouse caricato (`mis_dw`)

---

## 🚀 Guida all'Installazione

### 1. Clona il repository, installa Ollama e prepara l'ambiente virtuale

```bash
git clone https://github.com/claudio-48/nl2sql.git
cd nl2sql

# Installa Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Creazione ed attivazione venv
python3 -m venv venv
source venv/bin/activate
```

### 2. Installa le dipendenze Python

```bash
pip install --upgrade pip
pip install "vanna[chromadb,ollama,postgres]" pandas streamlit plotly psycopg2-binary
```

### 3. Configura ed avvia Ollama

Assicurati che Ollama sia installato ed avvia il download del modello di codice locale e di embedding:

```bash
# Scarica il modello LLM di generazione codice SQL
ollama run qwen2.5-coder:7b

# Scarica il modello per la ricerca vettoriale RAG
ollama pull nomic-embed-text
```

---

## 🛠️ Configurazione e Addestramento (Training)

### 1. Inizializzazione di Vanna (`app_poc.py`)

Utilizza il file `app_poc.py` per definire la connessione tra Vanna, Ollama, ChromaDB e PostgreSQL:

```bash
python3 app_poc.py
```

### 2. Esecuzione dello script di training (`train_poc.py`)

Esegui lo script di addestramento per indicizzare il DDL, i commenti dello schema e gli esempi di query Few-Shot:

```bash
python3 train_poc.py
```

> **Nota:** Se apporti modifiche alle regole aziendali o agli esempi in `train_poc.py`, cancella la cartella del Vector DB locale con `rm -rf ./vanna_chroma_db` prima di rieseguire lo script di training.

---

## 🖥️ Avvio dell'Applicazione Web

Per avviare l'interfaccia Streamlit esegui l'utility nativa di Streamlit:

```bash
streamlit run app_web.py
```

L'interfaccia si aprirà automaticamente nel browser all'indirizzo `http://localhost:8501`.

---


## 🛣️ Roadmap Prossimi Sviluppi (Integrazione OpenACS)

* [x] **Fase 1:** Prototipazione locale con Ollama, Vanna e Postgres.
* [x] **Fase 2:** Ottimizzazione grafici Plotly e soglie di visualizzazione.
* [x] **Fase 3:** Introduzione memoria di sessione ed eliminazione modelli non performanti (`deepseek-r1`).
* [ ] **Fase 4:** 
  * Wrapping dell'engine Python/Vanna in un microservizio **FastAPI** locale (`POST /api/v1/ask`).
  * Sviluppo di un pacchetto nativo **OpenACS (Tcl/ADP)** per integrare l'assistente nell'interfaccia ERP aziendale ereditando il sistema di permessi e le ACL del Kernel ACS.