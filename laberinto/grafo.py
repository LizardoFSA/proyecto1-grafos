"""
Modelo del laberinto como grafo dirigido G = (V, E).

- Cada vértice de V representa una posición o intersección del centro de almacenamiento.
- Cada arco (u, v) de E representa un pasillo de sentido único que se recorre de u hacia v.
- Un pasillo puede estar *activo* o *bloqueado*. Los algoritmos trabajan solo con los
  arcos activos, es decir, con el grafo G - C donde C es el conjunto de pasillos bloqueados.

Restricciones del modelo (se validan al agregar arcos):
- sin lazos (u, u),
- sin arcos repetidos,
- sin arcos recíprocos (si existe (u, v) no puede existir (v, u)).

Este módulo solo usa estructuras básicas del lenguaje (diccionarios, listas, conjuntos).
"""

import json


class ErrorGrafo(ValueError):
    """Error lanzado cuando una operación violaría las restricciones del modelo."""


class Grafo:
    """
    Grafo dirigido con pasillos activables/bloqueables.

    Atributos:
        vertices (list[str]): vértices en orden de inserción.
        posiciones (dict[str, tuple[float, float]]): coordenadas para dibujar cada vértice.
        arcos (dict[tuple[str, str], dict]): para cada arco (u, v) guarda
            {"activo": bool, "agregado": bool}. "agregado" indica que el pasillo fue
            incorporado por el usuario después de la configuración inicial.
    """

    def __init__(self):
        self.vertices = []
        self.posiciones = {}
        self.arcos = {}

    # ------------------------------------------------------------------ vértices
    def agregar_vertice(self, v, posicion=(0.0, 0.0)):
        """
        Agrega el vértice v al grafo.

        Parámetros:
            v (str): nombre del vértice.
            posicion (tuple): coordenadas (x, y) usadas en la visualización.
        Resultado:
            None. Lanza ErrorGrafo si el vértice ya existe.
        """
        if v in self.posiciones:
            raise ErrorGrafo(f"El vértice '{v}' ya existe.")
        self.vertices.append(v)
        self.posiciones[v] = posicion

    # ------------------------------------------------------------------ arcos
    def motivo_rechazo_arco(self, u, v):
        """
        Indica por qué no se puede agregar el arco (u, v), o None si es válido.

        Parámetros:
            u, v (str): origen y destino del pasillo.
        Resultado:
            str con la explicación del rechazo, o None si el arco es admisible.
        """
        if u not in self.posiciones or v not in self.posiciones:
            return "Ambos extremos deben ser vértices existentes."
        if u == v:
            return f"No se admiten lazos ({u} → {u})."
        if (u, v) in self.arcos:
            return f"El pasillo {u} → {v} ya existe (arco repetido)."
        if (v, u) in self.arcos:
            return f"Ya existe el pasillo {v} → {u}; no se admiten arcos recíprocos."
        return None

    def agregar_arco(self, u, v, agregado=False):
        """
        Agrega el pasillo dirigido u → v (activo).

        Parámetros:
            u, v (str): origen y destino.
            agregado (bool): True si se incorpora como modificación de la red.
        Resultado:
            None. Lanza ErrorGrafo si viola alguna restricción del modelo.
        """
        motivo = self.motivo_rechazo_arco(u, v)
        if motivo:
            raise ErrorGrafo(motivo)
        self.arcos[(u, v)] = {"activo": True, "agregado": agregado}

    def eliminar_arco(self, u, v):
        """Elimina definitivamente el arco (u, v) del grafo."""
        if (u, v) not in self.arcos:
            raise ErrorGrafo(f"No existe el pasillo {u} → {v}.")
        del self.arcos[(u, v)]

    def bloquear(self, u, v):
        """Bloquea el pasillo u → v (deja de considerarse en los algoritmos)."""
        if (u, v) not in self.arcos:
            raise ErrorGrafo(f"No existe el pasillo {u} → {v}.")
        self.arcos[(u, v)]["activo"] = False

    def restablecer(self, u, v):
        """Restablece (reactiva) el pasillo u → v previamente bloqueado."""
        if (u, v) not in self.arcos:
            raise ErrorGrafo(f"No existe el pasillo {u} → {v}.")
        self.arcos[(u, v)]["activo"] = True

    def alternar_bloqueo(self, u, v):
        """Bloquea el pasillo si está activo o lo restablece si está bloqueado. Retorna el nuevo estado."""
        nuevo = not self.arcos[(u, v)]["activo"]
        self.arcos[(u, v)]["activo"] = nuevo
        return nuevo

    def esta_activo(self, u, v):
        """Retorna True si el pasillo u → v existe y está activo."""
        datos = self.arcos.get((u, v))
        return bool(datos and datos["activo"])

    def arcos_activos(self):
        """Retorna la lista de arcos activos (u, v) en orden de inserción."""
        return [a for a, d in self.arcos.items() if d["activo"]]

    def arcos_bloqueados(self):
        """Retorna la lista de arcos bloqueados (u, v)."""
        return [a for a, d in self.arcos.items() if not d["activo"]]

    def lista_adyacencia(self, excluidos=None):
        """
        Construye la lista de adyacencia de los arcos activos.

        Resultado:
            dict[str, list[str]] con los sucesores de cada vértice (orden de inserción,
            lo que hace deterministas los recorridos).
        """
        excluidos = excluidos or set()
        ady = {v: [] for v in self.vertices}
        for (u, v), d in self.arcos.items():
            if d["activo"] and (u, v) not in excluidos:
                ady[u].append(v)
        return ady

    # ------------------------------------------------------------------ utilidades
    def copiar(self):
        """Retorna una copia independiente del grafo."""
        g = Grafo()
        g.vertices = list(self.vertices)
        g.posiciones = dict(self.posiciones)
        g.arcos = {a: dict(d) for a, d in self.arcos.items()}
        return g

    def a_dict(self):
        """Serializa el grafo a un diccionario (para guardar en JSON)."""
        return {
            "vertices": [{"nombre": v, "x": self.posiciones[v][0], "y": self.posiciones[v][1]}
                         for v in self.vertices],
            "arcos": [{"origen": u, "destino": v, "activo": d["activo"], "agregado": d["agregado"]}
                      for (u, v), d in self.arcos.items()],
        }

    @staticmethod
    def desde_dict(datos):
        """Construye un grafo desde el diccionario producido por a_dict(), validando restricciones."""
        g = Grafo()
        for vd in datos["vertices"]:
            g.agregar_vertice(vd["nombre"], (vd["x"], vd["y"]))
        for ad in datos["arcos"]:
            g.agregar_arco(ad["origen"], ad["destino"], ad.get("agregado", False))
            if not ad.get("activo", True):
                g.bloquear(ad["origen"], ad["destino"])
        return g

    def guardar_json(self, ruta, extra=None):
        """Guarda el grafo en un archivo JSON. 'extra' permite añadir datos como s y t."""
        datos = self.a_dict()
        if extra:
            datos.update(extra)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    @staticmethod
    def cargar_json(ruta):
        """Carga un grafo desde JSON. Retorna (grafo, datos_crudos)."""
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        return Grafo.desde_dict(datos), datos


