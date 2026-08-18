# Sandbox

Executable coding material is treated as potentially hostile.

## Backends

1. **Docker** (preferred when `docker` is available): `--network none`, CPU/memory/PID limits, read-only root, tmpfs `/tmp`.
2. **Subprocess fallback**: temporary directory, timeout, stripped environment, POSIX `resource` limits when the OS supports them.

The subprocess backend is **not** equivalent to a container. Do not use it to execute arbitrary third-party code on a trusted host. v0.1 verified coding tasks are generator-owned, but the engine still isolates them.

## Limits (defaults)

- timeout: 12s
- memory: 512 MB (Docker / POSIX)
- no outbound network in Docker mode

## Cleanup

Work directories are deleted after each run.
