"""Unit Tests für TODO-App mit vollständiger Coverage

ÜBERSICHT:
==========
Diese Datei enthält 113 umfassende Unit Tests für die TODO-App.
Sie testen alle kritischen Funktionen ohne externe Abhängigkeiten.

STRUKTUR:
- Fixtures: Wiederverwendbare Test-Komponenten
- TestCapitalizationFunctions: Text-Formatierung
- TestTodoModel: Todo-Datenstruktur
- TestCategoryModel: Kategorie-Datenstruktur
- TestTodoController: TODO-Geschäftslogik
- TestCategoryController: Kategorie-Geschäftslogik
- Integration Tests: Komplexe Workflows
- Edge Cases: Spezialfälle und Fehlerbehandlung

ANPASSUNGEN:
- Neue Tests hinzufügen: Kopiere eine TestXxx Klasse und ändere @test_xxx Methoden
- Coverage verbessern: Siehe "Missing" Spalte im Coverage Report
- Fehlerbehandlung testen: pytest.raises() verwenden (siehe Beispiele unten)
"""

import pytest
from datetime import date, timedelta, datetime
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import sys
import os

# Pfad-Setup: Erlaubt Imports aus Parent-Directory (models, controllers)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Todo, Category, TodoStatus, RecurrenceType, JSONStorage
from app.controllers import TodoController, CategoryController, capitalize_first_letter, capitalize_sentences


# ===== FIXTURES =====
# 
# ERKLÄRUNG: Fixtures sind wiederverwendbare Setup-Komponenten
# Sie werden automatisch vor jedem Test aufgerufen und bieten Test-Daten
#
# BEISPIEL: @pytest.fixture decorator erstellt eine Funktion, die pytest automatisch aufruft
#
# ANPASSUNGEN:
# - Neue Fixture hinzufügen: @pytest.fixture + def fixture_name(): return Mock()
# - Storage-Verhalten ändern: mock_storage.load_todos.return_value = [existing_todo]
#

@pytest.fixture
def mock_storage():
    """Mock JSONStorage für unabhängige Tests
    
    ERKLÄRUNG:
    - Mock() simuliert die JSONStorage Klasse
    - .return_value legt fest, was beim Aufrufen zurückkommt
    - Dadurch keine echten Dateien geschrieben/gelesen
    
    VERWENDUNG:
    test_create_todo_basic(todo_controller) -> erhält diese mock_storage automatisch
    
    ANPASSUNGEN:
    - Andere Return-Werte: mock_storage.load_todos.return_value = [pre_loaded_todo]
    - Exception auslösen: mock_storage.save_todos.side_effect = IOError("Datei nicht beschreibbar")
    """
    storage = Mock(spec=JSONStorage)
    storage.load_todos.return_value = []        # Simuliert: Keine Todos geladen
    storage.load_categories.return_value = []   # Simuliert: Keine Kategorien geladen
    return storage


@pytest.fixture
def todo_controller(mock_storage):
    """Erstelle TodoController mit Mock-Storage
    
    ERKLÄRUNG:
    - TodoController ist die Geschäftslogik-Klasse (controllers.py)
    - Verwendet mock_storage statt echte Dateioperationen
    - Damit sind Tests schnell und unabhängig
    
    VERWENDUNG:
    def test_example(todo_controller):
        todo = todo_controller.create_todo(title="Test")
    
    ANPASSUNGEN:
    - Vorinitialisiern mit Todos:
      mock_storage.load_todos.return_value = [pre_created_todo]
      controller = TodoController(storage=mock_storage)
    """
    controller = TodoController(storage=mock_storage)
    return controller


@pytest.fixture
def category_controller(mock_storage):
    """Erstelle CategoryController mit Mock-Storage
    
    ERKLÄRUNG:
    - CategoryController für Kategorie-Verwaltung
    - Funktioniert analog zu todo_controller
    
    VERWENDUNG:
    def test_example(category_controller):
        cat = category_controller.create_category(name="Work")
    """
    controller = CategoryController(storage=mock_storage)
    return controller


@pytest.fixture
def sample_todo():
    """Erstelle Sample Todo für wiederverwendbare Test-Daten
    
    ERKLÄRUNG:
    - Todo mit typischen Werten erstellen
    - Wird in mehreren Tests verwendet
    
    VERWENDUNG:
    def test_example(sample_todo):
        assert sample_todo.title == "Test Task"
    
    ANPASSUNGEN:
    - Andere Werte setzen: sample_todo.due_date = date(2025, 12, 31)
    - Neue Sample erstellen: @pytest.fixture def sample_todo_overdue(): ...
    """
    return Todo(
        title="Test Task",
        description="Test Description",
        due_date=date.today(),
        categories=["Test"]
    )


@pytest.fixture
def sample_category():
    """Erstelle Sample Category für Tests
    
    ERKLÄRUNG:
    - Kategorie mit Testdaten
    - Hilft beim Testen von Kategorie-Funktionen
    
    VERWENDUNG:
    def test_example(sample_category):
        assert sample_category.name == "Test Category"
    """
    return Category(name="Test Category", color="#FF6B6B")


# ===== HELPER FUNCTION TESTS =====
#
# ERKLÄRUNG: Diese Tests prüfen Text-Formatierungsfunktionen
# Sie sind in controllers.py definiert und werden überall verwendet
#
# DATEIEN: controllers.py, Zeilen 9-32
#
# ANPASSUNGEN:
# - Neue Sprache testen: test_capitalize_sentences_with_umlauts()
# - Edge Cases: test_capitalize_very_long_text()
#

class TestCapitalizationFunctions:
    """Tests für Kapitalisierungsfunktionen
    
    ERKLÄRUNG:
    - capitalize_first_letter(): Erstes Zeichen zu Großbuchstaben
    - capitalize_sentences(): Alle Sätze kapitalisieren (nach ". ")
    
    VERWENDUNG IN APP:
    - create_todo(title="hello") -> speichert "Hello"
    - update_todo() wendet die gleiche Kapitalisierung an
    
    TESTING-STRATEGIE:
    - Normal Cases: "hello" -> "Hello"
    - Edge Cases: "", "a", "already capitalized"
    - Fehler-Cases: None (in den Funktionen nicht möglich)
    """
    
    def test_capitalize_first_letter_with_lowercase(self):
        """Arrange: lowercase text
           Act: call capitalize_first_letter
           Assert: first letter is uppercase
           
        ERKLÄRUNG:
        - Testet die Standardfunktionalität
        - Input: "hello world" -> Output: "Hello world"
        
        ANPASSUNGEN:
        - Weitere Testfälle: "test" -> "Test", "a" -> "A"
        - Fehlerfall: "" (leerer String) -> siehe next test
        """
        # Arrange
        text = "hello world"
        
        # Act
        result = capitalize_first_letter(text)
        
        # Assert
        assert result == "Hello world"
    
    def test_capitalize_first_letter_with_empty_string(self):
        """Arrange: empty string
           Act: call capitalize_first_letter
           Assert: returns empty string"""
        # Arrange
        text = ""
        
        # Act
        result = capitalize_first_letter(text)
        
        # Assert
        assert result == ""
    
    def test_capitalize_first_letter_with_single_char(self):
        """Arrange: single character
           Act: call capitalize_first_letter
           Assert: returns uppercase character"""
        # Arrange
        text = "a"
        
        # Act
        result = capitalize_first_letter(text)
        
        # Assert
        assert result == "A"
    
    def test_capitalize_first_letter_already_capitalized(self):
        """Arrange: already capitalized text
           Act: call capitalize_first_letter
           Assert: remains capitalized"""
        # Arrange
        text = "Hello world"
        
        # Act
        result = capitalize_first_letter(text)
        
        # Assert
        assert result == "Hello world"
    
    def test_capitalize_sentences_single_sentence(self):
        """Arrange: single sentence
           Act: call capitalize_sentences
           Assert: first letter capitalized"""
        # Arrange
        text = "hello world"
        
        # Act
        result = capitalize_sentences(text)
        
        # Assert
        assert result == "Hello world"
    
    def test_capitalize_sentences_multiple_sentences(self):
        """Arrange: multiple sentences
           Act: call capitalize_sentences
           Assert: all sentences capitalized"""
        # Arrange
        text = "hello world. this is a test. another sentence"
        
        # Act
        result = capitalize_sentences(text)
        
        # Assert
        assert result == "Hello world. This is a test. Another sentence"
    
    def test_capitalize_sentences_with_empty_string(self):
        """Arrange: empty string
           Act: call capitalize_sentences
           Assert: returns empty string"""
        # Arrange
        text = ""
        
        # Act
        result = capitalize_sentences(text)
        
        # Assert
        assert result == ""


