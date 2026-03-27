#!/usr/bin/env python3
"""PDF 파일들을 pymupdf4llm을 이용하여 LLM용 마크다운으로 변환하는 프로그램."""

import argparse
import os
import sys
import time
from pathlib import Path


def _find_tessdata():
    """시스템에서 tessdata 디렉토리를 찾아 TESSDATA_PREFIX를 설정합니다."""
    # 이미 올바르게 설정되어 있으면 스킵
    prefix = os.environ.get("TESSDATA_PREFIX", "")
    if prefix and Path(prefix).joinpath("eng.traineddata").exists():
        return prefix

    candidates = [
        "/usr/share/tesseract-ocr/5/tessdata",
        "/usr/share/tesseract-ocr/4/tessdata",
        "/usr/share/tesseract-ocr/3/tessdata",
        "/usr/share/tessdata",
        "/opt/homebrew/share/tessdata",
        "/usr/local/share/tessdata",
    ]
    for path in candidates:
        if Path(path).joinpath("eng.traineddata").exists():
            os.environ["TESSDATA_PREFIX"] = path
            return path

    return None


def convert_pdfs(input_dir: str, output_dir: str | None = None, *, page_chunks: bool = False, use_ocr: bool = False):
    """지정된 폴더의 모든 PDF 파일을 마크다운으로 변환합니다.

    Args:
        input_dir: PDF 파일이 있는 폴더 경로
        output_dir: 마크다운 파일을 저장할 폴더 경로 (미지정 시 input_dir 사용)
        page_chunks: True이면 페이지별 메타데이터를 포함한 JSON도 함께 저장
        use_ocr: True이면 Tesseract OCR 사용 (기본값: False)
    """
    if use_ocr:
        tessdata = _find_tessdata()
        if tessdata:
            print(f"모드: OCR 활성 (tessdata: {tessdata})")
        else:
            print("오류: Tesseract 언어 데이터(eng.traineddata)를 찾을 수 없습니다.")
            print("  설치: sudo apt install tesseract-ocr tesseract-ocr-kor")
            sys.exit(1)
    else:
        print("모드: 텍스트 추출 (OCR 비활성)")

    import pymupdf4llm

    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"오류: '{input_dir}' 폴더가 존재하지 않습니다.")
        sys.exit(1)

    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)

    # 하위 폴더 포함 재귀 탐색
    pdf_files = sorted(input_path.rglob("*.pdf"))
    if not pdf_files:
        print(f"'{input_dir}' 폴더(하위 포함)에 PDF 파일이 없습니다.")
        sys.exit(0)

    print(f"총 {len(pdf_files)}개의 PDF 파일을 발견했습니다. (하위 폴더 포함)")
    print(f"출력 폴더: {output_path}\n")

    success_count = 0
    fail_count = 0

    for i, pdf_file in enumerate(pdf_files, 1):
        # 입력 폴더 기준 상대 경로를 유지하여 출력 폴더에 동일 구조 생성
        rel_path = pdf_file.relative_to(input_path)
        file_output_dir = output_path / rel_path.parent
        file_output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[{i}/{len(pdf_files)}] 변환 중: {rel_path}")
        start_time = time.time()

        try:
            md_kwargs = {
                "write_images": False,
                "use_ocr": use_ocr,
            }
            if page_chunks:
                md_kwargs["page_chunks"] = True

            result = pymupdf4llm.to_markdown(str(pdf_file), **md_kwargs)

            if page_chunks:
                # 전체 마크다운 텍스트 합치기
                markdown_text = "\n\n".join(chunk["text"] for chunk in result)

                # 페이지별 청크 메타데이터를 JSON으로 저장
                import json
                json_filepath = file_output_dir / (pdf_file.stem + "_chunks.json")
                json_filepath.write_text(
                    json.dumps(result, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                print(f"  청크 메타데이터 -> {json_filepath}")
            else:
                markdown_text = result

            md_filename = pdf_file.stem + ".md"
            md_filepath = file_output_dir / md_filename
            md_filepath.write_text(markdown_text, encoding="utf-8")

            elapsed = time.time() - start_time
            print(f"  완료: {md_filepath} ({elapsed:.1f}초)")
            success_count += 1

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"  실패: {e} ({elapsed:.1f}초)")
            fail_count += 1

    print(f"\n변환 완료: 성공 {success_count}개, 실패 {fail_count}개")


def main():
    parser = argparse.ArgumentParser(
        description="PDF 파일들을 pymupdf4llm을 이용하여 LLM용 마크다운으로 변환합니다."
    )
    parser.add_argument("input_dir", help="PDF 파일이 있는 폴더 경로")
    parser.add_argument(
        "-o", "--output-dir",
        help="마크다운 파일을 저장할 폴더 경로 (기본값: 입력 폴더와 동일)",
    )
    parser.add_argument(
        "--chunks",
        action="store_true",
        help="페이지별 청크 메타데이터를 JSON으로 함께 저장",
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Tesseract OCR 활성화 (스캔된 이미지 PDF용, Tesseract 설치 필요)",
    )
    args = parser.parse_args()

    convert_pdfs(args.input_dir, args.output_dir, page_chunks=args.chunks, use_ocr=args.ocr)


if __name__ == "__main__":
    main()
