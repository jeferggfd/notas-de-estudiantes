import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Dashboard Interactivo de Notas", page_icon="📊", layout="wide"
)

@st.cache_data
def cargar_datos_por_defecto():
  datos = {
      "ID": [
          "E01",
          "E02",
          "E03",
          "E04",
          "E05",
          "E06",
          "E07",
          "E08",
          "E09",
          "E10",
          "E11",
          "E12",
      ],
      "Estudiante": [
          "Ana",
          "Luis",
          "Sofía",
          "Diego",
          "Marta",
          "Pedro",
          "Carla",
          "Juan",
          "Lucía",
          "Andrés",
          "Camila",
          "Tomás",
      ],
      "Sexo": [
          "Mujer",
          "Hombre",
          "Mujer",
          "Hombre",
          "Mujer",
          "Hombre",
          "Mujer",
          "Hombre",
          "Mujer",
          "Hombre",
          "Mujer",
          "Hombre",
      ],
      "Sección": ["A", "A", "A", "B", "B", "B", "C", "C", "C", "D", "D", "D"],
      "Promedio": [
          6.30,
          5.60,
          4.10,
          3.10,
          4.80,
          6.10,
          5.60,
          3.50,
          6.60,
          4.20,
          4.80,
          6.30,
      ],
      "Asistencia (%)": [95, 88, 72, 60, 90, 96, 82, 68, 98, 78, 85, 92],
  }
  return pd.DataFrame(datos)

st.sidebar.title("Datos y filtros")
st.sidebar.text("Carga el archivo de estudiantes")


archivo_subido = st.sidebar.file_uploader(
    "estudia...notas.csv", type=["csv"], label_visibility="collapsed"
)

if archivo_subido is not None:
  df = pd.read_csv(archivo_subido, sep=";")
else:
  df = cargar_datos_por_defecto()

st.sidebar.markdown("---")

sexos_disponibles = (
    df["Sexo"].unique() if "Sexo" in df.columns else ["Mujer", "Hombre"]
)
sexos_seleccionados = st.sidebar.multiselect(
    "Sexo", options=sexos_disponibles, default=list(sexos_disponibles)
)


secciones = (
    ["Todas"] + list(df["Sección"].unique())
    if "Sección" in df.columns
    else ["Todas"]
)
seccion_seleccionada = st.sidebar.selectbox("Sección", options=secciones)


rango_promedio = st.sidebar.slider(
    "Rango del promedio", min_value=1.00, max_value=7.00, value=(1.00, 7.00)
)


asistencia_minima = st.sidebar.number_input(
    "Asistencia mínima (%)", min_value=0, max_value=100, value=0
)

st.sidebar.markdown(
    "Los filtros se combinan. Quitar ambos sexos deja la selección vacía."
)


filtrado = df.copy()

if "Sexo" in filtrado.columns and sexos_seleccionados:
  filtrado = filtrado[filtrado["Sexo"].isin(sexos_seleccionados)]
else:
  filtrado = filtrado.iloc[0:0]

if "Sección" in filtrado.columns and seccion_seleccionada != "Todas":
  filtrado = filtrado[filtrado["Sección"] == seccion_seleccionada]

if "Promedio" in filtrado.columns:
  filtrado = filtrado[
      (filtrado["Promedio"] >= rango_promedio[0])
      & (filtrado["Promedio"] <= rango_promedio[1])
  ]

if "Asistencia (%)" in filtrado.columns:
  filtrado = filtrado[filtrado["Asistencia (%)"] >= asistencia_minima]


st.title("Dashboard interactivo de notas")
st.markdown(
    "Explora los resultados de un curso combinando filtros. **Promedio**: 50%"
    " de cada evaluación. **Aprobación del ejercicio**: promedio mayor o igual"
    " a 4,0. Datos ficticios."
)

sexos_str = (
    ", ".join(sexos_seleccionados) if sexos_seleccionados else "Ninguno"
)
st.markdown(
    f"Filtros activos: {sexos_str} · Sección: {seccion_seleccionada} · Promedio:"
    f" {rango_promedio[0]:.2f} a {rango_promedio[1]:.2f} · Asistencia mínima:"
    f" {asistencia_minima}%"
)


total_estudiantes = len(filtrado)
promedio_general = (
    filtrado["Promedio"].mean() if total_estudiantes > 0 else 0.0
)
aprobados = (
    len(filtrado[filtrado["Promedio"] >= 4.0]) if total_estudiantes > 0 else 0
)
porcentaje_aprobacion = (
    (aprobados / total_estudiantes) * 100 if total_estudiantes > 0 else 0.0
)

col1, col2, col3 = st.columns(3)
col1.metric("Estudiantes seleccionados", f"{total_estudiantes}")
col2.metric("Promedio general", f"{promedio_general:.2f}")
col3.metric("Aprobación", f"{porcentaje_aprobacion:.2f} %")

st.markdown("---")


st.write("Gráfico")
col_r1, col_r2, _ = st.columns([2, 2, 6])
tipo_grafico = col_r1.radio(
    "Tipo de gráfico",
    options=["Notas por estudiante", "Promedio por sección"],
    label_visibility="collapsed",
    horizontal=True,
)
mostrar_tabla = st.checkbox("Mostrar tabla", value=True)

st.subheader("Visualización de notas")

if filtrado.empty:
  st.warning(
      "No hay estudiantes que cumplan con los filtros seleccionados. Ajusta"
      " los criterios en la barra lateral."
  )
else:

  if mostrar_tabla:
    col_grafico, col_tabla = st.columns([1.2, 1])
  else:
    col_grafico = st.container()

  with col_grafico:
    fig, ax = plt.subplots(figsize=(7, 4))

    if tipo_grafico == "Notas por estudiante":
      ax.bar(filtrado["Estudiante"], filtrado["Promedio"], color="#1f77b4")
      ax.set_ylabel("Promedio de notas")
      ax.set_xlabel("Estudiante")
      plt.xticks(rotation=45, ha="right")
      ax.axhline(y=4.0, color="red", linestyle="--", label="Aprobación: 4,0")
      ax.legend(loc="upper right", fontsize=8)
      ax.set_title("Promedio por estudiante")
    else:
      prom_seccion = filtrado.groupby("Sección")["Promedio"].mean()
      ax.bar(prom_seccion.index, prom_seccion.values, color="#ff7f0e")
      ax.set_ylabel("Promedio de sección")
      ax.set_xlabel("Sección")
      ax.axhline(y=4.0, color="red", linestyle="--", label="Aprobación: 4,0")
      ax.legend(loc="upper right", fontsize=8)
      ax.set_title("Promedio por sección")

    ax.grid(axis="y", linestyle="--", alpha=0.6)
    st.pyplot(fig)

  if mostrar_tabla:
    with col_tabla:
      st.subheader("Estudiantes seleccionados")
      st.dataframe(filtrado, use_container_width=True, hide_index=True)

st.markdown("---")
csv_data = filtrado.to_csv(index=False, sep=";").encode("utf-8")
st.download_button(
    label="Descargar selección CSV",
    data=csv_data,
    file_name="estudiantes_filtrados.csv",
    mime="text/csv",
)

st.caption(
    f"Mostrando {total_estudiantes} de {len(df)} estudiantes. La asistencia"
    " solo se usa como filtro; la aprobación depende del promedio."
)
