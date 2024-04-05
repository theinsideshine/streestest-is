import requests
import threading
import time
from datetime import datetime

# Bloqueo para sincronizar la impresión en la consola
print_lock = threading.Lock()

# Variable global para contar los errores
error_count = 0

# Lista para almacenar los datos para la salida CSV
csv_data = []

# Función para enviar una solicitud HTTP
def send_request(url, thread_num, start_time,formatted_start_time):
    try:
        global error_count  # Indica que se utilizará la variable global error_count
       
        # Realiza la solicitud
        response = requests.get(url + f"?start_time={start_time.timestamp() * 1000}")
        # Calcula el tiempo de respuesta
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()        
       
        # Guarda los datos para la salida CSV
        if response.status_code == 200:
            csv_data.append((formatted_start_time, response_time))
        else:
            csv_data.append((formatted_start_time, -1))  # Si hay un error, registra -1 como tiempo de respuesta
            error_count += 1  # Incrementa el contador de errores
       
        # Imprime la hora de la solicitud, respuesta y tiempo de respuesta de manera sincronizada
        with print_lock:
            if response.status_code == 200:
                print(f"Hilo {thread_num}: Hora de solicitud: {formatted_start_time} s Tiempo de respuesta: {response_time} segundos")
            else:
                print(f"Hilo {thread_num}: Hora de solicitud: {formatted_start_time} s Tiempo de respuesta: -1 segundos")
    except Exception as e:
        print("Error al enviar solicitud:", e)

# Función para enviar múltiples solicitudes concurrentemente
def send_requests_concurrently(num_requests, urls , time_delay_s):
    threads = []
    for i in range(num_requests):
        url = urls[i % len(urls)]  # Alterna entre las URLs
         # Imprime el número de hilo y la hora de la solicitud
        start_time = datetime.now()
        # Formatea la hora de la solicitud sin fecha pero con milisegundos
        formatted_start_time = start_time.strftime("%S.%f")[:-3]  # Formato hora, minutos, segundos y milisegundos
        thread = threading.Thread(target=send_request, args=(url, i+1,start_time,formatted_start_time))  # Pasar el número de hilo como argumento
        threads.append(thread)
        thread.start()
        time.sleep(time_delay_s) 
    for thread in threads:
        thread.join()

# URLs de los endpoints
urls = ["http://localhost:8081/queue/mp3/2",
        "http://localhost:8081/queue/mp3/3"]

# Número de solicitudes a enviar
num_requests = 300

# Tiempo en ms de delay entre thread
time_delay_ms = 10
time_delay_s = time_delay_ms / 1000

print(f"Numero de hilos: {num_requests}")
print(f"Delay entre thread: {time_delay_ms} ms // {time_delay_s} s")

# Enviar las solicitudes concurrentemente
send_requests_concurrently(num_requests, urls, time_delay_s)

# Generar nombre de archivo para salida CSV
file_name = f"localQueueRds-Nr{num_requests}-Td{time_delay_ms}-Ne{error_count}.csv"

# Guardar la salida CSV
with open(file_name, "w") as f:
    f.write("hs,tr\n")  # Escribir encabezados
    for data in csv_data:
        f.write(f"{data[0]},{data[1]}\n")

print(f"Numero de hilos: {num_requests}")
print(f"Delay entre thread: {time_delay_ms} ms // {time_delay_s} s")
# Imprime la cantidad de errores al finalizar todas las solicitudes
print(f"Suma de errores: {error_count}")
