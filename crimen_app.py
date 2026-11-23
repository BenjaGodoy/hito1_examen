# crimen_app.py
# ============================================================
#  DASHBOARD — Crimen en Los Ángeles: ¿dónde, cuándo y qué ocurre?
#  Examen final · Hito 1 · versión beta 2.1.0
#  Felipe Farías · Benjamín Godoy — Visualización de la Información, UDD
#  Ejecutar:  streamlit run crimen_app.py
#
#  Misma estructura que tips_app.py: el script se ejecuta de ARRIBA
#  A ABAJO cada vez que el usuario mueve un filtro.
# ============================================================

import pandas as pd
import plotly.express as px
import streamlit as st

# ── 1. CONFIGURACIÓN DE LA PÁGINA ────────────────────────────
st.set_page_config(
    page_title="Crimen en Los Ángeles",
    page_icon="🚓",
    layout="wide",
)

# ── 2. PALETA DE COLORES Y ESTILO COMPARTIDO ─────────────────
# La misma categoría tiene siempre el mismo color en todos los gráficos.
COLOR_GRAVEDAD = {"Grave": "#B9544A", "Otros": "#3A3E48"}
COLOR_SEXO     = {"Mujer": "#D4877A", "Hombre": "#3A3E48", "Desconocido": "#E8C79A"}
COLOR_ARMA     = {"Con arma": "#B9544A", "Sin arma": "#E8C79A"}
COLOR_ARRESTO  = {"Sí": "#B9544A", "No": "#3A3E48"}
COLORES        = {"Gravedad": COLOR_GRAVEDAD, "Sexo": COLOR_SEXO, "Arma": COLOR_ARMA, "Arresto": COLOR_ARRESTO}
ORDEN_DIAS     = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
CENTRO         = {"lat": 34.05, "lon": -118.35}   # vista inicial del mapa

LAYOUT = dict(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Inter,Arial,sans-serif", size=12),
    margin=dict(t=50, b=40, l=50, r=20),
    legend=dict(orientation="h", y=-0.2),
)

# ── 3. CARGAR Y PREPARAR LOS DATOS ───────────────────────────
# @st.cache_data: lee el CSV UNA sola vez y guarda el resultado.
# Sin esta línea se volvería a leer en cada clic de un filtro.
@st.cache_data
def cargar_datos():
    # Datos limpios del Certamen 2 (muestra de 200.000 delitos, random_state=42)
    df = pd.read_csv("data/crimen_la_limpio.csv", parse_dates=["Fecha"])

    # Columnas de fecha y etiquetas en español (pandas puro)
    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.to_period("M").dt.to_timestamp()
    df["Día"] = df["Fecha"].dt.dayofweek.map(dict(enumerate(ORDEN_DIAS)))
    df["Gravedad"] = df["Gravedad"].map({1: "Grave", 2: "Otros"})
    df["Sexo"] = df["Sexo"].map({"F": "Mujer", "M": "Hombre"}).fillna("Desconocido")
    df["Arma"] = df["Arma"].map({1: "Con arma", 0: "Sin arma"})
    df["Arresto"] = df["Arresto"].map({1: "Sí", 0: "No"})
    return df

df = cargar_datos()

# ── 4. SIDEBAR — FILTROS GLOBALES ────────────────────────────
# Todo lo que está dentro de "with st.sidebar:" va al panel lateral.
# Cada widget devuelve el valor elegido y lo guardamos en una variable.
with st.sidebar:
    st.title("🚓 Crimen en LA")
    st.caption("Filtros globales — afectan todos los KPIs y gráficos")

    # slider de rango → tupla (año mínimo, año máximo)
    año_min, año_max = st.slider(
        "Años",
        min_value=int(df["Año"].min()),
        max_value=int(df["Año"].max()),
        value=(int(df["Año"].min()), int(df["Año"].max())),
    )

    # multiselect → varias zonas a la vez
    zonas_todas = sorted(df["Zona"].unique())
    zonas = st.multiselect("Zona policial", options=zonas_todas, default=zonas_todas)

    # radio → una sola opción
    gravedad = st.radio("Gravedad del delito", options=["Todos", "Grave", "Otros"])

    st.divider()
    st.caption(f"Dataset: {len(df):,} delitos (muestra 2016–2019)")
    st.caption("Versión beta 2.1.0")