def validar_configuracion_inicial(grafo, s, t, min_v=10, max_v=12, min_e=14, max_e=20):
    """
    Comprueba las condiciones exigidas a la configuración inicial del laberinto.

    Parámetros:
        grafo (Grafo): red a validar (se consideran todos sus arcos).
        s, t (str): entrada y salida.
        min_v, max_v, min_e, max_e (int): cotas para |V| y |E|.
    Resultado:
        list[tuple[str, bool]] con cada condición y si se cumple. La condición de
        "al menos dos caminos sin arcos compartidos" se agrega en algoritmos.py
        (para no crear dependencias circulares) mediante validar_modelo_completo().
    """
    n, m = len(grafo.vertices), len(grafo.arcos)
    grado = {v: 0 for v in grafo.vertices}
    for (u, v) in grafo.arcos:
        grado[u] += 1
        grado[v] += 1
    aislados = [v for v, g in grado.items() if g == 0]
    lazos = [a for a in grafo.arcos if a[0] == a[1]]
    reciprocos = [a for a in grafo.arcos if (a[1], a[0]) in grafo.arcos]
    return [
        (f"{min_v} ≤ |V| ≤ {max_v}  (|V| = {n})", min_v <= n <= max_v),
        (f"{min_e} ≤ |E| ≤ {max_e}  (|E| = {m})", min_e <= m <= max_e),
        (f"s y t pertenecen a V y s ≠ t  (s = {s}, t = {t})",
         s in grafo.posiciones and t in grafo.posiciones and s != t),
        ("Sin lazos", not lazos),
        ("Sin arcos recíprocos", not reciprocos),
        ("Sin vértices aislados" + (f"  (aislados: {aislados})" if aislados else ""), not aislados),
    ]
