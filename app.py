#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servidor local para LÚMINA (Python 3.10+, sin paquetes externos).

Ejecutar: python app.py
Probar: python -m unittest discover -s tests -v
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import webbrowser
from solver import solve

ROOT = Path(__file__).resolve().parent
# Lista explícita: solo sirve archivos necesarios, evita rutas arbitrarias.
STATIC_FILES = {
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/index.html': ('index.html', 'text/html; charset=utf-8'),
    '/css/styles.css': ('css/styles.css', 'text/css; charset=utf-8'),
    '/js/app.js': ('js/app.js', 'text/javascript; charset=utf-8'),
}

class WebHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if self.path.startswith('/api/'):
            super().log_message(fmt, *args)

    def respond(self, payload: bytes, mime: str, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(payload)

    def respond_json(self, data: dict, status: int = 200):
        self.respond(json.dumps(data, ensure_ascii=False).encode('utf-8'),
                        'application/json; charset=utf-8', status)

    def do_GET(self):
        if self.path in STATIC_FILES:
            path, mime = STATIC_FILES[self.path]
            try:
                self.respond((ROOT / path).read_bytes(), mime)
            except OSError:
                self.respond(b'Archivo no disponible', 'text/plain; charset=utf-8', 500)
        elif self.path == '/health':
            self.respond_json({'ok': True, 'app': 'Lumina'})
        elif self.path == '/favicon.ico':
            self.respond(b'', 'image/x-icon')
        else:
            self.respond(b'Ruta no encontrada', 'text/plain; charset=utf-8', 404)

    def do_POST(self):
        if self.path != '/api/solve':
            self.respond_json({'ok': False, 'error': 'Ruta no encontrada'}, 404)
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 1 <= size <= 8192:
                raise ValueError('La solicitud no tiene un tamaño válido.')
            data = json.loads(self.rfile.read(size))
            answer = solve(data)
            self.respond_json(answer)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.respond_json({'ok': False, 'error': str(exc)}, 400)
        except Exception:
            self.respond_json({'ok': False, 'error': 'Error interno al resolver el sistema.'}, 500)


def main():
    parser = argparse.ArgumentParser(description='LÚMINA | Álgebra Studio')
    parser.add_argument('--port', type=int, default=0, help='Puerto local; 0 elige uno libre')
    parser.add_argument('--no-browser', action='store_true', help='No abrir navegador')
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), WebHandler)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'\nLÚMINA | Álgebra Studio\nAbre esta dirección: {url}')
    print('Para cerrar, presiona Ctrl + C.\n')
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Aplicación cerrada.')
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
