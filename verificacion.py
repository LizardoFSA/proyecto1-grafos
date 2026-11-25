"""
Informe de verificación por consola.

Ejecución:  python verificacion.py   (opcional: python verificacion.py > resultados.txt)

Imprime:
1. La validación del modelo inicial (|V|, |E|, sin lazos/recíprocos/aislados, ≥ 2 caminos).
2. Los resultados de las tres configuraciones (Original, Modificación 1, Modificación 2),
   con las comprobaciones matemáticas, y una tabla comparativa.
3. El caso independiente de 5 vértices con la solución manual esperada contrastada con
   la obtenida por el código.
4. La comparación de estrategias (BFS vs DFS; Edmonds-Karp vs Ford-Fulkerson-DFS vs voraz).
"""

import sys

from laberinto import algoritmos as alg
from laberinto.configuraciones import (red_original, configuraciones_comparadas, caso_verificacion,
                                       contraejemplo_voraz, ENTRADA, SALIDA)

# La consola de Windows puede no usar UTF-8 por defecto (símbolos →, ∅, ≤).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def seccion(titulo):
    """Imprime un encabezado de sección."""
    print("\n" + "=" * 78 + f"\n{titulo}\n" + "=" * 78)


def modelo_inicial():
    """Muestra V, E y la validación de la configuración inicial."""
    g = red_original()
    seccion("1. MODELO MATEMÁTICO DE LA CONFIGURACIÓN INICIAL")
    print(f"V = {{{', '.join(g.vertices)}}}   |V| = {len(g.vertices)}")
    print(f"E = {alg.formato_arcos(list(g.arcos))}   |E| = {len(g.arcos)}")
    print(f"Entrada s = {ENTRADA}, salida t = {SALIDA}\n")
    for texto, ok in alg.validar_modelo_completo(g, ENTRADA, SALIDA):
        print(f"  [{'OK' if ok else 'FALLA'}] {texto}")


def configuraciones():
    """Analiza las tres configuraciones y muestra una tabla comparativa."""
    seccion("2. RESULTADOS DE LAS TRES CONFIGURACIONES (mismos s y t)")
    resumen = []
    for nombre, desc, g in configuraciones_comparadas():
        a = alg.analizar(g, ENTRADA, SALIDA)
        print(f"\n--- {nombre}: {desc}")
        print(alg.informe_texto(g, a))
        m, f = a["minimo"], a["flujo"]
        resumen.append((nombre, "Sí" if m["existe"] else "No",
                        str(m["longitud"]) if m["existe"] else "—",
                        str(f["valor"]), alg.formato_arcos(f["corte"]),
                        "OK" if all(ok for _, ok in a["verificacion"]) else "FALLA"))
    print("\nTabla comparativa")
    encabezado = ("Configuración", "¿Camino?", "d(s,t)", "Máx. caminos", "Corte mínimo", "Verif.")
    anchos = [16, 9, 7, 13, 24, 6]
    print("  ".join(h.ljust(w) for h, w in zip(encabezado, anchos)))
    for fila in resumen:
        print("  ".join(c.ljust(w) for c, w in zip(fila, anchos)))


def caso_manual():
    """Contrasta la resolución manual del caso de 5 vértices con el código."""
    seccion("3. CASO INDEPENDIENTE DE VERIFICACIÓN (5 vértices)")
    g = caso_verificacion()
    print(f"V = {{{', '.join(g.vertices)}}}")
    print(f"E = {alg.formato_arcos(list(g.arcos))}")
    print("""
Resolución manual:
  * Camino mínimo: no existe el arco s→t, así que d(s,t) ≥ 2. Como s→b y b→t existen,
    s → b → t tiene 2 arcos; luego d(s,t) = 2.
  * Familia de caminos sin arcos compartidos: P1 = s → a → c → t, P2 = s → b → t
    (P1 usa {s→a, a→c, c→t}, P2 usa {s→b, b→t}: no comparten arcos).
  * Conjunto de pasillos: C = {s→a, s→b}. Son los únicos arcos que salen de s, así que
    al eliminarlos s no tiene sucesores y t es inalcanzable.
  * |familia| = |C| = 2. Toda familia de caminos arco-disjuntos usa un arco distinto de C
    en cada camino (todo camino s–t cruza C), luego ninguna familia tiene más de 2 caminos;
    y ningún conjunto con menos de 2 arcos separa s de t porque hay 2 caminos disjuntos.
    Por lo tanto la familia es máxima y C es mínimo.
""")
    a = alg.analizar(g, "s", "t")
    print("Resultado del código:")
    print(alg.informe_texto(g, a))
    esperado = {"d": 2, "k": 2, "corte": 2}
    obtenido = {"d": a["minimo"]["longitud"], "k": a["flujo"]["valor"], "corte": len(a["flujo"]["corte"])}
    print(f"\nManual {esperado}  vs  código {obtenido}  ->  "
          f"{'COINCIDEN' if esperado == obtenido else 'NO COINCIDEN'}")


def estrategias():
    """Compara BFS/DFS y las estrategias de caminos disjuntos en la red original y el contraejemplo."""
    seccion("4. COMPARACIÓN DE ESTRATEGIAS")
    for nombre, g in (("Red original", red_original()), ("Contraejemplo voraz", contraejemplo_voraz())):
        bfs = alg.bfs_camino_minimo(g, "s", "t")
        dfs = alg.dfs_camino(g, "s", "t")
        ek = alg.max_caminos_disjuntos(g, "s", "t", "bfs")
        ff = alg.max_caminos_disjuntos(g, "s", "t", "dfs")
        vz = alg.caminos_disjuntos_voraz(g, "s", "t")
        print(f"\n{nombre}:")
        print(f"  BFS : {alg.formato_camino(bfs['camino'])} (longitud {bfs['longitud']})")
        print(f"  DFS : {alg.formato_camino(dfs['camino'])} (longitud {dfs['longitud']})")
        print(f"  Edmonds-Karp      : {ek['valor']} caminos ({len(ek['aumentos'])} aumentos)")
        print(f"  Ford-Fulkerson DFS: {ff['valor']} caminos ({len(ff['aumentos'])} aumentos)")
        print(f"  Voraz             : {vz['valor']} caminos -> "
              + " | ".join(alg.formato_camino(c) for c in vz["caminos"]))


if __name__ == "__main__":
    modelo_inicial()
    configuraciones()
    caso_manual()
    estrategias()
