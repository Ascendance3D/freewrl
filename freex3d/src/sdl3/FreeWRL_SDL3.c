/* FreeWRL_SDL3.c: experimental SDL3 frontend scaffold (macOS only for now).

   Built only with -DFREEWRL_SDL3_FRONTEND=ON, as the freewrl_sdl3 program. The Cocoa
   FreeWRL.app stays the default frontend. SDL3 owns only this program's window and its
   OpenGL 4.1 core context; the FreeWRL OpenGL renderer draws into that context through the
   cdllFreeWRL frontend API, as FWGLView.m does in the Cocoa frontend.

     freewrl_sdl3 [freewrl options] <world>

   This scaffold forwards no keyboard, mouse or wheel input. It handles only quit, window
   close and window geometry events. Lines that start with "SDL3_" on stderr are for QA
   (tools/macos-ci/sdl3-scaffold.sh). */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <SDL3/SDL.h>

#include "libFreeWRL.h"
#include "../dllFreeWRL/cdllFreeWRL.h"

void fwg_register_consolemessage_callback(void (*callback)(char *));

#define FW_SDL3_WIDTH 672
#define FW_SDL3_HEIGHT 480

static void console_to_stderr(char *msg)
{
	fputs(msg, stderr);
}

/* Logical size in points, drawable size in pixels. They differ on a Retina display. */
struct geometry {
	int w, h, pw, ph;
	float density;
};

static void read_geometry(SDL_Window *window, struct geometry *g)
{
	if (!SDL_GetWindowSize(window, &g->w, &g->h))
		g->w = g->h = 0;
	if (!SDL_GetWindowSizeInPixels(window, &g->pw, &g->ph))
		g->pw = g->ph = 0;
	g->density = SDL_GetWindowPixelDensity(window);
	if (g->density <= 0.0f)
		g->density = 1.0f;
}

/* Sends a geometry change to FreeWRL: the density factor (HUD scale) and the drawable
   size in pixels, which is what the GL viewport uses. */
static void apply_geometry(void *fwctx, const struct geometry *now, struct geometry *sent)
{
	if (now->density != sent->density)
		dllFreeWRL_setDensityFactor(fwctx, now->density);
	if (now->pw != sent->pw || now->ph != sent->ph)
		dllFreeWRL_onResize(fwctx, now->pw, now->ph);
	if (memcmp(now, sent, sizeof *now)) {
		fprintf(stderr, "SDL3_GEOMETRY logical=%dx%d drawable=%dx%d density=%.2f\n",
			now->w, now->h, now->pw, now->ph, now->density);
		*sent = *now;
	}
}

static void log_gl_context(void)
{
	int major = 0, minor = 0, profile = 0, dbl = 0, alpha = 0, depth = 0, stencil = 0, interval = -99;
	SDL_GL_GetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, &major);
	SDL_GL_GetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, &minor);
	SDL_GL_GetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, &profile);
	SDL_GL_GetAttribute(SDL_GL_DOUBLEBUFFER, &dbl);
	SDL_GL_GetAttribute(SDL_GL_ALPHA_SIZE, &alpha);
	SDL_GL_GetAttribute(SDL_GL_DEPTH_SIZE, &depth);
	SDL_GL_GetAttribute(SDL_GL_STENCIL_SIZE, &stencil);
	if (!SDL_GL_GetSwapInterval(&interval))
		interval = -99;
	fprintf(stderr, "SDL3_GL_CONTEXT version=%d.%d profile=%s doublebuffer=%d alpha=%d depth=%d "
		"stencil=%d swap_interval=%d\n", major, minor,
		profile == SDL_GL_CONTEXT_PROFILE_CORE ? "core" : "other", dbl, alpha, depth, stencil, interval);
}

