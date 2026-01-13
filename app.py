import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analyse Incendies BDIFF", layout="wide")

@st.cache_data
def load_geo_data():
    """Récupère les coordonnées GPS des communes françaises"""
    url = "https://www.data.gouv.fr/fr/datasets/r/dbe8b394-4ae1-4940-aa2a-360749008f1b"
    try:
        geo = pd.read_csv(url, sep=',', usecols=['code_commune_insee', 'latitude', 'longitude'])
        geo['code_commune_insee'] = geo['code_commune_insee'].astype(str).str.zfill(5)
        return geo
    except:
        return pd.DataFrame()

@st.cache_data
def process_data(file):
    # 1. Chargement : on saute les 2 premières lignes de texte
    # On ajoute quoting=1 ou on nettoie après pour enlever les guillemets (")
    df = pd.read_csv(file, sep=';', skiprows=2, encoding='utf-8')
    
    # 2. Nettoyage crucial des noms de colonnes
    # Cette ligne enlève les guillemets et les espaces invisibles autour des noms
    df.columns = [c.replace('"', '').strip() for c in df.columns]
    
    # 3. Conversion de la date (le nom doit être propre maintenant)
    df['Date de première alerte'] = pd.to_datetime(df['Date de première alerte'])
    df['Mois'] = df['Date de première alerte'].dt.month
    
    # 4. Calcul de la surface en Hectares
    df['Surface (Ha)'] = df['Surface parcourue (m2)'] / 10000
    
    # 5. Préparation Code INSEE pour jointure géo
    df['Code INSEE'] = df['Code INSEE'].astype(str).str.replace('"', '').str.zfill(5)
    
    geo_df = load_geo_data()
    if not geo_df.empty:
        df = pd.merge(df, geo_df, left_on='Code INSEE', right_on='code_commune_insee', how='left')
    
    return df

st.title("🔥 Dashboard Incendies (BDIFF)")

uploaded_file = st.sidebar.file_uploader("Charger le fichier data_incendies.csv", type=['csv'])

if uploaded_file:
    try:
        data = process_data(uploaded_file)
        
        # Sidebar - Filtres
        depts = st.sidebar.multiselect("Filtrer par Département", options=sorted(data['Département'].unique()))
        df_filtered = data[data['Département'].isin(depts)] if depts else data

        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("Nombre d'incendies", len(df_filtered))
        c2.metric("Surface totale (Ha)", f"{df_filtered['Surface (Ha)'].sum():.1f}")
        c3.metric("Moyenne (Ha)", f"{df_filtered['Surface (Ha)'].mean():.2f}")

        # Carte
        st.subheader("📍 Cartographie des incidents")
        if 'latitude' in df_filtered.columns:
            fig_map = px.scatter_mapbox(
                df_filtered, lat="latitude", lon="longitude", size="Surface (Ha)",
                color="Surface (Ha)", hover_name="Nom de la commune",
                mapbox_style="carto-positron", zoom=5, height=500
            )
            st.plotly_chart(fig_map, use_container_width=True)

        # Tableau
        st.subheader("📋 Liste des interventions")
        st.dataframe(df_filtered[['Année', 'Département', 'Nom de la commune', 'Surface (Ha)', 'Nature']])
        
    except Exception as e:
        st.error(f"Erreur d'analyse : {e}")
        # Affiche les colonnes réellement détectées pour déboguer
        if 'df' in locals() or 'data' in locals():
            st.write("Colonnes détectées dans votre fichier :", df.columns.tolist() if 'df' in locals() else data.columns.tolist())
else:
    st.info("Veuillez charger le fichier CSV.")
