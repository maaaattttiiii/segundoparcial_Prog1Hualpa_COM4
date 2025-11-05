"""
Parcial 2 - Persistencia Jerárquica (NBA)
-----------------------------------------
Estructura jerárquica:
nba / conferencia (este-oeste) / equipo / players.csv

Cada jugador se guarda como un diccionario con:
id, nombre, posicion, puntos, rebotes, asistencias

Requisitos cumplidos:
✔ Jerarquía 3 niveles
✔ Persistencia CSV (with open)
✔ Recursividad para lectura global
✔ CRUD + ordenamiento + estadísticas
✔ Manejo de errores y validaciones
"""

import os
import csv
import uuid
from typing import List, Dict, Any, Optional

# ---------------------------
# CONFIGURACIÓN GLOBAL
# ---------------------------
BASE_DIR = os.path.join(os.getcwd(), "data", "nba")
CSV_FILENAME = "players.csv"
CSV_HEADERS = ["id", "nombre", "posicion", "puntos", "rebotes", "asistencias"]


# ---------------------------
# VALIDACIONES
# ---------------------------
def validar_nombre(nombre: str) -> bool:
    return isinstance(nombre, str) and nombre.strip() != ""


def validar_posicion(posicion: str) -> bool:
    posiciones_validas = {"base", "escolta", "alero", "ala-pivot", "pivot"}
    return posicion.lower() in posiciones_validas


def validar_estadistica(valor: Any) -> bool:
    try:
        v = float(valor)
        return v >= 0
    except (TypeError, ValueError):
        return False


# ---------------------------
# UTILIDADES
# ---------------------------
def asegurar_directorio(*partes: str) -> str:
    """Crea directorios si no existen y devuelve la ruta final."""
    ruta = os.path.join(BASE_DIR, *partes)
    os.makedirs(ruta, exist_ok=True)
    return ruta


def inicializar_csv_si_necesario(ruta_dir: str) -> str:
    """Crea el CSV si no existe."""
    ruta_csv = os.path.join(ruta_dir, CSV_FILENAME)
    if not os.path.exists(ruta_csv):
        with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
    return ruta_csv


def leer_csv(ruta_csv: str) -> List[Dict[str, str]]:
    jugadores = []
    try:
        with open(ruta_csv, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for fila in reader:
                jugadores.append(fila)
    except FileNotFoundError:
        return []
    return jugadores


def escribir_csv(ruta_csv: str, filas: List[Dict[str, Any]]) -> None:
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(filas)


# ---------------------------
# CRUD
# ---------------------------
def alta_jugador(conferencia: str, equipo: str, jugador: Dict[str, Any]) -> Dict[str, str]:
    """Crea un nuevo jugador dentro de la jerarquía."""
    if not validar_nombre(jugador.get("nombre", "")):
        raise ValueError("Nombre inválido.")
    if not validar_posicion(jugador.get("posicion", "")):
        raise ValueError("Posición inválida.")
    for stat in ("puntos", "rebotes", "asistencias"):
        if not validar_estadistica(jugador.get(stat, 0)):
            raise ValueError(f"Valor inválido en {stat}")

    dir_path = asegurar_directorio(conferencia, equipo)
    ruta_csv = inicializar_csv_si_necesario(dir_path)

    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre": jugador["nombre"].strip(),
        "posicion": jugador["posicion"].lower(),
        "puntos": float(jugador["puntos"]),
        "rebotes": float(jugador["rebotes"]),
        "asistencias": float(jugador["asistencias"]),
    }

    jugadores = leer_csv(ruta_csv)
    jugadores.append({k: str(v) for k, v in nuevo.items()})
    escribir_csv(ruta_csv, jugadores)
    return nuevo


def leer_todos_los_jugadores(base_dir: Optional[str] = None) -> List[Dict[str, str]]:
    """Función RECURSIVA que recorre toda la jerarquía NBA."""
    if base_dir is None:
        base_dir = BASE_DIR

    todos = []

    if not os.path.exists(base_dir):
        return todos

    for elemento in os.listdir(base_dir):
        ruta = os.path.join(base_dir, elemento)
        if os.path.isdir(ruta):
            todos.extend(leer_todos_los_jugadores(ruta))  # recursividad
        elif os.path.basename(ruta) == CSV_FILENAME:
            filas = leer_csv(ruta)
            for f in filas:
                f["_origen"] = ruta
                todos.append(f)
    return todos


