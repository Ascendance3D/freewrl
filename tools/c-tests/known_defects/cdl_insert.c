/*
 * Known-defect reproducer, NOT part of the routine run (run-containers.sh --known-defects).
 *
 * cdl_insert (freex3d/src/lib/list.c) into a non-empty circular list sets
 * point->next = item instead of linking item->next = point and point->prev->next = item.
 * The item before `point` keeps its next pointer, `point` loses its original successor,
 * and the new item still points at itself, so a forward walk from the head never returns
 * to it (cdl_count and cdl_foreach would loop forever). cd_list_t has no callers in the
 * engine today. This program asserts the intended behavior; fixing it is a separate change.
 *
 * Exit status: 0 = intended behavior (defect gone, retire this reproducer),
 * KNOWN_DEFECT_EXIT (42) = defect reproduced normally. Anything else (sanitizer report,
 * crash, signal) is an unexpected failure, and run-containers.sh treats it as one.
 */
#include <stdio.h>
#include <stdlib.h>

#include <config.h>
#include <system.h>
#include <display.h>
#include <internal.h>

#include <list.h>

#define KNOWN_DEFECT_EXIT 42

static int V[4] = { 0, 1, 2, 3 };

/* bounded forward walk: 1 if the ring is exactly V[idx[0..n-1]] with consistent links */
static int ring_is(cd_list_t *head, const int *idx, int n)
{
	cd_list_t *l = head;
	for (int i = 0; i < n; i++) {
		if (!l || cdl_elem(l) != &V[idx[i]]) return 0;
		if (cdl_prev(cdl_next(l)) != l || cdl_next(cdl_prev(l)) != l) return 0;
		l = cdl_next(l);
	}
	return l == head;
}

int main(void)
{
	int failures = 0;

	/* insert V[3] before the middle item of V[0], V[1], V[2] */
	cd_list_t *nodes[4];
	cd_list_t *head = NULL;
	for (int i = 0; i < 3; i++)
		head = cdl_append(head, nodes[i] = cdl_new(&V[i]));
	nodes[3] = cdl_new(&V[3]);
	head = cdl_insert(head, nodes[1], nodes[3]);
	static const int want_mid[] = { 0, 3, 1, 2 };
	int ok = ring_is(head, want_mid, 4);
	printf("%s cdl_insert before a middle item gives 0,3,1,2\n", ok ? "PASS" : "FAIL");
	if (!ok) failures++;
	for (int i = 0; i < 4; i++) free(nodes[i]); /* links may be corrupt: free directly */

	/* insert V[1] before the head of a one-item list */
	cd_list_t *a = cdl_new(&V[0]), *b = cdl_new(&V[1]);
	head = cdl_insert(a, a, b);
	static const int want_head[] = { 1, 0 };
	ok = head == b && ring_is(head, want_head, 2);
	printf("%s cdl_insert before the head gives 1,0 with the new item as head\n", ok ? "PASS" : "FAIL");
	if (!ok) failures++;
	free(a);
	free(b);

	printf(failures ? "KNOWN DEFECT PRESENT: cdl_insert (%d)\n" : "cdl_insert behaves; retire this reproducer\n",
	       failures);
	return failures ? KNOWN_DEFECT_EXIT : 0;
}
