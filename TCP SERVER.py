import socket
import threading
import json
import pyDes
import base64
import datetime

# Diffie Hellman Parameters
g_value = 5
n_value = 23

def read_contacts_data():
    with open("contacts.json", "r") as ReadContactsInfo:
        return json.load(ReadContactsInfo)

def pad_or_truncate_key(key):
    # If key is less than 8 bytes, pad it with zeros
    if len(key) < 8:
        key += b'0' * (8 - len(key))
    # If key is more than 8 bytes truncate it
    elif len(key) > 8:
        key = key[:8]
    return key

def save_received_message_to_history(sender_username, received_message):
    with open(f"chat_history_{sender_username}.txt", "a", encoding="utf8") as AppendChatHistoryFile:
        AppendChatHistoryFile.write(f"RECEIVED | {datetime.datetime.now()} | {sender_username}: {received_message}\n")


def handle_client(client_socket, user=None):
    shared_key = None
    sender_username = None

    try:
        while True:
            request = client_socket.recv(1024)
            if not request:
                print("Client disconnected gracefully.")
                break  # Client closed connection

            data = json.loads(request.decode())

            if user:
                for u in read_contacts_data()["users"]:
                    if u["IP Address"] == client_socket.getpeername()[0]:
                        sender_username = u["username"]
                        break
            else:
                sender_username = "Unknown"

            if "key" in data:
                client_key = int(data["key"])
                print(f"Received client's key: {client_key}")

                # NEW: generate a random private key
                import random
                server_private_key = random.randint(1, n_value)
                server_key = (g_value ** server_private_key) % n_value
                print(f"Generated server key: {server_key}")

                shared_key = (client_key ** server_private_key) % n_value
                print(f"Generated shared key: {shared_key}")

                shared_key = str(shared_key).encode()
                shared_key = pad_or_truncate_key(shared_key)
                print(f"Final key after padding or truncating: {shared_key.decode('utf-8')}")

                # Send server key to client
                response = json.dumps({"key": server_key})
                client_socket.send(response.encode())
                print("Sent server key to the client")

            elif "encrypted_message" in data and shared_key:
                encrypted_message = base64.b64decode(data['encrypted_message'])
                des = pyDes.des(shared_key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
                decrypted_message = des.decrypt(encrypted_message)
                decrypted_message = decrypted_message.decode()
                print(f"{datetime.datetime.now()} | {sender_username}: Decrypted message: {decrypted_message}")
                save_received_message_to_history(sender_username, decrypted_message)

            elif "unencrypted_message" in data:
                print(f"{datetime.datetime.now()} | {sender_username} says: {data['unencrypted_message']}")
                save_received_message_to_history(sender_username, data['unencrypted_message'])

            else:
                print("Unknown data received.")

    except (ConnectionResetError, BrokenPipeError):
        print("Client disconnected forcibly.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        try:
            client_socket.close()
            print("Client socket closed.")
        except Exception as close_err:
            print(f"Error while closing socket: {close_err}")


def chat_responder():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 6001))
    server_socket.listen(5)

    print("Listening on port 6001...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from: {addr[0]}:{addr[1]}")

        # Handle clients in separate threads
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

chat_responder()