# ── 5. APLICAR LOS FILTROS (pandas puro) ─────────────────────
mask = df["Año"].between(año_min, año_max) & df["Zona"].isin(zonas)
if gravedad != "Todos":
    mask &= df["Gravedad"] == gravedad

dff = df[mask]  # dff = "dataframe filtrado"

# ── 6. ENCABEZADO Y PREGUNTA DEL DASHBOARD ───────────────────
st.title("Crimen en Los Ángeles: ¿dónde, cuándo y qué ocurre?")
st.markdown("**Pregunta:** ¿en qué zonas, en qué momentos y qué tipos de delito concentran la actividad criminal "
            "en Los Ángeles entre 2016 y 2019? Pensado para quienes planifican el patrullaje y la prevención.")
st.caption(f"Mostrando {len(dff):,} de {len(df):,} delitos con los filtros aplicados")

# Si el filtro deja la tabla vacía, avisamos y detenemos la app
if dff.empty:
    st.warning("No hay delitos para los filtros seleccionados. Ajusta el panel lateral.")
    st.stop()

# ── 7. KPIs (TARJETAS DE MÉTRICAS) ───────────────────────────
k1, k2, k3, k4 = st.columns(4)

pct_arma       = (dff["Arma"] == "Con arma").mean() * 100
pct_arresto    = (dff["Arresto"] == "Sí").mean() * 100
arresto_global = (df["Arresto"] == "Sí").mean() * 100   # referencia SIN filtros

k1.metric("Delitos", f"{len(dff):,}", delta=f"{len(dff) / len(df) * 100:.0f}% del total", delta_color="off")
k2.metric("Edad mediana de la víctima", f"{dff['Edad'].median():.0f} años")
k3.metric("Delitos con arma", f"{pct_arma:.1f}%")
k4.metric("Delitos con arresto", f"{pct_arresto:.1f}%",
          delta=f"{pct_arresto - arresto_global:+.1f} pts vs total")

st.divider()

# ── 8. PESTAÑAS: DÓNDE · CUÁNDO · QUÉ Y A QUIÉNES ────────────
tab1, tab2, tab3 = st.tabs(["📍 Dónde", "🕒 Cuándo", "📊 Qué y a quiénes"])

# ---------- 8.1 DÓNDE: MAPAS ----------
with tab1:
    df_mapa = dff.dropna(subset=["LAT", "LON"])
    st.caption(f"Se excluyen {len(dff) - len(df_mapa):,} delitos con coordenadas inválidas "
               "(0, 0 o fuera de Los Ángeles). Mapas con una muestra de hasta 20.000 puntos (random_state=42).")
    muestra = df_mapa.sample(min(20000, len(df_mapa)), random_state=42)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Mapa de puntos")
        # CONTROL LOCAL: este selectbox solo afecta a este mapa
        color_por = st.selectbox("Colorear por", ["Gravedad", "Arma", "Arresto", "Sexo"], key="sel_color")
        fig = px.scatter_map(
            muestra, lat="LAT", lon="LON", color=color_por, color_discrete_map=COLORES[color_por],
            hover_name="Zona",
            hover_data={"Delito": True, "Fecha": "|%d-%m-%Y", "Hora": True, "LAT": False, "LON": False},
            center=CENTRO, zoom=9, opacity=0.5, height=520,
        )
        fig.update_layout(**LAYOUT, map_style="open-street-map")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Mapa de densidad")
        fig = px.density_map(
            muestra, lat="LAT", lon="LON", radius=3, center=CENTRO, zoom=9, height=575,
            color_continuous_scale="YlOrRd", hover_data={"Zona": True},
        )
        fig.update_layout(**LAYOUT, map_style="open-street-map", coloraxis_colorbar_title="Densidad")
        st.plotly_chart(fig, width="stretch")

    st.markdown("**Lectura (versión beta):** los delitos cubren toda la ciudad, pero se concentran en el centro "
                "(Downtown) y el sur (77th Street, Southwest). El Valle de San Fernando y Harbor muestran menor densidad. "
                "Esto sugiere priorizar el patrullaje en el eje centro–sur.")