# ===== TODO MODEL TESTS =====
#
# ERKLÄRUNG: Diese Tests prüfen die Todo Dataclass aus models.py
# Sie testen die Datenstruktur, Validierung und Methoden
#
# DATEIEN: models.py, Zeilen 27-153 (Todo Klasse)
#
# KRITISCHE METHODEN ZUM TESTEN:
# - __post_init__(): Validierung beim Erstellen (Titel nicht leer, max 200 Zeichen, max 5 Kategorien)
# - mark_completed(): Status zu COMPLETED, completed_at setzen
# - mark_open(): Status zu OPEN, completed_at zurücksetzen
# - toggle_completion(): Wechsel zwischen OPEN und COMPLETED
# - is_overdue(): Prüfe ob Datum in der Vergangenheit
# - is_due_today(): Prüfe ob Datum heute
# - update(): Felder aktualisieren
# - should_create_next_recurrence(): Prüfe für wiederkehrende Aufgaben
# - get_next_due_date(): Berechne nächstes Datum
#
# ANPASSUNGEN:
# - Tests für neue Methoden hinzufügen
# - Validierungen testen (pytest.raises)
# - Datum-Logik mit Zeitzonen testen
#

class TestTodoModel:
    """Tests für Todo Dataclass
    
    ERKLÄRUNG:
    - Todo ist die Datenstruktur aus models.py
    - Speichert: title, description, status, due_date, categories, recurrence, etc.
    - Validiert automatisch im __post_init__
    
    VERWENDUNG IN APP:
    - TodoController.create_todo() erstellt Todo Instanzen
    - TodoController.update_todo() ändert Todo Felder
    - Daten werden in todos.json gespeichert
    
    TEST-COVERAGE:
    - Erstellung mit Validierung
    - Status-Änderungen (mark_completed, mark_open, toggle)
    - Datum-Checks (is_overdue, is_due_today, is_due_this_week)
    - Wiederholungs-Logik (should_create_next_recurrence, get_next_due_date)
    """
    
    def test_todo_creation_with_required_fields(self, sample_todo):
        """Arrange: create todo with required fields
           Act: verify todo attributes
           Assert: all fields set correctly
           
        ERKLÄRUNG:
        - Mindestanforderung: title (erforderlich)
        - Andere Felder: optional mit Defaults
        
        ANPASSUNGEN:
        - Weitere Required Fields: description="Muss angegeben sein"
        - Verschiedene Data Types testen: integer, dict, list
        
        HÄUFIGE FEHLER:
        - "Titel darf nicht leer sein" wenn title=""
        - TypeError wenn title=None statt ""
        """
        # Arrange
        title = "Test Task"
        
        # Act
        todo = Todo(title=title)
        
        # Assert
        assert todo.title == title
        assert todo.status == TodoStatus.OPEN
        assert todo.id is not None
        assert todo.created_at is not None
    
    def test_todo_creation_with_all_fields(self, sample_todo):
        """Arrange: create todo with all fields
           Act: access all fields
           Assert: all fields are set"""
        # Assert
        assert sample_todo.title == "Test Task"
        assert sample_todo.description == "Test Description"
        assert sample_todo.due_date == date.today()
        assert sample_todo.categories == ["Test"]
        assert sample_todo.status == TodoStatus.OPEN
    
    def test_todo_creation_fails_with_empty_title(self):
        """Arrange: try to create todo with empty title
           Act: call Todo constructor
           Assert: raises ValueError
           
        ERKLÄRUNG:
        - __post_init__ wirft ValueError wenn title leer ist
        - pytest.raises() catcht die Exception und prüft sie
        
        VERWENDUNG:
        with pytest.raises(ValueError, match="Titel darf nicht leer sein"):
            # Code, der Exception wirft
        
        ANPASSUNGEN:
        - Andere Exceptions testen: KeyError, TypeError, AttributeError
        - Match-Text ändern: match="Deine Error Message"
        - Multiple Exceptions: pytest.raises((ValueError, TypeError))
        
        CODE IN models.py ZEILEN 49-50:
        if not self.title or not self.title.strip():
            raise ValueError("Titel darf nicht leer sein")
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Titel darf nicht leer sein"):
            Todo(title="")
    
    def test_todo_creation_fails_with_whitespace_title(self):
        """Arrange: try to create todo with whitespace-only title
           Act: call Todo constructor
           Assert: raises ValueError"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Titel darf nicht leer sein"):
            Todo(title="   ")
    
    def test_todo_creation_fails_with_too_long_title(self):
        """Arrange: create todo with title > 200 chars
           Act: call Todo constructor
           Assert: raises ValueError"""
        # Arrange
        long_title = "a" * 201
        
        # Act & Assert
        with pytest.raises(ValueError, match="max. 200 Zeichen"):
            Todo(title=long_title)
    
    def test_todo_creation_fails_with_too_many_categories(self):
        """Arrange: create todo with > 5 categories
           Act: call Todo constructor
           Assert: raises ValueError"""
        # Arrange
        categories = ["cat1", "cat2", "cat3", "cat4", "cat5", "cat6"]
        
        # Act & Assert
        with pytest.raises(ValueError, match="Max. 5 Kategorien"):
            Todo(title="Test", categories=categories)
    
    def test_todo_mark_completed(self, sample_todo):
        """Arrange: open todo
           Act: call mark_completed
           Assert: status is COMPLETED and completed_at is set
           
        ERKLÄRUNG:
        - mark_completed() ändert Status zu COMPLETED
        - Setzt timestamp in completed_at (für Statistiken wichtig)
        
        VERWENDUNG IN APP:
        - Wenn User Checkbox anklickt: toggle_completion()
        - toggle_completion() ruft mark_completed() auf
        
        CODE IN models.py ZEILEN 112-115:
        def mark_completed(self) -> None:
            self.status = TodoStatus.COMPLETED
            self.completed_at = datetime.now()
            self.updated_at = datetime.now()
        
        ANPASSUNGEN:
        - Test dass updated_at sich ändert
        - Test dass completed_at nicht None ist
        - Test nach mark_open(): completed_at ist wieder None
        """
        # Arrange
        assert sample_todo.status == TodoStatus.OPEN
        
        # Act
        sample_todo.mark_completed()
        
        # Assert
        assert sample_todo.status == TodoStatus.COMPLETED
        assert sample_todo.completed_at is not None
    
    def test_todo_mark_open(self, sample_todo):
        """Arrange: completed todo
           Act: mark as open
           Assert: status is OPEN and completed_at is None"""
        # Arrange
        sample_todo.mark_completed()
        assert sample_todo.status == TodoStatus.COMPLETED
        
        # Act
        sample_todo.mark_open()
        
        # Assert
        assert sample_todo.status == TodoStatus.OPEN
        assert sample_todo.completed_at is None
    
    def test_todo_toggle_completion(self, sample_todo):
        """Arrange: open todo
           Act: toggle completion twice
           Assert: ends in original state"""
        # Arrange
        original_status = sample_todo.status
        
        # Act
        sample_todo.toggle_completion()
        first_toggle = sample_todo.status
        sample_todo.toggle_completion()
        second_toggle = sample_todo.status
        
        # Assert
        assert first_toggle == TodoStatus.COMPLETED
        assert second_toggle == original_status
    
    def test_todo_is_overdue(self):
        """Arrange: create overdue todo
           Act: call is_overdue
           Assert: returns True"""
        # Arrange
        past_date = date.today() - timedelta(days=1)
        todo = Todo(title="Test", due_date=past_date)
        
        # Act
        result = todo.is_overdue()
        
        # Assert
        assert result is True
    
    def test_todo_is_not_overdue_when_completed(self):
        """Arrange: create completed overdue todo
           Act: call is_overdue
           Assert: returns False"""
        # Arrange
        past_date = date.today() - timedelta(days=1)
        todo = Todo(title="Test", due_date=past_date, status=TodoStatus.COMPLETED)
        
        # Act
        result = todo.is_overdue()
        
        # Assert
        assert result is False
    
    def test_todo_is_overdue_without_due_date(self, sample_todo):
        """Arrange: create todo without due_date
           Act: call is_overdue
           Assert: returns False"""
        # Arrange
        todo = Todo(title="Test")
        
        # Act
        result = todo.is_overdue()
        
        # Assert
        assert result is False
    
    def test_todo_is_due_today(self):
        """Arrange: create todo due today
           Act: call is_due_today
           Assert: returns True"""
        # Arrange
        todo = Todo(title="Test", due_date=date.today())
        
        # Act
        result = todo.is_due_today()
        
        # Assert
        assert result is True
    
    def test_todo_is_not_due_today(self):
        """Arrange: create todo due tomorrow
           Act: call is_due_today
           Assert: returns False"""
        # Arrange
        tomorrow = date.today() + timedelta(days=1)
        todo = Todo(title="Test", due_date=tomorrow)
        
        # Act
        result = todo.is_due_today()
        
        # Assert
        assert result is False
    
    def test_todo_update(self, sample_todo):
        """Arrange: existing todo
           Act: call update with new values
           Assert: values are updated and updated_at changes"""
        # Arrange
        old_updated_at = sample_todo.updated_at
        
        # Act
        sample_todo.update(title="Updated Title", description="Updated Description")
        
        # Assert
        assert sample_todo.title == "Updated Title"
        assert sample_todo.description == "Updated Description"
        assert sample_todo.updated_at > old_updated_at
    
    def test_todo_should_create_next_recurrence_not_for_none(self, sample_todo):
        """Arrange: todo with NONE recurrence
           Act: call should_create_next_recurrence
           Assert: returns False"""
        # Arrange
        sample_todo.recurrence = RecurrenceType.NONE
        
        # Act
        result = sample_todo.should_create_next_recurrence()
        
        # Assert
        assert result is False
    
    def test_todo_should_create_next_recurrence_for_daily(self, sample_todo):
        """Arrange: completed daily todo
           Act: call should_create_next_recurrence
           Assert: returns True"""
        # Arrange
        sample_todo.mark_completed()
        sample_todo.recurrence = RecurrenceType.DAILY
        
        # Act
        result = sample_todo.should_create_next_recurrence()
        
        # Assert
        assert result is True
    
    def test_todo_get_next_due_date_daily(self, sample_todo):
        """Arrange: daily todo
           Act: call get_next_due_date
           Assert: returns date + 1 day"""
        # Arrange
        sample_todo.recurrence = RecurrenceType.DAILY
        sample_todo.due_date = date.today()
        
        # Act
        next_date = sample_todo.get_next_due_date()
        
        # Assert
        assert next_date == date.today() + timedelta(days=1)
    
    def test_todo_get_next_due_date_weekly(self, sample_todo):
        """Arrange: weekly todo
           Act: call get_next_due_date
           Assert: returns date + 7 days"""
        # Arrange
        today = date.today()
        # Verwende den 10. des Monats, um Monatsüberlauf zu vermeiden
        safe_date = date(today.year, today.month, 10)
        sample_todo.recurrence = RecurrenceType.WEEKLY
        sample_todo.due_date = safe_date
        
        # Act
        next_date = sample_todo.get_next_due_date()
        
        # Assert
        assert next_date == safe_date + timedelta(days=7)
    
    def test_todo_get_next_due_date_monthly(self, sample_todo):
        """Arrange: monthly todo on day 15
           Act: call get_next_due_date
           Assert: returns same day next month"""
        # Arrange
        today = date.today()
        sample_todo.due_date = date(today.year, today.month, 15)
        sample_todo.recurrence = RecurrenceType.MONTHLY
        
        # Act
        next_date = sample_todo.get_next_due_date()
        
        # Assert
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1
        assert next_date.month == next_month
        assert next_date.year == next_year
        assert next_date.day == 15


