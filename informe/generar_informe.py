"""
Genera el informe técnico en PDF (informe/Informe_Proyecto1_Grafos.pdf).

Ejecución (desde la carpeta raíz del proyecto):
    python informe/generar_informe.py

Requiere reportlab (solo para generar el informe; la aplicación no lo necesita):
    pip install reportlab

Los resultados numéricos se calculan en el momento con el código del proyecto, de modo que
el informe siempre coincide con lo que muestra la aplicación. Las imágenes están en informe/img
(capturas de la aplicación).

Los datos del grupo se editan en la sección DATOS DEL GRUPO.
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate,  # noqa: E402
                                PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table,
                                TableStyle, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents  # noqa: E402

from laberinto import algoritmos as alg  # noqa: E402
from laberinto.configuraciones import (red_original, configuraciones_comparadas,  # noqa: E402
                                       caso_verificacion, contraejemplo_voraz, MODIFICACIONES)

# =========================================================================== DATOS DEL GRUPO
INTEGRANTES = ["Benjamín Aliaga", "Juan Carrera", "Lizardo Salazar"]
DOCENTE = "Elliott Mardones"
FECHA = "26 de noviembre de 2026"

SALIDA_PDF = os.path.join(RAIZ, "informe", "Informe_Proyecto1_Grafos.pdf")
IMG = os.path.join(RAIZ, "informe", "img")

# =========================================================================== FUENTES Y ESTILOS
FUENTES = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont("Cuerpo", os.path.join(FUENTES, "cambria.ttc"), subfontIndex=0))
pdfmetrics.registerFont(TTFont("Cuerpo-B", os.path.join(FUENTES, "cambriab.ttf")))
pdfmetrics.registerFont(TTFont("Cuerpo-I", os.path.join(FUENTES, "cambriai.ttf")))
pdfmetrics.registerFont(TTFont("Cuerpo-BI", os.path.join(FUENTES, "cambriaz.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(FUENTES, "consola.ttf")))
pdfmetrics.registerFont(TTFont("Mono-B", os.path.join(FUENTES, "consolab.ttf")))
pdfmetrics.registerFontFamily("Cuerpo", normal="Cuerpo", bold="Cuerpo-B", italic="Cuerpo-I",
                              boldItalic="Cuerpo-BI")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-B", italic="Mono", boldItalic="Mono-B")

AZUL = colors.HexColor("#1f3a5f")
GRIS = colors.HexColor("#555555")
FONDO_TABLA = colors.HexColor("#e8eef5")
FONDO_CODIGO = colors.HexColor("#f4f4f1")
VERDE = colors.HexColor("#15803d")

E = {
    "cuerpo": ParagraphStyle("cuerpo", fontName="Cuerpo", fontSize=10.5, leading=14.6,
                             alignment=TA_JUSTIFY, spaceAfter=6),
    "lista": ParagraphStyle("lista", fontName="Cuerpo", fontSize=10.5, leading=14.4,
                            alignment=TA_JUSTIFY, leftIndent=16, bulletIndent=5, spaceAfter=3),
    "h1": ParagraphStyle("h1", keepWithNext=1, fontName="Cuerpo-B", fontSize=16, leading=20, textColor=AZUL,
                         spaceBefore=6, spaceAfter=10),
    "h2": ParagraphStyle("h2", keepWithNext=1, fontName="Cuerpo-B", fontSize=12.5, leading=16, textColor=AZUL,
                         spaceBefore=10, spaceAfter=5),
    "h3": ParagraphStyle("h3", keepWithNext=1, fontName="Cuerpo-BI", fontSize=11, leading=14, textColor=colors.black,
                         spaceBefore=6, spaceAfter=3),
    "formula": ParagraphStyle("formula", fontName="Cuerpo", fontSize=11, leading=16,
                              alignment=TA_CENTER, spaceBefore=4, spaceAfter=8),
    "pie": ParagraphStyle("pie", fontName="Cuerpo-I", fontSize=9, leading=11.5, textColor=GRIS,
                          alignment=TA_CENTER, spaceBefore=3, spaceAfter=10),
    "celda": ParagraphStyle("celda", fontName="Cuerpo", fontSize=9.3, leading=11.8, alignment=TA_LEFT),
    "celda_b": ParagraphStyle("celda_b", fontName="Cuerpo-B", fontSize=9.3, leading=11.8),
    "codigo": ParagraphStyle("codigo", fontName="Mono", fontSize=8.4, leading=10.6),
    "ref": ParagraphStyle("ref", fontName="Cuerpo", fontSize=9.8, leading=12.6, leftIndent=18,
                          firstLineIndent=-18, spaceAfter=3, alignment=TA_LEFT),
}

ANCHO_UTIL = A4[0] - 2 * 2.3 * cm
contador = {"fig": 0, "tab": 0}
REF = {}


# =========================================================================== AYUDAS
def P(texto, estilo="cuerpo"):
    """Párrafo con el estilo indicado."""
    return Paragraph(texto, E[estilo])


def vinetas(items):
    """Lista con viñetas."""
    return [Paragraph(t, E["lista"], bulletText="•") for t in items]


def figura(nombre, pie, ancho_cm=15.5):
    """Imagen de informe/img escalada al ancho indicado, con pie numerado."""
    from PIL import Image as PILImage
    ruta = os.path.join(IMG, nombre)
    w, h = PILImage.open(ruta).size
    ancho = min(ancho_cm * cm, ANCHO_UTIL)
    contador["fig"] += 1
    img = Image(ruta, width=ancho, height=ancho * h / w)
    return KeepTogether([img, P(f"<b>Figura {contador['fig']}.</b> {pie}", "pie")])


def tabla(filas, anchos, pie=None, encabezado=True, alinear_centro=()):
    """
    Tabla con encabezado sombreado. 'filas' puede contener str o Paragraph.
    'alinear_centro' indica columnas centradas.
    """
    datos = []
    for i, fila in enumerate(filas):
        datos.append([c if not isinstance(c, str) else
                      Paragraph(c, E["celda_b"] if (encabezado and i == 0) else E["celda"])
                      for c in fila])
    t = Table(datos, colWidths=[a * cm for a in anchos], repeatRows=1 if encabezado else 0)
    estilo = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9aa7b5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    if encabezado:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), FONDO_TABLA))
    for c in alinear_centro:
        estilo.append(("ALIGN", (c, 0), (c, -1), "CENTER"))
    t.setStyle(TableStyle(estilo))
    bloque = []
    if pie:
        contador["tab"] += 1
        bloque.append(P(f"<b>Tabla {contador['tab']}.</b> {pie}", "pie"))
    bloque.append(t)
    bloque.append(Spacer(1, 8))
    return KeepTogether(bloque)


def codigo(texto):
    """Bloque de pseudocódigo/código con fondo gris."""
    pre = Preformatted(texto.strip("\n"), E["codigo"])
    t = Table([[pre]], colWidths=[ANCHO_UTIL])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FONDO_CODIGO),
                           ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#c8c8c0")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return KeepTogether([t, Spacer(1, 8)])


def cam(c):
    """Camino como texto con flechas."""
    return " → ".join(c)


def arcos_txt(arcos):
    """Conjunto de arcos como texto."""
    return "∅" if not arcos else "{" + ", ".join(f"{u}→{v}" for u, v in arcos) + "}"


def ok(b):
    return f"<font color='#15803d'><b>Cumple</b></font>" if b else "<font color='#d62828'><b>No cumple</b></font>"


# =========================================================================== CÁLCULOS
G0 = red_original()
CONFIGS = [(n, d, g, alg.analizar(g, "s", "t")) for n, d, g in configuraciones_comparadas()]
A0 = CONFIGS[0][3]
GV = caso_verificacion()
AV = alg.analizar(GV, "s", "t")
GC = contraejemplo_voraz()
FC = alg.max_caminos_disjuntos(GC, "s", "t")
VC = alg.caminos_disjuntos_voraz(GC, "s", "t")
DFS0 = alg.dfs_camino(G0, "s", "t")
g_inter = red_original()
g_inter.bloquear("G", "t")
g_inter.bloquear("H", "t")
A_INTER = alg.analizar(g_inter, "s", "t")

# Comprobación de que el texto (escrito a partir de estos valores) sigue siendo válido.
_esperado = {"Original": (4, 3, 3), "Modificación 1": (4, 2, 2), "Modificación 2": (3, 2, 2)}
for _n, _d, _g, _a in CONFIGS:
    assert (_a["minimo"]["longitud"], _a["flujo"]["valor"], len(_a["flujo"]["corte"])) == _esperado[_n], _n
    assert all(v for _, v in _a["verificacion"]), _n
assert (AV["minimo"]["longitud"], AV["flujo"]["valor"]) == (2, 2)
assert (FC["valor"], VC["valor"]) == (2, 1)
assert DFS0["longitud"] == 5
assert (A_INTER["flujo"]["valor"], A_INTER["minimo"]["longitud"]) == (1, 4)


# =========================================================================== PÁGINA
def decorar(canv, doc):
    """Encabezado y pie de página (excepto portada)."""
    canv.saveState()
    canv.setFont("Cuerpo", 8.5)
    canv.setFillColor(GRIS)
    canv.drawString(2.3 * cm, A4[1] - 1.5 * cm, "Teoría de Grafos – INFO1158")
    canv.drawRightString(A4[0] - 2.3 * cm, A4[1] - 1.5 * cm,
                         "Proyecto 1 · Simulador de laberintos y rutas alternativas")
    canv.setStrokeColor(colors.HexColor("#b8c2cc"))
    canv.setLineWidth(0.5)
    canv.line(2.3 * cm, A4[1] - 1.65 * cm, A4[0] - 2.3 * cm, A4[1] - 1.65 * cm)
    canv.drawCentredString(A4[0] / 2, 1.2 * cm, str(doc.page))
    canv.restoreState()


class DocumentoInforme(BaseDocTemplate):
    """Documento que registra cada título de sección (h1) y subsección (h2) en el índice con su página."""

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ("h1", "h2"):
            texto = flowable.getPlainText()
            if texto != "Contenido":
                self.notify("TOCEntry", (0 if flowable.style.name == "h1" else 1, texto, self.page))


def construir_documento():
    doc = DocumentoInforme(SALIDA_PDF, pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm,
                          topMargin=2.2 * cm, bottomMargin=2.0 * cm,
                          title="Informe técnico – Proyecto 1: Simulador de laberintos y rutas alternativas",
                          author=", ".join(INTEGRANTES), subject="Teoría de Grafos – INFO1158")
    marco = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="m")
    doc.addPageTemplates([PageTemplate(id="portada", frames=[marco]),
                          PageTemplate(id="normal", frames=[marco], onPage=decorar)])
    return doc


# =========================================================================== CONTENIDO
def portada():
    h = []
    # Logo de la Universidad Católica de Temuco – Facultad de Ingeniería
    from PIL import Image as PILImage
    ruta_logo = os.path.join(IMG, "logo_uct.png")
    lw, lh = PILImage.open(ruta_logo).size
    h.append(Image(ruta_logo, width=10 * cm, height=10 * cm * lh / lw))
    h.append(Spacer(1, 0.8 * cm))
    h.append(P("<font color='#555555'>Teoría de Grafos – INFO1158 · Proyecto práctico final</font>",
               "formula"))
    h.append(Spacer(1, 0.6 * cm))
    h.append(Paragraph("Proyecto 1<br/>Simulador interactivo de laberintos y rutas alternativas",
                       ParagraphStyle("t", fontName="Cuerpo-B", fontSize=22, leading=28,
                                      alignment=TA_CENTER, textColor=AZUL)))
    h.append(Spacer(1, 0.4 * cm))
    h.append(Paragraph("Informe técnico", ParagraphStyle("st", fontName="Cuerpo-I", fontSize=14,
                                                         leading=18, alignment=TA_CENTER, textColor=GRIS)))
    h.append(Spacer(1, 1.0 * cm))
    from PIL import Image as PILImage
    ruta = os.path.join(IMG, "modelo_original.png")
    w, hh = PILImage.open(ruta).size
    h.append(Image(ruta, width=13 * cm, height=13 * cm * hh / w))
    h.append(Spacer(1, 1.0 * cm))
    datos = [["Integrantes", "<br/>".join(INTEGRANTES)],
             ["Docente", DOCENTE],
             ["Fecha de entrega", FECHA]]
    t = Table([[Paragraph(a, E["celda_b"]), Paragraph(b, E["celda"])] for a, b in datos],
              colWidths=[4 * cm, 10 * cm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#c0c8d0")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    h.append(t)
    h.append(NextPageTemplate("normal"))
    h.append(PageBreak())
    return h


def indice():
    """Índice con números de página, generado automáticamente a partir de los títulos (h1 y h2)."""
    indice_auto = TableOfContents()
    indice_auto.dotsMinLevel = 0
    indice_auto.levelStyles = [
        ParagraphStyle("indice0", fontName="Cuerpo-B", fontSize=11, leading=14, spaceBefore=6,
                       leftIndent=0, firstLineIndent=0),
        ParagraphStyle("indice1", fontName="Cuerpo", fontSize=10, leading=12.8, spaceBefore=0,
                       leftIndent=18, firstLineIndent=0),
    ]
    return [P("Contenido", "h1"), indice_auto]


def introduccion():
    h = [P("1. Introducción", "h1")]
    h.append(P(
        "Un centro de almacenamiento utiliza robots de inspección que circulan por pasillos de "
        "sentido único. Cada inspección exige llegar desde una entrada <i>s</i> hasta una salida "
        "<i>t</i> respetando los sentidos de circulación. El centro necesita (i) encontrar un "
        "trayecto con el menor número de pasillos, (ii) saber cuántas rutas pueden mantenerse sin "
        "depender de los mismos pasillos y (iii) identificar qué bloqueos mínimos impedirían el "
        "acceso a la salida, observando además cómo cambian estas respuestas cuando la red se modifica."))
    h.append(P(
        "En este informe se modela el laberinto como un grafo dirigido, se comparan estrategias "
        "algorítmicas para los tres problemas, se justifica la elección de la búsqueda en anchura "
        "(BFS) para el camino mínimo y del algoritmo de Edmonds-Karp (flujo máximo con capacidad "
        "unitaria) para los caminos sin arcos compartidos y el corte mínimo, y se describe una "
        "aplicación interactiva en Python, con código algorítmico propio, que permite bloquear y "
        "restablecer pasillos, agregar pasillos y cambiar la entrada y la salida. Finalmente se "
        "analizan tres configuraciones de la red y se verifican los resultados, tanto con un caso "
        "resuelto manualmente como mediante comprobaciones automáticas."))
    return h


def modelo():
    h = [P("2. Modelación matemática del laberinto", "h1")]
    h.append(P("2.1 Definición del modelo", "h2"))
    h.append(P(
        "El laberinto se representa mediante un grafo dirigido <i>G</i> = (<i>V</i>, <i>E</i>), donde:"))
    h += vinetas([
        "cada vértice <i>v</i> ∈ <i>V</i> corresponde a una posición o intersección del centro;",
        "cada arco (<i>u</i>, <i>v</i>) ∈ <i>E</i> corresponde a un pasillo de sentido único que solo "
        "puede recorrerse desde <i>u</i> hacia <i>v</i>;",
        "<i>s</i> ∈ <i>V</i> es la entrada y <i>t</i> ∈ <i>V</i> la salida, con <i>s</i> ≠ <i>t</i>;",
        "la longitud de un camino es su número de arcos (no se consideran distancias físicas);",
        "un pasillo bloqueado se modela retirando su arco: si <i>B</i> ⊆ <i>E</i> es el conjunto de "
        "pasillos bloqueados, los algoritmos trabajan sobre <i>G</i> − <i>B</i> = (<i>V</i>, <i>E</i> ∖ <i>B</i>).",
    ])
    h.append(P(
        "El modelo no admite lazos (<i>u</i>, <i>u</i>), arcos repetidos ni arcos recíprocos "
        "(si (<i>u</i>, <i>v</i>) ∈ <i>E</i> entonces (<i>v</i>, <i>u</i>) ∉ <i>E</i>), y ningún vértice queda aislado."))

    h.append(P("2.2 Configuración inicial", "h2"))
    V = G0.vertices
    E_ = list(G0.arcos)
    h.append(P(f"<b>V</b> = {{{', '.join(V)}}},  |<i>V</i>| = {len(V)}.", "formula"))
    h.append(P(f"<b>E</b> = {arcos_txt(E_)},  |<i>E</i>| = {len(E_)}.", "formula"))
    h.append(figura("modelo_original.png",
                    "Configuración inicial del laberinto. Cada flecha es un pasillo de sentido único; "
                    "<i>s</i> (verde) es la entrada y <i>t</i> (rojo) la salida."))
    h.append(P(
        "La red representa un centro organizado en sectores que los robots atraviesan de izquierda "
        "a derecha. Los pasillos internos (B→C, D→E y H→G) conectan intersecciones del mismo sector y "
        "generan rutas alternativas que comparten parte de su recorrido."))
    grado_sal = {v: 0 for v in V}
    grado_ent = {v: 0 for v in V}
    for u, v in E_:
        grado_sal[u] += 1
        grado_ent[v] += 1
    roles = {"s": "Entrada de los robots", "A": "Recepción norte", "B": "Recepción centro",
             "C": "Recepción sur", "D": "Almacenamiento norte", "E": "Almacenamiento centro",
             "F": "Almacenamiento sur", "G": "Despacho norte", "H": "Despacho centro",
             "I": "Despacho sur", "t": "Salida"}
    filas = [["Vértice", "Interpretación en el laberinto", "Pasillos de salida", "Grado sal.", "Grado ent."]]
    for v in V:
        sal = ", ".join(f"{v}→{w}" for (u, w) in E_ if u == v) or "—"
        filas.append([f"<b>{v}</b>", roles[v], sal, str(grado_sal[v]), str(grado_ent[v])])
    h.append(tabla(filas, [1.5, 4.4, 5.4, 1.6, 1.6],
                   "Correspondencia entre vértices, posiciones del laberinto y pasillos.",
                   alinear_centro=(0, 3, 4)))

    h.append(P("2.3 Comprobación de las restricciones", "h2"))
    filas = [["Condición exigida", "Resultado"]]
    for texto, cumple in alg.validar_modelo_completo(G0, "s", "t"):
        filas.append([texto, ok(cumple)])
    h.append(tabla(filas, [11.5, 3.0], "Restricciones de la configuración inicial "
                   "(calculadas por la función <i>validar_modelo_completo</i>)."))
    h.append(P(
        "La condición de admitir al menos dos caminos sin arcos compartidos se cumple holgadamente: "
        "por ejemplo, s → A → D → G → t y s → C → F → I → t no comparten ningún pasillo."))

    h.append(P("2.4 Formulación de los problemas", "h2"))
    h.append(P("<b>Camino mínimo.</b> La distancia de <i>s</i> a <i>t</i> es"))
    h.append(P("<i>d</i><sub>G</sub>(<i>s</i>, <i>t</i>) = mín { <i>k</i> : (<i>s</i> = <i>v</i><sub>0</sub>, "
               "<i>v</i><sub>1</sub>, …, <i>v</i><sub>k</sub> = <i>t</i>) es un camino dirigido en <i>G</i> },",
               "formula"))
    h.append(P("y no está definida (no se le asigna valor numérico) cuando no existe camino."))
    h.append(P("<b>Caminos sin arcos compartidos.</b> Se busca el máximo número λ(<i>s</i>, <i>t</i>) de "
               "caminos dirigidos de <i>s</i> a <i>t</i> que no comparten arcos (pueden compartir vértices)."))
    h.append(P("<b>Corte mínimo de pasillos.</b> Para <i>C</i> ⊆ <i>E</i>, sea <i>G</i> − <i>C</i> = "
               "(<i>V</i>, <i>E</i> ∖ <i>C</i>). Se busca"))
    h.append(P("κ′(<i>s</i>, <i>t</i>) = mín { |<i>C</i>| : <i>C</i> ⊆ <i>E</i>, no existe camino dirigido "
               "de <i>s</i> a <i>t</i> en <i>G</i> − <i>C</i> }.", "formula"))
    h.append(P("El teorema de Menger, en su versión para arcos en grafos dirigidos, afirma que "
               "λ(<i>s</i>, <i>t</i>) = κ′(<i>s</i>, <i>t</i>) (Menger, 1927; Diestel, 2017). "
               "Esta igualdad guía tanto la selección de algoritmos como la verificación."))
    return h


def investigacion():
    h = [P("3. Investigación y selección de algoritmos", "h1")]
    h.append(P("3.1 Búsqueda de caminos: BFS frente a DFS", "h2"))
    h.append(P(
        "<b>Búsqueda en anchura (BFS).</b> Parte de <i>s</i> y visita los vértices por niveles usando "
        "una cola FIFO: primero todos los vértices a distancia 1, luego los de distancia 2, etc. "
        "Para cada vértice descubierto guarda su predecesor π(<i>v</i>), lo que permite reconstruir "
        "el camino retrocediendo desde <i>t</i> (Cormen et al., 2009, §22.2)."))
    h.append(P(
        "<b>Búsqueda en profundidad (DFS).</b> Usa una pila (o recursión) y avanza tanto como puede "
        "por cada rama antes de retroceder (Cormen et al., 2009, §22.3). Encuentra un camino a "
        "<i>t</i> si existe, pero el camino depende del orden de exploración y no tiene por qué ser "
        "el más corto."))
    h.append(P(
        "<b>Otras alternativas.</b> El algoritmo de Dijkstra resuelve caminos mínimos con pesos no "
        "negativos; con todos los pesos iguales a 1 entrega el mismo resultado que BFS, pero con el "
        "costo adicional de una cola de prioridad, por lo que no aporta ventajas en este modelo."))
    filas = [["Criterio", "BFS", "DFS"],
             ["Estructura auxiliar", "Cola (FIFO)", "Pila (LIFO) o recursión"],
             ["Orden de exploración", "Por niveles de distancia a <i>s</i>", "En profundidad por ramas"],
             ["¿Encuentra un camino si existe?", "Sí", "Sí"],
             ["¿Garantiza el menor número de arcos?", "<b>Sí</b> (Teorema 22.5 de Cormen et al.)", "No"],
             ["Complejidad temporal", "O(|<i>V</i>| + |<i>E</i>|)", "O(|<i>V</i>| + |<i>E</i>|)"],
             ["Usos típicos", "Distancias en grafos no ponderados, caminos de aumento cortos",
              "Ordenamiento topológico, componentes fuertes, detección de ciclos"],
             ["Resultado en la red original", f"{cam(A0['minimo']['camino'])} (4 arcos)",
              f"{cam(DFS0['camino'])} (5 arcos)"]]
    h.append(tabla(filas, [4.6, 5.2, 5.2], "Comparación entre BFS y DFS para buscar caminos de <i>s</i> a <i>t</i>."))
    h.append(P(
        "<b>Selección y justificación.</b> Se selecciona BFS. Como los vértices se extraen de la cola en "
        "orden no decreciente de distancia, cuando un vértice <i>v</i> se descubre por primera vez "
        "desde <i>u</i> se cumple <i>d</i>(<i>s</i>, <i>v</i>) = <i>d</i>(<i>s</i>, <i>u</i>) + 1, y el "
        "camino de predecesores tiene exactamente <i>d</i>(<i>s</i>, <i>v</i>) arcos (Cormen et al., 2009, "
        "Teorema 22.5; Kleinberg y Tardos, 2006, §3.2). Por lo tanto, el primer descubrimiento de "
        "<i>t</i> entrega <i>d</i><sub>G</sub>(<i>s</i>, <i>t</i>) y un camino que la alcanza. Si <i>t</i> "
        "nunca se descubre, no hay camino y la aplicación lo informa sin asignar longitud. La tabla 3 "
        "muestra que, en la propia red del proyecto, DFS devuelve un camino de 5 arcos cuando el mínimo es 4."))

    h.append(P("3.2 Máximo número de caminos sin arcos compartidos", "h2"))
    h.append(P(
        "<b>Estrategia A: voraz repetida.</b> Buscar un camino mínimo con BFS, retirar sus arcos y repetir "
        "hasta que no quede camino. Es sencilla y produce caminos válidos sin arcos compartidos, pero "
        "<b>no garantiza el máximo</b>: una elección temprana puede bloquear dos rutas a la vez y la "
        "estrategia no puede deshacerla."))
    h.append(figura("contraejemplo.png",
                    "Contraejemplo para la estrategia voraz. El camino más corto s → a → b → t usa a→b y b→t; "
                    "al retirarlos no queda ninguna ruta. El óptimo tiene 2 caminos: s → a → d → e → t y "
                    "s → c → f → b → t.", 12.5))
    h.append(P(
        f"En la red de la figura 2 la estrategia voraz obtiene {VC['valor']} camino, mientras que el "
        f"flujo máximo obtiene {FC['valor']}. Edmonds-Karp encuentra primero el camino de aumento "
        f"{cam(FC['aumentos'][0])} y luego {cam(FC['aumentos'][1])}, que recorre el arco "
        "<b>residual b→a</b>, es decir, <i>cancela</i> el uso de a→b. Al descomponer el flujo resultante "
        f"se obtienen {cam(FC['caminos'][0])} y {cam(FC['caminos'][1])}."))
    h.append(P(
        "<b>Estrategia B: flujo máximo con capacidad unitaria.</b> Se asigna capacidad 1 a cada arco "
        "activo y se calcula un flujo máximo de <i>s</i> a <i>t</i>. Por el teorema de integralidad existe "
        "un flujo máximo con valores 0 o 1, y un flujo entero de valor <i>k</i> se descompone en <i>k</i> "
        "caminos que no comparten arcos (más, eventualmente, ciclos que se descartan); recíprocamente, "
        "<i>k</i> caminos sin arcos compartidos definen un flujo de valor <i>k</i>. Así, el flujo máximo "
        "coincide con λ(<i>s</i>, <i>t</i>) (Kleinberg y Tardos, 2006, §7.6). Para calcularlo se "
        "investigaron dos variantes del método de Ford-Fulkerson (1956):"))
    h += vinetas([
        "<b>Ford-Fulkerson con DFS:</b> busca caminos de aumento en la red residual con búsqueda en "
        "profundidad. Con capacidades unitarias realiza a lo sumo λ ≤ grado<super>+</super>(<i>s</i>) "
        "aumentos, cada uno en O(|<i>V</i>| + |<i>E</i>|).",
        "<b>Edmonds-Karp:</b> igual que el anterior, pero cada camino de aumento se busca con BFS, "
        "por lo que siempre es el más corto en la red residual. Garantiza O(|<i>V</i>|·|<i>E</i>|<super>2</super>) "
        "para capacidades arbitrarias, independientemente de los valores (Edmonds y Karp, 1972), y "
        "O(|<i>E</i>|·(|<i>V</i>| + |<i>E</i>|)) con capacidades unitarias.",
    ])
    h.append(P(
        "<b>Otras alternativas revisadas.</b> Para redes con capacidades unitarias existen algoritmos "
        "asintóticamente más rápidos, como el de Dinic (1970) y la cota O(|<i>E</i>|·mín(|<i>V</i>|<super>2/3</super>, "
        "|<i>E</i>|<super>1/2</super>)) de Even y Tarjan (1975). Con |<i>E</i>| ≤ 20 su complejidad adicional "
        "no se justifica."))
    filas = [["Estrategia", "Óptima", "Complejidad (capacidad 1)", "Observaciones"],
             ["Voraz (BFS + retirar arcos)", "No", "O(<i>k</i>·(|<i>V</i>|+|<i>E</i>|))",
              "Falla en el contraejemplo de la figura 2."],
             ["Ford-Fulkerson (DFS)", "Sí", "O(<i>k</i>·(|<i>V</i>|+|<i>E</i>|))",
              "Con capacidades grandes puede requerir muchos aumentos; los caminos dependen del orden de la DFS."],
             ["<b>Edmonds-Karp (BFS)</b>", "<b>Sí</b>", "O(<i>k</i>·(|<i>V</i>|+|<i>E</i>|)); O(|<i>V</i>||<i>E</i>|<super>2</super>) general",
              "Cota independiente de las capacidades; reutiliza BFS; resultados deterministas."],
             ["Dinic / Even-Tarjan", "Sí", "O(|<i>E</i>|·mín(|<i>V</i>|<super>2/3</super>, |<i>E</i>|<super>1/2</super>))",
              "Más complejo de implementar; ventaja solo en redes grandes."]]
    h.append(tabla(filas, [3.8, 1.6, 4.3, 5.3],
                   "Comparación de estrategias para el máximo número de caminos sin arcos compartidos "
                   "(<i>k</i> = número de caminos obtenidos)."))
    h.append(P(
        "<b>Selección.</b> Se implementa <b>Edmonds-Karp con capacidad unitaria</b>, porque garantiza "
        "el óptimo (a diferencia de la estrategia voraz), tiene una cota de tiempo independiente del "
        "orden de exploración, reutiliza la BFS ya justificada y deja al final la red residual, que "
        "entrega directamente el corte mínimo. Ford-Fulkerson con DFS y la estrategia voraz también se "
        "implementaron, pero solo para la comparación (botón «Comparar estrategias» de la aplicación)."))

    h.append(P("3.3 Relación con el corte mínimo de pasillos", "h2"))
    h.append(P(
        "<b>Desigualdad débil.</b> Si existen <i>k</i> caminos de <i>s</i> a <i>t</i> sin arcos compartidos "
        "y <i>C</i> separa <i>s</i> de <i>t</i>, entonces <i>C</i> debe contener al menos un arco de cada camino; "
        "como los caminos no comparten arcos, esos arcos son distintos y |<i>C</i>| ≥ <i>k</i>. Luego "
        "λ(<i>s</i>, <i>t</i>) ≤ κ′(<i>s</i>, <i>t</i>)."))
    h.append(P(
        "<b>Igualdad.</b> El teorema de flujo máximo y corte mínimo (Ford y Fulkerson, 1956; Cormen et al., "
        "2009, Teorema 26.6) garantiza que, al terminar el algoritmo, el conjunto <i>S</i> de vértices "
        "alcanzables desde <i>s</i> en la red residual no contiene a <i>t</i>, y que todos los arcos que "
        "van de <i>S</i> a <i>V</i> ∖ <i>S</i> están saturados. Por lo tanto,"))
    h.append(P("<i>C</i> = { (<i>u</i>, <i>v</i>) ∈ <i>E</i> activo : <i>u</i> ∈ <i>S</i>, <i>v</i> ∉ <i>S</i> } "
               "  y  |<i>C</i>| = valor del flujo = λ(<i>s</i>, <i>t</i>).", "formula"))
    h.append(P(
        "En consecuencia, si una familia de caminos y un conjunto de pasillos tienen la misma "
        "cardinalidad, la familia es máxima y el corte es mínimo. Esta comprobación se usa en la "
        "sección 6. El corte mínimo no es necesariamente único: el procedimiento entrega el que queda "
        "«más cerca» de <i>s</i>."))
    return h


def implementacion():
    h = [P("4. Implementación", "h1")]
    h.append(P("4.1 Tecnología y organización del código", "h2"))
    h.append(P(
        "La aplicación está escrita en Python. La interfaz usa "
        "<i>tkinter</i>, que viene incluido con Python, por lo que no hay dependencias externas. Los "
        "algoritmos usan solo estructuras básicas del lenguaje (<i>dict</i>, <i>list</i>, <i>set</i> y "
        "<i>collections.deque</i> como cola); no se emplea ninguna biblioteca de grafos ni de flujo. "
        "Cada función principal está documentada con su finalidad, sus parámetros y su resultado."))
    filas = [["Archivo", "Contenido"],
             ["laberinto/grafo.py", "Clase <i>Grafo</i>: vértices, pasillos activos o bloqueados, validación de "
              "lazos, arcos repetidos y recíprocos, lista de adyacencia, lectura y escritura en JSON, "
              "validación de la configuración inicial."],
             ["laberinto/algoritmos.py", "BFS (camino mínimo) y DFS (comparación); Edmonds-Karp y "
              "Ford-Fulkerson con DFS; descomposición del flujo en caminos; corte mínimo; estrategia "
              "voraz; verificaciones y corte por fuerza bruta; formato del informe de resultados."],
             ["laberinto/configuraciones.py", "Red original, modificaciones 1 y 2, caso de verificación de "
              "5 vértices y contraejemplo de la estrategia voraz."],
             ["app.py", "Interfaz gráfica interactiva."]]
    h.append(tabla(filas, [4.4, 10.6], "Estructura del proyecto."))

    h.append(P("4.2 Representación del grafo", "h2"))
    h.append(P(
        "Los pasillos se guardan en un diccionario <i>arcos</i>[(<i>u</i>, <i>v</i>)] = {activo, agregado}. "
        "Bloquear un pasillo solo cambia <i>activo</i> a falso, por lo que restablecerlo no pierde "
        "información. Antes de cada recorrido se construye la lista de adyacencia de los arcos activos. "
        "Al agregar un pasillo, la función <i>motivo_rechazo_arco</i> rechaza los lazos, los arcos "
        "repetidos y los recíprocos, considerando también los pasillos bloqueados."))

    h.append(P("4.3 Camino mínimo (BFS) y reconstrucción", "h2"))
    h.append(P("La función <i>bfs_camino_minimo</i> (archivo <i>algoritmos.py</i>) implementa la búsqueda "
               "en anchura seleccionada en la sección 3.1. Su funcionamiento se resume en el siguiente "
               "pseudocódigo:"))
    h.append(codigo("""
