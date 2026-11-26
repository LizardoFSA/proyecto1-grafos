"""
Algoritmos implementados con código propio (sin bibliotecas de grafos):

1. Camino mínimo en número de arcos:
   - bfs_camino_minimo  -> Búsqueda en anchura (BFS). ESTRATEGIA SELECCIONADA.
     Explora por niveles, por lo que el primer momento en que alcanza t lo hace
     con la menor cantidad de arcos posible: d_G(s, t). Complejidad O(|V| + |E|).
   - dfs_camino         -> Búsqueda en profundidad (DFS). Se incluye solo para la
     comparación: encuentra *un* camino si existe, pero no garantiza que sea mínimo.

2. Máximo número de caminos dirigidos s–t sin arcos compartidos:
   Se modela como flujo máximo con capacidad 1 en cada arco activo. Por el teorema de
   Menger (versión arcos) / teorema de flujo máximo–corte mínimo, el valor del flujo
   máximo entero coincide con el número máximo de caminos arco-disjuntos y con la
   cardinalidad mínima de un conjunto de arcos que separa s de t.
   - max_caminos_disjuntos(..., estrategia="bfs") -> Edmonds-Karp (caminos de aumento
     más cortos con BFS). ESTRATEGIA SELECCIONADA. O(|V|·|E|²) en general y
     O(|E|·(|V|+|E|)) con capacidades unitarias, pues el flujo ≤ grado de salida de s.
   - max_caminos_disjuntos(..., estrategia="dfs") -> Ford-Fulkerson con DFS, para comparar.
   - caminos_disjuntos_voraz -> estrategia ingenua (buscar un camino BFS y borrar sus
     arcos, repetir). Se incluye para mostrar que NO siempre es óptima.

3. Corte mínimo: tras el flujo máximo, el conjunto S de vértices alcanzables desde s en
   la red residual define el corte (S, V \\ S); los arcos activos que salen de S hacia
   V \\ S forman un conjunto mínimo de pasillos cuya eliminación impide llegar a t.

Fuentes:
- Cormen, Leiserson, Rivest, Stein. Introduction to Algorithms, 3.ª/4.ª ed., cap. 22 (BFS/DFS)
  y cap. 26 (Flujo máximo, Ford-Fulkerson, Edmonds-Karp, teorema max-flow min-cut).
- Edmonds, J.; Karp, R. M. (1972). "Theoretical improvements in algorithmic efficiency for
  network flow problems". Journal of the ACM 19(2): 248–264.
- Ford, L. R.; Fulkerson, D. R. (1956). "Maximal flow through a network".
  Canadian Journal of Mathematics 8: 399–404.
- Menger, K. (1927). "Zur allgemeinen Kurventheorie". Fundamenta Mathematicae 10: 96–115.
- Kleinberg, Tardos. Algorithm Design, cap. 7 (7.6 Disjoint Paths in Directed Graphs).
"""

from collections import deque
from itertools import combinations


# =====================================================================================
# 1. CAMINO MÍNIMO
# =====================================================================================
def reconstruir_camino(padre, s, t):
    """
    Reconstruye el camino s → ... → t siguiendo el diccionario de predecesores.

    Parámetros:
        padre (dict[str, str|None]): predecesor de cada vértice descubierto.
        s, t (str): extremos.
    Resultado:
        list[str] con los vértices del camino, o [] si t no fue alcanzado.
    """
    if t not in padre:
        return []
    camino = []
    actual = t
    while actual is not None:
        camino.append(actual)
        actual = padre[actual]
    camino.reverse()
    return camino if camino and camino[0] == s else []


