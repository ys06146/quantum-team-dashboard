# 예찬 invsqrt 통합 재제출 · 2026-11-12

Kaggle 접수 완료, 채점 Pending. 아직 실제 점수 미확인.

예찬의 `12 / 17 / 28 / 27 / 28` 후보를 기존 DQI 개선 제출본에 통합했다. 예찬이 후보를 탐색했고 서진이 회로 재현·검증·통합·제출을 수행했다. 기존 DQI와 화학 12개 파일은 그대로이며 `invsqrt.kmb`만 교체했다.

- 예찬 소스: [고정 커밋 f7d9290](https://github.com/ys06146/jjeya/tree/f7d929063ea3ee75a2c26a642aa563623924392f/reports/yechan/2026-11-08).
- 공식 invsqrt 비용: 2,076,774.233715282 → 1,941,280.5598621224 (6.524237% 감소).
- 큐비트 256개, Toffoli 7,327개. 최대 허용오차 사용률 92.510770%.
- 재생성 회로 SHA-256: `53479d65b192b99868275f8f26e166b0a95715eef742b7d493515d8c64ce3057`.
- 예찬의 macOS·Kaggle 회로 해시와 동일. 서진 WSL에서 공식 전체 200,540,928샷 PASS, 예찬 공식 결과와 일치.
- 로컬 종합 예상치: 4.116238835774176. 실제 Kaggle 점수와 구분한다.
- DQI 원저자: [Syed Asad Ali (syed3000), 공개 데이터셋 v11](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio), Apache-2.0; SomeJoint C1 및 Ali Haydar Ozdag 기여 포함.
- 소연의 독립 검토는 별도이며 완료로 표시하지 않는다.

## 재현

공식 원본 자료와 고정된 kickmix 환경을 준비한 뒤 `work/week1` 도구에서 아래 설정으로 회로를 생성한다. 기존 파일이 없는 새 출력 경로를 사용한다.

```sh
python scripts/invsqrt_lab.py --output artifacts/yechan-reproduced/invsqrt.kmb --delta-bits 12 --coef-bits 17 --square-bits 28 --product-bits 27 --result-bits 28
python scripts/run_baselines.py --tasks invsqrt --profile full --workers 4 --invsqrt-file artifacts/yechan-reproduced/invsqrt.kmb
```

## 증거

[제출 결과](submission.json) · [통합 출처](provenance.json) · [서진 full 검증](invsqrt-full.json) · [예찬 원본 검증 기록](yechan-source-full.json) · [ZIP 파일별 해시](archive-manifest.json)

공식 회로·분자 데이터·제출 ZIP은 저장소에 재배포하지 않는다. 제출 ZIP과 원본 실행 기록은 팀 공유 Drive의 `seojin_work/week1`에 있다. 공개 사본은 개인 PC 루트 경로를 `<REPRO_ROOT>`로 치환했으며 [사본/원본 해시 대응](publication-manifest.json)을 제공한다.
