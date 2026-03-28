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
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
            st.subheader(f"檔案 {idx+1}: {uploaded_file.name}")
            reader = PdfReader(uploaded_file)
            total_pages = len(reader)
            st.info(f"總頁數: {total_pages}")

            # 讓用戶輸入要刪除的頁碼 (例如: 1, 3, 5-7)
            exclude_str = st.text_input(f"要刪除的頁碼 (選填，例如: 1, 3-5)", key=f"ex_{idx}")
            
            # 處理頁碼邏輯
            excluded_pages = set()
            if exclude_str:
                try:
                    for part in exclude_str.split(','):
                        if '-' in part:
                            start, end = map(int, part.split('-'))
                            excluded_pages.update(range(start, end + 1))
                        else:
                            excluded_pages.add(int(part))
                except ValueError:
                    st.error("頁碼格式輸入錯誤，請檢查。")

            # 加入有效頁面到合併器
            for page_num in range(1, total_pages + 1):
                if page_num not in excluded_pages:
                    final_writer.add_page(reader.pages[page_num - 1])

    # 3. 輸出與下載
    if st.button("🚀 開始合併並下載"):
        output_pdf = io.BytesIO()
        final_writer.write(output_pdf)
        st.success("合併完成！")
        st.download_button(
            label="💾 下載合併後的 PDF",
            data=output_pdf.getvalue(),
            file_name="merged_and_cleaned.pdf",
            mime="application/pdf"
        )