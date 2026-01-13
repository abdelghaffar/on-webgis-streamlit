import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analyse Incendies France", layout="wide")

st.sidebar.header("📁 Configuration")
uploaded_file = st.sidebar.file_uploader("Charger le fichier data_incendies.csv", type=['csv'])

if uploaded_file is not None:
    @st.cache_data
    def load_data(file):
        # On saute les 5 premières lignes d'en-tête du fichier BDIFF
        df = pd.read_csv(file, sep=';', skiprows=5)
        
        # Conversion de la date
        df['Date de première alerte'] = pd.to_datetime(df['Date de première alerte'])
        df['Mois'] = df['Date de première alerte'].dt.month_name()
        
        # Conversion de la surface en Hectares (1 ha = 10 000 m2) pour plus de lisibilité
        df['Surface (Ha)'] = df['Surface parcourue (m2)'] / 10000
        
        return df

    df = load_data(uploaded_file)

    # --- FILTRES ---
    st.sidebar.subheader("Filtres")
    depts = st.sidebar.multiselect("Départements", options=sorted(df['Département'].unique()), default=df['Département'].unique()[:5])
    
    df_filtered = df[df['Département'].isin(depts)]

    # --- KPI ---
    st.title("🔥 Tableau de bord des Incendies")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Nombre d'incendies", len(df_filtered))
    c2.metric("Surface totale (Ha)", f"{df_filtered['Surface (Ha)'].sum():.1f}")
    c3.metric("Commune la plus touchée", df_filtered.groupby('Nom de la commune')['Surface (Ha)'].sum().idxmax())

    # --- GRAPHIQUES ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Surface brûlée par mois")
        fig_trend = px.bar(df_filtered.groupby('Mois')['Surface (Ha)'].sum().reset_index(), 
                           x='Mois', y='Surface (Ha)', color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        st.subheader("📊 Top 10 des départements (Surface)")
        top_depts = df_filtered.groupby('Département')['Surface (Ha)'].sum().nlargest(10).reset_index()
        fig_dept = px.pie(top_depts, names='Département', values='Surface (Ha)', hole=0.4)
        st.plotly_chart(fig_dept, use_container_width=True)

    # --- TABLEAU ---
    st.subheader("📋 Détails des interventions")
    st.dataframe(df_filtered[['Date de première alerte', 'Département', 'Nom de la commune', 'Surface (Ha)', 'Nature']], use_container_width=True)

else:
    st.info("Veuillez charger le fichier CSV pour extraire les indicateurs.")
