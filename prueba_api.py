import requests
import io
import webbrowser
import tempfile

# URL de tu API
url = 'http://localhost:8001/crear_pdf_manual/'
token = '95f397a7bce2f2ffbe6c404caa1994ae991c4ee5'  # Token de autenticación

headers = {'Authorization': f'Token {token}'}

# Datos de prueba
datos_pdf = {
    'nombre_cliente': 'Seba',
    'rut_cliente': '12345678-9',
    'correo_cliente': 'seba@example.com',
    'id_solicitud': '1001',
    'alto_max_caja': 30,
    'area_caja': 600,
    'cantidad_cajas': 50,
    'id_tipo_plancha': 'TP123',
    'area_total_plancha': 1200,
    'cantidad_planchas': 10,
    'coste_creacion': 500,
    'coste_materia_prima': 2000,
    'precio_caja': 15,
    'precio_total': 15000,
    'porcentaje_utilidad': 20,
    'fecha_solicitud': '15-11-2023',
}

try:
    respuesta = requests.post(url, json=datos_pdf, headers=headers)

    if respuesta.status_code == 200:
        # Usar io.BytesIO para manejar el contenido del PDF en memoria
        pdf_en_memoria = io.BytesIO(respuesta.content)

        # Crear un archivo temporal para el PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_en_memoria.getvalue())

        # Abrir el PDF con el navegador web predeterminado
        webbrowser.open_new(temp_pdf.name)
        print("PDF abierto en el navegador.")
    else:
        print(f"Error en la solicitud: {respuesta.status_code}, Respuesta: {respuesta.text}")

except requests.exceptions.RequestException as e:
    print(f"Ocurrió un error al hacer la solicitud: {e}")
