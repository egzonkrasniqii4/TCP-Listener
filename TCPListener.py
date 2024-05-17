import socket
import pyodbc
import json
from datetime import datetime, timezone

# Database connection parameters
db_params = {
    'driver': '{SQL Server}',
    'server': '192.168.49.49',
    'database': 'PeopleCounter',
    'user': 'sa',
    'password': 'sasa',                          
    'autocommit': True
}

# Set up the database connection
connection = pyodbc.connect(**db_params)
cursor = connection.cursor()





def handle_connection(client_socket):
    try:
        # Receive data from the client
        data = client_socket.recv(buffer_size)

        if data:
            # Decode received data as string
            data_str = data.decode('utf-8')

            # Check if the data starts with the HTTP POST request
            if data_str.startswith("POST / HTTP/1.1"):
                # Parse the JSON data
                json_data = json.loads(data_str.split("\r\n\r\n")[-1])

                # Insert data into the database
                count_right = json_data['CountLogs'][0]['Counts'][0]['LogPeriodValue']
                count_left = json_data['CountLogs'][0]['Counts'][1]['LogPeriodValue']
                timestamp = json_data['CountLogs'][0]['Timestamp']
                friendly_device_serial = json_data['FriendlyDeviceSerial']
                ipv4_address = json_data['IPv4Address']

                cursor.execute("INSERT INTO PeopleCounterIrisysRift (Timestamp, CountRight, CountLeft, FriendlyDeviceSerial, IPv4Address) VALUES (?, ?, ?, ?, ?)",
                               (timestamp, count_right, count_left, friendly_device_serial, ipv4_address))
                print("Data saved to database")

            else:
                print("Invalid request format. Expected POST request.")

        else:
            print("No data received from client.")
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the client socket
        client_socket.close()

# Set up initial socket
host = '192.168.49.49'  # localhost
port = 9008  # Port 9008
buffer_size = 4096  # Increase buffer size to accommodate larger data                 

try:
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set SO_REUSEADDR option
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind server socket
    server_socket.bind((host, port))
    server_socket.listen(1)

    # Get the port assigned by the system
    _, assigned_port = server_socket.getsockname()
    print(f"Listening on {host}:{assigned_port}")

    while True:
        # Accept incoming connections
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Handle the connection
        handle_connection(client_socket)

except KeyboardInterrupt:
    print("Server stopped by the user.")
finally:
    # Close the server socket
    if server_socket:
        server_socket.close()

    # Close the database connection
    if connection:
        connection.close()
