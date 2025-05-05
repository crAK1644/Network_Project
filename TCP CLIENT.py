from socket import *
import os, threading, json, pyDes, base64
from datetime import datetime, timedelta

current_time = datetime.now()
tcp_port = 6001
tcp_cli_sock = socket(AF_INET, SOCK_STREAM)
divisor = 23
prime = 5
shared_key = None

def save_own_msg_to_history(target_destination, own_username, own_plaintext_msg):
    with open(f'chat_history_{target_destination}.txt', 'a', encoding='utf-8') as AppendChatHistoryFile:
        AppendChatHistoryFile.write(f"SENT | {current_time} | {own_username}: {own_plaintext_msg}\n")

def chat_initiator():
    print("Welcome to the TCP Client!\nThis program is used for displaying available users, sending messages to them, or viewing chat history logs.\n"
          "Fetching your username from the 'own_user_info.json' file...\nIf you want to change your username, just delete the 'own_user_info.json' file.\n")
    chat_initiator()

def begin_announcer():
    print(f"Note that the received messages will be shown in the TCP Server. This is the client.\n"
          "The session is ready! Awaiting your messages...\n")

def read_contact_data():
    with open("contacts.json", "r") as ReadContactsInfo:
        contacts_data = json.load(ReadContactsInfo)
        return contacts_data

def pad_or_truncate_key(key):
    # If key is less than 8 bytes, pad it with zeros
    if len(key) < 8:
        key += b'0' * (8 - len(key))
    # If key is more than 8 bytes, truncate it
    elif len(key) > 8:
        key = key[:8]
    return key

def handle_client(tcp_cli_sock):
    global shared_key
    while True:
        response = json.loads(tcp_cli_sock.recv(2048).decode())
        if 'encrypted_message' in response:
            decrypted_message = pyDes.des(shared_key, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5).decrypt(response['encrypted_message'])
            print(f"Decrypted message: {decrypted_message}")
        elif 'unencrypted_message' in response:
            print(f"Unencrypted message: {response['unencrypted_message']}")
        else:
            print("Unknown data received.")

def chat_initiator():
    global shared_key
    if os.path.exists("user_info_self.json"):
        with open("user_info_self.json", "r") as ReadOwnUserInfo:
            own_data = json.load(ReadOwnUserInfo)
            own_username = own_data['username']
            print(f"Welcome back, {own_username}!\n")
    else:
        print("You didn't start the UDP client and server before.\n"
              "Please start them first, for registration and user detection purposes.\n\nTerminating...")
        exit()

    while True:
        choice = input("Please choose an action (users/chat/history): ").lower()
        read_contact_data()
        if choice == 'users':
            users = read_contact_data()['users']
            print("All users (Activity within the last 15 minutes):\n")
            for user in users:
                last_seen_time = datetime.strptime(user['Last Seen'], "%d/%m/%Y %H:%M:%S")
                if (current_time - last_seen_time) < timedelta(minutes=15):
                    username = user['username']
                    status = user['Status']
                    print(f"{username} ({status})\n")
        elif choice == 'chat':
            while True:
                target_destination = input("Who do you want to chat with?: ")
                read_contact_data()
                for user in read_contact_data()['users']:
                    last_seen_time = datetime.strptime(user['Last Seen'], "%d/%m/%Y %H:%M:%S")
                    if target_destination.lower() == user['username'].lower() and (
                            (current_time - last_seen_time) < timedelta(minutes=15)):
                        target_ip = user['IP Address']
                        try:
                            tcp_cli_sock.connect((target_ip, tcp_port))
                        except ConnectionRefusedError as e:
                            print("Connection has been refused!")
                            exit()

                security = input("Please specify your chat security preference (secure/unsecure): ").lower()
                if security == 'unsecure':
                    print(f"Initiating plaintext unsecure chat, with {target_destination} at {target_ip}...\n")
                    begin_announcer()
                    while True:
                        try:
                            own_plaintext_msg = input(f"{own_username}: ")
                            save_own_msg_to_history(target_destination, own_username, own_plaintext_msg)
                            plaintext_msg_as_json = {'unencrypted_message': own_plaintext_msg}
                            tcp_cli_sock.send(json.dumps(plaintext_msg_as_json).encode())
                            print(f"{current_time} | Plaintext message sent to {target_destination} at {target_ip}.\n")
                        except ConnectionResetError as e:
                            print("Connection has been terminated from the other side!")
                            break

                elif security == 'secure':
                    print(f"Initiating secure chat, with {target_destination} at {target_ip}...\n")
                    begin_announcer()
                    while True:
                        private_key = int(input("Please enter a random number between 1 and 23: "))
                        if 1 <= private_key <= 23:
                            break
                        else:
                            print("Invalid input. Please enter a number between 1 and 23.")
                    common_key = ((prime ** private_key) % divisor)
                    print(f"Generated common key: {common_key}")
                    tcp_cli_sock.send(json.dumps({"key": common_key}).encode())
                    print("Sent common key to server.")
                    response = json.loads(tcp_cli_sock.recv(2048).decode())
                    second_user_shared_key = int(response['key'])
                    print(f"Received server's shared key: {second_user_shared_key}")
                    combined_key = str((second_user_shared_key ** private_key) % divisor).encode()
                    print(f"Generated combined key: {combined_key.decode('utf-8')}")
                    combined_key = pad_or_truncate_key(combined_key)  # Pad or truncate the key before using it
                    print(f"Final key after padding or truncating: {combined_key.decode('utf-8')}")
                    while True:
                        own_plaintext_msg = input(f"{own_username}: ")
                        save_own_msg_to_history(target_destination, own_username, own_plaintext_msg)
                        own_encrypted_msg = pyDes.des(combined_key, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5).encrypt(own_plaintext_msg, padmode=2)
                        own_encrypted_msg_str = base64.b64encode(own_encrypted_msg).decode()  # Convert bytes to string
                        encrypted_msg_as_json = {'encrypted_message': own_encrypted_msg_str}
                        tcp_cli_sock.send(json.dumps(encrypted_msg_as_json).encode())
                        print(f"{current_time} | Encrypted message sent to {target_destination} at {target_ip}.\n")

                else:
                    print("Invalid input: Please specify 'secure' or 'unsecure' only.")
        elif choice == 'history':
            view_history = input("Which logs? (username): ")
            if(os.path.exists(f"chat_history_{view_history}.txt")):
                with open(f"chat_history_{view_history}.txt", 'r', encoding='utf-8') as ReadChatHistoryFile:
                    content = ReadChatHistoryFile.read()
                    print(content)
            else:
                print("The specified user could not be found.")
        else:
            print("Invalid input!\n")

    client_thread = threading.Thread(target=handle_client, args=(tcp_cli_sock))
    client_thread.start()

chat_initiator()