"""pynput 으로 마우스/키보드 동작을 녹화하고 재생한다. (ESC 로 녹화 종료)"""
import threading
import time

from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode

_kb = keyboard.Controller()
_mouse = mouse.Controller()


def _encode_key(key):
    if isinstance(key, Key):
        return {"k": "s", "v": key.name}
    if getattr(key, "vk", None) is not None:
        return {"k": "v", "v": key.vk}
    return {"k": "c", "v": key.char}


def _decode_key(d):
    if d["k"] == "s":
        return Key[d["v"]]
    if d["k"] == "v":
        return KeyCode.from_vk(d["v"])
    return KeyCode.from_char(d["v"])


def record(max_seconds=600):
    """ESC 를 누를 때까지 녹화하고 이벤트 리스트를 반환."""
    events = []
    done = threading.Event()
    last = [time.time()]

    def add(**ev):
        now = time.time()
        ev["t"] = round(min(now - last[0], 5.0), 3)  # 너무 긴 공백은 5초로 제한
        last[0] = now
        events.append(ev)

    def on_click(x, y, button, pressed):
        add(type="mouse", x=x, y=y, button=button.name, pressed=pressed)

    def on_scroll(x, y, dx, dy):
        add(type="scroll", x=x, y=y, dx=dx, dy=dy)

    def on_press(key):
        if key == Key.esc:
            done.set()
            return False
        add(type="key", key=_encode_key(key), pressed=True)

    def on_release(key):
        if key == Key.esc:
            return
        add(type="key", key=_encode_key(key), pressed=False)

    ml = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    kl = keyboard.Listener(on_press=on_press, on_release=on_release)
    ml.start()
    kl.start()
    done.wait(max_seconds)
    ml.stop()
    kl.stop()
    return events


def replay(events, stop_event, stopped_exc=Exception):
    """녹화된 이벤트를 재생. stop_event 가 켜지면 stopped_exc 를 던진다."""
    for ev in events:
        end = time.time() + ev.get("t", 0)
        while time.time() < end:
            if stop_event.is_set():
                raise stopped_exc()
            time.sleep(min(0.02, max(0, end - time.time())))
        if stop_event.is_set():
            raise stopped_exc()
        kind = ev["type"]
        if kind == "mouse":
            _mouse.position = (ev["x"], ev["y"])
            time.sleep(0.05)  # 이동 직후 바로 누르면 무시하는 프로그램이 있어 잠깐 대기
            btn = getattr(mouse.Button, ev["button"], mouse.Button.left)
            (_mouse.press if ev["pressed"] else _mouse.release)(btn)
        elif kind == "scroll":
            _mouse.position = (ev["x"], ev["y"])
            _mouse.scroll(ev["dx"], ev["dy"])
        elif kind == "key":
            key = _decode_key(ev["key"])
            (_kb.press if ev["pressed"] else _kb.release)(key)
            time.sleep(0.01)