# ===== CATEGORY MODEL TESTS =====

class TestCategoryModel:
    """Tests für Category Dataclass"""
    
    def test_category_creation(self, sample_category):
        """Arrange: create category
           Act: access fields
           Assert: all fields set correctly"""
        # Assert
        assert sample_category.name == "Test Category"
        assert sample_category.color == "#FF6B6B"
        assert sample_category.id is not None
        assert sample_category.created_at is not None
    
    def test_category_creation_fails_with_empty_name(self):
        """Arrange: try to create category with empty name
           Act: call Category constructor
           Assert: raises ValueError"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Name darf nicht leer sein"):
            Category(name="")
    
    def test_category_creation_fails_with_long_name(self):
        """Arrange: try to create category with name > 50 chars
           Act: call Category constructor
           Assert: raises ValueError"""
        # Arrange
        long_name = "a" * 51
        
        # Act & Assert
        with pytest.raises(ValueError, match="max. 50 Zeichen"):
            Category(name=long_name)
    
    def test_category_creation_fails_with_invalid_color(self):
        """Arrange: try to create category with invalid color
           Act: call Category constructor
           Assert: raises ValueError"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Ungültige Hex-Farbe"):
            Category(name="Test", color="notacolor")
    
    def test_category_is_valid_hex_color(self):
        """Arrange: valid and invalid hex colors
           Act: call _is_valid_hex_color
           Assert: correct validation"""
        # Assert
        assert Category._is_valid_hex_color("#FF6B6B") is True
        assert Category._is_valid_hex_color("#000000") is True
        assert Category._is_valid_hex_color("#FFFFFF") is True
        assert Category._is_valid_hex_color("#FFF") is False
        assert Category._is_valid_hex_color("FF6B6B") is False
        assert Category._is_valid_hex_color("not_color") is False
    
    def test_category_equality(self):
        """Arrange: two categories with same ID
           Act: compare them
           Assert: they are equal"""
        # Arrange
        cat1 = Category(name="Test", color="#FF6B6B")
        cat2_id = cat1.id
        cat2 = Category(name="Different", color="#4ECDC4")
        cat2.id = cat2_id
        
        # Act & Assert
        assert cat1 == cat2
    
    def test_category_string_representation(self, sample_category):
        """Arrange: category
           Act: convert to string
           Assert: includes name with circle"""
        # Act
        result = str(sample_category)
        
        # Assert
        assert "Test Category" in result
        assert "●" in result


# ===== TODO CONTROLLER TESTS =====
#
# ERKLÄRUNG: Diese Tests prüfen die Geschäftslogik aus controllers.py
# TodoController macht: CRUD, Filter, Statistiken, Recurrence
#
# DATEIEN: controllers.py, Zeilen 40-289 (TodoController Klasse)
#
# HAUPTMETHODEN:
# - create_todo(): Neue Aufgabe, mit Kapitalisierung und Validierung
# - get_todos(): Alle Aufgaben zurückgeben
# - get_todo(id): Einzelne Aufgabe by ID
# - update_todo(id, **kwargs): Felder ändern (mit Validierung)
# - delete_todo(id): Aufgabe löschen
# - toggle_completion(id): Status wechseln
# - mark_completed/mark_open(id): Status direkt setzen
# - Filter-Methoden: get_open_todos, get_completed_todos, get_todos_by_category, etc.
# - search_todos(query): Titel + Beschreibung durchsuchen
# - get_stats(): Statistiken (total, open, completed, overdue)
# - handle_recurring_todos(): Neue Instanzen von wiederkehrenden Aufgaben
#
# ANPASSUNGEN:
# - Neue Filter-Methoden testen
# - Performance mit vielen Todos testen
# - Datenbank-Fehler simulieren (mit Mock)
#

