# Guion del video – Proyecto 1: Simulador de laberintos y rutas alternativas

**Duración objetivo:** unos 14 minutos. El profesor pide entre 10 y 20; quedan 6 minutos de margen bajo el máximo y 4 sobre el mínimo.

**Reparto:** tres partes de unos 4 min 40 s cada una.

| Parte | Tiempo | Integrante | Tema | Criterios de la rúbrica |
|---|---|---|---|---|
| 1 | 0:00 – 4:40 | Integrante 1 | Problema, modelo matemático y camino mínimo (BFS frente a DFS) | 1 y 2 |
| 2 | 4:40 – 9:20 | Integrante 2 | Caminos sin arcos compartidos, flujo máximo, corte mínimo y verificación | 2 y 3 |
| 3 | 9:20 – 14:00 | Integrante 3 | Simulación interactiva en vivo, comparación y cierre | 3 y 4 |

**Operador de la app:** una sola persona maneja el computador durante todo el video. Lo más cómodo es que sea quien hable en la parte 3, porque es la parte con más acciones en vivo. En las partes 1 y 2 el operador sigue las indicaciones **[Pantalla]** mientras habla el compañero.

**Cómo leer el guion**

- **[Pantalla]**: lo que hace el operador en la aplicación.
- Los párrafos con sangría son lo que se dice. No hace falta leerlos al pie de la letra; sirven de base.
- Ritmo calculado: unas 140 palabras por minuto, que es un ritmo tranquilo.

---

## Antes de grabar

**Aplicación**

- [ ] Abrir con `python app.py` y maximizar la ventana.
- [ ] Cargar la configuración **Original**, en el modo **Todo**.
- [ ] Dejar marcada la casilla **«Recalcular automáticamente al modificar»**.
- [ ] Cerrar otras ventanas y silenciar notificaciones (Windows, WhatsApp, Discord).
- [ ] Hacer un ensayo completo con cronómetro: las acciones en pantalla toman más tiempo del que parece.

**Grabación**

- [ ] Grabar la pantalla con voz, por ejemplo con OBS, una reunión de Zoom/Teams/Meet o la grabadora de pantalla de Windows (Win + Alt + R).
- [ ] Que cada integrante diga su nombre al empezar su parte. La rúbrica evalúa la participación de todos, criterio 5.
- [ ] Opcional: mostrar la cámara de quien habla en una esquina.

**Publicación**

- [ ] Subir el video a YouTube como **Público**, o como **No listado**, que cualquiera con el enlace puede ver. El profesor pide que esté «disponible públicamente».
- [ ] Abrir el enlace en una ventana de incógnito para confirmar que se ve sin iniciar sesión.
- [ ] **Un solo integrante** sube el enlace a EDUCA, a más tardar el **lunes 30 de noviembre a las 17:00**.

---

## Parte 1 – Integrante 1 (0:00 – 4:40)

### 1.1 Apertura (0:00 – 0:40)

**[Pantalla]** La aplicación abierta con la red Original en modo Todo.

> Hola, somos el grupo formado por [nombre integrante 1], [nombre integrante 2] y [nombre integrante 3], y este es nuestro proyecto de Teoría de Grafos: un simulador interactivo de laberintos y rutas alternativas. Yo soy [nombre] y voy a presentar el problema, cómo lo modelamos como grafo y cómo encontramos el camino más corto. Luego [nombre] explicará los caminos que no comparten pasillos y el corte mínimo, y finalmente [nombre] hará la simulación en vivo, modificando la red.

### 1.2 El problema (0:40 – 1:40)

> El contexto es un centro de almacenamiento donde unos robots de inspección se mueven por pasillos de un solo sentido. Cada inspección parte en una entrada y debe llegar a una salida, respetando la dirección de los pasillos.
>
> El centro necesita responder tres preguntas. Primero: ¿cuál es el trayecto con menos pasillos? Segundo: ¿cuántas rutas puede tener el robot que no dependan de los mismos pasillos? Esto importa porque si un pasillo se bloquea, todas las rutas que lo usan caen al mismo tiempo. Y tercero: ¿cuál es la menor cantidad de pasillos que, al bloquearse, dejaría la salida incomunicada?
>
> Además, la aplicación tiene que mostrar cómo cambian estas respuestas cuando la red se modifica.

### 1.3 Modelo matemático (1:40 – 3:20)

**[Pantalla]** Mostrar la red. Señalar con el mouse s, t y algunas flechas mientras se nombran.

