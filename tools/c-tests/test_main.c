/*
 * Host-only container tests: runs every suite and prints one PASS/FAIL line per
 * test and a summary per suite. Exit status is nonzero if any check failed.
 * Built and run by run-containers.sh; never starts FreeWRL.
 */
#include "test_support.h"

int ct_check_failures = 0;

static int run_suite(const ct_suite *s, int *total, int *failed)
{
	int suite_failed = 0;
	for (int i = 0; i < s->count; i++) {
		int before = ct_check_failures;
		s->cases[i].fn();
		int ok = ct_check_failures == before;
		printf("%s %s: %s\n", ok ? "PASS" : "FAIL", s->name, s->cases[i].name);
		if (!ok) suite_failed++;
	}
	printf("== %s: %d tests, %d passed, %d failed\n", s->name, s->count,
	       s->count - suite_failed, suite_failed);
	*total += s->count;
	*failed += suite_failed;
	return suite_failed;
}

int main(void)
{
	const ct_suite *suites[] = {
		&ct_vector_suite, &ct_list_suite, &ct_queue_suite, &ct_payload_suite, &ct_cdl_suite,
	};
	int total = 0, failed = 0;

	setvbuf(stdout, NULL, _IOLBF, 0);
	for (int i = 0; i < CT_COUNT(suites); i++)
		run_suite(suites[i], &total, &failed);
	printf("== TOTAL: %d tests, %d passed, %d failed\n", total, total - failed, failed);
	printf(failed ? "CONTAINER TESTS FAILED\n" : "CONTAINER TESTS PASS\n");
	return failed ? 1 : 0;
}