def actualizar_jugador(jugador_id: str, cambios: Dict[str, Any]) -> Dict[str, str]:
    """Actualiza un jugador existente por su ID."""
    todos = leer_todos_los_jugadores()
    for j in todos:
        if j["id"] == jugador_id:
            ruta = j["_origen"]
            jugadores = leer_csv(ruta)
            for fila in jugadores:
                if fila["id"] == jugador_id:
                    fila.update({
                        "nombre": cambios.get("nombre", fila["nombre"]),
                        "posicion": cambios.get("posicion", fila["posicion"]),
                        "puntos": cambios.get("puntos", fila["puntos"]),
                        "rebotes": cambios.get("rebotes", fila["rebotes"]),
                        "asistencias": cambios.get("asistencias", fila["asistencias"]),
                    })
                    escribir_csv(ruta, jugadores)
                    return fila
    raise KeyError("Jugador no encontrado.")


def eliminar_jugador(jugador_id: str) -> bool:
    todos = leer_todos_los_jugadores()
    for j in todos:
        if j["id"] == jugador_id:
            ruta = j["_origen"]
            jugadores = leer_csv(ruta)
            nuevos = [f for f in jugadores if f["id"] != jugador_id]
            escribir_csv(ruta, nuevos)
            return True
    return False


# ---------------------------
# ESTADÍSTICAS
# ---------------------------
def estadisticas_globales(jugadores: List[Dict[str, str]]) -> Dict[str, Any]:
    total = len(jugadores)
    if total == 0:
        return {"total": 0}

    puntos = [float(j["puntos"]) for j in jugadores]
    rebotes = [float(j["rebotes"]) for j in jugadores]
    asistencias = [float(j["asistencias"]) for j in jugadores]

    return {
        "total_jugadores": total,
        "promedio_puntos": sum(puntos) / total,
        "promedio_rebotes": sum(rebotes) / total,
        "promedio_asistencias": sum(asistencias) / total,
    }


# ---------------------------
# MENÚ INTERACTIVO
# ---------------------------
def menu():
    while True:
        print("\n=== GESTOR NBA ===")
        print("1. Alta de jugador")
        print("2. Listar todos (recursivo)")
        print("3. Actualizar jugador")
        print("4. Eliminar jugador")
        print("5. Estadísticas globales")
        print("0. Salir")

        op = input("Opción: ").strip()

        if op == "1":
            conferencia = input("Conferencia (este/oeste): ").lower().strip()
            equipo = input("Equipo: ").lower().replace(" ", "_")
            nombre = input("Nombre del jugador: ")
            posicion = input("Posición (base/escolta/alero/ala-pivot/pivot): ")
            puntos = input("Puntos por partido: ")
            rebotes = input("Rebotes por partido: ")
            asistencias = input("Asistencias por partido: ")

            try:
                nuevo = alta_jugador(conferencia, equipo, {
                    "nombre": nombre,
                    "posicion": posicion,
                    "puntos": puntos,
                    "rebotes": rebotes,
                    "asistencias": asistencias
                })
                print("Jugador agregado:", nuevo)
            except Exception as e:
                print("Error:", e)

        elif op == "2":
            todos = leer_todos_los_jugadores()
            if not todos:
                print("No hay jugadores cargados.")
            else:
                print("\n--- LISTA DE JUGADORES ---")
                for j in todos:
                    print(f"{j['nombre']} ({j['posicion']}) - {j['puntos']} pts, {j['rebotes']} reb, {j['asistencias']} ast")

        elif op == "3":
            id_jugador = input("ID del jugador a actualizar: ")
            campo = input("Campo a modificar (nombre/posicion/puntos/rebotes/asistencias): ")
            valor = input("Nuevo valor: ")
            try:
                actualizado = actualizar_jugador(id_jugador, {campo: valor})
                print("Jugador actualizado:", actualizado)
            except Exception as e:
                print("Error:", e)

        elif op == "4":
            id_jugador = input("ID del jugador a eliminar: ")
            if eliminar_jugador(id_jugador):
                print("Jugador eliminado correctamente.")
            else:
                print("No se encontró el jugador.")

        elif op == "5":
            jugadores = leer_todos_los_jugadores()
            stats = estadisticas_globales(jugadores)
            print("\n--- ESTADÍSTICAS GLOBALES ---")
            for k, v in stats.items():
                print(f"{k}: {v}")

        elif op == "0":
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")


# ---------------------------
# EJECUCIÓN PRINCIPAL
# ---------------------------
if __name__ == "__main__":
    menu()