# ---------- 8.2 CUÁNDO ----------
with tab2:
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Delitos por mes")
        r_mes = dff.groupby(["Mes", "Gravedad"]).size().reset_index(name="Delitos")
        fig = px.line(r_mes, x="Mes", y="Delitos", color="Gravedad", markers=True,
                      color_discrete_map=COLOR_GRAVEDAD, labels={"Delitos": "Cantidad de delitos"})
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, width="stretch")

    with col4:
        st.subheader("Día de la semana × hora")
        fig = px.density_heatmap(dff, x="Hora", y="Día", nbinsx=24, color_continuous_scale="YlOrRd",
                                 category_orders={"Día": ORDEN_DIAS},
                                 labels={"Hora": "Hora del día (0-23 h)", "Día": "Día de la semana"})
        fig.update_layout(**LAYOUT, coloraxis_colorbar_title="Delitos")
        st.plotly_chart(fig, width="stretch")

# ---------- 8.3 QUÉ Y A QUIÉNES ----------
with tab3:
    col5, col6 = st.columns([3, 2])

    with col5:
        st.subheader("Top 10 tipos de delito")
        r_top = dff["Delito"].value_counts().head(10).reset_index()
        r_top.columns = ["Delito", "Delitos"]
        r_top["%"] = (r_top["Delitos"] / len(dff) * 100).round(1)
        fig = px.bar(r_top, x="Delitos", y="Delito", orientation="h", hover_data={"%": True},
                     color_discrete_sequence=["#B9544A"],
                     labels={"Delitos": "Cantidad de delitos", "Delito": "Tipo de delito"})
        fig.update_layout(**LAYOUT, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch")

    with col6:
        st.subheader("Arresto con y sin arma")
        r_arma = (dff.groupby("Arma")["Arresto"].apply(lambda s: (s == "Sí").mean() * 100)
                     .round(1).reset_index(name="% arresto"))
        fig = px.bar(r_arma, x="Arma", y="% arresto", color="Arma", text="% arresto",
                     color_discrete_map=COLOR_ARMA,
                     labels={"Arma": "Uso de arma", "% arresto": "Delitos con arresto (%)"})
        fig.update_layout(**LAYOUT, showlegend=False)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Edad de las víctimas")
    fig = px.histogram(dff[dff["Sexo"] != "Desconocido"], x="Edad", color="Sexo", nbins=40, opacity=0.7,
                       barmode="overlay", color_discrete_map=COLOR_SEXO,
                       labels={"Edad": "Edad de la víctima (años)"})
    fig.update_layout(**LAYOUT, yaxis_title="Cantidad de víctimas")
    st.plotly_chart(fig, width="stretch")

# ── 9. HALLAZGOS PRINCIPALES (coherentes con el Certamen 2) ──
st.divider()
st.subheader("Hallazgos principales")
st.markdown("""
1. **Dónde:** el sur y el centro concentran más delitos (77th Street, Southwest y Central).
2. **Cuándo:** el viernes de 17 a 20 h es el momento más crítico; la madrugada, el más tranquilo.
3. **Qué y a quiénes:** predominan la agresión simple y los robos ligados a vehículos; la mitad de las víctimas tiene entre 27 y 50 años.
4. **Arma y arresto:** los delitos con arma terminan en arresto cerca de 3 veces más que los sin arma.
""")

# ── 10. TABLA DE DATOS (DESPLEGABLE) ─────────────────────────
with st.expander("Ver datos filtrados"):
    columnas = ["Fecha", "Hora", "Zona", "Delito", "Gravedad", "Edad", "Sexo", "Arma", "Arresto"]
    st.dataframe(dff[columnas], width="stretch", hide_index=True)
