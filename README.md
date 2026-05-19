# 성북구 데이트 코스 자동 추천 v42

## 실행
1. `.env.example`을 복사해서 `.env` 파일 생성
2. `.env` 안에 `KAKAO_REST_API_KEY=본인_REST_API_키` 입력
3. 터미널에서 실행

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## v42 수정
- 조건 입력에서 요일/방문시간 제거
- 상단에 `keyboard_double...` 텍스트가 보이지 않도록 사이드바 접기 버튼 숨김
- 전체 배경 흰색 유지
- 지도에 코스 순서 번호 표시
- 카카오 API 기반 실제 장소만 사용


## 최종 보완
- 같은 조건으로 눌러도 상위 후보 안에서 랜덤 샘플링하여 더 다양한 코스를 생성합니다.
- 조건 입력 사이드바의 빨간 포인트 색상을 핑크로 고정했습니다.


## Streamlit Cloud 배포

GitHub에는 `.env` 파일을 올리지 말고, Streamlit Cloud의 **App settings → Secrets**에 아래처럼 입력하세요.

```toml
KAKAO_REST_API_KEY = "본인_REST_API_키"
```

로컬 실행은 기존처럼 `.env` 파일을 사용하면 됩니다.