> Modelamos el laberinto como un grafo dirigido G igual a (V, E). Cada vértice es una posición o intersección del centro y cada arco es un pasillo de sentido único: el arco de u a v solo se puede recorrer de u hacia v. El vértice s, en verde, es la entrada y t, en rojo, la salida. La longitud de un camino es su cantidad de arcos.
>
> Nuestra red tiene 11 vértices: s, las letras de la A a la I, y t. Los organizamos en sectores que el robot cruza de izquierda a derecha: A, B y C son la recepción; D, E y F, el almacenamiento; y G, H e I, el despacho. Tiene 18 pasillos. Algunos son internos, como B hacia C, D hacia E y H hacia G, y crean rutas alternativas que comparten parte del trayecto.
>
> Un pasillo bloqueado lo modelamos quitando su arco: si B es el conjunto de pasillos bloqueados, los algoritmos trabajan sobre G menos B.

**[Pantalla]** Clic en **«Validar modelo»** y dejar visible la ventana con las comprobaciones.

> La configuración inicial cumple todas las condiciones del enunciado: tiene entre 10 y 12 vértices, entre 14 y 20 arcos, no tiene lazos, arcos repetidos ni arcos recíprocos, no tiene vértices aislados y admite al menos dos caminos de s a t sin arcos compartidos; de hecho, admite tres.

**[Pantalla]** Cerrar la ventana.

### 1.4 Camino mínimo: BFS frente a DFS (3:20 – 4:40)

**[Pantalla]** Seleccionar el modo **«Camino mínimo»**.

> Para el camino mínimo comparamos dos búsquedas. La búsqueda en profundidad, DFS, avanza todo lo posible por una rama antes de retroceder: encuentra un camino si existe, pero no garantiza que sea el más corto. La búsqueda en anchura, BFS, recorre el grafo por niveles con una cola: primero los vértices a un arco de s, luego los que están a dos, y así sucesivamente. Por eso, la primera vez que llega a t lo hace con la menor cantidad de arcos posible. Ambas tardan un tiempo proporcional a vértices más arcos.

**[Pantalla]** Clic en **«Comparar estrategias (BFS/DFS, flujo)»** y señalar las dos primeras líneas.

> Aquí se ve la diferencia en nuestra propia red: DFS encuentra s, A, D, E, G, t, con 5 pasillos, mientras que BFS encuentra s, A, D, G, t, con solo 4. Por eso elegimos BFS. Cada vértice guarda desde dónde fue descubierto, y así reconstruimos el camino retrocediendo desde t. Si t nunca se alcanza, la aplicación dice que no existe camino y no le asigna ninguna longitud.

**[Pantalla]** Cerrar la ventana.

> Ahora [nombre integrante 2] va a explicar cómo contamos las rutas independientes.

---

## Parte 2 – Integrante 2 (4:40 – 9:20)

### 2.1 Caminos sin arcos compartidos (4:40 – 6:00)

**[Pantalla]** Seleccionar el modo **«Caminos sin arcos compartidos»**.

> Soy [nombre]. La segunda pregunta es cuántas rutas de s a t podemos tener sin que dos de ellas usen el mismo pasillo. Pueden pasar por el mismo vértice, pero no por el mismo arco.
>
> Investigamos dos estrategias. La primera es voraz: buscar el camino más corto, borrar sus pasillos y repetir hasta que no queden caminos. Es simple, pero no siempre da el máximo, como vamos a ver en un momento.
>
> La segunda es plantearlo como un problema de flujo máximo: cada pasillo tiene capacidad 1 y se manda la mayor cantidad de flujo posible desde s hasta t. Un flujo de valor k se puede separar en k caminos que no comparten arcos, y al revés, k caminos así forman un flujo de valor k. Por eso el flujo máximo es exactamente el número que buscamos.
>
> Para calcularlo usamos Edmonds-Karp, que es el método de Ford-Fulkerson buscando cada camino de aumento con BFS. Garantiza el óptimo y tiene un tiempo acotado sin importar el orden en que se exploren los vértices.

> En la red original obtenemos 3 caminos, cada uno con un color: s, A, D, G, t en azul; s, B, E, H, t en verde; y s, C, F, I, t en morado. Ninguno comparte pasillos.

### 2.2 Por qué no basta la estrategia voraz (6:00 – 7:00)

**[Pantalla]** En la lista de configuraciones, elegir **«Contraejemplo estrategia voraz»** y pulsar **«Cargar configuración»**. Luego, clic en **«Comparar estrategias»**.

