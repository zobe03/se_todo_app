"""Controllers - Geschäftslogik"""

from typing import List, Optional, Dict, Any
from datetime import date
from app.models import (
    Todo, TodoStatus, RecurrenceType, Category, JSONStorage,
    ExternalTaskAPI, ExternalTaskAdapter, ExternalTaskImporter, ExternalTask
)


# ===== HILFSFUNKTIONEN =====

def capitalize_first_letter(text: str) -> str:
    """Erster Buchstabe groß"""
    if not text:
        return text
    return text[0].upper() + text[1:] if len(text) > 1 else text.upper()


def capitalize_sentences(text: str) -> str:
    """Erster Buchstabe nach Satzanfang oder nach '. ' groß"""
    if not text:
        return text
    
    # Erster Buchstabe groß
    result = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Nach ". " auch groß
    parts = result.split(". ")
    capitalized_parts = [parts[0]]
    for part in parts[1:]:
        if part:
            capitalized_parts.append(part[0].upper() + part[1:] if len(part) > 1 else part.upper())
        else:
            capitalized_parts.append(part)
    
    return ". ".join(capitalized_parts)


# ===== TODO CONTROLLER =====

class TodoController:
    """Controller für Todo-Management (CRUD + Filter + Recurrence)"""
    
    def __init__(self, storage: Optional[JSONStorage] = None):
        """Initialisiere TodoController"""
        self.storage = storage or JSONStorage()
        self._todos: List[Todo] = self._load_todos()

    def _load_todos(self) -> List[Todo]:
        """Lade Todos aus Storage"""
        return self.storage.load_todos()

    def _save_todos(self) -> None:
        """Speichere Todos in Storage"""
        self.storage.save_todos(self._todos)

    # ===== CRUD Operationen =====

    def create_todo(
        self,
        title: str,
        description: str = "",
        due_date: Optional[date] = None,
        categories: Optional[List[str]] = None,
        recurrence: RecurrenceType = RecurrenceType.NONE,
        recurrence_interval: int = 1,
        recurrence_end_date: Optional[date] = None,
    ) -> Todo:
        """Erstelle neue Aufgabe"""
        if categories is None:
            categories = []

        if not title or not title.strip():
            raise ValueError("Titel darf nicht leer sein")
        if len(categories) > 5:
            raise ValueError("Max. 5 Kategorien pro Aufgabe erlaubt")

        # Kapitalisierung
        title = capitalize_first_letter(title.strip())
        description = capitalize_sentences(description.strip()) if description else ""

        todo = Todo(
            title=title,
            description=description,
            due_date=due_date,
            categories=categories,
            recurrence=recurrence,
            recurrence_interval=recurrence_interval,
            recurrence_end_date=recurrence_end_date,
        )

        self._todos.append(todo)
        self._save_todos()
        return todo

    def get_todos(self) -> List[Todo]:
        """Erhalte alle Todos"""
        return self._todos.copy()

    def get_todo(self, todo_id: str) -> Optional[Todo]:
        """Erhalte einzelnes Todo by ID"""
        for todo in self._todos:
            if todo.id == todo_id:
                return todo
        return None

    def update_todo(self, todo_id: str, **kwargs) -> Optional[Todo]:
        """Update Aufgabe"""
        todo = self.get_todo(todo_id)
        if not todo:
            return None

        if "title" in kwargs and kwargs["title"]:
            if not kwargs["title"].strip():
                raise ValueError("Titel darf nicht leer sein")
            kwargs["title"] = capitalize_first_letter(kwargs["title"].strip())

        if "description" in kwargs:
            kwargs["description"] = capitalize_sentences(kwargs["description"].strip()) if kwargs["description"] else ""

        if "categories" in kwargs:
            if len(kwargs["categories"]) > 5:
                raise ValueError("Max. 5 Kategorien pro Aufgabe erlaubt")

        todo.update(**kwargs)
        self._save_todos()
        return todo

    def delete_todo(self, todo_id: str) -> bool:
        """Lösche Aufgabe"""
        todo = self.get_todo(todo_id)
        if not todo:
            return False

        self._todos.remove(todo)
        self._save_todos()
        return True

    # ===== Status Management =====

    def toggle_completion(self, todo_id: str) -> Optional[Todo]:
        """Toggle Todo zwischen offen und erledigt"""
        todo = self.get_todo(todo_id)
        if not todo:
            return None

        todo.toggle_completion()
        self._save_todos()
        return todo

    def mark_completed(self, todo_id: str) -> Optional[Todo]:
        """Markiere Todo als erledigt"""
        todo = self.get_todo(todo_id)
        if not todo:
            return None

        todo.mark_completed()
        self._save_todos()
        return todo

    def mark_open(self, todo_id: str) -> Optional[Todo]:
        """Markiere Todo als offen"""
        todo = self.get_todo(todo_id)
        if not todo:
            return None

        todo.mark_open()
        self._save_todos()
        return todo

    # ===== Filterung =====

    def get_todos_by_status(self, status: TodoStatus) -> List[Todo]:
        """Erhalte Todos gefiltert nach Status"""
        return [todo for todo in self._todos if todo.status == status]

    def get_open_todos(self) -> List[Todo]:
        """Erhalte alle offenen Todos"""
        return self.get_todos_by_status(TodoStatus.OPEN)

    def get_completed_todos(self) -> List[Todo]:
        """Erhalte alle erledigten Todos"""
        return self.get_todos_by_status(TodoStatus.COMPLETED)

    def get_todos_by_category(self, category: str) -> List[Todo]:
        """Erhalte Todos gefiltert nach Kategorie"""
        return [todo for todo in self._todos if category in todo.categories]

    def filter_todos(
        self,
        status: Optional[TodoStatus] = None,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Todo]:
        """Filter Todos nach mehreren Kriterien"""
        result = self._todos.copy()

        if status is not None:
            result = [t for t in result if t.status == status]

        if category is not None:
            result = [t for t in result if category in t.categories]

        if search_query:
            query = search_query.lower().strip()
            result = [
                t for t in result
                if query in t.title.lower() or query in t.description.lower()
            ]

        return result

    def search_todos(self, query: str) -> List[Todo]:
        """Suche Todos nach Titel + Beschreibung"""
        return self.filter_todos(search_query=query)

    def get_overdue_todos(self) -> List[Todo]:
        """Erhalte alle überfälligen Todos"""
        return [todo for todo in self._todos if todo.is_overdue()]

    def get_due_today_todos(self) -> List[Todo]:
        """Erhalte alle Todos die heute fällig sind"""
        return [todo for todo in self._todos if todo.is_due_today()]

    def get_due_this_week_todos(self) -> List[Todo]:
        """Erhalte alle Todos die diese Woche fällig sind"""
        return [todo for todo in self._todos if todo.is_due_this_week()]

    # ===== Statistiken =====

    def get_stats(self) -> Dict:
        """Erhalte Statistiken über Todos"""
        return {
            "total": len(self._todos),
            "open": len(self.get_open_todos()),
            "completed": len(self.get_completed_todos()),
            "overdue": len(self.get_overdue_todos()),
        }

    # ===== Recurrence Handling =====

    def handle_recurring_todos(self) -> List[Todo]:
        """Erstelle neue Instanzen von wiederkehrenden Aufgaben"""
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
                recurrence_interval=todo.recurrence_interval,
                recurrence_end_date=todo.recurrence_end_date,
            )

            self._todos.append(new_todo)
            created.append(new_todo)

        if created:
            self._save_todos()

        return created

    def refresh(self) -> None:
        """Lade Todos neu aus Storage"""
        self._todos = self._load_todos()

    # ===== ADAPTER PATTERN: EXTERNE AUFGABEN IMPORTIEREN =====

    def import_from_external_source(
        self, 
        external_api: ExternalTaskAPI,
        merge_strategy: str = "skip_duplicates"
    ) -> Dict[str, Any]:
        """Importiert Aufgaben von externer Quelle via Adapter Pattern.
        
        Args:
            external_api: Externe API-Quelle
            merge_strategy: "skip_duplicates", "overwrite", "keep_both"
        
        Returns:
            Dict mit Import-Statistiken
        
        Live-Coding-Anpassungen:
        - Verschiedene Merge-Strategien implementieren
        - Konflikt-Auflösung bei ID-Duplikaten
        - Import-Log für Nachvollziehbarkeit
        
        Beispiel:
        >>> api = ExternalTaskAPI()
        >>> api.add_mock_task(ExternalTask(task_id="ext-1", name="Test"))
        >>> stats = controller.import_from_external_source(api)
        >>> print(stats)  # {'imported': 1, 'skipped': 0, 'errors': 0}
        """
        # Adapter-Pattern: Verwende Adapter zur Konvertierung
        importer = ExternalTaskImporter(
            api=external_api,
            adapter=ExternalTaskAdapter()
        )
        
        imported_todos = importer.import_tasks()
        
        stats = {
            "imported": 0,
            "skipped": 0,
            "errors": 0,
            "total_fetched": len(imported_todos)
        }
        
        # Merge-Strategien
        existing_ids = {todo.id for todo in self._todos}
        
        for imported_todo in imported_todos:
            try:
                if imported_todo.id in existing_ids:
                    if merge_strategy == "skip_duplicates":
                        stats["skipped"] += 1
                        continue
                    elif merge_strategy == "overwrite":
                        # Ersetze bestehendes Todo
                        self._todos = [t for t in self._todos if t.id != imported_todo.id]
                        self._todos.append(imported_todo)
                        stats["imported"] += 1
                    elif merge_strategy == "keep_both":
                        # Generiere neue ID für Import
                        import uuid
                        imported_todo.id = str(uuid.uuid4())
                        self._todos.append(imported_todo)
                        stats["imported"] += 1
                else:
                    # Neues Todo
                    self._todos.append(imported_todo)
                    stats["imported"] += 1
            except Exception as e:
                stats["errors"] += 1
                print(f"Fehler beim Import von Task {imported_todo.id}: {e}")
        
        if stats["imported"] > 0:
            self._save_todos()
        
        return stats
    
    def export_to_external_format(self, todo_ids: Optional[List[str]] = None) -> List[ExternalTask]:
        """Exportiert Todos in externes Format (reverse Adapter).
        
        Args:
            todo_ids: Spezifische Todo-IDs, oder None für alle
        
        Returns:
            Liste von ExternalTask-Objekten
        
        Live-Coding:
        - Export zu echter API
        - Batch-Upload
        - Retry-Logik bei Fehlern
        """
        todos_to_export = self._todos
        if todo_ids:
            todos_to_export = [t for t in self._todos if t.id in todo_ids]
        
        return [ExternalTaskAdapter.reverse_adapt(todo) for todo in todos_to_export]


