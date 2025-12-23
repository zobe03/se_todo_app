"""App Main Entry Point - Streamlit Todo App"""

import streamlit as st
from ui import apply_page_config, show_todo_list_page, show_categories_page
from controllers import TodoController, CategoryController


# ===== Page Config =====
apply_page_config()

# ===== Session State Initialization =====
if "todo_controller" not in st.session_state:
    st.session_state.todo_controller = TodoController()

if "category_controller" not in st.session_state:
    st.session_state.category_controller = CategoryController()

if "edit_todo_id" not in st.session_state:
    st.session_state.edit_todo_id = None

if "confirm_delete_todo" not in st.session_state:
    st.session_state.confirm_delete_todo = None

if "confirm_delete_category" not in st.session_state:
    st.session_state.confirm_delete_category = None

if "show_new_category_form" not in st.session_state:
    st.session_state.show_new_category_form = False

if "show_new_task_form" not in st.session_state:
    st.session_state.show_new_task_form = False

if "last_action" not in st.session_state:
    st.session_state.last_action = None

# ===== Navigation =====
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio(
    label="Navigation",
    options=["📝 Aufgaben verwalten", "🏷️ Kategorien verwalten"],
    label_visibility="collapsed",
)

# ===== Page Router =====
if page == "📝 Aufgaben verwalten":
    show_todo_list_page(st.session_state.todo_controller, st.session_state.category_controller)
elif page == "🏷️ Kategorien verwalten":
    show_categories_page(st.session_state.category_controller)

# ===== Footer =====
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888;">
    <small>📋 Todo App v1.0 | Daten werden lokal gespeichert | <a href="README.md">Dokumentation</a></small>
    </div>
    """,
    unsafe_allow_html=True,
)
