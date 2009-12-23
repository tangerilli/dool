//
//  JMDoolLoggerAdvancedPreferences.m
//  doolAdiumPlugin
//
//  Created by Tony Angerilli on 13/12/09.
//  Copyright 2009 Tony Angerilli. All rights reserved.
//

#import "AIDoolLoggerPlugin.h"
#import "JMDoolLoggerAdvancedPreferences.h"
#import <AIUtilities/AIDictionaryAdditions.h>
#import <Adium/AIListObject.h>
#import <Adium/AIPreferenceControllerProtocol.h>


@interface JMDoolLoggerAdvancedPreferences (PRIVATE)
- (void)preferencesChanged:(NSNotification *)notification;
@end

@implementation JMDoolLoggerAdvancedPreferences

- (NSString *)label{
	FILE *fp;
	fp=fopen("/tmp/test.txt", "a");
	fprintf(fp, "label...\n");
	fclose(fp);
    return @"DOOL Logging";
}

- (NSString *)nibName{
    return @"Dool_Logger_Prefs";
}

@protocol AIAdium, AIPreferenceController;

//Configure the preference view
- (void)viewDidLoad
{
	[[adium preferenceController] registerPreferenceObserver:self forGroup:PREF_GROUP_DOOL_LOGGING];
}

- (void)viewWillClose
{
	[[adium preferenceController] unregisterPreferenceObserver:self];
}

//Reflect new preferences in view
- (void)preferencesChangedForGroup:(NSString *)group key:(NSString *)key
							object:(AIListObject *)object preferenceDict:(NSDictionary *)prefDict firstTime:(BOOL)firstTime
{
	id				tmp;
	
	[checkbox_enableDoolLogging setState:[[prefDict objectForKey:KEY_DOOL_LOGGER_ENABLE] boolValue]];
	
	//This ugliness is because setStringValue doesn't like being passed nil
	[text_serverURL setStringValue:(tmp = [prefDict objectForKey:KEY_SERVER_URL]) ? tmp : @""];
}

//Save changed preference
- (IBAction)changePreference:(id)sender
{
	FILE *fp;
	fp=fopen("/tmp/test.txt", "a");
	fprintf(fp, "saving preferences...\n");
	fclose(fp);
    if (sender == checkbox_enableDoolLogging) {
        [[adium preferenceController] setPreference:[NSNumber numberWithBool:[sender state]]
                                             forKey:KEY_DOOL_LOGGER_ENABLE
                                              group:PREF_GROUP_DOOL_LOGGING];
    } 
	else if (sender == text_serverURL) {
		[[adium preferenceController] setPreference:[sender stringValue]
                                             forKey:KEY_SERVER_URL
                                              group:PREF_GROUP_DOOL_LOGGING];
	}// else if (sender == text_URL) {
//		[[adium preferenceController] setPreference:[sender stringValue]
//                                             forKey:KEY_SQL_URL
//                                              group:PREF_GROUP_SQL_LOGGING];
//	} else if (sender == text_Port) {
//		[[adium preferenceController] setPreference:[sender stringValue]
//                                             forKey:KEY_SQL_PORT
//                                              group:PREF_GROUP_SQL_LOGGING];
//	} else if (sender == text_database) {
//		[[adium preferenceController] setPreference:[sender stringValue]
//                                             forKey:KEY_SQL_DATABASE
//                                              group:PREF_GROUP_SQL_LOGGING];
//	} else if (sender == text_Password) {
//		[[adium preferenceController] setPreference:[NSNumber numberWithBool:[sender state]]
//                                             forKey:KEY_SQL_PASSWORD
//                                              group:PREF_GROUP_SQL_LOGGING];
//	}
}

@end
