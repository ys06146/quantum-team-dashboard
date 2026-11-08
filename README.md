# Quantum Team Dashboard

다섯 명의 양자 회로 팀을 위한 공개 정적 대시보드. 팀 계획, 주차별 역할, 개인별 가이드, 공식 기준 예제의 로컬 검증 요약을 웹에서 읽습니다.

- 대상: 소연 · 지우 · 예찬 · 서진 · 서희
- 공개 URL: https://ys06146.github.io/quantum-team-dashboard/
- GitHub Pages: `main` 브랜치의 `/docs`
- 외부 패키지·로그인·분석 추적·API 키 없이 동작합니다.

## 수정과 재생성

Python 3.12 이상에서:

```text
python build.py
python -m http.server 8765 --bind 127.0.0.1 --directory docs
```

브라우저에서 `http://127.0.0.1:8765/`를 확인합니다. `build.py`는 모든 내부 파일 링크와 문서 앵커도 검사합니다.

- `content/plan.html`: 3주 계획·역할 화면
- `content/tasks.json`: 15개 주차별 업무의 상세 설명
- `content/guides/*.md`: 개인별 가이드 원본
- `content/baselines.json`: 공개용 검증 결과 요약
- `assets/`: 공통 스타일과 인터랙션
- `docs/`: GitHub Pages 배포 파일

수정 후 `python build.py`를 실행하고 원본과 `docs`를 함께 커밋·푸시하면 Pages에 반영됩니다.

## 범위와 출처

공식 기준 예제의 로컬 full PASS 기록은 2026-11-07 기준입니다. 팀의 새 후보 검증 또는 Kaggle 제출 완료를 의미하지 않습니다. 계획 날짜와 담당별 산출물은 팀 실행 제안입니다.

공식 대회 ZIP, 회로·분자 적분 데이터, 가상환경, 계정 정보, 로컬 원본 로그는 이 저장소에 포함하지 않습니다. 공식 파일은 [Kaggle Data](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/data)에서 확보하고 팀 작업 폴더에서 사용합니다.

참조: [공식 평가 코드](https://www.kaggle.com/code/metric/google-quantum-ai-metric), [kickmix](https://github.com/quantumlib/Qualtran/tree/main/kickmix).
