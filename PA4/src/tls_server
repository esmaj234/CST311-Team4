import ssl
import sys
import http.server

server_port = 443
server_addr = '10.0.1.3'


ssl_key_file = "./web-key.pem"
ssl_certificate_file = "./web-cert.pem"

if __name__ == '__main__':
  context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
  context.load_cert_chain(ssl_certificate_file, ssl_key_file)
  
  
  handler = http.server.SimpleHTTPRequestHandler
  
  httpd = http.server.HTTPServer((server_addr, server_port), handler)
  httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
  print('The server is ready to receive...')
  httpd.serve_forever()
