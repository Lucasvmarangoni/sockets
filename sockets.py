import socket
import argparse

parser = argparse.ArgumentParser(description="HTTP client")
parser.add_argument("-V", "--verb", required=True, help="HTTP Verb (ex: post)")
parser.add_argument("-H", "--host", required=True, help="Hostname (ex: ptl-xxxxx.libcurl.so)")
parser.add_argument("-p", "--path", help="Path com querystring (ex: /pentesterlab?key=please)")
parser.add_argument("-c", "--cookie", help="Cookie (ex: key=please)")
parser.add_argument("-ct", "--contenttype", help="Content-Type (ex: key/please)")
parser.add_argument("-ua", "--useragent", help="User-Agent")
parser.add_argument("-al", "--acceptlanguage", help="Accept-Language (ex: key-please)")
parser.add_argument("-ah", "--anyheader", action="append", help="Any custom header (e.g. X-Header: Value). Can be used multiple times.")

body_group = parser.add_mutually_exclusive_group()
body_group.add_argument("-bj", "--json", help="JSON Body (ex: '{\"key\": \"value\"}')")
body_group.add_argument("-bf", "--form", help="form-urlencoded Body (ex: key=value)")
body_group.add_argument("-bx", "--xml", help="XML Body (ex: '<key>value</key>')")
body_group.add_argument("-br", "--raw", help="Raw Body (text/plain)")

args = parser.parse_args()

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
    return  content_type_exists

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

# python3 sockets.py -H ptl-0d282d11-8e71e5a5.libcurl.so -p /pentesterlab -c key=please
# multipart with file: python3 sockets.py -V post -H ptl-ebb6e78e-6df06d4b.libcurl.so -p /pentesterlab -ah "Content-Type: multipart/form-data; boundary=meu_boundary" --raw "$(cat multipart-with-file.txt)"