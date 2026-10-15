import streamlit as st
import random
import json
import os

DATA_FILE = "quiz_data.json"

DEFAULT_DATA = [
    {"era": "고조선", "q": "고조선의 사회 질서를 유지하기 위해 제정된 8개의 법 조항은?", "a": "범금 8조 (8조법)", "memorized": False},
    {"era": "삼국시대", "q": "백제 근초고왕 때 고구려 고국원왕을 전사시킨 전투 지역은?", "a": "평양성", "memorized": False},
    {"era": "남북국시대", "q": "발해 무왕 때 장문휴를 보내 공격한 당나라의 산둥반도 지역은?", "a": "등주", "memorized": False},
    {"era": "고려", "q": "고려 광종이 호족의 세력을 약화시키고 왕권을 강화하기 위해 실시한 노비 해방 법안은?", "a": "노비안검법", "memorized": False},
    {"era": "조선 전기", "q": "세조가 현직 관리에게만 수조권을 지급하기 위해 실시한 토지 제도는?", "a": "직전법", "memorized": False},
    {"era": "개항기", "q": "1882년 임오군란의 결과로 조선과 일본이 체결한 조약은?", "a": "제물포 조약", "memorized": False}
]

def load_quiz_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if "memorized" not in item:
                    item["memorized"] = False
            return data
    else:
        save_quiz_data(DEFAULT_DATA)
        return [item.copy() for item in DEFAULT_DATA]

def save_quiz_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

st.title("🇰🇷 나만의 한국사 암기장")

quiz_data = load_quiz_data()

# 세션 상태 초기화
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0

# 미암기 필터
unmemorized_only = st.toggle("미암기 문제만 보기", value=False)

filtered_data = [item for item in quiz_data if not item.get("memorized", False)] if unmemorized_only else quiz_data

# 현황 표시
total_cnt = len(quiz_data)
memo_cnt = sum(1 for item in quiz_data if item.get("memorized", False))
st.markdown(f"📊 **암기 현황:** {memo_cnt} / {total_cnt} 완료 (남은 문제: {total_cnt - memo_cnt}개)")
st.divider()

if not filtered_data:
    if total_cnt > 0 and unmemorized_only:
        st.success("🎉 축하합니다! 모든 문제를 다 외웠습니다!")
    else:
        st.warning("등록된 문제가 없습니다. 아래에서 문제를 추가해 주세요!")
else:
    if st.session_state.current_idx >= len(filtered_data):
        st.session_state.current_idx = 0

    current_item = filtered_data[st.session_state.current_idx]

    # 카드 박스 느낌의 출력
    st.markdown(f"### `[{current_item['era']}]` ({st.session_state.current_idx + 1}/{len(filtered_data)})")
    st.markdown(f"<div style='text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0;'>Q. {current_item['q']}</div>", unsafe_allow_html=True)

    # 정답 보기 토글
    show_ans = st.checkbox("정답 보기", key="show_ans_box")
    if show_ans:
        st.info(f"정답: **{current_item['a']}**")

    # 암기 완료 체크 버튼
    is_memo = current_item.get("memorized", False)
    btn_label = "↩️ 미암기 상태로 되돌리기" if is_memo else "⭕ 암기 완료로 표시"
    if st.button(btn_label, use_container_width=True):
        # 원본 데이터에서 해당 문제 찾아 상태 변경
        for original in quiz_data:
            if original["q"] == current_item["q"]:
                original["memorized"] = not is_memo
                break
        save_quiz_data(quiz_data)
        st.rerun()

    st.divider()

    # 이전 / 다음 / 랜덤 버튼
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.current_idx = (st.session_state.current_idx - 1) % len(filtered_data)
            st.rerun()
    with col2:
        if st.button("🔀 랜덤", use_container_width=True):
            random.shuffle(quiz_data)
            save_quiz_data(quiz_data)
            st.session_state.current_idx = 0
            st.rerun()
    with col3:
        if st.button("다음 ➡️", use_container_width=True):
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(filtered_data)
            st.rerun()

# 문제 추가 및 삭제 폼
with st.expander("➕ 새 문제 추가 / 🗑️ 문제 삭제"):
    with st.form("add_form", clear_on_submit=True):
        new_era = st.selectbox("시대 선택", ["선사·고조선", "삼국·남북국", "고려", "조선 전기", "조선 후기", "근대(개항기~일제)", "현대"])
        new_q = st.text_area("문제 입력")
        new_a = st.text_input("정답 입력")
        submitted = st.form_submit_button("저장하기")
        if submitted:
            if new_q.strip() and new_a.strip():
                quiz_data.append({"era": new_era, "q": new_q.strip(), "a": new_a.strip(), "memorized": False})
                save_quiz_data(quiz_data)
                st.success("✅ 새 문제가 추가되었습니다!")
                st.rerun()
            else:
                st.error("⚠️ 문제와 정답을 모두 입력해 주세요!")

    st.divider()

    # 삭제 기능
    if quiz_data:
        delete_target = st.selectbox("삭제할 문제 선택", options=range(len(quiz_data)), format_func=lambda i: f"[{quiz_data[i]['era']}] {quiz_data[i]['q'][:20]}...")
        if st.button("선택한 문제 삭제", type="primary"):
            quiz_data.pop(delete_target)
            save_quiz_data(quiz_data)
            st.success("🗑️ 삭제되었습니다.")
            st.rerun()
