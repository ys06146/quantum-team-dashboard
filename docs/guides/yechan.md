# 예찬 · Week 1 실험 시작 안내

예찬이 직접 할 일은 **역제곱근 근사와 고정소수점 비트 폭의 후보를 만들고, 정확도와 회로 비용을 함께 비교하는 것**이다. 서진이 준비한 공통 환경과 공식 검증기를 그대로 사용하면 된다.

## 1. 먼저 이 순서로 파일 보기

| 순서 | 파일 | 무엇을 확인하고 어떻게 쓰나 |
|---|---|---|
| 1 | [검증 결과 요약](../results.html) | 세 공식 기본 예제의 실제 상태·검증 범위·비용을 읽는다. 후보 비교의 출발점이다. |
| 2 | [공통 환경 README](../resources.html#environment) | 실행 위치, Python 경로, 폴더 구조를 확인한다. 개인 PC의 Python 3.12 환경을 먼저 확인한다. |
| 3 | [실험 실행 도구](../resources.html#team-files) | 비트 폭을 인자로 바꿔 전 입력 수치 모델 검사와 후보 `.kmb` 생성을 한다. |
| 4 | [공식 역제곱근 참조 코드](../resources.html#official-files) | `Precision` → `fixed_point_model` → `relative_error` → `build_nr_circuit` 순서로 읽는다. 계산 방식과 회로 생성이 연결되는 지점이다. |
| 5 | [공식 역제곱근 검증기](../resources.html#official-files) | `ProblemSpecInvSqrt`, `validate_registers`, `verify`를 읽고 입력·보조 큐비트·위상 검사와 비용 계산을 이해한다. |
| 6 | [기본 수치 모델 결과](../resources.html#team-files) | 기본 비트 폭, 최악 입력, 상대오차, 큐비트 수, 정적 Toffoli 수를 확인한다. |
| 7 | [재생성한 기본 회로](../resources.html#team-files) | 직접 읽는 텍스트가 아니라 검증기에 넣는 바이너리다. 공식 예제와 같은 회로인지 해시로 확인한다. |

공식 배포 원본은 `vendor/competition`에 있다. 그 안의 코드를 직접 덮어쓰면 기준 비교가 깨지므로, 수식이나 회로 로직을 바꿀 때는 `artifacts/candidates/yechan` 아래에 복사본을 만든다. 비트 폭만 바꾸는 첫 실험은 복사 없이 제공된 실험 도구로 가능하다.

## 2. 지금 바로 실행하기

먼저 [지우 가이드의 환경 준비](jiwoo.html#section-2)로 개인 Python 3.12 환경과 `$Py`를 설정한다. 아래 명령은 그 PowerShell 창에서 실행한다.

PowerShell에서 다음 두 줄을 먼저 실행한다. 이하 명령은 모두 `week1`을 기준으로 한다.

```powershell
Set-Location -LiteralPath (Join-Path $ProjectRoot 'seojin_work\week1')
$env:PYTHONUTF8 = '1'
```

환경 확인과 빠른 기준 예제 확인:

```powershell
& $Py scripts\environment_check.py
& $Py scripts\run_baselines.py --tasks invsqrt --profile smoke
```

초기 기준 환경은 Python 3.12.4, kickmix 1.0.0, NumPy 2.2.6, SciPy 1.15.3이었다. 공유 가상환경에는 기반 Python 버전 변경 이력이 있으므로 지우 가이드 2절대로 개인 PC의 Python 3.12 환경을 준비하고 $Py를 사용한다. `Activate.ps1` 없이 위 경로의 Python을 직접 사용한다. `smoke`는 x=1..4096만 검사하므로 전체 통과로 해석하면 안 된다.

## 3. 기준값을 먼저 이해하기

공식 입력은 `n_p=10`, 22비트 x 레지스터, `1 ≤ x ≤ 3,133,452`이다. 회로는 x를 보존하면서 역제곱근에 해당하는 위상을 적용하고, 사용한 보조 큐비트를 0으로 돌려놓아야 한다.

공식 참조 알고리즘은 x를 정규화해 M을 [1,4)로 옮기고, 네 구간의 3차 다항식으로 초기 근사를 만든 뒤 Newton–Raphson 보정을 한다. 역연산으로 보조 상태를 지우는 과정까지 회로 비용에 들어간다.

| 설정 | 기본값 | 예찬이 살펴볼 내용 |
|---|---:|---|
| `delta_bits` | 14 | 구간 내 delta의 절삭 정밀도 |
| `coef_bits` | 17 | 다항식 계수와 Horner 중간값의 정밀도 |
| `square_bits` | 28 | 초기 근사값 제곱의 정밀도 |
| `product_bits` | 28 | M과 제곱값의 곱, 보정항의 정밀도 |
| `result_bits` | 29 | 마지막 곱의 정밀도 |

기본 수치 모델은 3,133,452개 입력을 모두 검사했다. 최대 상대오차는 약 `2.8426147154e-8`, 최악 입력은 `x=2,588,411`, 허용오차 `2^-24 ≈ 5.9604644775e-8`의 약 47.69%다. 생성 회로는 260큐비트, 정적 Toffoli-like 7,735개다. 이 정적 개수는 위상 회전 합성 비용까지 포함한 공식 `score`와 다르다.

## 4. 첫 후보 만들기

한 번에 비트 폭 하나만 바꾼다. 아래는 `coef_bits=16`을 조사하는 명령 예시이며, 개선이나 통과를 보장하는 추천값이 아니다.

먼저 수치 모델만 확인한다:

```powershell
& $Py scripts\invsqrt_lab.py --coef-bits 16 --model-only --output artifacts\candidates\yechan\coef16_model_new.kmb
```

이 명령은 `.kmb`를 만들지 않고 `coef16_model.model.json`만 만든다. `model_within_tolerance`, `worst_relative_error`, `worst_x`, `error_over_tolerance`를 확인한다. 오버플로 예외나 허용오차 초과가 나오면 해당 조건을 실패 실험으로 기록한다.

수치 모델이 통과하면 다른 이름으로 회로를 생성한다:

```powershell
& $Py scripts\invsqrt_lab.py --coef-bits 16 --output artifacts\candidates\yechan\coef16_circuit.kmb
```

기존 파일을 덮어쓰지 않도록 도구가 막아둔 상태다. 재실험할 때는 새 이름을 사용한다. 출력된 `.model.json`의 `official_verification: NOT_RUN`은 정상이다. 아직 공식 회로 검증을 실행하지 않았다는 뜻이다.

후보의 빠른 검증과 전체 검증:

```powershell
& $Py scripts\run_baselines.py --tasks invsqrt --profile smoke --invsqrt-file artifacts\candidates\yechan\coef16_circuit.kmb
& $Py scripts\run_baselines.py --tasks invsqrt --profile full --invsqrt-file artifacts\candidates\yechan\coef16_circuit.kmb --invsqrt-workers 8
```

Windows 병렬 옵션 `--invsqrt-workers 8`은 [실행 어댑터](../resources.html#team-files)를 사용한다. 원본 검증기의 작업·샷 수·배치·난수 시드와 검사·비용 계산을 유지하면서 작업을 여러 프로세스에 배분한다. 각 프로세스는 부모와 작업·시드가 동일한지 검사한다. 옵션을 빼면 공식 CLI의 순차 실행을 사용한다. 메모리나 CPU 여유가 적으면 2~4로 낮춘다.

## 5. 정확도 실험에서 반드시 볼 지점

- 정규화 구간이 바뀌는 4의 거듭제곱 주변과 최소·최대 입력을 확인한다.
- 정규화한 M의 구간 경계 1, 1.5, 2, 3, 4 주변에서 양쪽의 정수 입력을 비교한다.
- 계수의 반올림뿐 아니라 곱셈에서 버려지는 부분곱 비트까지 `fixed_point_model`로 확인한다.
- 수식이나 다항식 계수를 바꾸면 수치 모델과 회로 생성 코드가 같은 계산을 하는지 함께 수정·검증한다.
- 후보 평가는 허용오차 이내인지를 먼저 확인하고, 통과한 후보끼리 공식 `score`가 낮은지 비교한다.

## 6. 결과를 이렇게 읽기

| 결과 | 의미 | 다음 행동 |
|---|---|---|
| `model_within_tolerance: true` | 고정소수점 수치 근사가 전체 입력에서 허용오차 이내 | 실제 회로 검증을 진행한다. |
| `smoke / PASS` | 축소 입력·샷 조건에서 회로 동작 확인 | full 검증으로 넘어간다. |
| `full / PASS` | 명시된 전체 문제 조건에서 공식 검증을 통과 | 같은 기준 회로의 full 비용과 비교한다. |
| `FAIL` 또는 `ERROR` | 원본 로그의 원인 확인 필요 | 회로 실패인지, 경로·환경 오류인지 구분해 기록한다. |

실행 결과는 `reports/runs/<시각>-<profile>/invsqrt.json`, 원본 출력은 대응하는 `logs/<시각>-<profile>/invsqrt.log`에 남는다. JSON의 `input_files`, `command`, `verification_scope`, `official_result`를 함께 읽는다. `latest-full.json`은 가장 최근 실행을 가리키므로 예전 기준값은 [검증 요약의 고정 링크](../results.html)를 사용한다.

공식 invsqrt 비용은 큐비트 수 × Toffoli 등가 비용이다. 회전 합성에 남는 오차 여유도 비용에 영향을 주므로 큐비트나 정적 Toffoli 수만 보고 개선을 선언하지 않는다. `worst_error_over_tolerance`는 1에 가까울수록 여유가 적다. 로컬 PASS는 해당 시드에서의 검증 결과이며 Kaggle 제출·리더보드 평가를 완료했다는 뜻이 아니다.

## 7. 서진에게 넘길 파일

- 후보 회로 `.kmb`와 그것을 만든 코드 또는 실행 명령.
- 같은 실험의 `.model.json` 및 전체 검증 `invsqrt.json`.
- 대응하는 원본 `.log`와 변경한 비트 폭·수식의 짧은 설명.
- 기준 대비 공식 비용, 큐비트 수, 최악 오차, 실행 시간, 통과 여부를 적은 비교표.

기록 양식은 [실험 기록 템플릿](../resources.html#team-files)을 복사해 사용한다. 예찬은 수치 후보와 그 근거를 만들고, 서진은 공통 실행·회로 통합·제출 패키징을 담당한다. 검증 재확인은 소연과 공유하면 된다. 여기서 자동으로 대회 제출을 하지는 않는다.

## 8. 다른 두 예제는 언제 보나

| 과제 | 기본 입력 | 코드·결과 활용 |
|---|---|---|
| DQI | [dqi.kmb](../resources.html#official-files) | 약 886MB 바이너리다. [공식 검증기](../resources.html#official-files)와 [참조 생성 코드](../resources.html#official-files)를 통해 팀의 다른 과제 흐름을 파악한다. 첫 역제곱근 실험에는 필요 없다. |
| DFTHC-SOS | [submission.npz](../resources.html#official-files)와 `angle_k_0.kmb`~`angle_k_9.kmb` | 한 묶음으로 검증한다. [공식 설명](../resources.html#official-files)에서 수치 근사와 회로 비용이 결합되는 방식을 읽는다. |

전체 배포 파일과 검증기의 출처는 [공식 Kaggle Data](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/data)다. 다운로드 당시 ZIP과 파일별 SHA-256은 [무결성 기록](../results.html)에 남아 있다.
