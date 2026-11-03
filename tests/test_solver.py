"""Pruebas con unittest (incluido con Python)."""
import json
from fractions import Fraction
from http.server import ThreadingHTTPServer
from http.client import HTTPConnection
from pathlib import Path
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import WebHandler
from solver import solve, number

class SolverTests(unittest.TestCase):
    def check_solution(self, values, method, x, y):
        result = solve({'values': values, 'method': method})
        self.assertTrue(result['ok'])
        self.assertEqual(result['status'], 'unique')
        self.assertEqual(number(result['result']['x']), Fraction(x))
        self.assertEqual(number(result['result']['y']), Fraction(y))
        self.assertTrue(all(check['pass'] for check in result['checks']))
        self.assertGreaterEqual(len(result['steps']), 3)

    def test_sustitucion_del_taller(self):
        self.check_solution([3,-1,7,1,2,4], 'sustitucion', Fraction(18,7), Fraction(5,7))

    def test_igualacion_del_taller(self):
        self.check_solution([5,2,16,1,-1,1], 'igualacion', Fraction(18,7), Fraction(11,7))

    def test_todos_los_metodos(self):
        for method in ('sustitucion','igualacion','reduccion','cramer'):
            with self.subTest(method=method):
                self.check_solution([2,3,13,4,-1,5], method, 2, 3)

    def test_sistemas_especiales(self):
        for values, expected in [([1,1,2,2,2,4],'infinite'), ([1,1,2,2,2,5],'none'),
                                    ([0,0,0,0,0,0],'infinite'), ([0,0,1,0,0,0],'none')]:
            with self.subTest(values=values):
                self.assertEqual(solve({'values': values, 'method': 'cramer'})['status'], expected)

    def test_fracciones_decimales_y_negativos(self):
        self.check_solution(['1/2', '1.5', 5, -1, 1, 0], 'cramer', Fraction(5,2), Fraction(5,2))

    def test_rechaza_entrada_invalida(self):
        for invalid in [[], [1, 2], [1,2,'hola',4,5,6], [1,2,'1/0',4,5,6]]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    solve({'values': invalid, 'method': 'sustitucion'})

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1',0), WebHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, path, body=None):
        connection = HTTPConnection('127.0.0.1',self.server.server_port, timeout=5)
        headers = {'Content-Type': 'application/json'} if body is not None else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read()
        status = response.status
        connection.close()
        return status, content

    def test_static_files(self):
        for url, starts in [('/', b'<!doctype'),('/index.html', b'<!doctype'),
                            ('/css/styles.css', b'/* L'), ('/js/app.js', b'/* L')]:
            with self.subTest(url=url):
                status, data = self.request('GET',url)
                self.assertEqual(status,200)
                self.assertTrue(data.startswith(starts), data[:40])

    def test_api(self):
        body=json.dumps({'method':'igualacion','values':[5,2,16,1,-1,1]}).encode()
        status, data = self.request('POST','/api/solve',body)
        self.assertEqual(status,200)
        answer=json.loads(data)
        self.assertEqual(answer['result']['x'],'18/7')
        self.assertEqual(answer['result']['y'],'11/7')

    def test_api_bad_input(self):
        body=json.dumps({'values':[1,2,3], 'method':'igualacion'}).encode()
        status, data = self.request('POST','/api/solve',body)
        self.assertEqual(status,400)
        self.assertFalse(json.loads(data)['ok'])

    def test_unknown_path_returns_404(self):
        status, _=self.request('GET','/solver.py')
        self.assertEqual(status,404)

if __name__ == '__main__':
    unittest.main()
