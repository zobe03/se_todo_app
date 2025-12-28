"""Models - Datenstrukturen und Storage"""

import json
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid


# ===== ENUMS =====

class TodoStatus(str, Enum):
    """Status einer Aufgabe"""
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"


class RecurrenceType(str, Enum):
    """Wiederholungstyp einer Aufgabe"""
    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"


# ===== TODO MODEL =====

@dataclass
class Todo:
    """Dataclass für eine Todo-Aufgabe"""
    
    title: str
    description: str = ""
    status: TodoStatus = TodoStatus.OPEN
    due_date: Optional[date] = None
    categories: List[str] = field(default_factory=list)
    recurrence: RecurrenceType = RecurrenceType.NONE
    recurrence_interval: int = 1
    recurrence_end_date: Optional[date] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validierung nach Initialisierung"""
        if not self.title or not self.title.strip():
            raise ValueError("Titel darf nicht leer sein")
        
        if len(self.title) > 200:
            raise ValueError("Titel darf max. 200 Zeichen lang sein")
        
        if len(self.categories) > 5:
            raise ValueError("Max. 5 Kategorien pro Aufgabe erlaubt")
        
        self.title = self.title.strip()

    def mark_completed(self) -> None:
        """Markiere Aufgabe als erledigt"""
        self.status = TodoStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_open(self) -> None:
        """Markiere Aufgabe als offen"""
        self.status = TodoStatus.OPEN
        self.completed_at = None
        self.updated_at = datetime.now()

    def toggle_completion(self) -> None:
        """Toggle zwischen offen und erledigt"""
        if self.status == TodoStatus.OPEN:
            self.mark_completed()
        else:
            self.mark_open()

    # ===== FACTORY METHODS (Erzeugungsmuster) =====
    
    @classmethod
    def create_standard(cls, title: str, description: str = "", 
                       categories: Optional[List[str]] = None) -> "Todo":
        """Factory Method: Erstellt Standard-Todo ohne Fälligkeitsdatum.
        
        Verwendung:
        - Allgemeine Aufgaben ohne spezielle Anforderungen
        - Client-Code muss konkrete Initialisierung nicht kennen
        
        Live-Coding-Anpassungen:
        - Default-Kategorien ergänzen: categories = categories or ["General"]
        - Priorität hinzufügen
        """
        return cls(
            title=title,
            description=description,
            categories=categories or []
        )
    
    @classmethod
    def create_urgent(cls, title: str, description: str = "",
                     categories: Optional[List[str]] = None) -> "Todo":
        """Factory Method: Erstellt dringende Aufgabe mit Fälligkeit heute.
        
        Vorteile:
        - Automatisches "Urgent"-Tag
        - Fälligkeit immer gesetzt (heute)
        - Einheitliche Erstellung dringender Aufgaben
        
        Live-Coding-Anpassungen:
        - Stunden-Offset: due_date=date.today() + timedelta(hours=4)
        - Notification-Flag setzen
        """
        cats = categories or []
        if "Urgent" not in cats:
            cats.append("Urgent")
        
        return cls(
            title=title,
            description=description,
            due_date=date.today(),
            categories=cats
        )
    
    @classmethod
    def create_recurring(cls, title: str, recurrence_type: RecurrenceType,
                        interval: int = 1, description: str = "",
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None,
                        categories: Optional[List[str]] = None) -> "Todo":
        """Factory Method: Erstellt wiederkehrende Aufgabe.
        
        Verwendung:
        - Regelmäßige Aufgaben (täglich, wöchentlich, monatlich)
        - Wiederholungs-Logik vorkonfiguriert
        
        Live-Coding-Anpassungen:
        - Automatische End-Date-Berechnung
        - Max-Wiederholungen statt End-Date
        - "Recurring"-Kategorie automatisch hinzufügen
        """
        return cls(
            title=title,
            description=description,
            due_date=start_date or date.today(),
            categories=categories or [],
            recurrence=recurrence_type,
            recurrence_interval=interval,
            recurrence_end_date=end_date
        )
    
    @classmethod
    def create_with_deadline(cls, title: str, days_until_due: int,
                            description: str = "",
                            categories: Optional[List[str]] = None) -> "Todo":
        """Factory Method: Erstellt Todo mit relativem Fälligkeitsdatum.
        
        Verwendung:
        - Deadline in X Tagen
        - Flexible Datum-Berechnung
        
        Live-Coding-Anpassungen:
        - Arbeitstage statt Kalendertage
        - Wochenenden überspringen
        """
        from datetime import timedelta
        due = date.today() + timedelta(days=days_until_due)
        return cls(
            title=title,
            description=description,
            due_date=due,
            categories=categories or []
        )

    def update(self, **kwargs) -> None:
        """Update Felder der Aufgabe"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """Prüfe, ob Aufgabe überfällig ist"""
        if self.status == TodoStatus.COMPLETED:
            return False
        if self.due_date is None:
            return False
        return self.due_date < date.today()

    def is_due_today(self) -> bool:
        """Prüfe, ob Aufgabe heute fällig ist"""
        if self.due_date is None:
            return False
        return self.due_date == date.today()

    def is_due_this_week(self) -> bool:
        """Prüfe, ob Aufgabe diese Woche fällig ist"""
        if self.due_date is None:
            return False
        today = date.today()
        days_until_sunday = 6 - today.weekday()
        end_of_week = today.replace(day=today.day + days_until_sunday)
        return today <= self.due_date <= end_of_week

    def should_create_next_recurrence(self) -> bool:
        """Prüfe, ob eine neue wiederkehrende Aufgabe erstellt werden sollte"""
        if self.recurrence == RecurrenceType.NONE:
            return False
        if self.status != TodoStatus.COMPLETED:
            return False
        if self.recurrence_end_date and date.today() > self.recurrence_end_date:
            return False
        return True

    def get_next_due_date(self) -> Optional[date]:
        """Berechne nächstes Fälligkeitsdatum für wiederkehrende Aufgaben"""
        if not self.due_date:
            return None
        
        current_due = self.due_date
        
        if self.recurrence == RecurrenceType.DAILY:
            return date(
                current_due.year,
                current_due.month,
                current_due.day + self.recurrence_interval
            )
        elif self.recurrence == RecurrenceType.WEEKLY:
            return date(
                current_due.year,
                current_due.month,
                current_due.day + (7 * self.recurrence_interval)
            )
        elif self.recurrence == RecurrenceType.MONTHLY:
            next_month = current_due.month + self.recurrence_interval
            next_year = current_due.year
            if next_month > 12:
                next_year += 1
                next_month -= 12
            return date(next_year, next_month, current_due.day)
        
        return None

    def __str__(self) -> str:
        """String-Darstellung"""
        status_str = "✅" if self.status == TodoStatus.COMPLETED else "☐"
        due_str = f" (Fällig: {self.due_date})" if self.due_date else ""
        return f"{status_str} {self.title}{due_str}"


# ===== CATEGORY MODEL =====

@dataclass
class Category:
    """Dataclass für eine Kategorie"""
    
    name: str
    color: str = "#0078D4"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validierung nach Initialisierung"""
        if not self.name or not self.name.strip():
            raise ValueError("Kategorie-Name darf nicht leer sein")
        
        if len(self.name) > 50:
            raise ValueError("Kategorie-Name darf max. 50 Zeichen lang sein")
        
        self.name = self.name.strip()
        
        if not self._is_valid_hex_color(self.color):
            raise ValueError("Ungültige Hex-Farbe (z.B. #FF5733)")

    @staticmethod
    def _is_valid_hex_color(color: str) -> bool:
        """Prüfe, ob String gültige Hex-Farbe ist"""
        if not color.startswith("#"):
            return False
        if len(color) != 7:
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        """String-Darstellung mit Farbpunkt"""
        return f"● {self.name}"

    def __eq__(self, other):
        """Vergleich nach ID"""
        if not isinstance(other, Category):
            return False
        return self.id == other.id

    def __hash__(self):
        """Hashable für Verwendung in Sets"""
        return hash(self.id)


