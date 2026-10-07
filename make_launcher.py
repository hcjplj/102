"""저장한 블록 프로젝트(JSON)를 골라 '더블클릭하면 바로 실행되는 파일'을 만든다.  python make_launcher.py

JSON 파일 옆에 같은 이름의 .exe (JSON 이 안에 들어가 파이썬 없는 PC 에서도 실행) 또는
.bat (이 PC 의 파이썬으로 실행) 가 생긴다. 실행 기록은 옆에 .log 파일로 쌓인다.
exe 를 만들려면 pip install pyinstaller 가 필요하다.

이 파일은 실행기도 겸한다:  python make_launcher.py --run 내작업.json [--delay 5] [--log run.log] [--quiet]
실행 중 ESC 로 멈춘다. 종료 코드: 0 정상 / 1 오류 / 2 사용자가 중지 / 3 파일을 읽을 수 없음
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = getattr(sys, "frozen", False)
EXIT_OK, EXIT_ERROR, EXIT_STOPPED, EXIT_BAD_FILE = 0, 1, 2, 3


# ───────────────────────── 실행기 ─────────────────────────

def run(path, delay=0.0, log_path=None, quiet=False):
    from pynput import keyboard
    from core.engine import Engine, EngineError, Stopped

    def log(msg):
        line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
        if not quiet and sys.stdout:  # 콘솔 없이 실행하면 stdout 이 없다
            try:
                print(line, flush=True)
            except Exception:
                pass
        if log_path:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    try:
        with open(path, encoding="utf-8-sig") as f:  # 메모장이 붙이는 BOM 도 허용
            state = json.load(f)
        if not isinstance(state.get("blocks", {}).get("blocks"), list):
            raise ValueError("블록 프로젝트 파일이 아닙니다. 앱에서 [저장]한 .json 파일을 지정하세요.")
    except (OSError, ValueError, AttributeError) as e:
        log(f"오류: 프로젝트 파일을 읽을 수 없습니다: {e}")
        return EXIT_BAD_FILE

    stop = threading.Event()
    listener = keyboard.Listener(on_press=lambda k: stop.set() if k == keyboard.Key.esc else None)
    name = os.path.basename(path)
    try:
        if delay > 0:
            log(f"{name}: {delay:g}초 뒤 시작합니다. (ESC: 중지)")
            time.sleep(delay)
        listener.start()
        log(f"{name}: 시작")
        started = time.time()
        Engine(stop).run(state)
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


def run_main(argv):
    p = argparse.ArgumentParser(description="저장한 블록 프로젝트(JSON)를 화면 없이 실행합니다.")
    p.add_argument("--run", metavar="JSON", help="실행할 .json 파일")
    p.add_argument("--delay", type=float, default=0.0, help="시작 전 대기 초")
    p.add_argument("--log", help="실행 기록을 덧붙여 쓸 파일")
    p.add_argument("--quiet", action="store_true", help="콘솔에 출력하지 않음")
    a = p.parse_args(argv)
    if FROZEN:  # exe 로 묶인 경우: 안에 든 JSON 을 실행, 기록은 exe 옆에
        return run(os.path.join(sys._MEIPASS, "project.json"), a.delay,
                   a.log or os.path.splitext(sys.executable)[0] + ".log", a.quiet)
    return run(a.run, a.delay, a.log, a.quiet)


# ───────────────────────── 파일 만들기 ─────────────────────────

def make_bat(json_path, delay):
    base = os.path.splitext(os.path.basename(json_path))[0]
    args = f" --delay {delay:g}" if delay > 0 else ""
    # JSON 과 로그는 .bat 위치 기준(%~dp0)이라 폴더째 옮겨도 동작한다
    return (
        "@echo off\r\n"
        f'"{sys.executable}" "{os.path.abspath(__file__)}" --run "%~dp0{os.path.basename(json_path)}"'
        f' --log "%~dp0{base}.log"{args}\r\n'
        "if errorlevel 1 (echo. & echo 오류 또는 중지로 끝났습니다. 위 내용을 확인하세요. & pause)\r\n"
    )


def build_exe(json_path, delay, hidden):
    """PyInstaller 로 이 파일 + core + JSON 을 exe 하나로 묶는다."""
    if delay > 0:
        raise OSError("exe 는 대기 시간을 지원하지 않습니다. (.bat 을 쓰거나 블록의 '대기'를 쓰세요)")
    out_dir = os.path.dirname(json_path)
    name = os.path.splitext(os.path.basename(json_path))[0]
    work = tempfile.mkdtemp(prefix="make_launcher_")
    try:
        copy = os.path.join(work, "project.json")  # 묶인 JSON 은 항상 project.json 이름
        shutil.copyfile(json_path, copy)
        cmd = [
            sys.executable, "-m", "PyInstaller", "--onefile", "--noconfirm", "--clean",
            "--noconsole" if hidden else "--console",
            "--name", name, "--distpath", out_dir, "--workpath", work, "--specpath", work,
            "--add-data", f"{copy}{os.pathsep}.", "--paths", HERE,
            "--exclude-module", "tkinter", os.path.abspath(__file__),
        ]
        r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            tail = r.stderr.strip().splitlines()[-8:]
            raise OSError("exe 빌드 실패: " + " / ".join(tail))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return os.path.join(out_dir, name + ".exe")


def write_launcher(json_path, delay, hidden, kind):
    json_path = os.path.abspath(json_path)
    if kind == "exe":
        return build_exe(json_path, delay, hidden)
    out = os.path.splitext(json_path)[0] + ".bat"
    with open(out, "w", encoding="mbcs", newline="") as f:  # 한글 경로를 위해 시스템 기본 인코딩
        f.write(make_bat(json_path, delay))
    return out


def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title("실행 파일 만들기")
    root.resizable(False, False)
    hidden = tk.BooleanVar(value=False)
    delay = tk.StringVar(value="0")
    kind = tk.StringVar(value="exe")

    tk.Label(root, text="저장한 .json 프로젝트를 골라 실행 파일을 만듭니다.").grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 6))
    tk.Label(root, text="시작 전 대기(초)").grid(row=1, column=0, sticky="e", padx=(12, 4))
    tk.Entry(root, textvariable=delay, width=6).grid(row=1, column=1, sticky="w")
    tk.Radiobutton(root, text="exe (파이썬 없이 실행, 만드는 데 1분 정도)", variable=kind, value="exe").grid(row=2, column=0, columnspan=2, sticky="w", padx=12)
    tk.Radiobutton(root, text="bat (이 PC의 파이썬 사용, 즉시 생성)", variable=kind, value="bat").grid(row=3, column=0, columnspan=2, sticky="w", padx=12)
    tk.Checkbutton(root, text="콘솔 창 없이 실행 (exe 만)", variable=hidden).grid(row=4, column=0, columnspan=2, pady=4)

    def go():
        try:
            d = float(delay.get() or 0)
        except ValueError:
            messagebox.showerror("입력 오류", "대기 시간은 숫자로 입력하세요.")
            return
        paths = filedialog.askopenfilenames(title="프로젝트 선택 (여러 개 가능)", filetypes=[("블록 프로젝트", "*.json")])
        made, failed = [], []
        for p in paths:
            root.title("만드는 중... 잠시 기다려 주세요")
            root.update()
            try:
                made.append(write_launcher(p, d, hidden.get(), kind.get()))
            except (OSError, UnicodeEncodeError) as e:
                failed.append(f"{os.path.basename(p)}: {e}")
        root.title("실행 파일 만들기")
        if made:
            messagebox.showinfo("완료", "만든 파일:\n" + "\n".join(made))
        if failed:
            messagebox.showerror("실패", "\n".join(failed))

    tk.Button(root, text="JSON 선택하고 만들기", command=go, width=24).grid(row=5, column=0, columnspan=2, padx=12, pady=(6, 12))
    root.mainloop()


if __name__ == "__main__":
    if FROZEN or "--run" in sys.argv:
        sys.exit(run_main(sys.argv[1:]))
    gui()
