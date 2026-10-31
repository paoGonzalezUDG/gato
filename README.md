# Gato con Minimax

Juego del Gato (Tic-Tac-Toe) en consola contra la computadora. La computadora decide sus jugadas con el algoritmo **Minimax** (búsqueda con adversario) y la profundidad de la búsqueda se puede limitar para tener tres niveles de dificultad.

## Requisitos

- Python 3.8 o superior (probado con Python 3.13).
- No necesita librerías externas: solo usa la librería estándar (`math`, `random`).

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
python busqueda_con_adversario.py
```

En Windows, si `python` no se reconoce, usar `py busqueda_con_adversario.py`.

## Cómo jugar

1. Elige el nivel: `1` Fácil, `2` Difícil o `3` Imposible.
2. Elige quién inicia: `1` la computadora o `2` tú. **Quien inicia juega con X.**
3. En tu turno escribe el número de una casilla libre y presiona Enter. Las casillas libres muestran su número:

   ```
   1 | 2 | 3
   ---------
   4 | 5 | 6
   ---------
   7 | 8 | 9
   ```

4. Al terminar la partida puedes jugar otra vez (`s`) o salir (cualquier otra tecla). `Ctrl + C` cancela la partida en cualquier momento.

Las entradas inválidas (letras, números fuera de rango, casillas ocupadas) se rechazan con un mensaje y se vuelve a preguntar.

## Algoritmo: Minimax

El juego se modela como un problema de búsqueda con adversario:

| Elemento | En el código | Descripción |
|---|---|---|
| Estado inicial | `[" "] * 9` | Tablero vacío (lista de 9 casillas). |
| Jugador | `jugador(estado)` | X empieza; después se alternan. |
| Acciones | `acciones(estado)` | Casillas libres. |
| Modelo de transición | `resultado(estado, accion)` | Nuevo tablero con la ficha colocada (no modifica el original). |
| Prueba terminal | `es_terminal(estado)` | Hay ganador o el tablero está lleno. |
| Utilidad | `utilidad(estado)` | +1 si gana X, −1 si gana O, 0 si es empate. |

- **MAX** juega con X y elige la jugada de mayor valor (`valor_max`).
- **MIN** juega con O y elige la jugada de menor valor (`valor_min`).
- `valor_max` y `valor_min` se llaman entre sí recursivamente hasta llegar a estados terminales; cada uno supone que el rival también juega de forma óptima.
- `minimax(estado, profundidad)` devuelve la mejor casilla para quien tenga el turno, por lo que la computadora puede jugar tanto con X como con O.
- Entre jugadas con el mismo valor elige una al azar, para que las partidas no sean siempre iguales.

### Profundidad limitada y función de evaluación

Para controlar cuántos niveles del árbol visita, las funciones reciben el parámetro `profundidad`, que disminuye en 1 en cada llamada recursiva. Al llegar a 0 la búsqueda se corta y el estado se califica con la heurística `evaluar(estado)`:

```
evaluar = (líneas que X aún puede completar − líneas que O aún puede completar) / 10
```

Se divide entre 10 para que la estimación siempre valga menos que una victoria real (±1). Si `profundidad` es infinita (`math.inf`), es el Minimax completo.

Al mover, el programa muestra cuántos nodos visitó, para comparar el esfuerzo de cada nivel.

## Niveles de dificultad

| Nivel | Profundidad | Nodos en la 1.ª jugada | Si inicia la computadora | Si inicias tú |
|---|---|---|---|---|
| Fácil | 1 | 9 | Se le puede ganar | Se le puede ganar |
| Difícil | 3 | 585 | Nunca pierde | Se le puede ganar |
| Imposible | completa | 549,945 | Nunca pierde | Nunca pierde |

- **Fácil** solo mira su propia jugada: aprovecha una victoria inmediata, pero no ve las amenazas del rival.
- **Difícil** mira 3 jugadas adelante: bloquea amenazas, pero sufre el **efecto horizonte**. Por ejemplo, si inicias en la 1, la computadora toma el centro (5), juegas 6, la computadora juega 7 y tú respondes 3: creas dos amenazas a la vez (1-2-3 y 3-6-9) que la computadora no vio venir porque aparecen a más de 3 niveles de distancia.
- **Imposible** explora el árbol completo y juega perfecto. Con juego perfecto de ambos lados, el gato siempre termina en empate. La primera jugada tarda alrededor de un segundo.

Los niveles se definen en el diccionario `NIVELES` de `busqueda_con_adversario.py`; para agregar uno basta con añadir una entrada con su nombre y profundidad.

## Pruebas

Las pruebas usan `unittest`, que viene incluido con Python, así que no hay que instalar nada.

### Cómo correrlas

1. Abre una terminal **dentro de la carpeta del proyecto** (donde están `busqueda_con_adversario.py` y `test_busqueda_con_adversario.py`). En VS Code: menú *Terminal → New Terminal*.
2. Ejecuta cualquiera de estos comandos (en Windows puedes cambiar `python` por `py`):

   ```bash
   # Todas las pruebas, mostrando el nombre y resultado de cada una
   python -m unittest -v test_busqueda_con_adversario

   # Todas las pruebas, forma corta (equivalente)
   python test_busqueda_con_adversario.py
   ```

3. Tardan unos 10 segundos. Si todo está bien, al final aparece:

   ```
   ----------------------------------------------------------------------
   Ran 30 tests in 9.5s

   OK
   ```

   Si alguna falla, en lugar de `OK` aparece `FAILED (failures=N)` y, arriba, el nombre de la prueba que falló con el detalle del error.

### Correr solo una parte

```bash
# Solo un grupo: PruebasReglas, PruebasMinimax o PruebasConsola
python -m unittest -v test_busqueda_con_adversario.PruebasMinimax

# Solo una prueba
python -m unittest -v test_busqueda_con_adversario.PruebasMinimax.test_imposible_nunca_pierde
```

### Qué comprueban

Las 30 pruebas de `test_busqueda_con_adversario.py` comprueban:

- **Reglas del juego:** las 8 líneas ganadoras para X y O, empates, turnos y que los estados no se modifiquen.
- **Minimax:** que gane cuando puede y bloquee amenazas, el número exacto de nodos por nivel, y —recorriendo todas las partidas posibles del rival— que Imposible nunca pierde, jugando primero o segundo.
- **Consola:** ejecutan el programa real con entradas inválidas, casillas ocupadas, jugar otra vez y cancelar, verificando que nunca aparezca un error de Python.

## Estructura

```
busqueda_con_adversario.py       Juego, algoritmo Minimax e interfaz de consola
test_busqueda_con_adversario.py  Pruebas automáticas
```
