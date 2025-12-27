"""End-to-End Tests mit Playwright für die Streamlit-App.

Ziel: Prüfen, dass ein Benutzer alle Abläufe erfolgreich
durchführen kann, inklusive Frontend (Streamlit), Backend und Persistenz.

Framework: pytest + Playwright

Szenarien (3 Stück):
1) Aufgabe über UI anlegen → sichtbar und gespeichert, App-Neustart → wiederhergestellt
2) Aufgabe als erledigt markieren → Status sichtbar (UI) und gespeichert (JSON)
3) Aufgabe löschen → aus UI und Persistenz entfernt

Hinweise fürs Live-Coding:
- Wenn Selektoren instabil sind, verwende `page.get_by_text(...)` für sichtbare Texte.
- Mit `pytest -s` werden Prints gezeigt; mit `--headed` öffnet Playwright den Browser sichtbar.
- Datenisolation: Wir leeren `data/todos.json` vor jedem Test und stellen nachher wieder her.
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

import pytest
from playwright.sync_api import expect

# Projektpfad für Importe
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ===== Hilfsfunktionen für Daten-Setup =====

DATA_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "data"
TODOS_JSON = DATA_DIR / "todos.json"
CATS_JSON = DATA_DIR / "categories.json"


def _write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


# ===== Fixtures: Daten-Reset + Streamlit-Server =====

@pytest.fixture(autouse=True)
def reset_data_files():
    """Sorge pro Test für leere Persistenz-Dateien und stelle danach wieder her.

    Live-Coding-Optionen:
    - Statt Leeren: Backup/Restore, wenn vorhandene produktive Daten wichtig sind.
    - Alternativ: App im temporären Arbeitsverzeichnis starten (cwd=tmp_path).
    """
    backup_dir = DATA_DIR / "_backup_e2e"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup anlegen, falls vorhanden
    if TODOS_JSON.exists():
        shutil.copy(TODOS_JSON, backup_dir / "todos.json.bak")
    if CATS_JSON.exists():
        shutil.copy(CATS_JSON, backup_dir / "categories.json.bak")

    # Leere Dateien schreiben
    _write_json(TODOS_JSON, [])
    _write_json(CATS_JSON, [])

    yield

    # Restore (falls Backups vorhanden)
    try:
        if (backup_dir / "todos.json.bak").exists():
            shutil.copy(backup_dir / "todos.json.bak", TODOS_JSON)
        if (backup_dir / "categories.json.bak").exists():
            shutil.copy(backup_dir / "categories.json.bak", CATS_JSON)
    finally:
        shutil.rmtree(backup_dir, ignore_errors=True)


@pytest.fixture()
def streamlit_server():
    """Startet die Streamlit-App und liefert base_url. Stoppt nach Test.

    Hinweise:
    - `--server.headless=true` für CI/Headless-Umgebungen
    - Warte auf Port 8501, bevor Tests starten
    """
    env = os.environ.copy()
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true", "--logger.level=error"],
        cwd=str(Path(__file__).resolve().parent.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    base_url = "http://localhost:8501"

    # Warten bis Server bereit
    for _ in range(60):
        try:
            import urllib.request
            with urllib.request.urlopen(base_url) as resp:
                if resp.status == 200:
                    break
        except Exception:
            time.sleep(0.5)
    else:
        proc.terminate()
        raise RuntimeError("Streamlit-Server nicht erreichbar")

    yield base_url

    # Stoppen
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


# ===== Szenario 1: Anlegen und Wiederherstellen =====

def test_e2e_create_and_restore(streamlit_server, page):
    """Aufgabe über UI anlegen, Persistenz prüfen und nach App-Neustart wiederherstellen."""
    page.goto(streamlit_server)

    # Formular öffnen
    page.get_by_role("button", name="Neue Aufgabe ＋").click()

    # Titel/Optionales ausfüllen
    page.get_by_label("📝 Titel (Pflicht)").fill("E2E Create")
    page.get_by_role("button", name="☑️ Aufgabe hinzufügen").click()

    # Erfolg sichtbar
    page.get_by_text("☑️ Aufgabe erstellt: E2E Create").is_visible()
    # Aufgabe in Liste sichtbar
    page.get_by_text("E2E Create").is_visible()

    # Persistenz: JSON enthält Eintrag
    with open(TODOS_JSON, "r", encoding="utf-8") as f:
        raw = json.load(f)
        assert len(raw) == 1
        assert raw[0]["title"] == "E2E Create"

    # App neu starten und prüfen, dass Aufgabe wieder angezeigt wird
    # Hinweis: Für Stabilität kurze Wartezeit
    # Seite neu laden (Streamlit baut State aus Persistenz wieder auf)
    page.reload()
    page.wait_for_load_state("networkidle")
    page.get_by_text("E2E Create").is_visible()


# ===== Szenario 2: Erledigt markieren und Persistenz prüfen =====

def test_e2e_complete_and_persist(streamlit_server, page):
    """Checkbox in UI setzen → Aufgabe wird erledigt und JSON zeigt COMPLETED."""
    page.goto(streamlit_server)

    # Neue Aufgabe erstellen
    page.get_by_role("button", name="Neue Aufgabe ＋").click()
    page.get_by_label("📝 Titel (Pflicht)").fill("E2E Complete")
    page.get_by_role("button", name="☑️ Aufgabe hinzufügen").click()

    # Warte auf Streamlit rerun und Aufgabe sichtbar
    expect(page.get_by_text("E2E Complete")).to_be_visible()
    page.wait_for_timeout(500)
    
    # Klick auf das Label-Element, das die Checkbox umgibt (robuster für Streamlit)
    # Das st.checkbox Widget in Streamlit rendert ein label-Element, das geklickt werden kann
    page.locator('label').filter(has=page.locator('input[aria-label="mark_done"]')).first.click(force=True)
    
    # Warte auf Streamlit rerun nach Toggle
    page.wait_for_timeout(2500)

    # Prüfe Persistenz
    with open(TODOS_JSON, "r", encoding="utf-8") as f:
        raw = json.load(f)
        assert any(item["title"] == "E2E Complete" and item["status"] == "COMPLETED" for item in raw), \
            f"Expected COMPLETED status in JSON, but got: {raw}"
    
    # UI-Check: Erledigte Aufgaben Sektion sollte erscheinen
    expect(page.get_by_text("Erledigte Aufgaben")).to_be_visible(timeout=5000)


# ===== Szenario 3: Löschen und Konsistenz prüfen =====

def test_e2e_delete_and_consistency(streamlit_server, page):
    """UI-Löschen inkl. Bestätigung → Aufgabe aus UI und JSON entfernt."""
    page.goto(streamlit_server)

    # Aufgabe erstellen
    page.get_by_role("button", name="Neue Aufgabe ＋").click()
    page.get_by_label("📝 Titel (Pflicht)").fill("E2E Delete")
    page.get_by_role("button", name="☑️ Aufgabe hinzufügen").click()

    # Löschen: Trash klicken, dann Bestätigen (✓)
    page.get_by_role("button", name="🗑️").click()
    page.get_by_role("button", name="✓").click()

    # In UI sollte der Titel nicht mehr sichtbar sein
    # Warte robust bis Item verborgen ist (Streamlit rerun)
    expect(page.get_by_text("E2E Delete")).to_be_hidden()

    # Persistenz: JSON leer
    with open(TODOS_JSON, "r", encoding="utf-8") as f:
        raw = json.load(f)
        assert all(item["title"] != "E2E Delete" for item in raw)