# ===== STORAGE =====

class JSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder für date und Todo/Category Objekte"""
    
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, (TodoStatus, RecurrenceType)):
            return obj.value
        if isinstance(obj, Todo):
            return {
                "id": obj.id,
                "title": obj.title,
                "description": obj.description,
                "status": obj.status.value,
                "due_date": obj.due_date.isoformat() if obj.due_date else None,
                "categories": obj.categories,
                "recurrence": obj.recurrence.value,
                "recurrence_interval": obj.recurrence_interval,
                "recurrence_end_date": obj.recurrence_end_date.isoformat() if obj.recurrence_end_date else None,
                "created_at": obj.created_at.isoformat(),
                "updated_at": obj.updated_at.isoformat(),
                "completed_at": obj.completed_at.isoformat() if obj.completed_at else None,
            }
        if isinstance(obj, Category):
            return {
                "id": obj.id,
                "name": obj.name,
                "color": obj.color,
                "created_at": obj.created_at.isoformat(),
            }
        return super().default(obj)


class JSONStorage:
    """JSON-basierte Persistierung für Todos und Kategorien"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialisiere Storage mit Datenverzeichnis
        
        Args:
            data_dir: Pfad zum Datenverzeichnis
        """
        self.data_dir = Path(data_dir)
        self.todos_file = self.data_dir / "todos.json"
        self.categories_file = self.data_dir / "categories.json"
        
        self._create_data_directory()

    def _create_data_directory(self) -> None:
        """Erstelle Datenverzeichnis und initiale JSON-Dateien"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.todos_file.exists():
            self.todos_file.write_text(json.dumps([], ensure_ascii=False, indent=2))
        
        if not self.categories_file.exists():
            self.categories_file.write_text(json.dumps([], ensure_ascii=False, indent=2))

    def load_todos(self) -> List[Todo]:
        """
        Lade alle Todos aus JSON
        
        Returns:
            List von Todo-Objekten
        """
        try:
            with open(self.todos_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            todos = []
            for todo_dict in data:
                todo = self._dict_to_todo(todo_dict)
                todos.append(todo)
            
            return todos
        except Exception as e:
            print(f"Fehler beim Laden der Todos: {e}")
            return []

    def save_todos(self, todos: List[Todo]) -> None:
        """
        Speichere Todos in JSON
        
        Args:
            todos: List von Todo-Objekten
        """
        try:
            todo_dicts = []
            for todo in todos:
                todo_dict = {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status.value,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "categories": todo.categories,
                    "recurrence": todo.recurrence.value,
                    "recurrence_interval": todo.recurrence_interval,
                    "recurrence_end_date": todo.recurrence_end_date.isoformat() if todo.recurrence_end_date else None,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat(),
                    "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
                }
                todo_dicts.append(todo_dict)
            
            with open(self.todos_file, "w", encoding="utf-8") as f:
                json.dump(todo_dicts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Fehler beim Speichern der Todos: {e}")

    def load_categories(self) -> List[Category]:
        """
        Lade alle Kategorien aus JSON
        
        Returns:
            List von Category-Objekten
        """
        try:
            with open(self.categories_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            categories = []
            for cat_dict in data:
                category = self._dict_to_category(cat_dict)
                categories.append(category)
            
            return categories
        except Exception as e:
            print(f"Fehler beim Laden der Kategorien: {e}")
            return []

    def save_categories(self, categories: List[Category]) -> None:
        """
        Speichere Kategorien in JSON
        
        Args:
            categories: List von Category-Objekten
        """
        try:
            cat_dicts = []
            for category in categories:
                cat_dict = {
                    "id": category.id,
                    "name": category.name,
                    "color": category.color,
                    "created_at": category.created_at.isoformat(),
                }
                cat_dicts.append(cat_dict)
            
            with open(self.categories_file, "w", encoding="utf-8") as f:
                json.dump(cat_dicts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Fehler beim Speichern der Kategorien: {e}")

    @staticmethod
    def _dict_to_todo(todo_dict: Dict[str, Any]) -> Todo:
        """Konvertiere Dict zu Todo"""
        due_date = None
        if todo_dict.get("due_date"):
            due_date = date.fromisoformat(todo_dict["due_date"])
        
        recurrence_end_date = None
        if todo_dict.get("recurrence_end_date"):
            recurrence_end_date = date.fromisoformat(todo_dict["recurrence_end_date"])
        
        return Todo(
            id=todo_dict["id"],
            title=todo_dict["title"],
            description=todo_dict.get("description", ""),
            status=TodoStatus(todo_dict["status"]),
            due_date=due_date,
            categories=todo_dict.get("categories", []),
            recurrence=RecurrenceType(todo_dict.get("recurrence", "NONE")),
            recurrence_interval=todo_dict.get("recurrence_interval", 1),
            recurrence_end_date=recurrence_end_date,
            created_at=datetime.fromisoformat(todo_dict["created_at"]),
            updated_at=datetime.fromisoformat(todo_dict["updated_at"]),
            completed_at=datetime.fromisoformat(todo_dict["completed_at"]) if todo_dict.get("completed_at") else None,
        )

    @staticmethod
    def _dict_to_category(cat_dict: Dict[str, Any]) -> Category:
        """Konvertiere Dict zu Category"""
        return Category(
            id=cat_dict["id"],
            name=cat_dict["name"],
            color=cat_dict.get("color", "#0078D4"),
            created_at=datetime.fromisoformat(cat_dict["created_at"]),
        )


# ===== ADAPTER PATTERN: EXTERNE AUFGABENQUELLEN =====

@dataclass
class ExternalTask:
    """Externe Aufgabe von fiktiver API (z.B. Trello, Jira, Asana).
    
    Unterschiede zu Todo:
    - task_id statt id
    - name statt title
    - details statt description
    - priority statt status
    - deadline statt due_date
    - tags statt categories
    - created/modified statt created_at/updated_at
    """
    task_id: str
    name: str
    details: str = ""
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    deadline: Optional[str] = None  # ISO-Format String
    tags: List[str] = field(default_factory=list)
    is_completed: bool = False
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    modified: str = field(default_factory=lambda: datetime.now().isoformat())
    repeat_pattern: Optional[str] = None  # "daily", "weekly", "monthly", None


class ExternalTaskAPI:
    """Fiktive externe API für Aufgaben.
    
    Simuliert externe Datenquelle mit anderem Format.
    In der Realität: REST API, GraphQL, Datenbank, etc.
    
    Live-Coding-Anpassungen:
    - HTTP-Requests zu echter API
    - Authentifizierung hinzufügen
    - Error Handling für Netzwerkfehler
    """
    
    def __init__(self):
        """Initialisiere mit Mock-Daten."""
        self._tasks: List[ExternalTask] = []
    
    def fetch_tasks(self) -> List[ExternalTask]:
        """Hole Aufgaben von externer Quelle.
        
        Live-Coding:
        return requests.get("https://api.example.com/tasks").json()
        """
        return self._tasks
    
    def add_mock_task(self, task: ExternalTask) -> None:
        """Füge Mock-Task hinzu (nur für Demo/Tests)."""
        self._tasks.append(task)
    
    def clear_tasks(self) -> None:
        """Lösche alle Tasks (nur für Tests)."""
        self._tasks.clear()


class ExternalTaskAdapter:
    """Adapter: Konvertiert ExternalTask -> Todo.
    
    Design Pattern: Adapter (Wrapper Pattern)
    - Übersetzt externes Format in internes Format
    - Bestehender Code bleibt unverändert
    - Ermöglicht Integration verschiedener Quellen
    
    Live-Coding-Anpassungen:
    - Bidirektionaler Adapter (Todo -> ExternalTask)
    - Batch-Konvertierung optimieren
    - Caching für häufige Konvertierungen
    """
    
    @staticmethod
    def adapt(external_task: ExternalTask) -> Todo:
        """Konvertiert ExternalTask in Todo.
        
        Mapping:
        - task_id -> id
        - name -> title
        - details -> description
        - priority -> status (high/urgent -> Urgent-Kategorie)
        - deadline -> due_date
        - tags -> categories
        - repeat_pattern -> recurrence
        
        Args:
            external_task: Externe Aufgabe
        
        Returns:
            Todo-Objekt im internen Format
        
        Live-Coding:
        - Fehlerbehandlung bei ungültigen Daten
        - Logging für Konvertierungen
        - Validierung vor Konvertierung
        """
        # Status-Mapping
        status = TodoStatus.COMPLETED if external_task.is_completed else TodoStatus.OPEN
        
        # Datum-Konvertierung
        due_date = None
        if external_task.deadline:
            try:
                due_date = date.fromisoformat(external_task.deadline)
            except (ValueError, TypeError):
                due_date = None
        
        # Recurrence-Mapping
        recurrence = RecurrenceType.NONE
        if external_task.repeat_pattern:
            recurrence_map = {
                "daily": RecurrenceType.DAILY,
                "weekly": RecurrenceType.WEEKLY,
                "monthly": RecurrenceType.MONTHLY,
            }
            recurrence = recurrence_map.get(
                external_task.repeat_pattern.lower(), 
                RecurrenceType.NONE
            )
        
        # Priority zu Kategorie konvertieren
        categories = external_task.tags.copy() if external_task.tags else []
        if external_task.priority in ["high", "urgent"]:
            if "Urgent" not in categories:
                categories.append("Urgent")
        
        # Zeitstempel-Konvertierung
        created_at = datetime.fromisoformat(external_task.created)
        updated_at = datetime.fromisoformat(external_task.modified)
        completed_at = updated_at if external_task.is_completed else None
        
        # Todo erstellen
        return Todo(
            id=external_task.task_id,
            title=external_task.name,
            description=external_task.details,
            status=status,
            due_date=due_date,
            categories=categories,
            recurrence=recurrence,
            recurrence_interval=1,
            recurrence_end_date=None,
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at
        )
    
    @staticmethod
    def adapt_many(external_tasks: List[ExternalTask]) -> List[Todo]:
        """Konvertiert mehrere externe Aufgaben.
        
        Live-Coding:
        - Parallel-Verarbeitung für große Listen
        - Progress-Callback für UI
        - Fehlerhafte Tasks überspringen statt Abbruch
        """
        return [ExternalTaskAdapter.adapt(task) for task in external_tasks]
    
    @staticmethod
    def reverse_adapt(todo: Todo) -> ExternalTask:
        """Konvertiert Todo zurück in ExternalTask (optional).
        
        Für bidirektionale Synchronisation.
        
        Live-Coding:
        - Sync-Konflikte erkennen
        - Merge-Strategien implementieren
        """
        # Status-Mapping
        is_completed = todo.status == TodoStatus.COMPLETED
        
        # Priority aus Kategorien ableiten
        priority = "urgent" if "Urgent" in todo.categories else "normal"
        
        # Recurrence-Mapping
        repeat_pattern = None
        if todo.recurrence != RecurrenceType.NONE:
            pattern_map = {
                RecurrenceType.DAILY: "daily",
                RecurrenceType.WEEKLY: "weekly",
                RecurrenceType.MONTHLY: "monthly",
            }
            repeat_pattern = pattern_map.get(todo.recurrence)
        
        # Tags ohne "Urgent"
        tags = [cat for cat in todo.categories if cat != "Urgent"]
        
        return ExternalTask(
            task_id=todo.id,
            name=todo.title,
            details=todo.description,
            priority=priority,
            deadline=todo.due_date.isoformat() if todo.due_date else None,
            tags=tags,
            is_completed=is_completed,
            created=todo.created_at.isoformat(),
            modified=todo.updated_at.isoformat(),
            repeat_pattern=repeat_pattern
        )


class ExternalTaskImporter:
    """Import-Service für externe Aufgaben (Facade).
    
    Vereinfacht Integration in Controller.
    
    Live-Coding-Erweiterungen:
    - Duplikat-Erkennung
    - Merge-Strategien (bei ID-Konflikten)
    - Selective Import (Filter-Optionen)
    """
    
    def __init__(self, api: ExternalTaskAPI, adapter: ExternalTaskAdapter):
        """Initialisiere Importer.
        
        Args:
            api: Externe API-Quelle
            adapter: Adapter für Konvertierung
        """
        self.api = api
        self.adapter = adapter
    
    def import_tasks(self) -> List[Todo]:
        """Importiert alle Tasks von externer Quelle.
        
        Returns:
            Liste konvertierter Todos
        
        Live-Coding:
        - Progress-Tracking
        - Error-Handling pro Task
        - Import-Statistiken zurückgeben
        """
        external_tasks = self.api.fetch_tasks()
        return self.adapter.adapt_many(external_tasks)
    
    def import_task_by_id(self, task_id: str) -> Optional[Todo]:
        """Importiert einzelnen Task nach ID.
        
        Live-Coding:
        - Direkter API-Call statt fetch_all
        - Caching für bereits importierte Tasks
        """
        external_tasks = self.api.fetch_tasks()
        for task in external_tasks:
            if task.task_id == task_id:
                return self.adapter.adapt(task)
        return None
