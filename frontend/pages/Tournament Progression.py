import streamlit as st
from helpers import page_cfg

MAX_COLUMNS = page_cfg.load_page_config()

# Initialize blocks and next id counter
if "blocks" not in st.session_state:
    st.session_state["blocks"] = [1]
if "next_block_id" not in st.session_state:
    st.session_state["next_block_id"] = max(st.session_state["blocks"]) + 1

# Title and Add button
col_title, col_add = st.columns([10, 1])
with col_title:
    st.title("Football Tournament Analysis")
with col_add:
    add_disabled = len(st.session_state["blocks"]) >= MAX_COLUMNS
    if st.button("➕", help="Add new column to compare", disabled=add_disabled):
        new_id = st.session_state["next_block_id"]
        st.session_state["blocks"].append(new_id)
        st.session_state["next_block_id"] += 1
        st.rerun()

# Function to render a single block
def render_block(block_id, block_number):
    # Header with delete button
    col_title, col_delete = st.columns([7, 1])

    with col_title:
        st.subheader(f"Title {block_id}")
        st.caption(f"Subtitle {block_id}")

    with col_delete:
        # Delete button (disabled if only one block)
        disabled = (len(st.session_state["blocks"]) == 1)
        if st.button("❌", key=f"delete_{block_id}", disabled=disabled):
            # remove the block safely
            if block_id in st.session_state["blocks"]:
                st.session_state["blocks"].remove(block_id)
            st.rerun()

    # Content sections
    st.write("**Statistics**")
    st.write("**Advanced Statistics**")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Tab 1", "Tab 2", "Tab 3", "Tab 4", "Tab 5"]
    )

    with tab1:
        st.write("Content Tab 1")
    with tab2:
        st.write("Content Tab 2")
    with tab3:
        st.write("Content Tab 3")
    with tab4:
        st.write("Content Tab 4")
    with tab5:
        st.write("Content Tab 5")

# Display blocks in rows with a maximum of MAX_COLUMNS per row
blocks = st.session_state["blocks"]

if len(blocks) == 1:
    render_block(blocks[0], 1)
else:
    for row_start in range(0, len(blocks), MAX_COLUMNS):
        row_blocks = blocks[row_start: row_start + MAX_COLUMNS]
        cols = st.columns(len(row_blocks))
        for i, block_id in enumerate(row_blocks):
            with cols[i]:
                render_block(block_id, row_start + i + 1)
