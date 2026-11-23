# Crimen en Los Ángeles: ¿dónde, cuándo y qué ocurre?

Dashboard interactivo hecho con **Streamlit** y **Plotly Express** a partir del análisis exploratorio del Certamen 2 de Visualización de la Información (UDD, 2026).

**App publicada:** [PEGAR AQUÍ EL ENLACE .streamlit.app](https://share.streamlit.io)

![Captura del dashboard](captura.png)

## Descripción
El dashboard responde **en qué zonas, en qué momentos y qué tipos de delito concentran la actividad criminal en Los Ángeles entre 2016 y 2019**. Está pensado para quienes planifican el patrullaje y la prevención.

Incluye:
- Filtros globales en el panel lateral: años, zona policial y gravedad del delito.
- KPIs: cantidad de delitos, edad mediana de la víctima, % con arma y % con arresto (comparado con el total).
- Mapa de puntos y mapa de densidad interactivos (`px.scatter_map`, `px.density_map`).
- Gráficos de tipos de delito, edad de las víctimas, evolución mensual, día × hora y relación arma–arresto.

## Datos
- **Fuente:** *Crime Data from 2010 to 2019*, Departamento de Policía de Los Ángeles (LAPD), publicado en Kaggle (licencia CC0).
- **Período:** 2016–2019 (902.673 delitos).
- **Limpieza (Certamen 2):** edades ≤ 0 o > 100 como nulas, coordenadas (0, 0) o fuera de Los Ángeles como nulas, sexo 'H' y '-' como 'X', arma nula como "Sin arma".
- **Muestra:** el archivo completo supera los 25 MB, por lo que `data/crimen_la_limpio.csv` contiene una **muestra aleatoria de 200.000 delitos (`random_state=42`)**.

## Estructura del repositorio
```
crimen_app.py            # la app
requirements.txt         # librerías
README.md
.streamlit/config.toml   # tema de colores
data/crimen_la_limpio.csv
```

## Ejecutar en local
```bash
pip install -r requirements.txt
streamlit run crimen_app.py
```

## Versiones
- `v2.1.0-beta` — Hito 1 (23 de noviembre)
- `v3.0.0` — Examen final (3 de diciembre)

## Integrantes
- Felipe Farías
- Benjamín Godoy
