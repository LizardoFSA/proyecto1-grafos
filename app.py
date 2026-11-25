"""
Simulador interactivo de laberintos y rutas alternativas – Interfaz gráfica (tkinter).

Ejecución:  python app.py

Funciones de la interfaz:
- Visualizar vértices y pasillos dirigidos (flechas). Los vértices se pueden arrastrar.
- Seleccionar entrada (s) y salida (t) distintas (listas o clic derecho sobre un vértice).
- Calcular y destacar: un camino mínimo (BFS), una familia máxima de caminos sin arcos
  compartidos (Edmonds-Karp) y los pasillos de un corte mínimo.
- Bloquear / restablecer pasillos (clic sobre la flecha o desde la lista).
- Agregar pasillos dirigidos (se rechazan lazos, repetidos y recíprocos).
- Cargar las configuraciones del proyecto, compararlas y comparar estrategias.
- Guardar / abrir la red en JSON.

La interfaz solo dibuja y llama a las funciones de laberinto/algoritmos.py, donde está
todo el código algorítmico propio.
"""

import math
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from laberinto.grafo import Grafo, ErrorGrafo
from laberinto import algoritmos as alg
from laberinto.configuraciones import catalogo, configuraciones_comparadas, ENTRADA, SALIDA

# ----------------------------------------------------------------------------- estilo
ANCHO_MODELO, ALTO_MODELO = 880, 540      # sistema de coordenadas de las posiciones
RADIO = 22
COLOR_ARCO = "#4a4a4a"
COLOR_BLOQUEADO = "#b5b5b5"
COLOR_MINIMO = "#ff9f1c"                  # camino mínimo (modo individual)
COLOR_MINIMO_FONDO = "#ffe08a"            # camino mínimo (franja de fondo en modo "Todo")
COLOR_CORTE = "#d62828"
COLOR_SELECCION = "#9ad0ff"
COLORES_CAMINOS = ["#1d4ed8", "#16a34a", "#9333ea", "#0891b2", "#a16207", "#db2777",
                   "#4d7c0f", "#7c2d12"]
COLOR_S, COLOR_T, COLOR_VERTICE, COLOR_LADO_S = "#86efac", "#fca5a5", "#ffffff", "#dbeafe"

MODOS = [("Todo", "todo"), ("Camino mínimo", "minimo"),
         ("Caminos sin arcos compartidos", "caminos"), ("Corte mínimo", "corte")]


