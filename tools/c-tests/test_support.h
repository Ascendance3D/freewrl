/*
 * Minimal host-only test support for tools/c-tests (plain C17, no framework).
 * A test is a void function; CHECK records a failure and keeps going.
 */
#ifndef FW_CTEST_SUPPORT_H
#define FW_CTEST_SUPPORT_H

#include <stdio.h>

typedef struct {
	const char *name;
	void (*fn)(void);
} ct_case;

typedef struct {
	const char *name;
	const ct_case *cases;
	int count;
} ct_suite;

extern int ct_check_failures;

#define CHECK(cond) do { if (!(cond)) { ct_check_failures++; \
	printf("    check failed: %s (%s:%d)\n", #cond, __FILE__, __LINE__); } } while (0)

#define CT_COUNT(a) ((int)(sizeof(a) / sizeof((a)[0])))

extern const ct_suite ct_vector_suite;
extern const ct_suite ct_list_suite;
extern const ct_suite ct_queue_suite;
extern const ct_suite ct_payload_suite;
extern const ct_suite ct_cdl_suite;

/* run-bounds.sh */
extern const ct_suite ct_hanim_suite;
extern const ct_suite ct_texture_suite;
extern const ct_suite ct_shader_suite;
extern const ct_suite ct_eai_suite;
extern const ct_suite ct_tempfile_suite;
extern const ct_suite ct_pickray_suite;
extern const ct_suite ct_sensors_suite;
extern const ct_suite ct_parse_error_suite;

#endif
