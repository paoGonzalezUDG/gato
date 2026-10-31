"""
Búsqueda con adversario: algoritmo Minimax.

Se aplica al juego del Gato (Tic-Tac-Toe):
  - MAX juega con 'X' e intenta maximizar la utilidad.
  - MIN juega con 'O' e intenta minimizarla.
Utilidad de un estado terminal: +1 si gana X, -1 si gana O, 0 si es empate.
"""

import math

VACIO = " "
LINEAS_GANADORAS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # filas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columnas
    (0, 4, 8), (2, 4, 6),             # diagonales
]


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


# ---------------------------------------------------------------------------
# Minimax
# ---------------------------------------------------------------------------

def valor_max(estado):
    """Mejor utilidad que MAX puede asegurar desde este estado."""
    if es_terminal(estado):
        return utilidad(estado)
    v = -math.inf
    for a in acciones(estado):
        v = max(v, valor_min(resultado(estado, a)))
    return v


def valor_min(estado):
    """Mejor utilidad (la menor) que MIN puede asegurar desde este estado."""
    if es_terminal(estado):
        return utilidad(estado)
    v = math.inf
    for a in acciones(estado):
        v = min(v, valor_max(resultado(estado, a)))
    return v


def minimax(estado):
    """Devuelve la acción óptima para el jugador en turno."""
    if es_terminal(estado):
        return None
    if jugador(estado) == "X":
        return max(acciones(estado), key=lambda a: valor_min(resultado(estado, a)))
    return min(acciones(estado), key=lambda a: valor_max(resultado(estado, a)))


# ---------------------------------------------------------------------------
# Interfaz por consola: humano (O) contra la computadora (X)
# ---------------------------------------------------------------------------

def imprimir(estado):
    filas = [" | ".join(estado[i:i + 3]) for i in (0, 3, 6)]
    print("\n" + "\n---------\n".join(filas) + "\n")


def jugar():
    estado = [VACIO] * 9
    print("Casillas numeradas del 1 al 9 (de izquierda a derecha, de arriba abajo).")
    while not es_terminal(estado):
        imprimir(estado)
        if jugador(estado) == "X":
            accion = minimax(estado)
            print(f"La computadora (X) juega en la casilla {accion + 1}")
        else:
            try:
                accion = int(input("Tu turno (O), elige casilla 1-9: ")) - 1
            except ValueError:
                continue
            if accion not in acciones(estado):
                print("Movimiento inválido.")
                continue
        estado = resultado(estado, accion)

    imprimir(estado)
    g = ganador(estado)
    print(f"Ganó {g}." if g else "Empate.")


if __name__ == "__main__":
    jugar()