class Aplicacion(tk.Tk):
    """Ventana principal del simulador."""

    def __init__(self):
        super().__init__()
        self.title("Simulador de laberintos y rutas alternativas – Teoría de Grafos INFO1158")
        # tamaño inicial ajustado a la pantalla (deja espacio para la barra de tareas)
        ancho = min(1400, self.winfo_screenwidth() - 40)
        alto = min(860, self.winfo_screenheight() - 90)
        self.geometry(f"{ancho}x{alto}+10+5")
        self.minsize(1000, 620)

        self.catalogo = catalogo()
        self.grafo = Grafo()
        self.s, self.t = ENTRADA, SALIDA
        self.analisis = None             # último resultado de alg.analizar()
        self.desactualizado = False      # True si la red cambió y no se ha recalculado
        self.arco_seleccionado = None
        self.arrastrando = None
        self.lista_arcos = []            # arcos en el mismo orden que el Listbox

        self.var_modo = tk.StringVar(value="todo")
        self.var_auto = tk.BooleanVar(value=True)
        self.var_config = tk.StringVar(value="Original")
        self.var_s, self.var_t = tk.StringVar(), tk.StringVar()
        self.var_origen, self.var_destino = tk.StringVar(), tk.StringVar()
        self.var_estado = tk.StringVar()

        self._construir_interfaz()
        self.cargar_configuracion("Original")

    # ======================================================================== interfaz
    def _construir_interfaz(self):
        """Crea los paneles: lienzo + resultados (izquierda) y controles (derecha)."""
        principal = ttk.Frame(self)
        principal.pack(fill="both", expand=True)

        izquierda = ttk.Frame(principal)
        izquierda.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)
        derecha = ttk.Frame(principal, width=360)
        derecha.pack(side="right", fill="y", padx=(4, 8), pady=8)

        # --- lienzo
        self.lienzo = tk.Canvas(izquierda, bg="#fbfbf8", highlightthickness=1,
                                highlightbackground="#cccccc")
        self.lienzo.pack(fill="both", expand=True)
        self.lienzo.bind("<Configure>", lambda e: self.dibujar())
        self.lienzo.bind("<ButtonPress-1>", self._al_presionar)
        self.lienzo.bind("<B1-Motion>", self._al_arrastrar)
        self.lienzo.bind("<ButtonRelease-1>", lambda e: setattr(self, "arrastrando", None))
        self.lienzo.bind("<Button-3>", self._menu_vertice)

        # --- leyenda
        self.leyenda = ttk.Frame(izquierda)
        self.leyenda.pack(fill="x", pady=(4, 2))

        # --- resultados
        marco_res = ttk.LabelFrame(izquierda, text="Resultados")
        marco_res.pack(fill="both", expand=False, pady=(4, 0))
        self.texto = tk.Text(marco_res, height=13, wrap="word", font=("Consolas", 10),
                             bg="#ffffff", relief="flat")
        barra = ttk.Scrollbar(marco_res, command=self.texto.yview)
        self.texto.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.texto.pack(fill="both", expand=True, padx=4, pady=4)
        self.texto.tag_configure("titulo", font=("Consolas", 10, "bold"))
        self.texto.tag_configure("ok", foreground="#15803d")
        self.texto.tag_configure("falla", foreground=COLOR_CORTE, font=("Consolas", 10, "bold"))
        self.texto.tag_configure("aviso", foreground=COLOR_CORTE, font=("Consolas", 10, "bold"))
        self.texto.tag_configure("minimo", foreground="#b45309", font=("Consolas", 10, "bold"))
        self.texto.tag_configure("corte", foreground=COLOR_CORTE, font=("Consolas", 10, "bold"))
        for i, c in enumerate(COLORES_CAMINOS):
            self.texto.tag_configure(f"p{i}", foreground=c, font=("Consolas", 10, "bold"))

        ttk.Label(self, textvariable=self.var_estado, anchor="w", relief="sunken",
                  padding=(6, 2)).pack(side="bottom", fill="x")

        self._construir_controles(derecha)

    def _construir_controles(self, padre):
        """Crea los grupos de controles del panel derecho."""
        pad = {"padx": 6, "pady": 3}

        # 1. Configuraciones
        f = ttk.LabelFrame(padre, text="Configuración de la red")
        f.pack(fill="x", pady=(0, 6))
        self.combo_config = ttk.Combobox(f, textvariable=self.var_config, state="readonly",
                                         values=list(self.catalogo.keys()), width=34)
        self.combo_config.grid(row=0, column=0, columnspan=2, sticky="ew", **pad)
        ttk.Button(f, text="Cargar configuración",
                   command=lambda: self.cargar_configuracion(self.var_config.get())
                   ).grid(row=1, column=0, sticky="ew", **pad)
        ttk.Button(f, text="Validar modelo", command=self.validar_modelo
                   ).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(f, text="Abrir JSON…", command=self.abrir_json
                   ).grid(row=2, column=0, sticky="ew", **pad)
        ttk.Button(f, text="Guardar JSON…", command=self.guardar_json
                   ).grid(row=2, column=1, sticky="ew", **pad)
        f.columnconfigure((0, 1), weight=1)

        # 2. Entrada / salida
        f = ttk.LabelFrame(padre, text="Entrada y salida")
        f.pack(fill="x", pady=6)
        ttk.Label(f, text="Entrada s:").grid(row=0, column=0, sticky="w", **pad)
        self.combo_s = ttk.Combobox(f, textvariable=self.var_s, state="readonly", width=7)
        self.combo_s.grid(row=0, column=1, **pad)
        ttk.Label(f, text="Salida t:").grid(row=0, column=2, sticky="w", **pad)
        self.combo_t = ttk.Combobox(f, textvariable=self.var_t, state="readonly", width=7)
        self.combo_t.grid(row=0, column=3, **pad)
        ttk.Button(f, text="Aplicar entrada/salida", command=self.aplicar_extremos
                   ).grid(row=1, column=0, columnspan=4, sticky="ew", **pad)
        ttk.Label(f, text="(También: clic derecho sobre un vértice)", foreground="#666"
                  ).grid(row=2, column=0, columnspan=4, sticky="w", padx=6)

        # 3. Pasillos
        f = ttk.LabelFrame(padre, text="Pasillos (clic en una flecha = bloquear/restablecer)")
        f.pack(fill="both", expand=True, pady=6)
        cont = ttk.Frame(f)
        cont.pack(fill="both", expand=True, **pad)
        self.lista = tk.Listbox(cont, height=9, font=("Consolas", 10), activestyle="none",
                                exportselection=False)
        barra = ttk.Scrollbar(cont, command=self.lista.yview)
        self.lista.configure(yscrollcommand=barra.set)
        self.lista.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.lista.bind("<<ListboxSelect>>", self._al_seleccionar_lista)
        self.lista.bind("<Double-Button-1>", lambda e: self.alternar_seleccionado())
        botones = ttk.Frame(f)
        botones.pack(fill="x", **pad)
        ttk.Button(botones, text="Bloquear / Restablecer", command=self.alternar_seleccionado
                   ).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(botones, text="Eliminar agregado", command=self.eliminar_seleccionado
                   ).pack(side="left", fill="x", expand=True, padx=(3, 0))
        ttk.Button(f, text="Restablecer todos los pasillos", command=self.restablecer_todos
                   ).pack(fill="x", **pad)

        # 4. Agregar pasillo
        f = ttk.LabelFrame(padre, text="Agregar pasillo dirigido")
        f.pack(fill="x", pady=6)
        ttk.Label(f, text="Desde:").grid(row=0, column=0, **pad)
        self.combo_origen = ttk.Combobox(f, textvariable=self.var_origen, state="readonly", width=6)
        self.combo_origen.grid(row=0, column=1, **pad)
        ttk.Label(f, text="Hacia:").grid(row=0, column=2, **pad)
        self.combo_destino = ttk.Combobox(f, textvariable=self.var_destino, state="readonly", width=6)
        self.combo_destino.grid(row=0, column=3, **pad)
        ttk.Button(f, text="Agregar", command=self.agregar_pasillo
                   ).grid(row=0, column=4, sticky="ew", **pad)

        # 5. Cálculo y visualización
        f = ttk.LabelFrame(padre, text="Resultados a destacar")
        f.pack(fill="x", pady=6)
        for i, (texto, valor) in enumerate(MODOS):
            ttk.Radiobutton(f, text=texto, value=valor, variable=self.var_modo,
                            command=self.dibujar).grid(row=i // 2, column=i % 2, sticky="w", **pad)
        ttk.Checkbutton(f, text="Recalcular automáticamente al modificar",
                        variable=self.var_auto).grid(row=2, column=0, columnspan=2, sticky="w", **pad)
        ttk.Button(f, text="▶  Recalcular", command=self.recalcular
                   ).grid(row=3, column=0, columnspan=2, sticky="ew", **pad)
        ttk.Button(f, text="Comparar las 3 configuraciones", command=self.ventana_comparacion
                   ).grid(row=4, column=0, columnspan=2, sticky="ew", **pad)
        ttk.Button(f, text="Comparar estrategias (BFS/DFS, flujo)", command=self.ventana_estrategias
                   ).grid(row=5, column=0, columnspan=2, sticky="ew", **pad)
        f.columnconfigure((0, 1), weight=1)

    # ====================================================================== estado
    def cargar_configuracion(self, nombre):
        """
        Carga una configuración del catálogo en el lienzo.

        Parámetros:
            nombre (str): clave del catálogo (Original, Modificación 1, …).
        """
        grafo, s, t = self.catalogo[nombre]
        self._establecer_grafo(grafo.copiar(), s, t)
        self.var_estado.set(f"Configuración cargada: {nombre}")

    def _establecer_grafo(self, grafo, s, t):
        """Reemplaza la red actual y sus extremos, y recalcula."""
        self.grafo, self.s, self.t = grafo, s, t
        self.arco_seleccionado = None
        vertices = list(grafo.vertices)
        for combo in (self.combo_s, self.combo_t, self.combo_origen, self.combo_destino):
            combo["values"] = vertices
        self.var_s.set(s)
        self.var_t.set(t)
        self.var_origen.set(vertices[0] if vertices else "")
        self.var_destino.set(vertices[1] if len(vertices) > 1 else "")
        self.recalcular()

    def red_modificada(self, mensaje):
        """Se llama tras cada cambio en la red: refresca la lista y recalcula o marca desactualizado."""
        self.var_estado.set(mensaje)
        if self.var_auto.get():
            self.recalcular(mensaje)
        else:
            self.desactualizado = True
            self._actualizar_lista()
            self._mostrar_resultados()
            self.dibujar()

    def recalcular(self, mensaje=None):
        """Ejecuta los algoritmos sobre la red actual y actualiza lista, texto y dibujo."""
        self.analisis = alg.analizar(self.grafo, self.s, self.t)
        self.desactualizado = False
        self._actualizar_lista()
        self._mostrar_resultados()
        self.dibujar()
        if mensaje is None:
            self.var_estado.set("Resultados recalculados.")

    # ================================================================== acciones
    def aplicar_extremos(self, s=None, t=None):
        """Cambia la entrada y la salida (deben ser distintas)."""
        s = s or self.var_s.get()
        t = t or self.var_t.get()
        if s == t:
            messagebox.showerror("Entrada y salida", "La entrada y la salida deben ser vértices distintos.")
            self.var_s.set(self.s)
            self.var_t.set(self.t)
            return
        self.s, self.t = s, t
        self.var_s.set(s)
        self.var_t.set(t)
        self.red_modificada(f"Nueva entrada s = {s}, salida t = {t}.")

    def alternar_arco(self, arco):
        """Bloquea o restablece un pasillo."""
        activo = self.grafo.alternar_bloqueo(*arco)
        self.arco_seleccionado = arco
        accion = "restablecido" if activo else "bloqueado"
        self.red_modificada(f"Pasillo {arco[0]} → {arco[1]} {accion}.")

    def alternar_seleccionado(self):
        """Bloquea/restablece el pasillo seleccionado en la lista."""
        if not self.arco_seleccionado:
            messagebox.showinfo("Pasillos", "Seleccione un pasillo de la lista o haga clic en una flecha.")
            return
        self.alternar_arco(self.arco_seleccionado)

    def eliminar_seleccionado(self):
        """Elimina un pasillo agregado por el usuario (los originales solo se bloquean)."""
        arco = self.arco_seleccionado
        if not arco:
            messagebox.showinfo("Pasillos", "Seleccione un pasillo de la lista.")
            return
        if not self.grafo.arcos[arco]["agregado"]:
            messagebox.showinfo("Pasillos", "Solo se eliminan pasillos agregados.\n"
                                "Los pasillos de la configuración se bloquean.")
            return
        self.grafo.eliminar_arco(*arco)
        self.arco_seleccionado = None
        self.red_modificada(f"Pasillo agregado {arco[0]} → {arco[1]} eliminado.")

    def restablecer_todos(self):
        """Reactiva todos los pasillos bloqueados."""
        for arco in self.grafo.arcos_bloqueados():
            self.grafo.restablecer(*arco)
        self.red_modificada("Todos los pasillos fueron restablecidos.")

    def agregar_pasillo(self):
        """Agrega el pasillo Desde → Hacia validando las restricciones del modelo."""
        u, v = self.var_origen.get(), self.var_destino.get()
        try:
            self.grafo.agregar_arco(u, v, agregado=True)
        except ErrorGrafo as e:
            messagebox.showerror("Pasillo no admitido", str(e))
            return
        self.arco_seleccionado = (u, v)
        self.red_modificada(f"Pasillo {u} → {v} agregado.")

    def validar_modelo(self):
        """Muestra las condiciones exigidas a la configuración inicial para la red actual."""
        checks = alg.validar_modelo_completo(self.grafo, self.s, self.t)
        texto = "\n".join(f"{'✔' if ok else '✘'}  {d}" for d, ok in checks)
        nota = ("\n\nNota: las cotas de |V| y |E| se exigen solo a la configuración inicial."
                "\nSe consideran todos los pasillos, incluidos los bloqueados.")
        (messagebox.showinfo if all(ok for _, ok in checks) else messagebox.showwarning)(
            "Validación del modelo", texto + nota)

    def guardar_json(self):
        """Guarda la red actual (con s y t) en un archivo JSON."""
        ruta = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON", "*.json")])
        if ruta:
            self.grafo.guardar_json(ruta, {"entrada": self.s, "salida": self.t})
            self.var_estado.set(f"Red guardada en {ruta}")

    def abrir_json(self):
        """Abre una red guardada en JSON."""
        ruta = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not ruta:
            return
        try:
            grafo, datos = Grafo.cargar_json(ruta)
        except (ErrorGrafo, KeyError, ValueError, OSError) as e:
            messagebox.showerror("Abrir JSON", f"No se pudo cargar la red:\n{e}")
            return
        s = datos.get("entrada", grafo.vertices[0])
        t = datos.get("salida", grafo.vertices[-1])
        self._establecer_grafo(grafo, s, t)
        self.var_estado.set(f"Red cargada desde {ruta}")

    # ======================================================================= lista
    def _actualizar_lista(self):
        """Rellena la lista de pasillos con su estado."""
        self.lista.delete(0, "end")
        self.lista_arcos = list(self.grafo.arcos.keys())
        corte = set(self.analisis["flujo"]["corte"]) if self.analisis and not self.desactualizado else set()
        for i, (u, v) in enumerate(self.lista_arcos):
            d = self.grafo.arcos[(u, v)]
            estado = "activo" if d["activo"] else "BLOQUEADO"
            extra = (" (nuevo)" if d["agregado"] else "") + (" [corte]" if (u, v) in corte else "")
            self.lista.insert("end", f"{u:>2} → {v:<2}  {estado}{extra}")
            if not d["activo"]:
                self.lista.itemconfig(i, foreground="#888888")
            elif (u, v) in corte:
                self.lista.itemconfig(i, foreground=COLOR_CORTE)
            if (u, v) == self.arco_seleccionado:
                self.lista.selection_set(i)
                self.lista.see(i)

    def _al_seleccionar_lista(self, _evento):
        sel = self.lista.curselection()
        if sel:
            self.arco_seleccionado = self.lista_arcos[sel[0]]
            self.dibujar()

    # =================================================================== resultados
    def _mostrar_resultados(self):
        """Escribe el informe del análisis en el panel de texto, con colores."""
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        if self.desactualizado:
            self.texto.insert("end", "⚠ La red fue modificada. Presione «Recalcular» para "
                                     "actualizar los resultados.\n\n", "aviso")
        if self.analisis:
            for linea in alg.informe_texto(self.grafo, self.analisis).split("\n"):
                tag = ()
                l = linea.strip()
                if l[:2] in ("1)", "2)", "3)", "4)"):
                    tag = ("titulo",)
                elif l.startswith("[OK]"):
                    tag = ("ok",)
                elif l.startswith("[FALLA]"):
                    tag = ("falla",)
                elif l.startswith("Camino:") or l.startswith("d(s,t)"):
                    tag = ("minimo",)
                elif l.startswith("|C|") or l.startswith("Existe camino: NO"):
                    tag = ("corte",)
                elif l.startswith("P") and l[1:2].isdigit():
                    i = int(l[1:l.index(" ")]) - 1
                    tag = (f"p{i % len(COLORES_CAMINOS)}",)
                self.texto.insert("end", linea + "\n", tag)
        self.texto.configure(state="disabled")
        self._actualizar_leyenda()

    def _actualizar_leyenda(self):
        """Dibuja la leyenda de colores debajo del lienzo."""
        for w in self.leyenda.winfo_children():
            w.destroy()

        def item(color, texto, discontinuo=False, cruz=False):
            c = tk.Canvas(self.leyenda, width=34, height=16, highlightthickness=0, bg=self.cget("bg"))
            c.create_line(2, 8, 32, 8, fill=color, width=4, dash=(4, 3) if discontinuo else None,
                          arrow="last")
            if cruz:
                c.create_text(17, 8, text="✕", fill=COLOR_CORTE, font=("Arial", 10, "bold"))
            c.pack(side="left", padx=(8, 2))
            ttk.Label(self.leyenda, text=texto).pack(side="left")

        item(COLOR_MINIMO, "Camino mínimo")
        if self.analisis and not self.desactualizado:
            for i in range(self.analisis["flujo"]["valor"]):
                item(COLORES_CAMINOS[i % len(COLORES_CAMINOS)], f"P{i + 1}")
        item(COLOR_CORTE, "Corte mínimo", cruz=True)
        item(COLOR_BLOQUEADO, "Bloqueado", discontinuo=True)

    # ===================================================================== dibujo
    def _escala(self):
        """Retorna (factor, desplazamiento_x, desplazamiento_y) para ajustar el modelo al lienzo."""
        w = max(self.lienzo.winfo_width(), 100)
        h = max(self.lienzo.winfo_height(), 100)
        f = min(w / ANCHO_MODELO, h / ALTO_MODELO)
        return f, (w - ANCHO_MODELO * f) / 2, (h - ALTO_MODELO * f) / 2

    def _a_pantalla(self, v):
        f, dx, dy = self._escala()
        x, y = self.grafo.posiciones[v]
        return x * f + dx, y * f + dy

    def _extremos_arco(self, u, v):
        """Coordenadas de pantalla del segmento u→v recortado al borde de los círculos."""
        x1, y1 = self._a_pantalla(u)
        x2, y2 = self._a_pantalla(v)
        r = RADIO * self._escala()[0]
        d = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        return x1 + ux * r, y1 + uy * r, x2 - ux * (r + 2), y2 - uy * (r + 2)

    def dibujar(self):
        """Redibuja toda la red destacando los resultados según el modo elegido."""
        cv = self.lienzo
        cv.delete("all")
        if not self.grafo.vertices:
            return
        f = self._escala()[0]
        modo = self.var_modo.get()
        mostrar = self.analisis is not None and not self.desactualizado

        arcos_min, arco_camino, arcos_corte, lado_s = set(), {}, set(), set()
        if mostrar:
            c = self.analisis["minimo"]["camino"]
            arcos_min = set(zip(c, c[1:]))
            for i, cam in enumerate(self.analisis["flujo"]["caminos"]):
                for a in zip(cam, cam[1:]):
                    arco_camino[a] = i
            arcos_corte = set(self.analisis["flujo"]["corte"])
            lado_s = self.analisis["flujo"]["lado_s"]

        # 1) franjas de fondo: selección y camino mínimo (modo "Todo")
        for (u, v) in self.grafo.arcos:
            x1, y1, x2, y2 = self._extremos_arco(u, v)
            if (u, v) == self.arco_seleccionado:
                cv.create_line(x1, y1, x2, y2, fill=COLOR_SELECCION, width=max(14 * f, 8),
                               capstyle="round")
            if modo == "todo" and (u, v) in arcos_min:
                cv.create_line(x1, y1, x2, y2, fill=COLOR_MINIMO_FONDO, width=max(12 * f, 7),
                               capstyle="round")

        # 2) pasillos
        flecha = (12 * f + 2, 14 * f + 2, 5 * f + 1)
        flecha_g = (15 * f + 3, 17 * f + 3, 6 * f + 2)
        for (u, v), datos in self.grafo.arcos.items():
            x1, y1, x2, y2 = self._extremos_arco(u, v)
            color, ancho, forma, guiones = COLOR_ARCO, 2, flecha, None
            if not datos["activo"]:
                color, guiones = COLOR_BLOQUEADO, (6, 4)
            elif modo in ("todo", "caminos") and (u, v) in arco_camino:
                color = COLORES_CAMINOS[arco_camino[(u, v)] % len(COLORES_CAMINOS)]
                ancho, forma = 4, flecha_g
            elif modo == "minimo" and (u, v) in arcos_min:
                color, ancho, forma = COLOR_MINIMO, 5, flecha_g
            elif modo == "corte" and (u, v) in arcos_corte:
                color, ancho, forma = COLOR_CORTE, 4, flecha_g
            elif modo != "todo" and mostrar:
                color = "#9a9a9a"  # atenuar lo que no forma parte del resultado elegido
            cv.create_line(x1, y1, x2, y2, fill=color, width=ancho, arrow="last",
                           arrowshape=forma, dash=guiones)
            if datos["agregado"]:
                mx, my = x1 + (x2 - x1) * 0.25, y1 + (y2 - y1) * 0.25
                cv.create_text(mx, my - 10 * f, text="nuevo", fill="#555",
                               font=("Arial", max(int(8 * f), 7), "italic"))
            if not datos["activo"]:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                cv.create_text(mx, my, text="⛔", font=("Arial", max(int(11 * f), 8)))

        # 3) marcas del corte mínimo
        if modo in ("todo", "corte"):
            for (u, v) in arcos_corte:
                x1, y1, x2, y2 = self._extremos_arco(u, v)
                mx, my = x1 + (x2 - x1) * 0.45, y1 + (y2 - y1) * 0.45
                r = max(9 * f, 7)
                cv.create_oval(mx - r, my - r, mx + r, my + r, fill="white",
                               outline=COLOR_CORTE, width=2)
                cv.create_text(mx, my, text="✕", fill=COLOR_CORTE,
                               font=("Arial", max(int(10 * f), 8), "bold"))

        # 4) vértices
        r = RADIO * f
        fuente = ("Arial", max(int(12 * f), 8), "bold")
        for v in self.grafo.vertices:
            x, y = self._a_pantalla(v)
            relleno = COLOR_VERTICE
            if modo == "corte" and v in lado_s:
                relleno = COLOR_LADO_S
            if v == self.s:
                relleno = COLOR_S
            elif v == self.t:
                relleno = COLOR_T
            grosor = 3 if v in (self.s, self.t) else 1.5
            cv.create_oval(x - r, y - r, x + r, y + r, fill=relleno, outline="#222", width=grosor)
            cv.create_text(x, y, text=v, font=fuente)
            if v in (self.s, self.t):
                cv.create_text(x, y + r + 9 * f, text="entrada" if v == self.s else "salida",
                               font=("Arial", max(int(9 * f), 7)), fill="#333")

        # 5) aviso si no hay camino
        if mostrar and not self.analisis["minimo"]["existe"]:
            cv.create_text(12, 12, anchor="nw", fill=COLOR_CORTE, font=("Arial", 12, "bold"),
                           text=f"No existe camino de {self.s} a {self.t}: 0 caminos disponibles; "
                                f"el conjunto vacío ya impide el desplazamiento.")
        elif modo == "corte" and mostrar:
            cv.create_text(12, 12, anchor="nw", fill="#1e3a8a", font=("Arial", 10),
                           text="Vértices azules: lado S del corte (alcanzables desde s en la red residual)")
        elif self.desactualizado:
            cv.create_text(12, 12, anchor="nw", fill=COLOR_CORTE, font=("Arial", 11, "bold"),
                           text="Resultados desactualizados: presione «Recalcular».")

    # ================================================================== mouse
    def _vertice_en(self, x, y):
        """Retorna el vértice bajo el punto de pantalla (x, y), o None."""
        r = RADIO * self._escala()[0]
        for v in reversed(self.grafo.vertices):
            vx, vy = self._a_pantalla(v)
            if math.hypot(x - vx, y - vy) <= r:
                return v
        return None

    def _arco_en(self, x, y, tolerancia=7):
        """Retorna el arco más cercano al punto (x, y) si está a menos de 'tolerancia' píxeles."""
        mejor, dist_min = None, tolerancia
        for (u, v) in self.grafo.arcos:
            x1, y1, x2, y2 = self._extremos_arco(u, v)
            dx, dy = x2 - x1, y2 - y1
            largo2 = dx * dx + dy * dy or 1
            k = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / largo2))
            d = math.hypot(x - (x1 + k * dx), y - (y1 + k * dy))
            if d < dist_min:
                mejor, dist_min = (u, v), d
        return mejor

    def _al_presionar(self, e):
        """Clic izquierdo: arrastrar vértice o bloquear/restablecer pasillo."""
        v = self._vertice_en(e.x, e.y)
        if v:
            self.arrastrando = v
            return
        arco = self._arco_en(e.x, e.y)
        if arco:
            self.alternar_arco(arco)

    def _al_arrastrar(self, e):
        """Mueve el vértice que se está arrastrando."""
        if not self.arrastrando:
            return
        f, dx, dy = self._escala()
        x = min(max((e.x - dx) / f, RADIO), ANCHO_MODELO - RADIO)
        y = min(max((e.y - dy) / f, RADIO), ALTO_MODELO - RADIO)
        self.grafo.posiciones[self.arrastrando] = (x, y)
        self.dibujar()

    def _menu_vertice(self, e):
        """Clic derecho sobre un vértice: elegirlo como entrada o salida."""
        v = self._vertice_en(e.x, e.y)
        if not v:
            return
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=f"Usar {v} como entrada (s)", command=lambda: self.aplicar_extremos(v, self.t))
        menu.add_command(label=f"Usar {v} como salida (t)", command=lambda: self.aplicar_extremos(self.s, v))
        menu.tk_popup(e.x_root, e.y_root)

    # ============================================================== ventanas extra
    def ventana_comparacion(self):
        """
        Muestra una tabla con los resultados de las tres configuraciones del proyecto
        (Original, Modificación 1 y 2, con los mismos s y t) y de la red actual en pantalla.
        """
        filas = []
        for nombre, desc, g in configuraciones_comparadas():
            filas.append((nombre, desc, g, ENTRADA, SALIDA))
        filas.append(("Actual (pantalla)", "Red que se está editando.", self.grafo, self.s, self.t))

        win = tk.Toplevel(self)
        win.title("Comparación de configuraciones")
        win.geometry("1400x330")
        cols = ("conf", "desc", "s_t", "existe", "d", "minimo", "k", "caminos", "corte", "ok")
        titulos = ("Configuración", "Modificación", "s, t", "¿Camino?", "d(s,t)", "Camino mínimo",
                   "Máx. caminos", "Caminos sin arcos compartidos", "Corte mínimo C", "Verificación")
        anchos = (120, 220, 50, 65, 55, 160, 85, 330, 160, 85)
        arbol = ttk.Treeview(win, columns=cols, show="headings", height=6)
        for c, ti, an in zip(cols, titulos, anchos):
            arbol.heading(c, text=ti)
            arbol.column(c, width=an, anchor="w")
        arbol.pack(fill="both", expand=True, padx=8, pady=8)

        texto_tabla = ["\t".join(titulos)]
        for nombre, desc, g, s, t in filas:
            a = alg.analizar(g, s, t)
            m, fl = a["minimo"], a["flujo"]
            valores = (nombre, desc, f"{s}, {t}", "Sí" if m["existe"] else "No",
                       m["longitud"] if m["existe"] else "—",
                       alg.formato_camino(m["camino"]) if m["existe"] else "No existe",
                       fl["valor"],
                       " | ".join(alg.formato_camino(c) for c in fl["caminos"]) or "Ninguno",
                       alg.formato_arcos(fl["corte"]),
                       "OK" if all(ok for _, ok in a["verificacion"]) else "FALLA")
            arbol.insert("", "end", values=valores)
            texto_tabla.append("\t".join(str(x) for x in valores))

        def copiar():
            self.clipboard_clear()
            self.clipboard_append("\n".join(texto_tabla))
            self.var_estado.set("Tabla copiada al portapapeles (separada por tabulaciones).")

        ttk.Button(win, text="Copiar tabla al portapapeles", command=copiar).pack(pady=(0, 8))

    def ventana_estrategias(self):
        """
        Compara, sobre la red actual, las estrategias investigadas:
        BFS vs DFS para caminos, y Edmonds-Karp vs Ford-Fulkerson(DFS) vs voraz para
        caminos sin arcos compartidos (valor, caminos de aumento y tiempo medio).
        """
        g, s, t = self.grafo, self.s, self.t

        def medir(func, *args, repeticiones=300):
            inicio = time.perf_counter()
            for _ in range(repeticiones):
                r = func(*args)
            return r, (time.perf_counter() - inicio) / repeticiones * 1e6

        bfs, t_bfs = medir(alg.bfs_camino_minimo, g, s, t)
        dfs, t_dfs = medir(alg.dfs_camino, g, s, t)
        ek, t_ek = medir(alg.max_caminos_disjuntos, g, s, t, "bfs")
        ff, t_ff = medir(alg.max_caminos_disjuntos, g, s, t, "dfs")
        vz, t_vz = medir(alg.caminos_disjuntos_voraz, g, s, t)

        def cam(r):
            return f"{alg.formato_camino(r['camino'])}  (longitud {r['longitud']})" if r["existe"] else "No existe"

        lineas = [
            f"Red actual, s = {s}, t = {t}", "",
            "CAMINO DE s A t",
            f"  BFS (seleccionada): {cam(bfs)}   [{t_bfs:.1f} µs]",
            f"  DFS               : {cam(dfs)}   [{t_dfs:.1f} µs]",
            "  → BFS garantiza el mínimo número de arcos; DFS solo garantiza encontrar un camino.", "",
            "MÁXIMO NÚMERO DE CAMINOS SIN ARCOS COMPARTIDOS",
            f"  Edmonds-Karp (seleccionada): {ek['valor']} caminos, {len(ek['aumentos'])} caminos "
            f"de aumento   [{t_ek:.1f} µs]",
        ]
        lineas += [f"      aumento {i}: {alg.formato_camino(c)}" for i, c in enumerate(ek["aumentos"], 1)]
        lineas += [f"  Ford-Fulkerson con DFS    : {ff['valor']} caminos, {len(ff['aumentos'])} "
                   f"caminos de aumento   [{t_ff:.1f} µs]"]
        lineas += [f"      aumento {i}: {alg.formato_camino(c)}" for i, c in enumerate(ff["aumentos"], 1)]
        lineas += [f"  Voraz (BFS + borrar arcos): {vz['valor']} caminos   [{t_vz:.1f} µs]"
                   + ("   ← NO óptimo en esta red" if vz["valor"] < ek["valor"] else "")]
        lineas += [f"      {alg.formato_camino(c)}" for c in vz["caminos"]]
        lineas += ["", "  Los métodos de flujo usan la red residual (arcos inversos) y pueden",
                   "  reasignar arcos ya usados; la estrategia voraz no, por eso puede quedarse corta.",
                   "  (Ver la configuración «Contraejemplo estrategia voraz».)"]

        win = tk.Toplevel(self)
        win.title("Comparación de estrategias")
        win.geometry("820x480")
        txt = tk.Text(win, font=("Consolas", 10), wrap="none")
        txt.insert("1.0", "\n".join(lineas))
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=8, pady=8)


def main():
    """Punto de entrada de la aplicación."""
    app = Aplicacion()
    app.mainloop()


if __name__ == "__main__":
    main()
