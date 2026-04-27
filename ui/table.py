"""Отрисовка таблицы в Streamlit"""
import streamlit as st


def render_table(sheet, rows, cols):
    """Отрисовать таблицу"""
    show_formulas = st.session_state.get('show_formulas', False)

    # Инициализация значений ДО создания виджетов
    for row in range(rows):
        for col_idx in range(1, cols + 1):
            key = f"{row},{col_idx}"
            cell_key = f"val_{key}"

            cell = sheet.get(row, col_idx - 1)

            if show_formulas:
                val = cell.get("formula") or str
                (cell.get("computed") or cell.get("value") or "")
            else:
                val = str(cell.get("computed") or cell.get("value") or "")

            # Всегда обновляем session_state из sheet (актуальные данные)
            st.session_state[cell_key] = val

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

            def on_change(row=row, col=col_idx-1,
                          cell_key=cell_key, show_formulas=show_formulas):
                new_val = st.session_state[cell_key]
                sheet.set(row, col, new_val)

                # Обновляем session_state с результатом/формулой
                cell = sheet.get(row, col)
                if show_formulas:
                    st.session_state[cell_key] = cell.get
                    ("formula") or str(cell.get("computed") or "")
                else:
                    st.session_state[cell_key] = str(cell.get
                                                     ("computed") or "")

            with col:
                st.text_input(
                    label=f"R{row}C{col_idx}",
                    key=cell_key,
                    label_visibility="collapsed",
                    on_change=on_change
                )
