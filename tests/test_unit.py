"""Unit Tests für TODO-App mit vollständiger Coverage"""

import pytest
from datetime import date, timedelta, datetime
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Todo, Category, TodoStatus, RecurrenceType, JSONStorage
from controllers import TodoController, CategoryController, capitalize_first_letter, capitalize_sentences


# ===== FIXTURES =====

@pytest.fixture
def mock_storage():
    """Mock JSONStorage für unabhängige Tests"""
    storage = Mock(spec=JSONStorage)
    storage.load_todos.return_value = []
    storage.load_categories.return_value = []
    return storage


@pytest.fixture
def todo_controller(mock_storage):
    """Erstelle TodoController mit Mock-Storage"""
    controller = TodoController(storage=mock_storage)
    return controller


@pytest.fixture
def category_controller(mock_storage):
    """Erstelle CategoryController mit Mock-Storage"""
    controller = CategoryController(storage=mock_storage)
    return controller


@pytest.fixture
def sample_todo():
    """Erstelle Sample Todo"""
    return Todo(
        title="Test Task",
        description="Test Description",
        due_date=date.today(),
        categories=["Test"]
    )


@pytest.fixture
def sample_category():
    """Erstelle Sample Category"""
    return Category(name="Test Category", color="#FF6B6B")


# ===== HELPER FUNCTION TESTS =====

class TestCapitalizationFunctions:
    """Tests für Kapitalisierungsfunktionen"""
    
    def test_capitalize_first_letter_with_lowercase(self):
        """Arrange: lowercase text
           Act: call capitalize_first_letter
           Assert: first letter is uppercase"""
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

class TestTodoModel:
    """Tests für Todo Dataclass"""
    
    def test_todo_creation_with_required_fields(self, sample_todo):
        """Arrange: create todo with required fields
           Act: verify todo attributes
           Assert: all fields set correctly"""
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
           Assert: raises ValueError"""
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
           Assert: status is COMPLETED and completed_at is set"""
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
        sample_todo.recurrence = RecurrenceType.WEEKLY
        sample_todo.due_date = date.today()
        
        # Act
        next_date = sample_todo.get_next_due_date()
        
        # Assert
        assert next_date == date.today() + timedelta(days=7)
    
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

class TestTodoController:
    """Tests für TodoController CRUD und Filterung"""
    
    def test_create_todo_basic(self, todo_controller):
        """Arrange: controller ready
           Act: create todo with title
           Assert: todo created and saved"""
        # Act
        todo = todo_controller.create_todo(title="Test Task")
        
        # Assert
        assert todo.title == "Test Task"
        assert todo.status == TodoStatus.OPEN
        assert len(todo_controller.get_todos()) == 1
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
           Assert: title updated and saved"""
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
           Assert: todo removed and saved"""
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
           Assert: status is COMPLETED"""
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
           Assert: returns matching todos"""
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
           Assert: new todo created with next date"""
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

class TestCategoryController:
    """Tests für CategoryController CRUD"""
    
    def test_create_category_basic(self, category_controller):
        """Arrange: controller ready
           Act: create category
           Assert: category created and saved"""
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

class TestIntegration:
    """Integration tests für Controllers zusammen"""
    
    def test_create_todo_and_category_workflow(self, todo_controller, category_controller):
        """Arrange: both controllers ready
           Act: create category then todo with category
           Assert: todo linked to category"""
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
        todo = todo_controller.create_todo(
            title="Weekly Task",
            due_date=date.today(),
            recurrence=RecurrenceType.WEEKLY
        )
        todo_controller.toggle_completion(todo.id)
        
        # Act
        created = todo_controller.handle_recurring_todos()
        
        # Assert
        assert len(created) == 1
        assert created[0].due_date == date.today() + timedelta(days=7)
    
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
