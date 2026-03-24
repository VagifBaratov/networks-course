import email.utils
import socket
import os
import sys
import signal
import mimetypes

HOST = 'localhost'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

server_running = True
server_socket = None

def signal_handler(sig, frame):
    global server_running, server_socket
    print("\nSigint received")
    server_running = False
    if server_socket:
        server_socket.close()
        print("Server socket is closed")

def parse_request(request_data):
    try:
        lines = request_data.split('\n')
        if lines:
            first_line = lines[0].split()
            if len(first_line) >= 2:
                method = first_line[0]
                path = first_line[1]
                return path
    except Exception as e:
        print(f"Parse error: {e}")
    return '/'

def get_file_path(path):
    filename = path.lstrip('/')
    
    safe_path = os.path.abspath(os.path.join(BASE_DIR, filename))
    if not safe_path.startswith(BASE_DIR):
        return None
    
    return safe_path

def read_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except (IOError, OSError):
        return None

def get_file_last_modified(file_path):
    try:
        mtime = os.path.getmtime(file_path)
        last_modified = email.utils.formatdate(mtime, usegmt=True)
        return last_modified
    except (IOError, OSError):
        return None

def create_response(status_code, status_text, headers, content):
    response = f"HTTP/1.1 {status_code} {status_text}\r\n"
    for key, value in headers.items():
        response += f"{key}: {value}\r\n"
    response += "\r\n"
    
    if isinstance(content, bytes):
        return response.encode() + content
    else:
        return response.encode() + content.encode()

def handle_request(client_socket, client_address):
    try:
        client_socket.settimeout(5)
        
        request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')

        path = parse_request(request_data)
        file_path = get_file_path(path)

        if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
            
            last_modified = get_file_last_modified(file_path)
            if_modified_since = None
            for line in request_data.split('\n'):
                if line.lower().startswith('if-modified-since:'):
                    if_modified_since = line.split(':', 1)[1].strip()
                    break
            
            if if_modified_since and last_modified:
                try:
                    if_modified_time = email.utils.parsedate_to_datetime(if_modified_since)
                    file_time = email.utils.parsedate_to_datetime(last_modified)
                    
                    if file_time <= if_modified_time:
                        response = create_response(
                            304, "Not Modified",
                            {
                                "Last-Modified": last_modified,
                                "Connection": "close",
                            },
                            ""  
                        )
                        print(f"File not modified (304): {file_path}")
                        client_socket.sendall(response)
                        return
                except Exception as e:
                    print(f'Error in parsing "If-Modified-Since": {e}')

            content = read_file(file_path)
            if content is not None:
                content_type, _ = mimetypes.guess_type(file_path)
                if content_type is None:
                    content_type = "application/octet-stream"  # двоичные данные по умолчанию
                
                response = create_response(
                    200, "OK",
                    {
                        "Content-Type": content_type,
                        "Content-Length": len(content),
                        "Connection": "close",
                        "Last-Modified": last_modified, 
                    },
                    content
                )
                print(f"Founded file: {file_path}")
            else:
                error_content = "<html><body><h1>500 Internal Server Error</h1></body></html>"
                response = create_response(
                    500, "Internal Server Error",
                    {"Content-Type": "text/html", "Connection": "close"},
                    error_content
                )
                print(f"Error in reading: {file_path}")
        else:
            error_content = "<html><body><h1>404 Not found</h1></body></html>"
            response = create_response(
                404, "Not Found",
                {"Content-Type": "text/html", "Content-Length": len(error_content), "Connection": "close"},
                error_content
            )
            print(f"Not founf: {file_path if file_path else path}")
        
        client_socket.sendall(response)
        
    except socket.timeout:
        print(f"Timeout in reading: {client_address}")
    except Exception as e:
        print(f"Request processing error: {e}")
        
        error_content = "<html><body><h1>500 Internal Server Error</h1></body></html>"
        try:
            response = create_response(
                500, "Internal Server Error",
                {"Content-Type": "text/html", "Connection": "close"},
                error_content
            )
            client_socket.sendall(response)
        except:
            pass
    finally:
        client_socket.close()

def start_server():
    global server_running, server_socket
    
    signal.signal(signal.SIGINT, signal_handler)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        
        server_socket.settimeout(1)
        
        print(f"\nServer running")
        print(f"Adress: http://{HOST}:{PORT}")
        print(f"Base dirrectory: {BASE_DIR}")
        
        while server_running:
            try:
                client_socket, client_address = server_socket.accept()
                print(f"\nClient is connected: {client_address}")
                
                handle_request(client_socket, client_address)
                print(f"Connection with {client_address} closed")
                print("-" * 50)
                
            except socket.timeout:
                continue
            except OSError as e:
                if server_running:
                    print(f"Socket error: {e}")
                break
                
    except Exception as e:
        if server_running:
            print(f"Server error: {e}")
    finally:
        if server_socket:
            server_socket.close()
        print("\nServer is stopped")

if __name__ == "__main__":
    PORT = int(sys.argv[1])
    start_server()