class TestTodoController:
    """Tests für TodoController CRUD und Filterung
    
    ERKLÄRUNG:
    - TodoController ist die Geschäftslogik-Schicht
    - Verwendet Todo Modelle und JSONStorage
    - Macht Validierung, Transformation, Persistierung
    
    VERWENDUNG IN APP:
    - ui.py importiert TodoController
    - Alle UI-Aktionen gehen durch TodoController
    - Beispiel: st.button("Speichern") -> todo_controller.create_todo()
    
    TEST-STRATEGIE:
    - CRUD: Create, Read, Update, Delete testen
    - Fehlerbehandlung: ValueError bei ungültigen Daten
    - Mock Storage: Keine echten Dateien
    - Isolation: Jeder Test ist unabhängig
    
    HÄUFIGE FEHLER:
    - Vergessen todo_controller.storage.save_todos.assert_called() zu prüfen
    - Keine Kapitalisierung in Tests berücksichtigen
    - Mock Storage nicht richtig initialisieren
    """
    
    def test_create_todo_basic(self, todo_controller):
        """Arrange: controller ready
           Act: create todo with title
           Assert: todo created and saved
           
        ERKLÄRUNG:
        - Test für grundlegende create_todo Funktion
        - Prüft: Rückgabewert, Liste, Storage aufgerufen
        
        VERWENDUNG:
        - Basis-Test für alle create_todo Varianten
        
        CODE IN controllers.py ZEILEN 68-82:
        def create_todo(self, title: str, ...):
            if not title or not title.strip():
                raise ValueError("Titel darf nicht leer sein")
            title = capitalize_first_letter(title.strip())
            # ... erstelle Todo
            self._todos.append(todo)
            self._save_todos()  <- Das mocken wir!
        
        ANPASSUNGEN:
        - Test mit verschiedenen Titeln: "HELLO", "123 Test"
        - Test dass assert_called genau richtig aufgerufen wird
        """
        # Act
        todo = todo_controller.create_todo(title="Test Task")
        
        # Assert
        assert todo.title == "Test Task"
        assert todo.status == TodoStatus.OPEN
        assert len(todo_controller.get_todos()) == 1
        # Prüfe dass Storage save_todos aufgerufen wurde
        todo_controller.storage.save_todos.assert_called()
    
    def test_create_todo_with_all_fields(self, todo_controller):
        """Arrange: controller ready with date
           Act: create todo with all fields
           Assert: todo created with all fields"""
        # Arrange
        test_date = date.today()
        
        # Act
        todo = todo_controller.create_todo(
            title="Test",
            description="Description",
            due_date=test_date,
            categories=["Work"],
            recurrence=RecurrenceType.DAILY
        )
        
        # Assert
        assert todo.title == "Test"
        assert todo.description == "Description"
        assert todo.due_date == test_date
        assert todo.categories == ["Work"]
        assert todo.recurrence == RecurrenceType.DAILY
    
    def test_create_todo_fails_with_empty_title(self, todo_controller):
        """Arrange: controller ready
           Act: try to create todo with empty title
           Assert: raises ValueError"""
        # Act & Assert
        with pytest.raises(ValueError, match="Titel darf nicht leer sein"):
            todo_controller.create_todo(title="")
    
    def test_create_todo_fails_with_whitespace_title(self, todo_controller):
        """Arrange: controller ready
           Act: try to create todo with whitespace title
           Assert: raises ValueError"""
        # Act & Assert
        with pytest.raises(ValueError, match="Titel darf nicht leer sein"):
            todo_controller.create_todo(title="   ")
    
    def test_create_todo_fails_with_too_many_categories(self, todo_controller):
        """Arrange: controller ready
           Act: create todo with 6 categories
           Assert: raises ValueError"""
        # Arrange
        categories = ["cat1", "cat2", "cat3", "cat4", "cat5", "cat6"]
        
        # Act & Assert
        with pytest.raises(ValueError, match="Max. 5 Kategorien"):
            todo_controller.create_todo(title="Test", categories=categories)
    
    def test_create_todo_capitalizes_title(self, todo_controller):
        """Arrange: controller ready
           Act: create todo with lowercase title
           Assert: title is capitalized"""
        # Act
        todo = todo_controller.create_todo(title="hello world")
        
        # Assert
        assert todo.title == "Hello world"
    
    def test_create_todo_capitalizes_description(self, todo_controller):
        """Arrange: controller ready
           Act: create todo with lowercase description
           Assert: description is capitalized"""
        # Act
        todo = todo_controller.create_todo(
            title="Test",
            description="hello world. this is a test"
        )
        
        # Assert
        assert todo.description == "Hello world. This is a test"
    
    def test_get_todos(self, todo_controller):
        """Arrange: create multiple todos
           Act: call get_todos
           Assert: returns all todos"""
        # Arrange
        todo1 = todo_controller.create_todo(title="Task 1")
        todo2 = todo_controller.create_todo(title="Task 2")
        
        # Act
        todos = todo_controller.get_todos()
        
        # Assert
        assert len(todos) == 2
        assert todo1 in todos
        assert todo2 in todos
    
    def test_get_todo_by_id(self, todo_controller):
        """Arrange: create todo
           Act: get todo by ID
           Assert: returns correct todo"""
        # Arrange
        created_todo = todo_controller.create_todo(title="Test Task")
        
        # Act
        found_todo = todo_controller.get_todo(created_todo.id)
        
        # Assert
        assert found_todo == created_todo
        assert found_todo.title == "Test Task"
    
    def test_get_todo_returns_none_for_invalid_id(self, todo_controller):
        """Arrange: controller ready
           Act: get todo with invalid ID
           Assert: returns None"""
        # Act
        result = todo_controller.get_todo("invalid-id")
        
        # Assert
        assert result is None
    
    def test_update_todo_title(self, todo_controller):
        """Arrange: create todo
           Act: update title
           Assert: title updated and saved
           
        ERKLÄRUNG:
        - Test für update_todo mit title Parameter
        - Prüft: title geändert, in Liste, Storage aufgerufen
        
        VERWENDUNG IN APP:
        - User öffnet Edit-Modal
        - Ändert Titel
        - Klickt "Speichern" -> update_todo wird aufgerufen
        
        CODE IN controllers.py ZEILEN 112-123:
        def update_todo(self, todo_id: str, **kwargs) -> Optional[Todo]:
            todo = self.get_todo(todo_id)
            if not todo:
                return None
            if "title" in kwargs and kwargs["title"]:
                if not kwargs["title"].strip():
                    raise ValueError("Titel darf nicht leer sein")
                kwargs["title"] = capitalize_first_letter(...)
            # ... update todo
            self._save_todos()
            return todo
        
        WICHTIG:
        - Kapitalisierung wird angewendet: "hello" -> "Hello"
        - Validierung: leere Titel wirken ValueError
        
        ANPASSUNGEN:
        - Test mehrere Felder gleichzeitig ändern
        - Test dass ID nicht ändert
        - Test dass updated_at sich ändert
        """
        # Arrange
        todo = todo_controller.create_todo(title="Original")
        
        # Act
        updated = todo_controller.update_todo(todo.id, title="Updated")
        
        # Assert
        assert updated.title == "Updated"
        assert todo_controller.get_todo(todo.id).title == "Updated"
    
    def test_update_todo_fails_with_empty_title(self, todo_controller):
        """Arrange: create todo
           Act: try to update with whitespace title
           Assert: raises ValueError"""
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Titel darf nicht leer sein"):
            todo_controller.update_todo(todo.id, title="   ")
    
    def test_update_todo_returns_none_for_invalid_id(self, todo_controller):
        """Arrange: controller ready
           Act: update non-existent todo
           Assert: returns None"""
        # Act
        result = todo_controller.update_todo("invalid-id", title="Updated")
        
        # Assert
        assert result is None
    
    def test_update_todo_capitalizes_title(self, todo_controller):
        """Arrange: create todo
           Act: update with lowercase title
           Assert: title capitalized"""
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        
        # Act
        updated = todo_controller.update_todo(todo.id, title="updated title")
        
        # Assert
        assert updated.title == "Updated title"
    
    def test_delete_todo(self, todo_controller):
        """Arrange: create todo
           Act: delete it
           Assert: todo removed and saved
           
        ERKLÄRUNG:
        - Test für delete_todo Funktion
        - Prüft: Rückgabewert True, Liste verkleinert, Storage aufgerufen
        
        VERWENDUNG IN APP:
        - Wenn User Löschen-Button klickt
        - Bestätigung mit ✓/✗ Buttons
        
        CODE IN controllers.py ZEILEN 127-132:
        def delete_todo(self, todo_id: str) -> bool:
            todo = self.get_todo(todo_id)
            if not todo:
                return False
            self._todos.remove(todo)
            self._save_todos()
            return True
        
        ANPASSUNGEN:
        - Test dass nicht-existierende ID False zurückgibt
        - Test dass mehrere Todos nur das richtige löscht
        - Test mit verschiedenen Todo-Status (OPEN, COMPLETED)
        """
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        assert len(todo_controller.get_todos()) == 1
        
        # Act
        result = todo_controller.delete_todo(todo.id)
        
        # Assert
        assert result is True
        assert len(todo_controller.get_todos()) == 0
        todo_controller.storage.save_todos.assert_called()
    
    def test_delete_todo_returns_false_for_invalid_id(self, todo_controller):
        """Arrange: controller ready
           Act: delete non-existent todo
           Assert: returns False"""
        # Act
        result = todo_controller.delete_todo("invalid-id")
        
        # Assert
        assert result is False
    
    def test_toggle_completion_open_to_completed(self, todo_controller):
        """Arrange: open todo
           Act: toggle completion
           Assert: status is COMPLETED
           
        ERKLÄRUNG:
        - Test für toggle_completion Funktion
        - Wechselt Status: OPEN -> COMPLETED oder COMPLETED -> OPEN
        
        VERWENDUNG IN APP:
        - User klickt auf Checkbox (☐ oder ☑️)
        - Toggle wird aufgerufen
        
        CODE IN controllers.py ZEILEN 143-151:
        def toggle_completion(self, todo_id: str) -> Optional[Todo]:
            todo = self.get_todo(todo_id)
            if not todo:
                return None
            todo.toggle_completion()
            self._save_todos()
            return todo
        
        ANPASSUNGEN:
        - Auch completed_at prüfen
        - updated_at prüfen (sollte sich ändern)
        - Mehrfaches Toggle testen (OPEN -> COMPLETED -> OPEN)
        """
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        
        # Act
        updated = todo_controller.toggle_completion(todo.id)
        
        # Assert
        assert updated.status == TodoStatus.COMPLETED
        assert updated.completed_at is not None
    
    def test_toggle_completion_completed_to_open(self, todo_controller):
        """Arrange: completed todo
           Act: toggle completion
           Assert: status is OPEN"""
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        todo_controller.toggle_completion(todo.id)
        
        # Act
        updated = todo_controller.toggle_completion(todo.id)
        
        # Assert
        assert updated.status == TodoStatus.OPEN
        assert updated.completed_at is None
    
    def test_mark_completed(self, todo_controller):
        """Arrange: open todo
           Act: mark as completed
           Assert: status is COMPLETED"""
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        
        # Act
        updated = todo_controller.mark_completed(todo.id)
        
        # Assert
        assert updated.status == TodoStatus.COMPLETED
    
    def test_mark_open(self, todo_controller):
        """Arrange: completed todo
           Act: mark as open
           Assert: status is OPEN"""
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        todo_controller.mark_completed(todo.id)
        
        # Act
        updated = todo_controller.mark_open(todo.id)
        
        # Assert
        assert updated.status == TodoStatus.OPEN
    
    def test_get_todos_by_status_open(self, todo_controller):
        """Arrange: create open and completed todos
           Act: get todos by open status
           Assert: returns only open todos"""
        # Arrange
        todo1 = todo_controller.create_todo(title="Task 1")
        todo2 = todo_controller.create_todo(title="Task 2")
        todo_controller.toggle_completion(todo2.id)
        
        # Act
        open_todos = todo_controller.get_todos_by_status(TodoStatus.OPEN)
        
        # Assert
        assert len(open_todos) == 1
        assert open_todos[0] == todo1
    
    def test_get_open_todos(self, todo_controller):
        """Arrange: create open and completed todos
           Act: get open todos
           Assert: returns only open todos"""
        # Arrange
        todo1 = todo_controller.create_todo(title="Task 1")
        todo2 = todo_controller.create_todo(title="Task 2")
        todo_controller.toggle_completion(todo2.id)
        
        # Act
        open_todos = todo_controller.get_open_todos()
        
        # Assert
        assert len(open_todos) == 1
        assert open_todos[0] == todo1
    
    def test_get_completed_todos(self, todo_controller):
        """Arrange: create open and completed todos
           Act: get completed todos
           Assert: returns only completed todos"""
        # Arrange
        todo1 = todo_controller.create_todo(title="Task 1")
        todo2 = todo_controller.create_todo(title="Task 2")
        todo_controller.toggle_completion(todo2.id)
        
        # Act
        completed_todos = todo_controller.get_completed_todos()
        
        # Assert
        assert len(completed_todos) == 1
        assert completed_todos[0] == todo2
    
    def test_get_todos_by_category(self, todo_controller):
        """Arrange: create todos with different categories
           Act: get todos by category
           Assert: returns only todos with that category"""
        # Arrange
        todo1 = todo_controller.create_todo(title="Task 1", categories=["Work"])
        todo2 = todo_controller.create_todo(title="Task 2", categories=["Personal"])
        
        # Act
        work_todos = todo_controller.get_todos_by_category("Work")
        
        # Assert
        assert len(work_todos) == 1
        assert work_todos[0] == todo1
    
    def test_filter_todos_by_status(self, todo_controller):
        """Arrange: create todos with mixed status
           Act: filter by status
           Assert: returns correct todos"""
        # Arrange
        todo1 = todo_controller.create_todo(title="Task 1")
        todo2 = todo_controller.create_todo(title="Task 2")
        todo_controller.toggle_completion(todo2.id)
        
        # Act
        filtered = todo_controller.filter_todos(status=TodoStatus.COMPLETED)
        
        # Assert
        assert len(filtered) == 1
        assert filtered[0] == todo2
    
    def test_filter_todos_by_category(self, todo_controller):
        """Arrange: create todos with different categories
           Act: filter by category
           Assert: returns correct todos"""
        # Arrange
        todo1 = todo_controller.create_todo(title="Task 1", categories=["Work"])
        todo2 = todo_controller.create_todo(title="Task 2", categories=["Personal"])
        
        # Act
        filtered = todo_controller.filter_todos(category="Work")
        
        # Assert
        assert len(filtered) == 1
        assert filtered[0] == todo1
    
    def test_filter_todos_by_search_query(self, todo_controller):
        """Arrange: create todos with different titles
           Act: filter by search query
           Assert: returns matching todos
           
        ERKLÄRUNG:
        - Test für search_todos / filter_todos mit search_query
        - Durchsucht Titel und Beschreibung
        - Case-insensitive
        
        VERWENDUNG IN APP:
        - User gibt Suchtext in Filter-Sidebar ein
        - Ergebnisse werden sofort gefiltert
        
        CODE IN controllers.py ZEILEN 198-210:
        def filter_todos(self, search_query: Optional[str] = None) -> List[Todo]:
            result = self._todos.copy()
            if search_query:
                query = search_query.lower().strip()
                result = [
                    t for t in result
                    if query in t.title.lower() or query in t.description.lower()
                ]
            return result
        
        WICHTIG:
        - Groß-/Kleinschreibung spielt keine Rolle
        - Sucht in title UND description
        - Leere query = alle Todos (oder keine, siehe Code)
        
        ANPASSUNGEN:
        - Test mit Description durchsuchen
        - Test mit Spezialzeichen: "test@#$"
        - Test mit Wildcards (falls später implementiert)
        - Test Performance mit 1000 Todos
        """
        # Arrange
        todo1 = todo_controller.create_todo(title="Buy groceries")
        todo2 = todo_controller.create_todo(title="Write report")
        
        # Act
        filtered = todo_controller.filter_todos(search_query="groceries")
        
        # Assert
        assert len(filtered) == 1
        assert filtered[0] == todo1
    
    def test_search_todos(self, todo_controller):
        """Arrange: create todos with different titles and descriptions
           Act: search todos
           Assert: returns matching todos"""
        # Arrange
        todo1 = todo_controller.create_todo(
            title="Task 1",
            description="Buy groceries at store"
        )
        todo2 = todo_controller.create_todo(
            title="Task 2",
            description="Write documentation"
        )
        
        # Act
        results = todo_controller.search_todos("groceries")
        
        # Assert
        assert len(results) == 1
        assert results[0] == todo1
    
    def test_get_overdue_todos(self, todo_controller):
        """Arrange: create overdue and future todos
           Act: get overdue todos
           Assert: returns only overdue todos"""
        # Arrange
        past_date = date.today() - timedelta(days=1)
        future_date = date.today() + timedelta(days=1)
        
        todo1 = todo_controller.create_todo(title="Overdue", due_date=past_date)
        todo2 = todo_controller.create_todo(title="Future", due_date=future_date)
        
        # Act
        overdue = todo_controller.get_overdue_todos()
        
        # Assert
        assert len(overdue) == 1
        assert overdue[0] == todo1
    
    def test_get_due_today_todos(self, todo_controller):
        """Arrange: create todos with different due dates
           Act: get todos due today
           Assert: returns only today's todos"""
        # Arrange
        todo1 = todo_controller.create_todo(title="Today", due_date=date.today())
        todo2 = todo_controller.create_todo(title="Tomorrow", due_date=date.today() + timedelta(days=1))
        
        # Act
        today_todos = todo_controller.get_due_today_todos()
        
        # Assert
        assert len(today_todos) == 1
        assert today_todos[0] == todo1
    
    def test_get_stats(self, todo_controller):
        """Arrange: create todos with mixed status
           Act: get stats
           Assert: stats are correct"""
        # Arrange
        todo_controller.create_todo(title="Task 1")
        todo_controller.create_todo(title="Task 2")
        todo2 = todo_controller.create_todo(title="Task 3")
        todo_controller.toggle_completion(todo2.id)
        
        # Act
        stats = todo_controller.get_stats()
        
        # Assert
        assert stats["total"] == 3
        assert stats["open"] == 2
        assert stats["completed"] == 1
    
    def test_handle_recurring_todos_daily(self, todo_controller):
        """Arrange: create completed daily todo
           Act: handle recurrence
           Assert: new todo created with next date
           
        ERKLÄRUNG:
        - Test für wiederkehrende Aufgaben (Recurrence)
        - Wenn tägliche Aufgabe erledigt, neue Instanz für morgen
        
        VERWENDUNG IN APP:
        - Aufgabe mit Wiederholung erstellen
        - User abhaken (mark_completed)
        - System erkennt Recurrence und erstellt neue für nächsten Zeitraum
        
        CODE IN controllers.py ZEILEN 253-275:
        def handle_recurring_todos(self) -> List[Todo]:
            created = []
            for todo in self._todos:
                if not todo.should_create_next_recurrence():
                    continue
                next_due_date = todo.get_next_due_date()
                if not next_due_date:
                    continue
                new_todo = Todo(
                    title=todo.title,
                    description=todo.description,
                    due_date=next_due_date,
                    categories=todo.categories.copy(),
                    recurrence=todo.recurrence,
                    ...
                )
                self._todos.append(new_todo)
                created.append(new_todo)
            if created:
                self._save_todos()
            return created
        
        WICHTIG:
        - get_next_due_date() rechnet das Datum
        - daily: +1 Tag
        - weekly: +7 Tage
        - monthly: +1 Monat (same day)
        
        ANPASSUNGEN:
        - Test mit custom recurrence_interval (z.B. alle 2 Tage)
        - Test mit recurrence_end_date (wann stoppt es?)
        - Test mehrere Recurrences gleichzeitig
        """
        # Arrange
        todo = todo_controller.create_todo(
            title="Daily Task",
            due_date=date.today(),
            recurrence=RecurrenceType.DAILY
        )
        todo_controller.toggle_completion(todo.id)
        
        # Act
        created = todo_controller.handle_recurring_todos()
        
        # Assert
        assert len(created) == 1
        assert created[0].due_date == date.today() + timedelta(days=1)
        assert created[0].title == "Daily Task"


