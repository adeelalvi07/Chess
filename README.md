# Chess
 PYTHON CHESS GAME | SOCKET PROGRAMMING + GUI PROJECT
📌 PROJECT SUMMARY
This is a two-player Chess Game implemented in Python using socket programming for network communication and Tkinter for the graphical interface. It demonstrates the integration of networking with GUI, real-time player interaction, and basic client-server architecture.

🎮 GAME FEATURES
✅ Two-player networked chess

🔄 Real-time move synchronization

♟️ Click-based piece selection and movement

❗ Invalid move detection

🪟 Simple and clean GUI built using Tkinter

📤 Server-client architecture for remote play

🖼️ Chess board and pieces rendered using PIL

⚙️ HOW TO RUN
REQUIREMENTS

Required libraries:

python
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
Install missing dependencies via:

bash
Copy
Edit
pip install pillow
FILE STRUCTURE
bash
Copy
Edit
PythonChessGame/
│
├── server.py       # Start this first
├── player1.py      # Connects as Player 1
├── player2.py      # Connects as Player 2
├── assets/         # (optional) Images for pieces and board
└── README.txt
INSTRUCTIONS TO PLAY
Start the server:

Run server.py on one device.

Note the IP address (use ipconfig or ifconfig).

Set the IP address:

In both player1.py and player2.py, update the server IP to match the server machine's IP.

Run player files:

On two devices (or separate terminals), run player1.py and player2.py.

Enjoy the game!

🧠 CONCEPTS USED
Networking: socket and threading for multiplayer support

GUI: Tkinter used for drawing board and capturing events

Concurrency: Threads handle listening/sending data

OOP: Classes encapsulate board and move logic

Error Handling: Detect and reject illegal moves

🖼️ SCREENSHOTS
✔️ User Interface

👨‍💻 DEVELOPERS
Name: Muhammad Adeel, Saad Tariq

Course: Computer Networks

Semester: 3rd Semester

Institution: Air University Islamabad

