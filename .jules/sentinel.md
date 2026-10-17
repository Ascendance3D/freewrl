## 2025-02-21 - [Command Injection in Browser Launch]
**Vulnerability:** Shell command injection in `startNewHTMLWindow` (`freex3d/src/lib/plugin/pluginUtils.c`) due to passing an unescaped Anchor URL directly to `system()` and `freewrlSystem()`.
**Learning:** The URL was substituted directly into a shell command using `sprintf`, which allows an attacker to terminate the command and inject arbitrary shell code. The `freewrlSystem()` wrapper used `execl` by splitting on spaces but failed to validate the arguments or resolve the binary path properly.
**Prevention:** Always use `fork` and `execvp` (or equivalent APIs) with an `argv` array for invoking external programs to prevent shell evaluation. Validate URLs to reject control characters and leading hyphens (argument injection).
