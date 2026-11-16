import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from abc import ABC, abstractmethod

class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.tamano = 0

    def agregar(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self.tamano += 1

    def buscar(self, identificador):
        actual = self.cabeza
        while actual is not None:
            if actual.dato.id == identificador:
                return actual.dato
            actual = actual.siguiente
        return None

    def __iter__(self):
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def __len__(self):
        return self.tamano


class ColaTurnos:
    def __init__(self):
        self.frente = None
        self.final = None
        self.tamano = 0

    def esta_vacia(self):
        return self.frente is None

    def encolar(self, turno):
        nuevo_nodo = Nodo(turno)
        if self.esta_vacia():
            self.frente = nuevo_nodo
            self.final = nuevo_nodo
        else:
            self.final.siguiente = nuevo_nodo
            self.final = nuevo_nodo
        self.tamano += 1

    def desencolar(self):
        if self.esta_vacia():
            return None
        turno = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self.tamano -= 1
        return turno

    def eliminar(self, identificador):
        anterior = None
        actual = self.frente
        while actual is not None:
            if actual.dato.id == identificador:
                if anterior is None:
                    self.frente = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                if actual == self.final:
                    self.final = anterior
                self.tamano -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def posicion(self, identificador):
        actual = self.frente
        posicion_actual = 1
        while actual is not None:
            if actual.dato.id == identificador:
                return posicion_actual
            actual = actual.siguiente
            posicion_actual += 1
        return None

    def obtener_todos(self):
        elementos = []
        actual = self.frente
        while actual is not None:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

    def __len__(self):
        return self.tamano

class Persona:
    def __init__(self, documento, nombre):
        self.documento = documento
        self.nombre = nombre


class Estudiante(Persona):
   def __init__(self, documento, nombre):
        super().__init__(documento, nombre)


class Funcionario(Persona):
    def __init__(self, documento, nombre, servicio_codigo):
        super().__init__(documento, nombre)
        self.servicio_codigo = servicio_codigo
    pass


class Servicio(ABC):
    def __init__(self, codigo, nombre, tiempo_promedio):
        self.codigo = codigo
        self.nombre = nombre
        self.tiempo_promedio = tiempo_promedio

    @abstractmethod
    def calcular_tiempo_estimado(self, personas_adelante):
        pass


class RegistroAcademico(Servicio):
    def calcular_tiempo_estimado(self, personas_adelante):
        return personas_adelante * self.tiempo_promedio

class BienestarInstitucional(Servicio):
    def calcular_tiempo_estimado(self, personas_adelante):
        tiempo = personas_adelante * self.tiempo_promedio
        if personas_adelante > 0:
            tiempo += 5
        return tiempo


class SoporteTecnologico(Servicio):
    def calcular_tiempo_estimado(self, personas_adelante):
        tiempo = personas_adelante * self.tiempo_promedio
        tiempo += (personas_adelante // 2) * 5
        return tiempo

@dataclass
class Turno:
    id: str
    estudiante_documento: str
    estudiante_nombre: str
    servicio_codigo: str
    servicio_nombre: str
    fecha_creacion: str
    estado: str = "En espera"
    funcionario_documento: Optional[str] = None
    fecha_llamado: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_finalizacion: Optional[str] = None


class SistemaTurnos:
    def __init__(self):
        self.estudiantes = {}
        self.funcionarios = {}

        self.servicios = {
            "RA": RegistroAcademico("RA", "Registro Academico", 8),
            "BI": BienestarInstitucional("BI", "Bienestar Institucional", 12),
            "ST": SoporteTecnologico("ST", "Soporte Tecnologico", 15),
        }

        self.turnos = []
        self.historial = ListaEnlazada()

        self.colas = {
            codigo: ColaTurnos()
            for codigo in self.servicios
        }

    def buscar_turno(self, identificador):
        for turno in self.turnos:
            if turno.id == identificador.upper():
                return turno

        return None

    def obtener_siguiente_id(self, codigo_servicio):
        mayor = 0

        for turno in self.turnos:
            if turno.servicio_codigo != codigo_servicio:
                continue

            try:
                numero = int(turno.id.split("-")[-1])
                mayor = max(mayor, numero)
            except ValueError:
                continue

        return f"{codigo_servicio}-{mayor + 1:04d}"


BG = "#F4F6FA"
SIDEBAR = "#17233C"
SIDEBAR_HOVER = "#243653"
PRIMARY = "#356AE6"
PRIMARY_DARK = "#2856C5"
TEXT = "#1D2939"
MUTED = "#667085"
WHITE = "#FFFFFF"
BORDER = "#E4E7EC"
GREEN = "#12A36D"
ORANGE = "#D97706"
RED = "#D92D20"


class FilaCeroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fila Cero | Gestión de turnos")
        self.root.geometry("1180x740")
        self.root.minsize(980, 640)
        self.root.configure(bg=BG)

        self.sistema = SistemaTurnos()
        self._configurar_estilos()
        self._construir_estructura()
        self.mostrar_inicio()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=WHITE,
            foreground=TEXT,
            fieldbackground=WHITE,
            rowheight=34,
            bordercolor=BORDER,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#EEF2F7",
            foreground="#344054",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(9, 10)
        )
        style.map("Treeview", background=[("selected", "#E8F0FF")],
                  foreground=[("selected", TEXT)])
        style.configure("TCombobox", padding=7, font=("Segoe UI", 10))
        style.configure("TEntry", padding=8, font=("Segoe UI", 10))

    def _construir_estructura(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=225)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=22, pady=(26, 30))
        tk.Label(brand, text="FILA CERO", bg=SIDEBAR, fg=WHITE,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(brand, text="GESTIÓN DE TURNOS", bg=SIDEBAR, fg="#AAB8CF",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(3, 0))

        nav_items = [
            ("⌂", "Inicio", self.mostrar_inicio),
            ("＋", "Registrar estudiante", self.vista_registrar_estudiante),
            ("♙", "Registrar funcionario", self.vista_registrar_funcionario),
            ("▣", "Generar turno", self.vista_generar_turno),
            ("☷", "Filas de espera", self.vista_filas),
            ("◷", "Historial", self.vista_historial),
            ("⇩", "Exportar historial", self.vista_exportar_historial),
            ("▤", "Estadísticas", self.vista_estadisticas),
        ]
        for icon, label, command in nav_items:
            btn = tk.Button(
                self.sidebar, text=f"  {icon}   {label}", command=command,
                anchor="w", bg=SIDEBAR, fg="#E6ECF5",
                activebackground=SIDEBAR_HOVER, activeforeground=WHITE,
                relief="flat", bd=0, padx=18, pady=12,
                font=("Segoe UI", 10), cursor="hand2"
            )
            btn.pack(fill="x", padx=10, pady=2)

        tk.Frame(self.sidebar, bg="#34435B", height=1).pack(
            fill="x", padx=18, pady=(22, 12)
        )
        tk.Label(self.sidebar, text="Sistema académico", bg=SIDEBAR,
                 fg="#AAB8CF", font=("Segoe UI", 9)).pack(anchor="w", padx=22)

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(self.content, bg=WHITE, height=68,
                          highlightbackground=BORDER, highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        self.page_title = tk.Label(topbar, text="Inicio", bg=WHITE, fg=TEXT,
                                   font=("Segoe UI", 16, "bold"))
        self.page_title.pack(side="left", padx=28)
        self.clock_label = tk.Label(topbar, text=datetime.now().strftime("%d/%m/%Y"),
                                    bg=WHITE, fg=MUTED, font=("Segoe UI", 9))
        self.clock_label.pack(side="right", padx=28)

        self.page = tk.Frame(self.content, bg=BG)
        self.page.pack(fill="both", expand=True, padx=28, pady=24)

    def _limpiar_pagina(self, titulo):
        for widget in self.page.winfo_children():
            widget.destroy()
        self.page_title.config(text=titulo)

    def _titulo_seccion(self, titulo, subtitulo=None):
        tk.Label(self.page, text=titulo, bg=BG, fg=TEXT,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w")
        if subtitulo:
            tk.Label(self.page, text=subtitulo, bg=BG, fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 18))
        else:
            tk.Frame(self.page, bg=BG, height=18).pack()

    def _boton(self, parent, texto, comando, color=PRIMARY, ancho=None):
        return tk.Button(
            parent, text=texto, command=comando, bg=color, fg=WHITE,
            activebackground=PRIMARY_DARK if color == PRIMARY else color,
            activeforeground=WHITE, relief="flat", bd=0, padx=16, pady=9,
            font=("Segoe UI", 9, "bold"), cursor="hand2", width=ancho
        )

    def _tarjeta(self, parent, titulo, valor, detalle, color=PRIMARY):
        card = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER,
                        highlightthickness=1, padx=18, pady=16)
        tk.Label(card, text=titulo.upper(), bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(card, text=str(valor), bg=WHITE, fg=color,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(8, 1))
        tk.Label(card, text=detalle, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")
        return card

    def _crear_tabla(self, parent, columnas, alturas=12):
        cont = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER,
                        highlightthickness=1)
        cont.pack(fill="both", expand=True)
        identificadores = [col[0] for col in columnas]
        tabla = ttk.Treeview(cont, columns=identificadores, show="headings",
                             height=alturas)
        for col, titulo, ancho in columnas:
            tabla.heading(col, text=titulo)
            tabla.column(col, width=ancho, anchor="w")
        scroll = ttk.Scrollbar(cont, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        tabla.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=8)
        return tabla

    def _servicio_opciones(self):
        return {
            f"{s.codigo} - {s.nombre}": s.codigo
            for s in self.sistema.servicios.values()
        }

    def _seleccionar_codigo(self, texto):
        return self._servicio_opciones().get(texto)

    def mostrar_inicio(self):
        self._limpiar_pagina("Inicio")
        self._titulo_seccion("Panel general",
                             "Resumen del estado actual de Fila Cero.")

        total = len(self.sistema.turnos)
        esperando = sum(t.estado == "En espera" for t in self.sistema.turnos)
        atencion = sum(t.estado == "En atencion" for t in self.sistema.turnos)
        finalizados = sum(t.estado == "Finalizado" for t in self.sistema.turnos)

        cards = tk.Frame(self.page, bg=BG)
        cards.pack(fill="x", pady=(0, 22))
        values = [
            ("Turnos registrados", total, "Total acumulado", PRIMARY),
            ("En espera", esperando, "Pendientes de atención", ORANGE),
            ("En atención", atencion, "Atención en curso", GREEN),
            ("Finalizados", finalizados, "Atenciones completadas", "#475467"),
        ]
        for i, item in enumerate(values):
            card = self._tarjeta(cards, *item)
            card.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else 8, 0))
            cards.grid_columnconfigure(i, weight=1)

        tk.Label(self.page, text="Turnos recientes", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 10))
        tabla = self._crear_tabla(self.page, [
            ("id", "Turno", 110), ("nombre", "Estudiante", 210),
            ("servicio", "Dependencia", 220), ("estado", "Estado", 130),
            ("fecha", "Fecha de creación", 170)
        ], 8)
        for turno in reversed(self.sistema.turnos[-8:]):
            tabla.insert("", "end", values=(
                turno.id, turno.estudiante_nombre, turno.servicio_nombre,
                turno.estado, turno.fecha_creacion.replace("T", " ")
            ))

    def _formulario(self, titulo, subtitulo):
        self._limpiar_pagina(titulo)
        self._titulo_seccion(titulo, subtitulo)
        panel = tk.Frame(self.page, bg=WHITE, highlightbackground=BORDER,
                         highlightthickness=1, padx=24, pady=22)
        panel.pack(fill="x", anchor="n")
        return panel

    def _campo(self, parent, etiqueta, fila, variable=None, ancho=42):
        tk.Label(parent, text=etiqueta, bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).grid(
            row=fila, column=0, sticky="w", pady=(10, 5)
        )
        entrada = ttk.Entry(parent, textvariable=variable, width=ancho)
        entrada.grid(row=fila + 1, column=0, sticky="ew", pady=(0, 8))
        parent.grid_columnconfigure(0, weight=1)
        return entrada

    def vista_registrar_estudiante(self):
        panel = self._formulario("Registrar estudiante",
                                 "Agrega un estudiante al sistema.")
        doc = tk.StringVar()
        nombre = tk.StringVar()
        e1 = self._campo(panel, "Documento", 0, doc)
        self._campo(panel, "Nombre completo", 2, nombre)

        def guardar():
            documento, nom = doc.get().strip(), nombre.get().strip()
            if not documento or not nom:
                messagebox.showwarning("Campos obligatorios",
                                       "Completa el documento y el nombre.")
                return
            if documento in self.sistema.estudiantes or documento in self.sistema.funcionarios:
                messagebox.showerror("Documento existente",
                                     "Ya existe una persona con ese documento.")
                return
            self.sistema.estudiantes[documento] = Estudiante(documento, nom)
            messagebox.showinfo("Registro exitoso",
                                f"Estudiante {nom} registrado correctamente.")
            self.mostrar_inicio()

        self._boton(panel, "Guardar estudiante", guardar).grid(
            row=5, column=0, sticky="w", pady=(16, 0)
        )
        e1.focus_set()

    def vista_registrar_funcionario(self):
        panel = self._formulario("Registrar funcionario",
                                 "Registra al funcionario y asígnalo a una dependencia.")
        doc, nombre, servicio = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self._campo(panel, "Documento", 0, doc)
        self._campo(panel, "Nombre completo", 2, nombre)
        tk.Label(panel, text="Dependencia", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).grid(row=4, column=0, sticky="w",
                                                     pady=(10, 5))
        combo = ttk.Combobox(panel, textvariable=servicio, state="readonly",
                             values=list(self._servicio_opciones().keys()), width=40)
        combo.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        if combo["values"]:
            combo.current(0)

        def guardar():
            documento, nom = doc.get().strip(), nombre.get().strip()
            codigo = self._seleccionar_codigo(servicio.get())
            if not documento or not nom or not codigo:
                messagebox.showwarning("Campos obligatorios",
                                       "Completa todos los campos.")
                return
            if documento in self.sistema.estudiantes or documento in self.sistema.funcionarios:
                messagebox.showerror("Documento existente",
                                     "Ya existe una persona con ese documento.")
                return
            self.sistema.funcionarios[documento] = Funcionario(documento, nom, codigo)
            messagebox.showinfo("Registro exitoso", "Funcionario registrado correctamente.")
            self.mostrar_inicio()

        self._boton(panel, "Guardar funcionario", guardar).grid(
            row=6, column=0, sticky="w", pady=(16, 0)
        )

    def vista_generar_turno(self):
        panel = self._formulario("Generar turno",
                                 "Selecciona un estudiante registrado y la dependencia que necesita.")
        documento, servicio = tk.StringVar(), tk.StringVar()
        self._campo(panel, "Documento del estudiante", 0, documento)
        tk.Label(panel, text="Dependencia", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w",
                                                    pady=(10, 5))
        combo = ttk.Combobox(panel, textvariable=servicio, state="readonly",
                             values=list(self._servicio_opciones().keys()), width=40)
        combo.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        if combo["values"]:
            combo.current(0)

        def generar():
            estudiante = self.sistema.estudiantes.get(documento.get().strip())
            codigo = self._seleccionar_codigo(servicio.get())
            if estudiante is None:
                messagebox.showerror("Estudiante no encontrado",
                                     "No hay un estudiante registrado con ese documento.")
                return
            if not codigo:
                messagebox.showwarning("Dependencia", "Selecciona una dependencia.")
                return
            serv = self.sistema.servicios[codigo]
            identificador = self.sistema.obtener_siguiente_id(codigo)
            turno = Turno(
                id=identificador,
                estudiante_documento=estudiante.documento,
                estudiante_nombre=estudiante.nombre,
                servicio_codigo=codigo,
                servicio_nombre=serv.nombre,
                fecha_creacion=datetime.now().isoformat(timespec="seconds")
            )
            self.sistema.turnos.append(turno)
            self.sistema.historial.agregar(turno)
            self.sistema.colas[codigo].encolar(turno)
            posicion = len(self.sistema.colas[codigo])
            espera = serv.calcular_tiempo_estimado(posicion - 1)
            messagebox.showinfo(
                "Turno generado",
                f"Turno: {turno.id}\nEstudiante: {estudiante.nombre}\n"
                f"Dependencia: {serv.nombre}\nPosición: {posicion}\n"
                f"Espera estimada: {espera} minutos"
            )
            self.mostrar_inicio()

        self._boton(panel, "Generar turno", generar).grid(
            row=4, column=0, sticky="w", pady=(16, 0)
        )

    def vista_filas(self):
        self._limpiar_pagina("Filas de espera")
        self._titulo_seccion("Filas de espera", "Turnos pendientes organizados por dependencia (FIFO).")

        for codigo, servicio in self.sistema.servicios.items():
            pendientes = self.sistema.colas[codigo].obtener_todos()

            bloque = tk.Frame(
                self.page,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1,
                padx=15,
                pady=12
            )
            bloque.pack(fill="x", pady=(0, 12))

            encabezado = tk.Frame(bloque, bg=WHITE)
            encabezado.pack(fill="x")

            tk.Label(
                encabezado,
                text=servicio.nombre,
                bg=WHITE,
                fg=TEXT,
                font=("Segoe UI", 11, "bold")
            ).pack(side="left")

            tk.Label(
                encabezado,
                text=f"{len(pendientes)} en espera",
                bg=WHITE,
                fg=ORANGE,
                font=("Segoe UI", 9, "bold")
            ).pack(side="right")

            if pendientes:
                for pos, turno in enumerate(pendientes, start=1):
                    espera = servicio.calcular_tiempo_estimado(pos - 1)

                    tk.Label(
                        bloque,
                        text=(
                            f"{pos}. {turno.id} · "
                            f"{turno.estudiante_nombre} · "
                            f"Espera estimada: {espera} min"
                        ),
                        bg=WHITE,
                        fg=MUTED,
                        font=("Segoe UI", 9)
                    ).pack(anchor="w", pady=3)
            else:
                tk.Label(
                    bloque,
                    text="No hay turnos pendientes.",
                    bg=WHITE,
                    fg=MUTED,
                    font=("Segoe UI", 9)
                ).pack(anchor="w", pady=(9, 0))

        acciones = tk.Frame(self.page, bg=BG)
        acciones.pack(fill="x", pady=5)

        self._boton(
            acciones,
            "Llamar siguiente",
            self.ventana_llamar
        ).pack(side="left")

        self._boton(
            acciones,
            "Iniciar atención",
            self.ventana_iniciar_atencion
        ).pack(side="left", padx=8)

        self._boton(
            acciones,
            "Finalizar atención",
            self.ventana_finalizar_atencion
        ).pack(side="left", padx=8)

        self._boton(
            acciones,
            "Cancelar turno",
            self.ventana_cancelar,
            RED
        ).pack(side="left", padx=8)


    def ventana_iniciar_atencion(self):

        def ejecutar(codigo):

            turno = next(
                (
                    t for t in self.sistema.turnos
                    if t.servicio_codigo == codigo
                    and t.estado == "Llamado"
                ),
                None
            )

            if turno is None:
                messagebox.showinfo(
                    "Sin turnos llamados",
                    "No hay ningún turno llamado para iniciar la atención."
                )
                return

            turno.estado = "En atencion"
            turno.fecha_inicio = datetime.now().isoformat(
                timespec="seconds"
            )

            messagebox.showinfo(
                "Atención iniciada",
                f"Se inició la atención del turno {turno.id}.\n"
                f"Estudiante: {turno.estudiante_nombre}"
            )

            self.vista_filas()

        self._selector_servicio_dialogo(
            "Iniciar atención",
            ejecutar
        )


    def ventana_finalizar_atencion(self):

        def ejecutar(codigo):

            turno = next(
                (
                    t for t in self.sistema.turnos
                    if t.servicio_codigo == codigo
                    and t.estado == "En atencion"
                ),
                None
            )

            if turno is None:
                messagebox.showinfo(
                    "Sin atención activa",
                    "No hay ningún turno en atención en esta dependencia."
                )
                return

            turno.estado = "Finalizado"
            turno.fecha_finalizacion = datetime.now().isoformat(
                timespec="seconds"
            )

            messagebox.showinfo(
                "Atención finalizada",
                f"El turno {turno.id} ha sido finalizado correctamente."
            )

            self.vista_filas()

        self._selector_servicio_dialogo(
            "Finalizar atención",
            ejecutar
        )

    def _selector_servicio_dialogo(self, titulo, callback):
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry("420x190")
        ventana.resizable(False, False)
        ventana.configure(bg=WHITE)
        ventana.transient(self.root)
        ventana.grab_set()
        tk.Label(ventana, text=titulo, bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=22, pady=(20, 12))
        var = tk.StringVar()
        combo = ttk.Combobox(ventana, textvariable=var, state="readonly",
                             values=list(self._servicio_opciones().keys()), width=42)
        combo.pack(padx=22, fill="x")
        if combo["values"]:
            combo.current(0)

        def aceptar():
            codigo = self._seleccionar_codigo(var.get())
            if not codigo:
                messagebox.showwarning("Dependencia", "Selecciona una dependencia.",
                                       parent=ventana)
                return
            ventana.destroy()
            callback(codigo)

        self._boton(ventana, "Continuar", aceptar).pack(anchor="e", padx=22, pady=18)

    def ventana_llamar(self):
        def ejecutar(codigo):
            servicio = self.sistema.servicios[codigo]
            activo = next((t for t in self.sistema.turnos
                           if t.servicio_codigo == codigo
                           and t.estado in ("Llamado", "En atencion")), None)
            if activo:
                messagebox.showwarning("Turno activo",
                                       "Ya existe un turno llamado o en atención en esta dependencia.")
                return
            turno = self.sistema.colas[codigo].desencolar()
            if turno is None:
                messagebox.showinfo("Fila vacía", "No hay turnos pendientes en esta dependencia.")
                return
            turno.estado = "Llamado"
            turno.fecha_llamado = datetime.now().isoformat(timespec="seconds")
            messagebox.showinfo("Turno llamado",
                                f"Turno: {turno.id}\nEstudiante: {turno.estudiante_nombre}\n"
                                f"Dependencia: {servicio.nombre}")
            self.vista_filas()
        self._selector_servicio_dialogo("Llamar siguiente turno", ejecutar)

    def ventana_cancelar(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Cancelar turno")
        ventana.geometry("390x170")
        ventana.configure(bg=WHITE)
        ventana.transient(self.root)
        ventana.grab_set()
        tk.Label(ventana, text="Número del turno", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=22, pady=(20, 6))
        var = tk.StringVar()
        ttk.Entry(ventana, textvariable=var, width=35).pack(padx=22, fill="x")

        def cancelar():
            turno = self.sistema.buscar_turno(var.get().strip().upper())
            if turno is None:
                messagebox.showerror("No encontrado", "El turno indicado no existe.", parent=ventana)
                return
            if turno.estado != "En espera":
                messagebox.showwarning("No permitido",
                                       "Solo se pueden cancelar turnos que estén en espera.",
                                       parent=ventana)
                return
            self.sistema.colas[turno.servicio_codigo].eliminar(turno.id)
            turno.estado = "Cancelado"
            ventana.destroy()
            messagebox.showinfo("Turno cancelado", f"El turno {turno.id} fue cancelado.")
            self.vista_filas()

        self._boton(ventana, "Confirmar cancelación", cancelar, RED).pack(
            anchor="e", padx=22, pady=16
        )

    def vista_historial(self):
        self._limpiar_pagina("Historial")
        self._titulo_seccion("Historial de turnos",
                             "Consulta todos los turnos registrados y su estado.")
        filtros = tk.Frame(self.page, bg=BG)
        filtros.pack(fill="x", pady=(0, 12))
        filtro = tk.StringVar(value="Todos")
        opciones = ["Todos"] + list(self._servicio_opciones().keys())
        combo = ttk.Combobox(filtros, textvariable=filtro, values=opciones,
                             state="readonly", width=35)
        combo.pack(side="left")

        tabla = self._crear_tabla(self.page, [
            ("id", "Turno", 100), ("estudiante", "Estudiante", 190),
            ("servicio", "Dependencia", 190), ("estado", "Estado", 120),
            ("creacion", "Creación", 165), ("funcionario", "Funcionario", 120)
        ], 14)

        def cargar(*_):
            tabla.delete(*tabla.get_children())
            codigo = self._seleccionar_codigo(filtro.get()) if filtro.get() != "Todos" else None
            for turno in self.sistema.turnos:
                if codigo and turno.servicio_codigo != codigo:
                    continue
                tabla.insert("", "end", values=(
                    turno.id, turno.estudiante_nombre, turno.servicio_nombre,
                    turno.estado, turno.fecha_creacion.replace("T", " "),
                    turno.funcionario_documento or "—"
                ))
        combo.bind("<<ComboboxSelected>>", cargar)
        cargar()

    def vista_exportar_historial(self):
        panel = self._formulario(
            "Descargar historial de un usuario",
            "Busca un estudiante por su número de documento y exporta todos sus turnos a un archivo CSV."
        )

        documento = tk.StringVar()
        entrada = self._campo(panel, "Documento del estudiante", 0, documento)

        tk.Label(
            panel,
            text="El archivo incluirá el número de turno, estudiante, dependencia, "
                 "estado y fechas de cada atención.",
            bg=WHITE, fg=MUTED, justify="left", wraplength=650,
            font=("Segoe UI", 9)
        ).grid(row=2, column=0, sticky="w", pady=(8, 12))

        def exportar():
            doc = documento.get().strip()
            if not doc:
                messagebox.showwarning(
                    "Documento requerido",
                    "Escribe el documento del estudiante."
                )
                return

            estudiante = self.sistema.estudiantes.get(doc)
            if estudiante is None:
                messagebox.showerror(
                    "Usuario no encontrado",
                    "No existe un estudiante registrado con ese documento."
                )
                return

            turnos_usuario = [
                turno for turno in self.sistema.turnos
                if turno.estudiante_documento == doc
            ]

            if not turnos_usuario:
                messagebox.showinfo(
                    "Sin historial",
                    f"{estudiante.nombre} no tiene turnos registrados."
                )
                return

            ruta = filedialog.asksaveasfilename(
                title="Guardar historial de turnos",
                initialfile=f"historial_{doc}.csv",
                defaultextension=".csv",
                filetypes=[("Archivo CSV", "*.csv")]
            )
            if not ruta:
                return

            columnas = [
                "turno",
                "documento_estudiante",
                "nombre_estudiante",
                "codigo_servicio",
                "dependencia",
                "estado",
                "fecha_creacion",
                "fecha_llamado",
                "fecha_inicio",
                "fecha_finalizacion",
                "documento_funcionario"
            ]

            try:
                with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                    escritor = csv.DictWriter(archivo, fieldnames=columnas)
                    escritor.writeheader()

                    for turno in turnos_usuario:
                        escritor.writerow({
                            "turno": turno.id,
                            "documento_estudiante": turno.estudiante_documento,
                            "nombre_estudiante": turno.estudiante_nombre,
                            "codigo_servicio": turno.servicio_codigo,
                            "dependencia": turno.servicio_nombre,
                            "estado": turno.estado,
                            "fecha_creacion": turno.fecha_creacion or "",
                            "fecha_llamado": turno.fecha_llamado or "",
                            "fecha_inicio": turno.fecha_inicio or "",
                            "fecha_finalizacion": turno.fecha_finalizacion or "",
                            "documento_funcionario": turno.funcionario_documento or ""
                        })

                messagebox.showinfo(
                    "Exportación exitosa",
                    f"Se exportaron {len(turnos_usuario)} turnos de "
                    f"{estudiante.nombre}.\\n\\nArchivo guardado en:\\n{ruta}"
                )
            except OSError as error:
                messagebox.showerror(
                    "Error al guardar",
                    f"No fue posible crear el archivo.\\n{error}"
                )

        self._boton(panel, "Descargar historial CSV", exportar).grid(
            row=3, column=0, sticky="w", pady=(8, 0)
        )
        entrada.focus_set()

    def vista_estadisticas(self):
        self._limpiar_pagina("Estadísticas")
        self._titulo_seccion("Estadísticas",
                             "Indicadores calculados a partir del historial de turnos.")
        estados = ["En espera", "Llamado", "En atencion", "Finalizado", "Cancelado"]
        total = len(self.sistema.turnos)
        resumen = tk.Frame(self.page, bg=BG)
        resumen.pack(fill="x", pady=(0, 20))
        for i, estado in enumerate(estados):
            cantidad = sum(t.estado == estado for t in self.sistema.turnos)
            self._tarjeta(resumen, estado, cantidad, "Turnos", PRIMARY if i == 0 else GREEN if i == 3 else MUTED).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 0)
            )
            resumen.grid_columnconfigure(i, weight=1)

        tk.Label(self.page, text="Turnos por dependencia", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 10))
        tabla = self._crear_tabla(self.page, [
            ("codigo", "Código", 100), ("servicio", "Dependencia", 280),
            ("cantidad", "Turnos registrados", 180),
            ("espera", "Actualmente en espera", 180)
        ], 8)
        for codigo, servicio in self.sistema.servicios.items():
            cantidad = sum(t.servicio_codigo == codigo for t in self.sistema.turnos)
            en_espera = len(self.sistema.colas[codigo])
            tabla.insert("", "end", values=(codigo, servicio.nombre, cantidad, en_espera))

        tk.Label(self.page, text=f"Total general: {total} turnos",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=12)
        
def iniciar_app():
    root = tk.Tk()
    FilaCeroApp(root)
    root.mainloop()

if __name__ == "__main__":
    iniciar_app() 

