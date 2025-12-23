# 📋 Todo App - Dokumentation

## Überblick

Eine moderne, responsive Todo-App gebaut mit **Streamlit** und Python. Verwalte deine Aufgaben effizient mit Kategorien, Fälligkeitsdaten, Wiederholungen und intelligenten Filtern.

**✅ Features:**
- ✏️ Aufgaben erstellen, bearbeiten, löschen
- ☑️ Aufgaben als erledigt markieren
- 🏷️ Bis zu 5 benutzerdefinierte Kategorien
- 📅 Fälligkeitsdaten mit Kalenderpicker (<3 Klicks)
- ↻ Wiederkehrende Aufgaben (täglich, wöchentlich, monatlich)
- 🔍 Intelligente Filter & Suche
- 💾 Automatisches Speichern (lokal als JSON)
- 📱 Responsive Design (Desktop/Tablet/Mobile)

---

## Installation

### 1. Repository klonen oder herunterladen
```bash
cd /Users/student/Desktop/SE
```

### 2. Virtual Environment erstellen (optional, aber empfohlen)
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# oder: .venv\Scripts\activate  # Windows
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

**Dependencies:**
- `streamlit>=1.28.0` - Web Framework
- `pydantic>=2.0.0` - Datenvalidierung
- `python-dateutil>=2.8.2` - Datumsformatierung

---

## Verwendung

### App starten
```bash
streamlit run app.py
```

Die App öffnet sich automatisch unter **http://localhost:8501**

### Hauptfunktionen

#### 1️⃣ Aufgabenliste (Startseite)
- **Neue Aufgabe erstellen:** Titel + optionale Details eingeben → Speichern
- **Aufgabe abhaken:** Checkbox klicken → markiert als erledigt
- **Aufgabe bearbeiten:** ✏️ Button → Modal öffnet sich
- **Aufgabe löschen:** 🗑️ Button → Bestätigung erforderlich

#### 2️⃣ Filter & Suche
- **Status:** Alle | Offen | Erledigt
- **Kategorie:** Nach Kategorie filtern
- **Fällig:** Alle | Heute | Diese Woche | Überfällig
- **Suche:** Titel durchsuchen

#### 3️⃣ Kategorien verwalten
- **Neue Kategorie:** Name + Farbe wählen
- **Kategorie löschen:** 🗑️ Button
- **Max. 5 Kategorien:** Limit ist erreicht, wenn 5 erstellt sind
- **Kategorien Seite:** Detaillierte Kategorien-Verwaltung

---

## Projektstruktur

```
/Users/student/Desktop/SE/
├── app.py                          # Streamlit Main Entry Point (schlank!)
├── requirements.txt                # Python Dependencies
├── README.md                       # Diese Datei
├── ROADMAP.md                      # Projekt-Roadmap
├── UI-SPEC.md                      # UI-Spezifikation
├── data/
│   ├── todos.json                  # Persistierte Todos (JSON)
│   └── categories.json             # Persistierte Kategorien (JSON)
├── main/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── todo.py                 # Todo Dataclass + Enums
│   │   ├── category.py             # Category Dataclass
│   │   └── storage.py              # JSONStorage
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── todo_controller.py      # Todo Geschäftslogik
│   │   └── category_controller.py  # Kategorie Geschäftslogik
│   └── views/
│       ├── __init__.py
│       └── ui.py                   # Streamlit UI + Pages
└── testing/
    ├── __init__.py
    ├── test_models.py
    ├── test_todo_controller.py
    ├── test_storage.py
    └── test_category_controller.py
```

---

## MVC-Architektur

Die App folgt dem **Model-View-Controller** Pattern:

### **Model** (`main/models/`)
- **Todo**: Aufgaben-Datenstruktur mit Status, Fälligkeitsdatum, Kategorien, Wiederholung
- **Category**: Kategorie-Datenstruktur mit Name, Farbe
- **Storage**: JSON-basierte Persistierung (Save/Load)

### **Controller** (`main/controllers/`)
- **TodoController**: Geschäftslogik für CRUD, Filter, Statistiken, Recurrence
- **CategoryController**: Geschäftslogik für Kategorien mit Validierung (max. 5)

### **View** (`main/views/ui.py`)
- **Streamlit Pages**: `show_todo_list_page()`, `show_categories_page()`
- **Komponenten**: `render_task_card()`, `render_new_task_form()`, `render_filter_sidebar()`
- **Styling**: Responsive Design mit CSS

### **App** (`app.py`)
- **Schlanke Orchestrierungs-Schicht**: Navigation, Session State, Page Router

---

## Usability-Prinzipien

✅ **Sichtbarkeit Systemstatus**
- Status-Header zeigt: Offen/Erledigt/Überfällig Zahl
- Toast-Meldungen für Aktionen (Erstellen, Löschen, Aktualisieren)

✅ **Übereinstimmung System & Wirklichkeit**
- Deutsche Labels: "Erledigt", nicht "COMPLETED"
- Intuitive Icons: ☐ (offen), ☑️ (erledigt), 🗑️ (löschen), ✏️ (bearbeiten)

✅ **Nutzerkontrolle & Freiheit**
- Bestätigung vor dem Löschen
- Abbrechen-Buttons in Modalen
- Keine unumkehrbaren Aktionen ohne Warnung

✅ **Beständigkeit & Standards**
- Konsistente Button-Positionen
- Standard-Icons und Farben
- Vertraute UI-Patterns

✅ **Fehlervermeidung**
- Validierung: Titel nicht leer, max. 5 Kategorien
- Warnung bei überfälligen Aufgaben
- Klare Fehlermeldungen

