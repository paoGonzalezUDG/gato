"""
Búsqueda con adversario: algoritmo Minimax con profundidad limitada.

Se aplica al juego del Gato (Tic-Tac-Toe):
  - MAX juega con 'X' e intenta maximizar la utilidad.
  - MIN juega con 'O' e intenta minimizarla.
Utilidad de un estado terminal: +1 si gana X, -1 si gana O, 0 si es empate.

El número de niveles (profundidad) que explora minimax se puede limitar.
Al llegar al límite, el estado se evalúa con una heurística en lugar de
seguir buscando. Así se obtienen los niveles de dificultad del juego.
"""

import math
import random

VACIO = " "
LINEAS_GANADORAS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # filas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columnas
    (0, 4, 8), (2, 4, 6),             # diagonales
]

# Nivel de juego -> (nombre, profundidad máxima que explora minimax)
NIVELES = {
    "1": ("Fácil", 1),
    "2": ("Difícil", 3),
    "3": ("Imposible", math.inf),
}

# Contador de nodos visitados en la última búsqueda
nodos_visitados = 0


# ---------------------------------------------------------------------------
# Definición del juego
# ---------------------------------------------------------------------------

def jugador(estado):
    """Devuelve a quién le toca mover: X empieza siempre."""
    x = estado.count("X")
    o = estado.count("O")
    return "X" if x == o else "O"


def acciones(estado):
    """Lista de casillas libres (movimientos legales)."""
    return [i for i, c in enumerate(estado) if c == VACIO]


def resultado(estado, accion):
    """Estado resultante de aplicar la acción (no modifica el original)."""
    nuevo = list(estado)
    nuevo[accion] = jugador(estado)
    return nuevo


def ganador(estado):
    for a, b, c in LINEAS_GANADORAS:
        if estado[a] != VACIO and estado[a] == estado[b] == estado[c]:
            return estado[a]
    return None


def es_terminal(estado):
    return ganador(estado) is not None or VACIO not in estado


def utilidad(estado):
    g = ganador(estado)
    if g == "X":
        return 1
    if g == "O":
        return -1
    return 0


def evaluar(estado):
    """
    Función de evaluación para estados donde se corta la búsqueda.
    Cuenta las líneas que cada jugador todavía puede completar (sin fichas
    del rival). Se divide entre 10 para que siempre valga menos que ganar.
    """
    if es_terminal(estado):
        return utilidad(estado)
    abiertas_x = abiertas_o = 0
    for linea in LINEAS_GANADORAS:
        fichas = [estado[i] for i in linea]
        if "O" not in fichas:
            abiertas_x += 1
        if "X" not in fichas:
            abiertas_o += 1
    return (abiertas_x - abiertas_o) / 10


# ---------------------------------------------------------------------------
# Minimax con límite de profundidad
# ---------------------------------------------------------------------------

def valor_max(estado, profundidad=math.inf):
    """Mejor utilidad que MAX puede asegurar mirando `profundidad` niveles."""
    global nodos_visitados
    nodos_visitados += 1
    if es_terminal(estado) or profundidad == 0:
        return evaluar(estado)
    v = -math.inf
    for a in acciones(estado):
        v = max(v, valor_min(resultado(estado, a), profundidad - 1))
    return v


def valor_min(estado, profundidad=math.inf):
    """Mejor utilidad (la menor) que MIN puede asegurar mirando `profundidad` niveles."""
    global nodos_visitados
    nodos_visitados += 1
    if es_terminal(estado) or profundidad == 0:
        return evaluar(estado)
    v = math.inf
    for a in acciones(estado):
        v = min(v, valor_max(resultado(estado, a), profundidad - 1))
    return v


def minimax(estado, profundidad=math.inf):
    """
    Devuelve la acción óptima para el jugador en turno explorando como
    máximo `profundidad` niveles (math.inf = búsqueda completa).
    Las acciones se barajan para que, entre jugadas igual de buenas,
    no elija siempre la misma.
    """
    global nodos_visitados
    nodos_visitados = 0
    if es_terminal(estado):
        return None
    opciones = acciones(estado)
    random.shuffle(opciones)
    if jugador(estado) == "X":
        return max(opciones, key=lambda a: valor_min(resultado(estado, a), profundidad - 1))
    return min(opciones, key=lambda a: valor_max(resultado(estado, a), profundidad - 1))


# ---------------------------------------------------------------------------
# Interfaz por consola: humano contra la computadora
# ---------------------------------------------------------------------------

def leer(mensaje):
    """input() sin espacios ni el BOM que agrega PowerShell al usar tuberías."""
    return input(mensaje).replace("﻿", "").strip()


def imprimir(estado):
    """Muestra el tablero; las casillas libres llevan su número (1-9)."""
    celdas = [c if c != VACIO else str(i + 1) for i, c in enumerate(estado)]
    filas = [" | ".join(celdas[i:i + 3]) for i in (0, 3, 6)]
    print("\n" + "\n---------\n".join(filas) + "\n")


def elegir_nivel():
    print("Niveles de juego:")
    for clave, (nombre, profundidad) in NIVELES.items():
        niveles = "todos" if profundidad == math.inf else profundidad
        print(f"  {clave}. {nombre} (niveles explorados: {niveles})")
    while True:
        opcion = leer("Elige el nivel (1-3): ")
        if opcion in NIVELES:
            return NIVELES[opcion]
        print("Opción inválida.")


def elegir_quien_inicia():
    """Devuelve la ficha de la computadora. Quien inicia juega con X."""
    print("\n¿Quién inicia? (quien inicia juega con X)")
    print("  1. La computadora")
    print("  2. Yo")
    while True:
        opcion = leer("Elige quién inicia (1-2): ")
        if opcion == "1":
            return "X"
        if opcion == "2":
            return "O"
        print("Opción inválida.")


def jugar():
    nombre, profundidad = elegir_nivel()
    compu = elegir_quien_inicia()
    humano = "O" if compu == "X" else "X"
    print(f"\nNivel: {nombre}")
    print(f"La computadora juega con {compu} y tú con {humano}.")
    estado = [VACIO] * 9
    print(f"Escribe el número de una casilla libre para colocar tu {humano}.")
    while not es_terminal(estado):
        imprimir(estado)
        if jugador(estado) == compu:
            print("La computadora está pensando...")
            accion = minimax(estado, profundidad)
            print(f"La computadora ({compu}) juega en la casilla {accion + 1} "
                  f"({nodos_visitados} nodos visitados)")
        else:
            entrada = leer(f"Tu turno ({humano}), elige casilla 1-9: ")
            if not entrada.isdecimal() or not 1 <= int(entrada) <= 9:
                print("Entrada inválida: escribe un número del 1 al 9.")
                continue
            accion = int(entrada) - 1
            if accion not in acciones(estado):
                print("Esa casilla ya está ocupada, elige otra.")
                continue
        estado = resultado(estado, accion)

    imprimir(estado)
    g = ganador(estado)
    if g == compu:
        print(f"Ganó la computadora ({compu}).")
    elif g == humano:
        print(f"¡Ganaste ({humano})!")
    else:
        print("Empate.")


if __name__ == "__main__":
    try:
        while True:
            jugar()
            if leer("\n¿Jugar otra vez? (s/n): ").lower() != "s":
                break
            print()
    except (KeyboardInterrupt, EOFError):
        print("\nPartida cancelada.")
