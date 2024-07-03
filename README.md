
# Backdoors Project

This project contains various scripts and tools for backdoor operations. It includes several Python scripts that perform different tasks related to backdoor functionality.

## Contents

- `backdoor.py`: Main backdoor script.
- `Dumper.py`: Script for dumping data.
- `server1.py`: Server-side script for handling backdoor connections.
- `lazagne`: Directory containing LaZagne-related modules.
- `winpwnage`: Directory containing WinPwnage-related modules.

## Setup

### Prerequisites

Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).

### Installation

1. Clone the repository or download the zip file and extract it.
2. Navigate to the project directory.
3. Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### Running the Scripts

- To run the main backdoor script:

```bash
python backdoor.py
```

- To run the server-side script:

```bash
python server1.py
```

### Dependencies

The project relies on the following third-party libraries:

- pynput
- opencv-python
- pyaudio
- numpy
- moviepy
- Pillow

These are specified in the `requirements.txt` file and can be installed using the instructions above.

## Usage

- `backdoor.py` is the main backdoor script. It includes functionalities for connecting to a remote server, capturing keystrokes, and more.
- `Dumper.py` is used for data dumping operations.
- `server1.py` sets up a server to handle incoming connections from the backdoor clients.
- The `lazagne` and `winpwnage` directories contain modules related to LaZagne and WinPwnage tools, respectively.

## BACKDOOR! Functions
Screenshot              - Capture a screenshot from the target
Audio                   - Record audio on the target
Screen Record           - Record the screen on the target
Webcam                  - Take a picture from the webcam
Keylogger               - Track and save keylogs on the target
Lock                    - Lock the target's workstation

Dump Password           - Dump passwords from the target (lazagne> https://github.com/AlessandroZ/LaZagne.git)

Privilege Escalation    - Elevate privileges to Admin or System (winpwnage> https://github.com/rootm0s/WinPwnage.git)

## License

This project is for educational and ethical hacking purposes only. Use it responsibly.

## Special thanks
AlessandroZ for 
rootm0s for 