# ===== CATEGORY CONTROLLER TESTS =====
#
# ERKLÄRUNG: Tests für Kategorie-Verwaltung (Controllers.py)
#
# HAUPTMETHODEN:
# - create_category(): Neue Kategorie mit auto-Farbe
# - get_categories(): Alle Kategorien
# - update_category(): Name/Farbe ändern
# - delete_category(): Kategorie löschen
# - get_category_by_name(): Nach Name suchen (wichtig!)
# - is_category_used(): Prüft ob in Todos verwendet
#
# WICHTIG:
# - Max. 5 Kategorien total
# - Farben auto-zugewiesen aus Palette
# - Namen müssen eindeutig sein
# - Kapitalisierung wird angewendet
#

class TestCategoryController:
    """Tests für CategoryController CRUD
    
    ERKLÄRUNG:
    - CategoryController verwaltet Kategorien
    - Jede Kategorie hat Name, Farbe, ID
    - Wird von TodoController verwendet
    
    VERWENDUNG IN APP:
    - Kategorien-Sidebar: Neue Kategorie hinzufügen/ändern/löschen
    - Todos: Kategorie auswählen beim Erstellen
    - Filter: Nach Kategorie filtern
    
    TEST-STRATEGIE:
    - CRUD: Erstellen, Lesen, Ändern, Löschen
    - Validierung: Max 5, eindeutige Namen
    - Auto-Farben: Palette-Zyklus
    - Kapitalisierung: "work" -> "Work"
    """
    
    def test_create_category_basic(self, category_controller):
        """Arrange: controller ready
           Act: create category
           Assert: category created and saved
           
        ERKLÄRUNG:
        - Neue Kategorie mit Auto-Farb-Zuweisung
        
        CODE IN controllers.py ZEILEN 306-325:
        def create_category(self, name: str, color: str = None) -> Category:
            if len(self._categories) >= self.MAX_CATEGORIES:
                raise ValueError(f"Max. {self.MAX_CATEGORIES} Kategorien...")
            if self.category_exists(name):
                raise ValueError(f"Kategorie '{name}' existiert bereits")
            name = capitalize_first_letter(name.strip())
            if color is None:
                color_palette = ["#FF6B6B", "#4ECDC4", ...]
                color = color_palette[len(self._categories) % len(color_palette)]
            category = Category(name=name, color=color)
            self._categories.append(category)
            self._save_categories()
            return category
        
        ANPASSUNGEN:
        - Test auto-Farbzuweisung der Reihe nach
        - Test dass Namen eindeutig sein müssen
        - Test dass Max 5 Kategorien erzwingt
        """
        # Act
        category = category_controller.create_category(name="Work")
        
        # Assert
        assert category.name == "Work"
        assert category.color is not None
        assert len(category_controller.get_categories()) == 1
        category_controller.storage.save_categories.assert_called()
    
    def test_create_category_fails_with_empty_name(self, category_controller):
        """Arrange: controller ready
           Act: try to create category with empty name
           Assert: raises ValueError"""
        # Act & Assert
        with pytest.raises(ValueError):
            category_controller.create_category(name="")
    
    def test_create_category_fails_with_duplicate_name(self, category_controller):
        """Arrange: controller ready
           Act: create two categories with same name
           Assert: second creation raises ValueError"""
        # Arrange
        category_controller.create_category(name="Work")
        
        # Act & Assert
        with pytest.raises(ValueError, match="existiert bereits"):
            category_controller.create_category(name="Work")
    
    def test_create_category_fails_with_max_categories(self, category_controller):
        """Arrange: create max categories
           Act: try to create one more
           Assert: raises ValueError"""
        # Arrange
        for i in range(5):
            category_controller.create_category(name=f"Cat{i}")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Max."):
            category_controller.create_category(name="Cat6")
    
    def test_create_category_auto_assigns_color(self, category_controller):
        """Arrange: controller ready
           Act: create categories without color
           Assert: each gets a color from palette"""
        # Act
        cat1 = category_controller.create_category(name="Cat1")
        cat2 = category_controller.create_category(name="Cat2")
        cat3 = category_controller.create_category(name="Cat3")
        
        # Assert
        assert cat1.color == "#FF6B6B"
        assert cat2.color == "#4ECDC4"
        assert cat3.color == "#45B7D1"
    
    def test_create_category_capitalizes_name(self, category_controller):
        """Arrange: controller ready
           Act: create category with lowercase name
           Assert: name is capitalized"""
        # Act
        category = category_controller.create_category(name="work")
        
        # Assert
        assert category.name == "Work"
    
    def test_get_categories(self, category_controller):
        """Arrange: create multiple categories
           Act: get all categories
           Assert: returns all categories"""
        # Arrange
        cat1 = category_controller.create_category(name="Work")
        cat2 = category_controller.create_category(name="Personal")
        
        # Act
        categories = category_controller.get_categories()
        
        # Assert
        assert len(categories) == 2
        assert cat1 in categories
        assert cat2 in categories
    
    def test_get_category_by_id(self, category_controller):
        """Arrange: create category
           Act: get by ID
           Assert: returns correct category"""
        # Arrange
        created = category_controller.create_category(name="Work")
        
        # Act
        found = category_controller.get_category(created.id)
        
        # Assert
        assert found == created
    
    def test_get_category_by_name(self, category_controller):
        """Arrange: create category
           Act: get by name
           Assert: returns correct category"""
        # Arrange
        created = category_controller.create_category(name="Work")
        
        # Act
        found = category_controller.get_category_by_name("Work")
        
        # Assert
        assert found == created
    
    def test_update_category_name(self, category_controller):
        """Arrange: create category
           Act: update name
           Assert: name updated and saved"""
        # Arrange
        category = category_controller.create_category(name="Work")
        
        # Act
        updated = category_controller.update_category(category.id, name="Job")
        
        # Assert
        assert updated.name == "Job"
    
    def test_update_category_capitalizes_name(self, category_controller):
        """Arrange: create category
           Act: update with lowercase name
           Assert: name is capitalized"""
        # Arrange
        category = category_controller.create_category(name="Work")
        
        # Act
        updated = category_controller.update_category(category.id, name="job")
        
        # Assert
        assert updated.name == "Job"
    
    def test_update_category_fails_with_duplicate_name(self, category_controller):
        """Arrange: create two categories
           Act: try to rename first to second's name
           Assert: raises ValueError"""
        # Arrange
        cat1 = category_controller.create_category(name="Work")
        category_controller.create_category(name="Personal")
        
        # Act & Assert
        with pytest.raises(ValueError, match="existiert bereits"):
            category_controller.update_category(cat1.id, name="Personal")
    
    def test_update_category_color(self, category_controller):
        """Arrange: create category
           Act: update color
           Assert: color updated"""
        # Arrange
        category = category_controller.create_category(name="Work")
        
        # Act
        updated = category_controller.update_category(category.id, color="#000000")
        
        # Assert
        assert updated.color == "#000000"
    
    def test_delete_category(self, category_controller):
        """Arrange: create category
           Act: delete it
           Assert: category removed and saved"""
        # Arrange
        category = category_controller.create_category(name="Work")
        
        # Act
        result = category_controller.delete_category(category.id)
        
        # Assert
        assert result is True
        assert len(category_controller.get_categories()) == 0
    
    def test_validate_max_categories(self, category_controller):
        """Arrange: create max categories
           Act: validate
           Assert: returns True"""
        # Arrange
        for i in range(5):
            category_controller.create_category(name=f"Cat{i}")
        
        # Act
        result = category_controller.validate_max_categories()
        
        # Assert
        assert result is True
    
    def test_category_exists(self, category_controller):
        """Arrange: create category
           Act: check if exists
           Assert: returns True"""
        # Arrange
        category_controller.create_category(name="Work")
        
        # Act
        result = category_controller.category_exists("Work")
        
        # Assert
        assert result is True
    
    def test_get_color_for_category(self, category_controller):
        """Arrange: create category
           Act: get color
           Assert: returns color"""
        # Arrange
        category = category_controller.create_category(name="Work")
        
        # Act
        color = category_controller.get_color_for_category(category.id)
        
        # Assert
        assert color == category.color


