from app_poc import vn

# Test 1: Query in linguaggio naturale
domanda = "Qual è la zona di vendita in cui abbiamo fatturato di più?"
print(f"\n--- Domanda: {domanda} ---")

# Genera la query SQL
sql_generata = vn.generate_sql(domanda)
print(f"SQL Generata:\n{sql_generata}\n")

# Esegue la query su Postgres e mostra il risultato
df = vn.run_sql(sql_generata)
print("Risultato:")
print(df)