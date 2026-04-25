import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import requests

# ── DEBE SER LA PRIMERA LLAMADA A STREAMLIT ──────────────────────────────────
st.set_page_config(page_title="Radiohead Data Explorer", layout="wide")

# ── CARGA DE DATOS ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('radiohead_tracks.csv')
    STUDIO_ALBUMS = [
        "Pablo Honey", "The Bends", "OK Computer", "Kid A",
        "Amnesiac", "Hail to the Thief", "In Rainbows",
        "The King of Limbs", "A Moon Shaped Pool"
    ]
    # Filtrar solo álbumes de estudio
    df = df[df['album'].isin(STUDIO_ALBUMS)].copy()
    return df

try:
    df_app = load_data()
except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo 'radiohead_tracks.csv'. Asegúrate de subirlo.")
    st.stop()

AUDIO_FEATURES = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                  'liveness', 'loudness', 'speechiness', 'tempo', 'valence']

# ── TÍTULO ────────────────────────────────────────────────────────────────────
st.title("🎵 Radiohead: Studio Album Analysis")
st.markdown("Explora las características musicales de los **9 álbumes de estudio** de Radiohead y sus letras.")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Configuración")
album_list = ["Todos"] + list(df_app['album'].unique())
selected_album = st.sidebar.selectbox("Selecciona un Álbum:", album_list)

display_df = df_app if selected_album == "Todos" else df_app[df_app['album'] == selected_album]

# ── PESTAÑAS PRINCIPALES ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Radar por Álbum",
    "🔥 Correlaciones",
    "🎈 Energía vs Valencia",
    "🔍 Letras"
])

# ── TAB 1: RADAR ──────────────────────────────────────────────────────────────
with tab1:
    st.subheader("La 'Huella' Sonora de los Álbumes")
    st.markdown("Compara las características de dos álbumes en un gráfico de radar.")

    features_radar = ['energy', 'danceability', 'valence', 'acousticness', 'speechiness']
    df_radar = df_app.groupby('album')[features_radar].mean().reset_index()
    albums_available = df_radar['album'].unique()

    col_a, col_b = st.columns(2)
    alb1 = col_a.selectbox("Álbum A:", albums_available, index=0)
    alb2 = col_b.selectbox("Álbum B:", albums_available, index=min(2, len(albums_available)-1))

    fig_radar = go.Figure()
    for alb in [alb1, alb2]:
        vals = df_radar[df_radar['album'] == alb][features_radar].values.flatten().tolist()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=features_radar, fill='toself', name=alb
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ── TAB 2: CORRELACIONES ──────────────────────────────────────────────────────
with tab2:
    st.subheader("Mapa de Calor de Correlaciones")
    st.markdown("Correlación entre los atributos de audio del álbum seleccionado.")

    fig_corr, ax_corr = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        display_df[AUDIO_FEATURES].corr(),
        annot=True, fmt='.2f', cmap='coolwarm',
        ax=ax_corr, linewidths=0.5
    )
    ax_corr.set_title(f'Correlaciones — {selected_album}', fontsize=12)
    plt.tight_layout()
    st.pyplot(fig_corr)

# ── TAB 3: SCATTER ────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Energía vs Valencia por canción")
    st.markdown("Cada punto es una canción. Pasa el ratón para ver el nombre.")

    fig_bubble = px.scatter(
        display_df,
        x="valence", y="energy",
        color="album",
        hover_name="name",
        title=f"Energía vs Valencia — {selected_album}"
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

    # Scatter adicional con seaborn
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Distribución de Acousticness por álbum**")
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        sns.boxplot(data=display_df, x='album', y='acousticness',
                    palette='tab10', ax=ax2)
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig2)

    with col2:
        st.markdown("**Energía media por álbum**")
        energy_mean = (
            df_app.groupby('album')['energy'].mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        sns.barplot(data=energy_mean, x='energy', y='album',
                    palette='viridis', ax=ax3)
        ax3.set_xlabel('Energía media')
        ax3.set_ylabel('')
        plt.tight_layout()
        st.pyplot(fig3)

# ── TAB 4: LETRAS ─────────────────────────────────────────────────────────────
with tab4:
    st.subheader("🔍 Explorador de Letras (lyrics.ovh)")
    st.markdown("Busca la letra de cualquier canción de Radiohead.")

    song_col, info_col = st.columns([1, 2])

    with song_col:
        target_song = st.selectbox(
            "Elige una canción:",
            display_df['name'].unique()
        )
        search_btn = st.button("🎵 Obtener Letra")

    with info_col:
        if search_btn:
            with st.spinner('Buscando letra en lyrics.ovh...'):
                try:
                    r = requests.get(
                        f"https://api.lyrics.ovh/v1/Radiohead/{target_song}",
                        timeout=8
                    )
                    if r.status_code == 200:
                        lyrics = r.json().get('lyrics', '')
                        if lyrics:
                            st.success(f"✅ Letra encontrada ({len(lyrics)} caracteres)")
                            st.text_area("Letra:", lyrics, height=350)
                        else:
                            st.warning("Letra no disponible para esta canción.")
                    else:
                        st.error("No se encontró la letra. Prueba con otra canción.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

st.markdown("---")
st.caption("Datos: Spotify · Letras: lyrics.ovh · App: Streamlit")