# ===== INTEGRATION TESTS =====
#
# ERKLÄRUNG: Tests die mehrere Komponenten zusammen testen
# Nicht einzelne Funktionen, sondern ganze Workflows
#
# BEISPIELE:
# - Kategorie erstellen, dann Todo mit dieser Kategorie
# - Todo erstellen, bearbeiten, erledigen, löschen
# - Mehrere Filter kombinieren
#
# ANPASSUNGEN:
# - Realistischere Szenarien hinzufügen
# - Performance-Tests mit vielen Todos
# - Fehler-Szenarien testen (z.B. Storage-Fehler)
#

class TestIntegration:
    """Integration tests für Controllers zusammen
    
    ERKLÄRUNG:
    - Testen wie Components zusammenarbeiten
    - Nicht einzelne Methoden, sondern Workflows
    - Realistischere Szenarien
    
    VERWENDUNG:
    - Verifica dass App insgesamt funktioniert
    - Finde Bugs die nur bei Kombination auftauchen
    
    BEISPIEL-WORKFLOW:
    1. Kategorie erstellen
    2. Todo mit Kategorie erstellen
    3. Todo nach Kategorie filtern
    4. Todo bearbeiten
    5. Todo löschen
    
    ANPASSUNGEN:
    - Komplexere Workflows hinzufügen
    - Error-Cases testen
    - Race-Conditions prüfen
    """
    
    def test_create_todo_and_category_workflow(self, todo_controller, category_controller):
        """Arrange: both controllers ready
           Act: create category then todo with category
           Assert: todo linked to category
           
        ERKLÄRUNG:
        - Todo mit Kategorie erstellen
        - Prüft dass Beziehung stimmt
        
        VERWENDUNG:
        - User erstellt Kategorie "Arbeit"
        - Erstellt Todo in dieser Kategorie
        - Filtered nach Kategorie
        
        ANPASSUNGEN:
        - Test dass Kategorie nicht gelöscht wird wenn Todo sie noch braucht
        - Test mehrere Todos in gleicher Kategorie
        - Test Kategorie umbenennen (auch Todos updaten?)
        """
        # Arrange
        category = category_controller.create_category(name="Work")
        
        # Act
        todo = todo_controller.create_todo(
            title="Work Task",
            categories=[category.name]
        )
        
        # Assert
        assert category.name in todo.categories
        assert todo_controller.get_todos_by_category(category.name)[0] == todo
    
    def test_complete_todo_workflow(self, todo_controller):
        """Arrange: controller ready
           Act: create, update, complete, and delete todo
           Assert: all operations succeed"""
        # Act - Create
        todo = todo_controller.create_todo(title="Complete Workflow")
        original_id = todo.id
        
        # Act - Update
        todo_controller.update_todo(original_id, description="Added description")
        updated = todo_controller.get_todo(original_id)
        assert updated.description == "Added description"
        
        # Act - Complete
        todo_controller.toggle_completion(original_id)
        completed = todo_controller.get_todo(original_id)
        assert completed.status == TodoStatus.COMPLETED
        
        # Act - Delete
        result = todo_controller.delete_todo(original_id)
        assert result is True
        assert todo_controller.get_todo(original_id) is None


