"""
Pruebas automáticas de los algoritmos.

Ejecución:  python -m unittest discover -s tests -v
"""

import os
import random
import sys
import unittest
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from laberinto.grafo import Grafo, ErrorGrafo  # noqa: E402
from laberinto import algoritmos as alg  # noqa: E402
from laberinto.configuraciones import (red_original, configuraciones_comparadas,  # noqa: E402
                                       caso_verificacion, contraejemplo_voraz)


def grafo_desde(vertices, arcos):
    g = Grafo()
    for v in vertices:
        g.agregar_vertice(v)
    for u, v in arcos:
        g.agregar_arco(u, v)
    return g


def todos_los_caminos(g, s, t):
    """Enumera todos los caminos simples s–t (solo para grafos pequeños)."""
    ady = g.lista_adyacencia()
    res = []

    def rec(u, camino):
        if u == t:
            res.append(list(camino))
            return
        for v in ady[u]:
            if v not in camino:
                camino.append(v)
                rec(v, camino)
                camino.pop()
    rec(s, [s])
    return res


def max_disjuntos_fuerza_bruta(g, s, t):
    """Máximo número de caminos arco-disjuntos por búsqueda exhaustiva."""
    caminos = [set(zip(c, c[1:])) for c in todos_los_caminos(g, s, t)]
    mejor = 0

    def rec(i, usados, k):
        nonlocal mejor
        mejor = max(mejor, k)
        for j in range(i, len(caminos)):
            if not (caminos[j] & usados):
                rec(j + 1, usados | caminos[j], k + 1)
    rec(0, set(), 0)
    return mejor


class TestModelo(unittest.TestCase):
    def test_restricciones(self):
        g = grafo_desde("abc", [("a", "b")])
        with self.assertRaises(ErrorGrafo):
            g.agregar_arco("a", "a")      # lazo
        with self.assertRaises(ErrorGrafo):
            g.agregar_arco("a", "b")      # repetido
        with self.assertRaises(ErrorGrafo):
            g.agregar_arco("b", "a")      # recíproco
        g.bloquear("a", "b")
        with self.assertRaises(ErrorGrafo):
            g.agregar_arco("b", "a")      # recíproco aunque esté bloqueado

    def test_modelo_inicial_valido(self):
        checks = alg.validar_modelo_completo(red_original(), "s", "t")
        self.assertTrue(all(ok for _, ok in checks), checks)


class TestCaminoMinimo(unittest.TestCase):
    def test_original(self):
        r = alg.bfs_camino_minimo(red_original(), "s", "t")
        self.assertEqual(r["longitud"], 4)
        self.assertTrue(alg.es_camino_valido(red_original(), r["camino"], "s", "t"))

    def test_sin_camino(self):
        g = grafo_desde("sat", [("s", "a"), ("t", "a")])
        r = alg.bfs_camino_minimo(g, "s", "t")
        self.assertFalse(r["existe"])
        self.assertIsNone(r["longitud"])
        f = alg.max_caminos_disjuntos(g, "s", "t")
        self.assertEqual((f["valor"], f["caminos"], f["corte"]), (0, [], []))

    def test_bloqueo_respetado(self):
        g = red_original()
        for a in [("G", "t"), ("H", "t"), ("I", "t")]:
            g.bloquear(*a)
        self.assertFalse(alg.bfs_camino_minimo(g, "s", "t")["existe"])
        g.restablecer("I", "t")
        self.assertEqual(alg.bfs_camino_minimo(g, "s", "t")["camino"][-2:], ["I", "t"])

    def test_dfs_no_garantiza_minimo(self):
        g = red_original()
        self.assertGreater(alg.dfs_camino(g, "s", "t")["longitud"],
                           alg.bfs_camino_minimo(g, "s", "t")["longitud"])


class TestFlujo(unittest.TestCase):
    def test_configuraciones(self):
        esperados = {"Original": (4, 3), "Modificación 1": (4, 2), "Modificación 2": (3, 2)}
        for nombre, _, g in configuraciones_comparadas():
            a = alg.analizar(g, "s", "t")
            self.assertEqual((a["minimo"]["longitud"], a["flujo"]["valor"]), esperados[nombre])
            self.assertTrue(all(ok for _, ok in a["verificacion"]), (nombre, a["verificacion"]))

    def test_caso_manual(self):
        a = alg.analizar(caso_verificacion(), "s", "t")
        self.assertEqual(a["minimo"]["longitud"], 2)
        self.assertEqual(a["flujo"]["valor"], 2)
        self.assertEqual(len(a["flujo"]["corte"]), 2)

    def test_contraejemplo_voraz(self):
        g = contraejemplo_voraz()
        self.assertEqual(alg.caminos_disjuntos_voraz(g, "s", "t")["valor"], 1)
        self.assertEqual(alg.max_caminos_disjuntos(g, "s", "t", "bfs")["valor"], 2)
        self.assertEqual(alg.max_caminos_disjuntos(g, "s", "t", "dfs")["valor"], 2)

    def test_aleatorio_contra_fuerza_bruta(self):
        """En 300 grafos aleatorios: flujo = fuerza bruta de caminos = fuerza bruta de corte."""
        rnd = random.Random(2026)
        for _ in range(300):
            n = rnd.randint(4, 7)
            vs = [str(i) for i in range(n)]
            pares = [(u, v) for u, v in combinations(vs, 2)]
            arcos = []
            for u, v in pares:
                if rnd.random() < 0.45:
                    arcos.append((u, v) if rnd.random() < 0.5 else (v, u))
            g = grafo_desde(vs, arcos)
            for a in list(g.arcos):
                if rnd.random() < 0.1:
                    g.bloquear(*a)
            s, t = rnd.sample(vs, 2)
            for est in ("bfs", "dfs"):
                f = alg.max_caminos_disjuntos(g, s, t, est)
                self.assertEqual(f["valor"], max_disjuntos_fuerza_bruta(g, s, t))
                kb, _ = alg.corte_minimo_fuerza_bruta(g, s, t, f["valor"])
                self.assertEqual(kb, f["valor"])
            a = alg.analizar(g, s, t)
            self.assertTrue(all(ok for _, ok in a["verificacion"]), a["verificacion"])
            todos = todos_los_caminos(g, s, t)
            if todos:
                self.assertEqual(a["minimo"]["longitud"], min(len(c) - 1 for c in todos))
            else:
                self.assertIsNone(a["minimo"]["longitud"])


if __name__ == "__main__":
    unittest.main()
