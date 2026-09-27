//
//  FreeWRLAppDelegate.m
//  FreeWRL
//
//  Created by John Stewart on 11-07-20.
//  Copyright 2011 CRC Canada. All rights reserved.
//

#import "FreeWRLAppDelegate.h"
#import "../../../freex3d/src/dllFreeWRL/cdllFreeWRL.h"

// Created lazily by FWGLView when the GL context comes up; NULL until then.
extern void *fwctx;

static NSString * OperationsChangedContext = @"OperationsChangedContext";
NSOperationQueue * _queue = nil;
bool *opFlagPtr;
static bool appRunningNow = false;


@implementation FreeWRLAppDelegate
+(bool)applicationHasLaunched
{
    return appRunningNow;
}


- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    //NSLog (@"Delegate: applicationDidFinishLaunching queue %p",_queue);

        _queue = [[NSOperationQueue alloc] init];
    // Set to 1 to serialize operations. Comment out for parallel operations.
    // [_queue setMaxConcurrentOperationCount:1];
    
    
    [_queue addObserver:self
             forKeyPath:@"operations"
                options:0
                context:&OperationsChangedContext];
    appRunningNow = true;
    
}

- (void)dealloc
{
    //NSLog (@"Delegate: dealloc");
    [_queue removeObserver:self forKeyPath:@"operations"];
    [_queue release];
    [super dealloc];
}



- (void)observeValueForKeyPath:(NSString *)keyPath
                      ofObject:(id)object
                        change:(NSDictionary *)change
                       context:(void *)context
{
    //NSLog (@"Delegate: observeValueForKeyPath");
    if (context == &OperationsChangedContext)
    {
        //NSLog(@"Delegate: Queue size: %u", [[_queue operations] count]);
    }
    else
    {
        //NSLog (@"Delegate: observeValueForKeyPath - having to super");
        [super observeValueForKeyPath:keyPath
                             ofObject:object
                               change:change
                              context:context];
    }
}


- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)theApplication
{
	return YES;
}

// A world opened from Finder (double-click) or `open -a FreeWRL world.wrl` is delivered here by
// LaunchServices as an odoc/open Apple event, NOT on argv. Without this handler AppKit hands the
// document to the default NSDocumentController, which has no document class for our declared types
// and puts up "FreeWRL cannot open files in the ... file format". Feed it to the same loader the
// Load button and the argv startup path use (dllFreeWRL_onLoad), so routed documents actually open.
- (void)application:(NSApplication *)application openURLs:(NSArray<NSURL *> *)urls
{
	for (NSURL *url in urls) {
		if (!url.isFileURL) continue;
		NSString *path = [url.path copy];
		// fwctx is created by the GL view a moment after launch. On a cold launch-to-open the event
		// can arrive first, so wait (off the main thread) for the context, then load exactly once.
		// dllFreeWRL_onLoad is already called from non-main threads elsewhere (the initializer
		// thread and here), so this is consistent with existing use.
		dispatch_async(dispatch_get_global_queue(QOS_CLASS_DEFAULT, 0), ^{
			for (int i = 0; i < 1000 && !fwctx; i++) usleep(10000); // up to ~10 s for GL init
			if (fwctx) dllFreeWRL_onLoad(fwctx, (char *)[path UTF8String]);
			[path release];
		});
	}
}

@end
