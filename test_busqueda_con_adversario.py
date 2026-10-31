"""
Pruebas de busqueda_con_adversario.py

Ejecutar con:  python -m unittest -v test_busqueda_con_adversario
"""

import os
import random
import subprocess
import sys
import unittest

import busqueda_con_adversario as juego
from busqueda_con_adversario import VACIO

ARCHIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "busqueda_con_adversario.py")
FACIL, DIFICIL, IMPOSIBLE = (juego.NIVELES[k][1] for k in ("1", "2", "3"))

# Respuestas a "¿Quién inicia?"
INICIA_COMPU, INICIA_HUMANO = "1", "2"


def tablero(texto):
    """'XX OO    ' -> lista de 9 casillas (un punto también cuenta como vacío)."""
    return [VACIO if c == "." else c for c in texto]


def peor_resultado(estado, profundidad, compu="X"):
    """
    Recorre TODAS las respuestas posibles del humano mientras la computadora
    (ficha `compu`) juega con minimax. Devuelve el peor resultado que obtuvo
    la computadora: 1 ganó, 0 empate, -1 perdió.
    """
    if juego.es_terminal(estado):
        return juego.utilidad(estado) * (1 if compu == "X" else -1)
    if juego.jugador(estado) == compu:
        accion = juego.minimax(estado, profundidad)
        return peor_resultado(juego.resultado(estado, accion), profundidad, compu)
    return min(peor_resultado(juego.resultado(estado, a), profundidad, compu)
               for a in juego.acciones(estado))


class PruebasReglas(unittest.TestCase):

    def test_turnos_alternan_empezando_por_x(self):
        self.assertEqual(juego.jugador([VACIO] * 9), "X")
        self.assertEqual(juego.jugador(tablero("X        ")), "O")
        self.assertEqual(juego.jugador(tablero("XO       ")), "X")

    def test_acciones_son_casillas_libres(self):
        self.assertEqual(juego.acciones([VACIO] * 9), list(range(9)))
        self.assertEqual(juego.acciones(tablero("XOX OXO X")), [3, 7])
        self.assertEqual(juego.acciones(tablero("XOXXOOOXX")), [])

    def test_resultado_no_modifica_el_original(self):
        original = [VACIO] * 9
        nuevo = juego.resultado(original, 4)
        self.assertEqual(original, [VACIO] * 9)
        self.assertEqual(nuevo[4], "X")

    def test_detecta_las_8_lineas_para_ambos_jugadores(self):
        for linea in juego.LINEAS_GANADORAS:
            for ficha in "XO":
                estado = [VACIO] * 9
                for i in linea:
                    estado[i] = ficha
                self.assertEqual(juego.ganador(estado), ficha, linea)
                self.assertTrue(juego.es_terminal(estado))

    def test_tablero_vacio_y_empate(self):
        self.assertIsNone(juego.ganador([VACIO] * 9))
        self.assertFalse(juego.es_terminal([VACIO] * 9))
        empate = tablero("XOXXOOOXX")
        self.assertIsNone(juego.ganador(empate))
        self.assertTrue(juego.es_terminal(empate))
        self.assertEqual(juego.utilidad(empate), 0)

    def test_victoria_con_tablero_lleno_no_es_empate(self):
        self.assertEqual(juego.ganador(tablero("XOXOXOXOX")), "X")

    def test_utilidad(self):
        self.assertEqual(juego.utilidad(tablero("XXXOO    ")), 1)
        self.assertEqual(juego.utilidad(tablero("OOOXX X  ")), -1)


