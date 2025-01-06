import socket

# Define the server address and port
SERVER_HOST = 'localhost'  # Change to the server's IP if needed
SERVER_PORT = 44444

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

    # Open a file to write the received data
    with open('received_data.txt', 'a') as file:
        while True:
            # Receive data from the server
            data = client_socket.recv(1024)
            if not data:
                break  # Break the loop if no data is received
            # Write the received data to the file
            file.write(data.decode('utf-8'))
            print(f"Received data: {data.decode('utf-8')}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the socket
    client_socket.close()
    print("Connection closed.")
