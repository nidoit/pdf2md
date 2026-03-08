#!/bin/bash
# PDF to Markdown 변환 실행 스크립트
# venv를 자동으로 생성하고 marker-pdf를 설치한 후 변환을 실행합니다.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# 시스템 빌드 의존성 확인 (Arch Linux)
check_arch_deps() {
    if command -v pacman &>/dev/null; then
        local missing=()
        for pkg in python python-pillow python-numpy; do
            if ! pacman -Qi "$pkg" &>/dev/null; then
                missing+=("$pkg")
            fi
        done
        if [ ${#missing[@]} -gt 0 ]; then
            echo "필요한 시스템 패키지가 없습니다. 먼저 설치해주세요:"
            echo ""
            echo "  sudo pacman -S ${missing[*]}"
            echo ""
            exit 1
        fi
    fi
}

# marker-pdf 설치 함수
install_marker() {
    check_arch_deps
    echo "marker-pdf 설치 중... (시간이 걸릴 수 있습니다)"
    "$VENV_DIR/bin/pip" install --upgrade pip
    # Pillow, numpy 등은 시스템 패키지를 사용하고 소스 빌드를 하지 않음
    "$VENV_DIR/bin/pip" install --only-binary Pillow,numpy -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo ""
        echo "설치 실패. .venv 폴더를 삭제 후 다시 시도하세요:"
        echo "  rm -rf $VENV_DIR"
        exit 1
    fi
    echo "설치 완료."
    echo ""
}

# venv가 없으면 생성
if [ ! -d "$VENV_DIR" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv --system-site-packages "$VENV_DIR"
    install_marker
# venv는 있지만 marker가 설치되지 않은 경우
elif ! "$VENV_DIR/bin/python" -c "import marker" 2>/dev/null; then
    echo "marker-pdf가 설치되어 있지 않습니다. 설치를 진행합니다."
    install_marker
fi

# venv의 python으로 실행
"$VENV_DIR/bin/python" "$SCRIPT_DIR/pdf2md.py" "$@"