class PruebasMinimax(unittest.TestCase):

    def setUp(self):
        random.seed(0)

    def test_estado_terminal_no_tiene_jugada(self):
        self.assertIsNone(juego.minimax(tablero("XXXOO    ")))
        self.assertIsNone(juego.minimax(tablero("XOXXOOOXX")))

    def test_gato_perfecto_termina_en_empate(self):
        self.assertEqual(juego.valor_max([VACIO] * 9), 0)

    def test_todos_los_niveles_ganan_si_pueden(self):
        for profundidad in (FACIL, DIFICIL, IMPOSIBLE):
            # Con X y con O.
            self.assertEqual(juego.minimax(tablero("XX.OO...."), profundidad), 2)
            self.assertEqual(juego.minimax(tablero("XX.OO.X.."), profundidad), 5)

    def test_dificil_e_imposible_bloquean(self):
        for profundidad in (DIFICIL, IMPOSIBLE):
            # X bloquea la amenaza de O en 3-4-5.
            self.assertEqual(juego.minimax(tablero("X..OO...X"), profundidad), 5)
            # O bloquea la amenaza de X en 0-1-2.
            self.assertEqual(juego.minimax(tablero("XX..O...."), profundidad), 2)

    def test_profundidad_limita_los_nodos_visitados(self):
        juego.minimax([VACIO] * 9, FACIL)
        self.assertEqual(juego.nodos_visitados, 9)
        juego.minimax([VACIO] * 9, DIFICIL)
        self.assertEqual(juego.nodos_visitados, 9 + 9 * 8 + 9 * 8 * 7)
        juego.minimax([VACIO] * 9, IMPOSIBLE)
        self.assertEqual(juego.nodos_visitados, 549945)

    def test_evaluacion_nunca_iguala_una_victoria(self):
        for _ in range(500):
            estado = [VACIO] * 9
            while not juego.es_terminal(estado):
                estado = juego.resultado(estado, random.choice(juego.acciones(estado)))
                if not juego.es_terminal(estado):
                    self.assertLess(abs(juego.evaluar(estado)), 1)

    def test_imposible_nunca_pierde(self):
        for compu in "XO":
            with self.subTest(computadora=compu):
                self.assertGreaterEqual(peor_resultado([VACIO] * 9, IMPOSIBLE, compu), 0)

    def test_dificil_nunca_pierde_si_inicia(self):
        self.assertGreaterEqual(peor_resultado([VACIO] * 9, DIFICIL, "X"), 0)

    def test_dificil_se_le_puede_ganar_si_juega_segundo(self):
        # Efecto horizonte: X1, O5, X6, O7, X3 deja dos amenazas a la vez
        # (1-2-3 y 3-6-9) y eso ocurre a más de 3 niveles de distancia.
        self.assertEqual(peor_resultado([VACIO] * 9, DIFICIL, "O"), -1)

    def test_facil_se_le_puede_ganar(self):
        for compu in "XO":
            with self.subTest(computadora=compu):
                self.assertEqual(peor_resultado([VACIO] * 9, FACIL, compu), -1)


