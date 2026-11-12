# Quantum Team Dashboard

다섯 명의 양자 회로 팀을 위한 공개 정적 대시보드. 팀 계획, 주차별 역할, 개인별 가이드, 공식 기준 예제의 로컬 검증 요약을 웹에서 읽습니다.

- 대상: 소연 · 지우 · 예찬 · 서진 · 서희
- 공개 URL: https://ys06146.github.io/quantum-team-dashboard/
- GitHub Pages: `main` 브랜치의 `/docs`
- 외부 패키지·로그인·분석 추적·API 키 없이 동작합니다.

## 최신 1주차 결과 · 2026.11.12 공개

- **Kaggle 실제 공개 점수: 1.00000 → 4.02469**, 두 번째 제출 Complete 확인.
- 공개 DQI v11 재검증·통합으로 DQI 비용 약 65.19배 개선. 다른 두 과제는 공식 기준본 유지.
- [작업 결과와 검증 근거](https://ys06146.github.io/quantum-team-dashboard/week1.html)
- [12장 발표 자료](https://ys06146.github.io/quantum-team-dashboard/meeting/jjeya-week1-meeting.html) · [발표 대본](https://ys06146.github.io/quantum-team-dashboard/speaker-notes.html)
- [공개 기록](content/records/) · [실행·검증·패키징 도구](work/week1/)

결과 원본은 `content/latest-results.json`, `content/week1-results.md`, `content/records/`, `content/meeting/`에 보관한다. `python build.py`가 웹 결과를 생성하므로 기존 계획·가이드 동기화 뒤에도 최신 결과가 유지된다. 새 실험 결과는 이 파일들을 명시적으로 갱신한다.

## 드라이브에서 수정하면 자동 반영

계획은 팀 폴더의 `quantum-team-plan-share.html`, 가이드는 각 원본 `*_GUIDE.md` 또는 `.html`에서 수정합니다. Windows 작업 스케줄러가 로그인 시와 2분 간격으로 문서를 확인하고, 변환·링크 검사 후 GitHub Pages로 배포합니다. PC가 켜져 있고 Google Drive와 인터넷에 연결돼 있어야 합니다.

**수정할 파일, 형식 선택 규칙, 켜기·끄기, 오류 확인: [AUTO_SYNC.md](AUTO_SYNC.md)**

```text
python sync_drive.py                 # 드라이브 원본 변환·검사만
python sync_drive.py --publish       # 지금 동기화
python sync_drive.py --status        # 최근 상태
python build.py                      # 현재 가져온 content로 사이트 생성
python -m unittest discover -s tests -v
```

`content/`와 `docs/`는 생성 결과입니다. `assets/`, `build.py` 등 사이트 코드를 고친 경우 검사 후 커밋·푸시하세요. 저장소에 미커밋 작업이 있으면 문서 자동 배포가 잠시 멈춥니다.

## 범위와 출처

기존 비교 기준은 2026-11-07 공식 기준 예제 full PASS 기록입니다. 11/11 새 환경 재현·DQI 개선본 검증과 실제 제출 결과는 별도의 최신 결과 페이지에 기록합니다. 계획 날짜와 담당별 산출물은 팀 실행 제안입니다.

공식 대회 ZIP, 회로·분자 적분 데이터, 가상환경, 계정 정보, 로컬 원본 로그는 이 저장소에 포함하지 않습니다. 공식 파일은 [Kaggle Data](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/data)에서 확보하고 팀 작업 폴더에서 사용합니다.

참조: [공식 평가 코드](https://www.kaggle.com/code/metric/google-quantum-ai-metric), [kickmix](https://github.com/quantumlib/Qualtran/tree/main/kickmix).