# ===== CATEGORY CONTROLLER =====

class CategoryController:
    """Controller für Kategorie-Management (CRUD + Validierung)"""
    
    MAX_CATEGORIES = 5
    
    def __init__(self, storage: Optional[JSONStorage] = None):
        """Initialisiere CategoryController"""
        self.storage = storage or JSONStorage()
        self._categories: List[Category] = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Lade Kategorien aus Storage"""
        return self.storage.load_categories()

    def _save_categories(self) -> None:
        """Speichere Kategorien in Storage"""
        self.storage.save_categories(self._categories)

    # ===== CRUD Operationen =====

    def create_category(self, name: str, color: str = None) -> Category:
        """Erstelle neue Kategorie"""
        if len(self._categories) >= self.MAX_CATEGORIES:
            raise ValueError(
                f"Max. {self.MAX_CATEGORIES} Kategorien erlaubt. "
                f"Lösche eine, um eine neue anzulegen."
            )

        if self.category_exists(name):
            raise ValueError(f"Kategorie '{name}' existiert bereits")

        # Kapitalisierung
        name = capitalize_first_letter(name.strip())

        # Automatische Farbzuweisung aus Palette
        if color is None:
            color_palette = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B195", "#C06C84"]
            color = color_palette[len(self._categories) % len(color_palette)]

        category = Category(name=name, color=color)
        self._categories.append(category)
        self._save_categories()
        return category

    def get_categories(self) -> List[Category]:
        """Erhalte alle Kategorien"""
        return self._categories.copy()

    def get_category(self, category_id: str) -> Optional[Category]:
        """Erhalte einzelne Kategorie by ID"""
        for cat in self._categories:
            if cat.id == category_id:
                return cat
        return None

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Erhalte Kategorie by Name"""
        for cat in self._categories:
            if cat.name == name:
                return cat
        return None

    def update_category(
        self,
        category_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Optional[Category]:
        """Update Kategorie"""
        category = self.get_category(category_id)
        if not category:
            return None

        if name is not None:
            if not name.strip():
                raise ValueError("Name darf nicht leer sein")
            name_capitalized = capitalize_first_letter(name.strip())
            if name_capitalized != category.name and self.category_exists(name_capitalized):
                raise ValueError(f"Kategorie '{name_capitalized}' existiert bereits")
            category.name = name_capitalized

        if color is not None:
            if not Category._is_valid_hex_color(color):
                raise ValueError("Ungültige Hex-Farbe (z.B. #FF5733)")
            category.color = color

        self._save_categories()
        return category

    def delete_category(self, category_id: str) -> bool:
        """Lösche Kategorie"""
        category = self.get_category(category_id)
        if not category:
            return False

        self._categories.remove(category)
        self._save_categories()
        return True

    # ===== Validierung =====

    def validate_max_categories(self) -> bool:
        """Prüfe, ob Max-Anzahl Kategorien erreicht ist"""
        return len(self._categories) >= self.MAX_CATEGORIES

    def category_exists(self, name: str) -> bool:
        """Prüfe, ob Kategorie mit Name existiert"""
        return self.get_category_by_name(name) is not None

    def is_category_used(self, category_id: str, todos: List) -> bool:
        """Prüfe, ob Kategorie in Todos verwendet wird"""
        category = self.get_category(category_id)
        if not category:
            return False

        for todo in todos:
            if category.name in todo.categories:
                return True

        return False

    # ===== Hilfsfunktionen =====

    def get_color_for_category(self, category_id: str) -> str:
        """Erhalte Farbe für Kategorie"""
        category = self.get_category(category_id)
        return category.color if category else "#0078D4"

    def refresh(self) -> None:
        """Lade Kategorien neu aus Storage"""
        self._categories = self._load_categories()
