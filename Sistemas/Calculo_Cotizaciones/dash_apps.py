# Calculo_Cotizaciones/dash_apps.py
import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from .models import Historial
from django.db.models import Count
from dash import html  # Importar html de dash
from dash import dcc

# Crear un DataFrame de pandas directamente desde el modelo de Django
df = pd.DataFrame(Historial.objects.all().values())

# Preparar los datos para "Cantidad de cotizaciones por fecha"
df_fecha = df.groupby(df['fecha_cotizacion'].dt.date).count().id_historial.reset_index()
df_fecha.columns = ['fecha_cotizacion', 'cantidad']

# Preparar los datos para "Cantidad de cotizaciones por cliente"
df_cliente = df.groupby('nombre_cliente').count().id_historial.reset_index()
df_cliente.columns = ['nombre_cliente', 'cantidad']

# Preparar los datos para "Cantidad de cotizaciones aceptadas por fecha"
df_aceptadas = df[df['estado_cotizacion'] == 'Aceptado'].groupby(df['fecha_cotizacion'].dt.date).count().id_historial.reset_index()
df_aceptadas.columns = ['fecha_cotizacion', 'cantidad']

# Inicializar la aplicación Dash
app = DjangoDash('HistorialDashboards')


# Configurar los gráficos y el layout de la aplicación Dash
app.layout = html.Div([
    html.H1('Dashboards de Cotizaciones Realizadas'),

    dcc.Graph(
        id='cotizaciones-por-cliente',
        figure=px.bar(df_cliente, x='nombre_cliente', y='cantidad', title='Cantidad de Cotizaciones por Cliente'),
        style={'width': '50', 'height': '100'}
    ),

    dcc.Graph(
        id='cotizaciones-aceptadas-por-fecha',
        figure=px.bar(df_aceptadas, x='fecha_cotizacion', y='cantidad', title='Cantidad de Cotizaciones Aceptadas por Fecha'),
        style={'width': '50', 'height': '100'}
    ),

    dcc.Graph(
        id='cotizaciones-por-fecha',
        figure=px.bar(df_fecha, x='fecha_cotizacion', y='cantidad', title='Cantidad de Cotizaciones por Fecha'),
        style={'width': '50', 'height': '100'}
    )

])


