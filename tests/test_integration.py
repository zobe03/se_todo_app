"""Integrationstests für die JSONStorage-Persistenz.

Jeder Test nutzt ein temporäres Datenverzeichnis für Isolation und prüft,
dass Controller-Operationen korrekt auf Disk geschrieben und wieder geladen
werden.
"""

import os
import sys
from pathlib import Path

import pytest

# Erlaubt Importe aus dem Projektwurzelverzeichnis (ggf. anpassen, falls Projektstruktur geändert wird)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers import TodoController  # noqa: E402
from models import JSONStorage, TodoStatus  # noqa: E402


@pytest.fixture()
def storage_dir(tmp_path: Path) -> Path:
    """Stellt ein isoliertes Verzeichnis für JSONStorage-Dateien bereit."""
    # Jeder Test erhält seinen eigenen data/-Pfad unterhalb von pytest tmp; man kann hier auch einen festen Pfad für Debugging verwenden
    return tmp_path / "data"


@pytest.fixture()
def todo_controller(storage_dir: Path) -> TodoController:
    """Erstellt einen Controller mit echtem JSONStorage auf Disk.
    with mocks:
        @pytest.fixture()
        def storage_dir():
            storage = Mock(spec=JSONStorage)
            storage.load_todos.return_value = []
            storage.save_todos.return_value = None
            return storage

        @pytest.fixture()
        def todo_controller(storage_dir):
            return TodoController(storage=storage_dir)
    """
    # Nutzt echte Persistenz (keine Mocks), um Speichern/Laden zu testen; es könnten Mocks gewählt werden, um Tests schneller laufen zu lassen
    storage = JSONStorage(data_dir=storage_dir)
    return TodoController(storage=storage)


def test_create_multiple_todos_keeps_repository_consistent(todo_controller: TodoController, storage_dir: Path):
    """Mehrere Todos persistieren und Konsistenz prüfen."""
    titles = ["Alpha", "Beta", "Gamma"]

    # Speichert mehrere Todos nacheinander; man könnte zusätzliche Felder setzen, um Serialisierung zu zeigen
    for title in titles:
        todo_controller.create_todo(title=title)
    """for i, title in enumerate(titles):
            todo_controller.create_todo(
                title=title,
                description=f"Beschreibung für {title}",
                due_date=date.today() + timedelta(days=i),
                categories=["Work", "Urgent"] if i % 2 == 0 else ["Personal"]
            )
    """

    # Neuer Controller erzwingt Reload von Disk
    reloaded = TodoController(storage=JSONStorage(data_dir=storage_dir))
    todos = reloaded.get_todos()

    assert len(todos) == len(titles)
    assert {t.title for t in todos} == set(titles)



def test_updating_status_persists_in_repository(todo_controller: TodoController, storage_dir: Path):
    """Statusänderungen müssen auf Disk ankommen - beide Pfade (Toggle) demonstrieren."""
    todo = todo_controller.create_todo(title="Persist Status")

    # Pfad 1: Toggle von OPEN zu COMPLETED und speichern
    todo_controller.toggle_completion(todo.id)

    # Reload von Disk, um persistierten COMPLETED-Status zu verifizieren
    reloaded = TodoController(storage=JSONStorage(data_dir=storage_dir))
    persisted = reloaded.get_todo(todo.id)

    assert persisted is not None
    assert persisted.status == TodoStatus.COMPLETED, f"Status sollte COMPLETED sein, aber {persisted.status}"
    assert persisted.completed_at is not None, "completed_at sollte nach mark_completed gesetzt sein"

    # Pfad 2: Toggle zurück von COMPLETED zu OPEN und speichern
    todo_controller.toggle_completion(todo.id)

    # Reload von Disk, um persistierten OPEN-Status zu verifizieren
    reloaded2 = TodoController(storage=JSONStorage(data_dir=storage_dir))
    persisted2 = reloaded2.get_todo(todo.id)

    assert persisted2 is not None
    assert persisted2.status == TodoStatus.OPEN, f"Status sollte OPEN sein, aber {persisted2.status}"
    assert persisted2.completed_at is None, "completed_at sollte nach mark_open gelöscht sein"


def test_delete_removes_item_from_repository(todo_controller: TodoController, storage_dir: Path):
    """Löschen entfernt das Todo dauerhaft aus dem Storage."""
    todo = todo_controller.create_todo(title="To be removed")

    # Löschen und in Storage schreiben; beim Live-Coding kann man vorher einen zweiten Todo anlegen, um nur eines zu löschen
    deleted = todo_controller.delete_todo(todo.id)
    assert deleted is True

    # Reload von Disk, um Abwesenheit sicherzustellen; beim Live-Coding kann man hier assert len(todos) prüfen, bevor und nachdem gelöscht wurde
    reloaded = TodoController(storage=JSONStorage(data_dir=storage_dir))
    todos = reloaded.get_todos()

    assert all(t.id != todo.id for t in todos)
    assert len(todos) == 0
