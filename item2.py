import urllib.parse
import requests
import math

# Función para obtener coordenadas de una ubicación usando OpenCage
def get_coordinates(location, api_key):
    url = "https://api.opencagedata.com/geocode/v1/json?" + urllib.parse.urlencode({"q": location, "key": api_key})
    response = requests.get(url).json()
    if response['results']:
        return response['results'][0]['geometry']['lat'], response['results'][0]['geometry']['lng']
    else:
        return None, None

# Función para calcular la distancia entre dos puntos geográficos usando la fórmula de Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Función para obtener direcciones e instrucciones usando OpenRouteService
def get_route_instructions(orig_coords, dest_coords, transport_mode, api_key):
    url = f"https://api.openrouteservice.org/v2/directions/{transport_mode}"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [orig_coords[::-1], dest_coords[::-1]]
    }
    response = requests.post(url, json=body, headers=headers).json()
    return response

# Función para convertir segundos en horas y minutos
def convert_seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(hours)} horas {int(minutes)} minutos"

# Claves API
open_cage_key = "f4c03993b79245a1bd748a26d0091684"
open_route_key = "your_openroute_service_api_key"

while True:
    orig = input("Ubicación inicial: ")
    if orig.lower() in ["quit", "q", "s"]:
        break
    dest = input("Destino: ")
    if dest.lower() in ["quit", "q", "s"]:
        break
    
    print("Seleccione el tipo de medio de transporte:")
    print("1. Coche")
    print("2. Bicicleta")
    print("3. A pie")
    transport_mode = input("Ingrese el número correspondiente al medio de transporte: ")
    
    if transport_mode == "1":
        transport_mode = "driving-car"
    elif transport_mode == "2":
        transport_mode = "cycling-regular"
    elif transport_mode == "3":
        transport_mode = "foot-walking"
    else:
        print("Opción inválida. Usando coche por defecto.")
        transport_mode = "driving-car"

    orig_lat, orig_lng = get_coordinates(orig, open_cage_key)
    dest_lat, dest_lng = get_coordinates(dest, open_cage_key)
    
    if orig_lat is None or dest_lat is None:
        print("Error en la obtención de coordenadas para una o ambas ubicaciones.")
        continue
    
    distance_km = haversine(orig_lat, orig_lng, dest_lat, dest_lng)
    distance_miles = distance_km * 0.621371
    print(f"Distancia desde {orig} hasta {dest}: {distance_km:.2f} km ({distance_miles:.2f} millas)")

    route_instructions = get_route_instructions([orig_lng, orig_lat], [dest_lng, dest_lat], transport_mode, open_route_key)

    if "routes" in route_instructions:
        duration_seconds = route_instructions['routes'][0]['summary']['duration']
        duration_time = convert_seconds_to_time(duration_seconds)
        distance_route_km = route_instructions['routes'][0]['summary']['distance'] / 1000
        distance_route_miles = distance_route_km * 0.621371
        print("=============================================")
        print(f"Ruta desde {orig} hasta {dest}")
        print(f"Duración del viaje: {duration_time}")
        print(f"Distancia del viaje: {distance_route_km:.2f} km ({distance_route_miles:.2f} millas)")
        print("Instrucciones de la ruta:")
        for step in route_instructions['routes'][0]['segments'][0]['steps']:
            print(f"{step['instruction']} ({step['distance'] / 1000:.2f} km)")
        print("=============================================")
    else:
        print("Error al obtener las instrucciones de la ruta.")
        # Solicita si el usuario quiere salir
        exit = input("¿Quieres salir? (s/n): ")
        if exit.lower() == "s":
            print("¡Hasta la próxima!")
            break
