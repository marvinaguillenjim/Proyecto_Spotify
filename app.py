import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Configuración de la página
st.set_page_config(page_title="Radiohead Data Explorer", layout="wide")

st.title("🎵 Radiohead: Studio Album Analysis")
st.markdown("""
Esta aplicación permite explorar las características musicales de los álbumes de estudio de Radiohead 
y analizar sus letras mediante la API de `lyrics.ovh`.
""")

# 1. CARGA DE DATOS (Asegúrate de tener el CSV en la misma carpeta)
@st.cache_data
def load_data():
    # Aquí cargamos el dataset que usaste en Colab
    df = pd.read_csv('radiohead_tracks.csv')
    # PUNTO 1: FILTRADO DE ÁLBUMES DE ESTUDIO
    TARGET_ARTIST_ID = '4Z8W4fKeB5YxbusRsdQVPb'
    STUDIO_ALBUMS = [
        "Pablo Honey", "The Bends", "OK Computer", "Kid A", 
        "Amnesiac", "Hail to the Thief", "In Rainbows", 
        "The King of Limbs", "A Moon Shaped Pool"
    ]
    
    # Filtro por artista (Radiohead)
    df_radiohead = df[df['artist_ids'].str.contains(TARGET_ARTIST_ID)].copy()
    # Filtro por álbumes de estudio
    df_radiohead = df_radiohead[df_radiohead['album'].isin(STUDIO_ALBUMS)]
    
    return df_radiohead

try:
    df_app = load_data()

    # --- SIDEBAR (Interactividad) ---
    st.sidebar.header("Configuración")
    album_list = ["Todos"] + list(df_app['album'].unique())
    selected_album = st.sidebar.selectbox("Selecciona un Álbum:", album_list)

    if selected_album != "Todos":
        display_df = df_app[df_app['album'] == selected_album]
    else:
        display_df = df_app

    # --- VISUALIZACIÓN (Punto 2 y 3) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Energía vs. Valencia")
        fig, ax = plt.subplots()
        sns.scatterplot(data=display_df, x='valence', y='energy', hue='album', ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("Distribución de Acústica")
        fig2, ax2 = plt.subplots()
        sns.boxplot(data=display_df, x='album', y='acousticness', ax=ax2)
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    # --- ANÁLISIS DE LETRAS (Punto 2) ---
    st.divider()
    st.header("🔍 Explorador de Letras (lyrics.ovh)")
    
    song_col, lyric_col = st.columns([1, 2])
    
    with song_col:
        target_song = st.selectbox("Elige una canción:", display_df['name'].unique())
    
    if st.button("Obtener Letra"):
        with st.spinner('Buscando letra...'):
            r = requests.get(f"https://api.lyrics.ovh/v1/Radiohead/{target_song}")
            if r.status_code == 200:
                lyrics = r.json().get('lyrics', 'No encontrada')
                st.text_area("Letra:", lyrics, height=300)
                # Un pequeño gráfico rápido de longitud de letra
                st.info(f"Longitud de la letra: {len(lyrics)} caracteres.")
            else:
                st.error("No se pudo obtener la letra para esta canción.")

except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo 'tracks_features.csv'. Asegúrate de subirlo.")