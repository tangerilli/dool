//
//  AIDoolLoggerPlugin.m
//  doolAdiumPlugin
//
//  Created by Tony Angerilli on 13/12/09.
//
//  Based off of the Adium AISQLLoggerPlugin
//

#import "AIDoolLoggerPlugin.h"
#import "JMDoolLoggerAdvancedPreferences.h"
#import <AIUtilities/AIDictionaryAdditions.h>
#import <Adium/AIPreferenceControllerProtocol.h>
#import <Adium/AIChat.h>
#import <Adium/AIContentControllerProtocol.h>
#import <Adium/AIContentNotification.h>
#import <AIUtilities/AIAttributedStringAdditions.h>
#import <Adium/AIService.h>

#import "ASIFormDataRequest.h"

@interface AIDoolLoggerPlugin (PRIVATE)
- (void)postMessage:(NSAttributedString *)message
			   dest:(NSString *)destUID
			 source:(NSString *)sourceUID
			service:(NSString *)service
			   date:(NSDate *)date
			account:(AIAccount *)account
		 srcDisplay:(NSString *)srcDisplay;
- (void)preferencesChanged:(NSNotification *)notification;
@end

@implementation AIDoolLoggerPlugin

- (void)installPlugin
{		
	[[adium preferenceController] registerDefaults:[NSDictionary dictionaryNamed:DOOL_LOGGING_DEFAULT_PREFS
													forClass:[self class]]
													forGroup:PREF_GROUP_DOOL_LOGGING];
    advancedPreferences = [[JMDoolLoggerAdvancedPreferences preferencePane] retain];
	
	[[adium preferenceController] registerPreferenceObserver:self forGroup:PREF_GROUP_DOOL_LOGGING];
}

- (void)uninstallPlugin
{
	[[adium preferenceController] unregisterPreferenceObserver:self];
}

- (void)preferencesChangedForGroup:(NSString *)group key:(NSString *)key
							object:(AIListObject *)object preferenceDict:(NSDictionary *)prefDict firstTime:(BOOL)firstTime
{
	bool			newLogValue;
	
	newLogValue = [[prefDict objectForKey:KEY_DOOL_LOGGER_ENABLE] boolValue];
	serverURL = [prefDict objectForKey:KEY_SERVER_URL];
	
	if (newLogValue != observingContent) {
		observingContent = newLogValue;
		
		if (!observingContent) { //Stop Logging
			[[adium notificationCenter] removeObserver:self name:Content_ContentObjectAdded object:nil];
			
		} else { //Start Logging
			[[adium notificationCenter] addObserver:self selector:@selector(adiumSentOrReceivedContent:) name:Content_ContentObjectAdded object:nil];
		}
	}
}

//Content was sent or recieved
- (void)adiumSentOrReceivedContent:(NSNotification *)notification
{
    AIContentMessage 	*content = [[notification userInfo] objectForKey:@"AIContentObject"];
    //Message Content
    if (([[content type] isEqualToString:CONTENT_MESSAGE_TYPE] || 
		 [[content type] isEqualToString:CONTENT_NOTIFICATION_TYPE]) && [content postProcessContent]) {
        AIChat		*chat = [notification object];
        AIListObject	*source = [content source];
        AIListObject	*destination = [content destination];
        AIAccount	*account = [chat account];
        NSString	*srcDisplay = nil;
        NSString	*destDisplay = nil;
        NSString	*destUID = nil;
        NSString	*srcUID = nil;
        NSString	*destSrv = nil;
        NSString	*srcSrv = nil;
		
        if ([[account UID] isEqual:[source UID]]) {
            destUID  = [chat name];
            if (!destUID) {
                destUID = [[chat listObject] UID];
                destDisplay = [[chat listObject] displayName];
            }
            else {
                destDisplay = [chat displayName];;
            }
            destSrv = [[[chat account] service] serviceID];
            srcDisplay = [source displayName];
            srcUID = [source UID];
            srcSrv = [[source service] serviceID];
        } else {
            destUID = [chat name];
            if (!destUID) {
                srcDisplay = [[chat listObject] displayName];
                srcUID = [[chat listObject] UID];
                destUID = [destination UID];
                destDisplay = [destination displayName];
            }
            else {
                srcUID = [source UID];
                srcDisplay = srcUID;
                destDisplay = [chat displayName];
            }
            srcSrv = [[[chat account] service] serviceID];
            destSrv = srcSrv;
        }
		
        if (account && source) {
            //Log the message
			NSAttributedString *message = [[content message] attributedStringByConvertingAttachmentsToStrings];
			NSLog(@"Source service");
			NSLog(srcSrv);
			[self postMessage:message
						dest:destUID
					   source:srcUID
					  service:srcSrv
						 date:[content date]
					  account:account
				   srcDisplay:srcDisplay];
        }
    }
}


-(void)postMessage:(NSAttributedString *)message
			  dest:(NSString *)destUID
			source:(NSString *)sourceUID
		   service:(NSString *)service
			  date:(NSDate *)date
		   account:(AIAccount *)account
		srcDisplay:(NSString *)srcDisplay

{	
	NSString *postURL;
	NSString *hostname;
	NSString *timestamp;
	
	timestamp = [date description];
	hostname = [[[[NSHost currentHost] name] componentsSeparatedByString: @"."] objectAtIndex:0];
	NSLog(serverURL);
	NSLog(service);
	postURL = [NSString stringWithFormat:@"%@messages/%@/%@/add/", serverURL, service, [account UID]];
	
	NSLog(@"Posting to: ");
	NSLog(postURL);
	
	NSURL *url = [NSURL URLWithString:postURL];
	ASIFormDataRequest *request = [ASIFormDataRequest requestWithURL:url];
	[request setPostValue:destUID forKey:@"receiver_account"];
	[request setPostValue:sourceUID forKey:@"sender_account"];
	[request setPostValue:[account UID] forKey:@"owner_account"];
	[request setPostValue:srcDisplay forKey:@"alias"];
	[request setPostValue:timestamp forKey:@"timestamp"];
	[request setPostValue:[message string] forKey:@"message_text"];
	[request setPostValue:@"adium" forKey:@"client_type"];
	[request setPostValue:hostname forKey:@"host"];
	
	[request setDelegate:self];
	[request startAsynchronous];
}

- (void)requestFinished:(ASIHTTPRequest *)request
{
	NSString *responseString = [request responseString];
	
	NSLog(@"Got HTTP response");
	NSLog(responseString);
}

- (void)requestFailed:(ASIHTTPRequest *)request
{
	NSError *error = [request error];
	NSLog(@"HTTP request error");
	NSLog([error localizedDescription]);
}

- (NSString *)pluginAuthor {
    return @"Tony Angerilli";
}

- (NSString *)pluginDescription {
    return @"This plugin implements chat logging to a web service.";
}

- (NSString *)pluginVersion {
    return @"1.0";
}

- (NSString *)pluginURL {
    return @"http://projects.angerilli.ca/dool";
}

@end
