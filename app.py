import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io

st.set_page_config(page_title="PDF 合併與分頁工具", layout="wide")
st.title("📄 PDF 自動合併與刪除分頁工具")

# 1. 上傳檔案 (支援 1-2 個)
uploaded_files = st.file_uploader("請上傳 1 至 2 個 PDF 檔案", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if len(uploaded_files) > 2:
        st.warning("目前僅支援最多上傳 2 個檔案，將只處理前兩個。")
        uploaded_files = uploaded_files[:2]

    final_writer = PdfWriter()
    
    # 建立兩欄來顯示每個檔案的設定
    cols = st.columns(len(uploaded_files))
    
    can_merge = True
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            st.subheader(f"檔案 {idx+1}: {uploaded_file.name}")
            reader = PdfReader(uploaded_file)
            
            # 修正處：使用 .pages 獲取總頁數
            total_pages = len(reader.pages)
            st.info(f"總頁數: {total_pages}")

            # 讓用戶輸入要刪除的頁碼 (例如: 1, 3, 5-7)
            exclude_str = st.text_input(f"要刪除的頁碼 (選填，例如: 1, 3-5)", key=f"ex_{idx}")
            
            # 處理頁碼邏輯
            excluded_pages = set()
            if exclude_str:
                try:
                    for part in exclude_str.split(','):
                        part = part.strip()
                        if '-' in part:
                            start, end = map(int, part.split('-'))
                            excluded_pages.update(range(start, end + 1))
                        elif part:
                            excluded_pages.add(int(part))
                except Exception as e:
                    st.error(f"頁碼格式錯誤: {e}")
                    can_merge = False

            # 加入有效頁面到合併器 (PDF 頁碼從 0 開始索引，但用戶輸入通常從 1 開始)
            for page_num in range(1, total_pages + 1):
                if page_num not in excluded_pages:
                    final_writer.add_page(reader.pages[page_num - 1])

    # 3. 輸出與下載
    st.divider()
    if can_merge:
        if st.button("🚀 開始合併並下載"):
            if len(final_writer.pages) > 0:
                output_pdf = io.BytesIO()
                final_writer.write(output_pdf)
                st.success(f"合併完成！共有 {len(final_writer.pages)} 頁。")
                st.download_button(
                    label="💾 點我下載合併後的 PDF",
                    data=output_pdf.getvalue(),
                    file_name="merged_and_cleaned.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("錯誤：合併後的 PDF 沒有任何頁面，請檢查刪除範圍。")
