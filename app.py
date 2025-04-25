import streamlit as st
from datetime import datetime
from sdlxliff_fixer import parse_sdlxliff, fix_sdlxliff, save_fixed_file

# ====== Configuration ======
st.set_page_config(
    page_title="SDLXLIFF Fixer",
    page_icon="⚙️",
    layout="wide"
)

# ====== Header Section ======
with st.container():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("assets/future-group-logo.png", width=150)
    with col2:
        st.title("SDLXLIFF File Fixer")
        st.caption("Translation Engineering Tool - 2025 • v1.0.0")

# ====== Sidebar ======
with st.sidebar:
    st.header("Developer Information")
    st.subheader("Ahmed Mostafa Saad")
    st.write("""
    - **Position**: Localization Engineering & TMS Support Team Lead  
    - **Contact**: [ahmed.mostafaa@future-group.com](mailto:ahmed.mostafaa@future-group.com)  
    - **Company**: Future Group Translation Services
    """)
    st.divider()
    
    st.header("Tool Instructions")
    st.write("""
    1. Upload two SDLXLIFF files:
       - Clean (Source) File  
       - Damaged (Translated) File  
    2. Tool will extract valid translations from the damaged file  
    3. Download fixed file with correct structure and translations
    """)

# ====== Main Section ======
st.header("Fix Your SDLXLIFF File")

col_clean, col_damaged = st.columns(2)
with col_clean:
    clean_file = st.file_uploader("Upload CLEAN (source) SDLXLIFF file", type=["sdlxliff"])
with col_damaged:
    damaged_file = st.file_uploader("Upload DAMAGED (translated) SDLXLIFF file", type=["sdlxliff"])

if clean_file and damaged_file:
    with st.spinner("Processing your files..."):
        try:
            clean_content = clean_file.read()
            damaged_content = damaged_file.read()

            tree_clean = parse_sdlxliff(clean_content)
            tree_damaged = parse_sdlxliff(damaged_content)

            fixed_tree = fix_sdlxliff(tree_clean, tree_damaged)
            fixed_buffer, fixed_filename = save_fixed_file(fixed_tree, clean_file.name)

            st.success("✅ File fixed successfully!")
            st.download_button(
                label="Download Fixed File",
                data=fixed_buffer,
                file_name=fixed_filename,
                mime="application/xml"
            )

            # Optional JSON summary
            st.divider()
            st.json({
                "process_info": {
                    "clean_file": clean_file.name,
                    "damaged_file": damaged_file.name,
                    "fixed_file": fixed_filename,
                    "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            })

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ====== Footer ======
st.divider()
st.markdown("""
<div style="text-align: center; color: #555; padding: 10px;">
    Future Group - Localization Engineering • © 2025 • v1.0.0
</div>
""", unsafe_allow_html=True)
