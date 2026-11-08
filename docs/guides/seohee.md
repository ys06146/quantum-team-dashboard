# 서희 · Week 1 화학 과제 시작 가이드

작성일: 2026-11-08 · 대상: 화학 전공 담당 · 첫 주 제안 일정: 11/09–11/15

**서희의 첫 주 목표는 DFTHC-SOS의 화학 문제와 공식 평가 지표를 이해하고, 기준 결과를 설명한 뒤 지우와 다음 실험 가설 두 개를 정하는 것이다.** 팀 계획의 ‘서희’에 해당한다.

가장 먼저 [공식 화학 설명](../resources.html#official-files)을 읽고 → [기준 full 검증 JSON](../results.html#dfthcsos)을 확인하고 → [지우의 작업 가이드](jiwoo.html)에서 실제 실험 흐름을 보면 된다. 문서와 저장된 결과 검토는 별도 설치 없이 시작할 수 있다.

## 1. 서희가 맡는 일과 협업 범위

| 담당 | 직접 맡는 일 | 서로 주고받을 내용 |
|---|---|---|
| 서희 | 화학 문제·데이터 의미 설명, 오차·에너지 지표 해석, 근사 후보 검토, 화학 분석 문단 작성 | 지우에게 가설과 해석, 소연에게 판단 근거, 서진에게 확인할 파일·설정 |
| 지우 | 수치 파라미터·각도·트리 후보와 생성 코드 작성 | 서희와 가설을 합의하고 모델·회로 결과를 제공 |
| 서진 | 공통 실행, 회로 통합, 파일·버전·검증 로그 관리 | 후보가 실제 회로에서도 통과하는지 확인 |
| 소연 | 기준선과 후보의 독립 비교, 채택 근거 정리 | 서희의 지표 해석과 검증 결과를 대조 |
| 예찬 | 역제곱근 근사·비트 폭·경계 오차 실험 | 다른 과제의 수치 오차 분석 방법을 공유 |

양자화학·계산화학 경험이 적으면 용어, 단위, 공식 조건, 결과 읽기부터 시작한다. 경험이 있으면 지우와 분해·양자화 가설 설계까지 확장한다. [팀 전체 계획](../plan.html)에서 3주 흐름도 확인할 수 있다.

## 2. 어떤 파일부터 읽어야 하나

아래 링크는 `seohee_work/week1`에서 공통 자료로 연결된다. 웹 링크는 공개 가이드·결과·자료 안내로 연결된다. 실제 실험에서는 `jjeya` 폴더 배치를 유지한다. `.md`·`.py`·`.json`은 편집기로, `.html`은 브라우저로 연다.

| 순서 | 파일 | 읽을 부분 | 읽고 남길 내용 |
|---|---|---|---|
| 1 · 필수 | [SCORING_README.md](../resources.html#official-files) | System, Submission files, Worked example, Scoring | 어떤 고정 문제를 근사하고 무엇을 제출·평가하는지 5문장으로 정리 |
| 2 · 필수 | [화학 full 결과 JSON](../results.html#dfthcsos) · [전체 결과 요약](../results.html) | `official_result.metrics`, `resources`, `score`, `verified_shots`, `submission_sha256` | 기준 지표·단위·통과 조건·오차 여유를 표로 기록 |
| 3 · 필수 | [JIWOO_GUIDE.html](jiwoo.html) · [같은 내용의 Markdown](jiwoo.html) | 1·3·6·7절: 데이터, 실험 방향, 전달할 묶음 | 지우의 구현 업무와 서희의 해석·검토 업무를 구분하고 협업 메모 작성 |
| 4 · 데이터 | [reference.py](../resources.html#official-files) · [FCIDUMP](../resources.html#official-files) | 기준 오비탈·전자 수, 적분 로딩, 고정 shift, `UPPER_ENERGY` | 전자·오비탈·1전자/2전자 적분·기준 에너지의 데이터 사전 작성 |
| 5 · 데이터 | [submission.npz](../resources.html#official-files) | 지우 가이드 3절의 NumPy 읽기 예제로 배열명·형상 확인 | U, W, H2_I, tree_edges, angle_words가 어떤 입력인지 연결해 설명 |
| 6 · 판정 근거 | [verify.py](../resources.html#official-files) · [dfthc_math.py](../resources.html#official-files) | `evaluate_words`, `passes_accuracy`, `score_from_metrics`, `evaluate_dfthc_vectors` | 오차 정의와 단위, 부등호, E_SOS·E_gap·lambda_eff 관계를 원문과 대조 |
| 7 · 지우와 함께 | [ANGLE 참조 생성기](../resources.html#official-files) · [costs_prepare.py](../resources.html#official-files) | brot·J, 각도 로딩, 전체 자원 비용 | 정밀도 변경이 수치 오차와 회로 비용에 어떻게 영향을 줄지 가설 두 개 작성 |

FCIDUMP는 약 128MB이므로 먼저 `reference.py`와 설명서를 읽는다. NPZ와 KMB는 바이너리이며 전용 도구로 읽는다. 실제 회로 실행이 필요하면 지우 가이드 2절의 **개인 PC용 Python 3.12 환경**을 준비한다. 공유 `.venv`는 기반 Python 버전 불일치 이력이 있으므로 기존 폴더만 보고 실행 가능하다고 판단하지 않는다.

## 3. 이해해야 할 문제와 데이터

공식 대상은 **FeMoCo76o113e: 공간 오비탈 76개, 전자 113개**다. 주어진 해밀토니안을 근사한 수치 데이터와, 그 데이터를 각도로 로딩하는 회로가 함께 평가된다. 공식 FCIDUMP·전자 수·기준 에너지·고정 shift를 평가 기준으로 사용한다.

| 항목 | 기준 구조 | 서희가 설명할 내용 |
|---|---|---|
| R / B / C | 65 / 60 / 60 | 제공된 분해의 크기 파라미터. 바꾸면 재구성 오차와 자원 비용을 함께 확인 |
| U | (65, 60, 76) | 제출 벡터의 형상. 실제 평가는 회로에서 읽은 각도로 복원한 벡터를 사용 |
| W / H2_I | 분해 가중치·수치 파라미터 | 각도에서 복원한 벡터와 함께 해밀토니안 근사에 들어가는 값 |
| H1_I / Hsym_lower | NPZ에 포함 | 공식 평가는 제공된 고정 shift를 사용하며, 제출된 이 값들을 그대로 채점에 사용하지 않음 |
| tree_edges | (75, 2) | 각도 단어에서 76차원 벡터를 복원하는 트리 순서 |
| angle_words | (3976, 75) | 76개 one-body 행과 R×B개 two-body 행의 정수 각도 표. 샘플 NPZ의 회로 생성 보조 자료 |
| brot / J | 12 / 8 | 각도 단어 비트 수 / 회로 한 개가 처리하는 단어 수 |
| ANGLE 회로 | 10개 | `ceil(75 / J)`개. 대응 NPZ와 같은 설정에서 생성되어야 함 |

각도 해석식은 `theta = pi × word / 2^(brot−1)`이다. 정밀도를 낮출 때는 실제 각도를 그 정밀도에 맞춰 다시 양자화한다. 기존 12비트 정수를 그대로 11비트로 해석하면 각도 자체가 달라진다.

## 4. 기준 결과와 공식 통과 조건

아래 값은 **2026-11-07 공식 화학 예제의 로컬 full PASS 기록**이다. 표시값은 반올림했으며 정확한 비교에는 원본 JSON을 사용한다. 이 문서를 만들면서 새 후보를 실행하거나 대회에 제출한 것은 아니다.

| 지표 | 기준값 | 의미와 판정 기준 |
|---|---:|---|
| error_1 | 0.00318519503 Ha | 1전자 성분 재구성 잔차. `≤ 0.020 Ha`. |
| error_2 | 0.01863957063 Ha | 2전자 적분 재구성 잔차. `≤ 0.020 Ha`. |
| Lambda | 308.45593973309 Ha | LCU 정규화 계수. `> 49.0`을 엄격하게 만족. |
| E_SOS | -22144.23882724429 Ha | DFTHC 해밀토니안의 SOS 에너지 하한. |
| E_gap | 3.96547724429 Ha | `E_upper − E_SOS`. `> 3.914898 Ha`와 공식 `gap_in_domain` 검사 충족. |
| lambda_eff | 49.30136925057 Ha | `sqrt(E_gap × (2 Lambda − E_gap))`. 유한값이어야 함. |
| 전체 Toffoli / 전체 큐비트 | 93,237 / 730 | 전체 블록 인코딩 자원. 개별 ANGLE 자원과 구분. |
| 공식 로컬 비용 score | 3,355,599,588.3155375 | `lambda_eff × 전체 Toffoli × 전체 큐비트`. 같은 과제에서 낮을수록 유리. |

`error_1`과 `error_2`는 재구성 잔차의 Frobenius norm이다. 실제 바닥상태 에너지 오차와 같은 값으로 해석하지 않는다. `E_gap`은 고정 `E_upper`와 SOS 하한의 차이이며 들뜬 상태와 바닥상태의 에너지 차이를 직접 계산한 값이 아니다.

**현재 error_2의 남은 여유는 약 0.00136043 Ha, 즉 1.36043 mHa**다. 허용치의 약 93.2%를 이미 사용하므로 정밀도를 낮추는 실험에서 특히 확인할 지표다. 이 여유만으로 후보의 전체 통과를 예측할 수는 없다.

기준 회로 검증은 주소당 64 shots, 총 254,464 shots를 사용했다. ANGLE 회로의 큐비트 수는 119, 전체 비용식의 큐비트 수는 730이다. 각 ANGLE 회로의 한도는 128큐비트다. 수치 모델 통과, 축소 smoke 통과, 전체 full 통과를 나눠 기록한다.

## 5. 오늘 바로 해볼 결과 읽기

PowerShell에서 아래 명령은 저장된 JSON만 읽는다. 화학 시뮬레이션이나 패키지 설치를 실행하지 않는다. 드라이브 문자가 다르면 `$ProjectRoot`에 본인 PC의 jjeya 폴더 경로를 지정한다.

```powershell
Set-Location -LiteralPath (Join-Path $ProjectRoot 'seohee_work\week1')
$SeoheeBaselinePath = '..\..\seojin_work\week1\reports\runs\20261107T091146680709Z-full\dfthcsos.json'
$SeoheeReport = Get-Content -LiteralPath $SeoheeBaselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
$SeoheeMetrics = $SeoheeReport.official_result.metrics

$SeoheeMetrics | Format-List
[pscustomobject]@{
    Status = $SeoheeReport.official_result.status
    Score = $SeoheeReport.official_result.score
    VerifiedShots = $SeoheeReport.official_result.verified_shots
    Error1Margin_mHa = (0.020 - $SeoheeMetrics.error_1) * 1000
    Error2Margin_mHa = (0.020 - $SeoheeMetrics.error_2) * 1000
    SubmissionSHA256 = $SeoheeReport.official_result.submission_sha256
} | Format-List
```

출력에서 PASS, 254,464 shots, error_2 여유 약 1.36043 mHa를 확인하고 `baseline_review.md`에 기록한다. `submission_sha256`은 공식 검증기가 정의한 전체 제출 묶음의 해시이며 JSON 파일 자체의 해시와 구분한다.

NPZ 배열을 직접 확인하거나 수치 모델을 다시 평가할 때는 [지우 가이드](jiwoo.html)의 2~4절을 순서대로 따른다. 그 실행 명령의 작업 위치는 `seojin_work/week1`이며, 이 가이드의 메모 작성 위치인 `seohee_work/week1`과 다르다.

## 6. 첫 주 작업 순서와 완료 기준

일정은 제안이며 첫 주 말까지 아래 세 파일과 가설 두 개를 남기는 것이 목표다.

| 단계 | 직접 할 일 | 완료 기준 |
|---|---|---|
| 시작 | 1~3번 파일을 읽고 문제·평가 흐름 요약 | 팀원이 읽고 어떤 입력을 근사하며 무엇을 제출하는지 이해할 수 있음 |
| 데이터 확인 | 4~5번 파일에서 상수·배열·단위를 확인 | 오비탈·전자 수, NPZ와 각도·회로 관계를 설명 가능 |
| 지표 대조 | 6번 코드와 기준 JSON을 비교 | 각 지표의 의미·단위·정확한 부등호와 기준의 여유를 기록 |
| 가설 작성 | 지우와 변경 변수 하나씩인 가설 두 개 작성 | 변수·예상 효과·위험 지표·확인 방법이 모두 있음 |
| 주말 검토 | 지우·소연과 메모를 대조하고 서진에게 확인 사항 전달 | 세 파일에 근거 경로가 있고 해석이 원본과 일치 |

**첫 주 완료 체크:** 문제 설명 1장, 공식 지표표, 기준 결과 검토 메모, 가설 2개, 동료 검토 의견이 모두 남아 있어야 한다. 저장된 기준 결과를 읽은 것과 본인이 새로 실행한 결과를 구분해서 적는다.

## 7. 작성할 세 파일과 목차

아래 파일은 서희가 앞으로 작성할 산출물이다. 현재 제공된 HTML·Markdown 가이드와 구분한다. 저장 위치는 모두 `seohee_work/week1`이다.

| 작성할 파일 | 넣을 내용 | 검토자 |
|---|---|---|
| `chemistry_problem_brief.md` | 대상 문제, 76오비탈·113전자, 해밀토니안과 적분, 분해→각도→회로 흐름, 고정 입력과 근사 변수, 출처 | 지우 |
| `chemistry_metrics.md` | error_1/2, Lambda, E_SOS, E_gap, lambda_eff, score의 정의·단위·조건·기준값·코드 함수 | 소연 |
| `baseline_review.md` | 기준 JSON 경로·제출 해시, full 상태·샷 수, 오차 여유, 해석, 가설 2개, 질문·다음 행동 | 지우·소연, 실행 확인은 서진 |

`baseline_review.md`의 시작 목차로 아래를 복사해 사용할 수 있다.

```markdown
# 화학 기준 결과 검토

- 작성자 / 작성일:
- 기준 JSON 경로:
- 공식 submission_sha256:
- 기록 종류: 저장된 기준 결과 검토 / 직접 재실행
- full 상태 / shots:

## 지표 해석과 오차 여유
각 지표의 기준값, 조건, 여유, 코드 근거를 적는다.

## 가설 1
- 바꿀 변수와 비교 값:
- 예상 효과와 이유:
- 위험한 지표:
- 지우에게 필요한 입력·실험:
- 판정에 쓸 수치 모델·full 결과:

## 가설 2
위와 같은 항목으로 작성한다.

## 동료 검토와 다음 행동
- 확인한 사람 / 의견 / 수정 내용:
- 남은 질문과 담당자:
```

## 8. 지우와 논의할 첫 가설 두 개

| 가설 예시 | 서희가 확인할 내용 | 지우·서진에게 요청할 결과 |
|---|---|---|
| 각도 정밀도 12→11비트 | 올바르게 재양자화했는지, 특히 error_2 여유와 Lambda·E_gap 조건이 유지되는지 | 새 단어 표의 수치 지표, 대응 NPZ·ANGLE 회로, full 상태·전체 비용 |
| 같은 12비트 각도에서 J=8→4 | 물리적 각도와 복원 벡터가 유지되는지, 수치 지표가 같을 것으로 예상되는 근거 | 회로 수·ANGLE 큐비트·전체 Toffoli·전체 큐비트·score 변화 |

위 두 항목은 **실험 제안**이며 통과나 비용 개선이 확인된 후보가 아니다. 후보 채택은 공식 정확도 조건을 만족한 상태에서 전체 비용이 낮아지는지로 판단한다. J는 회로당 단어 묶음 크기이므로, 각도 정밀도 brot와 구분한다.

## 9. 누구에게 무엇을 전달하나

- **지우:** 문제·데이터 설명과 가설 두 개. 변경 변수, 예상 효과, 확인할 지표를 구체적으로 전달한다.
- **소연:** 공식 지표표와 기준 검토 메모. 원본 JSON·코드 함수, 단위, 부등호, 오차 여유를 함께 전달한다.
- **서진:** 실험에서 참조한 NPZ·ANGLE·트리의 경로와 설정, 제출 해시, 실행 환경이나 회로 대응에서 확인이 필요한 질문을 전달한다.

후보를 검토할 때는 `실험 ID → 입력·생성 설정 → 수치 모델 결과 → full JSON·로그 → 판단`이 연결되게 남긴다. 원본 공식 파일을 수정하지 않고 실험별 복사본과 기록으로 비교한다.

근거 자료는 공통 폴더의 공식 설명·검증 코드와 2026-11-07 full 결과다. 관련 안내: [소연 가이드](soyeon.html), [예찬 가이드](yechan.html), [공식 파일 무결성 기록](../results.html). 역할과 첫 주 일정은 팀 실행 제안이다.
