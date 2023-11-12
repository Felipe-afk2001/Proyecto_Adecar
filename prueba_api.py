import requests

# URL de tu API
url = 'http://localhost:8000/calcular/'

# Token de autenticación (reemplázalo con tu token real)
token = '95f397a7bce2f2ffbe6c404caa1994ae991c4ee5'

# Cabecera de autenticación
headers = {
    'Authorization': f'Token {token}'
}

# Datos para enviar en la petición POST
datos_prueba = {
    'largo_caja': 200,
    'ancho_caja': 200,
    'alto_caja': 200,
    'largo_plancha': 2200,
    'ancho_plancha': 1620,
    'coste_materia': 1500,
    'porcentaje_utilidad': 10,
    'coste_creacion': 200,
    'cantidad_caja': 200
}

# Realizar la petición POST
respuesta = requests.post(url, json=datos_prueba, headers=headers)

# Verificar la respuesta
print(f'Estado de la respuesta: {respuesta.status_code}')
if respuesta.status_code == 200:
    print("PDF generado exitosamente.")
    # Aquí puedes manejar el PDF, por ejemplo, guardarlo en un archivo
    with open('cotizacion.pdf', 'wb') as f:
        f.write(respuesta.content)
    import webbrowser
    webbrowser.open_new('cotizacion.pdf')
