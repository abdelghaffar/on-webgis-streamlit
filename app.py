import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Mon WebGIS Professionnel", layout="wide")

st.title("🌍 Application WebGIS Complète")
st.markdown("""
Cette application permet d'analyser des données spatiales, de calculer des zones d'influence 
et de planifier des itinéraires sur des fonds de carte haute résolution.
""")

# --- BARRE LATÉRALE (SIDEBAR) ---
st.sidebar.header("🛠️ Outils & Données")

# Section 1 : Fond de carte
map_type = st.sidebar.selectbox(
    "Choisir le fond de carte",
    ["OpenStreetMap", "ROADMAP", "SATELLITE", "TERRAIN", "HYBRID"]
)

# Section 2 : Importation de données
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("Charger GeoJSON ou CSV (lat/lon)", type=['geojson', 'csv'])

# Section 3 : Analyse Spatiale
st.sidebar.markdown("---")
st.sidebar.subheader("Analyse de Zone")
buffer_dist = st.sidebar.slider("Rayon du Buffer (mètres)", 0, 5000, 1000)

# Section 4 : Itinéraire
st.sidebar.markdown("---")
st.sidebar.subheader("Calcul d'itinéraire")
start = st.sidebar.text_input("Point de départ", "")
end = st.sidebar.text_input("Destination", "")
btn_route = st.sidebar.button("Tracer le trajet")

# --- LOGIQUE DE LA CARTE ---

# Initialisation de l'objet carte
m = leafmap.Map(center=[46.603354, 1.888334], zoom=5) # Centré sur la France
m.add_basemap(map_type)

# Traitement des données importées
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        # On suppose que le CSV a des colonnes 'latitude' et 'longitude'
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
    else:
        gdf = gpd.read_file(uploaded_file)

    # Création du Buffer (Conversion en mètres EPSG:3857 puis retour en 4326)
    gdf_buffer = gdf.to_crs(epsg=3857).buffer(buffer_dist).to_crs(epsg=4326)
    
    # Ajout à la carte
    m.add_gdf(gdf, layer_name="Mes Points", info_mode='on_click')
    m.add_gdf(gpd.GeoDataFrame(geometry=gdf_buffer), layer_name="Zone Tampon", style={'color': 'red', 'fillOpacity': 0.2})
    
    st.sidebar.success(f"✅ {len(gdf)} entités chargées")

# Traitement de l'itinéraire
if btn_route and start and end:
    try:
        m.add_route(start, end, route_type="drive", layer_name="Itinéraire")
        st.sidebar.success("✅ Itinéraire trouvé !")
    except:
        st.sidebar.error("❌ Lieu non trouvé. Soyez plus précis.")

# --- AFFICHAGE FINAL ---
col1, col2 = st.columns([4, 1])

with col1:
    # Affichage de la carte
    m.to_streamlit(height=700)

with col2:
    st.info("💡 **Astuce** : Utilisez les outils de dessin à gauche de la carte pour mesurer des distances ou dessiner des polygones.")
    if uploaded_file is not None:
        st.write("Aperçu des données :")
        st.dataframe(gdf.drop(columns='geometry').head(10))