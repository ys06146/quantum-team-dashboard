# 서진 · Week 1 실행·통합 가이드

서진은 공통 실행 환경, 세 과제의 검증 기록, 회로 통합과 제출 묶음을 담당한다. 예찬·지우가 후보 생성 코드와 설정을 만들고, 서희가 화학 지표를 검토하며, 소연이 독립 비교를 맡는다.

## 1. 먼저 확인할 기준 결과

[검증 결과 페이지](../results.html)에 세 공식 예제의 full PASS 기록을 정리했다. invsqrt는 200,540,928 shots, DQI는 102,400 shots, DFTHC-SOS는 254,464 shots를 검사했다. 기록은 2026-11-07 기준이며 새로운 후보의 통과를 뜻하지 않는다.

| 먼저 볼 파일 | 확인할 내용 |
|---|---|
| `reports/BASELINE_RESULTS.md` | 과제별 기준 비용·샷 수·재실행 환경 |
| `reports/baseline_manifest.json` | 확정된 과제별 원본 결과 경로 |
| `scripts/run_baselines.py` | full·smoke 분리, 입력·소스 해시와 실행 로그 저장 |
| `scripts/environment_check.py` | Python·패키지 버전과 kickmix 동작 확인 |
| `scripts/verify_assets.py` | 공식 ZIP과 추출한 파일의 무결성 확인 |

파일은 공통 `seojin_work/week1` 기준이다. [자료 안내](../resources.html#environment)에서 공식 데이터와 작업 폴더를 확인한다.

## 2. 실행 환경 확인

공유 가상환경은 기반 Python이 3.13으로 바뀌고 바이너리 패키지가 3.12로 남은 이력이 있다. 개인 PC에 Python 3.12 가상환경을 만들고 kickmix 1.0.0, NumPy 2.2.6, SciPy 1.15.3을 확인한다. 구체적인 Windows 준비 명령은 [지우 가이드의 환경 준비](jiwoo.html#section-2)를 따른다.

새 실행에서는 Python 버전, 패키지 버전, 운영체제, 작업 경로를 실제로 기록한다. 과거 결과를 새 PC의 동작 확인으로 대신하지 않는다. Windows에서 KMB를 읽을 때는 공통 week1 폴더에서 영문 상대 경로를 사용한다.

## 3. 세 과제 검증과 기록

환경 준비에서 설정한 `$Py`를 사용하고, 작업 위치를 `seojin_work/week1`로 맞춘다.

```powershell
& $Py scripts\environment_check.py
& $Py scripts\verify_assets.py
& $Py scripts\run_baselines.py --profile full --parallel 3 --workers 1 --invsqrt-workers 8
```

마지막 옵션은 invsqrt의 Windows 프로세스 분배를 보완한다. 원본 작업·샷·배치·시드를 유지하고 각 프로세스가 작업의 동일성을 확인한다. CPU·메모리 여유에 맞춰 워커 수를 정한다. DQI는 대용량 회로를 사용하므로 운영체제와 동시 실행 메모리도 기록한다.

`reports/runs/<실행ID>`의 JSON과 대응하는 `logs/<실행ID>`를 한 묶음으로 보존한다. 전체 검증이 끝나지 않은 실행은 완료된 PASS로 표시하지 않는다.

## 4. 후보를 전달받을 때

| 담당 | 받아야 할 파일과 근거 |
|---|---|
| 예찬 | invsqrt 후보 KMB, 생성 코드·설정, 모델 오차와 경계 입력 분석 |
| 지우 | 같은 실험에서 만든 NPZ·전체 ANGLE 회로, 트리·정밀도·분해 설정 |
| 서희 | 화학 지표 해석, 오차 여유, 후보에 대한 채택·보류 근거 |
| 소연 | 기준 대비 공식 비용·오류·자원 비교와 독립 재검증 로그 |

각 후보에 실험 ID, 파일 해시, 생성 명령, 환경 버전, 수치 모델 결과와 full 결과를 연결한다. 화학 후보는 NPZ와 ANGLE 묶음이 같은 설정인지 확인한다.

## 5. 첫 주 완료 기준

- 팀원이 공통 안내만으로 환경을 준비하고 공식 예제를 실행할 수 있다.
- 세 과제의 확정 기준 JSON·원본 로그·파일 해시를 찾을 수 있다.
- full과 smoke, 수치 모델 결과가 명확히 구분된다.
- invsqrt·DQI·dfthcsos의 제출 구조를 점검한 ZIP 초안이 있다.
- 지우·예찬과 후보 전달 형식을 합의하고, 소연이 기준 기록을 독립 확인한다.

웹 대시보드는 계획·가이드·확정 결과를 읽는 공간이다. 실제 회로 생성과 검증은 로컬 공통 작업 폴더에서 실행한다.

## 6. 팀 문서 수정과 자동 반영

계획과 가이드는 드라이브 원본에서 수정한다. 저장한 변경은 자동 동기화를 거쳐 팀 대시보드에 반영된다. 계획은 `quantum-team-plan-share.html`, 개인 가이드는 각 `*_GUIDE.md` 또는 `.html`을 사용한다.

운영 PC가 로그인·연결된 동안 2분마다 변경을 확인한다. PC가 꺼져 있으면 다음 로그인 뒤 반영된다. 수정할 정확한 파일과 상태 확인 방법은 [자동 반영 안내](https://github.com/ys06146/quantum-team-dashboard/blob/main/AUTO_SYNC.md)를 따른다.
