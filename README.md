# 💗 성북구 데이트 코스 자동 추천

카카오 로컬 API를 기반으로 서울 성북구의 실제 장소를 수집하고, 분위기·예산·이동수단 등의 조건에 맞춰 데이트 코스를 자동으로 추천하는 Streamlit 앱입니다. 코스는 지도에 순서대로 표시되며, 결과를 DOCX 문서로 내려받을 수 있습니다.

## ✨ 주요 기능
- 카카오 API 기반 실제 장소만 사용
- 카카오 API 병렬 수집(ThreadPool) + 프로세스 전역 캐시로 빠른 응답 (429 자동 재시도 포함)
- 분위기 키워드 / 예산 / 이동수단 / 장소 수 등 조건 입력
- 구간별 이동시간 계산 및 지도 시각화 (코스 순서 번호 표시)
- 같은 조건에서도 상위 후보 내 랜덤 샘플링으로 다양한 코스 생성
- 결과 DOCX 문서 다운로드

## 🔑 사전 준비: 카카오 REST API 키
1. [Kakao Developers](https://developers.kakao.com) 로그인
2. **내 애플리케이션 → 애플리케이션 추가**
3. **앱 키 → REST API 키** 복사

## 💻 로컬 실행
```bash
# 1. 저장소 클론
git clone https://github.com/<your-username>/seongbuk-date-planner.git
cd seongbuk-date-planner

# 2. (권장) 가상환경
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env
#  .env 파일을 열어 KAKAO_REST_API_KEY 값을 본인 키로 교체

# 5. 실행
streamlit run app.py
```

## ☁️ Streamlit Community Cloud 배포 (GitHub 연동)
1. 이 저장소를 본인의 GitHub 계정으로 push
2. [share.streamlit.io](https://share.streamlit.io) 접속 후 GitHub 로그인
3. **New app** → 저장소 / 브랜치 / `app.py` 선택
4. **Advanced settings → Secrets** 에 아래 입력 후 배포:
   ```toml
   KAKAO_REST_API_KEY = "발급받은_REST_API_키"
   ```

앱은 키를 `st.secrets` → 환경변수 → `.env` 순서로 자동으로 찾습니다. 배포 환경에서는 Secrets만 등록하면 됩니다.

## ⚠️ 보안 주의
- `.env` 와 `.streamlit/secrets.toml` 은 `.gitignore` 에 등록되어 있어 커밋되지 않습니다.
- API 키를 코드나 커밋에 절대 포함하지 마세요. 키가 노출되면 카카오 콘솔에서 재발급하세요.

## 📁 구조
```
seongbuk-date-planner/
├── app.py                          # 메인 Streamlit 앱
├── requirements.txt
├── .env.example                    # 로컬용 환경변수 템플릿
├── .gitignore
├── LICENSE
└── .streamlit/
    ├── config.toml                 # 테마 설정
    └── secrets.toml.example        # 배포용 Secrets 템플릿
```

## 📄 라이선스
MIT License
