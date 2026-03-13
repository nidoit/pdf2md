#!/bin/bash
# PDF to Markdown 변환 실행 스크립트
# venv를 자동으로 생성하고 pymupdf4llm을 설치한 후 변환을 실행합니다.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# venv가 없으면 생성
if [ ! -d "$VENV_DIR" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv "$VENV_DIR"
    echo "pymupdf4llm 설치 중..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo ""
        echo "설치 실패. .venv 폴더를 삭제 후 다시 시도하세요:"
        echo "  rm -rf $VENV_DIR"
        exit 1
    fi
    echo "설치 완료."
    echo ""
# venv는 있지만 pymupdf4llm이 설치되지 않은 경우
elif ! "$VENV_DIR/bin/python" -c "import pymupdf4llm" 2>/dev/null; then
    echo "pymupdf4llm이 설치되어 있지 않습니다. 설치를 진행합니다."
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo ""
        echo "설치 실패. .venv 폴더를 삭제 후 다시 시도하세요:"
        echo "  rm -rf $VENV_DIR"
        exit 1
    fi
    echo "설치 완료."
    echo ""
fi

# Tesseract OCR 데이터 경로 자동 설정
# pymupdf 내장 Tesseract가 /usr/share/tessdata/ 를 하드코딩하므로
# 실제 tessdata 경로가 다른 경우 심볼릭 링크를 생성
if [ ! -d /usr/share/tessdata ] || [ ! -f /usr/share/tessdata/eng.traineddata ]; then
    for tessdir in /usr/share/tesseract-ocr/5/tessdata /usr/share/tesseract-ocr/4/tessdata /usr/share/tesseract-ocr/3/tessdata /opt/homebrew/share/tessdata /usr/local/share/tessdata; do
        if [ -f "$tessdir/eng.traineddata" ]; then
            echo "Tesseract 데이터 경로 연결: $tessdir -> /usr/share/tessdata"
            sudo ln -sf "$tessdir" /usr/share/tessdata 2>/dev/null || {
                echo ""
                echo "⚠ /usr/share/tessdata 심볼릭 링크 생성에 sudo 권한이 필요합니다."
                echo "  다음 명령을 한 번 실행해주세요:"
                echo "    sudo ln -sf $tessdir /usr/share/tessdata"
                echo ""
            }
            break
        fi
    done
fi
export TESSDATA_PREFIX="/usr/share/tessdata"

# venv의 python으로 실행
"$VENV_DIR/bin/python" "$SCRIPT_DIR/pdf2md.py" "$@"
