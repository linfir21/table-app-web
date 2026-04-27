"""Отрисовка таблицы в Streamlit"""
import streamlit as st


def render_table(sheet, rows, cols):
    """Отрисовать таблицу"""
    show_formulas = st.session_state.get('show_formulas', False)
    
    # Собираем все изменения, потом одно сохранение
    changes = []
    
    # Заголовки
    header_cols = st.columns([0.5] + [1] * cols)
    with header_cols[0]:
        st.write("")
    for i, col in enumerate(header_cols[1:], 1):
        with col:
            st.write(chr(64 + i))
    
    # Ячейки
    for row in range(rows):
        cols_list = st.columns([0.5] + [1] * cols)
        
        with cols_list[0]:
            st.write(row + 1)
        
        for col_idx, col in enumerate(cols_list[1:], 1):
            key = f"{row},{col_idx}"
            cell_key = f"val_{key}"
            
            cell = sheet.get(row, col_idx - 1)
            
            if show_formulas:
                display = cell.get("formula") or str(cell.get("computed") or cell.get("value") or "")
            else:
                display = str(cell.get("computed") or cell.get("value") or "")
            
            # Устанавливаем начальное значение в session_state
            if cell_key not in st.session_state:
                st.session_state[cell_key] = display
            
            with col:
                new_val = st.text_input(
                    label=f"R{row}C{col_idx}",
                    key=cell_key,
                    label_visibility="collapsed"
                )
                
                # Проверяем изменение
                old_val = cell.get("formula") or str(cell.get("computed") or cell.get("value") or "")
                if new_val != old_val:
                    changes.append((row, col_idx - 1, new_val))
    
    # Применяем все изменения после рендера
    for row, col, val in changes:
        sheet.set(row, col, val)
    
    # Если были изменения — показываем кнопку применить
    if changes:
        if st.button("Применить изменения", key="apply_changes"):
            st.rerun()