def bfs_camino_minimo(grafo, s, t, excluidos=None):
    """
    Búsqueda en anchura desde s para obtener un camino con el menor número de arcos.

    Parámetros:
        grafo (Grafo): red con pasillos activos/bloqueados (solo se usan los activos).
        s, t (str): entrada y salida.
        excluidos (set[tuple] | None): arcos adicionales a ignorar (para evaluar G - C).
    Resultado:
        dict con:
          "existe"    (bool)        : True si hay camino dirigido de s a t.
          "longitud"  (int | None)  : d_G(s, t); None si no existe camino (no se asigna número).
          "camino"    (list[str])   : un camino mínimo (vacío si no existe).
          "distancias"(dict)        : distancia (en arcos) desde s a cada vértice alcanzado.
          "orden"     (list[str])   : orden en que BFS descubrió los vértices.
    """
    ady = grafo.lista_adyacencia(excluidos)
    distancia = {s: 0}
    padre = {s: None}
    orden = [s]
    cola = deque([s])
    while cola:
        u = cola.popleft()
        if u == t:
            break  # el primer descubrimiento de t ya fija d(s,t); no hace falta seguir
        for v in ady[u]:
            if v not in distancia:
                distancia[v] = distancia[u] + 1
                padre[v] = u
                orden.append(v)
                cola.append(v)
    camino = reconstruir_camino(padre, s, t)
    existe = bool(camino)
    return {
        "existe": existe,
        "longitud": len(camino) - 1 if existe else None,
        "camino": camino,
        "distancias": distancia,
        "orden": orden,
    }


def dfs_camino(grafo, s, t, excluidos=None):
    """
    Búsqueda en profundidad (iterativa) desde s hasta t. Solo para comparación con BFS.

    Parámetros: iguales a bfs_camino_minimo.
    Resultado:
        dict con "existe", "longitud" (longitud del camino hallado, NO necesariamente mínima)
        y "camino".
    """
    ady = grafo.lista_adyacencia(excluidos)
    padre = {s: None}
    visitados = set()
    pila = [s]
    while pila:
        u = pila.pop()
        if u in visitados:
            continue
        visitados.add(u)
        if u == t:
            break
        # se apilan en orden inverso para explorar primero el primer sucesor
        for v in reversed(ady[u]):
            if v not in visitados:
                padre[v] = u  # el último en apilar v es quien lo explora en profundidad
                pila.append(v)
    camino = reconstruir_camino(padre, s, t)
    return {"existe": bool(camino), "longitud": len(camino) - 1 if camino else None,
            "camino": camino}


def existe_camino(grafo, s, t, excluidos=None):
    """Retorna True si hay camino dirigido de s a t usando arcos activos no excluidos."""
    return bfs_camino_minimo(grafo, s, t, excluidos)["existe"]


# =====================================================================================
# 2. MÁXIMO NÚMERO DE CAMINOS SIN ARCOS COMPARTIDOS (FLUJO MÁXIMO UNITARIO)
# =====================================================================================
def _construir_red_residual(grafo):
    """
    Crea la red residual inicial con capacidad 1 por arco activo.

    Resultado:
        (capacidad, vecinos, originales)
        capacidad (dict[(u,v)] -> int): capacidad residual de cada arco (incluye arcos inversos con 0).
        vecinos   (dict[u] -> list[v]): vecinos en la red residual (directos e inversos).
        originales(list[(u,v)])        : arcos activos del grafo.
    """
    capacidad = {}
    vecinos = {v: [] for v in grafo.vertices}
    originales = grafo.arcos_activos()
    for (u, v) in originales:
        capacidad[(u, v)] = capacidad.get((u, v), 0) + 1
        capacidad.setdefault((v, u), 0)
        if v not in vecinos[u]:
            vecinos[u].append(v)
        if u not in vecinos[v]:
            vecinos[v].append(u)
    return capacidad, vecinos, originales


def _buscar_camino_aumento(capacidad, vecinos, s, t, estrategia):
    """
    Busca un camino de aumento en la red residual.

    Parámetros:
        estrategia (str): "bfs" (Edmonds-Karp) o "dfs" (Ford-Fulkerson con DFS).
    Resultado:
        list[str] con el camino de aumento, o [] si no existe (el flujo ya es máximo).
    """
    padre = {s: None}
    frontera = deque([s])
    while frontera:
        u = frontera.popleft() if estrategia == "bfs" else frontera.pop()
        if u == t:
            break
        for v in vecinos[u]:
            if v not in padre and capacidad[(u, v)] > 0:
                padre[v] = u
                if v == t and estrategia == "bfs":
                    return reconstruir_camino(padre, s, t)
                frontera.append(v)
    return reconstruir_camino(padre, s, t)


