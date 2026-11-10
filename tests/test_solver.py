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

    def test_sarrus_api(self):
        for values, expected in [([1,1,2,3,0,1,2,1,0],7), ([0,1,-5,0,2,-7,0,3,6],0)]:
            status, raw = self.request('POST','/api/solve',json.dumps({'operation':'determinant','dimension':3,'method':'sarrus','values':values}).encode())
            self.assertEqual(status,200)
            self.assertEqual(number(json.loads(raw)['result']['determinant']),expected)
        status, raw = self.request('POST','/api/solve',json.dumps({'operation':'determinant','values':[1]*12}).encode())
        self.assertEqual(status,400)
        self.assertFalse(json.loads(raw)['ok'])

    def test_unknown_path_returns_404(self):
        status, _=self.request('GET','/solver.py')
        self.assertEqual(status,404)



class SarrusTests(unittest.TestCase):
    exercises = [
        ([3,2,1,5,-2,-3,-2,4,4], 0),
        ([-1,2,0,0,1,-2,3,5,3], -25),
        ([4,1,2,3,0,1,2,-1,4], -12),
        ([1,2,0,-1,-3,-2,0,4,1], 7),
        ([1,1,2,3,0,1,2,1,0], 7),
        ([-1,3,-2,0,-1,2,1,4,2], 14),
        ([1,2,3,2,4,6,-1,-2,5], 0),
        ([0,1,-5,0,2,-7,0,3,6], 0),
    ]

    def test_all_eight_exercises(self):
        for values, expected in self.exercises:
            with self.subTest(values=values):
                answer = solve({'operation':'determinant','values':values})
                self.assertEqual(number(answer['result']['determinant']),expected)
                self.assertEqual(answer['status'],'determinant')
                self.assertEqual(len(answer['products']),6)
                self.assertEqual(len(answer['steps']),6)
                self.assertTrue(answer['checks'][0]['pass'])
                self.assertEqual([len(row) for row in answer['extendedMatrix']],[5,5,5])
                self.assertEqual(number(answer['sums']['down'])-number(answer['sums']['up']),expected)

    def test_large_intermediate_values_remain_exact(self):
        answer = solve({'operation':'determinant','values':['1000000000000',0,0,0,'1000000000000',0,0,0,'1000000000000']})
        self.assertEqual(answer['result']['determinant'],str(10**36))
        self.assertTrue(answer['checks'][0]['pass'])

    def test_signed_products_and_subtraction(self):
        answer = solve({'operation':'determinant','values':self.exercises[0][0]})
        self.assertEqual([number(p['value']) for p in answer['products']],[-24,12,20,4,-36,40])
        self.assertEqual(answer['sums'],{'down':'8','up':'8'})

    def test_fractions_and_decimals(self):
        answer = solve({'operation':'determinant','values':['1/2',0,0,0,'-1.5',0,0,0,'2/3']})
        self.assertEqual(number(answer['result']['determinant']),Fraction(-1,2))
        self.assertEqual(answer['result']['decimal'],'−0.5000')
        self.assertTrue(answer['checks'][0]['pass'])

    def test_against_permutation_definition(self):
        import itertools
        import random
        rng = random.Random(74)
        for _ in range(60):
            values = [rng.randint(-8,8) for _ in range(9)]
            total = 0
            for perm in itertools.permutations(range(3)):
                inversions = sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3))
                total += (-1)**inversions * values[perm[0]]*values[3+perm[1]]*values[6+perm[2]]
            self.assertEqual(number(solve({'operation':'determinant','values':values})['result']['determinant']),total)

    def test_invalid_inputs(self):
        cases = [{'operation':'other'}, {'operation':'determinant','dimension':2,'values':[1]*9},
                 {'operation':'determinant','dimension':True,'values':[1]*9},
                 {'operation':'determinant','dimension':'3','values':[1]*9},
                 {'operation':'determinant','method':'cramer3','values':[1]*9},
                 {'operation':'determinant','method':{},'values':[1]*9}]
        for values in ([],[1]*8,[1]*10,[[1]*3]*3,['1/0']*9,['hola']*9,[True]*9,[None]*9,['NaN']*9):
            cases.append({'operation':'determinant','values':values})
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                solve(payload)

