//
//  JMDoolLoggerAdvancedPreferences.h
//  doolAdiumPlugin
//
//  Created by Tony Angerilli on 13/12/09.
//  Copyright 2009 Tony Angerilli. All rights reserved.
//

#import <Adium/AIAdvancedPreferencePane.h>

@interface JMDoolLoggerAdvancedPreferences : AIAdvancedPreferencePane {
	IBOutlet    NSButton			*checkbox_enableDoolLogging;
	//IBOutlet    NSView				*view;
	IBOutlet	NSTextField			*text_serverURL;
}

@end
