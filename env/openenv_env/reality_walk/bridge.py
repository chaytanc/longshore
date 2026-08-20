"""MCPWalkBridge — a thin, synchronous bridge to the published walk MCP server.

The design choice that keeps this honest: we do NOT reimplement the world. The
world is the npm package `reality-next-door-walk` (source of truth: ../walk/).
This bridge launches that MCP server as a stdio subprocess and speaks MCP to it
with the official Python `mcp` SDK. Every `look/go/talk_to/do/work/map/where`
in the environment is a real MCP tool call to that one server, so there is zero
drift between "the world an agent walks here" and "the world we publish."

The `mcp` SDK is async; OpenEnv's `Environment.step()` and the Verifiers reward
path are sync. So we run the MCP `ClientSession` on a dedicated event loop in a
background thread and marshal each call across with
`asyncio.run_coroutine_threadsafe`. Closing the bridge exits the `stdio_client`
context, which terminates the subprocess — no orphaned node processes.

No network of its own: the bridge only opens a stdio pipe to a local child
process. The default launch command (`npx -y reality-next-door-walk`) makes npx
fetch the package the first time; point it at a local `node .../walk/server.js`
(see `for_local_walk`) for fully offline runs, which is what the tests use. The
walk server itself makes zero network calls (grep it — see ../walk/README.md).
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Dict, List, Optional, Sequence

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# The npm package name — the single published source of truth for the world.
WALK_PACKAGE = "reality-next-door-walk"
DEFAULT_COMMAND = "npx"
DEFAULT_ARGS: Sequence[str] = ("-y", WALK_PACKAGE)

# The eight tools the walk server exposes (see ../walk/server.js).
WALK_TOOLS = ("look", "go", "talk_to", "do", "work", "map", "where", "join")


class MCPWalkBridge:
    """Launch the walk MCP server as a subprocess and call its tools synchronously.

    Args:
        command: executable to launch (default ``npx``).
        args: arguments (default ``-y reality-next-door-walk``).
        cwd: working directory for the subprocess.
        env: environment for the subprocess (``None`` inherits the parent's).
        call_timeout_s: per-tool-call timeout.
        start_timeout_s: how long to wait for the server to initialize.
    """

    def __init__(
        self,
        command: Optional[str] = None,
        args: Optional[Sequence[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        call_timeout_s: float = 30.0,
        start_timeout_s: float = 60.0,
    ) -> None:
        if command is None:
            command = DEFAULT_COMMAND
            args = list(DEFAULT_ARGS)
        self._params = StdioServerParameters(
            command=command,
            args=list(args or []),
            cwd=cwd,
            env=env,
        )
        self._call_timeout = call_timeout_s
        self._start_timeout = start_timeout_s

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._session: Optional[ClientSession] = None
        self._ready = threading.Event()
        self._error: Optional[BaseException] = None
        self._stop: Optional[asyncio.Event] = None
        self._closed = False

    # -- construction helpers -------------------------------------------------

    @classmethod
    def for_local_walk(cls, server_js_path: str, **kwargs: Any) -> "MCPWalkBridge":
        """Bridge to a local ``node <path>/server.js`` — no network, for tests."""
        return cls(command="node", args=[server_js_path], **kwargs)

    @classmethod
    def for_npx(cls, **kwargs: Any) -> "MCPWalkBridge":
        """Bridge to the published package via ``npx -y reality-next-door-walk``."""
        return cls(command=DEFAULT_COMMAND, args=list(DEFAULT_ARGS), **kwargs)

    # -- lifecycle ------------------------------------------------------------

    def start(self) -> "MCPWalkBridge":
        if self._thread is not None:
            return self
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run, name="mcp-walk-bridge", daemon=True
        )
        self._thread.start()
        if not self._ready.wait(self._start_timeout):
            self.close()
            raise TimeoutError(
                f"walk MCP server did not become ready within {self._start_timeout}s "
                f"(command: {self._params.command} {' '.join(self._params.args)})"
            )
        if self._error is not None:
            err = self._error
            self.close()
            raise RuntimeError(f"failed to start walk MCP server: {err!r}") from err
        return self

    def _run(self) -> None:
        assert self._loop is not None
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._serve())
        finally:
            self._loop.close()

    async def _serve(self) -> None:
        self._stop = asyncio.Event()
        try:
            async with stdio_client(self._params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    self._session = session
                    self._ready.set()
                    await self._stop.wait()
        except BaseException as exc:  # noqa: BLE001 - surface any startup failure
            self._error = exc
            self._session = None
            self._ready.set()

    def close(self) -> None:
        """Stop the session and terminate the subprocess. Idempotent."""
        if self._closed:
            return
        self._closed = True
        loop, thread, stop = self._loop, self._thread, self._stop
        if loop is not None and stop is not None and not loop.is_closed():
            try:
                loop.call_soon_threadsafe(stop.set)
            except RuntimeError:
                pass
        if thread is not None:
            thread.join(timeout=15)
        self._session = None

    def __enter__(self) -> "MCPWalkBridge":
        return self.start()

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- calling tools --------------------------------------------------------

    def call(self, tool: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Call an MCP tool and return its concatenated text content."""
        if self._closed:
            raise RuntimeError("bridge is closed")
        if self._session is None or self._loop is None:
            raise RuntimeError("bridge not started; call start() first")
        coro = self._session.call_tool(tool, arguments or {})
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        result = fut.result(timeout=self._call_timeout)
        return self._extract_text(result)

    def list_tools(self) -> List[str]:
        """Return the tool names the server advertises (for a startup sanity check)."""
        if self._session is None or self._loop is None:
            raise RuntimeError("bridge not started; call start() first")
        fut = asyncio.run_coroutine_threadsafe(self._session.list_tools(), self._loop)
        result = fut.result(timeout=self._call_timeout)
        return [t.name for t in result.tools]

    @staticmethod
    def _extract_text(result: Any) -> str:
        parts: List[str] = []
        for block in getattr(result, "content", None) or []:
            text = getattr(block, "text", None)
            if text is not None:
                parts.append(text)
        return "\n".join(parts)
