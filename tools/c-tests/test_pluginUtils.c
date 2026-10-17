/*
 * split_browser_command and launch_browser, extracted unchanged from
 * freex3d/src/lib/plugin/pluginUtils.c by run-bounds.sh
 */
#include "test_support.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <fcntl.h>

static int console_message_calls = 0;
#define ConsoleMessage(...) do { console_message_calls++; } while (0)

#include "pluginUtils.inc"

static char test_dir[] = "/tmp/fw-c-tests-pluginutils.XXXXXX";
static int setup_state = 0; /* 0 = not tried, 1 = ready, -1 = failed */
static char browser_script[256];
static char out_file[256];
static char touch_file[256];

static void remove_files(void) {
    unlink(out_file);
    unlink(touch_file);
}

static void cleanup_test_dir(void) {
    if (setup_state == 1) {
        remove_files();
        unlink(browser_script);
        rmdir(test_dir);
    }
    setup_state = 0;
}

/* Creates the temp dir and a mock browser that records its arguments. */
static int setup(void) {
    if (setup_state != 0) return setup_state > 0;
    setup_state = -1;
    if (mkdtemp(test_dir) == NULL) {
        CHECK(0);
        return 0;
    }
    snprintf(browser_script, sizeof(browser_script), "%s/mock_browser.sh", test_dir);
    snprintf(out_file, sizeof(out_file), "%s/mock_browser.out", test_dir);
    snprintf(touch_file, sizeof(touch_file), "%s/pwned", test_dir);
    FILE *f = fopen(browser_script, "w");
    if (!f) {
        CHECK(0);
        rmdir(test_dir);
        return 0;
    }
    fprintf(f, "#!/bin/sh\n");
    fprintf(f, "echo \"$@\" > \"%s\"\n", out_file);
    fclose(f);
    if (chmod(browser_script, 0755) != 0) {
        CHECK(0);
        unlink(browser_script);
        rmdir(test_dir);
        return 0;
    }
    setup_state = 1;
    return 1;
}

/* Waits for the orphaned grandchild to write the mock browser's output (up to ~5 s). */
static int read_browser_output(char *buf, size_t size) {
    struct stat st;
    for (int i = 0; i < 500; i++) {
        if (stat(out_file, &st) == 0 && st.st_size > 0) break;
        usleep(10000);
    }
    FILE *f = fopen(out_file, "r");
    if (!f) return 0;
    char *got = fgets(buf, (int)size, f);
    fclose(f);
    return got != NULL;
}

static void test_harmless_url(void) {
    char url[512], browser_cmd[512], buf[1024], expected[1024];

    if (!setup()) return;
    remove_files();
    /* Even though this URL looks like it has shell syntax, execvp shouldn't parse it */
    snprintf(url, sizeof(url), "http://example.com; touch %s", touch_file);
    snprintf(browser_cmd, sizeof(browser_cmd), "%s --arg1 --arg2", browser_script);

    launch_browser(browser_cmd, url);

    CHECK(read_browser_output(buf, sizeof(buf)));
    snprintf(expected, sizeof(expected), "--arg1 --arg2 http://example.com; touch %s\n", touch_file);
    CHECK(strcmp(buf, expected) == 0);
    struct stat st;
    CHECK(stat(touch_file, &st) != 0); /* No shell injection */
}

static void test_quoted_browser_arguments(void) {
    char browser_cmd[512], buf[512];

    if (!setup()) return;
    remove_files();
    snprintf(browser_cmd, sizeof(browser_cmd), "'%s' \"--title=a b\" plain\\ arg", browser_script);

    launch_browser(browser_cmd, "http://example.com");

    CHECK(read_browser_output(buf, sizeof(buf)));
    CHECK(strcmp(buf, "--title=a b plain arg http://example.com\n") == 0);
}

static void test_invalid_browser_command(void) {
    int before = console_message_calls;
    launch_browser("", "http://example.com");
    launch_browser("   \t ", "http://example.com");
    launch_browser("firefox 'unterminated", "http://example.com");
    CHECK(console_message_calls == before + 3);
}

static void test_reject_hyphen(void) {
    struct stat st;

    if (!setup()) return;
    remove_files();
    console_message_calls = 0;
    launch_browser(browser_script, "-http://example.com");
    /* Rejection happens before any fork, so nothing can still be running. */
    CHECK(console_message_calls == 1);
    CHECK(stat(out_file, &st) != 0);
}

static void test_reject_control_chars(void) {
    struct stat st;

    if (!setup()) return;
    remove_files();
    console_message_calls = 0;
    launch_browser(browser_script, "http://example.com\n");
    CHECK(console_message_calls == 1);
    CHECK(stat(out_file, &st) != 0);
}

static void test_cleanup(void) {
    cleanup_test_dir();
    CHECK(access(test_dir, F_OK) != 0);
}

static const ct_case cases[] = {
    { "harmless URL with spaces and shell metacharacters", test_harmless_url },
    { "quoted BROWSER arguments are preserved", test_quoted_browser_arguments },
    { "invalid BROWSER command is refused", test_invalid_browser_command },
    { "reject hyphen in URL", test_reject_hyphen },
    { "reject control chars in URL", test_reject_control_chars },
    { "cleanup test dir", test_cleanup },
};
const ct_suite ct_pluginutils_suite = { "pluginutils", cases, CT_COUNT(cases) };