# ===== ADDITIONAL EDGE CASE TESTS FOR COVERAGE =====

class TestTodoEdgeCases:
    """Edge case tests für zusätzliche Coverage"""
    
    def test_todo_is_due_this_week(self):
        """Arrange: create todo due this week
           Act: call is_due_this_week
           Assert: returns True"""
        # Arrange
        today = date.today()
        days_until_sunday = 6 - today.weekday()
        mid_week = today + timedelta(days=1)
        todo = Todo(title="Test", due_date=mid_week)
        
        # Act
        result = todo.is_due_this_week()
        
        # Assert
        assert result is True
    
    def test_todo_is_not_due_this_week(self):
        """Arrange: create todo due next week
           Act: call is_due_this_week
           Assert: returns False"""
        # Arrange
        today = date.today()
        days_until_sunday = 6 - today.weekday()
        next_week = today + timedelta(days=days_until_sunday + 1)
        todo = Todo(title="Test", due_date=next_week)
        
        # Act
        result = todo.is_due_this_week()
        
        # Assert
        assert result is False
    
    def test_todo_get_next_due_date_none(self):
        """Arrange: todo with NONE recurrence
           Act: get next due date
           Assert: returns None"""
        # Arrange
        todo = Todo(title="Test", recurrence=RecurrenceType.NONE)
        
        # Act
        result = todo.get_next_due_date()
        
        # Assert
        assert result is None
    
    def test_todo_get_next_due_date_no_due_date(self):
        """Arrange: todo without due_date
           Act: get next due date
           Assert: returns None"""
        # Arrange
        todo = Todo(title="Test", recurrence=RecurrenceType.DAILY)
        
        # Act
        result = todo.get_next_due_date()
        
        # Assert
        assert result is None
    
    def test_todo_update_preserves_id(self):
        """Arrange: create todo
           Act: update fields
           Assert: ID doesn't change"""
        # Arrange
        todo = Todo(title="Test")
        original_id = todo.id
        
        # Act
        todo.update(title="Updated", description="Desc")
        
        # Assert
        assert todo.id == original_id
    
    def test_todo_mark_open_clears_completed_at(self):
        """Arrange: completed todo
           Act: mark as open
           Assert: completed_at is None"""
        # Arrange
        todo = Todo(title="Test")
        todo.mark_completed()
        assert todo.completed_at is not None
        
        # Act
        todo.mark_open()
        
        # Assert
        assert todo.completed_at is None
    
    def test_todo_should_create_next_recurrence_respects_end_date(self):
        """Arrange: completed todo past end_date
           Act: call should_create_next_recurrence
           Assert: returns False"""
        # Arrange
        todo = Todo(
            title="Test",
            recurrence=RecurrenceType.DAILY,
            recurrence_end_date=date.today() - timedelta(days=1),
            status=TodoStatus.COMPLETED
        )
        
        # Act
        result = todo.should_create_next_recurrence()
        
        # Assert
        assert result is False
    
    def test_todo_should_create_next_recurrence_not_completed(self):
        """Arrange: open recurring todo
           Act: call should_create_next_recurrence
           Assert: returns False"""
        # Arrange
        todo = Todo(
            title="Test",
            recurrence=RecurrenceType.DAILY,
            status=TodoStatus.OPEN
        )
        
        # Act
        result = todo.should_create_next_recurrence()
        
        # Assert
        assert result is False


