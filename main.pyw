"""102 (블록 코딩 자동화 도구) - 실행 파일.  python main.py"""
import ctypes
import json
import os
import threading
import time

try:  # 화면 배율(DPI)이 달라도 좌표가 어긋나지 않도록
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

import webview
from pynput import keyboard

from core import recorder
from core.engine import Engine, EngineError, Stopped

HERE = os.path.dirname(os.path.abspath(__file__))
window = None
stop_event = threading.Event()
busy = threading.Lock()


def js(code):
    try:
        window.evaluate_js(code)
    except Exception:
        pass


def status(msg, kind="info"):
    js(f"onStatus({json.dumps(msg, ensure_ascii=False)}, {json.dumps(kind)})")


def esc_listener():
    def on_press(key):
        if key == keyboard.Key.esc:
            stop_event.set()
    return keyboard.Listener(on_press=on_press)


def run_job(state):
    if not busy.acquire(blocking=False):
        return
    stop_event.clear()
    js("onRunState(true)")
    listener = esc_listener()
    try:
        for n in (3, 2, 1):
            status(f"{n}초 뒤 시작합니다. 작업할 창을 클릭해 두세요. (ESC: 중지)", "run")
            time.sleep(1)
        window.minimize()
        time.sleep(0.5)
        listener.start()
        Engine(stop_event, on_step=lambda i: js(f"highlight({json.dumps(i)})")).run(state)
        msg, kind = "실행이 끝났습니다.", "ok"
    except Stopped:
        msg, kind = "사용자가 중지했습니다.", "warn"
    except EngineError as e:
        msg, kind = f"오류: {e}", "err"
    except Exception as e:  # noqa: BLE001
        msg, kind = f"예기치 않은 오류: {e!r}", "err"
    finally:
        listener.stop()
        window.restore()
        js("highlight(null)")
        js("onRunState(false)")
        busy.release()
    status(msg, kind)


class Api:
    def run(self, state_json):
        threading.Thread(target=run_job, args=(json.loads(state_json),), daemon=True).start()

    def stop(self):
        stop_event.set()

    def pick_file(self):
        r = window.create_file_dialog(
            webview.OPEN_DIALOG, file_types=("Excel 파일 (*.xlsx;*.xlsm;*.xls)", "모든 파일 (*.*)")
        )
        return r[0] if r else None

    def pick_program(self):
        r = window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=("실행 파일 (*.exe;*.bat;*.cmd;*.lnk)", "모든 파일 (*.*)"),
        )
        return r[0] if r else None

    def record_macro(self):
        for n in (3, 2, 1):
            status(f"{n}초 뒤 녹화를 시작합니다. 동작을 수행하고 ESC 로 끝내세요.", "run")
            time.sleep(1)
        window.minimize()
        time.sleep(0.5)
        try:
            events = recorder.record()
        finally:
            window.restore()
        if events:
            status(f"녹화 완료: 이벤트 {len(events)}개", "ok")
        else:
            status("녹화된 동작이 없습니다. 관리자 권한 창에서는 녹화되지 않으니 앱도 관리자 권한으로 실행해 보세요.", "warn")
        return events

    def play_macro(self, events):
        stop_event.clear()
        listener = esc_listener()
        status("2초 뒤 녹화 동작을 재생합니다. (ESC: 중지)", "run")
        time.sleep(2)
        window.minimize()
        time.sleep(0.5)
        listener.start()
        try:
            recorder.replay(events, stop_event, Stopped)
            status("재생 완료", "ok")
        except Stopped:
            status("재생을 중지했습니다.", "warn")
        finally:
            listener.stop()
            window.restore()

    def save_project(self, text):
        r = window.create_file_dialog(
            webview.SAVE_DIALOG, save_filename="project.blocks.json",
            file_types=("블록 프로젝트 (*.json)",),
        )
        if not r:
            return False
        path = r if isinstance(r, str) else r[0]
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return True

    def load_project(self):
        r = window.create_file_dialog(webview.OPEN_DIALOG, file_types=("블록 프로젝트 (*.json)",))
        if not r:
            return None
        with open(r[0], encoding="utf-8") as f:
            return f.read()


def main():
    global window
    scr = webview.screens[0]
    w, h = int(scr.width / 3), int(scr.height * 0.6)  # 가로 33%, 세로 60%
    window = webview.create_window(
        "102",
        url=os.path.join(HERE, "core", "web", "index.html"),
        js_api=Api(),
        width=w, height=h,
        screen=scr,  # 기본 모니터 가운데에 배치
        min_size=(640, 480),
    )
    webview.start()


if __name__ == "__main__":
    try:
        main()
    except Exception:  # pythonw 로 실행하면 오류가 안 보이므로 파일에 남긴다
        import traceback
        with open(os.path.join(HERE, "error.log"), "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise
