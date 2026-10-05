"""저장한 블록 프로젝트(JSON)를 화면 없이 바로 실행한다. (예약 실행용)

    python runner.py 내작업.blocks.json
    python runner.py 내작업.blocks.json --delay 5 --log run.log
    pythonw runner.py 내작업.blocks.json --log run.log      (콘솔 창 없이)

실행 중 ESC 를 누르면 멈춥니다.
종료 코드: 0 정상 / 1 실행 중 오류 / 2 사용자가 중지 / 3 파일을 읽을 수 없음
"""
import argparse
import json
import os
import sys
import threading
import time
from datetime import datetime

from pynput import keyboard

from core.engine import Engine, EngineError, Stopped

EXIT_OK, EXIT_ERROR, EXIT_STOPPED, EXIT_BAD_FILE = 0, 1, 2, 3


class Logger:
    """콘솔(있으면)과 로그 파일(지정하면)에 시각과 함께 기록."""

    def __init__(self, path=None, quiet=False):
        self.path, self.quiet = path, quiet

    def __call__(self, msg):
        line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
        if not self.quiet and sys.stdout:  # pythonw 로 실행하면 콘솔이 없음
            try:
                print(line, flush=True)
            except Exception:
                pass
        if self.path:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")


def load_project(path):
    try:
        with open(path, encoding="utf-8-sig") as f:  # 메모장이 붙이는 BOM 도 허용
            state = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"파일이 없습니다: {path}")
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"프로젝트 파일을 읽을 수 없습니다: {e}")
    if not isinstance(state, dict) or not isinstance(state.get("blocks", {}).get("blocks"), list):
        raise ValueError("블록 프로젝트 파일이 아닙니다. 앱에서 [저장]한 .json 파일을 지정하세요.")
    return state


def block_types(state):
    """블록 id -> 종류 (진행 상황을 읽기 쉽게 기록하기 위함)."""
    found = {}

    def walk(x):
        if isinstance(x, dict):
            if "id" in x and "type" in x:
                found[x["id"]] = x["type"]
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(state)
    return found


def run(path, delay=0.0, log_path=None, quiet=False, verbose=False):
    log = Logger(log_path, quiet)
    try:
        state = load_project(path)
    except ValueError as e:
        log(f"오류: {e}")
        return EXIT_BAD_FILE

    stop = threading.Event()

    def on_press(key):
        if key == keyboard.Key.esc:
            stop.set()

    listener = keyboard.Listener(on_press=on_press)
    types = block_types(state) if verbose else {}
    name = os.path.basename(path)
    try:
        if delay > 0:
            log(f"{name}: {delay:g}초 뒤 시작합니다. (ESC: 중지)")
            end = time.time() + delay
            while time.time() < end:
                time.sleep(0.1)
        listener.start()
        log(f"{name}: 시작")
        started = time.time()
        step = (lambda i: log(f"  블록: {types.get(i, i)}")) if verbose else None
        Engine(stop, on_step=step).run(state)
        log(f"{name}: 끝 ({time.time() - started:.1f}초)")
        return EXIT_OK
    except Stopped:
        log(f"{name}: 사용자가 중지했습니다.")
        return EXIT_STOPPED
    except EngineError as e:
        log(f"{name}: 오류: {e}")
        return EXIT_ERROR
    except Exception as e:  # noqa: BLE001
        log(f"{name}: 예기치 않은 오류: {e!r}")
        return EXIT_ERROR
    finally:
        listener.stop()


def main(argv=None):
    p = argparse.ArgumentParser(description="저장한 블록 프로젝트(JSON)를 화면 없이 실행합니다.")
    p.add_argument("project", help="앱에서 저장한 .json 파일")
    p.add_argument("--delay", type=float, default=0.0, help="시작 전 대기 초 (기본 0)")
    p.add_argument("--log", help="실행 기록을 덧붙여 쓸 파일")
    p.add_argument("--quiet", action="store_true", help="콘솔에 출력하지 않음")
    p.add_argument("--verbose", action="store_true", help="실행하는 블록 종류를 하나씩 기록")
    a = p.parse_args(argv)
    return run(a.project, a.delay, a.log, a.quiet, a.verbose)


if __name__ == "__main__":
    sys.exit(main())
