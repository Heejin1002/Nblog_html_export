import streamlit as st
from blog_html2 import extract_blog_html
import pyperclip
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import os
import shutil

st.set_page_config(page_title="네이버 블로그 본문 추출기", layout="wide")
st.title("네이버 블로그 본문 추출기 (Streamlit)")

st.markdown("""
- 네이버 블로그 URL을 입력하고 **추출** 버튼을 누르세요.
- 본문 HTML과 미리보기를 바로 확인할 수 있습니다.
- 복사 버튼으로 제목/HTML을 클립보드에 복사할 수 있습니다.
""")

url = st.text_input("네이버 블로그 URL 입력", "", placeholder="https://blog.naver.com/블로그ID/글번호")

col1, col2 = st.columns([1, 1])

if 'html' not in st.session_state:
    st.session_state['html'] = ''
    st.session_state['title'] = ''

if st.button("추출", type="primary"):
    if not url.strip():
        st.warning("URL을 입력하세요.")
    else:
        with st.spinner("HTML 추출 중... 잠시만 기다려주세요."):
            try:
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument(
                    "user-agent=Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
                )
                # 여기서부터 추가!
                if os.path.exists("/usr/bin/chromium-browser"):
                    options.binary_location = "/usr/bin/chromium-browser"
                elif os.path.exists("/usr/bin/chromium"):
                    options.binary_location = "/usr/bin/chromium"
                # 2. 모바일 주소 변환 함수
                def to_mobile_url(url):
                    import re
                    m = re.match(r'https?://blog.naver.com/([^/]+)/([0-9]+)', url)
                    if m:
                        blog_id, log_no = m.group(1), m.group(2)
                        return f"https://m.blog.naver.com/{blog_id}/{log_no}"
                    m = re.match(r'https?://blog.naver.com/PostView.naver\?blogId=([^&]+)&logNo=([0-9]+)', url)
                    if m:
                        blog_id, log_no = m.group(1), m.group(2)
                        return f"https://m.blog.naver.com/{blog_id}/{log_no}"
                    return url # 변환할 수 없으면 원본 URL 반환

                # 모바일 주소로 변환
                mobile_url = to_mobile_url(url.strip())

                # 리눅스용 chromium 경로 지정
                if os.path.exists("/usr/bin/chromium-browser"):
                    options.binary_location = "/usr/bin/chromium-browser"
                elif os.path.exists("/usr/bin/chromium"):
                    options.binary_location = "/usr/bin/chromium"

                html, title = extract_blog_html(mobile_url, options)
                st.session_state['html'] = html
                st.session_state['title'] = title
                st.success("추출 완료!")
            except Exception as e:
                st.session_state['html'] = ''
                st.session_state['title'] = ''
                st.error(f"오류 발생: {e}")

if st.session_state['html']:
    with col1:
        st.subheader("제목")
        st.code(st.session_state['title'], language=None)
        if st.button("제목 복사하기"):
            pyperclip.copy(st.session_state['title'])
            st.info("제목이 클립보드에 복사되었습니다.")
        st.subheader("본문 HTML")
        st.text_area("HTML 결과", st.session_state['html'], height=400)
        if st.button("본문 HTML 복사하기"):
            pyperclip.copy(st.session_state['html'])
            st.info("HTML이 클립보드에 복사되었습니다.")
    with col2:
        st.subheader("미리보기")
        st.components.v1.html(st.session_state['html'], height=600, scrolling=True) 