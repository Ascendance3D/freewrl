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

#define ConsoleMessage(...) ((void)0)

#include "pluginUtils.inc"

static char test_dir[] = "/tmp/fw-c-tests-pluginutils.XXXXXX";
static int done_setup = 0;

static void setup(void) {
    if (!done_setup) {
        CHECK(mkdtemp(test_dir) != NULL);
        done_setup = 1;
    }
}

static void test_harmless_url(void) {
    setup();
    char touch_file[256];
    snprintf(touch_file, sizeof(touch_file), "%s/pwned", test_dir);

    char url[256];
    /* Even though this URL looks like it has shell syntax, execvp shouldn't parse it */
    snprintf(url, sizeof(url), "http://example.com; touch %s", touch_file);

    launch_browser("echo", url);

    /* Wait for child to exit */
    usleep(100000);

    struct stat st;
    CHECK(stat(touch_file, &st) != 0); /* File should NOT exist */
}

static void test_reject_hyphen(void) {
    launch_browser("echo", "-http://example.com");
}

static void test_reject_control_chars(void) {
    launch_browser("echo", "http://example.com\n");
    launch_browser("echo", "http://example.com\t");
}

static const ct_case cases[] = {
    { "harmless URL with spaces and shell metacharacters", test_harmless_url },
    { "reject hyphen in URL", test_reject_hyphen },
    { "reject control chars in URL", test_reject_control_chars },
};
const ct_suite ct_pluginutils_suite = { "pluginutils", cases, CT_COUNT(cases) };
