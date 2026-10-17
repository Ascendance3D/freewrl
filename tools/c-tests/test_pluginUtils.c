/*
 * launch_browser, extracted unchanged from
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
static int done_setup = 0;
static char browser_script[256];

static void setup(void) {
    if (!done_setup) {
        CHECK(mkdtemp(test_dir) != NULL);
        done_setup = 1;

        snprintf(browser_script, sizeof(browser_script), "%s/mock_browser.sh", test_dir);
        FILE *f = fopen(browser_script, "w");
        if (f) {
            /* This script writes its arguments to mock_browser.out */
            fprintf(f, "#!/bin/sh\n");
            fprintf(f, "out=\"%s/mock_browser.out\"\n", test_dir);
            fprintf(f, "echo \"$@\" > \"$out\"\n");
            fclose(f);
            chmod(browser_script, 0755);
        }
    }
}

static void test_harmless_url(void) {
    setup();
    char touch_file[256];
    char out_file[256];
    snprintf(touch_file, sizeof(touch_file), "%s/pwned", test_dir);
    snprintf(out_file, sizeof(out_file), "%s/mock_browser.out", test_dir);
    unlink(out_file);
    unlink(touch_file);

    char url[256];
    /* Even though this URL looks like it has shell syntax, execvp shouldn't parse it */
    snprintf(url, sizeof(url), "http://example.com; touch %s", touch_file);

    char browser_cmd[512];
    snprintf(browser_cmd, sizeof(browser_cmd), "%s --arg1 --arg2", browser_script);

    launch_browser(browser_cmd, url);

    /* Wait for child to exit */
    usleep(100000);

    struct stat st;
    CHECK(stat(touch_file, &st) != 0); /* File should NOT exist (no shell injection) */
    CHECK(stat(out_file, &st) == 0); /* Browser script should have run */

    FILE *f = fopen(out_file, "r");
    if (f) {
        char buf[512];
        if (fgets(buf, sizeof(buf), f)) {
            /* Should match exactly the arguments passed */
            char expected[512];
            snprintf(expected, sizeof(expected), "--arg1 --arg2 http://example.com; touch %s\n", touch_file);
            CHECK(strcmp(buf, expected) == 0);
        }
        fclose(f);
    }
}

static void test_reject_hyphen(void) {
    console_message_calls = 0;
    setup();
    char out_file[256];
    snprintf(out_file, sizeof(out_file), "%s/mock_browser.out", test_dir);
    unlink(out_file);

    launch_browser(browser_script, "-http://example.com");

    CHECK(console_message_calls > 0);
    usleep(100000);
    struct stat st;
    CHECK(stat(out_file, &st) != 0); /* Browser should NOT have run */
}

static void test_reject_control_chars(void) {
    console_message_calls = 0;
    setup();
    char out_file[256];
    snprintf(out_file, sizeof(out_file), "%s/mock_browser.out", test_dir);
    unlink(out_file);

    launch_browser(browser_script, "http://example.com\n");

    CHECK(console_message_calls > 0);
    usleep(100000);
    struct stat st;
    CHECK(stat(out_file, &st) != 0); /* Browser should NOT have run */
}

static void cleanup_test_dir(void) {
    if (done_setup) {
        char path[256];
        snprintf(path, sizeof(path), "%s/mock_browser.sh", test_dir);
        unlink(path);
        snprintf(path, sizeof(path), "%s/mock_browser.out", test_dir);
        unlink(path);
        snprintf(path, sizeof(path), "%s/pwned", test_dir);
        unlink(path);
        rmdir(test_dir);
        done_setup = 0;
    }
}

static const ct_case cases[] = {
    { "harmless URL with spaces and shell metacharacters", test_harmless_url },
    { "reject hyphen in URL", test_reject_hyphen },
    { "reject control chars in URL", test_reject_control_chars },
    { "cleanup test dir", cleanup_test_dir },
};
const ct_suite ct_pluginutils_suite = { "pluginutils", cases, CT_COUNT(cases) };
