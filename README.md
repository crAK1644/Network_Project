# 🖧 Network Communication Project (TCP & UDP)

This project demonstrates fundamental network communication principles using Python's built-in `socket` module. It includes both **TCP** and **UDP** client-server models, useful for learning and testing real-time data transmission protocols.

## 📁 Project Structure

```
Network_Project/
├── TCP CLIENT.py     # Python TCP Client
├── TCP SERVER.py     # Python TCP Server
├── UDP CLIENT.py     # Python UDP Client
├── UDP SERVER.py     # Python UDP Server
├── README.md          # This file
└── .idea/             # (Optional) IDE configuration files
```

## 🚀 How to Run

### Prerequisites

- Python 3.x installed
- Run scripts in separate terminal windows or tabs

---

### TCP Communication

1. **Start the TCP Server**
   ```bash
   python "TCP SERVER.py"
   ```

2. **Run the TCP Client in another terminal**
   ```bash
   python "TCP CLIENT.py"
   ```

---

### UDP Communication

1. **Start the UDP Server**
   ```bash
   python "UDP SERVER.py"
   ```

2. **Run the UDP Client**
   ```bash
   python "UDP CLIENT.py"
   ```

## 🧠 Learning Objectives

- Understand the differences between **TCP** (connection-oriented) and **UDP** (connectionless) protocols
- Practice establishing and managing client-server connections
- Gain experience with `socket`, `bind`, `listen`, `send`, and `recv` functions in Python

## 📦 Dependencies

- No external libraries required — uses Python's standard `socket` module

## ✍️ Author

Developed as part of a Computer Networks course  
Feel free to fork, modify, and reuse for academic or learning purposes.


