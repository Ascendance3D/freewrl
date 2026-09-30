/*
 * fw_temp_file_create and fw_temp_dir_create (with temp_template), extracted unchanged
 * from freex3d/src/lib/io_files.c by run-bounds.sh (tempfile.inc). The tests create files only inside a private
 * directory made by mkdtemp, and remove them.
 */
#include "test_support.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define ERROR_MSG(...) ((void)0)

#include "tempfile.inc"

static char base_dir[] = "/tmp/fw-c-tests-tempfile.XXXXXX";
static char other_dir[] = "/tmp/fw-c-tests-tempfile-env.XXXXXX";

static int count_files(const char *dir)
{
	int n = 0;
	struct dirent *e;
	DIR *d = opendir(dir);
	if (!d) return -1;
	while ((e = readdir(d)))
		if (strcmp(e->d_name, ".") && strcmp(e->d_name, "..")) n++;
	closedir(d);
	return n;
}

static void setup(void)
{
	static int done;
	if (!done) {
		CHECK(mkdtemp(base_dir) != NULL);
		CHECK(mkdtemp(other_dir) != NULL);
		done = 1;
	}
	unsetenv("TMPDIR");
}

static void creates_private_file(void)
{
	char *path = NULL;
	struct stat st;
	mode_t old = umask(0);   /* even with no umask the file is not group or world accessible */
	FILE *fp;
	setup();
	fp = fw_temp_file_create(base_dir, "freewrl_test_", &path);
	umask(old);
	CHECK(fp != NULL && path != NULL);
	if (!fp || !path) return;
	CHECK(!strncmp(path, base_dir, strlen(base_dir)));
	CHECK(strstr(path, "/freewrl_test_") != NULL);
	CHECK(strlen(path) == strlen(base_dir) + strlen("/freewrl_test_") + 6);
	CHECK(stat(path, &st) == 0 && S_ISREG(st.st_mode) && (st.st_mode & 0777) == 0600);
	CHECK(fputs("hello", fp) >= 0);
	CHECK(fclose(fp) == 0);
	CHECK(stat(path, &st) == 0 && st.st_size == 5);
	CHECK(unlink(path) == 0);
	free(path);
	CHECK(count_files(base_dir) == 0);
}

static void names_are_unique(void)
{
	char *a = NULL, *b = NULL;
	FILE *fa, *fb;
	setup();
	fa = fw_temp_file_create(base_dir, "u_", &a);
	fb = fw_temp_file_create(base_dir, "u_", &b);
	CHECK(fa && fb && a && b && strcmp(a, b));
	if (fa) fclose(fa);
	if (fb) fclose(fb);
	if (a) unlink(a);
	if (b) unlink(b);
	free(a); free(b);
	CHECK(count_files(base_dir) == 0);
}

static void missing_directory_uses_tmp(void)
{
	/* as tempnam did: a directory that does not exist is replaced by /tmp */
	char *path = NULL;
	char dir[256];
	FILE *fp;
	setup();
	snprintf(dir, sizeof dir, "%s/does-not-exist", base_dir);
	fp = fw_temp_file_create(dir, "fw-c-tests-missing_", &path);
	CHECK(fp && path && !strncmp(path, "/tmp/fw-c-tests-missing_", 24));
	if (fp) fclose(fp);
	if (path) unlink(path);
	free(path);
	CHECK(count_files(base_dir) == 0);
}

static void unwritable_directory_fails_cleanly(void)
{
	char *path = (char *)"unchanged";
	char dir[256];
	FILE *fp;
	setup();
	if (geteuid() == 0) return; /* root can write anywhere */
	snprintf(dir, sizeof dir, "%s/ro", base_dir);
	CHECK(mkdir(dir, 0500) == 0);
	fp = fw_temp_file_create(dir, "x_", &path);
	CHECK(fp == NULL);
	CHECK(path == NULL);
	CHECK(fw_temp_dir_create(dir, "x_") == NULL);
	CHECK(count_files(dir) == 0);
	CHECK(rmdir(dir) == 0);
}

