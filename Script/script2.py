from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import requests
 
WEBHOOK_URL = 'https://webhook.site/ea1edc64-1ab5-4483-9e86-8268ddff65e0'
 
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        user_agent = self.headers.get('User-Agent')
        with open('user_agents.txt', 'a') as f:
            f.write(user_agent + '\n')
        try:
            requests.get(WEBHOOK_URL, headers={'User-Agent': user_agent}, verify=False)
        except Exception as e:
            logging.error(f'Error enviando a Webhook.site: {e}')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'User-Agent capturado exitosamente. (Revisa el archivo user_agents.txt)')
        logging.info(f'User-Agent: {user_agent}')
 
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Servidor HTTP levantado en el puerto 8080. (Accede a localhost:8080 para verificar)')
    httpd.serve_forever()
 