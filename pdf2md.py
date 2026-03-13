#!/usr/bin/env python3
"""PDF 파일들을 pymupdf4llm을 이용하여 LLM용 마크다운으로 변환하는 프로그램."""

import argparse
import os
import sys
import time
from pathlib import Path


def convert_pdfs(input_dir: str, output_dir: str | None = None, *, page_chunks: bool = False):
    """지정된 폴더의 모든 PDF 파일을 마크다운으로 변환합니다.

    Args:
        input_dir: PDF 파일이 있는 폴더 경로
        output_dir: 마크다운 파일을 저장할 폴더 경로 (미지정 시 input_dir 사용)
        page_chunks: True이면 페이지별 메타데이터를 포함한 JSON도 함께 저장
    """
    import pymupdf4llm

    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"오류: '{input_dir}' 폴더가 존재하지 않습니다.")
        sys.exit(1)

    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(input_path.glob("*.pdf"))
    if not pdf_files:
        print(f"'{input_dir}' 폴더에 PDF 파일이 없습니다.")
        sys.exit(0)

    print(f"총 {len(pdf_files)}개의 PDF 파일을 발견했습니다.")
    print(f"출력 폴더: {output_path}\n")

    success_count = 0
    fail_count = 0

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] 변환 중: {pdf_file.name}")
        start_time = time.time()

        try:
            if page_chunks:
                chunks = pymupdf4llm.to_markdown(
                    str(pdf_file),
                    page_chunks=True,
                    write_images=True,
                    image_path=str(output_path),
                )

                # 전체 마크다운 텍스트 합치기
                markdown_text = "\n\n".join(chunk["text"] for chunk in chunks)

                # 페이지별 청크 메타데이터를 JSON으로 저장
                import json
                json_filepath = output_path / (pdf_file.stem + "_chunks.json")
                json_filepath.write_text(
                    json.dumps(chunks, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                print(f"  청크 메타데이터 -> {json_filepath}")
            else:
                markdown_text = pymupdf4llm.to_markdown(
                    str(pdf_file),
                    write_images=True,
                    image_path=str(output_path),
                )

            md_filename = pdf_file.stem + ".md"
            md_filepath = output_path / md_filename
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
    args = parser.parse_args()

    convert_pdfs(args.input_dir, args.output_dir, page_chunks=args.chunks)


if __name__ == "__main__":
    main()