static void creates_private_directory(void)
{
	struct stat st;
	char *d, *e;
	mode_t old = umask(0);
	setup();
	d = fw_temp_dir_create(base_dir, "fwx3z_");
	e = fw_temp_dir_create(base_dir, "fwx3z_");
	umask(old);
	CHECK(d && e && strcmp(d, e));
	if (d) {
		CHECK(!strncmp(d, base_dir, strlen(base_dir)) && strstr(d, "/fwx3z_"));
		CHECK(stat(d, &st) == 0 && S_ISDIR(st.st_mode) && (st.st_mode & 0777) == 0700);
		CHECK(rmdir(d) == 0);
	}
	if (e) CHECK(rmdir(e) == 0);
	free(d); free(e);
	CHECK(count_files(base_dir) == 0);
}

static void tmpdir_is_preferred(void)
{
	char *path = NULL;
	FILE *fp;
	setup();
	setenv("TMPDIR", other_dir, 1);
	fp = fw_temp_file_create(base_dir, "env_", &path);
	unsetenv("TMPDIR");
	CHECK(fp && path && !strncmp(path, other_dir, strlen(other_dir)));
	if (fp) fclose(fp);
	if (path) unlink(path);
	free(path);
	CHECK(count_files(other_dir) == 0);
}

static void empty_or_bad_tmpdir_is_ignored(void)
{
	const char *values[] = { "", "/nonexistent/fw-c-tests" };
	setup();
	for (int i = 0; i < CT_COUNT(values); i++) {
		char *path = NULL;
		FILE *fp;
		setenv("TMPDIR", values[i], 1);
		fp = fw_temp_file_create(base_dir, "env_", &path);
		unsetenv("TMPDIR");
		CHECK(fp && path && !strncmp(path, base_dir, strlen(base_dir)));
		if (fp) fclose(fp);
		if (path) unlink(path);
		free(path);
	}
	CHECK(count_files(base_dir) == 0);
}

static void trailing_slash_in_directory(void)
{
	char dir[256], *path = NULL;
	FILE *fp;
	setup();
	snprintf(dir, sizeof dir, "%s/", base_dir);
	fp = fw_temp_file_create(dir, "s_", &path);
	CHECK(fp && path && !strstr(path, "//"));
	if (fp) fclose(fp);
	if (path) unlink(path);
	free(path);
}

static void null_directory_uses_tmp(void)
{
	char *path = NULL;
	FILE *fp;
	setup();
	fp = fw_temp_file_create(NULL, "fw-c-tests-null-dir_", &path);
	CHECK(fp && path && !strncmp(path, "/tmp/fw-c-tests-null-dir_", 25));
	if (fp) fclose(fp);
	if (path) unlink(path);
	free(path);
}

static void cleanup_dirs(void)
{
	CHECK(rmdir(base_dir) == 0);
	CHECK(rmdir(other_dir) == 0);
}

static const ct_case cases[] = {
	{ "creates a 0600 file and returns its path", creates_private_file },
	{ "names are unique", names_are_unique },
	{ "missing directory uses /tmp", missing_directory_uses_tmp },
	{ "unwritable directory fails, creates nothing", unwritable_directory_fails_cleanly },
	{ "creates a 0700 directory", creates_private_directory },
	{ "TMPDIR is preferred", tmpdir_is_preferred },
	{ "empty or missing TMPDIR is ignored", empty_or_bad_tmpdir_is_ignored },
	{ "trailing slash in directory", trailing_slash_in_directory },
	{ "NULL directory uses /tmp", null_directory_uses_tmp },
	{ "test directories are empty", cleanup_dirs },
};
const ct_suite ct_tempfile_suite = { "temp-file", cases, CT_COUNT(cases) };
