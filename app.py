import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import requests

# 2. CARGA DE DATOS (Lo que ya tienes)
df_app = pd.read_csv('radiohead_tracks.csv')
AUDIO_FEATURES = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence']

# 3. FILTRO LATERAL (Sidebar)
selected_album = st.sidebar.selectbox("Selecciona un Álbum:", ["Todos"] + list(df_app['album'].unique()))
display_df = df_app if selected_album == "Todos" else df_app[df_app['album'] == selected_album]

# ---------------------------------------------------------
# 4. AQUÍ VAN LOS CAMBIOS (Nuevos Gráficos)
# ---------------------------------------------------------
st.header("📊 Análisis Avanzado de Radiohead")

# Creamos las pestañas para organizar el contenido
tab1, tab2, tab3 = st.tabs(["🎯 Comparativa de Radar", "🔥 Correlaciones", "🎈 Popularidad"])

with tab1:
    st.subheader("La 'Huella' Sonora de los Álbumes")
    # Lógica del gráfico de Radar que te pasé antes...
    features_radar = ['energy', 'danceability', 'valence', 'acousticness', 'speechiness']
    df_radar = df_app.groupby('album')[features_radar].mean().reset_index()
    
    col_a, col_b = st.columns(2)
    alb1 = col_a.selectbox("Álbum A:", df_radar['album'].unique(), index=0)
    alb2 = col_b.selectbox("Álbum B:", df_radar['album'].unique(), index=2)
    
    fig_radar = go.Figure()
    for alb in [alb1, alb2]:
        fig_radar.add_trace(go.Scatterpolar(
            r=df_radar[df_radar['album'] == alb][features_radar].values.flatten(),
            theta=features_radar, fill='toself', name=alb
        ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
    st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    st.subheader("Mapa de Calor de Atributos")
    fig_corr, ax_corr = plt.subplots()
    sns.heatmap(display_df[AUDIO_FEATURES].corr(), annot=True, cmap='coolwarm', ax=ax_corr)
    st.pyplot(fig_corr)

with tab3:
    st.subheader("Hits vs. Atributos")
    fig_bubble = px.scatter(display_df, x="valence", y="energy", size="popularity", 
                            color="album", hover_name="name")
    st.plotly_chart(fig_bubble, use_container_width=True)

# ---------------------------------------------------------
# 5. SECCIÓN DE LETRAS (Al final de todo)
# ---------------------------------------------------------
st.divider()
st.header("🔍 Buscador de Letras")
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