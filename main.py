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