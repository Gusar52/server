# server
# http-server: a simple static HTTP server
HTTP Server with Virtual Hosts Support

Python Version
License: MIT

A lightweight HTTP server with virtual hosts support developed by Artem Skvorok and Ivan Gusarov.
## Key Features
  - 🚀 Multi-threaded request handling
  - 🌐 Virtual hosts support (multiple domains on single IP)
  - 📁 Static file serving with directory indexing
  - 🔄 Proxy pass functionality
  - ⚙️ JSON configuration
  - 📊 Detailed request logging

## 1. To use our server, clone the repository and install dependencies:
```bash
git clone https://github.com/Gusar52/server/
cd http-server
pip install -r requirements.txt
```
## 2. Edit config.json to set up your virtual hosts
## 3. Start the server
To run our server you can run tis command:
```bash
python main.py
```
## 4. Now you can visit your host to view your server and you will see the information in terminal
## For more information about functionality use
```bash
python main.py --help
```

## Project structure
```
server/
├── src/
│   ├── http_server.py       
│   └── virtual_server_manager.py 
├── main.py
├── config.json
└── requirements.txt
```

## Testing
```bash 
python test_server.py
```
