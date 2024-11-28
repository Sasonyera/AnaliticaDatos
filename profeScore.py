import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
import io
import plotly.io as pio
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Estadistico Docente", page_icon=":bar_chart:", layout="wide")

# Estilos CSS personalizados
st.markdown(
    """
    <style>
    /* Fondo de la página */
    .main {
        background-color: #148E40;
    }
    
    /* Contenedor principal */
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 3rem;
        padding-right: 3rem;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Título principal */
    h1 {
        color: #148E40;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
    }

    /* Textos secundarios */
    h2, h3, .stMarkdown, label {
        color: #ffffff;
        font-family: 'Verdana', sans-serif;
    }

    /* Botones */
    .stButton>button {
        background-color: #ff6347;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #ff4500;
        color: #ffffff;
    }

    .st-emotion-cache-6qob1r {
        background-color:#148E40;
    }
    .st-emotion-cache-phe2gf p {
        color:#000000;
    }
    .st-emotion-cache-1puwf6r p {
        word-break: break-word;
        margin-bottom: 0px;
        font-size: 17px;
    }
    .st-emotion-cache-h4xjwg {
    position: fixed;
    top: 0px;
    left: 0px;
    right: 0px;
    height: 3.75rem;
    background: rgb(20, 142, 64);
    outline: none;
    z-index: 999990;
    display: block;
}


    /* Sidebar */
    .css-1d391kg .css-1r6slb0 {
        background-color: #ff6347;
    }
    .css-1d391kg .css-1r6slb0 h2 {
        color: #ffffff;
    }
    </style>
    """,

    unsafe_allow_html=True
)
logo_path = "barras2.png"
banner_path = "logoUSB.png"

st.sidebar.image(logo_path, use_container_width=True)
st.image(banner_path, use_container_width=True)
st.title("Estadistico Docente")

