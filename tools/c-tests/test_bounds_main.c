/*
 * Host-only bounds tests: runs the suites built by run-bounds.sh and prints one
 * PASS/FAIL line per test. Exit status is nonzero if any check failed.
 *
 *   test_bounds                 run every suite
 *   test_bounds SUITE           run one suite
 *   test_bounds SUITE INDEX     run one test of a suite (0-based)
 */
#include "test_support.h"
#include <stdlib.h>
#include <string.h>

int ct_check_failures = 0;

int main(int argc, char **argv)
{
	const ct_suite *suites[] = {
		&ct_hanim_suite, &ct_texture_suite, &ct_texheader_suite, &ct_shader_suite, &ct_eai_suite,
		&ct_tempfile_suite, &ct_pickray_suite, &ct_sensors_suite, &ct_parse_error_suite, &ct_bvh_suite,
	};
	int total = 0, failed = 0, ran = 0;

	setvbuf(stdout, NULL, _IOLBF, 0);
	for (int s = 0; s < CT_COUNT(suites); s++) {
		const ct_suite *suite = suites[s];
		int suite_failed = 0, suite_ran = 0;
		if (argc > 1 && strcmp(argv[1], suite->name))
			continue;
		ran = 1;
		for (int i = 0; i < suite->count; i++) {
			int before = ct_check_failures, ok;
			if (argc > 2 && i != atoi(argv[2]))
				continue;
			suite->cases[i].fn();
			ok = ct_check_failures == before;
			printf("%s %s: %s\n", ok ? "PASS" : "FAIL", suite->name, suite->cases[i].name);
			suite_ran++;
			if (!ok) suite_failed++;
		}
		printf("== %s: %d tests, %d passed, %d failed\n", suite->name, suite_ran,
		       suite_ran - suite_failed, suite_failed);
		total += suite_ran;
		failed += suite_failed;
	}
	if (!ran) {
		printf("no suite named %s\n", argv[1]);
		return 2;
	}
	printf("== TOTAL: %d tests, %d passed, %d failed\n", total, total - failed, failed);
	printf(failed ? "BOUNDS TESTS FAILED\n" : "BOUNDS TESTS PASS\n");
	return failed ? 1 : 0;
}