bfs_camino_minimo(G, s, t):
    distancia[s] <- 0 ;  padre[s] <- NULO ;  cola <- [s]
    mientras cola no vacia:
        u <- cola.extraer_frente()
        si u = t: terminar                         # d(s,t) ya quedo fijada
        para cada v sucesor de u por un pasillo ACTIVO:
            si v no tiene distancia:
                distancia[v] <- distancia[u] + 1 ;  padre[v] <- u ;  cola.agregar(v)
    camino <- reconstruir(padre, s, t)             # retrocede t, padre[t], ..., s e invierte
    si camino vacio: devolver {existe: falso, longitud: NULO}   # sin longitud numerica
    devolver {existe: verdadero, longitud: |camino| - 1, camino}
"""))
    h.append(P(
        "La cola, implementada con <i>collections.deque</i>, hace que los vértices se procesen por niveles: "
        "primero los que están a 1 arco de <i>s</i>, luego los que están a 2, y así sucesivamente. Solo se "
        "recorren los pasillos activos, por lo que los bloqueados nunca forman parte del resultado. Cada "
        "vértice se descubre una única vez y en ese momento se guardan su distancia y su predecesor "
        "(<i>padre</i>); por eso la búsqueda puede detenerse apenas se extrae <i>t</i>, pues su distancia ya "
        "es <i>d</i><sub>G</sub>(<i>s</i>, <i>t</i>). La reconstrucción recorre los predecesores desde "
        "<i>t</i> hasta <i>s</i> e invierte la lista obtenida. Si <i>t</i> nunca se descubre, la función "
        "indica que no existe camino y devuelve la longitud como NULO, de modo que no se le asigna un valor "
        "numérico. Cada vértice entra a la cola a lo sumo una vez y cada arco se revisa a lo sumo una vez, "
        "así que el tiempo es O(|<i>V</i>| + |<i>E</i>|)."))

    h.append(CondPageBreak(8.5 * cm))
    h += [P("4.4 Caminos sin arcos compartidos y corte mínimo (Edmonds-Karp)", "h2"),
          P("La función <i>max_caminos_disjuntos</i> calcula, en una sola ejecución, el "
            "número máximo de caminos, una familia que lo alcanza y un corte mínimo:"),
          codigo("""
