import streamlit as st
import leafmap.foliumap as leafmap  # Backend principal compatible Streamlit
import leafmap.colormaps as cm
import leafmap.legends as legends
import pandas as pd

st.set_page_config(page_title="Multi-Module WebGIS", layout="wide")

st.title("🛠️ WebGIS Full-Stack avec Leafmap")

# --- BARRE LATÉRALE : SÉLECTION DES MODULES ---
st.sidebar.title("Modules & Outils")

# 1. Module : Basemaps & Backends
backend = st.sidebar.selectbox(
    "Choisir le Backend (Moteur)", 
    ["folium", "kepler", "plotly", "pydeck"]
)

# 2. Module : OSM (Recherche de données)
st.sidebar.subheader("🌍 Données OpenStreetMap")
place_query = st.sidebar.text_input("Rechercher un lieu (ex: Paris, France)", "")

# 3. Module : Colormaps & Legends
st.sidebar.subheader("🎨 Visualisation")
color_palette = st.sidebar.selectbox("Palette de couleurs (Colormaps)", cm.list_colormaps())

# --- INTERFACE PRINCIPALE (ONGLETS) ---
tab_map, tab_tools, tab_settings = st.tabs(["🗺️ Carte", "🛠️ Outils SIG", "⚙️ Fond & Opacité"])

with tab_settings:
    st.subheader("Réglages des couches")
    opacite = st.slider("Opacité globale", 0.0, 1.0, 0.7)

with tab_map:
    # Initialisation selon le backend choisi
    if backend == "folium":
        m = leafmap.Map(center=[48.8566, 2.3522], zoom=12)
        
        # Ajout du fond Cadastre IGN via module WMS/XYZ
        url_cadastre = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
        m.add_tile_layer(url_cadastre, name="Cadastre (IGN)", opacity=opacite)
        
        # Ajout d'une légende via le module legends
        m.add_legend(title="Légende", builtin_legend='NLCD')
        
        # Affichage
        m.to_streamlit(height=700)
    
    elif backend == "kepler":
        st.info("Utilisation du module Kepler.gl pour les données massives.")
        m = leafmap.Map(backend="kepler")
        m.to_streamlit(height=700)

with tab_tools:
    st.subheader("Analyse de données")
    # Simulation du module OSM pour télécharger des données
    if place_query:
        st.write(f"Extraction des données OSM pour : {place_query}")
        # En production : gdf = leafmap.osm_gdf_from_place(place_query, tags={"amenity": "restaurant"})
        st.info("Module 'osm' prêt pour l'extraction vectorielle.")