def _descomponer_flujo(flujo_arcos, s, t, valor):
    """
    Descompone un flujo entero unitario en 'valor' caminos s–t arco-disjuntos.

    Parámetros:
        flujo_arcos (list[(u,v)]): arcos originales con flujo 1.
        s, t (str): extremos.
        valor (int): valor del flujo.
    Resultado:
        list[list[str]] con los caminos. Si al recorrer se forma un ciclo (posible en un
        flujo), el ciclo se descarta, de modo que cada camino no repite vértices.
    Al usar cada arco con flujo a lo sumo una vez, los caminos no comparten arcos.
    """
    salientes = {}
    for (u, v) in flujo_arcos:
        salientes.setdefault(u, []).append(v)
    caminos = []
    for _ in range(valor):
        camino = [s]
        posicion = {s: 0}
        actual = s
        while actual != t:
            siguiente = salientes[actual].pop(0)  # existe por conservación del flujo
            if siguiente in posicion:
                # se cerró un ciclo: se elimina del camino (sus arcos quedan consumidos)
                corte = posicion[siguiente]
                for x in camino[corte + 1:]:
                    del posicion[x]
                camino = camino[:corte + 1]
            else:
                posicion[siguiente] = len(camino)
                camino.append(siguiente)
            actual = siguiente
        caminos.append(camino)
    return caminos


def max_caminos_disjuntos(grafo, s, t, estrategia="bfs"):
    """
    Calcula el máximo número de caminos dirigidos de s a t que no comparten arcos,
    una familia que lo alcanza y un corte mínimo de pasillos.

    Parámetros:
        grafo (Grafo): red (solo arcos activos).
        s, t (str): entrada y salida distintas.
        estrategia (str): "bfs" = Edmonds-Karp (seleccionada); "dfs" = Ford-Fulkerson con DFS.
    Resultado:
        dict con:
          "valor"      (int)              : máximo número de caminos arco-disjuntos (= flujo máximo).
          "caminos"    (list[list[str]])  : familia máxima de caminos sin arcos compartidos.
          "corte"      (list[(u,v)])      : conjunto mínimo de pasillos que separa s de t.
          "lado_s"     (set[str])         : vértices alcanzables desde s en la red residual final.
          "aumentos"   (list[list[str]])  : caminos de aumento usados en cada iteración.
        Si no existe camino: valor 0, caminos [] y corte [] (el conjunto vacío ya separa s de t).
    """
    if s == t:
        raise ValueError("La entrada y la salida deben ser distintas.")
    capacidad, vecinos, originales = _construir_red_residual(grafo)
    aumentos = []
    while True:
        camino = _buscar_camino_aumento(capacidad, vecinos, s, t, estrategia)
        if not camino:
            break
        # capacidad unitaria: el cuello de botella de cualquier camino de aumento es 1
        for u, v in zip(camino, camino[1:]):
            capacidad[(u, v)] -= 1
            capacidad[(v, u)] += 1
        aumentos.append(camino)
    valor = len(aumentos)

    # Arcos originales que transportan flujo: su capacidad residual bajó de 1 a 0.
    flujo_arcos = [(u, v) for (u, v) in originales if capacidad[(u, v)] == 0]
    caminos = _descomponer_flujo(flujo_arcos, s, t, valor)

    # Corte mínimo: S = alcanzables desde s en la red residual final.
    lado_s = {s}
    cola = deque([s])
    while cola:
        u = cola.popleft()
        for v in vecinos[u]:
            if v not in lado_s and capacidad[(u, v)] > 0:
                lado_s.add(v)
                cola.append(v)
    corte = [(u, v) for (u, v) in originales if u in lado_s and v not in lado_s]

    return {"valor": valor, "caminos": caminos, "corte": corte,
            "lado_s": lado_s, "aumentos": aumentos}


