"""Recompute DQI cost contributions from preserved official full evidence."""
import argparse
from datetime import datetime,timezone
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--record",type=Path,default=ROOT/"reports/runs/20261107T111402131264Z-full/dqi.json")
    args=ap.parse_args()
    r=json.loads(args.record.read_text(encoding="utf-8"));s=r["official_result"]
    assert r["profile"]=="full" and r["status"]==s["status"]=="PASS"
    N=s["verified_shots"]
    gates={k:s["shot_operation_counts"].get(k,0)/N for k in ("CCX","CSWAP")}
    T=sum(gates.values());Q=s["num_qubits"];factor=s["repetition_factor"];score=factor*Q*Q*T
    assert math.isclose(T,s["toffoli_count"],rel_tol=1e-12)
    assert math.isclose(score,s["score"],rel_tol=1e-12)
    cases=[]
    for label,q,t in [("Q -5%",Q*.95,T),("Q -10%",Q*.9,T),("T -10%",Q,T*.9),("Q -5%, T -10%",Q*.95,T*.9)]:
        ratio=(q/Q)**2*(t/T)
        cases.append({"hypothesis":label,"cost_ratio":ratio,"reduction_percent":100*(1-ratio),"assumption":"R unchanged; same verifier validity. Not a measured candidate."})
    payload={"status":"PASS","checked_at_utc":datetime.now(timezone.utc).isoformat(),
      "record":args.record.relative_to(ROOT).as_posix(),"record_sha256":hashlib.file_digest(args.record.open("rb"),"sha256").hexdigest(),
      "verified_shots":N,"value_errors":s["value_errors"],"phase_errors":s["phase_errors"],
      "Q":Q,"syndrome_qubits":s["n"]*s["degree"],"ancilla_qubits":Q-s["n"]*s["degree"],
      "R":factor,"T_per_shot":T,"cost":score,"effective_error_rate":s["effective_error_rate"],
      "gate_contributions":[{"gate":k,"per_shot":v,"percent_of_T":100*v/T} for k,v in gates.items()],
      "sensitivity_hypotheses":cases,
      "decision":"Keep full-PASS baseline in week 2. Prioritize ancilla lifetime/reuse review and local CCX/CSWAP reductions. Defer decoder rewrite.",
      "limits":["Gate-family decomposition is measured from the official run.","Forward EEA / Chien-Forney / reverse EEA stage percentages were not profiled.","Scenarios are sensitivity calculations, not measured improvements.","This agent analysis is not a teammate review."]}
    (ROOT/"reports/DQI_BOTTLENECK.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    body=f"""# DQI 기준 비용 병목과 2주차 범위

2026-11-11 작성. 공식 full 결과의 비용식을 재계산했고 원본 score와 일치했다.

## 결론과 임시 결정

검증된 DQI 기준본을 유지한다. 2주차의 첫 검토는 임시 큐비트의 생존 구간과 재사용, CCX·CSWAP이 많은 국소 연산으로 한정한다. 디코더 전체 재작성은 이번 범위에서 보류한다. 팀원 검토 전 사용할 배서진 측 임시 결정이며 11/15에 공유한다.

## 실제로 측정한 기준

- 공식 기본 샷 수: {N:,}
- 값 오류 {s['value_errors']}, 위상 오류 {s['phase_errors']}
- 큐비트 Q: {Q:,} = 입력 syndrome {s['n']*s['degree']:,} + 임시 큐비트 {Q-s['n']*s['degree']:,}
- 샷당 Toffoli-like T: {T:,.9f}
- 반복 계수 R: {factor:.12f}
- 비용 R × Q² × T: {score:,.5f}
- 오류율 상한: {s['effective_error_rate']:.12f} < 1/16

오류 관측이 0이어도 통계적 상한은 0이 아니므로 R은 1보다 크다. classical bit 수 {s['num_bits']:,}개는 Q에 합산하지 않는다.

## 비용을 차지하는 연산

- CCX: 샷당 {gates['CCX']:,.9f}, T의 {100*gates['CCX']/T:.4f}%
- CSWAP: 샷당 {gates['CSWAP']:,.9f}, T의 {100*gates['CSWAP']/T:.4f}%
- 두 연산 합계는 공식 toffoli_count와 일치한다.
- CX 등 연산 횟수가 많아도 이 공식 비용의 T 항과 동일하게 세면 안 된다.
- 정적 최대 Toffoli-like {s['max_toffoli_count']:,}와 실제 샷 평균 T를 구분한다.

공식 참조 구현은 forward EEA, Chien search/Forney MBUC, reverse EEA와 정리 단계로 이루어진다. 위 수치는 게이트 종류별 실측이며 단계별 비용 비율을 측정한 것은 아니다. 어느 단계가 가장 비싼지 수치 없이 단정하지 않는다.

## 개선 방향의 민감도

다음은 R과 통과 조건이 유지된다는 가정의 계산이다. 구현 완료 또는 실제 개선 기록이 아니다.

- Q 5% 감소: 비용 9.75% 감소
- Q 10% 감소: 비용 19% 감소
- T 10% 감소: 비용 10% 감소
- Q 5%와 T 10% 동시 감소: 비용 18.775% 감소

큐비트는 비용에 제곱으로 들어가므로 임시 공간 재사용을 먼저 검토할 근거가 있다. 단, 큐비트를 줄이면서 게이트나 오류율 상한이 증가하면 전체 비용이 나빠질 수 있다.

## 다음 실험과 중단 기준

1. 기준본 해시를 고정하고 임시 큐비트 할당·해제 구간을 기록한다.
2. 한 국소 구간만 바꾼 후보를 별도 파일로 만든다. S 레지스터 복원, 임시 큐비트 0 복귀, MBUC 위상 조건, Z_POW 금지를 유지한다.
3. smoke는 실행 확인으로만 사용하고 최종 채택에는 공식 full을 사용한다.
4. full PASS와 R × Q² × T 감소가 모두 확인될 때만 채택한다.
5. 실패 또는 비용 증가 시 기존 기준본을 유지하고 로그·설정을 보존한다.

## 근거와 재생성

- [공식 full 원본](runs/20261107T111402131264Z-full/dqi.json)
- [분해한 수치와 계산 검증](DQI_BOTTLENECK.json)
- [공식 비용식](../vendor/competition/verifiers/dqi/verify_submission_dqi.py)
- [공식 회로 단계](../vendor/competition/verifiers/dqi/dqi_reference_circuit.py)
- 재생성 명령: python scripts/analyze_dqi.py
"""
    (ROOT/"reports/DQI_BOTTLENECK.md").write_text(body,encoding="utf-8")
    print(json.dumps(payload,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

