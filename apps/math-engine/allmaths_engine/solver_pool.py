"""Runs every solve in a separate worker process with a time limit.

A symbolic computation (an integral, a limit, a differential equation) can take arbitrarily long on a hostile or unlucky input.
The request is therefore sent to a worker process; if the answer does not arrive in time the worker is killed and replaced, so the
web server and the other learners are never blocked.
"""

from __future__ import annotations

import multiprocessing as mp
import queue
import threading
from dataclasses import asdict
from typing import Any

DEFAULT_TIMEOUT = 15.0


def _worker(conn: Any) -> None:  # runs in the child process
    from .solver import solve_text
    from .solver.types import SolverError

    while True:
        try:
            text, operation = conn.recv()
        except EOFError:
            return
        try:
            if operation == "_graph":
                import json

                from .graph_exact import exact_points

                conn.send(("ok", exact_points(json.loads(text))))
                continue
            sol = solve_text(text, operation)
            conn.send(("ok", asdict(sol)))
        except SolverError as exc:
            conn.send(("error", exc.code, exc.message))
        except RecursionError:
            conn.send(("error", "too_complex", "This problem is too complicated for me."))
        except Exception:  # noqa: BLE001 - never let a crash hide as a wrong answer
            conn.send(("error", "internal", "I could not solve this problem."))


def _slow_worker_for_tests(conn: Any) -> None:  # used by the tests to prove that a stuck worker is killed
    import time

    conn.recv()
    time.sleep(60)


class _Worker:
    def __init__(self, ctx: Any, target: Any = None) -> None:
        self.ctx = ctx
        self.target = target or _worker
        self.start()

    def start(self) -> None:
        self.parent, child = self.ctx.Pipe()
        self.proc = self.ctx.Process(target=self.target, args=(child,), daemon=True)
        self.proc.start()
        child.close()

    def kill(self) -> None:
        try:
            self.proc.kill()
            self.proc.join(2)
        except Exception:  # noqa: BLE001
            pass
        try:
            self.parent.close()
        except Exception:  # noqa: BLE001
            pass


class SolverPool:
    def __init__(self, workers: int = 2, timeout: float = DEFAULT_TIMEOUT, target: Any = None) -> None:
        self.timeout = timeout
        self._target = target
        self._ctx = mp.get_context("spawn")
        self._free: queue.Queue[_Worker] = queue.Queue()
        self._lock = threading.Lock()
        self._workers = workers
        self._started = False

    def _ensure(self) -> None:
        with self._lock:
            if not self._started:
                for _ in range(self._workers):
                    self._free.put(_Worker(self._ctx, self._target))
                self._started = True

    def run(self, text: str, operation: str) -> dict[str, Any]:
        """The solution as a dict, or {"error": code, "message": ...}."""
        self._ensure()
        try:
            worker = self._free.get(timeout=self.timeout)
        except queue.Empty:
            return {"error": "busy", "message": "The solver is busy. Please try again in a moment."}
        try:
            worker.parent.send((text, operation))
            if not worker.parent.poll(self.timeout):
                worker.kill()
                worker.start()
                return {"error": "timeout", "message": "This problem took too long. Try a simpler form of it."}
            reply = worker.parent.recv()
        except (EOFError, OSError, BrokenPipeError):
            worker.kill()
            worker.start()
            return {"error": "internal", "message": "I could not solve this problem."}
        finally:
            self._free.put(worker)
        if reply[0] == "ok":
            return {"solution": reply[1]}
        return {"error": reply[1], "message": reply[2]}

    def close(self) -> None:
        while not self._free.empty():
            self._free.get_nowait().kill()


_pool: SolverPool | None = None


def get_pool() -> SolverPool:
    global _pool
    if _pool is None:
        _pool = SolverPool()
    return _pool
