# Simulador interactivo de laberintos y rutas alternativas

Proyecto 1 – Teoría de Grafos (INFO1158).

La aplicación modela el laberinto como un grafo dirigido y calcula:

- un **camino mínimo** de `s` a `t`, en número de pasillos, con búsqueda en anchura (BFS);
- el **máximo número de caminos dirigidos sin arcos compartidos** y una familia que lo alcanza, con flujo máximo de capacidad unitaria (Edmonds-Karp);
- un **corte mínimo de pasillos**, es decir, un conjunto mínimo de arcos cuya eliminación impide llegar de `s` a `t`;
- la **verificación** de los resultados: los caminos respetan los sentidos de los arcos activos, las rutas no comparten arcos, |familia| = |corte|, G − C no tiene camino de `s` a `t`, y una búsqueda por fuerza bruta confirma que no existe un corte más pequeño.

Todo el código algorítmico es propio. Solo se usan estructuras básicas de Python (`dict`, `list`, `set`, `collections.deque`) y `tkinter` para la interfaz.

## Requisitos

- Python 3.9 o superior (probado con 3.13).
- `tkinter`, que viene incluido con Python en Windows y macOS. En Linux: `sudo apt install python3-tk`.
- No hay dependencias externas, así que no hace falta ejecutar `pip install`.

## Ejecución

```bash
python app.py                              # interfaz gráfica
python verificacion.py                     # informe completo por consola
python verificacion.py > resultados.txt    # guardar el informe
python -m unittest discover -s tests -v    # pruebas automáticas
```

## Uso de la interfaz

| Acción | Cómo |
|---|---|
| Cargar una configuración (Original, Modificación 1 o 2, caso de verificación, contraejemplo) | Lista «Configuración de la red» y botón **Cargar configuración** |
| Cambiar la entrada y la salida | Listas «Entrada s» y «Salida t» y botón **Aplicar**, o clic derecho sobre un vértice |
| Bloquear o restablecer un pasillo | Clic sobre la flecha, doble clic en la lista o botón **Bloquear / Restablecer** |
| Agregar un pasillo | «Desde» y «Hacia», botón **Agregar**. Se rechazan lazos, arcos repetidos y arcos recíprocos |
| Eliminar un pasillo agregado | Seleccionarlo en la lista y pulsar **Eliminar agregado** |
| Elegir qué resultado destacar | Opciones *Todo*, *Camino mínimo*, *Caminos sin arcos compartidos*, *Corte mínimo* |
| Recalcular | Automático al modificar la red, o manual con **Recalcular** si se desactiva la casilla |
| Comparar configuraciones | **Comparar las 3 configuraciones** muestra una tabla que se puede copiar al portapapeles |
| Comparar estrategias | **Comparar estrategias** muestra BFS frente a DFS y Edmonds-Karp frente a Ford-Fulkerson (DFS) y la estrategia voraz |
| Mover vértices | Arrastrar con el mouse |
| Guardar o abrir una red | **Guardar JSON…** y **Abrir JSON…** |
| Validar las condiciones del modelo inicial | Botón **Validar modelo** |

Colores: la franja amarilla o naranja marca el camino mínimo; cada camino sin arcos compartidos (P1, P2, …) tiene su propio color; ✕ en rojo marca los pasillos del corte mínimo; las líneas grises discontinuas con ⛔ son pasillos bloqueados. En el modo *Corte mínimo*, los vértices azules forman el lado S del corte.

## Estructura

```
app.py                       Interfaz gráfica (tkinter)
verificacion.py              Informe por consola: modelo, 3 configuraciones, caso manual, estrategias
laberinto/
  grafo.py                   Clase Grafo: vértices, pasillos activos y bloqueados, restricciones, JSON
  algoritmos.py              BFS, DFS, Edmonds-Karp y Ford-Fulkerson, descomposición en caminos,
                             corte mínimo, estrategia voraz, verificaciones
  configuraciones.py         Red principal, modificaciones, caso de verificación, contraejemplo
tests/test_algoritmos.py     Pruebas: casos fijos y 300 grafos aleatorios contra fuerza bruta
```

## Modelo y configuraciones

**Red principal:** `V = {s, A, B, C, D, E, F, G, H, I, t}` (|V| = 11) y 18 pasillos:
`s→A, s→B, s→C, A→D, A→E, B→E, B→C, C→F, D→E, D→G, E→G, E→H, F→H, F→I, H→G, G→t, H→t, I→t`.

| Configuración | Cambio | d(s,t) | Máx. caminos | Corte mínimo |
|---|---|---|---|---|
| Original | — | 4 | 3 | {s→A, s→B, s→C} |
| Modificación 1 | bloquear s→C y G→t | 4 | 2 | {s→A, s→B} |
| Modificación 2 | bloquear G→t y H→t; agregar D→t | 3 | 2 | {s→A, C→F} |

**Caso de verificación manual:** `V = {s, a, b, c, t}`, `E = {s→a, s→b, a→b, a→c, b→c, b→t, c→t}`, con d(s,t) = 2, 2 caminos y corte {s→a, s→b}.

## Fuentes

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., Stein, C. *Introduction to Algorithms* (3.ª ed.), MIT Press, 2009. Cap. 22 (BFS y DFS) y cap. 26 (flujo máximo).
- Kleinberg, J., Tardos, É. *Algorithm Design*. Pearson, 2006. Cap. 7 (7.6 *Disjoint Paths in Directed and Undirected Graphs*).
- Ford, L. R., Fulkerson, D. R. (1956). Maximal flow through a network. *Canadian Journal of Mathematics*, 8, 399–404.
- Edmonds, J., Karp, R. M. (1972). Theoretical improvements in algorithmic efficiency for network flow problems. *Journal of the ACM*, 19(2), 248–264.
- Menger, K. (1927). Zur allgemeinen Kurventheorie. *Fundamenta Mathematicae*, 10, 96–115.

## Informe técnico

El informe en PDF está en `informe/Informe_Proyecto1_Grafos.pdf`. Para regenerarlo (por ejemplo, después de completar los nombres del grupo y el enlace al repositorio al inicio de `informe/generar_informe.py`):

```bash
pip install reportlab      # solo se necesita para generar el informe
python informe/generar_informe.py
```

Las capturas de la aplicación usadas en el informe están en `informe/img/`.