max_caminos_disjuntos(G, s, t):
    para cada arco activo (u,v):  cap[(u,v)] <- 1 ;  cap[(v,u)] <- 0      # red residual
    repetir:
        P <- camino de s a t con cap > 0, hallado por BFS                  # camino de aumento
        si no existe P: salir
        para cada (u,v) en P:  cap[(u,v)] -= 1 ;  cap[(v,u)] += 1         # aumento en 1 unidad
    valor <- numero de aumentos
    F <- arcos originales con cap = 0                                      # arcos con flujo 1
    caminos <- descomponer(F): desde s seguir arcos de F no usados hasta t;
               si se repite un vertice, se elimina el ciclo formado
    S <- vertices alcanzables desde s con cap > 0                          # lado S del corte
    corte <- { (u,v) activo : u en S, v fuera de S }
    devolver valor, caminos, corte, S
""")]
    h.append(P(
        "Como cada arco de <i>F</i> se usa una sola vez durante la descomposición, los caminos obtenidos "
        "no comparten arcos; la eliminación de ciclos garantiza además que ningún camino repite vértices. "
        "Si no existe camino de <i>s</i> a <i>t</i>, el ciclo termina sin aumentos: el valor es 0, la familia "
        "es vacía y el corte es ∅, porque el conjunto vacío ya impide el desplazamiento."))

    h.append(P("4.5 Verificación automática incorporada", "h2"))
    h.append(P("Después de cada cálculo, la función <i>verificar</i> comprueba y muestra en pantalla que:"))
    h += vinetas([
        "el camino mínimo y todos los caminos declarados parten en <i>s</i>, terminan en <i>t</i>, no repiten "
        "vértices y solo usan pasillos <b>activos</b> en su sentido;",
        "cada vértice del camino mínimo está a la distancia BFS que corresponde a su posición;",
        "los caminos declarados independientes no comparten arcos;",
        "|familia de caminos| = |corte| = valor del flujo;",
        "en <i>G</i> − <i>C</i> no hay camino de <i>s</i> a <i>t</i> (se repite la BFS ignorando los arcos del corte);",
        "por fuerza bruta, ningún conjunto de pasillos de menor tamaño separa <i>s</i> de <i>t</i> "
        "(se recorren todas las combinaciones, lo que es posible porque la red es pequeña).",
    ])

    h.append(KeepTogether([P("4.6 Interfaz interactiva", "h2"), figura("interfaz.png",
                    "Interfaz de la aplicación (configuración Modificación 2, modo «Todo»). A la izquierda, "
                    "la red y los resultados; a la derecha, los controles.", 14.5)]))
    filas = [["Requisito", "Cómo se realiza en la aplicación"],
             ["Visualizar vértices y pasillos con dirección", "Lienzo con flechas; los vértices se pueden arrastrar."],
             ["Seleccionar entrada y salida distintas", "Listas «Entrada s» y «Salida t» o clic derecho sobre un vértice; se rechaza s = t."],
             ["Ejecutar los algoritmos", "Recálculo automático tras cada cambio o botón «Recalcular»."],
             ["Distinguir las soluciones", "Camino mínimo: franja amarilla (naranja en su modo propio). Cada camino "
              "P1, P2, … con un color distinto. Corte: arcos rojos marcados con × y, en el modo «Corte mínimo», el lado <i>S</i> en azul."],
             ["Bloquear y restablecer un pasillo", "Clic sobre la flecha, doble clic en la lista o botón; los pasillos bloqueados aparecen en gris discontinuo."],
             ["Agregar un pasillo dirigido", "Listas «Desde» y «Hacia» y botón «Agregar». Se rechazan lazos, arcos repetidos y recíprocos."],
             ["Comparar configuraciones", "Ventana con una tabla de las tres configuraciones (con los mismos <i>s</i> y <i>t</i>) y de la red actual, que puede copiarse."],
             ["Comparar estrategias", "Ventana con BFS frente a DFS y Edmonds-Karp frente a Ford-Fulkerson (DFS) y la estrategia voraz."]]
    h.append(tabla(filas, [5.0, 10.0], "Funcionalidades de la interfaz frente a los requisitos del enunciado."))

    h.append(P("4.7 Código fuente y ejecución", "h2"))
    h.append(P("El código fuente se adjunta junto a este informe en la entrega de la plataforma Educa. "
               "Incluye el archivo <i>LEEME.md</i>, con las dependencias y las instrucciones de ejecución."))
    h.append(P("Para ejecutar la aplicación solo se necesita Python con <i>tkinter</i>, que viene incluido "
               "en la instalación estándar; no se requieren paquetes adicionales. Desde la carpeta del "
               "proyecto:"))
    h.append(codigo("""
