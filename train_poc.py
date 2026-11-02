from app_poc import vn

print("--- 1. Caricamento DDL nello schema ---")

ddl_statements = [
    """
    CREATE TABLE time_dimension (
        time_key INTEGER PRIMARY KEY,
        full_date DATE NOT NULL,
        year_and_month INTEGER NOT NULL,
        year_and_month_date DATE NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        alpha_month VARCHAR(9) NOT NULL,
        alpha_month_short CHAR(3) NOT NULL,
        year_and_quarter INTEGER NOT NULL,
        alpha_quarter CHAR(6) NOT NULL
    );
    """,
    """
    CREATE TABLE product_dimension (
        product_key INTEGER PRIMARY KEY,
        product_code VARCHAR(40),
        product_description VARCHAR(1000),
        category_code VARCHAR(20),
        category_description VARCHAR(1000)
    );
    """,
    """
    CREATE TABLE customer_dimension (
        customer_key INTEGER PRIMARY KEY,
        customer_code VARCHAR(40),
        customer_description VARCHAR(1000),
        customer_type VARCHAR(50)
    );
    """,
    """
    CREATE TABLE sale_zones_dimension (
        sale_zones_key INTEGER PRIMARY KEY,
        sale_zones_code VARCHAR(40),
        sale_zones_description VARCHAR(1000)
    );
    """,
    """
    CREATE TABLE sale_reps_dimension (
        sale_reps_key INTEGER PRIMARY KEY,
        sale_reps_code VARCHAR(40),
        sale_reps_description VARCHAR(1000)
    );
    """,
    """
    CREATE TABLE order_lines_dw (
        line_id INTEGER PRIMARY KEY,
        time_key INTEGER REFERENCES time_dimension(time_key),
        customer_key INTEGER REFERENCES customer_dimension(customer_key),
        product_key INTEGER REFERENCES product_dimension(product_key),
        sale_zones_key INTEGER REFERENCES sale_zones_dimension(sale_zones_key),
        sale_reps_key INTEGER REFERENCES sale_reps_dimension(sale_reps_key),
        quantity NUMERIC(14,2),
        amount NUMERIC(12,3)
    );
    """,
    """
    CREATE VIEW mis_dw AS
    SELECT 
        l.quantity, l.amount,
        p.product_code, p.product_description, p.category_code, p.category_description,
        c.customer_code, c.customer_description, c.customer_type,
        t.full_date as order_date, t.year, t.year_and_month, t.year_and_month_date, t.month,
        t.alpha_month, t.alpha_month_short, t.year_and_quarter, t.alpha_quarter,
        s.sale_reps_code, s.sale_reps_description,
        z.sale_zones_code, z.sale_zones_description
    FROM order_lines_dw l
        JOIN sale_zones_dimension z ON l.sale_zones_key = z.sale_zones_key
        JOIN sale_reps_dimension s ON l.sale_reps_key = s.sale_reps_key
        JOIN time_dimension t ON l.time_key = t.time_key
        JOIN product_dimension p ON l.product_key = p.product_key
        JOIN customer_dimension c ON l.customer_key = c.customer_key;
    """
]

for ddl in ddl_statements:
    vn.train(ddl=ddl)

print("\n--- 2. Estrazione automatica dei commenti da Postgres ---")

query_commenti = """
    SELECT 
        c.table_name, 
        c.column_name, 
        pgd.description AS commento
    FROM pg_catalog.pg_statio_all_tables as st
    JOIN pg_catalog.pg_description pgd ON (pgd.objoid = st.relid)
    JOIN information_schema.columns c 
      ON (pgd.objsubid = c.ordinal_position AND c.table_name = st.relname)
    WHERE c.table_schema = 'public' 
      AND pgd.description IS NOT NULL
      AND c.table_name in ('time_dimension', 'product_dimension', 'customer_dimension', 'sale_zones_dimension', 'sale_reps_dimension', 'order_lines_dw');
"""

df_commenti = vn.run_sql(query_commenti)

