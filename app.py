import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(page_title="Dashboard Incendies", layout="wide")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    # Simulation de chargement - Remplacez par pd.read_csv("votre_fichier.csv")
    df = pd.read_csv("data_incendies.csv", parse_dates=['date'])
    df['année'] = df['date'].dt.year
    df['mois'] = df['date'].dt.month
    return df

try:
    df = load_data()
except:
    st.error("Veuillez charger un fichier 'data_incendies.csv'")
    st.stop()

# --- BARRE LATÉRALE (FILTRES) ---
st.sidebar.header("Filtres interactifs")
regions = st.sidebar.multiselect("Sélectionnez les régions", options=df['region'].unique(), default=df['region'].unique())
annee_range = st.sidebar.slider("Période", int(df['année'].min()), int(df['année'].max()), (2015, 2023))

# Filtrage du dataframe
df_filtered = df[(df['region'].isin(regions)) & (df['année'].between(annee_range[0], annee_range[1]))]

# --- ENTÊTE ET KPI ---
st.title("🔥 Exploration des Incendies de Forêt")

col1, col2, col3 = st.columns(3)
col1.metric("Total Incendies", len(df_filtered))
col2.metric("Surface Totale (Ha)", f"{df_filtered['surface'].sum():,.0f}")
col3.metric("Surface Moyenne", f"{df_filtered['surface'].mean():.2f}")

st.divider()

# --- VISUALISATIONS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Tendances Temporelles")
    df_trend = df_filtered.groupby('année').size().reset_index(name='nombre')
    fig_trend = px.line(df_trend, x='année', y='nombre', title="Nombre d'incendies par an")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.subheader("🗺️ Cartographie des Zones")
    # Utilisation de Plotly pour une carte rapide ou Folium pour plus de détails
    fig_map = px.scatter_mapbox(df_filtered, lat="latitude", lon="longitude", size="surface", 
                                color="surface", color_continuous_scale=px.colors.sequential.YlOrRd,
                                zoom=4, mapbox_style="carto-positron")
    st.plotly_chart(fig_map, use_container_width=True)

# --- EXPLORATION DES DONNÉES ---
st.subheader("🔍 Données Brutes")
st.dataframe(df_filtered, use_container_width=True)
