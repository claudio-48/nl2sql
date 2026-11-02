import streamlit as st
import pandas as pd
import plotly.express as px
from app_poc import vn

st.set_page_config(page_title="NL2SQL Assistant - DW Vendite", layout="wide")

st.title("📊 Assistant NL2SQL - Analisi Vendite")
st.caption("Interfaccia di interrogazione in linguaggio naturale con memoria conversazionale")

# 1. Inizializzazione della cronologia chat nella sessione
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra i messaggi precedenti a schermo quando si ricarica la pagina
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql" in message:
            st.code(message["sql"], language="sql")
        if "df" in message and not message["df"].empty:
            st.dataframe(message["df"], use_container_width=True, height=300)

# 2. Input della nuova domanda utente
user_query = st.chat_input("Fai una domanda sui dati di vendita (es. Fatturato per zona nel 2025)...")

if user_query:
    # Salva e mostra la domanda dell'utente
    st.chat_message("user").write(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        # Costruzione del prompt contestuale (Memoria degli ultimi scambi)
        # Se ci sono messaggi precedenti, uniamo l'intento per dare contesto
        context_query = user_query
        if len(st.session_state.messages) > 2:
            # Prende l'ultima domanda precedente per dare continuità
            prev_query = st.session_state.messages[-3]["content"]
            context_query = f"Contesto precedente: '{prev_query}'. Nuova richiesta: '{user_query}'"

        with st.spinner("Generazione SQL in corso..."):
            sql = vn.generate_sql(context_query)
        
        st.markdown("**Query SQL Generata:**")
        st.code(sql, language="sql")
        
        with st.spinner("Esecuzione query su Postgres..."):
            try:
                df = vn.run_sql(sql)
                st.markdown("**Risultato:**")
                st.dataframe(df, use_container_width=True, height=400)
                st.caption(f"Righe restituite: {len(df)}")
                
                # Controllo sul limite delle righe per il grafico (max 8 righe)
                if not df.empty and len(df.columns) >= 2:
                    if len(df) <= 8:
                        col_categoria = df.columns[0]
                        colonne_valore = df.columns[1:]
                        
                        if len(df.columns) > 2:
                            df_melted = df.melt(
                                id_vars=[col_categoria], 
                                value_vars=colonne_valore, 
                                var_name='Metrica', 
                                value_name='Valore'
                            )
                            fig = px.bar(df_melted, x=col_categoria, y='Valore', color='Metrica', barmode='group', title=f"Analisi: {user_query}")
                        else:
                            fig = px.bar(df, x=col_categoria, y=df.columns[1], title=f"Analisi: {user_query}", text_auto='.2s')
                        
                        fig.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("💡 Grafico disabilitato: il set di risultati supera le 20 righe. Fai riferimento alla tabella sopra.")
                
                # Salvataggio nella cronologia di sessione
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Ecco i risultati per: *{user_query}*",
                    "sql": sql,
                    "df": df
                })
                
            except Exception as e:
                st.error(f"Errore durante l'esecuzione della query SQL: {e}")
