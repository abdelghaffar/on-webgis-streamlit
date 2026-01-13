import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Configuration de la page
st.set_page_config(page_title="Analyse Incendies France", layout="wide", page_icon="🔥")

# --- FONCTION : CHARGEMENT DU RÉFÉRENTIEL GÉO ---
@st.cache_data
def load_geo_data():
    """Charge les coordonnées GPS des communes françaises pour la cartographie"""
    # Utilisation d'un export de data.gouv (Code INSEE, Lat, Lon)
    url = "https://www.data.gouv.fr/fr/datasets/r/dbe8b394-4ae1-4940-aa2a-360749008f1b"
    try:
        geo = pd.read_csv(url, sep=',', usecols=['code_commune_insee', 'latitude', 'longitude'])
        # On s'assure que le code INSEE est sur 5 caractères (ex: 01001)
        geo['code_commune_insee'] = geo['code_commune_insee'].astype(str).str.zfill(5)
        return geo
    except:
        st.error("Erreur lors du chargement des données géographiques.")
        return pd.DataFrame()

# --- FONCTION : TRAITEMENT DES DONNÉES INCENDIES ---
@st.cache_data
def process_data(file):
    """Nettoie et enrichit les données du fichier CSV BDIFF"""
    # Lecture en sautant les 5 lignes de métadonnées du fichier
    df = pd.read_csv(file, sep=';', skiprows=5)
    
    # 1. Nettoyage des colonnes
    df['Date de première alerte'] = pd.to_datetime(df['Date de première alerte'])
    df['Mois'] = df['Date de première alerte'].dt.month
    df['Nom_Mois'] = df['Date de première alerte'].dt.strftime('%m - %B')
    df['Surface (Ha)'] = df['Surface parcourue (m2)'] / 10000
    
    # 2. Préparation Code INSEE pour la jointure
    df['Code INSEE'] = df['Code INSEE'].astype(str).str.zfill(5)
    
    # 3. Fusion avec les coordonnées GPS
    geo_df = load_geo_data()
    if not geo_df.empty:
        df = pd.merge(df, geo_df, left_on='Code INSEE', right_on='code_commune_insee', how='left')
    
    return df

# --- INTERFACE UTILISATEUR ---
st.title("🔥 Tableau de Bord Interactif des Incendies")
st.markdown("Analyse basée sur les données de la base **BDIFF**.")

# Barre latérale : Chargement
st.sidebar.header("📁 Importation")
uploaded_file = st.sidebar.file_uploader("Charger 'data_incendies.csv'", type=['csv'])

if uploaded_file:
    # Traitement
    data = process_data(uploaded_file)
    
    # Barre latérale : Filtres
    st.sidebar.header("🔍 Filtres")
    
    all_depts = sorted(data['Département'].unique().tolist())
    selected_depts = st.sidebar.multiselect("Départements", options=all_depts, default=all_depts[:5])
    
    min_surface = st.sidebar.slider("Surface minimale (Ha)", 0.0, float(data['Surface (Ha)'].max()), 0.0)
    
    # Filtrage effectif
    mask = (data['Département'].isin(selected_depts)) & (data['Surface (Ha)'] >= min_surface)
    df_filtered = data[mask]

    # --- AFFICHAGE DES KPI ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nb Incendies", f"{len(df_filtered)}")
    with col2:
        st.metric("Surface Totale (Ha)", f"{df_filtered['Surface (Ha)'].sum():.1f}")
    with col3:
        st.metric("Surface Moyenne (Ha)", f"{df_filtered['Surface (Ha)'].mean():.2f}")
    with col4:
        st.metric("Max enregistré (Ha)", f"{df_filtered['Surface (Ha)'].max():.1f}")

    st.divider()

    # --- CARTOGRAPHIE ET TENDANCES ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📍 Localisation des départs de feux")
        if not df_filtered.dropna(subset=['latitude']).empty:
            fig_map = px.scatter_mapbox(
                df_filtered, 
                lat="latitude", 
                lon="longitude", 
                size="Surface (Ha)", 
                color="Surface (Ha)",
                hover_name="Nom de la commune",
                hover_data={"Surface (Ha)": ':.2f', "Nature": True, "latitude": False, "longitude": False},
                color_continuous_scale=px.colors.sequential.YlOrRd,
                zoom=5, 
                height=600,
                mapbox_style="carto-positron"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Aucune coordonnée GPS trouvée pour ces filtres.")

    with col_right:
        st.subheader("📊 Répartition par Nature")
        fig_pie = px.pie(df_filtered, names='Nature', values='Surface (Ha)', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- GRAPHIQUE TEMPOREL ---
    st.subheader("📈 Évolution mensuelle des surfaces brûlées")
    temp_data = df_filtered.groupby('Nom_Mois')['Surface (Ha)'].sum().reset_index()
    fig_line = px.bar(temp_data, x='Nom_Mois', y='Surface (Ha)', 
                      labels={'Nom_Mois': 'Mois', 'Surface (Ha)': 'Total Hectares'},
                      color_discrete_sequence=['#e63946'])
    st.plotly_chart(fig_line, use_container_width=True)

    # --- DATA TABLE ---
    with st.expander("🔎 Voir le détail des données filtrées"):
        st.dataframe(df_filtered[['Année', 'Département', 'Nom de la commune', 'Surface (Ha)', 'Nature', 'Date de première alerte']], use_container_width=True)

else:
    # Message si pas de fichier
    st.info("💡 Veuillez glisser-déposer votre fichier CSV dans la barre latérale pour activer l'analyse.")
    st.image("https://www.bdiff.fr/static/img/logo_bdiff.png", width=200) # Logo BDIFF pour le contexte
