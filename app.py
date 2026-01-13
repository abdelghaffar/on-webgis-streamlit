import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Analyse Incendies BDIFF", layout="wide", page_icon="🔥")

# --- CHARGEMENT DU RÉFÉRENTIEL GÉO ---
@st.cache_data
def load_geo_data():
    """Récupère les coordonnées GPS des communes (Data.gouv)"""
    url = "https://www.data.gouv.fr/fr/datasets/r/dbe8b394-4ae1-4940-aa2a-360749008f1b"
    try:
        geo = pd.read_csv(url, sep=',', usecols=['code_commune_insee', 'latitude', 'longitude'])
        geo['code_commune_insee'] = geo['code_commune_insee'].astype(str).str.zfill(5)
        return geo
    except:
        return pd.DataFrame()

# --- FONCTION DE TRAITEMENT DES DONNÉES ---
@st.cache_data
def process_data(file):
    # 1. Lecture : on saute les 2 premières lignes de texte de BDIFF
    df = pd.read_csv(file, sep=';', skiprows=2, encoding='utf-8')
    
    # 2. Nettoyage des noms de colonnes (enlève les " et les espaces)
    df.columns = [c.replace('"', '').strip() for c in df.columns]
    
    # 3. Nettoyage des données (certaines valeurs comme le Code INSEE ont des " internes)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.replace('"', '').strip()

    # 4. Conversions types
    df['Date de première alerte'] = pd.to_datetime(df['Date de première alerte'], errors='coerce')
    df['Surface (Ha)'] = pd.to_numeric(df['Surface parcourue (m2)'], errors='coerce') / 10000
    df['Code INSEE'] = df['Code INSEE'].str.zfill(5)
    
    # 5. Enrichissement Géographique
    geo_df = load_geo_data()
    if not geo_df.empty:
        df = pd.merge(df, geo_df, left_on='Code INSEE', right_on='code_commune_insee', how='left')
    
    return df

# --- INTERFACE STREAMLIT ---
st.title("🔥 Tableau de bord des Incendies (Format BDIFF)")

uploaded_file = st.sidebar.file_uploader("Charger 'data_incendies.csv'", type=['csv'])

if uploaded_file:
    try:
        data = process_data(uploaded_file)
        
        # --- FILTRES ---
        st.sidebar.header("🔍 Filtres")
        
        # Filtre Département
        all_depts = sorted(data['Département'].unique().tolist())
        selected_depts = st.sidebar.multiselect("Départements", options=all_depts, default=all_depts[:10])
        
        # Filtre Nature
        all_natures = sorted(data['Nature'].unique().tolist())
        selected_natures = st.sidebar.multiselect("Nature du feu", options=all_natures, default=all_natures)

        # Application des filtres
        mask = (data['Département'].isin(selected_depts)) & (data['Nature'].isin(selected_natures))
        df_filtered = data[mask]

        # --- AFFICHAGE DES KPI ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre d'incendies", f"{len(df_filtered)}")
        col2.metric("Surface Totale (Ha)", f"{df_filtered['Surface (Ha)'].sum():.1f}")
        col3.metric("Surface Moyenne (Ha)", f"{df_filtered['Surface (Ha)'].mean():.2f}")

        st.divider()

        # --- CARTOGRAPHIE ET GRAPHIQUE ---
        row1_col1, row1_col2 = st.columns([2, 1])

        with row1_col1:
            st.subheader("📍 Localisation des départs de feux")
            if not df_filtered.dropna(subset=['latitude']).empty:
                fig_map = px.scatter_mapbox(
                    df_filtered, 
                    lat="latitude", lon="longitude", 
                    size="Surface (Ha)", color="Surface (Ha)",
                    hover_name="Nom de la commune",
                    hover_data=["Date de première alerte", "Nature"],
                    color_continuous_scale=px.colors.sequential.YlOrRd,
                    zoom=5, height=500, mapbox_style="carto-positron"
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("Coordonnées GPS non disponibles pour cette sélection.")

        with row1_col2:
            st.subheader("📊 Répartition par Nature")
            fig_pie = px.pie(df_filtered, names='Nature', values='Surface (Ha)', hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- TENDANCE TEMPORELLE ---
        st.subheader("📈 Évolution des surfaces brûlées (par mois)")
        df_filtered['Mois'] = df_filtered['Date de première alerte'].dt.month
        temp_trend = df_filtered.groupby('Mois')['Surface (Ha)'].sum().reset_index()
        fig_trend = px.bar(temp_trend, x='Mois', y='Surface (Ha)', color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig_trend, use_container_width=True)

        # --- DONNÉES BRUTES ---
        with st.expander("🔎 Voir le tableau détaillé"):
            st.dataframe(df_filtered[['Année', 'Département', 'Nom de la commune', 'Date de première alerte', 'Surface (Ha)', 'Nature']])

    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
        st.info("Vérifiez que vous avez bien chargé le fichier exporté de BDIFF.")

else:
    st.info("👋 Veuillez charger votre fichier CSV dans la barre latérale pour commencer.")
    st.markdown("""
    **Format attendu :**
    - Séparateur : `;`
    - En-tête : Les 2 premières lignes sont sautées.
    - Colonnes requises : `Département`, `Date de première alerte`, `Surface parcourue (m2)`.
    """)
