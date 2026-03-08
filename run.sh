#!/bin/bash
# PDF to Markdown 변환 실행 스크립트
# venv를 자동으로 생성하고 marker-pdf를 설치한 후 변환을 실행합니다.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# venv가 없으면 생성
if [ ! -d "$VENV_DIR" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv "$VENV_DIR"
    echo "marker-pdf 설치 중... (시간이 걸릴 수 있습니다)"
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    echo "설치 완료."
    echo ""
fi

# venv의 python으로 실행
"$VENV_DIR/bin/python" "$SCRIPT_DIR/pdf2md.py" "$@"
