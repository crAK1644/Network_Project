from socket import *
import time
import json

udpClientSocket = socket(AF_INET, SOCK_DGRAM)  # opening new socket
udpClientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # allow broadcasting


def service_announcer():
    print("Welcome to the UDP CLIENT "
          "\n************************\n"
          "This client announces your presence to other users"
          "\n************************\n")

    username = input("Enter your username: ")
    username_to_json = {"username": username}

    with open("user_info_self.json", "w") as LocalUserInfo:
        LocalUserInfo.write(json.dumps(username_to_json))

    broadcast_addr = input(
        "Enter the broadcast address of the network that you want to connect (e.g., 192.168.1.255): ")

    print("Broadcasting your username to the network\n"
          "If you don't close this client, it will keep broadcasting every 8 seconds")

    server_address = (broadcast_addr, 6000)

    while True:
        message = json.dumps(username_to_json).encode("utf-8")
        udpClientSocket.sendto(message, server_address)
        time.sleep(8)


service_announcer()
