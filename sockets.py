import socket
import argparse
import base64
import os
import ssl

parser = argparse.ArgumentParser(description="HTTP client")
parser.add_argument("-V", "--verb", required=True, help="HTTP Verb (ex: post)")
parser.add_argument("-H", "--host", required=True, help="Hostname (ex: ptl-xxxxx.libcurl.so)")
parser.add_argument("-p", "--path", help="Path com querystring (ex: /pentesterlab?key=please)")
parser.add_argument("-c", "--cookie", help="Cookie (ex: key=please)")
parser.add_argument("-ct", "--contenttype", help="Content-Type (ex: key/please)")
parser.add_argument("-ua", "--useragent", help="User-Agent")
parser.add_argument("-al", "--acceptlanguage", help="Accept-Language (ex: key-please)")
parser.add_argument("-ah", "--anyheader", action="append", help="Any custom header (e.g. X-Header: Value). Can be used multiple times.")
parser.add_argument("-ab", "--authbasic", help="Basic Authentication (ex: key:please)")
parser.add_argument("-at", "--authtoken", help="Bearer Token (ex: token_value)")

parser.add_argument("-ws", "--websocket", action="store_true", help="Enable WebSocket mode")
parser.add_argument("-wm", "--wsmessage", help="Message to send over WebSocket (ex: key)")

body_group = parser.add_mutually_exclusive_group()
body_group.add_argument("-bj", "--json", help="JSON Body (ex: '{\"key\": \"value\"}')")
body_group.add_argument("-bf", "--form", help="form-urlencoded Body (ex: key=value)")
body_group.add_argument("-bx", "--xml", help="XML Body (ex: '<key>value</key>')")
body_group.add_argument("-by", "--yaml", help="YAML Body (ex: ' key: please')")
body_group.add_argument("-br", "--raw", help="Raw Body (text/plain)")

args = parser.parse_args()

if args.websocket:
    def generate_ws_key():
        return base64.b64encode(os.urandom(16)).decode()

    def encode_ws_frame(message):
        payload = message.encode()
        frame = bytearray([0x81])  

        length = len(payload)
        if length <= 125:
            frame.append(0x80 | length)  
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame += len(payload).to_bytes(2, byteorder='big')
        else:
            frame.append(0x80 | 127)
            frame += len(payload).to_bytes(8, byteorder='big')

        mask = os.urandom(4)
        frame += mask
        masked_payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        frame += masked_payload

        return frame

    def decode_ws_frame(sock):
        first_byte = sock.recv(1)
        second_byte = sock.recv(1)
        
        if not first_byte or not second_byte:
            return ""

        fin = (first_byte[0] >> 7) & 1
        opcode = first_byte[0] & 0x0F
        masked = (second_byte[0] >> 7) & 1
        payload_len = second_byte[0] & 0x7F

        if payload_len == 126:
            extended = sock.recv(2)
            payload_len = int.from_bytes(extended, byteorder='big')
        elif payload_len == 127:
            extended = sock.recv(8)
            payload_len = int.from_bytes(extended, byteorder='big')

        if masked:
            masking_key = sock.recv(4)
            masked_data = sock.recv(payload_len)
            data = bytes(b ^ masking_key[i % 4] for i, b in enumerate(masked_data))
        else:
            data = sock.recv(payload_len)

        return data.decode(errors="replace")  

    path = args.path or "/"
    ws_key = generate_ws_key()

    handshake = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {args.host}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {ws_key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )

    sock = socket.create_connection((args.host, 443))
    context = ssl.create_default_context()
    sock = context.wrap_socket(sock, server_hostname=args.host)
    sock.send(handshake.encode())

    response = sock.recv(4096).decode()
    if "101 Switching Protocols" not in response:
        print("[!] WebSocket handshake failed")
        exit()

    if args.wsmessage:
        sock.send(encode_ws_frame(args.wsmessage))
        print(decode_ws_frame(sock))

    sock.close()
    exit()

s = socket.socket()
s.connect((args.host, 80))

request = f"{args.verb.upper()} "

def ifcontenttype():
    global content_type_exists
    content_type_exists = False
    if args.anyheader:
        for header in args.anyheader:
            if "Content-Type:" in header:
                content_type_exists = True
                break
    return content_type_exists

if args.path:
    request += args.path.replace(" ", "%20")

request += " HTTP/1.1\r\n"
request += f"Host: {args.host}\r\n"

if args.cookie:
    request += f"Cookie: {args.cookie}\r\n"

if args.contenttype:
    request += f"Content-Type: {args.contenttype}\r\n"

if args.useragent:
    request += f"User-Agent: {args.useragent}\r\n"

if args.acceptlanguage:
    request += f"Accept-Language: {args.acceptlanguage}\r\n"

if args.anyheader:
    for header in args.anyheader:
        request += f"{header}\r\n"

if args.authbasic:
    credentials = base64.b64encode(args.authbasic.encode()).decode()
    request += f"Authorization: Basic {credentials}\r\n"

if args.authtoken:
    request += f"Authorization: Bearer {args.authtoken}\r\n"

body = ""

if args.json:
    body = args.json
    if not ifcontenttype():
        request += "Content-Type: application/json\r\n"

if args.form:
    body = args.form
    if not ifcontenttype():
        request += "Content-Type: application/x-www-form-urlencoded\r\n"

if args.xml:
    body = args.xml
    if not ifcontenttype():
        request += "Content-Type: application/xml\r\n"

if args.yaml:
    body = args.yaml
    if not ifcontenttype():
        request += "Content-Type: application/yaml\r\n"

if args.raw:
    body = args.raw
    if not ifcontenttype():
        request += "Content-Type: text/plain\r\n"

if body:
    request += f"Content-Length: {len(body.encode())}\r\n"

request += "Connection: close\r\n"
request += "\r\n"

if body:
    request += body

print(request)
s.send(request.encode())

response = b""
while True:
    data = s.recv(4096)
    if not data:
        break
    response += data

s.close()
print(response.decode())


# python3 sockets.py -V post -H ptl-0d282d11-8e71e5a5.libcurl.so -p /pentesterlab -c key=please
# multipart with file: python3 sockets.py -V post -H ptl-ebb6e78e-6df06d4b.libcurl.so -p /pentesterlab -ah "Content-Type: multipart/form-data; boundary=meu_boundary" --raw "$(cat multipart-with-file.txt)"
# -bx '<key value="&quot;please"></key>'