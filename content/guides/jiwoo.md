# 지우 · Week 1 화학 실험 시작 안내

지우의 첫 목표는 **DFTHC-SOS 기준선의 수치 데이터와 회로 연결을 이해하고, 같은 회로를 재생성해 검증한 뒤 개선 가설을 정리하는 것**이다. 서진이 확보한 전체 PASS를 출발점으로 삼고, 지우는 수치 파라미터·각도 데이터·실험 근거를 만든다.

## 1. 먼저 이 순서로 파일 보기

| 순서 | 파일 | 읽고 남길 내용 |
|---|---|---|
| 1 | [화학 전체 검증 JSON](../results.html#dfthcsos) | `official_result`의 metrics, resources, score를 읽는다. |
| 2 | [공식 화학 설명](../resources.html#official-files) | Submission files → Worked example → Scoring 순서로 읽는다. |
| 3 | [기준 submission.npz](../resources.html#official-files) | 아래 Python 코드로 배열 이름·형상·자료형을 확인한다. |
| 4 | [공식 화학 검증기](../resources.html#official-files) | `load_inputs`, `evaluate_words`, `evaluate_circuits`, `score_from_metrics`를 읽는다. |
| 5 | [ANGLE 참조 생성기](../resources.html#official-files) | 각도 단어가 10개 회로로 바뀌는 흐름과 `--brot`, `--batch-size`를 확인한다. |
| 6 | [수치 계산](../resources.html#official-files) · [비용 계산](../resources.html#official-files) | 수치 오차, 정규화 계수와 전체 회로 자원 비용이 연결되는 지점을 확인한다. |
| 7 | [소연 안내서](soyeon.html) | 후보의 비교·채택 기준과 전달할 근거를 확인한다. |

분석 메모는 `jiwoo_work/week1`에, 실제 회로 실험은 `seojin_work/week1/artifacts/candidates/jiwoo` 아래에 두는 구성을 제안한다. 아래 모든 실행 명령은 공통 week1 폴더에서 시작한다.

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

## 3. 화학 기준값과 데이터 구조

서진이 확보한 full PASS의 주요 수치다. 확인일은 2026-11-07이며, 원본 JSON을 비교 기준으로 고정한다.

| 항목 | 기준값 | 확인할 의미 |
|---|---|---|
| 공식 로컬 비용 score | 3,355,599,588.3155375 | 동일 과제에서 낮을수록 유리 |
| lambda_eff | 49.301369250574396 | 비용식의 유효 정규화 계수 |
| 전체 Toffoli 비용 | 93,237 | ANGLE 순·역방향과 상태 준비·회전 비용 합계 |
| 전체 큐비트 | 730 | 전체 블록 인코딩 자원 |
| error_1 / error_2 | 0.00318519503 / 0.01863957063 Ha | 각각 0.020 Ha 이하 |
| Lambda / E_gap | 308.45593973 / 3.96547724 | Lambda>49.0, E_gap>3.914898, 0<E_gap<2 Lambda |
| brot / J / 회로 수 | 12 / 8 / 10 | 각도 단어의 비트 수 / 회로당 단어 수 / ceil(75/J) |
| ANGLE 큐비트 / 전체 검증 샷 | 119 / 254,464 | 각 ANGLE의 한도는 128큐비트, 주소당 64 shots |

공식 비용은 `lambda_eff × 전체 Toffoli × 전체 큐비트`다. 기준 ANGLE 회로에는 119큐비트가 있고, 전체 계산에는 730큐비트가 들어간다. 두 값을 구분해 실험표에 적는다. [원본 결과](../results.html#dfthcsos)

아래 코드를 PowerShell에 한 블록으로 붙여 넣어 NPZ의 구조를 확인한다.

```powershell
@'
from pathlib import Path
import numpy as np

path = Path("vendor/competition/sample_submission/dfthcsos/submission.npz")
with np.load(path, allow_pickle=False) as data:
    for name in data.files:
        value = data[name]
        print(name, value.shape, value.dtype)
    words = data["angle_words"]
    print("angle_words range", int(words.min()), int(words.max()))
'@ | & $Py -X utf8 -
if ($LASTEXITCODE -ne 0) { throw 'NPZ 읽기 오류를 확인하세요.' }
```

| 배열 | 역할 |
|---|---|
| U | (R, B, 76) 형상. 검증기는 회로에서 복원한 각도로 벡터를 계산한다. |
| W, H2_I | 분해의 가중치와 수치 파라미터 |
| H1_I, Hsym_lower | 제출 묶음에 들어가지만 공식 점수 계산에서는 제공된 고정 shift를 사용한다. |
| tree_edges | (75, 2) 트리. 각도 단어를 76차원 벡터로 복원하는 순서 |
| angle_words | 샘플 NPZ에 포함된 회로 생성용 정수 각도 표. 검증기는 실제 회로에서 읽은 단어를 평가한다. |

각도 단어는 `theta = pi × word / 2^(brot-1)`로 해석한다. 주소 행은 one-body 76개가 먼저 오고 뒤에 R×B개가 이어진다. 기준 표는 3,976행과 75열이다.

## 4. 회로 생성 전 수치 모델 확인

아래 코드는 기준 NPZ의 각도 표를 공식 수치 함수로 평가한다. `passes_accuracy`와 error_1, error_2, Lambda, E_gap, lambda_eff를 기록한다. 이 단계 다음에는 실제 회로의 전체 검증을 수행한다.

```powershell
@'
from pathlib import Path
import json
import sys
import numpy as np

sys.path.insert(0, str(Path("vendor/competition/verifiers").resolve()))
from dfthcsos.verify import load_inputs, evaluate_words, passes_accuracy

path = Path("vendor/competition/sample_submission/dfthcsos/submission.npz")
inputs = load_inputs(path)
with np.load(path, allow_pickle=False) as data:
    metrics = evaluate_words(inputs, data["angle_words"], data["tree_edges"], 12)
print(json.dumps(metrics, indent=2))
print("passes_accuracy", passes_accuracy(metrics))
'@ | & $Py -X utf8 -
if ($LASTEXITCODE -ne 0) { throw '수치 모델 평가 오류를 확인하세요.' }
```

기준 데이터에서는 `passes_accuracy True`와 위 표에 가까운 수치가 기대된다. 차이가 나면 사용한 파일, 패키지 버전, 소수점 차이를 기록하고 서진·소연과 대조한다. 기준 FCIDUMP를 처음 읽을 때는 동기화 드라이브의 다운로드가 끝날 때까지 시간이 걸릴 수 있다.

## 5. 첫 작업으로 기준 회로 재생성

새 실험 폴더에 NPZ를 복사하고, 공식 생성기로 12비트·J=8 회로를 만든다. 기존 폴더가 있으면 새 실험 이름을 사용한다.

```powershell
$CandidateRoot = 'artifacts/candidates/jiwoo/baseline_rebuild'
$CandidateDir = Join-Path $CandidateRoot 'dfthcsos'
if (Test-Path -LiteralPath $CandidateRoot) {
    throw '새 실험 이름을 정해 CandidateRoot를 바꾸세요.'
}
New-Item -ItemType Directory -Path $CandidateDir | Out-Null
Copy-Item -LiteralPath 'vendor/competition/sample_submission/dfthcsos/submission.npz' -Destination $CandidateDir

& $Py vendor/competition/verifiers/dfthcsos/example_submission/angle_k_reference_circuit.py "$CandidateDir/submission.npz" $CandidateDir --brot 12 --batch-size 8 --format kmb
if ($LASTEXITCODE -ne 0) { throw 'ANGLE 회로 생성 오류를 확인하세요.' }
Get-ChildItem -LiteralPath $CandidateDir
```

`angle_k_0.kmb`부터 `angle_k_9.kmb`까지 10개와 `submission.npz`가 있는지 확인한다. 원본과 재생성 회로의 바이트 해시도 비교할 수 있다.

```powershell
0..9 | ForEach-Object {
    $Name = "angle_k_$_.kmb"
    $Original = Get-FileHash -LiteralPath "vendor/competition/sample_submission/dfthcsos/$Name" -Algorithm SHA256
    $Rebuilt = Get-FileHash -LiteralPath "$CandidateDir/$Name" -Algorithm SHA256
    [pscustomobject]@{ File = $Name; SameHash = ($Original.Hash -eq $Rebuilt.Hash) }
}
```

생성된 회로를 먼저 smoke, 다음 full로 검증한다. `--submission-root`에는 dfthcsos 폴더의 부모를 넘긴다.

```powershell
& $Py scripts\run_baselines.py --tasks dfthcsos --profile smoke --submission-root $CandidateRoot
if ($LASTEXITCODE -ne 0) { throw '축소 검증 로그를 확인하세요.' }

& $Py scripts\run_baselines.py --tasks dfthcsos --profile full --submission-root $CandidateRoot
if ($LASTEXITCODE -ne 0) { throw '전체 검증 로그를 확인하세요.' }
```

full의 주소당 샷 수는 64다. 새 실행 JSON·로그를 기록하고 baseline 비용·오차·큐비트와 비교한다. 같은 설정의 재생성이므로 기준과 같은 결과를 예상하며, 소수점 차이는 원본 값을 그대로 기록한다.

## 6. 기준 재현 다음의 개선 가설

첫 1주차에는 바꿀 요소, 예상 영향, 검사할 수치가 포함된 가설을 두 개 적는다. 아래는 실험 방향의 예시이며, 실제 개선 여부는 full 비용과 통과 결과로 판단한다.

- **J 변경**. 같은 12비트 각도 표에서 J=4와 J=8을 비교할 수 있다. 새로운 실험 폴더를 만들고 생성 명령의 `--batch-size`만 바꾼다. J=4에서는 19개 회로가 생성된다. 회로당 큐비트, 회로 수, 전체 Toffoli와 전체 큐비트의 변화를 비교한다.
- **각도 정밀도 변경**. brot 변경에 맞춰 실제 각도를 다시 양자화한 정수 단어 표를 만들고 수치 모델부터 평가한다. 기존 12비트 단어를 낮은 brot로 그대로 해석하면 각도 값이 달라지므로 단어 생성 방식도 함께 기록한다.
- **트리·분해 변경**. tree_edges와 그 트리에 맞는 각도 표를 함께 재생성한다. W·H2_I 변경도 복원 오차와 전체 비용을 함께 평가한다. 변경 변수 하나씩 비교한 뒤 조합 실험으로 확장한다.

제공된 ANGLE 생성기는 주어진 정수 단어 표에서 회로를 만드는 도구다. 새로운 분해·트리·양자화 후보를 만드는 코드는 지우의 후속 작업에 포함된다.

기준 error_2는 허용치 0.020 Ha의 약 93.2%를 사용한다. 정밀도를 낮추는 후보는 이 여유와 Lambda·E_gap 조건을 먼저 확인한다.

## 7. 서진·소연에게 넘길 묶음

서진에게 회로와 NPZ를 통합할 수 있는 입력을, 소연에게 비교 판단의 근거를 전달한다.

```text
jiwoo_work/week1/
  baseline_analysis.md
  experiment_plan.md

seojin_work/week1/artifacts/candidates/jiwoo/<실험ID>/
  dfthcsos/
    submission.npz
    angle_k_0.kmb ... angle_k_<K-1>.kmb
  experiment.md
  생성 코드 또는 정확한 생성 명령
```

`experiment.md`에는 다음 항목을 적는다.

- 실험 ID, 작성자·날짜, 기준 full 결과 경로.
- 변경한 요소와 값. brot, J, 트리, 분해 형상, 양자화 방법.
- 수치 모델의 error_1, error_2, Lambda, E_gap, lambda_eff와 통과 여부.
- 회로 full 결과의 score, 전체 Toffoli·큐비트, ANGLE 최대 큐비트, 샷 수.
- 기준 대비 비용 감소율, 실제 명령, Python·패키지 버전.
- 후보 전체 파일의 해시와 `reports/runs/<실행ID>/dfthcsos.json`, 대응 로그 경로.

공식 검증은 NPZ의 가중치·트리와 실제 회로에서 복원한 단어를 함께 사용하므로, 같은 실험에서 만든 NPZ와 전체 ANGLE 파일을 한 묶음으로 전달한다.

## 8. 1주차 완료 기준과 협업

완료 기준은 **기준 NPZ의 구조와 비용식을 설명하고, 기준 회로를 재생성해 full 결과를 남기며, 개선 가설 두 개와 탐색 범위를 정리하는 것**이다.

- 서진과 후보 폴더 구조, 배열 형상, 각도 단어·트리의 전달 방식을 맞춘다.
- 소연에게 수치 오차표와 전체 검증 근거를 보내 독립 비교를 요청한다.
- 2주차에는 합의한 방향으로 후보를 만들고 공식 비용이 감소하는지 확인한다.

자료 기준은 [공식 화학 설명](../resources.html#official-files), 로컬 검증기와 참조 생성기, 2026-11-07 full 결과다. 역할은 [팀 실행 계획](../plan.html)을 따른다.