for _, row in df_commenti.iterrows():
    doc_text = f"Nella tabella '{row['table_name']}', la colonna '{row['column_name']}' ha il seguente significato: {row['commento']}"
    print(f"Train Commento: {doc_text}")
    vn.train(documentation=doc_text)

print("\n--- 3. Regole di Business Generali ---")

regole_generali = [
    "Utilizzare principalmente la vista 'mis_dw' invece di fare join manuali.",
    "I sinonimi venduto e ordinato si riferiscono alla somma di mis_dw.amount e rappresentano l'importo totale netto delle vendite in Euro, IVA esclusa.",
    "Cliente utilizza customer_code per l'identificazione, customer_description per la visualizzazione.",
    "Periodo può essere filtrato tramite mis_dw.year (formato YYYY), mis_dw.order_date (data completa), mis_dw.year_and_month (formato YYYYMM), mis_dw.year_and_quarter (formato YYYYn) e mis_dw.month (formato MM).",
    "Per la visualizzazione dei mesi si possono usare mis_dw.alpha_month e mis_dw.alpha_month_short",
    "Per la visualizzazione di un trimestre si può usare mis_dw.alpha.quarter mentre per visualizzare annoe trimestre si possono concatenare mis_dw.year e mis_dw.alpha_quarter."
]

for regola in regole_generali:
    vn.train(documentation=regola)

regole_mappatura = [
    "Quando l'utente chiede 'zona di vendita', 'zona' o 'territorio', la colonna da usare nelle dimensioni o nei gruppi è sempre 'sale_zones_description'.",
    "Quando l'utente chiede 'venditore', 'rappresentante' o 'agente', la colonna da usare è sempre 'sale_reps_description'.",
    "Non confondere mai 'sale_zones_description' (zone geografiche) con 'sale_reps_description' (agenti di vendita).",
    "Quando l'utente chiede 'tipo_prodotto', la colonna da usare nelle dimensioni o nei gruppi è sempre 'category_description'.",
    "Quando l'utente chiede 'prodotto' o 'articolo' la colonna da usare nelle dimensioni o nei gruppi è sempre 'product_description'."    
]

for regola in regole_mappatura:
    vn.train(documentation=regola)    

print("\n--- 4. Coppie Domanda-SQL di Esempio (Few-Shot) ---")

vn.train(
    question="Qual è il totale venduto per ogni zona di vendita?",
    sql="""
        SELECT sale_zones_description, SUM(amount) AS totale_venduto
        FROM mis_dw
        GROUP BY sale_zones_description
        ORDER BY totale_venduto DESC;
    """
)

vn.train(
    question="Quali sono i 5 prodotti con il fatturato più alto nel 2025?",
    sql="""
        SELECT product_description, SUM(amount) AS totale_fatturato
        FROM mis_dw
        WHERE year = 2025
        GROUP BY product_description
        ORDER BY totale_fatturato DESC
        LIMIT 5;
    """
)

vn.train(
    question="Quanto ha venduto il cliente A nel 2025?",
    sql="""
        SELECT SUM(amount) FROM mis_dw WHERE customer_code = 'A' AND year = 2025;
    """
)

vn.train(
    question="Quali sono i 10 prodotti con il venduto più alto a marzo 2025?",
    sql="""
        SELECT product_description, SUM(amount) AS total 
        FROM mis_dw 
        WHERE year_and_month = 202503 
        GROUP BY product_description 
        ORDER BY total DESC LIMIT 10;
    """
)

vn.train(
    question="Mostra il totale venduto per venditore negli anni dal 2023 al 2025",
    sql="""
         SELECT sale_reps_description,
               COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0.000) AS venduto_2023,
               COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0.000) AS venduto_2024,
               COALESCE(SUM(amount) FILTER (WHERE year = 2025), 0.000) AS venduto_2025,
               SUM(amount) AS totale_periodo
          FROM mis_dw
         WHERE year BETWEEN 2023 AND 2025
         GROUP BY sale_reps_description
         ORDER BY totale_periodo DESC;    
    """
)

