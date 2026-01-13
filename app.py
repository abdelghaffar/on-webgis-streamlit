import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import os

# Configuration de la page
st.set_page_config(page_title="Leafmap WebGIS Demo", layout="wide")

# CSS personnalisé pour améliorer l'interface
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 Leafmap Interactive WebGIS")
st.markdown("Un clone de la plateforme de démonstration leafmap.org utilisant Streamlit.")

# --- BARRE LATÉRALE ---
st.sidebar.title("Menu Principal")
apps = [
    "🏠 Accueil", 
    "🗺️ Carte Interactive", 
    "🌓 Comparaison (Split Map)", 
    "🕒 Séries Temporelles",
    "🌍 Données OpenStreetMap"
]
choice = st.sidebar.radio("Aller vers", apps)

# --- MODULE 1 : CARTE INTERACTIVE ---
if choice == "🗺️ Carte Interactive":
    st.subheader("Visualisation et Couches")
    
    col1, col2 = st.columns([4, 1])
    
    with col2:
        basemap = st.selectbox("Fond de carte", leafmap.basemaps.keys(), index=15)
        opacity = st.slider("Opacité du Cadastre", 0.0, 1.0, 0.7)
        show_cadastre = st.checkbox("Afficher le Cadastre IGN", value=True)

    with col1:
        m = leafmap.Map(center=[48.8566, 2.3522], zoom=12)
        m.add_basemap(basemap)
        
        if show_cadastre:
            url_cadastre = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
            m.add_tile_layer(url_cadastre, name="Cadastre", opacity=opacity)
        
        m.add_layer_control()
        m.to_streamlit(height=650)

# --- MODULE 2 : SPLIT MAP ---
elif choice == "🌓 Comparaison (Split Map)":
    st.subheader("Comparateur de cartes côte à côte")
    
    col1, col2 = st.columns(2)
    with col1:
        left = st.selectbox("Carte de gauche", ["TERRAIN", "ROADMAP", "SATELLITE"])
    with col2:
        right = st.selectbox("Carte de droite", ["HYBRID", "OpenStreetMap", "Stamen.Toner"])
    
    m = leafmap.Map(center=[48.8566, 2.3522], zoom=13)
    m.split_map(left_layer=left, right_layer=right)
    m.to_streamlit(height=650)

# --- MODULE 3 : SÉRIES TEMPORELLES ---
elif choice == "🕒 Séries Temporelles":
    st.subheader("Analyse du changement (Timelapse)")
    st.info("Visualisation des données satellitaires historiques (Google Earth Engine).")
    
    m = leafmap.Map()
    # Exemple de couche Landsat historique
    m.add_basemap("HYBRID")
    m.to_streamlit(height=600)
    st.warning("Note: Pour un timelapse réel, une authentification Google Earth Engine est requise.")

# --- MODULE 4 : OPENSTREETMAP ---
elif choice == "🌍 Données OpenStreetMap":
    st.subheader("Extraction de données vectorielles")
    city = st.text_input("Entrez une ville pour extraire les bâtiments :", "Paris, France")
    
    if st.button("Extraire les données"):
        st.write(f"Recherche des bâtiments à {city}...")
        m = leafmap.Map()
        # Simulation d'affichage OSM
        m.add_osm_from_place(city, tags={"building": True}, label="Bâtiments")
        m.to_streamlit(height=600)

# --- ACCUEIL ---
else:
    st.write("Bienvenue dans votre portail WebGIS personnalisé.")
    st.image("https://leafmap.org/assets/images/leafmap-logo.png", width=200)
    st.markdown("""
    ### Fonctionnalités incluses :
    * **Moteur Folium** pour une compatibilité web totale.
    * **Gestionnaire de couches** interactif.
    * **Split-panel** pour l'analyse comparative.
    * **Intégration Flux IGN** (Cadastre).
    """)
