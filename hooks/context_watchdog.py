"""Claude Code Stop / SubagentStop hook: warn the user when a conversation's context gets long.

Every reply re-sends the whole context, so a turn at 900K tokens costs ~4x one at 250K.
Reads the tail of the transcript, takes context = input + cache_read + cache_creation tokens
of the last assistant message, and prints a systemMessage at the warn / strong thresholds
(warn once, then re-warn every `rewarn_step` tokens past `strong`). Also appends a log line.

Config: context_watchdog.json next to this file (warn, strong, rewarn_step, log).
The log path can also be set with the AG_TOKEN_LOG environment variable.
"""
import sys, os, json, time
from pathlib import Path

H = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG = str(Path.home() / ".claude" / "hooks" / "token_watch.log")


def main():
    d = json.loads(sys.stdin.read() or "{}")
    sub = d.get("hook_event_name", "") == "SubagentStop"
    p = (d.get("agent_transcript_path") if sub else None) or d.get("transcript_path")
    if not p or not os.path.isfile(p):
        return
    sid = str((d.get("agent_id") or d.get("session_id") or "x") if sub else (d.get("session_id") or "x"))
    try:
        with open(os.path.join(H, "context_watchdog.json")) as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    warn = cfg.get("warn", 250000)
    strong = cfg.get("strong", 450000)
    step = cfg.get("rewarn_step", 150000)
    log = os.environ.get("AG_TOKEN_LOG") or cfg.get("log") or DEFAULT_LOG
    log = os.path.expanduser(os.path.expandvars(log))
    with open(p, "rb") as f:
        size = f.seek(0, 2)
        f.seek(max(0, size - 2_000_000))
        data = f.read()
    ctx = None
    for line in reversed(data.split(b"\n")):
        if b'"usage"' not in line or b'"assistant"' not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        u = (o.get("message") or {}).get("usage")
        if o.get("type") == "assistant" and u:
            ctx = (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
            break
    if ctx is None or ctx < warn:
        return
    level = "STRONG" if ctx >= strong else "WARN"
    sf = os.path.join(H, "state", "".join(c for c in sid if c.isalnum() or c in "-_")[:80] + ".json")
    try:
        with open(sf) as f:
            st = json.load(f)
    except Exception:
        st = {}
    if level == "WARN":
        if st.get("warn"):
            return
        st["warn"] = ctx
    else:
        last = st.get("strong")
        if last and ctx < last + step:
            return
        st["strong"] = ctx
    os.makedirs(os.path.dirname(sf), exist_ok=True)
    with open(sf, "w") as f:
        json.dump(st, f)
    try:
        os.makedirs(os.path.dirname(log) or ".", exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%s\t%s\t%dK\t%s\n" % (time.strftime("%Y-%m-%d %H:%M"), "subagent" if sub else "session", sid, d.get("cwd", ""), ctx // 1000, level))
    except Exception:
        pass
    if not sub:
        mult = "~4x" if level == "STRONG" else "~2x"
        print(json.dumps({"systemMessage": "⚠ Token saver: this conversation is %dK tokens long; each reply re-reads all of it (%s the cost of a fresh one). Ask Claude to write a handoff note, then start a new session (or /compact)." % (ctx // 1000, mult)}))


try:
    main()
except Exception:
    pass
sys.exit(0)