vn.train(
    question="Mostra il totale venduto per rappresentante negli anni dal 2023 al 2025, aggiungendo dopo ogni periodo tranne il primo, lo scostamento percentuale rispetto al periodo precedente.",
    sql="""
        SELECT sale_reps_description,
            COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0.000) AS venduto_2023,
            COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0.000) AS venduto_2024,
            CASE 
              WHEN COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0) = 0 THEN NULL
              ELSE ROUND(
                (COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0) 
                - COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0)) 
                / COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0) * 100
                , 2)
            END AS "%_2024_vs_2023",
            COALESCE(SUM(amount) FILTER (WHERE year = 2025), 0.000) AS venduto_2025,
            CASE 
              WHEN COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0) = 0 THEN NULL
                ELSE ROUND(
                  (COALESCE(SUM(amount) FILTER (WHERE year = 2025), 0) 
                  - COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0)) 
                  / COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0) * 100
                  , 2)
            END AS "%_2025_vs_2024",
            SUM(amount) AS totale_periodo
        FROM mis_dw
        WHERE year BETWEEN 2023 AND 2025
        GROUP BY sale_reps_description
        ORDER BY totale_periodo DESC;
    """
)

vn.train(
    question="Mostra il venduto per rappresentante per trimestre del 2025",
    sql="""
         SELECT sale_reps_description,
               COALESCE(SUM(amount) FILTER (WHERE year_and_quarter = 20251), 0.000) AS Trim1,
               COALESCE(SUM(amount) FILTER (WHERE year_and_quarter = 20252), 0.000) AS Trim2,
               COALESCE(SUM(amount) FILTER (WHERE year_and_quarter = 20253), 0.000) AS Trim3,
               COALESCE(SUM(amount) FILTER (WHERE year_and_quarter = 20254), 0.000) AS Trim4,
               SUM(amount) AS totale_periodo
          FROM mis_dw
         WHERE year = 2025
         GROUP BY sale_reps_description
         ORDER BY totale_periodo DESC;
    """
)

vn.train(
    question="Estrai il venduto suddiviso per zona di vendita nel periodo 2017-2019",
    sql="""
         SELECT sale_zones_description,
               COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0.000) AS venduto_2017,
               COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0.000) AS venduto_2018,
               COALESCE(SUM(amount) FILTER (WHERE year = 2025), 0.000) AS venduto_2019,
               SUM(amount) AS totale_periodo
          FROM mis_dw
         WHERE year BETWEEN 2023 AND 2025
         GROUP BY sale_zones_description
         ORDER BY totale_periodo;
    """
)

vn.train(
    question="Mostra il totale venduto per zona negli anni dal 2023 al 2025, aggiungendo dopo ogni periodo tranne il primo, lo scostamento percentuale rispetto al periodo precedente.",
    sql="""
        SELECT sale_zones_description,
            COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0.000) AS venduto_2023,
            COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0.000) AS venduto_2024,
            CASE 
              WHEN COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0) = 0 THEN NULL
              ELSE ROUND(
                (COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0) 
                - COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0)) 
                / COALESCE(SUM(amount) FILTER (WHERE year = 2023), 0) * 100
                , 2)
            END AS "%_2024_vs_2023",
            COALESCE(SUM(amount) FILTER (WHERE year = 2025), 0.000) AS venduto_2025,
            CASE 
              WHEN COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0) = 0 THEN NULL
                ELSE ROUND(
                  (COALESCE(SUM(amount) FILTER (WHERE year = 2025), 0) 
                  - COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0)) 
                  / COALESCE(SUM(amount) FILTER (WHERE year = 2024), 0) * 100
                  , 2)
            END AS "%_2025_vs_2024",
            SUM(amount) AS totale_periodo
        FROM mis_dw
        WHERE year BETWEEN 2023 AND 2025
        GROUP BY sale_zones_description
        ORDER BY totale_periodo DESC;
    """
)

print("\nAddestramento completato con successo!")
