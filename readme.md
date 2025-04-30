# Pentest-oriented CLI tool for sending crafted HTTP and WebSocket requests

This tool has been developed for the pentesterlab HTML Badge exercises.

- My PentesterLab profile: <a href="https://pentesterlab.com/profile/lucasvm">lucasvm</a>
- My certificate of badge completion: <a href="https://pentesterlab.com/certs/a56c7ef2466da26a8dc39626a4a5b6">HTTP Badge</a>

It is a Python command-line tool that manually establishes socket connections to send HTTP/HTTPS and WebSocket requests, offering full control over verbs, headers, authentication, and request bodies for penetration testing purposes.

#### Usage
Run the script with:
```bash
python3 simplehttp.py [options]
```

#### Options
| Option | Description | Example |
|--------|-------------|---------|
| `-V`, `--verb` | **Required**. HTTP verb (e.g., GET, POST). | `-V post` |
| `-H`, `--host` | **Required**. Server hostname. | `-H example.com` |
| `-p`, `--path` | Path with query string. | `-p /api?key=value` |
| `-c`, `--cookie` | Request cookie. | `-c session=abc123` |
| `-ct`, `--contenttype` | Content-Type for the body. | `-ct application/json` |
| `-ua`, `--useragent` | Custom User-Agent. | `-ua "Mozilla/5.0"` |
| `-al`, `--acceptlanguage` | Accept-Language header. | `-al en-US` |
| `-ah`, `--anyheader` | Custom header (can be used multiple times). | `-ah "X-Custom: Value"` |
| `-ab`, `--authbasic` | Basic Authentication (user:pass). | `-ab user:pass` |
| `-at`, `--authtoken` | Bearer Token Authentication. | `-at token123` |
| `-ws`, `--websocket` | Enable WebSocket mode. | `-ws` |
| `-wm`, `--wsmessage` | Message to send over WebSocket. | `-wm "Hello"` |
| `-bj`, `--json` | JSON body. | `-bj '{"key": "value"}'` |
| `-bf`, `--form` | Form-urlencoded body. | `-bf key=value` |
| `-bx`, `--xml` | XML body. | `-bx '<key>value</key>'` |
| `-by`, `--yaml` | YAML body. | `-by 'key: value'` |
| `-br`, `--raw` | Raw text body. | `-br "text"` |

**Note**: Body options (`-bj`, `-bf`, `-bx`, `-by`, `-br`) are mutually exclusive.

#### Examples
1. **Simple POST request**:
   ```bash
   python3 simplehttp.py -V post -H ptl-0d282d11-8e71e5a5.libcurl.so -p /pentesterlab -c key=please
   ```

2. **POST with multipart/form-data**:
   ```bash
   python3 simplehttp.py -V post -H ptl-ebb6e78e-6df06d4b.libcurl.so -p /pentesterlab -ah "Content-Type: multipart/form-data; boundary=meu_boundary" --raw "$(cat multipart-with-file.txt)"
   ```

3. **POST with XML body**:
   ```bash
   python3 simplehttp.py -V post -H example.com -p /api -bx '<key value="please"></key>'
   ```

4. **WebSocket connection**:
   ```bash
   python3 simplehttp.py -H example.com -ws -wm "Hello, WebSocket!"
   ```

#### Output
- The constructed request is printed to the console.
- The server response is displayed after sending.

#### Limitations
- Supports only HTTP on port 80 and WebSocket on port 443 (with SSL).
- Does not handle redirects or complex errors automatically.
- WebSocket mode requires a compatible server.
