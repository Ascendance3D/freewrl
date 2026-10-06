//
//  AppController.m
//  FreeWRL
//
//  Created by Doug on 2018-05-30.
//  Copyright © 2018 freewrl.sf.net. All rights reserved.
//

#import "AppController.h"
#import "../../../freex3d/src/dllFreeWRL/cdllFreeWRL.h"

extern void* fwctx;

@implementation AppController
- (id) init
{
	self = [super init];
	if(self){
		// initialization code here
	}
	return self;
}
- (IBAction)OpenFile:(id)sender {
	NSOpenPanel* openDlg = [NSOpenPanel openPanel];
	
	[openDlg setCanChooseFiles:YES];
	
	[openDlg setAllowedFileTypes:@[@"wrl", @"x3d", @"x3dv"]];
	
	// Load the chosen world at once, through the same loader as argv and application:openURLs:.
	[openDlg beginWithCompletionHandler:^(NSInteger result) {
		if(result==NSModalResponseOK && fwctx) {
			dllFreeWRL_onLoad(fwctx,(char*)openDlg.URLs[0].fileSystemRepresentation);
		}
	}];

}
- (void) dealloc
{
	[super dealloc];
}
@end