python app.py
"""))
    return h


def resultados():
    h = [P("5. Resultados de las tres configuraciones y análisis", "h1")]
    h.append(P(
        "Las tres configuraciones mantienen la entrada <i>s</i> y la salida <i>t</i>. En las figuras se "
        "usa el modo «Todo» de la aplicación: franja amarilla para el camino mínimo, un color por cada "
        "camino de la familia máxima y × en rojo para los pasillos del corte mínimo; los pasillos "
        "bloqueados se muestran en gris discontinuo con un símbolo de prohibición. Cada modificación se "
        "construye a partir de la red original: antes de aplicarla, los pasillos bloqueados en la "
        "configuración anterior se restablecen desde la interfaz (clic sobre la flecha o botón «Restablecer "
        "todos los pasillos»)."))

    def bloque_config(i, nombre, desc, a, img, extra_img=None):
        m, f = a["minimo"], a["flujo"]
        b = [P(f"5.{i} {nombre}" + ("" if nombre == "Original" else f": {desc[0].lower() + desc[1:].rstrip('.')}"), "h2")]
        b.append(figura(img, f"Resultados en la configuración «{nombre}».", 13.2))
        filas = [["Resultado", "Valor"],
                 ["¿Existe camino de s a t?", "Sí" if m["existe"] else "No"],
                 ["d<sub>G</sub>(s, t) y un camino mínimo",
                  f"{m['longitud']}:  {cam(m['camino'])}" if m["existe"] else "No definida"],
                 ["Máximo número de caminos sin arcos compartidos", str(f["valor"])]]
        for j, c in enumerate(f["caminos"], 1):
            filas.append([f"   P{j}", f"{cam(c)}  ({len(c) - 1} arcos)"])
        filas.append(["Corte mínimo C", f"{arcos_txt(f['corte'])},  |C| = {len(f['corte'])}"])
        lado = ["s"] + sorted(v for v in f["lado_s"] if v != "s")
        filas.append(["Lado S del corte", "{" + ", ".join(lado) + "}"])
        b.append(tabla(filas, [6.3, 8.7], f"Resultados de la configuración «{nombre}»."))
        if extra_img:
            b.append(figura(extra_img[0], extra_img[1], 12))
        return b

    n, d, g, a = CONFIGS[0]
    h += bloque_config(1, n, d, a, "original_todo.png")
    dist = a["minimo"]["distancias"]
    niveles = {}
    for v, k in dist.items():
        niveles.setdefault(k, []).append(v)
    filas = [["Nivel BFS (distancia a s)"] + [str(k) for k in sorted(niveles)],
             ["Vértices"] + [", ".join(niveles[k]) for k in sorted(niveles)]]
    REF["niveles"] = contador["tab"] + 1
    h.append(tabla(filas, [4.6] + [2.08] * len(niveles), "Niveles de la BFS en la red original.",
                   alinear_centro=tuple(range(1, len(niveles) + 1))))
    h.append(P(
        "<b>Análisis.</b> La BFS ubica a <i>t</i> en el nivel 4, por lo que ningún camino tiene menos de 4 "
        "pasillos. Existen varios caminos mínimos (por ejemplo, s → A → E → G → t y s → B → E → H → t "
        "también tienen 4 arcos); como permite el enunciado, se presenta uno de ellos. La red admite 3 rutas sin pasillos compartidos, una por cada sector "
        "(norte, centro y sur). Este número no puede mejorarse: <i>s</i> tiene solo 3 pasillos de salida y "
        "cada ruta usa uno distinto. El corte mínimo encontrado, {s→A, s→B, s→C}, consiste justamente en "
        "esos 3 pasillos. Otro corte mínimo es {G→t, H→t, I→t}: la red tiene dos «cuellos» de capacidad 3, "
        "en la entrada y en la salida."))

    n, d, g, a = CONFIGS[1]
    h.append(CondPageBreak(6 * cm))
    h += bloque_config(2, n, d, a, "mod1_todo.png")
    h.append(P(
        "<b>Análisis.</b> Bloquear s→C (el caso descrito en el enunciado) deja a <i>s</i> con 2 salidas, y "
        "bloquear G→t deja a <i>t</i> con 2 entradas, por lo que el máximo baja de 3 a 2 rutas "
        "independientes. El sector sur sigue siendo accesible gracias al pasillo interno B→C, aunque "
        "ahora con 5 pasillos (s → B → C → F → I → t). La distancia mínima no cambia (sigue siendo 4), "
        "porque existe la alternativa s → A → E → H → t, de igual longitud que la ruta perdida "
        "s → A → D → G → t. La red queda más vulnerable: bloquear solo 2 pasillos (s→A y s→B, o bien "
        "H→t e I→t) basta para aislar la salida."))

    n, d, g, a = CONFIGS[2]
    h.append(CondPageBreak(6 * cm))
    h += bloque_config(3, n, d, a, "mod2_todo.png",
                       ("mod2_corte.png", "Modificación 2 en el modo «Corte mínimo»: los vértices azules forman "
                        "el lado <i>S</i> (alcanzables desde <i>s</i> en la red residual) y en rojo los 2 "
                        "pasillos del corte."))
    mi, fi = A_INTER["minimo"], A_INTER["flujo"]
    h.append(P(
        "<b>Análisis.</b> Esta modificación combina bloqueos y un pasillo nuevo. Si solo se bloquearan "
        f"G→t y H→t, la salida dependería únicamente de I→t: habría {fi['valor']} ruta independiente, "
        f"la distancia subiría a {mi['longitud']} ({cam(mi['camino'])}) y el corte mínimo sería "
        f"{arcos_txt(fi['corte'])}, un único pasillo crítico. El pasillo nuevo D→t compensa los bloqueos: "
        "devuelve una segunda ruta independiente y además <b>acorta</b> el trayecto mínimo a 3 pasillos "
        "(s → A → D → t), menos que en la red original. El máximo, sin embargo, queda en 2 y no en 3: "
        "aunque <i>s</i> conserva 3 salidas, ahora el cuello está en el interior. El corte "
        "{s→A, C→F} muestra que todo lo que sale por B y por C queda encerrado en el lado <i>S</i>, salvo "
        "a través de C→F, ya que E, G y H perdieron su conexión directa con <i>t</i>."))

    h.append(CondPageBreak(8 * cm))
    h.append(P("5.4 Comparación de las configuraciones", "h2"))
    filas = [["Configuración", "Cambio", "Camino", "d(s,t)", "Máx. caminos", "Corte mínimo", "|C| = máx."]]
    for n, d, g, a in CONFIGS:
        m, f = a["minimo"], a["flujo"]
        filas.append([n, d, "Sí" if m["existe"] else "No", str(m["longitud"]) if m["existe"] else "—",
                      str(f["valor"]), arcos_txt(f["corte"]),
                      ok(len(f["corte"]) == f["valor"]).replace("Cumple", "Sí")])
    h.append(tabla(filas, [2.6, 3.9, 1.5, 1.3, 1.6, 2.8, 1.5], "Resumen comparativo (s y t fijos).",
                   alinear_centro=(2, 3, 4, 6)))
    h.append(P(
        "<b>Interpretación general.</b> Los bloqueos reducen la cantidad de rutas independientes, aunque "
        "no necesariamente alargan el camino mínimo, porque la distancia depende de que sobreviva <i>una</i> "
        "ruta corta, mientras que la robustez depende de cuántas rutas disjuntas sobreviven. Agregar un "
        "pasillo puede mejorar ambas medidas, pero el máximo de rutas está limitado por el cuello más "
        "estrecho de la red. En la configuración original ese cuello estaba en la entrada y la salida; en "
        "la modificación 2 aparece en el interior. Que en las tres configuraciones el corte tenga la misma "
        "cardinalidad que la familia de caminos confirma empíricamente el teorema de Menger."))

    h.append(P("5.5 Caso sin camino", "h2"))
    h.append(P(
        "Para comprobar el comportamiento exigido cuando la salida es inalcanzable, se bloquearon en la "
        "aplicación los tres pasillos que llegan a <i>t</i> (G→t, H→t e I→t). La aplicación indica que no "
        "existe camino, no asigna longitud, informa 0 caminos disponibles y entrega el corte ∅, porque el "
        f"conjunto vacío ya impide el desplazamiento (figura {contador['fig'] + 1})."))
    h.append(figura("sin_camino.png", "Red original con G→t, H→t e I→t bloqueados: no existe camino de "
                    "<i>s</i> a <i>t</i>.", 12))
    return h


def verificacion():
    h = [P("6. Verificación de resultados", "h1")]
    h.append(P("6.1 Caso independiente resuelto manualmente", "h2"))
    h.append(P(
        f"Se construyó una red de 5 vértices: <b>V</b> = {{{', '.join(GV.vertices)}}} y "
        f"<b>E</b> = {arcos_txt(list(GV.arcos))}, con entrada <i>s</i> y salida <i>t</i>."))
    h.append(figura("verif_limpia.png", "Caso independiente de verificación (5 vértices, 7 pasillos).", 11))
    h.append(P("<b>Camino mínimo.</b> No existe el pasillo s→t, así que todo camino tiene al menos 2 arcos. "
               "Los sucesores de <i>s</i> son a y b, y b→t existe; por lo tanto, s → b → t es un camino de 2 "
               "arcos y <i>d</i>(<i>s</i>, <i>t</i>) = 2. (s → a → … necesita al menos 3 arcos, porque a no tiene "
               "pasillo directo a t.)"))
    h.append(P("<b>Familia de caminos.</b> P1 = s → a → c → t usa {s→a, a→c, c→t} y P2 = s → b → t usa "
               "{s→b, b→t}. Los conjuntos son disjuntos, así que P1 y P2 no comparten pasillos."))
    h.append(P("<b>Conjunto de pasillos.</b> C = {s→a, s→b} contiene todos los pasillos que salen de <i>s</i>; "
               "al eliminarlos, <i>s</i> no tiene sucesores y <i>t</i> es inalcanzable."))
    h.append(P("<b>Optimalidad.</b> Por la desigualdad débil (sección 3.3), ninguna familia de caminos sin arcos "
               "compartidos puede tener más de |C| = 2 caminos, y ningún conjunto separador puede tener menos "
               "de 2 pasillos, porque existen 2 caminos sin arcos compartidos. Como ambas cantidades "
               "coinciden, la familia es máxima y el corte es mínimo."))
    mv, fv = AV["minimo"], AV["flujo"]
    filas = [["Magnitud", "Resolución manual", "Resultado del código", "¿Coincide?"],
             ["d(s,t)", "2", str(mv["longitud"]), ok(mv["longitud"] == 2).replace("Cumple", "Sí")],
             ["Camino mínimo", "s → b → t", cam(mv["camino"]), ok(mv["camino"] == ["s", "b", "t"]).replace("Cumple", "Sí")],
             ["Máx. caminos sin arcos compartidos", "2", str(fv["valor"]), ok(fv["valor"] == 2).replace("Cumple", "Sí")],
             ["Familia de caminos", "s → a → c → t ; s → b → t", " ; ".join(cam(c) for c in fv["caminos"]),
              ok(sorted(map(tuple, fv["caminos"])) == sorted([("s", "a", "c", "t"), ("s", "b", "t")])).replace("Cumple", "Sí")],
             ["Corte mínimo", "{s→a, s→b}", arcos_txt(fv["corte"]),
              ok(set(fv["corte"]) == {("s", "a"), ("s", "b")}).replace("Cumple", "Sí")]]
    h.append(tabla(filas, [4.2, 3.8, 4.4, 2.0], "Contraste entre la resolución manual y el código "
                   "en el caso independiente.", alinear_centro=(3,)))
    h.append(figura("verif_todo.png", "Resultado de la aplicación en el caso de verificación: camino mínimo "
                    "(franja amarilla), P1 y P2 (colores) y corte {s→a, s→b} (× rojas).", 11))

    h.append(P("6.2 Comprobaciones en la red principal y sus modificaciones", "h2"))
    h.append(P(
        "Para cada configuración, la función <i>verificar</i> evaluó las condiciones de la sección 4.5. "
        f"La tabla {contador['tab'] + 1} resume el resultado; todas se cumplen."))
    nombres = [n for n, _, _, _ in CONFIGS]
    textos = [t for t, _ in CONFIGS[0][3]["verificacion"]]
    filas = [["Comprobación"] + nombres]
    for i, t in enumerate(textos):
        fila = [t.replace("Los 3 caminos", "Los caminos").replace("(3 = 3)", "").replace(
            "con menos de 3 arcos", "con menos arcos que el máximo")]
        for _, _, _, a in CONFIGS:
            fila.append(ok(a["verificacion"][i][1]))
        filas.append(fila)
    filas[0] = ["Comprobación", "Original", "Modif. 1", "Modif. 2"]
    h.append(tabla(filas, [8.6, 2.1, 2.2, 2.2], "Comprobaciones automáticas sobre las tres configuraciones.",
                   alinear_centro=(1, 2, 3)))
    h.append(P("Además, la optimalidad de cada resultado puede razonarse a mano:"))
    h += vinetas([
        "<b>Original:</b> grado<super>+</super>(<i>s</i>) = 3 acota el número de rutas por 3, y se exhiben 3; "
        f"el corte {{s→A, s→B, s→C}} tiene 3 pasillos. La distancia 4 se justifica con los niveles de la tabla {REF['niveles']}.",
        "<b>Modificación 1:</b> con s→C bloqueado, <i>s</i> tiene 2 salidas activas; se exhiben 2 rutas y el "
        "corte {s→A, s→B} separa <i>s</i> de <i>t</i>.",
        "<b>Modificación 2:</b> al retirar s→A y C→F, desde <i>s</i> solo se alcanzan B, C, E, G y H "
        "(s→B, s→C, B→C, B→E, E→G, E→H, H→G), y ninguno tiene un pasillo activo hacia <i>t</i>, porque G→t y "
        "H→t están bloqueados. Con 2 rutas sin pasillos compartidos y un corte de 2 pasillos, ambos son óptimos.",
    ])
    return h


def conclusiones():
    h = [P("7. Conclusiones", "h1")]
    h += vinetas([
        "El laberinto queda modelado por un grafo dirigido de 11 vértices y 18 pasillos que cumple todas "
        "las restricciones del enunciado y admite 3 rutas sin pasillos compartidos.",
        "BFS es la estrategia adecuada para el camino mínimo en número de pasillos: garantiza la distancia "
        "mínima en tiempo lineal, mientras que DFS puede devolver caminos más largos (5 arcos frente a 4 en "
        "la red original).",
        "El máximo número de rutas sin pasillos compartidos se resuelve correctamente como un flujo máximo "
        "con capacidad unitaria. Edmonds-Karp lo calcula de forma óptima, a diferencia de la estrategia "
        "voraz, que puede quedarse corta (1 frente a 2 en el contraejemplo), porque no puede reasignar "
        "pasillos mediante la red residual.",
        "La red residual final entrega un corte mínimo cuya cardinalidad coincide con el número de rutas, "
        "lo que certifica ambos resultados (teorema de Menger y teorema de flujo máximo y corte mínimo).",
        "Las modificaciones muestran que la distancia mínima y la robustez son medidas distintas: los "
        "bloqueos redujeron las rutas independientes de 3 a 2 sin alterar la distancia, y el pasillo nuevo "
        "D→t acortó el trayecto a 3, pero no recuperó la tercera ruta, porque el cuello de la red se "
        "desplazó al interior.",
        "La aplicación permite repetir estos análisis de forma interactiva y verifica automáticamente cada "
        "resultado.",
    ])
    return h


def referencias():
    h = [P("Referencias", "h1")]
    refs = [
        "Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2009). <i>Introduction to Algorithms</i> "
        "(3.ª ed.). MIT Press. Cap. 22 (búsqueda en anchura y en profundidad) y cap. 26 (flujo máximo, "
        "Ford-Fulkerson, Edmonds-Karp y teorema de flujo máximo y corte mínimo).",
        "Diestel, R. (2017). <i>Graph Theory</i> (5.ª ed.). Springer. Cap. 3 (teorema de Menger).",
        "Dinic, E. A. (1970). Algorithm for solution of a problem of maximum flow in networks with power "
        "estimation. <i>Soviet Mathematics Doklady</i>, 11, 1277–1280.",
        "Edmonds, J. y Karp, R. M. (1972). Theoretical improvements in algorithmic efficiency for network "
        "flow problems. <i>Journal of the ACM</i>, 19(2), 248–264.",
        "Even, S. y Tarjan, R. E. (1975). Network flow and testing graph connectivity. <i>SIAM Journal on "
        "Computing</i>, 4(4), 507–518.",
        "Ford, L. R. y Fulkerson, D. R. (1956). Maximal flow through a network. <i>Canadian Journal of "
        "Mathematics</i>, 8, 399–404.",
        "Kleinberg, J. y Tardos, É. (2006). <i>Algorithm Design</i>. Pearson/Addison-Wesley. Cap. 3 "
        "(recorridos de grafos) y cap. 7 (flujo en redes; §7.6, caminos disjuntos en grafos dirigidos).",
        "Menger, K. (1927). Zur allgemeinen Kurventheorie. <i>Fundamenta Mathematicae</i>, 10, 96–115.",
        "Python Software Foundation. (2024). <i>collections — Container datatypes</i> y <i>tkinter — Python "
        "interface to Tcl/Tk</i>. Documentación oficial de Python. https://docs.python.org/",
    ]
    h += [P(r, "ref") for r in refs]
    return h


def main():
    doc = construir_documento()
    historia = []
    historia += portada()
    historia += indice()
    historia.append(PageBreak())
    historia += introduccion()
    historia.append(PageBreak())
    historia += modelo()
    historia.append(PageBreak())
    historia += investigacion()
    historia.append(PageBreak())
    historia += implementacion()
    historia.append(PageBreak())
    historia += resultados()
    historia.append(PageBreak())
    historia += verificacion()
    historia.append(CondPageBreak(9 * cm))
    historia += conclusiones()
    historia.append(PageBreak())
    historia += referencias()
    doc.multiBuild(historia)  # varias pasadas para que el índice conozca las páginas definitivas
    print("Informe generado:", SALIDA_PDF)


if __name__ == "__main__":
    main()
