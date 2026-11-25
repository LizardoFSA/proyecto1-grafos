"""
Configuraciones del laberinto usadas en el proyecto.

RED PRINCIPAL (configuración inicial)
    V = {s, A, B, C, D, E, F, G, H, I, t}            |V| = 11
    E = {s→A, s→B, s→C, A→D, A→E, B→E, B→C, C→F, D→G, D→E,
         E→G, E→H, F→H, F→I, H→G, G→t, H→t, I→t}     |E| = 18
    Entrada s, salida t.

    Interpretación: s es el acceso de los robots al centro; A, B, C son las tres
    intersecciones de la zona de recepción; D, E, F las del sector de almacenamiento;
    G, H, I las del sector de despacho; t es la salida. Cada arco es un pasillo de un
    solo sentido.

MODIFICACIÓN 1 (bloqueos)
    Se bloquean los pasillos s→C y G→t.

MODIFICACIÓN 2 (bloqueos + nuevo pasillo)
    Se bloquean G→t y H→t, y se agrega el pasillo D→t.

Las tres configuraciones mantienen s y t como entrada y salida.

CASO DE VERIFICACIÓN MANUAL (5 vértices)
    V = {s, a, b, c, t}
    E = {s→a, s→b, a→b, a→c, b→c, b→t, c→t}
"""

from .grafo import Grafo

# Coordenadas pensadas para un lienzo de ~880 x 560 píxeles.
POSICIONES_PRINCIPAL = {
    "s": (70, 280),
    "A": (230, 110), "B": (230, 280), "C": (230, 450),
    "D": (420, 70), "E": (420, 250), "F": (420, 450),
    "G": (620, 130), "H": (620, 320), "I": (620, 470),
    "t": (800, 290),
}

ARCOS_PRINCIPAL = [
    ("s", "A"), ("s", "B"), ("s", "C"),
    ("A", "D"), ("A", "E"), ("B", "E"), ("B", "C"), ("C", "F"),
    ("D", "E"), ("D", "G"), ("E", "G"), ("E", "H"), ("F", "H"), ("F", "I"),
    ("H", "G"), ("G", "t"), ("H", "t"), ("I", "t"),
]

ENTRADA, SALIDA = "s", "t"

# Cada modificación se describe como operaciones sobre la red original.
MODIFICACIONES = {
    "Modificación 1": {
        "descripcion": "Bloqueo de los pasillos s→C y G→t.",
        "bloquear": [("s", "C"), ("G", "t")],
        "agregar": [],
    },
    "Modificación 2": {
        "descripcion": "Bloqueo de G→t y H→t; se agrega el pasillo D→t.",
        "bloquear": [("G", "t"), ("H", "t")],
        "agregar": [("D", "t")],
    },
}

POSICIONES_VERIFICACION = {
    "s": (120, 280), "a": (380, 120), "b": (380, 440), "c": (640, 280), "t": (820, 440),
}
ARCOS_VERIFICACION = [
    ("s", "a"), ("s", "b"), ("a", "b"), ("a", "c"), ("b", "c"), ("b", "t"), ("c", "t"),
]


# Contraejemplo para la comparación de estrategias de caminos disjuntos:
# la estrategia voraz (tomar el camino más corto y borrar sus arcos) obtiene 1 camino,
# mientras que el flujo máximo obtiene 2: s→a→d→e→t y s→c→f→b→t.
POSICIONES_CONTRAEJEMPLO = {
    "s": (80, 280), "a": (280, 150), "c": (280, 420), "d": (460, 70), "e": (640, 70),
    "f": (460, 420), "b": (560, 280), "t": (800, 280),
}
ARCOS_CONTRAEJEMPLO = [
    ("s", "a"), ("a", "b"), ("b", "t"), ("a", "d"), ("d", "e"), ("e", "t"),
    ("s", "c"), ("c", "f"), ("f", "b"),
]


def construir(posiciones, arcos):
    """
    Crea un grafo a partir de un diccionario de posiciones y una lista de arcos.

    Parámetros:
        posiciones (dict[str, tuple]): vértice -> (x, y).
        arcos (list[tuple[str, str]]): pasillos dirigidos.
    Resultado:
        Grafo.
    """
    g = Grafo()
    for v, p in posiciones.items():
        g.agregar_vertice(v, p)
    for u, v in arcos:
        g.agregar_arco(u, v)
    return g


def red_original():
    """Retorna la configuración inicial del laberinto."""
    return construir(POSICIONES_PRINCIPAL, ARCOS_PRINCIPAL)


def aplicar_modificacion(grafo, mod):
    """
    Aplica una modificación (bloqueos y nuevos pasillos) sobre una copia del grafo.

    Parámetros:
        grafo (Grafo): red base.
        mod (dict): {"bloquear": [...], "agregar": [...]}.
    Resultado:
        Grafo modificado (el original no cambia).
    """
    g = grafo.copiar()
    for u, v in mod.get("agregar", []):
        g.agregar_arco(u, v, agregado=True)
    for u, v in mod.get("bloquear", []):
        g.bloquear(u, v)
    return g


def caso_verificacion():
    """Retorna el caso independiente de 5 vértices para la verificación manual."""
    return construir(POSICIONES_VERIFICACION, ARCOS_VERIFICACION)


def configuraciones_comparadas():
    """
    Retorna la lista [(nombre, descripción, grafo)] de las tres configuraciones a comparar,
    todas con la misma entrada s y salida t.
    """
    base = red_original()
    lista = [("Original", "Red inicial sin modificaciones.", base)]
    for nombre, mod in MODIFICACIONES.items():
        lista.append((nombre, mod["descripcion"], aplicar_modificacion(base, mod)))
    return lista


def catalogo():
    """
    Configuraciones disponibles en la interfaz.

    Resultado:
        dict nombre -> (grafo, s, t).
    """
    cat = {nombre: (g, ENTRADA, SALIDA) for nombre, _, g in configuraciones_comparadas()}
    cat["Caso de verificación (5 vértices)"] = (caso_verificacion(), "s", "t")
    cat["Contraejemplo estrategia voraz"] = (contraejemplo_voraz(), "s", "t")
    return cat


def contraejemplo_voraz():
    """Retorna el grafo donde la estrategia voraz de caminos disjuntos no es óptima."""
    return construir(POSICIONES_CONTRAEJEMPLO, ARCOS_CONTRAEJEMPLO)