def caminos_disjuntos_voraz(grafo, s, t):
    """
    Estrategia ingenua de comparación: repetir {buscar camino mínimo con BFS; eliminar sus
    arcos} hasta que no haya camino. Es correcta como cota inferior pero NO garantiza el
    máximo, porque no puede "deshacer" decisiones (la red residual de Ford-Fulkerson sí).

    Resultado:
        dict con "valor" y "caminos".
    """
    usados = set()
    caminos = []
    while True:
        r = bfs_camino_minimo(grafo, s, t, excluidos=usados)
        if not r["existe"]:
            break
        caminos.append(r["camino"])
        usados.update(zip(r["camino"], r["camino"][1:]))
    return {"valor": len(caminos), "caminos": caminos}


# =====================================================================================
# 3. ANÁLISIS COMPLETO Y VERIFICACIÓN
# =====================================================================================
def analizar(grafo, s, t):
    """
    Ejecuta todos los cálculos solicitados para la configuración actual.

    Parámetros:
        grafo (Grafo), s, t (str).
    Resultado:
        dict con "s", "t", "minimo" (resultado BFS), "flujo" (resultado Edmonds-Karp)
        y "verificacion" (lista de comprobaciones (descripción, bool)).
    """
    minimo = bfs_camino_minimo(grafo, s, t)
    flujo = max_caminos_disjuntos(grafo, s, t, "bfs")
    verificacion = verificar(grafo, s, t, minimo, flujo)
    return {"s": s, "t": t, "minimo": minimo, "flujo": flujo, "verificacion": verificacion}


def es_camino_valido(grafo, camino, s, t):
    """
    Comprueba que 'camino' sea un camino dirigido de s a t que respeta los sentidos de los
    arcos activos y no repite vértices.
    """
    if not camino or camino[0] != s or camino[-1] != t:
        return False
    if len(set(camino)) != len(camino):
        return False
    return all(grafo.esta_activo(u, v) for u, v in zip(camino, camino[1:]))


def corte_minimo_fuerza_bruta(grafo, s, t, cota):
    """
    Verificación independiente: busca por enumeración el menor k ≤ cota tal que existe un
    conjunto de k arcos activos cuya eliminación separa s de t.

    Parámetros:
        cota (int): tamaño máximo a explorar (normalmente el valor del flujo).
    Resultado:
        (k, conjunto) con el menor tamaño hallado, o (None, None) si ninguno ≤ cota separa.
    Útil para grafos pequeños (|E| ≤ ~25 y cota ≤ 4).
    """
    activos = grafo.arcos_activos()
    for k in range(0, cota + 1):
        for C in combinations(activos, k):
            if not existe_camino(grafo, s, t, excluidos=set(C)):
                return k, list(C)
    return None, None


def verificar(grafo, s, t, minimo, flujo, fuerza_bruta=True):
    """
    Comprobaciones matemáticas sobre los resultados obtenidos.

    Parámetros:
        grafo (Grafo), s, t (str), minimo (resultado BFS), flujo (resultado de flujo).
        fuerza_bruta (bool): si True y el grafo es pequeño, confirma la minimalidad del corte
            enumerando todos los conjuntos de tamaño menor.
    Resultado:
        list[tuple[str, bool]].
    """
    checks = []
    caminos, corte, k = flujo["caminos"], flujo["corte"], flujo["valor"]

    if minimo["existe"]:
        checks.append(("El camino mínimo respeta los sentidos de los arcos activos",
                       es_camino_valido(grafo, minimo["camino"], s, t)))
        # Ningún camino puede ser más corto que d(s,t): comprobado por distancias BFS
        # (cada vértice del camino está a la distancia que indica su posición).
        d = minimo["distancias"]
        checks.append(("Cada vértice del camino mínimo está a la distancia BFS de su posición",
                       all(d.get(v) == i for i, v in enumerate(minimo["camino"]))))
    else:
        checks.append(("No existe camino: no se asigna longitud numérica",
                       minimo["longitud"] is None))

    checks.append((f"Los {k} caminos declarados respetan los sentidos de los arcos activos",
                   all(es_camino_valido(grafo, c, s, t) for c in caminos)))
    arcos_usados = [a for c in caminos for a in zip(c, c[1:])]
    checks.append(("Los caminos declarados independientes no comparten arcos",
                   len(arcos_usados) == len(set(arcos_usados))))
    checks.append((f"|familia de caminos| = |corte mínimo|  ({len(caminos)} = {len(corte)})",
                   len(caminos) == len(corte) == k))
    checks.append(("Eliminar el corte impide llegar de s a t (no hay camino en G − C)",
                   not existe_camino(grafo, s, t, excluidos=set(corte))))
    checks.append(("Todos los arcos del corte están activos",
                   all(grafo.esta_activo(u, v) for u, v in corte)))
    if not minimo["existe"]:
        checks.append(("Sin camino: 0 caminos disponibles y el conjunto vacío ya separa s de t",
                       k == 0 and corte == []))
    if fuerza_bruta and len(grafo.arcos_activos()) <= 25 and k <= 4:
        kb, _ = corte_minimo_fuerza_bruta(grafo, s, t, k)
        checks.append((f"Fuerza bruta: ningún conjunto con menos de {k} arcos separa s de t",
                       kb == k))
    return checks