class TestCategoryEdgeCases:
    """Edge case tests für Category"""
    
    def test_category_hash(self, sample_category):
        """Arrange: two categories with same ID
           Act: add to set
           Assert: only one in set"""
        # Arrange
        cat1 = sample_category
        cat2 = Category(name="Different", color="#4ECDC4")
        cat2.id = cat1.id
        
        # Act
        category_set = {cat1, cat2}
        
        # Assert
        assert len(category_set) == 1
    
    def test_category_with_default_color(self):
        """Arrange: create category without color
           Act: create it
           Assert: gets default color"""
        # Act
        cat = Category(name="Test")
        
        # Assert
        assert cat.color == "#0078D4"


class TestTodoControllerEdgeCases:
    """Edge case tests für TodoController"""
    
    def test_filter_todos_by_all_criteria(self, todo_controller):
        """Arrange: create todos with mixed attributes
           Act: filter by status, category, and search
           Assert: returns correct results"""
        # Arrange
        todo1 = todo_controller.create_todo(
            title="Buy groceries",
            categories=["Shopping"]
        )
        todo2 = todo_controller.create_todo(
            title="Work on report",
            categories=["Work"]
        )
        todo_controller.toggle_completion(todo2.id)
        
        # Act
        filtered = todo_controller.filter_todos(
            status=TodoStatus.OPEN,
            category="Shopping",
            search_query="groceries"
        )
        
        # Assert
        assert len(filtered) == 1
        assert filtered[0] == todo1
    
    def test_get_due_this_week_todos(self, todo_controller):
        """Arrange: create todos due this week and next week
           Act: get todos due this week
           Assert: returns only this week's todos"""
        # Arrange
        today = date.today()
        this_week = today + timedelta(days=1)
        next_week = today + timedelta(days=8)
        
        todo1 = todo_controller.create_todo(title="This Week", due_date=this_week)
        todo2 = todo_controller.create_todo(title="Next Week", due_date=next_week)
        
        # Act
        week_todos = todo_controller.get_due_this_week_todos()
        
        # Assert
        assert len(week_todos) >= 1
        assert todo1 in week_todos
    
    def test_mark_completed_returns_todo(self, todo_controller):
        """Arrange: create todo
           Act: mark as completed
           Assert: returns updated todo"""
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        
        # Act
        result = todo_controller.mark_completed(todo.id)
        
        # Assert
        assert result is not None
        assert result.status == TodoStatus.COMPLETED
    
    def test_mark_completed_returns_none_for_invalid_id(self, todo_controller):
        """Arrange: controller ready
           Act: mark invalid todo as completed
           Assert: returns None"""
        # Act
        result = todo_controller.mark_completed("invalid")
        
        # Assert
        assert result is None
    
    def test_mark_open_returns_none_for_invalid_id(self, todo_controller):
        """Arrange: controller ready
           Act: mark invalid todo as open
           Assert: returns None"""
        # Act
        result = todo_controller.mark_open("invalid")
        
        # Assert
        assert result is None
    
    def test_toggle_completion_returns_none_for_invalid_id(self, todo_controller):
        """Arrange: controller ready
           Act: toggle invalid todo
           Assert: returns None"""
        # Act
        result = todo_controller.toggle_completion("invalid")
        
        # Assert
        assert result is None
    
    def test_handle_recurring_todos_weekly(self, todo_controller):
        """Arrange: create completed weekly todo
           Act: handle recurrence
           Assert: new todo created 7 days later"""
        # Arrange
        today = date.today()
        # Verwende den 10. des Monats, um Monatsüberlauf zu vermeiden
        safe_date = date(today.year, today.month, 10)
        todo = todo_controller.create_todo(
            title="Weekly Task",
            due_date=safe_date,
            recurrence=RecurrenceType.WEEKLY
        )
        todo_controller.toggle_completion(todo.id)
        
        # Act
        created = todo_controller.handle_recurring_todos()
        
        # Assert
        assert len(created) == 1
        assert created[0].due_date == safe_date + timedelta(days=7)
    
    def test_handle_recurring_todos_monthly(self, todo_controller):
        """Arrange: create completed monthly todo
           Act: handle recurrence
           Assert: new todo created next month"""
        # Arrange
        today = date.today()
        todo = todo_controller.create_todo(
            title="Monthly Task",
            due_date=date(today.year, today.month, 15),
            recurrence=RecurrenceType.MONTHLY
        )
        todo_controller.toggle_completion(todo.id)
        
        # Act
        created = todo_controller.handle_recurring_todos()
        
        # Assert
        assert len(created) == 1
        next_date = created[0].due_date
        assert next_date.day == 15
    
    def test_handle_recurring_todos_with_custom_interval(self, todo_controller):
        """Arrange: create todo with custom interval
           Act: handle recurrence
           Assert: uses custom interval"""
        # Arrange
        # Use a day early in the month to avoid date math issues
        today = date.today()
        safe_date = date(today.year, today.month, 10)  # Day 10 is safe for all months
        
        todo = todo_controller.create_todo(
            title="Bi-weekly Task",
            due_date=safe_date,
            recurrence=RecurrenceType.WEEKLY,
            recurrence_interval=2
        )
        todo_controller.toggle_completion(todo.id)
        
        # Act
        created = todo_controller.handle_recurring_todos()
        
        # Assert
        assert len(created) == 1
        assert created[0].due_date == safe_date + timedelta(days=14)
    
    def test_refresh_reloads_todos(self, todo_controller):
        """Arrange: controller with todos
           Act: call refresh
           Assert: todos reloaded"""
        # Arrange
        todo = todo_controller.create_todo(title="Test")
        original_count = len(todo_controller.get_todos())
        todo_controller.storage.load_todos.return_value = []
        
        # Act
        todo_controller.refresh()
        
        # Assert
        assert len(todo_controller.get_todos()) == 0


class TestCategoryControllerEdgeCases:
    """Edge case tests für CategoryController"""
    
    def test_update_category_returns_none_for_invalid_id(self, category_controller):
        """Arrange: controller ready
           Act: update non-existent category
           Assert: returns None"""
        # Act
        result = category_controller.update_category("invalid", name="Test")
        
        # Assert
        assert result is None
    
    def test_delete_category_returns_false_for_invalid_id(self, category_controller):
        """Arrange: controller ready
           Act: delete non-existent category
           Assert: returns False"""
        # Act
        result = category_controller.delete_category("invalid")
        
        # Assert
        assert result is False
    
    def test_get_category_by_name_returns_none(self, category_controller):
        """Arrange: controller ready
           Act: get non-existent category by name
           Assert: returns None"""
        # Act
        result = category_controller.get_category_by_name("NonExistent")
        
        # Assert
        assert result is None
    
    def test_get_category_returns_none(self, category_controller):
        """Arrange: controller ready
           Act: get non-existent category by ID
           Assert: returns None"""
        # Act
        result = category_controller.get_category("invalid-id")
        
        # Assert
        assert result is None
    
    def test_is_category_used_returns_false(self, category_controller, todo_controller):
        """Arrange: category not used
           Act: check if used
           Assert: returns False"""
        # Arrange
        category = category_controller.create_category(name="Unused")
        
        # Act
        result = category_controller.is_category_used(category.id, [])
        
        # Assert
        assert result is False
    
    def test_is_category_used_returns_true(self, category_controller, todo_controller):
        """Arrange: category used in todo
           Act: check if used
           Assert: returns True"""
        # Arrange
        category = category_controller.create_category(name="Used")
        todo = todo_controller.create_todo(title="Test", categories=["Used"])
        
        # Act
        result = category_controller.is_category_used(category.id, [todo])
        
        # Assert
        assert result is True
    
    def test_get_color_for_invalid_category(self, category_controller):
        """Arrange: controller ready
           Act: get color for invalid category
           Assert: returns default color"""
        # Act
        color = category_controller.get_color_for_category("invalid")
        
        # Assert
        assert color == "#0078D4"
    
    def test_refresh_reloads_categories(self, category_controller):
        """Arrange: controller with categories
           Act: call refresh
           Assert: categories reloaded"""
        # Arrange
        category = category_controller.create_category(name="Test")
        original_count = len(category_controller.get_categories())
        category_controller.storage.load_categories.return_value = []
        
        # Act
        category_controller.refresh()
        
        # Assert
        assert len(category_controller.get_categories()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
