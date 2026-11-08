# 소연 · Week 1 검증 시작 안내

소연의 첫 목표는 **서진이 확보한 세 공식 기준선의 통과 조건과 비용을 정리하고, 본인 실행으로 재현 여부를 확인하는 것**이다. 이 검증표가 이후 예찬·지우 후보를 채택하는 공통 기준이 된다.

## 1. 먼저 이 순서로 파일 보기

| 순서 | 파일 | 읽고 남길 내용 |
|---|---|---|
| 1 | [전체 검증 요약](../results.html) | 세 과제의 full PASS와 재실행 환경을 확인한다. |
| 2 | [기준 결과 목록](../results.html) | 과제별 확정 JSON 경로를 찾는다. |
| 3 | [공통 실행기](../resources.html#team-files) | full·smoke 조건, 입력 해시, 원본 로그 저장 방식을 확인한다. |
| 4 | [DQI 검증기](../resources.html#official-files) | `clopper_pearson_upper_bound`, `repetition_overhead`, `verify`를 읽고 오류율 상한과 비용 관계를 정리한다. |
| 5 | [invsqrt 검증기](../resources.html#official-files) | 입력 범위, 상대오차, 위상·보조 상태와 비용 계산을 확인한다. |
| 6 | [DFTHC-SOS 공식 설명](../resources.html#official-files) | 수치 통과 조건, 회로 검사, 비용식과 Statistical interpretation 절을 읽는다. |
| 7 | [지우 안내서](jiwoo.html) · [예찬 안내서](yechan.html) | 어떤 후보와 분석 자료를 전달받게 되는지 파악한다. |

첫 산출물은 `soyeon_work/week1/baseline_review.md`에 작성한다. 이 경로는 팀 작업을 위한 안내서의 제안이다.

## 2. 내 PC에서 실행 준비

2026-11-07 확인 결과, 공유 폴더의 기존 가상환경은 Python 3.13을 불러오고 설치 패키지는 3.12용이었다. 아래 명령은 각자 PC의 로컬 폴더에 Python 3.12 가상환경을 만든다. 처음 준비할 때는 [Python 3.12.4 공식 배포 페이지](https://www.python.org/downloads/release/python-3124/)에서 Windows 64비트 설치 파일을 설치하고, PowerShell의 `py -0p` 목록에 3.12가 보이는지 확인한다.

공유 드라이브 문자가 다르면 `$ProjectRoot`에 본인 PC의 jjeya 폴더 경로를 지정한다. 이후의 모든 명령은 이 PowerShell 창에서 실행한다.

```powershell
Set-Location -LiteralPath (Join-Path $ProjectRoot 'seojin_work\week1')
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$Venv = Join-Path $env:LOCALAPPDATA 'jjeya\week1-py312'
$Py = Join-Path $Venv 'Scripts\python.exe'

if (-not (Test-Path -LiteralPath $Py)) {
    py -3.12 -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 설치와 py -0p 목록을 확인하세요.' }
}
& $Py -c 'import sys; assert sys.version_info[:2] == (3,12), sys.version'
if ($LASTEXITCODE -ne 0) { throw '이 로컬 가상환경의 Python 버전을 확인하세요.' }
& $Py -m pip install --disable-pip-version-check -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw '패키지 설치 오류를 확인하세요.' }
& $Py -m pip check
if ($LASTEXITCODE -ne 0) { throw '패키지 의존성 오류를 확인하세요.' }
& $Py -c 'import sys, importlib.metadata as m, kickmix, numpy, scipy; print(sys.version); print({p:m.version(p) for p in ("kickmix","numpy","scipy")})'
if ($LASTEXITCODE -ne 0) { throw '패키지 로딩 오류를 확인하세요.' }
```

확인할 버전은 kickmix 1.0.0, NumPy 2.2.6, SciPy 1.15.3이다. 다음 날 새 창을 열면 작업 폴더 이동과 `$env:PYTHONUTF8`, `$Venv`, `$Py` 설정을 다시 실행한다.

.kmb 파일은 아래 예시처럼 영문 상대 경로를 사용한다. 동기화 드라이브에서 대용량 파일을 읽는 속도가 느리면 week1 작업 자료를 로컬 디스크에 복사하고 그 위치에서 실행한다. 가상환경은 위 로컬 경로의 것을 사용하고, 공유할 때는 실행 결과와 로그를 함께 옮긴다.

## 3. 현재 확보한 기준 결과

2026-11-07에 확인한 공식 기본 샘플의 full 결과다. 숫자는 같은 과제의 후보와 비교할 기준 비용이다. 각 JSON의 `official_result`에 상세 수치가 있다.

| 과제 | 전체 검증 | 공식 로컬 비용 | 큐비트 | 검증 샷 | 원본 |
|---|---|---|---|---|---|
| invsqrt | PASS | 2,076,774.233715282 | 260 | 200,540,928 | [invsqrt JSON](../results.html#invsqrt) |
| DQI | PASS | 24,439,463,583,672.93 | 1,893 | 102,400 | [DQI JSON](../results.html#dqi) |
| DFTHC-SOS | PASS | 3,355,599,588.3155375 | 730 | 254,464 | [DFTHC-SOS JSON](../results.html#dfthcsos) |

invsqrt는 Windows Python 3.12.4와 12개 워커, DQI는 Ubuntu Python 3.12.3과 공식 4개 워커, DFTHC-SOS는 Windows Python 3.12.4에서 실행했다. 라이브러리는 위 고정 버전을 사용했다. 실행 시간은 환경의 영향을 받으므로 PC와 워커 수도 함께 기록한다.

최신 기본 결과는 [기준 결과 목록](../results.html)에서 고른다. `latest-full.json`은 가장 최근 실행 묶음만 담기 때문에 한 파일에 세 과제 모두가 들어 있지 않을 수 있다.

## 4. 기준선 직접 재현하기

먼저 invsqrt 축소 검증으로 Python과 실행 경로를 확인한다.

```powershell
& $Py scripts\run_baselines.py --tasks invsqrt --profile smoke
if ($LASTEXITCODE -ne 0) { throw '출력된 run 폴더의 invsqrt.json과 로그를 확인하세요.' }
```

smoke가 통과하면 다음 세 명령을 차례로 실행한다. invsqrt는 전체 3,133,452개 입력을 확인한다. DQI는 Windows에서 공식 실행기가 순차 방식으로 동작하므로 Ubuntu에서 측정한 99초보다 오래 걸릴 수 있다.

```powershell
& $Py scripts\run_baselines.py --tasks invsqrt --profile full --invsqrt-workers 4
if ($LASTEXITCODE -ne 0) { throw 'invsqrt 전체 검증 결과를 확인하세요.' }

& $Py scripts\run_baselines.py --tasks dqi --profile full --workers 1
if ($LASTEXITCODE -ne 0) { throw 'DQI 전체 검증 결과를 확인하세요.' }

& $Py scripts\run_baselines.py --tasks dfthcsos --profile full
if ($LASTEXITCODE -ne 0) { throw 'DFTHC-SOS 전체 검증 결과를 확인하세요.' }
```

각 명령이 출력하는 `reports/runs/<실행시각>-full` 경로를 따로 적는다. 대응 로그는 `logs/<실행시각>-full`에 있다. 소연의 완료 기록에는 실제 실행한 PC·날짜·명령과 이 경로를 넣는다.

## 5. 과제별로 무엇을 확인하나

| 과제 | 확인할 통과 조건 | 기준선에서 읽을 수치 |
|---|---|---|
| invsqrt | n_p=10, x=1..3,133,452, 입력마다 64 shots. 입력 보존, 보조 큐비트 정리, 공식 위상·정밀도 검사 | `worst_error_over_tolerance=0.4769116098`, 최악 x=2,588,411, 전체 200,540,928 shots |
| DQI | m=4095, n=70, degree=12, 102,400 shots. 공식 오류율 상한이 1/16 미만 | 값 오류 0, 위상 오류 0, `effective_error_rate=0.00086605873`, `log2_delta=-128` |
| DFTHC-SOS | error_1과 error_2 각각 0.020 Ha 이하, Lambda>49.0, E_gap>3.914898, 0<E_gap<2 Lambda. 각 ANGLE 회로 최대 128큐비트와 공식 상태 검사 | error_1=0.00318519503, error_2=0.01863957063, Lambda=308.45593973, E_gap=3.96547724 |

JSON의 `profile`, `verification_scope`, `command`, `input_files`, `verifier_sources`, `exit_code`와 `official_result`를 함께 확인한다. 실행 상태와 공식 결과가 모두 PASS이고 정상 종료했는지 점검한다.

DQI의 0건 오류를 읽을 때는 공식 상한값까지 함께 적는다. 같은 파일과 같은 salt의 재실행은 같은 의사난수 표본을 사용하므로 재현성 확인으로 기록한다. 다른 PC에서 소연이 실행했다는 사실과 통계적으로 새 표본을 얻었다는 사실은 각각 확인해야 한다.

DFTHC-SOS는 주소별 회로 검사와 수치 제약을 함께 통과해야 한다. 상세 확률 해석은 공식 설명의 Statistical interpretation 절을 따른다.

## 6. 후보 비교와 채택 기록

후보를 받으면 변경 내용, 생성 코드·명령, 회로와 NPZ, 실행 JSON, 원본 로그를 한 묶음으로 받는다. 동일 과제·입력 조건·검증기 버전에서 baseline과 candidate를 비교한다.

비용 개선율은 `(baseline_score - candidate_score) / baseline_score × 100`으로 기록한다. 예를 들어 10,000에서 9,000으로 내려가면 10% 비용 감소다. 세 과제의 공식 로컬 비용은 과제별 비용식에 따라 낮을수록 유리하다.

예찬의 invsqrt 후보를 재검증할 때는 실제 받은 영문 파일 경로를 `$Candidate`에 넣는다.

```powershell
$Candidate = 'artifacts/candidates/yechan/received_candidate.kmb'
if (-not (Test-Path -LiteralPath $Candidate)) { throw '실제 받은 후보 경로로 바꾸세요.' }
& $Py scripts\run_baselines.py --tasks invsqrt --profile full --invsqrt-file $Candidate --invsqrt-workers 4
```

지우 후보는 `후보루트/dfthcsos/submission.npz`와 `angle_k_*.kmb`가 함께 있어야 한다. 지우 안내서의 기준 회로 재생성 예시를 실행한 뒤에는 다음처럼 검증한다.

```powershell
& $Py scripts\run_baselines.py --tasks dfthcsos --profile full --submission-root artifacts/candidates/jiwoo/baseline_rebuild
```

| 상황 | 기록할 판단 |
|---|---|
| full PASS이며 공식 비용이 감소 | 채택 후보. 기준과 후보 해시, 감소율, 오차 여유를 기록한다. |
| full PASS이며 비용이 같거나 증가 | 재현 성공 또는 성능 변화로 기록하고 개선 가설을 다시 본다. |
| 수치 모델 또는 smoke만 통과 | 전체 검증 대기 |
| FAIL / ERROR | 로그에서 정확도·회로·파일·환경 원인을 구체적으로 기록한다. |
| RUNNING인데 프로세스와 로그 갱신이 없음 | 실행 미완료로 기록하고 서진에게 실행 ID를 전달한다. |

## 7. 소연이 작성해 넘길 것

```text
soyeon_work/week1/
  baseline_review.md
  candidate_comparison.md
```

`baseline_review.md`에는 과제별 통과 조건, 기준 수치, 소연의 실행 ID와 로그 경로, 기준과의 차이, 확인자·확인일을 적는다. `candidate_comparison.md`에는 후보가 도착할 때마다 아래 항목을 채운다.

- 후보 ID와 작성자, 비교 대상 baseline 실행 ID.
- 입력 파일과 공식 검증기 해시, Python·패키지 버전.
- full 통과 여부, 샷 수, 오차·오류율 상한, 큐비트, 공식 비용, 실행 시간.
- 비용 감소율과 변경한 요소, 채택·보류 판단 및 근거.
- 원본 JSON·로그·생성 코드의 경로.

원본 로그는 공통 `reports/runs`와 `logs` 아래에 보존하고 리뷰 문서에서 링크한다. 로컬 복사본으로 실행했다면 실행별 폴더를 공유 공간으로 옮겨 함께 전달한다.

## 8. 1주차 완료 기준과 협업

1주차 완료 기준은 **세 과제의 통과 조건을 설명하고, 소연이 직접 수행한 전체 검증 기록을 남기며, 이후 후보를 비교할 표를 준비하는 것**이다.

- 서진에게 환경·경로 문제와 재현 차이를 전달하고, 통과한 실행 ID를 공유한다.
- 지우에게 화학 수치 오차와 전체 비용 중 어떤 항목을 비교할지 전달한다.
- 예찬에게 invsqrt의 최악 오차와 전체 공식 비용 기준을 전달한다.
- 서진의 제출 ZIP이 준비되면 ZIP에 든 파일의 해시와 검증한 파일의 해시를 대조한다.

현재 확보된 세 PASS는 서진의 기준선 기록이다. 소연의 독립 재실행 여부는 새 실행 기록과 함께 남긴다.

자료 기준은 이 폴더의 공식 검증기와 2026-11-07 full 결과다. 역할은 [팀 실행 계획](../plan.html)을 따른다.
