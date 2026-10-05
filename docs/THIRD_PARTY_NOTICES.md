# 제3자 라이브러리 고지

이 프로젝트는 아래 라이브러리를 사용합니다. 각 라이브러리는 자신의 라이선스를 따르며, 이 저장소의 `LICENSE`(MIT + Commons Clause)는 해당 라이브러리에 적용되지 않습니다.

## 저장소에 파일이 포함된 것

### Blockly
- 위치: `core/web/lib/blockly_compressed.js`, `core/web/lib/blocks_compressed.js`, `core/web/lib/ko.js` (버전 10.4.3, 수정하지 않음)
- 저작권: Google LLC 및 Blockly 기여자
- 라이선스: Apache License 2.0 — 전문은 `core/web/lib/LICENSE-Blockly-Apache-2.0.txt`
- 원본: https://github.com/google/blockly

## 사용자가 `pip install -r requirements.txt` 로 설치하는 것 (저장소에 포함되지 않음)

| 라이브러리 | 라이선스 | 용도 |
|---|---|---|
| pynput | LGPL-3.0 | 마우스/키보드 녹화와 재생 |
| pywebview | BSD-3-Clause | 앱 창 |
| openpyxl | MIT | .xlsx 읽기 |
| xlrd | BSD | .xls 읽기 |
| pyperclip | BSD | 클립보드 붙여넣기 |

> pynput(LGPL)을 포함해서 exe 등으로 묶어 배포할 경우, LGPL-3.0 전문을 함께 제공하고 사용자가 해당 라이브러리를 교체할 수 있어야 하는 등 LGPL 조건을 따라야 합니다.
