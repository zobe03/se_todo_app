"""UI - Streamlit UI-Komponenten und Pages"""

import streamlit as st
from datetime import date, timedelta, datetime
import time
from typing import Optional, List, Dict
from controllers import TodoController, CategoryController
from models import Todo, TodoStatus, RecurrenceType


# ===== SECTION 1: Styles & Configuration =====

def apply_page_config():
    """Konfiguriere Streamlit Page"""
    st.set_page_config(
        page_title="Todo App",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
        <style>
        :root {
            --primary: #0078D4;
            --success: #107C10;
            --danger: #D83B01;
            --warning: #FFB900;
            --bg-light: #1a1a1a;
            --text-dark: #FFFFFF;
            --title-color: #BD8181;
        }

        body {
            background-color: #000000;
        }

        /* Streamlit rendert die Markdown-Überschriften anders, deswegen muss man direkter die Streamlit-Selektoren ansprechen */
        h1, h2, h3 {
            color: #BD8181 !important;
        }

        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stHeaderContainer"] h1,
        [data-testid="stHeaderContainer"] h2,
        [data-testid="stHeaderContainer"] h3 {
            color: #BD8181 !important;
        }

        [data-testid="stContainer"] {
            padding: 10px;
        }

        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 500;
            margin-top: 20px !important;
            background-color: rgba(189, 129, 129, 0.4) !important;
        }

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 1px solid #CCCCCC;
        }

        .streamlit-expanderHeader {
            border-radius: 8px;
            background-color: #FFFFFF;
            font-weight: 500;
        }

        [data-testid="stSidebar"] {
            background-color: #000000;
        }

        /* Selectbox Styling - Cursor pointer */
        [data-testid="stSelectbox"] input {
            caret-color: transparent !important;
            cursor: pointer !important;
        }

        [data-testid="stSelectbox"] {
            cursor: pointer !important;
        }

        [data-testid="stSelectbox"] * {
            cursor: pointer !important;
        }

        .stSelectbox input:focus {
            caret-color: transparent !important;
        }

        /* Radio Button Styling */
        [data-testid="stRadio"] input {
            cursor: pointer !important;
        }

        /* Date Input - Heutigen Tag markieren */
        [data-testid="stDateInput"] button[aria-pressed="true"] {
            background-color: rgba(189, 129, 129, 0.6) !important;
            border: 2px solid #BD8181 !important;
        }
        
        /* Date Input in Forms */
        [data-testid="stForm"] [data-testid="stDateInput"] button[aria-pressed="true"] {
            background-color: rgba(189, 129, 129, 0.6) !important;
            border: 2px solid #BD8181 !important;
        }
        
        /* Alle Date Input Buttons mit heute Markierung */
        button[data-baseweb="calendar-day"][aria-pressed="true"] {
            background-color: rgba(189, 129, 129, 0.6) !important;
            border: 2px solid #BD8181 !important;
        }
        
        /* Primary Button für Löschen-Bestätigung - Rot */
        button[kind="primary"] {
            background-color: #D83B01 !important;
            border: 2px solid #D83B01 !important;
        }
        </style>
        """, unsafe_allow_html=True)


# ===== SECTION 2: UI-Komponenten =====

def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Konvertiere Hex-Farbe zu RGBA"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def set_flash_message(message: str):
    """Lege eine flüchtige Success-Meldung mit Zeitstempel ab"""
    st.session_state.last_action = message
    st.session_state.last_action_time = datetime.now().timestamp()


def render_filter_sidebar(todo_ctrl: TodoController, category_ctrl: CategoryController) -> Dict:
    """Rendere Filter-Sidebar"""
    st.sidebar.markdown("### 🔍 Aufgabenfilter")
    
    with st.sidebar:
        with st.expander("***Status:***", expanded=False):
            status_filter = st.radio(
                label="Status",
                options=["Alle", "Offen", "Erledigt"],
                label_visibility="collapsed",
                horizontal=False,
            )

        with st.expander("***Kategorie:***", expanded=False):
            categories = [cat.name for cat in category_ctrl.get_categories()]
            category_options = ["Alle"] + categories
            category_filter = st.selectbox(
                label="Kategorie",
                options=category_options,
                label_visibility="collapsed",
            )

        with st.expander("***Fällig:***", expanded=False):
            due_filter = st.radio(
                label="Fällig",
                options=["Alle", "Heute", "Diese Woche", "Überfällig"],
                label_visibility="collapsed",
                horizontal=False,
            )

        with st.expander("***Suche:***", expanded=False):
            search_query = st.text_input(
                label="Titel durchsuchen",
                placeholder="Titel eingeben...",
                label_visibility="collapsed",
            )

    filters = {
        "status": None,
        "category": None,
        "due_type": due_filter,
        "search": search_query if search_query else None,
    }

    if status_filter == "Offen":
        filters["status"] = TodoStatus.OPEN
    elif status_filter == "Erledigt":
        filters["status"] = TodoStatus.COMPLETED

    if category_filter != "Alle":
        filters["category"] = category_filter

    # ===== KATEGORIENVERWALTUNG =====
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏷️ Kategorien")
    
    with st.sidebar:
        # Kategorien anzeigen
        categories = category_ctrl.get_categories()
        if categories:
            for category in categories:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f'<p style="color: white; margin: 0; padding: 4px 0; text-align: left; font-size: 16px; font-weight: bold;">{category.name}</p>', unsafe_allow_html=True)
                    with col2:
                        if st.button("✏️", key=f"edit_cat_sidebar_{category.id}", use_container_width=True):
                            st.session_state.edit_category_id = category.id
                            st.rerun()
                    with col3:
                        if st.session_state.get("confirm_delete_category") == category.id:
                            # Zeige Löschen und Abbrechen Buttons
                            del_col1, del_col2 = st.columns(2)
                            with del_col1:
                                if st.button("✓", key=f"confirm_delete_cat_{category.id}", use_container_width=True, type="primary"):
                                    category_ctrl.delete_category(category.id)
                                    set_flash_message("Kategorie gelöscht")
                                    st.session_state.confirm_delete_category = None
                                    st.rerun()
                            with del_col2:
                                if st.button("✗", key=f"cancel_delete_cat_{category.id}", use_container_width=True):
                                    st.session_state.confirm_delete_category = None
                                    st.rerun()
                        else:
                            # Zeige normalen Löschen Button
                            if st.button("🗑️", key=f"delete_cat_sidebar_{category.id}", use_container_width=True):
                                st.session_state.confirm_delete_category = category.id
                                st.rerun()
        
        # Edit Modal in Sidebar
        if st.session_state.get("edit_category_id"):
            cat = category_ctrl.get_category(st.session_state.edit_category_id)
            if cat:
                st.markdown("**Kategorie bearbeiten:**")
                with st.form(key=f"edit_cat_sidebar_form_{cat.id}"):
                    new_name = st.text_input(
                        label="Name",
                        value=cat.name,
                        max_chars=50,
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾", use_container_width=True):
                            category_ctrl.update_category(cat.id, name=new_name, color=cat.color)
                            st.session_state.edit_category_id = None
                            set_flash_message("Kategorie aktualisiert")
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌", use_container_width=True):
                            st.session_state.edit_category_id = None
                            st.rerun()
        
        # Neue Kategorie
        if st.button("➕ Neue Kategorie", use_container_width=True, key="btn_new_category_sidebar"):
            st.session_state.show_new_category_form = not st.session_state.get("show_new_category_form", False)
            st.rerun()
        
        if st.session_state.get("show_new_category_form"):
            with st.form(key="new_category_sidebar_form"):
                cat_name = st.text_input(
                    label="Kategorie-Name",
                    placeholder="z.B. Arbeit",
                    max_chars=50,
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("☑️", use_container_width=True):
                        try:
                            category_ctrl.create_category(cat_name)
                            st.session_state.show_new_category_form = False
                            set_flash_message("Kategorie erstellt")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ {str(e)}")
                with col2:
                    if st.form_submit_button("❌", use_container_width=True):
                        st.session_state.show_new_category_form = False
                        st.rerun()

    return filters

def render_help_box():
    """Rendere Hilfe-Box"""
    st.sidebar.markdown("### ❓ Hilfe")

    with st.sidebar:
        with st.expander("📖 Quick Start"):
            st.markdown("""
            - **Neue Aufgabe:** Titel + Datum eingeben
            - **Abhaken:** Checkbox klicken zum Erledigen
            - **Kategorien:** Oben verwalten (max. 5)
            - **Filter:** Links nutzen zum Filtern
            """)

        with st.expander("💾 Datensicherung"):
            st.markdown("""
            Daten werden lokal gespeichert in:
            - Datei: `data/todos.json`
            - Datei: `data/categories.json`
            """)

        st.markdown("Mehr Info: Siehe README.md oder GitHub: https://github.com/zobe03/se_todo_app")


def render_status_header(todo_ctrl: TodoController):
    """Rendere Status-Header mit Statistiken"""
    stats = todo_ctrl.get_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f'<div style="background-color: {hex_to_rgba("#BD8181", 0.3)}; padding: 20px; border-radius: 8px; text-align: center;"><p style="color: #FFFFFF; margin: 0; font-size: 14px;">Gesamt</p><p style="color: #FFFFFF; margin: 8px 0 0 0; font-size: 28px; font-weight: bold;">{stats["total"]}</p></div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div style="background-color: {hex_to_rgba("#BD8181", 0.3)}; padding: 20px; border-radius: 8px; text-align: center;"><p style="color: #FFB900; margin: 0; font-size: 14px;">Offen</p><p style="color: #FFB900; margin: 8px 0 0 0; font-size: 28px; font-weight: bold;">{stats["open"]}</p></div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f'<div style="background-color: {hex_to_rgba("#BD8181", 0.3)}; padding: 20px; border-radius: 8px; text-align: center;"><p style="color: #107C10; margin: 0; font-size: 14px;">Erledigt</p><p style="color: #107C10; margin: 8px 0 0 0; font-size: 28px; font-weight: bold;">{stats["completed"]}</p></div>',
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f'<div style="background-color: {hex_to_rgba("#BD8181", 0.3)}; padding: 20px; border-radius: 8px; text-align: center;"><p style="color: #D83B01; margin: 0; font-size: 14px;">Überfällig</p><p style="color: #D83B01; margin: 8px 0 0 0; font-size: 28px; font-weight: bold;">{stats["overdue"]}</p></div>',
            unsafe_allow_html=True
        )

    if st.session_state.get("last_action"):
        ts = st.session_state.get("last_action_time")
        if ts and (datetime.now().timestamp() - ts) <= 3:
            placeholder = st.empty()
            placeholder.success(f"☑️ {st.session_state.last_action}")
            time.sleep(3)
            placeholder.empty()
            st.session_state.last_action = None
            st.session_state.last_action_time = None
            st.rerun()
        else:
            st.session_state.last_action = None
            st.session_state.last_action_time = None


def render_new_task_form(todo_ctrl: TodoController, category_ctrl: CategoryController) -> Optional[Todo]:
    """Rendere Formular für neue Aufgabe"""
    
    if st.button("## Neue Aufgabe ＋" if not st.session_state.show_new_task_form else "## Schließen ❌", use_container_width=True, key="btn_toggle_form"):
        # Reset delete confirmations bei jedem anderen Button-Klick
        st.session_state.confirm_delete_todo = None
        st.session_state.confirm_delete_category = None
        st.session_state.show_new_task_form = not st.session_state.show_new_task_form
        st.rerun()

    if not st.session_state.get("show_new_task_form"):
        return None

    with st.container(border=True):
        st.markdown("**Quick-Datum:**")
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        selected_quick_date = None
        
        with quick_col1:
            if st.button("📅 Heute", use_container_width=True, key="btn_today"):
                selected_quick_date = date.today()
        with quick_col2:
            if st.button("📅 Morgen", use_container_width=True, key="btn_tomorrow"):
                selected_quick_date = date.today() + timedelta(days=1)
        with quick_col3:
            if st.button("📅 +7 Tage", use_container_width=True, key="btn_plus7"):
                selected_quick_date = date.today() + timedelta(days=7)

        with st.form(key="new_todo_form", clear_on_submit=True):
            title = st.text_input(
                label="📝 Titel (Pflicht)",
                placeholder="z.B. Bericht schreiben...",
                max_chars=200,
            )

            description = st.text_area(
                label="📄 Beschreibung (optional)",
                placeholder="Mehr Details...",
                max_chars=1000,
                height=80,
            )

            col1, col2 = st.columns(2)

            with col1:
                category_options = ["---"] + [cat.name for cat in category_ctrl.get_categories()]
                selected_category = st.selectbox(
                    label="🏷️ Kategorie (optional)",
                    options=category_options,
                )

                recurrence_str = st.selectbox(
                    label="↻ Wiederholung (optional)",
                    options=["Keine", "Täglich", "Wöchentlich", "Monatlich"],
                )

            with col2:
                initial_date = selected_quick_date if selected_quick_date else None
                due_date = st.date_input(
                    label="📅 Fälligkeitsdatum (optional)",
                    value=initial_date,
                    min_value=date.today(),
                )

            col1, col2 = st.columns(2)

            with col1:
                submitted = st.form_submit_button("☑️ Aufgabe hinzufügen", use_container_width=True)

            with col2:
                st.form_submit_button("🔄 Zurücksetzen", use_container_width=True)

            if submitted:
                if not title or not title.strip():
                    st.error("❌ Bitte gib einen Titel ein!")
                    return None

                try:
                    recurrence_map = {
                        "Keine": RecurrenceType.NONE,
                        "Täglich": RecurrenceType.DAILY,
                        "Wöchentlich": RecurrenceType.WEEKLY,
                        "Monatlich": RecurrenceType.MONTHLY,
                    }
                    recurrence = recurrence_map[recurrence_str]

                    categories = []
                    if selected_category != "---":
                        categories = [selected_category]

                    new_todo = todo_ctrl.create_todo(
                        title=title,
                        description=description,
                        due_date=due_date,
                        categories=categories,
                        recurrence=recurrence,
                    )

                    set_flash_message(f"Aufgabe erstellt: '{title}'")
                    st.success(f"☑️ Aufgabe erstellt: {title}")
                    st.rerun()
                    return new_todo

                except ValueError as e:
                    st.error(f"❌ Fehler: {str(e)}")
                    return None


def render_task_card(
    todo: Todo,
    todo_ctrl: TodoController,
    category_ctrl: CategoryController,
    show_edit: bool = True,
):
    """Rendere Single Task Card"""
    status_icon = "☑️" if todo.status == TodoStatus.COMPLETED else "☐"
    title_style = "text-decoration: line-through" if todo.status == TodoStatus.COMPLETED else ""

    metadata_parts = []
    
    if todo.categories:
        for cat_name in todo.categories:
            cat = category_ctrl.get_category_by_name(cat_name)
            if cat:
                metadata_parts.append(f"🏷️ {cat_name}")

    if todo.due_date:
        if todo.is_overdue():
            metadata_parts.append(f"⚠️ {todo.due_date} (Überfällig!)")
        elif todo.is_due_today():
            metadata_parts.append(f"📅 {todo.due_date} (Heute)")
        else:
            metadata_parts.append(f"📅 {todo.due_date}")

    if todo.recurrence != RecurrenceType.NONE:
        recurrence_display = {
            RecurrenceType.DAILY: "täglich",
            RecurrenceType.WEEKLY: "wöchentlich",
            RecurrenceType.MONTHLY: "monatlich",
        }
        metadata_parts.append(f"↻ {recurrence_display.get(todo.recurrence, 'wiederkehrend')}")

    metadata_str = " • ".join(metadata_parts)

    with st.container(border=True):
        col1, col2, col3 = st.columns([0.5, 7, 1.5])

        with col1:
            current_is_completed = todo.status == TodoStatus.COMPLETED
            new_is_completed = st.checkbox(
                label="mark_done",
                value=current_is_completed,
                label_visibility="collapsed",
                key=f"checkbox_{todo.id}",
            )
            # Toggle wenn sich der Status geändert hat
            if new_is_completed != current_is_completed:
                st.session_state.confirm_delete_todo = None
                st.session_state.confirm_delete_category = None
                todo_ctrl.toggle_completion(todo.id)
                st.rerun()

        with col2:
            # Titel mit Durchstreichung wenn erledigt
            if todo.status == TodoStatus.COMPLETED:
                st.markdown(f"**<s>{todo.title}</s>**", unsafe_allow_html=True)
            else:
                st.markdown(f"**{todo.title}**")
            if metadata_str:
                st.caption(metadata_str)
            if todo.description:
                st.caption(todo.description)

        with col3:
            if show_edit:
                btn_col1, btn_col2 = st.columns(2)

                with btn_col1:
                    if st.button("✏️", key=f"edit_{todo.id}", use_container_width=True):
                        st.session_state.confirm_delete_todo = None
                        st.session_state.confirm_delete_category = None
                        st.session_state.edit_todo_id = todo.id
                        st.rerun()

                with btn_col2:
                    if st.session_state.get("confirm_delete_todo") == todo.id:
                        # Zeige Löschen und Abbrechen Buttons
                        del_col1, del_col2 = st.columns(2)
                        with del_col1:
                            if st.button("✓", key=f"confirm_delete_todo_{todo.id}", use_container_width=True, type="primary"):
                                todo_ctrl.delete_todo(todo.id)
                                set_flash_message("Aufgabe gelöscht")
                                st.session_state.confirm_delete_todo = None
                                st.rerun()
                        with del_col2:
                            if st.button("✗", key=f"cancel_delete_todo_{todo.id}", use_container_width=True):
                                st.session_state.confirm_delete_todo = None
                                st.rerun()
                    else:
                        # Zeige normalen Löschen Button
                        if st.button("🗑️", key=f"delete_{todo.id}", use_container_width=True):
                            st.session_state.confirm_delete_todo = todo.id
                            st.rerun()
            else:
                if st.session_state.get("confirm_delete_todo") == todo.id:
                    # Zeige Löschen und Abbrechen Buttons
                    del_col1, del_col2 = st.columns(2)
                    with del_col1:
                        if st.button("✓", key=f"confirm_delete_todo_{todo.id}", use_container_width=True, type="primary"):
                            todo_ctrl.delete_todo(todo.id)
                            set_flash_message("Aufgabe gelöscht")
                            st.session_state.confirm_delete_todo = None
                            st.rerun()
                    with del_col2:
                        if st.button("✗", key=f"cancel_delete_todo_{todo.id}", use_container_width=True):
                            st.session_state.confirm_delete_todo = None
                            st.rerun()
                else:
                    # Zeige normalen Löschen Button
                    if st.button("🗑️", key=f"delete_{todo.id}", use_container_width=True):
                        st.session_state.confirm_delete_todo = todo.id
                        st.rerun()


def render_edit_todo_modal(
    todo: Todo,
    todo_ctrl: TodoController,
    category_ctrl: CategoryController,
):
    """Rendere Edit-Modal für Aufgabe"""
    st.markdown("## ✏️ ")

    with st.form(key=f"edit_form_{todo.id}"):
        new_title = st.text_input(
            label="📝 Titel (Pflicht)",
            value=todo.title,
            max_chars=200,
        )

        new_description = st.text_area(
            label="📄 Beschreibung (otional)",
            value=todo.description,
            max_chars=1000,
            height=80,
        )

        col1, col2 = st.columns(2)

        with col1:
            category_options = ["---"] + [cat.name for cat in category_ctrl.get_categories()]
            new_category = st.selectbox(
                label="🏷️ Kategorie (otional)",
                options=category_options,
                index=0 if not todo.categories else (
                    category_options.index(todo.categories[0]) if todo.categories[0] in category_options else 0
                ),
            )

            recurrence_map = {
                RecurrenceType.NONE: "Keine",
                RecurrenceType.DAILY: "Täglich",
                RecurrenceType.WEEKLY: "Wöchentlich",
                RecurrenceType.MONTHLY: "Monatlich",
            }
            new_recurrence_str = st.selectbox(
                label="↻ Wiederholung (otional)",
                options=["Keine", "Täglich", "Wöchentlich", "Monatlich"],
                index=["Keine", "Täglich", "Wöchentlich", "Monatlich"].index(
                    recurrence_map.get(todo.recurrence, "Keine")
                ),
            )

        with col2:
            new_due_date = st.date_input(
                label="📅 Fälligkeitsdatum (otional)",
                value=todo.due_date,
                min_value=date.today(),
            )

        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("💾 Speichern", use_container_width=True)

        with col2:
            if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                st.session_state.edit_todo_id = None
                st.rerun()

        if submitted:
            if not new_title or not new_title.strip():
                st.error("❌ Bitte gib einen Titel ein!")
                return

            try:
                recurrence_reverse_map = {
                    "Keine": RecurrenceType.NONE,
                    "Täglich": RecurrenceType.DAILY,
                    "Wöchentlich": RecurrenceType.WEEKLY,
                    "Monatlich": RecurrenceType.MONTHLY,
                }
                recurrence = recurrence_reverse_map[new_recurrence_str]

                categories = []
                if new_category != "---":
                    categories = [new_category]

                todo_ctrl.update_todo(
                    todo.id,
                    title=new_title,
                    description=new_description,
                    due_date=new_due_date,
                    categories=categories,
                    recurrence=recurrence,
                )

                set_flash_message("Aufgabe aktualisiert")
                st.session_state.edit_todo_id = None
                st.success("☑️ Aufgabe aktualisiert!")
                st.rerun()

            except ValueError as e:
                st.error(f"❌ Fehler: {str(e)}")


# ===== SECTION 3: Pages =====

def show_todo_list_page(todo_ctrl: TodoController, category_ctrl: CategoryController):
    """Hauptseite: Aufgabenliste mit Filter"""
    st.markdown("# Mein Todo-App")

    render_status_header(todo_ctrl)

    filters = render_filter_sidebar(todo_ctrl, category_ctrl)

    render_new_task_form(todo_ctrl, category_ctrl)

    st.divider()

    st.markdown("## Aufgaben")

    todos = todo_ctrl.get_todos()

    if filters["status"]:
        todos = [t for t in todos if t.status == filters["status"]]

    if filters["category"]:
        todos = [t for t in todos if filters["category"] in t.categories]

    if filters["due_type"] == "Heute":
        todos = [t for t in todos if t.is_due_today()]
    elif filters["due_type"] == "Diese Woche":
        todos = [t for t in todos if t.is_due_this_week() and not t.is_due_today()]
    elif filters["due_type"] == "Überfällig":
        todos = [t for t in todos if t.is_overdue()]

    if filters["search"]:
        todos = [t for t in todos if filters["search"].lower() in t.title.lower()]

    # Trenne offene und erledigte Aufgaben
    open_todos = [t for t in todos if t.status != TodoStatus.COMPLETED]
    completed_todos = [t for t in todos if t.status == TodoStatus.COMPLETED]

    open_todos.sort(key=lambda t: (t.is_overdue() == False, t.due_date or date.max))
    completed_todos.sort(key=lambda t: t.due_date or date.max, reverse=True)

    # Zeige offene Aufgaben
    if open_todos:
        for todo in open_todos:
            if st.session_state.get("edit_todo_id") == todo.id:
                render_edit_todo_modal(todo, todo_ctrl, category_ctrl)
                st.divider()
            else:
                render_task_card(todo, todo_ctrl, category_ctrl, show_edit=True)
    else:
        if not completed_todos:
            st.info("Keine Aufgaben gefunden. Erstelle eine neue!")

    # Zeige erledigte Aufgaben
    if completed_todos:
        st.divider()
        st.markdown("## Erledigte Aufgaben")
        for todo in completed_todos:
            render_task_card(todo, todo_ctrl, category_ctrl, show_edit=False)

    render_help_box()



