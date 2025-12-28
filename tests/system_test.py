"""Systemtests: End-to-End über Service (Controller), Repository (JSONStorage)
und kontrollierte UI-Aspekte ohne echten Browser.

Szenarien:
- Aufgabe anlegen → Speicherung und Abruf geprüft
- Aufgabe erledigt markieren → Status korrekt im System
- Aufgabe löschen → System konsistent
- Fehlerfälle → kontrollierte Fehlermeldung

Hinweis: Wir verwenden ein temporäres Datenverzeichnis (pytest tmp_path),
um echte Datei-I/O der Repository-Schicht zu testen, ohne Benutzerdateien
zu beeinflussen.
"""

import os
import sys
import json
from pathlib import Path
from datetime import date

import pytest

# Projekt-Imports ermöglichen
# Anpassbar beim Live-Coding: Wenn sich die Projektstruktur ändert (z.B. Ordner umbenannt),
# diesen Pfad entsprechend korrigieren, damit die Importe funktionieren.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.controllers import TodoController  # noqa: E402
from app.models import JSONStorage, TodoStatus  # noqa: E402


# === Fixtures ===

@pytest.fixture()
def storage_dir(tmp_path: Path) -> Path:
    """Isoliertes Datenverzeichnis für echte Persistenztests."""
    # Live-Coding-Varianten:
    # - Für reproduzierbares Debugging: festen Pfad verwenden (z.B. Path("/tmp/se_data"))
    # - Für schnelle Unit-Tests: Fixture durch Mock-Storage ersetzen (keine Datei-I/O)
    return tmp_path / "data"


@pytest.fixture()
def todo_controller(storage_dir: Path) -> TodoController:
    """Echter Controller mit JSONStorage auf Disk (kein Mock)."""
    # Alternative (schneller, ohne Datei-I/O):
    #
    # from unittest.mock import Mock
    # storage = Mock(spec=JSONStorage)
    # storage.load_todos.return_value = []
    # storage.save_todos.return_value = None
    # return TodoController(storage=storage)
    #
    # Hinweis: Für Persistenz-Validierung hier bewusst echter JSONStorage.
    storage = JSONStorage(data_dir=storage_dir)
    return TodoController(storage=storage)


# === Szenario 1: Aufgabe anlegen — Speicherung und Abruf ===

def test_system_create_and_fetch(todo_controller: TodoController, storage_dir: Path):
    """Anlegen einer Aufgabe wird in JSON gespeichert und ist nach Reload abrufbar."""
    # Arrange
    # Anpassbar: Titel/Beschreibung, zusätzliche Felder (due_date, categories, recurrence)
    title = "System Create"
    desc = "Beschreibung"

    # Act: Aufgabe anlegen
    created = todo_controller.create_todo(title=title, description=desc, due_date=date.today())
    # Live-Coding: Hier weitere Felder setzen, um Serialisierung zu demonstrieren:
    # categories=["Work"], recurrence=RecurrenceType.DAILY

    # Assert: Datei existiert und enthält Eintrag
    todos_json = storage_dir / "todos.json"
    assert todos_json.exists(), "todos.json sollte erzeugt worden sein"
    with open(todos_json, "r", encoding="utf-8") as f:
        raw = json.load(f)
        assert len(raw) == 1
        assert raw[0]["title"] == title
        # Anpassbar: Weitere Felder prüfen, z.B. raw[0]["description"], raw[0]["due_date"]

    # Reload des Controllers → Abruf prüfen
    reloaded = TodoController(storage=JSONStorage(data_dir=storage_dir))
    fetched = reloaded.get_todo(created.id)
    assert fetched is not None
    assert fetched.title == title
    assert fetched.description == desc
    # Debug-Hinweis: Bei unerwarteten Werten print() oder pdb.set_trace() einsetzen


# === Szenario 2: Aufgabe als erledigt markieren — Status korrekt ===

def test_system_mark_completed(todo_controller: TodoController, storage_dir: Path):
    """Erledigt-Markierung wird persistiert: Status=COMPLETED, completed_at gesetzt."""
    todo = todo_controller.create_todo(title="System Complete")

    # Act: erledigen
    todo_controller.mark_completed(todo.id)
    # Alternative Pfade: todo_controller.toggle_completion(todo.id) oder todo_controller.mark_open(todo.id)

    # Reload und prüfen
    reloaded = TodoController(storage=JSONStorage(data_dir=storage_dir))
    persisted = reloaded.get_todo(todo.id)
    assert persisted is not None
    assert persisted.status == TodoStatus.COMPLETED
    assert persisted.completed_at is not None
    # Anpassbar: Nach mark_open() sollte completed_at None sein; beide Pfade demonstrierbar


# === Szenario 3: Aufgabe löschen — System konsistent ===

def test_system_delete_consistency(todo_controller: TodoController, storage_dir: Path):
    """Löschen entfernt das Item aus Repository und Datei bleibt konsistent."""
    todo = todo_controller.create_todo(title="System Delete")
    # Live-Coding: Mehrere Todos anlegen und nur eines löschen, um Konsistenz zu zeigen

    # Act: löschen
    ok = todo_controller.delete_todo(todo.id)
    assert ok is True

    # Reload und prüfen
    reloaded = TodoController(storage=JSONStorage(data_dir=storage_dir))
    assert reloaded.get_todo(todo.id) is None
    assert len(reloaded.get_todos()) == 0

    # Datei-Inhalt verifizieren
    with open(storage_dir / "todos.json", "r", encoding="utf-8") as f:
        raw = json.load(f)
        assert raw == []
        # Anpassbar: Bei mehreren Einträgen prüfen, dass nur das gelöschte fehlt


# === Szenario 4: Fehlerfälle — kontrollierte Fehlermeldung ===

def test_system_errors_controlled_messages(todo_controller: TodoController):
    """Fehlerhafte Eingaben liefern klare, kontrollierte Fehlermeldungen."""
    # Leerer Titel
    with pytest.raises(ValueError, match="Titel darf nicht leer sein"):
        todo_controller.create_todo(title="   ")

    # Zu viele Kategorien
    too_many = [f"C{i}" for i in range(6)]
    with pytest.raises(ValueError, match="Max. 5 Kategorien pro Aufgabe erlaubt"):
        todo_controller.create_todo(title="System Error Categories", categories=too_many)
    # Erweiterbar: Weitere Fehlerfälle testen (z.B. Titel > 200 Zeichen,
    # invalides Datum, Kategorie-Validierung in CategoryController)
