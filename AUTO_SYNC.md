# 드라이브 → 대시보드 자동 반영

드라이브에서 아래 원본을 저장하면 이 PC가 2분마다 변경을 확인합니다. 문서 변환과 내부 링크 검사를 통과한 내용만 GitHub에 올립니다. GitHub Pages 배포 시간까지 포함해 보통 2~5분 정도 걸리며, 서비스 지연이 있으면 더 걸릴 수 있습니다.

사이트: <https://ys06146.github.io/quantum-team-dashboard/>

## 수정할 원본

아래 경로는 `jjeya` 기준입니다.

| 문서 | 원본 파일 |
| --- | --- |
| 3주 계획·역할·업무 상세 | `quantum-team-plan-share.html` |
| 소연 가이드 | `seojin_work/week1/SOYEON_GUIDE.md` 또는 `.html` |
| 지우 가이드 | `seojin_work/week1/JIWOO_GUIDE.md` 또는 `.html` |
| 예찬 가이드 | `seojin_work/week1/YECHAN_GUIDE.md` 또는 `.html` |
| 서진 가이드 | `seojin_work/week1/SEOJIN_GUIDE.md` 또는 `.html` |
| 서희 가이드 | `seohee_work/week1/SEOHEE_GUIDE.md` 또는 `.html` |

가이드는 **Markdown 수정이 가장 간단**합니다. HTML을 수정하면 `<main>…</main>` 안의 본문을 가져옵니다. HTML의 바깥 표지·내비게이션·스타일은 대시보드 공통 디자인을 사용합니다. HTML 본문을 선택한 경우 내려받는 `.md`는 변경 내용이 담긴 CommonMark HTML 형식입니다.

처음 연결할 때는 MD를 기준으로 시작합니다. 이후 MD 또는 HTML 중 내용이 바뀐 파일이 반영됩니다. 한 확인 주기 안에 둘 다 바뀌면 마지막 저장 시각이 늦은 파일을 사용합니다. 두 파일의 수정 사항을 병합하거나 다른 쪽 원본에 덮어쓰지는 않습니다. 두 형식 중 하나를 계속 편집하는 것을 권장합니다.

계획 HTML의 기존 탭·업무 버튼과 `tasks` 데이터 구조는 유지하세요. 계획 페이지뿐 아니라 홈의 주차별 단계, 일정, 개인별 역할·첫 주 산출물도 같은 계획에서 읽습니다. 공식 실험 파일 링크는 웹의 자료 안내로 연결됩니다.

## 실행 조건

- 이 Windows PC에 사용자가 로그인해 있고, PC가 깨어 있으며, Google Drive의 팀 폴더와 인터넷에 접근 가능해야 합니다.
- Codex나 브라우저는 열어 둘 필요가 없습니다. 기존 GitHub 인증으로 Windows 작업 스케줄러가 실행합니다.
- Git 내부 정보와 임시 빌드는 이 PC의 `%LOCALAPPDATA%/QuantumTeamDashboard`에 보관합니다. 드라이브가 Git 참조 폴더에 `desktop.ini`를 생성하는 충돌을 피하기 위한 구성입니다. 이전 Git 정보는 저장소 안의 `.git-drive-backup`에 보존되며 공개되지 않습니다. 다른 PC에서 운영하려면 그 PC에서 저장소를 별도로 복제하고 설치하세요.
- PC가 꺼져 있거나 로그아웃·절전 상태면 반영이 멈춥니다. 다음 로그인 또는 깨어난 뒤 실행 시 누적 변경을 확인합니다.
- 다른 팀원이 드라이브에서 수정한 내용도 이 PC의 드라이브에 동기화되면 같은 방식으로 반영됩니다.
- 저장소의 `content/`, `docs/`는 생성 결과입니다. 문서 수정은 위 원본에서 해주세요. 저장소에 커밋하지 않은 변경이나 푸시하지 않은 커밋이 있으면 자동 반영이 멈추고 오류를 남깁니다.
- 새 문서·폴더는 자동으로 공개하지 않습니다. 대상 추가는 `drive_sources.py`의 `GUIDES`에서 명시적으로 설정합니다. 검증 로그와 공식 대회 데이터는 이 자동화의 수집 대상이 아닙니다.

## 상태와 오류 확인

`quantum-team-dashboard/.sync-state/status.json`에서 최근 상태, `sync.log`에서 이력을 확인하세요. 이 폴더는 GitHub에 올라가지 않습니다. 날짜·시간은 UTC로 기록합니다.

| 상태 | 의미 |
| --- | --- |
| `unchanged` + `pages_confirmed: true` | 새 변경 없음, 최근 웹 반영 확인 완료 |
| `pushed_waiting_for_pages` / `waiting_for_pages` | GitHub에 전송됨, 웹 배포 확인 대기 |
| `waiting_for_stable_files` | 저장 중인 파일을 다음 주기에 다시 확인 |
| `repository_updated_retry_next_run` | 원격 수정 수신, 다음 주기에 재확인 |
| `error` | 검증·인증·네트워크·Git 상태 오류, 내용을 고치면 다음 주기에 재시도 |

잘못된 HTML 구조, 깨진 링크, 의심되는 인증정보가 발견되면 배포하지 않습니다. 생성·검증·커밋은 임시 복제본에서 진행하며, 실패한 변환으로 정상 사이트나 드라이브 원본을 덮어쓰지 않습니다. GitHub 푸시는 강제 푸시를 사용하지 않습니다.

## 수동 실행과 켜기·끄기

PowerShell을 `quantum-team-dashboard`에서 열고 Python 3.12 이상으로 실행합니다.

```powershell
python sync_drive.py                 # 변환·검사만, 공개하지 않음
python sync_drive.py --publish       # 지금 동기화
python sync_drive.py --status        # 최근 상태
Get-ScheduledTask -TaskName 'QuantumTeamDashboard-DriveSync'
Disable-ScheduledTask -TaskName 'QuantumTeamDashboard-DriveSync'  # 일시 중지
Enable-ScheduledTask -TaskName 'QuantumTeamDashboard-DriveSync'   # 다시 켜기
Start-ScheduledTask -TaskName 'QuantumTeamDashboard-DriveSync'    # 즉시 실행
```

재설치가 필요하면 `install_auto_sync.ps1`을 실행합니다. Python 경로가 다르면 `-PythonExecutable '실제 pythonw.exe 경로'`를 지정하세요. 설치는 현재 로그인 사용자 권한으로 실행하며 암호를 저장하지 않습니다.

GitHub 로그인 만료는 `gh auth status`로 확인하고 정상 계정으로 다시 로그인하세요. 정상 상태에서 오류가 발생하면 마지막 성공한 웹 페이지가 그대로 유지됩니다.