# Carga de datos
uploaded_file = st.file_uploader("📁 Cargar archivo Excel o CSV", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
    else:
        df = pd.read_excel(uploaded_file)
else:
    # Especifica la ruta de tu archivo local
    local_file_path = r"C:\Users\USER\Desktop\ProfeScoreUSB\ProfeScoreUSB\plantilla.xlsx"  # Reemplaza esta ruta con la de tu archivo

    try:
        if local_file_path.endswith('.csv'):
            df = pd.read_csv(local_file_path, encoding="ISO-8859-1")
        else:
            df = pd.read_excel(local_file_path)
        st.info(f"Usando el archivo local: {local_file_path}")
    except FileNotFoundError:
        st.error(f"No se encontró el archivo local en la ruta especificada: {local_file_path}")
        st.stop()
    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo: {e}")
        st.stop()

# Asegúrate de que los nombres de las columnas son correctos
expected_columns = ["Nombre", "Programa", "Materia", "Codigo", "Grupo", "Nota_Estudiante", "Nota_Director", "Autoevaluacion", "Definitiva", "Periodo"]
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    st.error(f"Las siguientes columnas faltan en el archivo cargado: {', '.join(missing_columns)}")
    st.stop()

# Mostrar información básica de los datos
st.write("Número total de registros:", len(df))

# Convertir tipos de datos
df['Autoevaluacion'] = pd.to_numeric(df['Autoevaluacion'], errors='coerce')
df['Nota_Director'] = pd.to_numeric(df['Nota_Director'], errors='coerce')
df['Definitiva'] = pd.to_numeric(df['Definitiva'], errors='coerce')

# Eliminar filas con valores nulos en las columnas clave
df = df.dropna(subset=['Autoevaluacion', 'Nota_Director', 'Definitiva'])

st.write("Número de registros después de eliminar valores nulos:", len(df))

# Filtros en la barra lateral
st.sidebar.header("Filtros")

# Filtro por Programa
programas = st.sidebar.multiselect("Selecciona el Programa", options=df["Programa"].unique())

# Filtro por Materia
materias = st.sidebar.multiselect("Selecciona la Materia", options=df["Materia"].unique())

# Filtro por Periodo
periodos = st.sidebar.multiselect("Selecciona el Periodo", options=df["Periodo"].unique())

# Aplicación de filtros
df_filtered = df.copy()

if programas:
    df_filtered = df_filtered[df_filtered["Programa"].isin(programas)]

if materias:
    df_filtered = df_filtered[df_filtered["Materia"].isin(materias)]

if periodos:
    df_filtered = df_filtered[df_filtered["Periodo"].isin(periodos)]

st.write("Número de registros después de aplicar los filtros:", len(df_filtered))

# Verificar si el DataFrame filtrado no está vacío
if df_filtered.empty:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")
else:
    # Función auxiliar para mostrar y descargar gráficos con Plotly
    def render_and_download_plotly(fig, filename, title, data=None):
        st.plotly_chart(fig, use_container_width=True)
        if data is not None:
            xlsx_buffer = io.BytesIO()
            with pd.ExcelWriter(xlsx_buffer, engine='xlsxwriter') as writer:
                data.to_excel(writer, index=False, sheet_name='Datos')
            st.download_button(
                label=f"Descargar datos de {title} como XLSX",
                data=xlsx_buffer.getvalue(),
                file_name=f"{filename}_datos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Gráficos
    st.header("Visualizaciones")

    # 1. Gráfico de dispersión de Autoevaluacion vs Nota_Director
    st.subheader("Comparación entre Autoevaluación y Nota Director")

    if df_filtered[['Autoevaluacion', 'Nota_Director']].dropna().empty:
        st.warning("No hay datos suficientes para mostrar este gráfico.")
    else:
        fig1 = px.scatter(
            df_filtered,
            x="Autoevaluacion",
            y="Nota_Director",
            hover_data=["Nombre", "Programa", "Materia", "Periodo"],
            labels={
                "Autoevaluacion": "Autoevaluación",
                "Nota_Director": "Nota Director"
            },
            title="Autoevaluación vs Nota Director"
        )
        render_and_download_plotly(fig1, "Autoevaluacion_vs_Nota_Director", "gráfico de Autoevaluación vs Nota Director", df_filtered[['Autoevaluacion', 'Nota_Director', 'Nombre', 'Programa', 'Materia', 'Periodo']])

    # 2. Diagrama de cajas de Distribución de Notas por Programa
    st.subheader("Distribución de Notas por Programa")

    if df_filtered[['Programa', 'Definitiva']].dropna().empty:
        st.warning("No hay datos suficientes para mostrar este gráfico.")
    else:
        fig2 = px.box(
            df_filtered,
            x="Programa",
            y="Definitiva",
            points="all",
            hover_data=["Nombre", "Materia", "Periodo"],
            labels={
                "Programa": "Programa",
                "Definitiva": "Nota Definitiva"
            },
            title="Distribución de Notas Definitivas por Programa"
        )
        render_and_download_plotly(fig2, "Distribucion_Notas_Programa", "diagrama de Distribución de Notas por Programa", df_filtered[['Programa', 'Definitiva', 'Nombre', 'Materia', 'Periodo']])

    # 3. Gráfico de barras horizontales Top 5 Profesores por Nota Definitiva
    st.subheader("Top 5 Profesores por Nota Definitiva")

    if df_filtered[['Nombre', 'Definitiva']].dropna().empty:
        st.warning("No hay datos suficientes para mostrar este gráfico.")
    else:
        top5_profesores = df_filtered.groupby("Nombre")["Definitiva"].mean().reset_index()
        top5_profesores = top5_profesores.sort_values(by="Definitiva", ascending=False).head(5)

        fig3 = px.bar(
            top5_profesores,
            x="Definitiva",
            y="Nombre",
            orientation='h',
            labels={
                "Definitiva": "Nota Definitiva Promedio",
                "Nombre": "Profesor"
            },
            title="Top 5 Profesores por Nota Definitiva"
        )
        render_and_download_plotly(fig3, "Top5_Profesores_Nota_Definitiva", "gráfico de Top 5 Profesores por Nota Definitiva", top5_profesores)

    # 4. Gráfico de barras Promedio de Notas por Materia
    st.subheader("Promedio de Notas por Materia")

    if df_filtered[['Materia', 'Definitiva']].dropna().empty:
        st.warning("No hay datos suficientes para mostrar este gráfico.")
    else:
        promedio_materia = df_filtered.groupby("Materia")["Definitiva"].mean().reset_index()

        fig4 = px.bar(
            promedio_materia,
            x="Materia",
            y="Definitiva",
            labels={
                "Materia": "Materia",
                "Definitiva": "Promedio de Nota Definitiva"
            },
            title="Promedio de Notas Definitivas por Materia"
        )
        render_and_download_plotly(fig4, "Promedio_Notas_Materia", "gráfico de Promedio de Notas por Materia", promedio_materia)

    # 5. Gráfico de líneas Evolución de Notas por Periodo
    st.subheader("Evolución de Notas por Periodo")

    if df_filtered[['Periodo', 'Definitiva']].dropna().empty:
        st.warning("No hay datos suficientes para mostrar este gráfico.")
    else:
        evolucion_periodo = df_filtered.groupby("Periodo")["Definitiva"].mean().reset_index()

        fig5 = px.line(
            evolucion_periodo,
            x="Periodo",
            y="Definitiva",
            labels={
                "Periodo": "Periodo",
                "Definitiva": "Promedio de Nota Definitiva"
            },
            title="Evolución de Notas Definitivas por Periodo"
        )
        render_and_download_plotly(fig5, "Evolucion_Notas_Periodo", "gráfico de Evolución de Notas por Periodo", evolucion_periodo)

    # 6. Gráfico de puntos (dot plot) Análisis de Outliers en Evaluaciones
    st.subheader("Análisis de Outliers en Evaluaciones")

    if df_filtered[['Autoevaluacion', 'Nota_Director']].dropna().empty:
        st.warning("No hay datos suficientes para mostrar este gráfico.")
    else:
        fig6 = px.strip(
            df_filtered,
            x="Definitiva",
            y="Materia",
            hover_data=["Nombre", "Programa", "Periodo"],
            labels={
                "Definitiva": "Nota Definitiva",
                "Materia": "Materia"
            },
            title="Análisis de Outliers en Evaluaciones"
        )
        render_and_download_plotly(fig6, "Outliers_Evaluaciones", "gráfico de Outliers en Evaluaciones", df_filtered[['Definitiva', 'Materia', 'Nombre', 'Programa', 'Periodo']])

    # Mostrar datos filtrados
    st.header("Datos Filtrados")
    st.write("Número de registros mostrados:", len(df_filtered))
    st.dataframe(df_filtered)

    # Descargar datos filtrados
    @st.cache_data
    def convert_df_to_excel(df):
        xlsx_buffer = io.BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos Filtrados')
        return xlsx_buffer.getvalue()

    xlsx = convert_df_to_excel(df_filtered)

    st.download_button(
        label="Descargar datos filtrados como XLSX",
        data=xlsx,
        file_name='datos_filtrados.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
