import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import pandas as pd
import os
import requests
from datetime import datetime

# --- Constantes ---
API_URL = "http://127.0.0.1:5001"
ALERTAS_PATH = "data/alertas.json"

# --- Inicialización de la App ---
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "Gestor Predictivo BOE"

# --- Funciones Auxiliares ---
def cargar_datos():
    """Carga los datos desde el archivo JSON de alertas de forma segura."""
    if os.path.exists(ALERTAS_PATH) and os.path.getsize(ALERTAS_PATH) > 0:
        try:
            # Leemos el archivo y nos aseguramos de que las columnas esperadas existan
            df = pd.read_json(ALERTAS_PATH)
            expected_cols = ['titulo', 'sector', 'tipo_norma', 'departamento']
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None # Añade la columna vacía si no existe
            return df
        except ValueError:
            # Si el JSON está malformado, devuelve un DataFrame vacío pero con la estructura correcta
            return pd.DataFrame(columns=['titulo', 'sector', 'tipo_norma', 'departamento'])
    # Si el archivo no existe o está vacío, también devolvemos la estructura correcta
    return pd.DataFrame(columns=['titulo', 'sector', 'tipo_norma', 'departamento'])

# --- Layout de la Interfaz (UI) ---
app.layout = html.Div(style={'fontFamily': 'sans-serif', 'padding': '20px'}, children=[
    html.H1(children='🎯 Gestor Predictivo Legal-Financiero'),
    html.Hr(),

    html.Div([
        html.Button('🔄 Actualizar Datos y Predecir con IA', id='update-button', n_clicks=0, style={'fontSize': '16px'}),
        dcc.Loading(id="loading-spinner", type="circle", children=html.Div(id="loading-output"))
    ], style={'marginBottom': '20px'}),
    
    html.Div(id='notification-area', style={'marginBottom': '20px', 'padding': '10px', 'borderRadius': '5px'}),

    html.Div([
        dcc.Dropdown(id='sector-filter', placeholder="Filtrar por sector..."),
        dcc.Input(id='search-input', type='text', placeholder='Buscar por palabra clave...', style={'marginLeft': '10px', 'width': '300px'}),
    ], className='row', style={'marginBottom': '20px'}),
    
    html.Hr(),

    html.H2(children='🚨 Alertas y Disposiciones'),
    dash_table.DataTable(
        id='alertas-table',
        columns=[{"name": i.replace('_', ' ').title(), "id": i} for i in ['titulo', 'sector', 'tipo_norma', 'departamento']],
        page_size=15,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '10px', 'whiteSpace': 'normal', 'height': 'auto'},
    )
])

# --- Lógica Interactiva (Callbacks) ---

@app.callback(
    Output('notification-area', 'children'),
    Output('notification-area', 'style'),
    Output('alertas-table', 'data'),      # Actualizamos la tabla directamente
    Output('sector-filter', 'options'), # Actualizamos las opciones del filtro
    Input('update-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_update_click(n_clicks):
    """Se dispara SOLO al hacer clic en el botón de actualizar."""
    try:
        response = requests.post(f"{API_URL}/actualizar", timeout=30)
        response.raise_for_status()
        api_response = response.json()

        timestamp = datetime.now().strftime("%H:%M:%S")
        mensaje = f"✅ Éxito ({timestamp}): {api_response.get('message', 'Proceso completado.')}"
        notificacion = html.Div([html.H4("Actualización Correcta"), html.P(mensaje)])
        estilo = {'border': '2px solid green', 'backgroundColor': '#e6ffed', 'padding': '10px', 'borderRadius': '5px'}
        
        # Recargamos los datos y actualizamos la tabla Y los filtros
        df_nuevos = cargar_datos()
        opciones_filtro = [{'label': i, 'value': i} for i in df_nuevos['sector'].unique()]
        return notificacion, estilo, df_nuevos.to_dict('records'), opciones_filtro

    except requests.exceptions.RequestException as e:
        timestamp = datetime.now().strftime("%H:%M:%S")
        mensaje = f"No se pudo conectar o la API falló. Asegúrate de que el servidor de la API (gestor_api.py) se está ejecutando y revisa su terminal para ver los errores."
        alarma = html.Div([html.H4(f"🚨 ALARMA DE CONEXIÓN/PROCESAMIENTO ({timestamp})"), html.P(mensaje)])
        estilo = {'border': '2px solid red', 'backgroundColor': '#ffe6e6', 'padding': '10px', 'borderRadius': '5px'}
        return alarma, estilo, dash.no_update, dash.no_update

@app.callback(
    Output('alertas-table', 'data', allow_duplicate=True), # Usamos allow_duplicate para que la tabla pueda ser actualizada por dos callbacks
    Input('sector-filter', 'value'),
    Input('search-input', 'value'),
    prevent_initial_call=True
)
def handle_filtering(sector_value, search_value):
    """Se dispara SOLO al cambiar los filtros."""
    df_filtrado = cargar_datos() # Siempre trabajamos con los datos más frescos del disco

    if sector_value:
        df_filtrado = df_filtrado[df_filtrado['sector'] == sector_value]
    if search_value:
        df_filtrado = df_filtrado[df_filtrado['titulo'].str.contains(search_value, case=False, na=False)]
    
    return df_filtrado.to_dict('records')


# --- Punto de Entrada ---
if __name__ == '__main__':
    app.run(debug=True)

