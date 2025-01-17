
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import random
import urllib.parse

coin_count = 0.0
click_count = 0
captcha_code = ""
is_captcha_active = False

def generate_captcha():
    return str(random.randint(100, 999))

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global coin_count, click_count, captcha_code, is_captcha_active

        if self.path.startswith('/click'):
            click_count += 1
            if click_count >= 1000 and not is_captcha_active:
                is_captcha_active = True
                captcha_code = generate_captcha()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                updated_content = content.replace('<span id="coin-count">0.00</span>', f'<span id="coin-count">{coin_count:.2f}</span>')
                updated_content = updated_content.replace('<div class="overlay" id="overlay">', f'<div class="overlay active" id="overlay">')
                updated_content = updated_content.replace('<p id="popup-message"></p>',f'<p id="popup-message">Введите капчу: <input type="text" id="captcha-input"> <button id="captcha-submit">Ок</button></p>')
                self.wfile.write(updated_content.encode('utf-8'))
            else:
               coin_count += 0.01
               self.send_response(200)
               self.send_header('Content-type', 'text/html')
               self.end_headers()
               with open('index.html', 'r', encoding='utf-8') as f:
                  content = f.read()
               updated_content = content.replace('<span id="coin-count">0.00</span>', f'<span id="coin-count">{coin_count:.2f}</span>')
               self.wfile.write(updated_content.encode('utf-8'))


        elif self.path.startswith('/check_captcha'):
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            input_captcha = query_params.get('captcha', [''])[0]

            if input_captcha == captcha_code:
                is_captcha_active = False
                click_count = 0
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                updated_content = content.replace('<span id="coin-count">0.00</span>', f'<span id="coin-count">{coin_count:.2f}</span>')
                updated_content = updated_content.replace('<div class="overlay active" id="overlay">', f'<div class="overlay" id="overlay">')
                updated_content = updated_content.replace(f'<p id="popup-message">Введите капчу: <input type="text" id="captcha-input"> <button id="captcha-submit">Ок</button></p>', '<p id="popup-message"></p>')
                self.wfile.write(updated_content.encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                updated_content = content.replace('<span id="coin-count">0.00</span>',f'<span id="coin-count">{coin_count:.2f}</span>' )
                updated_content = updated_content.replace('<p id="popup-message"></p>',f'<p id="popup-message">Неверная капча! <input type="text" id="captcha-input"> <button id="captcha-submit">Ок</button></p>')
                self.wfile.write(updated_content.encode('utf-8'))


        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            updated_content = content.replace('<span id="coin-count">0.00</span>', f'<span id="coin-count">{coin_count:.2f}</span>')
            self.wfile.write(updated_content.encode('utf-8'))

        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('style.css', 'r', encoding='utf-8') as f:
                content = f.read()
            self.wfile.write(content.encode('utf-8'))
        elif self.path.endswith('.js'):
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            with open(self.path[1:], 'r', encoding='utf-8') as f:
                content = f.read()
            self.wfile.write(content.encode('utf-8'))
        elif self.path.endswith(('.png', '.jpg', '.jpeg')):
             self.send_response(200)
             self.send_header('Content-type', 'image/' + self.path.split('.')[-1])
             self.end_headers()
             with open(self.path[1:], 'rb') as f:
                 content = f.read()
             self.wfile.write(content)

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