int main(int argc, char **argv)
{
	SDL_Window *window;
	SDL_GLContext context;
	void *fwctx;
	struct geometry now, sent;
	unsigned long hooks = 0, draws = 0, swaps = 0;
	Uint64 t0, t1;
	int close_sent = 0, geometry_dirty = 1;
	int version = SDL_GetVersion();

	fprintf(stderr, "SDL3_VERSION runtime=%d.%d.%d revision=%s\n", SDL_VERSIONNUM_MAJOR(version),
		SDL_VERSIONNUM_MINOR(version), SDL_VERSIONNUM_MICRO(version), SDL_GetRevision());

	if (!SDL_Init(SDL_INIT_VIDEO)) {
		fprintf(stderr, "freewrl_sdl3: SDL_Init(VIDEO) failed: %s\n", SDL_GetError());
		return 1;
	}

	/* The same context as FWGLView's basicPixelFormat: OpenGL 4.1 core, double buffered,
	   24-bit color, 8-bit alpha, 24-bit depth, 8-bit stencil, hardware accelerated. */
	SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 4);
	SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1);
	SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
	SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG);
	SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
	SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24);
	SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_ACCELERATED_VISUAL, 1);

	/* a normal titled window: native title bar with close, minimize and zoom controls */
	window = SDL_CreateWindow("FreeWRL \xE2\x80\x94 SDL3 Scaffold", FW_SDL3_WIDTH, FW_SDL3_HEIGHT,
		SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE | SDL_WINDOW_HIGH_PIXEL_DENSITY);
	if (!window) {
		fprintf(stderr, "freewrl_sdl3: SDL_CreateWindow failed: %s\n", SDL_GetError());
		SDL_Quit();
		return 1;
	}
	context = SDL_GL_CreateContext(window);
	if (!context) {
		fprintf(stderr, "freewrl_sdl3: no OpenGL 4.1 core context: %s\n", SDL_GetError());
		SDL_DestroyWindow(window);
		SDL_Quit();
		return 1;
	}
	if (!SDL_GL_MakeCurrent(window, context)) {
		fprintf(stderr, "freewrl_sdl3: SDL_GL_MakeCurrent failed: %s\n", SDL_GetError());
		SDL_GL_DestroyContext(context);
		SDL_DestroyWindow(window);
		SDL_Quit();
		return 1;
	}
	/* vertical sync paces the loop below, as NSOpenGLCPSwapInterval 1 does for Cocoa */
	if (!SDL_GL_SetSwapInterval(1))
		fprintf(stderr, "freewrl_sdl3: swap interval 1 rejected: %s\n", SDL_GetError());
	log_gl_context();
	fwl_log_gl_strings();

	/* One FreeWRL instance. This thread owns the display: it draws each frame with
	   dllFreeWRL_onDraw, and FreeWRL starts no display thread. dllFreeWRL_onInitArgv parses
	   the FreeWRL options and queues the world given on the command line. */
	fwctx = dllFreeWRL_dllFreeWRL();
	dllFreeWRL_onInitArgv(fwctx, argc, argv, 1);
	dllFreeWRL_setFontFolder(fwctx, FW_SDL3_FONT_DIR "/VeraMono.ttf");
	if (fwl_setCurrentHandle(fwctx, __FILE__, __LINE__))
		fwg_register_consolemessage_callback(console_to_stderr);
	fwl_clearCurrentHandle();

	memset(&sent, 0, sizeof sent);
	t0 = SDL_GetTicksNS();
	for (;;) {
		SDL_Event ev;
		while (SDL_PollEvent(&ev)) {
			switch (ev.type) {
			case SDL_EVENT_QUIT:
			case SDL_EVENT_WINDOW_CLOSE_REQUESTED:
				if (!close_sent) {
					/* With a frontend-owned display thread this only asks FreeWRL to
					   quit (it has no display thread to join). The loop keeps drawing
					   until dllFreeWRL_onDraw reports that the instance has shut down. */
					dllFreeWRL_onClose(fwctx);
					close_sent = 1;
				}
				break;
			case SDL_EVENT_WINDOW_RESIZED:
			case SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED:
			case SDL_EVENT_WINDOW_DISPLAY_SCALE_CHANGED:
				geometry_dirty = 1;
				break;
			default:
				break; /* input is not forwarded in this scaffold */
			}
		}
		if (geometry_dirty) {
			read_geometry(window, &now);
			apply_geometry(fwctx, &now, &sent);
			geometry_dirty = 0;
		}
		SDL_GL_MakeCurrent(window, context);
		fw_frontend_frame_hook();
		hooks++;
		draws++;
		if (!dllFreeWRL_onDraw(fwctx)) {
			/* FreeWRL has shut down and freed its instance: do not call it again */
			break;
		}
		SDL_GL_SwapWindow(window);
		swaps++;
	}
	t1 = SDL_GetTicksNS();
	fprintf(stderr, "SDL3_FRAMES hooks=%lu draws=%lu swaps=%lu seconds=%.2f fps=%.1f\n",
		hooks, draws, swaps, (double)(t1 - t0) / 1e9,
		t1 > t0 ? (double)swaps * 1e9 / (double)(t1 - t0) : 0.0);

	/* FreeWRL released its GL resources in its last dllFreeWRL_onDraw, with this context current */
	SDL_GL_DestroyContext(context);
	SDL_DestroyWindow(window);
	SDL_Quit();
	fprintf(stderr, "SDL3_EXIT clean\n");
	return 0;
}