def validar_modelo_completo(grafo, s, t):
    """
    Condiciones de la configuración inicial (grafo.validar_configuracion_inicial) más la
    exigencia de admitir al menos dos caminos s–t sin arcos compartidos.
    """
    from .grafo import validar_configuracion_inicial
    checks = validar_configuracion_inicial(grafo, s, t)
    k = max_caminos_disjuntos(grafo, s, t)["valor"]
    checks.append((f"Al menos dos caminos s–t sin arcos compartidos  (máximo = {k})", k >= 2))
    return checks


# =====================================================================================
# Formato de salida
# =====================================================================================
def formato_camino(camino):
    """Convierte ['s','A','t'] en 's → A → t'."""
    return " → ".join(camino)


def formato_arcos(arcos):
    """Convierte [('s','A'), ...] en '{s→A, ...}' ('∅' si está vacío)."""
    if not arcos:
        return "∅"
    return "{" + ", ".join(f"{u}→{v}" for u, v in arcos) + "}"


def informe_texto(grafo, analisis):
    """
    Genera el informe en texto de un análisis (se muestra en el panel de resultados de la interfaz).

    Parámetros:
        grafo (Grafo), analisis (dict producido por analizar()).
    Resultado:
        str multilínea.
    """
    s, t = analisis["s"], analisis["t"]
    m, f = analisis["minimo"], analisis["flujo"]
    bloq = grafo.arcos_bloqueados()
    lineas = [
        f"Entrada s = {s}    Salida t = {t}",
        f"|V| = {len(grafo.vertices)}   Pasillos activos: {len(grafo.arcos_activos())}"
        f" de {len(grafo.arcos)}   Bloqueados: {formato_arcos(bloq)}",
        "",
        "1) CAMINO MÍNIMO (BFS)",
    ]
    if m["existe"]:
        lineas += [f"   Existe camino: Sí",
                   f"   d(s,t) = {m['longitud']}",
                   f"   Camino: {formato_camino(m['camino'])}"]
    else:
        lineas += ["   Existe camino: NO. No hay camino dirigido de s a t;",
                   "   d(s,t) no está definida (no se asigna longitud)."]
    lineas += ["", "2) CAMINOS SIN ARCOS COMPARTIDOS (Edmonds-Karp, capacidad 1)",
               f"   Máximo número: {f['valor']}"]
    for i, c in enumerate(f["caminos"], 1):
        lineas.append(f"   P{i} ({len(c) - 1} arcos): {formato_camino(c)}")
    if f["valor"] == 0:
        lineas.append("   Cero caminos disponibles.")
    lineas += ["", "3) CORTE MÍNIMO DE PASILLOS",
               f"   |C| = {len(f['corte'])}   C = {formato_arcos(f['corte'])}"]
    if f["valor"] == 0:
        lineas.append("   El conjunto vacío ya impide el desplazamiento de s a t.")
    lado = [s] + sorted(v for v in f["lado_s"] if v != s)
    lineas.append(f"   Lado S del corte (alcanzable desde s en la red residual): {{{', '.join(lado)}}}")
    lineas += ["", "4) VERIFICACIÓN"]
    for texto, ok in analisis["verificacion"]:
        lineas.append(f"   [{'OK' if ok else 'FALLA'}] {texto}")
    return "\n".join(lineas)