> Este grafo pequeño muestra el problema de la estrategia voraz. El camino más corto es s, a, b, t. Si lo tomamos y borramos sus pasillos, ya no queda ninguna ruta: la estrategia voraz obtiene solo 1. Pero se pueden tener 2: s, a, d, e, t y s, c, f, b, t.
>
> Edmonds-Karp sí llega a 2, gracias a la red residual. Su segundo camino de aumento pasa por el arco de b hacia a, que es el inverso de a hacia b. Eso equivale a «deshacer» el uso de ese pasillo y redistribuir las rutas. Esa capacidad de corregir es lo que le falta a la estrategia voraz.

**[Pantalla]** Cerrar la ventana. Cargar de nuevo la configuración **«Original»**.

### 2.3 Corte mínimo y teorema de Menger (7:00 – 8:10)

**[Pantalla]** Seleccionar el modo **«Corte mínimo»**.

> La tercera pregunta es el menor número de pasillos que hay que bloquear para que el robot no pueda llegar de s a t.
>
> Si tenemos k rutas sin pasillos compartidos, para aislar la salida hay que cortar al menos un pasillo de cada ruta, y como no comparten pasillos, son k pasillos distintos. Por lo tanto, el corte nunca es menor que el número de rutas. El teorema de Menger, y en general el teorema de flujo máximo y corte mínimo, dice que además son iguales.
>
> Lo obtenemos al terminar el algoritmo: tomamos los vértices que todavía se alcanzan desde s en la red residual, que son los marcados en azul, y los pasillos que salen de ese grupo hacia el resto forman el corte. En la red original el corte es s hacia A, s hacia B y s hacia C, marcados con una equis roja: 3 pasillos, igual que las 3 rutas.

### 2.4 Verificación con un caso manual (8:10 – 9:20)

**[Pantalla]** Cargar **«Caso de verificación (5 vértices)»** en modo **Todo**.

> Para verificar el código resolvimos a mano un caso de 5 vértices. No hay pasillo directo de s a t, así que cualquier camino tiene al menos 2 arcos, y s, b, t tiene exactamente 2: la distancia mínima es 2. Encontramos 2 rutas sin pasillos compartidos, s, a, c, t y s, b, t, y un corte de 2 pasillos, s hacia a y s hacia b, que son las únicas salidas de s.
>
> Como hay 2 rutas y un corte de 2 pasillos, ninguna familia de rutas puede ser más grande y ningún corte puede ser más chico: las dos son óptimas. La aplicación obtiene exactamente lo mismo.
>
> Además, cada vez que calcula, la aplicación comprueba en el panel de resultados que los caminos respetan el sentido de los pasillos activos, que no comparten arcos, que el corte tiene el mismo tamaño que la familia de rutas y que, al quitar el corte, t queda inalcanzable. Incluso revisa por fuerza bruta que no exista un corte más pequeño.

> Ahora [nombre integrante 3] va a modificar la red en vivo.

---

## Parte 3 – Integrante 3 (9:20 – 14:00)

### 3.1 Bloqueo de pasillos: Modificación 1 (9:20 – 10:30)

**[Pantalla]** Cargar **«Original»** en modo **Todo**.

> Soy [nombre] y voy a mostrar la simulación. Para comparar, mantenemos s como entrada y t como salida en todas las configuraciones.

**[Pantalla]** Clic sobre la flecha **s → C**, que queda gris y discontinua.

> Bloqueo el pasillo de s a C, haciendo clic sobre la flecha. La aplicación recalcula sola: el camino mínimo sigue midiendo 4, pero ahora solo hay 2 rutas independientes, porque s se quedó con 2 salidas.

**[Pantalla]** Clic sobre la flecha **G → t**.

> Ahora bloqueo también G hacia t. Esta es nuestra Modificación 1. Lo interesante es que la distancia sigue siendo 4, con s, A, E, H, t. Aunque perdimos la ruta superior, existe otra igual de corta. El sector C sigue alcanzable gracias al pasillo interno de B a C, con una ruta de 5 pasillos. Seguimos teniendo 2 rutas y el corte es s hacia A y s hacia B: la red se volvió más frágil, porque basta bloquear 2 pasillos para aislar la salida.

### 3.2 Bloqueos y un pasillo nuevo: Modificación 2 (10:30 – 12:00)

**[Pantalla]** Clic en **«Restablecer todos los pasillos»**. Luego, clic en **G → t** y en **H → t**.

> Restablezco todo y ahora bloqueo los pasillos que llegan a t desde G y desde H. Queda una sola ruta independiente, s, C, F, I, t, de 4 pasillos, y el corte mínimo es un solo pasillo, C hacia F. Si ese pasillo se bloquea, el robot ya no puede salir.

**[Pantalla]** En «Agregar pasillo dirigido», elegir Desde **D** y Hacia **t**, y pulsar **«Agregar»**.

