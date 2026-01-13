import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(page_title="Expert WebGIS", layout="wide")

# --- INTERFACE ---
st.sidebar.title("Configuration")
opacite = st.sidebar.slider("Opacité du Cadastre", 0.0, 1.0, 0.6)

tab1, tab2 = st.tabs(["🗺️ Carte interactive", "📚 Informations"])

with tab1:
    # 1. Initialisation
    m = leafmap.Map(center=[48.8566, 2.3522], zoom=16)

    # 2. Ajout du fond Satellite (Google)
    m.add_tile_layer(
        url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        name="Satellite",
        attribution="Google"
    )

    # 3. Correction de l'erreur : Ajout du Cadastre IGN
    # On utilise explicitement le mot-clé 'opacity' dans add_tile_layer
    url_cadastre = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
    
    try:
        m.add_tile_layer(
            url=url_cadastre, 
            name="Cadastre (IGN)", 
            attribution="IGN-F/Géoplateforme",
            opacity=opacite,
            shown=True
        )
    except Exception as e:
        st.error(f"Erreur lors de l'ajout de la couche : {e}")

    # 4. Affichage
    m.add_layer_control()
    m.to_streamlit(height=700)
