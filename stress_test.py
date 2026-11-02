from app_poc import vn

domande_test = [
    # 1. Filtro temporale testuale (mese in italiano vs numero)
    "Quanto abbiamo venduto a Marzo 2025?",
    
    # 2. Aggregazione multi-dimensione e ordinamento
    "Mostrami il fatturato per categoria prodotto e zona di vendita nel 2025",
    
    # 3. Confronto/Filtro su tipologia cliente
    "Quali sono i primi 3 clienti (escludendo il tipo cliente AGENTI) per importo ordinato?",
    
    # 4. Domanda indiretta (richiede calcolo di media o conteggio)
    "Qual è il valore medio delle righe d'ordine gestite da ciascun rappresentante?"
]

for q in domande_test:
    print(f"\n==========================================")
    print(f"Domanda: {q}")
    print(f"==========================================")
    try:
        sql = vn.generate_sql(q)
        print(f"SQL Generata:\n{sql}\n")
        df = vn.run_sql(sql)
        print("Risultato (prime 5 righe):")
        print(df.head())
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")
