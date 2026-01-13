import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analyse Incendies BDIFF", layout="wide")

@st.cache_data
def load_geo_data():
    """Référentiel des communes pour les coordonnées GPS"""
    url = "https://www.data.gouv.fr/fr/datasets/r/dbe8b394-4ae1-4940-aa2a-360749008f1b"
    try:
        geo = pd.read_csv(url, sep=',', usecols=['code_commune_insee', 'latitude', 'longitude'])
        geo['code_commune_insee'] = geo['code_commune_insee'].astype(str).str.zfill(5)
        return geo
    except:
        return pd.DataFrame()

@st.cache_data
def process_data(file):
    """Traitement spécifique pour votre fichier data_incendies.csv"""
    # CORRECTION : skiprows=2 car il y a 2 lignes de texte avant les colonnes
    # AJOUT : encoding='latin-1' pour gérer les accents
    df = pd.read_csv(file, sep=';', skiprows=2, encoding='latin-1')
    
    # Nettoyage des noms de colonnes (suppression des guillemets et espaces)
    df.columns = df.columns.str.replace('"', '').str.strip()
    
    # Conversion date
    df['Date de première alerte'] = pd.to_datetime(df['Date de première alerte'])
    df['Surface (Ha)'] = df['Surface parcourue (m2)'] / 10000
    df['Code INSEE'] = df['Code INSEE'].astype(str).str.zfill(5)
    
    # Jointure Géo
    geo_df = load_geo_data()
    if not geo_df.empty:
        df = pd.merge(df, geo_df, left_on='Code INSEE', right_on='code_commune_insee', how='left')
    
    return df

st.title("🔥 Dashboard Incendies")

uploaded_file = st.sidebar.file_uploader("Charger le fichier CSV", type=['csv'])

if uploaded_file:
    try:
        data = process_data(uploaded_file)
        
        # Filtres
        depts = st.sidebar.multiselect("Départements", options=sorted(data['Département'].unique()))
        df_filtered = data[data['Département'].isin(depts)] if depts else data

        # KPI
        c1, c2 = st.columns(2)
        c1.metric("Nombre d'incendies", len(df_filtered))
        c2.metric("Surface totale (Ha)", f"{df_filtered['Surface (Ha)'].sum():.1f}")

        # Carte
        st.subheader("📍 Carte des incidents")
        fig_map = px.scatter_mapbox(
            df_filtered, lat="latitude", lon="longitude", size="Surface (Ha)",
            color="Surface (Ha)", hover_name="Nom de la commune",
            mapbox_style="carto-positron", zoom=5, height=500
        )
        st.plotly_chart(fig_map, use_container_width=True)

        st.dataframe(df_filtered.head())
        
    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
        st.info("Vérifiez que le fichier est bien au format BDIFF (séparateur point-virgule).")
else:
    st.info("En attente du fichier...")
