//
//  main.m
//  FreeWRL
//
//  Created by John Stewart on 11-07-20.
//  Copyright 2011 CRC Canada. All rights reserved.
//

#import <Cocoa/Cocoa.h>

int main(int argc, char *argv[])
{
    // No window state restoration: FreeWRL opens the world it is given. Without this AppKit keeps
    // Saved Application State, and a launch after a killed FreeWRL logs [StateRestoration] errors
    // (restoreWindowWithIdentifier ... className=(null), _NSPersistentUIDeleteItemAtFileURL).
    @autoreleasepool {
        [[NSUserDefaults standardUserDefaults] registerDefaults:@{
            @"ApplePersistenceIgnoreState": @YES,
            @"NSQuitAlwaysKeepsWindows": @NO,
        }];
    }
    return NSApplicationMain(argc, (const char **)argv);
}