class Solver3Tests(unittest.TestCase):
    example = [2,1,-1,8,-3,-1,2,-11,-2,1,2,-3]

    def test_unique_negative_and_determinants(self):
        answer = solve({'dimension': 3, 'method': 'cramer3', 'values': self.example})
        self.assertEqual(answer['status'], 'unique')
        self.assertEqual([number(answer['result'][v]) for v in 'xyz'], [2,3,-1])
        self.assertEqual([number(answer['determinants'][v]['value']) for v in ('D','Dx','Dy','Dz')], [-1,-2,-3,1])
        self.assertEqual(len(answer['checks']), 3)
        self.assertTrue(all(c['pass'] for c in answer['checks']))
        self.assertEqual(len(answer['steps']), 6)

    def test_fraction_decimal_and_negative(self):
        answer = solve({'dimension': 3, 'values': ['1/2',0,0,'1/3',0,'-1.5',0,3,0,0,'-2','1/2']})
        self.assertEqual([number(answer['result'][v]) for v in 'xyz'], [Fraction(2,3),-2,Fraction(-1,4)])
        self.assertTrue(all(c['pass'] for c in answer['checks']))

    def test_zero_determinant_ranks(self):
        cases = [
            ([1,1,1,3,2,2,2,6,0,0,0,0], 'infinite', 1, 1),
            ([1,1,1,3,2,2,2,7,0,0,0,0], 'none', 1, 2),
            ([0]*12, 'infinite', 0, 0),
            ([0,0,0,1]+[0]*8, 'none', 0, 1),
            ([1,0,1,2,0,1,1,3,1,1,2,6], 'none', 2, 3),
            ([0,1,1,2,1,0,1,3,1,1,2,5], 'infinite', 2, 2),
        ]
        for values, status, ra, rab in cases:
            with self.subTest(values=values):
                answer = solve({'dimension':3, 'values':values})
                self.assertEqual(answer['status'],status)
                self.assertIsNone(answer['result'])
                self.assertEqual(answer['ranks'], {'A':ra,'augmented':rab})
                self.assertEqual(number(answer['determinants']['D']['value']),0)

    def test_invalid_payloads(self):
        cases = [None, [], {'dimension':4}, {'dimension':'3'}, {'dimension':True}, {'dimension':3.0},
                 {'dimension':3,'values':[1]*6}, {'dimension':3,'values':[1]*13},
                 {'dimension':3,'values':self.example,'method':'sustitucion'},
                 {'dimension':2,'values':[1]*6,'method':[]},
                 {'dimension':3,'values':self.example,'method':[] }]
        for bad in ['', 'hola', '1/0', 'NaN', 'Infinity', True, None, {}, '1e100', '1/10000000000']:
            cases.append({'dimension':3,'values':[bad]+self.example[1:]})
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                solve(payload)


class API3Tests(APITests):
    def test_api3(self):
        status, raw = self.request('POST','/api/solve',json.dumps({'dimension':3,'method':'cramer3','values':Solver3Tests.example}).encode())
        answer = json.loads(raw)
        self.assertEqual(status,200)
        self.assertEqual([number(answer['result'][v]) for v in 'xyz'],[2,3,-1])
        self.assertTrue(all(c['pass'] for c in answer['checks']))

    def test_api3_invalid(self):
        for payload in [{'dimension':3,'values':[1]*11}, {'dimension':3,'method':'cramer','values':[1]*12},
                        {'dimension':5,'values':[1]*12}, {'dimension':3,'values':['1/0']*12},
                        {'dimension':3,'values':[1]*12,'method':{}}, None]:
            status, raw = self.request('POST','/api/solve',json.dumps(payload).encode())
            self.assertEqual(status,400)
            self.assertFalse(json.loads(raw)['ok'])

if __name__ == '__main__':
    unittest.main()
