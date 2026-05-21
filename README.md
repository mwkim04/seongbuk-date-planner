# 성북구 데이트 코스 자동 추천 💗

카카오 로컬 API 기반으로 성북구 안에서 데이트 코스를 자동으로 짜주는 Streamlit 앱.

---

## 🚀 Streamlit Community Cloud 배포 (링크 만들기)

### 1. 깃헙 레포지토리 만들기

이 폴더를 깃헙에 올립니다. **`.env` 파일이나 실제 API 키가 들어간 `secrets.toml`은 절대 같이 올리면 안 됩니다** (`.gitignore`에 이미 포함되어 있음).

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/본인계정/레포이름.git
git push -u origin main
```

### 2. Streamlit Cloud에 배포

1. <https://share.streamlit.io> 접속 → 깃헙 계정으로 로그인
2. **New app** 클릭
3. 다음 정보 입력:
   - Repository: `본인계정/레포이름`
   - Branch: `main`
   - Main file path: `app.py`
4. **Advanced settings → Secrets** 칸에 아래 내용 붙여넣기:

   ```toml
   KAKAO_REST_API_KEY = "본인의_카카오_REST_API_키"
   ```

5. **Deploy** 클릭 → 잠시 기다리면 `https://본인앱이름.streamlit.app` 링크 생성 완료 ✨

---

## 💻 로컬 실행

```bash
# 1) 의존성 설치
python -m pip install -r requirements.txt

# 2) .env.example을 복사해서 .env 만들고 본인 카카오 API 키 입력
cp .env.example .env

# 3) 실행
python -m streamlit run app.py
```

---

## 🔑 카카오 REST API 키 발급

1. <https://developers.kakao.com> 접속
2. 내 애플리케이션 → 애플리케이션 추가하기
3. 앱 만든 후 **REST API 키** 복사
4. `.env` (로컬) 또는 Streamlit Cloud Secrets (배포) 에 입력

---

## 📁 파일 구조

```
.
├── app.py                          # 메인 Streamlit 앱
├── requirements.txt                # 파이썬 의존성
├── .env.example                    # 로컬용 환경변수 템플릿
├── .gitignore                      # .env 등 보호
├── .streamlit/
│   ├── config.toml                 # 테마/서버 설정
│   └── secrets.toml.example        # Streamlit Cloud Secrets 템플릿
└── README.md
```

---

## ⚠️ 보안 주의

- **`.env`와 `.streamlit/secrets.toml`은 절대 깃헙에 커밋하지 마세요.**
- 이미 노출된 API 키가 있다면 [카카오 개발자센터](https://developers.kakao.com)에서 즉시 재발급하세요.
- 키 노출이 의심되면 키를 삭제하고 새로 만드는 것을 권장합니다.

---

## ✨ 기능

- 카카오 API로 성북구 실제 장소만 수집
- 분위기 키워드 기반 코스 자동 추천 (상위 후보 안에서 랜덤 샘플링으로 다양성 확보)
- Folium 지도에 코스 순서 번호 표시
- DOCX 결과물 다운로드 지원
