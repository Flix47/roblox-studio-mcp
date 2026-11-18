import sys
import os
import json
import platform
import subprocess
import threading

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"

def get_studio_executable():
    if IS_WINDOWS:
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            raise FileNotFoundError("LOCALAPPDATA environment variable not found")
        versions_dir = os.path.join(local, "Roblox", "Versions")
        if not os.path.isdir(versions_dir):
            raise FileNotFoundError(f"Roblox Versions directory not found: {versions_dir}")
        candidates = []
        for entry in os.scandir(versions_dir):
            if not entry.is_dir():
                continue
            exe = os.path.join(entry.path, "RobloxStudioBeta.exe")
            if os.path.isfile(exe):
                candidates.append((entry.stat().st_mtime, exe))
        if not candidates:
            raise FileNotFoundError(
                f"RobloxStudioBeta.exe not found, searched directory: {versions_dir}"
            )
        return max(candidates, key=lambda x: x[0])[1]

    elif IS_MACOS:
        exe = "/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio"
        if not os.path.isfile(exe):
            raise FileNotFoundError(f"Roblox Studio not found: {exe}")
        return exe

    else:
        raise RuntimeError(
            f"Unsupported platform: {platform.system()}. "
            "This script only supports Windows and macOS."
        )


STUDIO_PATH = get_studio_executable()


def pump(src, dst):
    try:
        for line in iter(src.readline, ""):
            if not line:
                break
            dst.write(line)
            dst.flush()
    except Exception:
        pass


def main():
    proc = subprocess.Popen(
        [STUDIO_PATH] + sys.argv[1:],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    threading.Thread(target=pump, args=(proc.stdout, sys.stdout), daemon=True).start()
    threading.Thread(target=pump, args=(proc.stderr, sys.stderr), daemon=True).start()

    try:
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue

            try:
                msg = json.loads(line_str)
                if isinstance(msg, dict) and msg.get("method") == "server/discover":
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg.get("id"),
                        "error": {
                            "code": -32601,
                            "message": "Method not found",
                        },
                    }
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
                    continue
            except Exception:
                pass

            if proc.poll() is not None:
                break

            if proc.stdin is None:
                break

            try:
                proc.stdin.write(line_str + "\n")
                proc.stdin.flush()
            except (BrokenPipeError, OSError):
                break

    except (KeyboardInterrupt, BrokenPipeError):
        pass
    finally:
        if proc.stdin is not None:
            try:
                proc.stdin.close()
            except Exception:
                pass
        proc.wait()


if __name__ == "__main__":
    main()
