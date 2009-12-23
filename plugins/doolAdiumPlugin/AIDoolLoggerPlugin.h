//
//  AIDoolLoggerPlugin.h
//  doolAdiumPlugin
//
//  Created by Tony Angerilli on 13/12/09.
//  Copyright 2009 Tony Angerilli. All rights reserved.
//

#import <Adium/AIPlugin.h>

#define KEY_DOOL_LOGGER_ENABLE		@"Enable dool Logging"
#define PREF_GROUP_DOOL_LOGGING		@"DoolLogging"
#define DOOL_LOGGING_DEFAULT_PREFS  @"DoolLogging"
#define KEY_SERVER_URL				@"URL"
#define CLIENT_TYPE					@"adium";

@class JMDoolLoggerAdvancedPreferences;

@interface AIDoolLoggerPlugin : AIPlugin <AIPluginInfo> {
	JMDoolLoggerAdvancedPreferences  *advancedPreferences;
	NSString *serverURL;
	
	bool		observingContent;
}

@end
