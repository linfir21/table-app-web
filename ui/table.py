"""Отрисовка таблицы в Streamlit"""
import streamlit as st


def render_table(sheet, rows, cols):
    """Отрисовать таблицу"""
    # Заголовки
    header_cols = st.columns([0.5] + [1] * cols)
    with header_cols[0]:
        st.write("")
    for i, col in enumerate(header_cols[1:], 1):
        with col:
            st.write(chr(64 + i))
    
    # Ячейки — простой ввод без сложной логики
    for row in range(rows):
        cols_list = st.columns([0.5] + [1] * cols)
        
        with cols_list[0]:
            st.write(row + 1)
        
        for col_idx, col in enumerate(cols_list[1:], 1):
            key = f"{row},{col_idx}"
            
            # Получаем текущее значение из sheet
            cell = sheet.get(row, col_idx - 1)
            current = str(cell.get("computed") or cell.get("value") or "")
            
            with col:
                # Простой text_input без on_change и session_state манипуляций
                user_input = st.text_input(
                    label=f"cell_{key}",
                    value=current,
                    label_visibility="collapsed",
                    key=f"input_{key}"
                )
                
                # Если изменилось — сохраняем в sheet (но не в session_state)
                if user_input != current:
                    sheet.set(row, col_idx - 1, user_input)
