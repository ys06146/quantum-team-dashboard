# 서진 · 1주차 작업 결과

2026.11.12 공개 자료 갱신. 실제 점수 확인: 2026.11.11 16:58 UTC. 미팅: 11월 15일.

## 실제 제출 결과

첫 공식 기준본의 공개 점수는 **1.00000**, 공개 DQI 개선본을 통합한 두 번째 제출은 **4.02469**다. 두 제출 모두 Kaggle에서 Complete 상태를 확인했다. 로컬 종합 예상치 4.02470과 실제 공개 점수는 별도로 기록한다.

이번 제출에서는 DQI 회로만 교체했다. invsqrt와 화학의 NPZ·ANGLE 10개는 공식 기준본을 유지했다. 팀원별 결과와 독립 확인은 15일 미팅에서 실제 자료로 확인한다.

## DQI 자원 비교

| 항목 | 공식 기준본 | 공개 DQI v11 |
| --- | --- | --- |
| 큐비트 Q | 1,893 | 892 |
| 평균 Toffoli T | 5,725,108.3821 | 395,507.3110 |
| 공식 DQI 비용 | 24,439,463,583,672.93 | 374,878,862,458.11 |
| DQI 비용 개선 배율 | 1 | 65.19296 |

DQI 비용은 기준의 약 1.53%다. 65.19배는 DQI 한 과제의 비용 개선 배율이며 실행 속도나 종합 점수를 뜻하지 않는다. 세 과제 개선 배율의 기하평균으로 계산한 종합 점수는 약 4.02다.

## 검증과 재현 근거

- 수정하지 않은 공식 기본 DQI 검사 102,400회 통과.
- 사전에 정한 서로 다른 입력 묶음 두 개, 총 204,800회 추가 검사 통과.
- 합계 307,200회에서 관측된 값 오류와 위상 오류는 각각 0건.
- 제출 ZIP의 13개 파일을 공식 full PASS 입력 해시와 대조했다.
- 세 공식 기준 예제는 새 WSL Ubuntu 환경에서도 full PASS였고 비용·샷 수·입력 및 검증기 해시가 기존 기록과 일치했다.
- 화학 오차 두 지표는 최대 약 6×10⁻¹⁶ 차이가 있었으며 상세 값을 보존했다.

유한 표본 검사는 모든 입력에서 오류가 없다는 증명이 아니다. 공개 저자가 드문 실패 가능성을 설명한다. 새 환경 재현은 같은 PC에서 수행했으며 소연이나 다른 팀원의 독립 실행을 완료했다는 뜻이 아니다.

## 공개 회로의 출처와 서진의 작업

Syed Asad Ali(syed3000)의 VQCC Own-Circuit Portfolio **데이터셋 버전 11**에서 공개 Apache 2.0 DQI 회로를 가져왔다. 회로 바이너리는 수정하지 않았다.

- 원저자: Syed Asad Ali. 선행 기여: SomeJoint/Agniv Banerjee, Ali Haydar Ozdag, Khattar·Gidney 및 원저자 노트북에 명시된 공개 연구.
- 서진: 공개 토론과 후보 조사, 출처·라이선스·버전·해시 기록, 공식 재검증과 추가 입력 검사, DQI 통합·패키징·실제 제출.
- 공개 회로를 새로 독자 개발한 성과로 표시하지 않는다. 전체 원본 생성 과정을 독립 재구축한 것은 아니다.

[공개 데이터셋](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio) · [원저자 설명](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook) · [토론](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/753923)

## 발표 자료와 확인할 기록

- [12장 발표 자료 열기](meeting/jjeya-week1-meeting.html)
- [발표 대본 읽기](speaker-notes.html)
- [발표 대본 Markdown](meeting/jjeya-week1-speaker-notes.md)
- [첫 제출 기록](records/FIRST_SUBMISSION_20261111.json)
- [실제 점수 4.02469 제출 기록](records/SECOND_SUBMISSION_20261111.json)
- [DQI 출처·비용·역할](records/DQI_PROVENANCE.json)
- [추가 검증 두 묶음](records/DQI_ROBUSTNESS.json)
- [DQI 공식 full 결과](records/full/dqi-public-v11.json)
- [새 환경 재현 요약](records/REPRODUCTION_20261111.json)
- [invsqrt 기준 결과](records/full/invsqrt-baseline.json)
- [DQI 기준 결과](records/full/dqi-baseline.json)
- [화학 기준 결과](records/full/dfthcsos-baseline.json)
- [DQI 병목 분석 수치](records/DQI_BOTTLENECK.json)
- [제출 ZIP 파일별 해시](records/SUBMISSION_MANIFEST.json)
- [공개 사본과 원본 기록의 해시 목록](records/PUBLICATION_MANIFEST.json)
- [공통 실행·검증·패키징 도구](https://github.com/ys06146/quantum-team-dashboard/tree/main/work/week1)

공개 JSON은 개인 PC의 절대 경로만 자리표시자로 바꾼 사본이다. 입력·검증기 해시와 결과 수치는 유지했다. source_record와 source_sha256는 공유 드라이브의 원본 파일을 가리키며 공개 사본 자체의 해시와 구분한다. 전체 회로·공식 대회 데이터·제출 ZIP·원본 로그는 기존 공유 드라이브에서 확인한다.

## 15일 미팅에서 확인할 것

- 예찬: invsqrt 기준 재현, 경계·오차 분석과 개선 방향.
- 지우·서희: 같은 설정의 NPZ·ANGLE 대응, 화학 지표와 오차 여유.
- 소연: 실제 별도 환경 실행 기록과 기준 비교.
- 전원: 후보 전달 형식과 다음 실험의 담당·변수·산출물·확인 날짜 합의.

발표 약 15분, 팀원 공유 약 12분, 합의 약 10분을 포함해 약 40분을 제안한다. 다음 실험 일정은 미팅에서 확정한다.
