import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Título de la aplicación
st.title('📈 Evolución de las Bandas Cambiarias')
st.markdown('Proyección de las bandas cambiarias que se expanden un 1% cada 30 días.')

# --- Parámetros Iniciales del Problema ---
techo_inicial = 1400.0
piso_inicial = 1000.0
fecha_inicio = datetime(2025, 4, 14)
fecha_fin = datetime(2027, 1, 14)  # Proyección hasta enero de 2027
porcentaje_expansion = 0.01

# --- Cargar y procesar datos históricos del dólar ---
try:
    # La única línea modificada para usar la nueva ruta del archivo
    df_historico = pd.read_csv(
        ' ACÁ VA LA RUTA DEL CSV DESCARGADO DE INVESTING DESDE EL 14/04/25 HASTA LA ACTUALIDAD /usd-ars.csv', 
        sep=',',
        decimal=','
    )
    
    # Renombrar columnas para mayor claridad
    df_historico = df_historico.rename(columns={
        'Fecha': 'Fecha',
        'Último': 'valor_dolar_historico'
    })
    
    # Convertir la columna de fechas al formato correcto
    df_historico['Fecha'] = pd.to_datetime(df_historico['Fecha'], format='%d.%m.%Y')
    
    # Convertir la columna de valor a un tipo numérico (float)
    df_historico['valor_dolar_historico'] = pd.to_numeric(
        df_historico['valor_dolar_historico'].str.replace('.', '').str.replace(',', '.'), 
        errors='coerce'
    )

except FileNotFoundError:
    st.warning("El archivo `usd-ars.csv` no se encontró en la ruta especificada.")
    df_historico = pd.DataFrame()
except Exception as e:
    st.error(f"Ocurrió un error al procesar el archivo CSV: {e}")
    df_historico = pd.DataFrame()

# --- Generación de los datos de las bandas ---
fechas = []
techos = []
pisos = []
precios_centrales = []

meses_proyectados = (fecha_fin.year - fecha_inicio.year) * 12 + (fecha_fin.month - fecha_inicio.month)

for i in range(meses_proyectados + 1):
    mes_actual = fecha_inicio + relativedelta(months=i)
    
    techo_actual = techo_inicial * ((1 + porcentaje_expansion) ** i)
    piso_actual = piso_inicial * ((1 - porcentaje_expansion) ** i)
    precio_central = (techo_inicial + piso_inicial) / 2

    fechas.append(mes_actual)
    techos.append(techo_actual)
    pisos.append(piso_actual)
    precios_centrales.append(precio_central)

df_bandas = pd.DataFrame({
    'Fecha': fechas,
    'Techo': techos,
    'Piso': pisos,
    'Precio Central': precios_centrales
})

# --- Creación del Gráfico con Plotly ---
fig = go.Figure()

# Añadir la banda superior
fig.add_trace(go.Scatter(
    x=df_bandas['Fecha'],
    y=df_bandas['Techo'],
    mode='lines',
    name='Banda Superior',
    line=dict(color='red', width=2),
    hovertemplate="<b>%{x|%Y-%m}</b><br>Techo: %{y:.2f}"
))

# Añadir la banda inferior y rellenar el área entre las dos
fig.add_trace(go.Scatter(
    x=df_bandas['Fecha'],
    y=df_bandas['Piso'],
    mode='lines',
    name='Banda Inferior',
    line=dict(color='red', width=2),
    fill='tonexty',
    fillcolor='rgba(255, 0, 0, 0.1)',
    hovertemplate="<b>%{x|%Y-%m}</b><br>Piso: %{y:.2f}"
))

# Añadir la línea central
fig.add_trace(go.Scatter(
    x=df_bandas['Fecha'],
    y=df_bandas['Precio Central'],
    mode='lines',
    name='Precio Central',
    line=dict(color='black', dash='dash'),
    hovertemplate="<b>%{x|%Y-%m}</b><br>Precio Central: %{y:.2f}"
))

# Añadir la nueva traza para el valor del dólar histórico
if not df_historico.empty:
    fig.add_trace(go.Scatter(
        x=df_historico['Fecha'],
        y=df_historico['valor_dolar_historico'],
        mode='lines+markers',
        name='Valor Histórico del Dólar',
        line=dict(color='blue', width=2),
        hovertemplate="<b>%{x|%Y-%m}</b><br>Valor Dólar: %{y:.2f}"
    ))

# Configuración del layout del gráfico
fig.update_layout(
    title='Proyección de las Bandas Cambiarias vs. Dólar Histórico',
    xaxis_title='Fecha',
    yaxis_title='Valor',
    legend=dict(x=0.01, y=0.99),
    hovermode='x unified',
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)

# Sección para mostrar los datos en una tabla
if st.checkbox('Mostrar datos de la tabla'):
    st.subheader('Datos proyectados')
    df_bandas = pd.merge(df_bandas, df_historico, on='Fecha', how='left')
    st.dataframe(df_bandas.style.format({
        'Fecha': lambda t: t.strftime("%Y-%m"),
        'Techo': '{:.2f}',
        'Piso': '{:.2f}',
        'Precio Central': '{:.2f}',
        'valor_dolar_historico': '{:.2f}'
    }))