class PruebasConsola(unittest.TestCase):
    """Ejecuta el programa real simulando lo que escribe el usuario."""

    def ejecutar(self, entradas):
        proceso = subprocess.run(
            [sys.executable, ARCHIVO],
            input="\n".join(entradas) + "\n",
            capture_output=True, text=True, encoding="utf-8", timeout=120,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertNotIn("Traceback", proceso.stdout + proceso.stderr)
        return proceso.stdout

    def conversar(self, niveles, inicia, respuestas):
        """
        Juega como una persona: lee la salida y contesta según la pregunta.
        En su turno intenta las casillas 1, 2, 3... (las ocupadas se rechazan).
        """
        niveles, inicia, respuestas = list(niveles), list(inicia), list(respuestas)
        salida, casilla = "", 0
        with subprocess.Popen(
            [sys.executable, "-u", ARCHIVO],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        ) as proceso:
            while True:
                c = proceso.stdout.read(1)
                if not c:
                    break
                salida += c
                if salida.endswith("Elige el nivel (1-3): "):
                    texto = niveles.pop(0)
                elif salida.endswith("Elige quién inicia (1-2): "):
                    texto = inicia.pop(0)
                elif salida.endswith("elige casilla 1-9: "):
                    texto, casilla = str(casilla % 9 + 1), casilla + 1
                elif salida.endswith("(s/n): "):
                    texto, casilla = respuestas.pop(0), 0
                else:
                    continue
                proceso.stdin.write(texto + "\n")
                proceso.stdin.flush()
        self.assertEqual(proceso.returncode, 0, salida)
        self.assertNotIn("Traceback", salida)
        return salida

    # Intenta todas las casillas en orden; las ocupadas se rechazan y sigue.
    TODAS = [str(n) for n in range(1, 10)] * 2

    def test_partida_completa_en_cada_nivel_y_turno(self):
        for nivel in "123":
            for inicia in (INICIA_COMPU, INICIA_HUMANO):
                with self.subTest(nivel=nivel, inicia=inicia):
                    salida = self.conversar([nivel], [inicia], ["n"])
                    self.assertRegex(salida, r"Ganó la computadora|¡Ganaste|Empate")
                    self.assertIn("¿Jugar otra vez?", salida)

    def test_inicia_la_computadora(self):
        salida = self.ejecutar(["1", INICIA_COMPU])
        self.assertIn("La computadora juega con X y tú con O.", salida)
        # Lo primero que pasa en el tablero es la jugada de la computadora.
        self.assertLess(salida.index("La computadora (X) juega"), salida.index("Tu turno (O)"))

    def test_inicia_el_humano(self):
        salida = self.ejecutar(["1", INICIA_HUMANO, "5"])
        self.assertIn("La computadora juega con O y tú con X.", salida)
        self.assertLess(salida.index("Tu turno (X)"), salida.index("La computadora (O) juega"))
        self.assertIn("4 | X | 6", salida)

    def test_quien_inicia_invalido(self):
        salida = self.ejecutar(["1", "", "0", "3", "si", "12", INICIA_HUMANO, "5"])
        self.assertEqual(salida.count("Opción inválida."), 5)
        self.assertIn("tú con X", salida)

    def test_nivel_invalido(self):
        salida = self.ejecutar(["", "0", "4", "abc", "1 2", "-1", "1", INICIA_COMPU] + self.TODAS + ["n"])
        self.assertEqual(salida.count("Opción inválida."), 6)
        self.assertIn("Nivel: Fácil", salida)

    def test_bom_de_powershell_se_ignora(self):
        salida = self.ejecutar(["﻿2", INICIA_HUMANO, "﻿5"])
        self.assertNotIn("Opción inválida.", salida)
        self.assertNotIn("Entrada inválida", salida)
        self.assertIn("4 | X | 6", salida)

    def test_nivel_con_espacios(self):
        salida = self.ejecutar(["  2  ", f" {INICIA_COMPU} "] + self.TODAS + ["n"])
        self.assertIn("Nivel: Difícil", salida)
        self.assertIn("tú con O", salida)

    def test_casillas_invalidas(self):
        malas = ["", "abc", "0", "10", "-1", "5.5", "²", "1e1", "99999999999999999999"]
        for inicia in (INICIA_COMPU, INICIA_HUMANO):
            with self.subTest(inicia=inicia):
                salida = self.ejecutar(["1", inicia] + malas + self.TODAS + ["n"])
                self.assertEqual(salida.count("Entrada inválida"), len(malas))

    def test_casilla_ocupada(self):
        # Tras jugar en la 1, volver a pedir la 1 siempre está ocupada
        # (nadie puede ganar antes del segundo turno del humano).
        for inicia in (INICIA_COMPU, INICIA_HUMANO):
            with self.subTest(inicia=inicia):
                salida = self.ejecutar(["1", inicia, "1", "1"] + self.TODAS)
                self.assertIn("Esa casilla ya está ocupada", salida)

    def test_jugar_otra_vez(self):
        salida = self.conversar(["1", "3", "2"], [INICIA_COMPU, INICIA_HUMANO, INICIA_HUMANO], ["s", "S", "n"])
        self.assertEqual(salida.count("Nivel:"), 3)
        for nombre in ("Fácil", "Imposible", "Difícil"):
            self.assertIn(f"Nivel: {nombre}", salida)
        self.assertEqual(salida.count("tú con O"), 1)
        self.assertEqual(salida.count("tú con X"), 2)

    def test_respuesta_distinta_de_s_termina(self):
        for respuesta in ("n", "N", "", "no", "x"):
            with self.subTest(respuesta=respuesta):
                salida = self.conversar(["1"], [INICIA_COMPU], [respuesta])
                self.assertEqual(salida.count("Nivel:"), 1)

    def test_fin_de_entrada_cancela_sin_error(self):
        for entradas in ([], ["1"], ["1", INICIA_COMPU], ["1", INICIA_HUMANO, "5"]):
            with self.subTest(entradas=entradas):
                self.assertIn("Partida cancelada.", self.ejecutar(entradas))

    def test_tablero_muestra_numeros_de_casillas_libres(self):
        salida = self.ejecutar(["1", INICIA_HUMANO])
        self.assertIn("1 | 2 | 3", salida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
