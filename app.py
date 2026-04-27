"""Точка входа — Streamlit приложение"""
import streamlit as st

from core.sheet import Sheet
from ui.table import render_table
from config import DEFAULT_ROWS, DEFAULT_COLS, MAX_ROWS, MAX_COLS


def main():
    st.set_page_config(page_title="Таблица", layout="wide")
    st.title("Таблица")
    
    # Инициализация
    if 'sheet' not in st.session_state:
        st.session_state.sheet = Sheet()
    
    sheet = st.session_state.sheet
    
    # Боковая панель
    st.sidebar.header("Настройки таблицы")
    
    rows = st.sidebar.number_input(
        "Количество строк",
        min_value=1,
        max_value=MAX_ROWS,
        value=DEFAULT_ROWS,
        step=1
    )
    
    cols = st.sidebar.number_input(
        "Количество колонок",
        min_value=1,
        max_value=MAX_COLS,
        value=DEFAULT_COLS,
        step=1
    )
    
    # Действия
    st.sidebar.header("Действия")
    
    if st.sidebar.button("💾 Сохранить"):
        sheet._save()
        st.sidebar.success("Сохранено!")
    
    if st.sidebar.button("🗑️ Очистить всё"):
        sheet.clear()
        st.rerun()
    
    # Отрисовка
    render_table(sheet, int(rows), int(cols))
    
    # Статус
    total = len(sheet._data)
    st.write(f"Ячеек заполнено: {total}")


if __name__ == "__main__":
    main()
