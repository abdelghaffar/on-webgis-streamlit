import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(page_title="WebGIS Cadastre", layout="wide")

st.title("🗺️ WebGIS avec Cadastre IGN")

# --- ONGLETS ---
tab1, tab2 = st.tabs(["🗺️ Carte", "🖼️ Fond de carte"])

with tab2:
    st.subheader("Options de fond")
    choix_fond = st.selectbox(
        "Choisir la couche :", 
        ["OpenStreetMap", "Satellite (Google)", "Plan Cadastral (IGN)", "Parcelles (IGN)"]
    )

with tab1:
    # Initialisation de la carte
    m = leafmap.Map(center=[48.8566, 2.3522], zoom=15)

    # Logique pour le fond de carte
    if choix_fond == "OpenStreetMap":
        m.add_basemap("OpenStreetMap")
    
    elif choix_fond == "Satellite (Google)":
        m.add_basemap("SATELLITE")

    elif choix_fond == "Plan Cadastral (IGN)":
        # Utilisation du flux WMTS officiel de l'IGN pour le Plan Cadastral
        url_ign = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
        m.add_tile_layer(url=url_ign, name="Cadastre IGN", attribution="IGN-F/Géoplateforme")

    elif choix_fond == "Parcelles (IGN)":
        # Variante : seulement les bordures de parcelles (souvent utile en superposition)
        url_parcelles = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=CADASTRALPARCELS.PARCELS&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
        m.add_tile_layer(url=url_parcelles, name="Parcelles", attribution="IGN-F/Géoplateforme")

    # Affichage de la carte
    m.to_streamlit(height=700)