✅ **Wiedererkennung statt Erinnerung**
- Farb-Badges für Kategorien
- Status-Icons (☑️, ☐, ⚠️)
- Visuelle Indikatoren für Zustände

✅ **Flexibilität & Effizienz**
- Quick-Buttons: Heute, Morgen, +7 Tage
- Filter-Sidebar immer erreichbar
- Schnelle Suche

✅ **Ästhetisches & minimalistisches Design**
- Whitespace, 2-3 Farben, große Buttons
- Keine überflüssigen UI-Elemente
- Klare Hierarchie

✅ **Gute Fehlermeldungen**
- Kurz, konkret, nahe am Feld
- Mit Lösungsvorschlag
- z.B.: "Du hast bereits 5 Kategorien. Lösche eine, um eine neue anzulegen."

✅ **Hilfe & Dokumentation**
- In-App Help-Box mit Quick Start
- Tooltips für komplexe Funktionen
- Link zu README.md

---

## Performance

### <5 Sekunden für neue Aufgabe ✅
- JSON-Storage ist schnell (<100ms)
- Kein Datenbank-Overhead
- Session-Caching für Controller

### Fälligkeitsdatum in <3 Klicks ✅
- `st.date_input()` = 1 Klick Kalender
- Vorausgefüllte Quick-Buttons (Heute, Morgen, +7 Tage) = 1 Klick

### Responsive Design ✅
- Desktop: 2-Spalten Layout (Sidebar + Main)
- Mobile: 1-Spalte, Sidebar einklappbar
- Tablet: Hybrid-Layout

---

## Datenspeicherung

Todos und Kategorien werden **lokal als JSON** gespeichert:

```
data/
├── todos.json       # Format: [{ id, title, status, due_date, categories, ... }]
└── categories.json  # Format: [{ id, name, color, created_at }]
```

**Vorteile:**
- ✅ Keine externe Abhängigkeiten (keine Datenbank nötig)
- ✅ Einfach zu sichern & zu exportieren
- ✅ Menschlich lesbar & editierbar
- ✅ Schnell (für bis ~1000 Aufgaben)

**Sicherung:**
- Manuell: `data/` Folder kopieren/backuppen
- Auto: Bei jeder Änderung automatisch gespeichert

---

## Wiederkehrende Aufgaben

Aufgaben können sich wiederholen (täglich, wöchentlich, monatlich):

1. **Neue Aufgabe erstellen** → Wiederholung: Wöchentlich
2. Aufgabe wird erledigt (Checkbox abhaken)
3. System erkennt: "Diese Aufgabe wiederholt sich"
4. Neue Instanz wird für nächste Woche erstellt
5. Alte Instanz bleibt als erledigt erhalten

**Beispiel:**
- Dienstag 18.12. - "Einkaufen" (Wöchentlich) ✅
- → Neue Aufgabe wird erstellt für Dienstag 25.12.

---

## Kategorien

### Erstellen
- Max. 5 Kategorien gleichzeitig
- Farbpicker für visuelle Unterscheidung
- Namen können doppelt nicht sein

### Löschen
- Mit 🗑️ Button
- Button wird deaktiviert bei 5 Kategorien
- Bestätigung erforderlich

### Zuordnung
- Pro Aufgabe max. 1 Kategorie (aktuell)
- Kann beim Erstellen oder Bearbeiten gesetzt werden
- Filter nach Kategorie möglich

---

## Keyboard Shortcuts (optional für Zukunft)

- **N** = Neue Aufgabe
- **S** = Suche fokussieren
- **Esc** = Modal schließen
- **Enter** = Speichern

*(Noch nicht implementiert)*

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "Aufgaben werden nicht gespeichert"
- Überprüfe: Existiert `data/` Folder?
- Überprüfe: Hat die App Schreibrechte?
- JSON-Datei nicht beschädigt? (lesbar mit Editor)

### "Kategorie kann nicht gelöscht werden"
- Überprüfe: Ist die Kategorie in einer Aufgabe verwendet?
- (Aktuell: Kategorien können jederzeit gelöscht werden)

### "App lädt sehr langsam"
- Überprüfe: Wie viele Aufgaben sind gespeichert? (>1000?)
- Streamlit: Browser-Cache leeren (Ctrl+F5)
- `.streamlit/config.toml`: `client.caching = true` aktivieren

---

## Entwicklung

### Tests ausführen
```bash
pytest testing/ -v
```

### Code-Struktur
- **Models**: Datenstrukturen, Validierung
- **Controllers**: Geschäftslogik, keine Streamlit-Imports
- **Views**: Nur Streamlit-Code, Komponenten, Pages
- **App**: Orchestrierung, minimal!

### Erweiterungen
- [ ] Datenbank-Support (SQLite, PostgreSQL)
- [ ] Cloud-Speicherung (Google Drive, Dropbox)
- [ ] Drag & Drop Sorting
- [ ] Collaborative Editing
- [ ] Dark Mode
- [ ] Export (PDF, CSV)

---

## Lizenz & Credits

- **Framework**: Streamlit
- **Architektur**: MVC (Model-View-Controller)
- **Sprache**: Python 3.12+
- **Autor**: [Dein Name]
- **Datum**: Dezember 2025

---

## Support & Dokumentation

- **ROADMAP.md**: Projekt-Plan & Phasen
- **UI-SPEC.md**: Detaillierte UI-Spezifikation
- **Code-Kommentare**: Ausführliche Docstrings in Python-Dateien

---

**Made with ❤️ using Python & Streamlit**
