# 1주차 실행·검증·패키징 도구

서진이 준비한 공통 도구의 공개 사본이다. [작업 결과](https://ys06146.github.io/quantum-team-dashboard/week1.html)와 [출처 및 검증 기록](../../content/records/)을 먼저 확인한다.

## 입력 준비

Python 3.12 환경에서 이 폴더를 작업 루트로 사용한다. 공식 대회 Data의 원본 ZIP을 `data/competition.zip`에 두고 `vendor/competition`에 원래 구조로 추출한다. [공식 Data](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/data)의 접근·이용 조건을 따른다. 공식 회로와 검증기, 분자 데이터, 제출 ZIP은 이 저장소에 재배포하지 않는다.

```sh
python3.12 -m venv .venv-local
.venv-local/bin/python -m pip install -r requirements.txt
.venv-local/bin/python scripts/environment_check.py
.venv-local/bin/python scripts/verify_assets.py
.venv-local/bin/python scripts/run_baselines.py --profile full --parallel 1 --workers 4
```

Windows는 대시보드의 [환경 안내](https://ys06146.github.io/quantum-team-dashboard/guides/jiwoo.html#section-2)를 따른다. 새 결과는 `reports/runs/<실행ID>`와 `logs/<실행ID>`에 생성된다. 전체 full은 오래 걸릴 수 있다. smoke는 축소 확인이며 full PASS로 표시하지 않는다.

## 공개 DQI 개선본 재현

[원저자 데이터셋 버전 11](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio)에서 DQI 파일을 준비한다. 최신 버전이 아닌 기록된 버전·해시를 확인한다. SHA-256은 `3ec03d5d3ae3d8fc2d7bf83d0e9b841f54d60f1ee900ac021be45d98526e5f20`이다.

같은 설정의 공식 invsqrt·화학 파일을 유지한 후보 폴더에 dqi.kmb만 교체하고 `run_baselines.py --submission-root <후보 폴더> --tasks dqi --profile full --workers 4`로 검사한다. 추가 입력 검사는 후보를 `artifacts/candidates/dqi-public-syed-v11/dqi.kmb`에 두고 `check_public_dqi_salts.py`로 실행한다. 재실행 결과는 새 기록이며 공개한 과거 결과를 덮어쓰지 않도록 별도 작업 복사본에서 실행한다.

## 전달과 패키징

`make_candidate_manifest.py`, `check_candidate_handoff.py`, `build_submission.py`의 `--help`로 현재 인자를 확인한다. 패키징은 새 실행에서 생성한 full PASS JSON과 입력 해시를 기준으로 한다. 공개 JSON에는 경로를 치환한 사본이 있으므로 원본 해시 대조용 실행 기록으로 그대로 사용하지 않는다. 이 도구는 Kaggle 업로드를 수행하지 않는다.

`analyze_dqi.py`는 당시 기준 기록 경로를 사용한다. 새 실험에서는 기록 경로를 해당 실행 ID로 맞춘다. 수치 민감도 예시는 실측 개선 결과와 구분한다.
