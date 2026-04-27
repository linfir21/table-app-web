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
        value=st.session_state.get('rows', DEFAULT_ROWS),
        step=1
    )
    
    cols = st.sidebar.number_input(
        "Количество колонок",
        min_value=1,
        max_value=MAX_COLS,
        value=st.session_state.get('cols', DEFAULT_COLS),
        step=1
    )
    
    st.session_state.rows = int(rows)
    st.session_state.cols = int(cols)
    
    # Переключатель режима
    st.sidebar.header("Режим отображения")
    show_formulas = st.sidebar.checkbox("Показывать формулы")
    st.session_state.show_formulas = show_formulas
    
    # Действия
    st.sidebar.header("Действия")
    
    if st.sidebar.button("💾 Сохранить"):
        sheet._save()
        st.sidebar.success("Сохранено!")
    
    if st.sidebar.button("🗑️ Очистить всё"):
        confirm = st.sidebar.checkbox("Подтвердить удаление")
        if confirm:
            sheet.clear()
            st.rerun()
    
    # Отрисовка
    render_table(sheet, st.session_state.rows, st.session_state.cols)
    
    # Статус
    total = len(sheet._data)
    formulas = sum(1 for c in sheet._data.values() if c.get('formula'))
    st.write(f"Ячеек заполнено: {total} | Формул: {formulas}")


if __name__ == "__main__":
    main()