> Para corregirlo agrego un pasillo nuevo de D a t. Esta es nuestra Modificación 2. Con un solo pasillo pasamos de 1 a 2 rutas independientes, y además el camino mínimo baja a 3 pasillos, s, A, D, t: más corto que en la red original.

**[Pantalla]** Seleccionar el modo **«Corte mínimo»**.

> Pero el máximo es 2 y no 3, porque ahora el cuello de botella está en el interior de la red. El corte es s hacia A y C hacia F: los vértices en azul, que son B, C, E, G y H, quedan encerrados, porque G y H perdieron su salida a t.

### 3.3 Restricciones, caso sin camino y cambio de entrada (12:00 – 12:50)

**[Pantalla]** Volver al modo **Todo**. Intentar agregar el pasillo de **C** hacia **B** y mostrar el mensaje de error.

> La aplicación respeta las reglas del modelo: si intento agregar C hacia B, lo rechaza porque ya existe B hacia C y no se admiten arcos recíprocos. Tampoco acepta lazos ni pasillos repetidos.

**[Pantalla]** Cerrar el mensaje. Clic en **I → t** y en **D → t**.

> Si bloqueo también I hacia t y D hacia t, ya no existe ningún camino: la aplicación lo indica, no inventa una longitud, muestra cero rutas disponibles y el corte vacío, porque la salida ya está incomunicada.

**[Pantalla]** Cargar **«Original»**. Clic derecho sobre **B** y elegir **«Usar B como entrada (s)»**.

> También podemos cambiar la entrada o la salida, con clic derecho sobre un vértice o con las listas del panel. Con B como entrada, la distancia a t es 3 y hay 2 rutas independientes, porque B tiene solo 2 salidas.

**[Pantalla]** Clic derecho sobre **s** y elegir **«Usar s como entrada (s)»**.

### 3.4 Comparación y cierre (12:50 – 14:00)

**[Pantalla]** Clic en **«Comparar las 3 configuraciones»**.

> Esta tabla resume las tres configuraciones con la misma entrada y salida. Original: distancia 4, 3 rutas y un corte de 3 pasillos. Modificación 1: distancia 4, 2 rutas y corte de 2. Modificación 2: distancia 3, 2 rutas y corte de 2. En las tres, el número de rutas coincide con el tamaño del corte mínimo, tal como dice el teorema de Menger, y todas las verificaciones dan OK.
>
> La conclusión principal es que la distancia mínima y la robustez de la red son cosas distintas. Los bloqueos redujeron las rutas independientes sin alargar el camino más corto, y el pasillo nuevo acortó el camino pero no recuperó la tercera ruta, porque el cuello de botella se movió al interior.
>
> Para resumir: usamos BFS para el camino mínimo, Edmonds-Karp con capacidad 1 para las rutas sin pasillos compartidos, y la red residual para obtener el corte mínimo, todo implementado con código propio y verificado. Muchas gracias por su atención.

**[Pantalla]** Opcional: los tres integrantes aparecen en cámara para despedirse.

---

## Resultados para tener a mano

Son los valores que deben aparecer en pantalla; están verificados con el código.

| Situación | ¿Camino? | d(s,t) y camino mínimo | Rutas sin arcos compartidos | Corte mínimo |
|---|---|---|---|---|
| Original | Sí | 4: s→A→D→G→t | 3 | {s→A, s→B, s→C} |
| Solo s→C bloqueado | Sí | 4: s→A→D→G→t | 2 | {s→A, s→B} |
| Modificación 1 (s→C y G→t bloqueados) | Sí | 4: s→A→E→H→t | 2 | {s→A, s→B} |
| G→t y H→t bloqueados | Sí | 4: s→C→F→I→t | 1 | {C→F} |
| Modificación 2 (+ pasillo D→t) | Sí | 3: s→A→D→t | 2 | {s→A, C→F} |
| Además I→t y D→t bloqueados | No | No definida | 0 | ∅ |
| Original con entrada B | Sí | 3: B→E→G→t | 2 | {B→E, B→C} |
| Caso de verificación (5 vértices) | Sí | 2: s→b→t | 2 | {s→a, s→b} |
| Contraejemplo voraz | Sí | 3: s→a→b→t | 2 (la estrategia voraz obtiene 1) | {s→a, s→c} |

**Si se acaba el tiempo:** acortar la sección 3.3; el caso de entrada B es lo primero que se puede saltar.

**Si sobra tiempo:** el video puede durar hasta 20 minutos. Se puede mostrar el modo «Camino mínimo» en cada modificación o explicar con más calma el contraejemplo voraz.
