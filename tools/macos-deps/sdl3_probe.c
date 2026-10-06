/* Test-only probe for the SDL3 that tools/macos-deps/build.sh pins (built by
 * freex3d/CMakeLists.txt with -DFREEWRL_SDL3_PROBE=ON, run by ctest). It is
 * not part of FreeWRL: it checks that the headers and the linked library are
 * the pinned release and commit. It calls no SDL initialisation and creates
 * no SDL object. */
#include <stdio.h>
#include <string.h>
#include <SDL3/SDL_revision.h>
#include <SDL3/SDL_version.h>

#if SDL_MAJOR_VERSION != FW_SDL3_MAJOR || SDL_MINOR_VERSION != FW_SDL3_MINOR || SDL_MICRO_VERSION != FW_SDL3_MICRO
#error "SDL3 headers are not the release pinned in tools/macos-deps/build.sh"
#endif

int main(void)
{
	char tag[64];
	const char *rev = SDL_GetRevision();
	const char *at;
	size_t n;
	int linked = SDL_GetVersion();

	printf("SDL3 headers %d.%d.%d (%s)\n", SDL_MAJOR_VERSION, SDL_MINOR_VERSION,
		SDL_MICRO_VERSION, SDL_REVISION);
	printf("SDL3 library %d.%d.%d (%s)\n", SDL_VERSIONNUM_MAJOR(linked),
		SDL_VERSIONNUM_MINOR(linked), SDL_VERSIONNUM_MICRO(linked), rev);
	if (linked != SDL_VERSION) {
		fprintf(stderr, "FAIL: linked SDL3 is not the header version\n");
		return 1;
	}
	/* "SDL-release-3.4.18-0-g829a65d76": the release tag, 0 commits past it */
	snprintf(tag, sizeof tag, "release-%d.%d.%d-0-g", FW_SDL3_MAJOR, FW_SDL3_MINOR, FW_SDL3_MICRO);
	at = strstr(rev, tag);
	n = at ? strspn(at + strlen(tag), "0123456789abcdef") : 0;
	if (n < 7 || strncmp(at + strlen(tag), FW_SDL3_COMMIT, n) != 0) {
		fprintf(stderr, "FAIL: revision is not %s%s\n", tag, FW_SDL3_COMMIT);
		return 1;
	}
	printf("PASS: SDL3 %d.%d.%d at commit %s\n", FW_SDL3_MAJOR, FW_SDL3_MINOR, FW_SDL3_MICRO,
		FW_SDL3_COMMIT);
	return 0;
}
