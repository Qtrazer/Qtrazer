"""Modelo para operaciones con la API."""

import requests
from src.config.settings import CONFIG_TABLAS

class ClienteAPI:
    def __init__(self):
        self.url_base = "https://datosabiertos.bogota.gov.co/api/3/action/datastore_search"
        self.recurso_id = "b64ba3c4-9e41-41b8-b3fd-2da21d627558"

    def obtener_registros(self, nombre_tabla, callback_progreso=None):
        """Obtiene registros de la API para una tabla específica."""
        try:
            config = CONFIG_TABLAS[nombre_tabla]
            columnas = config['columnas']

            # Obtener total de registros
            params = {
                'resource_id': self.recurso_id,
                'limit': 1
            }
            respuesta = requests.get(self.url_base, params=params)
            total_registros = respuesta.json()['result']['total']

            # Obtener todos los registros
            registros = []
            offset = 0
            limite = 100

            while offset < total_registros:
                params = {
                    'resource_id': self.recurso_id,
                    'limit': limite,
                    'offset': offset
                }
                respuesta = requests.get(self.url_base, params=params)
                datos = respuesta.json()['result']['records']
                registros.extend(datos)

                if callback_progreso:
                    callback_progreso('api', min(offset + limite, total_registros), total_registros)

                offset += limite

            return registros

        except Exception as e:
            print(f"Error al obtener registros de la API: {str(e)}")
            return None 