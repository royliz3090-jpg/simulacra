package game27;

import com.badlogic.gdx.graphics.Pixmap;
import com.badlogic.gdx.graphics.PixmapIO;
import com.google.gson.Gson;
import java.util.Locale;
import sengine.File;
import sengine.graphics2d.texturefile.FIFormat;
import sengine.graphics2d.texturefile.TextureFile;
import sengine.utils.LiveEditor;
import sengine.utils.NetRequest;
import sengine.utils.SheetsParser;

public class Globals {
   public static String version = "1.0.53";
   public static float MIN_LENGTH = 1.7777778F;
   public static float LENGTH = 2.0555556F;
   public static int topSafeAreaInset = 0;
   public static int bottomSafeAreaInset = 0;
   public static final String MAIL_BLOCK_TOKEN = "#block#";
   public static final String MAIL_ACTION_PREFIX = "action://";
   public static final String MAIL_GRAPHIC_PREFIX = "graphic://";
   public static final String MAIL_ALIGN_CENTER_PREFIX = "align://center/";
   public static final String MAIL_ALIGN_RIGHT_PREFIX = "align://right/";
   public static final String PHOTOROLL_PREFIX = "photoroll://";
   public static final String SECTION_PREFIX = "chats://section/";
   public static final String GROUP_ADD_PREFIX = "groupadd/";
   public static final String GROUP_REMOVE_PREFIX = "groupremove/";
   public static final String BROWSER_PREFIX = "browser://";
   public static final String VOICE_PREFIX = "vo://";
   public static final String ATTACHMENT_TITLE_TOKEN = "=";
   public static final String ATTACHMENT_WILDCARD = "photoroll://?";
   public static final String KEYBOARD_WILDCARD = "keyboard://";
   public static final String KEyBOARD_ALPHANUMERIC_WILDCARD = "keyboard://alphanumeric";
   public static final String KEYBOARD_NUMERIC_WILDCARD = "keyboard://numeric";
   public static final String CORRUPTED_PREFIX = "corrupted://";
   public static final String ORIGIN_USER = "user";
   public static final String ORIGIN_SENDER = "sender";
   public static final String TIME_AUTO = "auto";
   public static final String STATE_PREFIX = "#state:";
   public static final String STATE_SUFFIX = "#";
   public static final String FRIENDS_STATE_PREFIX = "friends.";
   public static final String WEBPAGE_FS_PREFIX = "content/webpages/";
   public static final String WEBLAYOUTS_FS_PREFIX = "content/weblayouts/";
   public static final String SUBTITLE_FS_PREFIX = "content/subtitles/";
   public static String googleConfigID;
   public static final String CONTENT_PREFIX_EN_US = "en-us://";
   public static final String CONTENT_PREFIX_ZH_CN = "zh-cn://";
   public static final String CONTENT_PREFIX_ES_LATAM = "es-latam://";
   public static String contentPrefix = "en-us://";
   public static String SAVE_FILENAME_EN_US = "save20170902.fs";
   public static String SAVE_FILENAME_ZH_CN = "save20170902zhcn.fs";
   public static String SAVE_FILENAME_ES_LATAM = "save20170902eslatam.fs";
   public static Locale timeLocale = Locale.US;
   public static String[] timeLocaleCustomAMPM = new String[]{"am", "pm"};
   public static float dialogueTreeMaxCharsPerWord;
   public static boolean r_highQuality = true;
   public static boolean isWindowed = false;
   public static String helpTwitterURL = "https://twitter.com/playsimulacra";
   public static String helpMailURL = "https://kaigangames.com/contact/";
   public static String helpFacebookURL = "https://www.facebook.com/playsimulacra/";
   public static String helpDiscordURL = "https://discordapp.com/invite/playsimulacra";
   public static Grid grid;
   public static float consoleChars = 18.0F;
   public static float maxTouchMoveDistance = 0.05F;
   public static float minTouchMoveDistance = 0.01F;
   public static float minWordDragDistance = 0.06F;
   public static float maxWordSnapDistance = 0.2F;
   public static float loadingFrameRate = 0.1F;
   public static float surfaceSnapDistance = 0.05F;
   public static int layoutSectionSize = 192;
   public static int layoutContentSectionSize = 16;
   public static float s_mediaSeekResolution = 1.0F;
   public static float s_mediaMinSeekDiff = 0.5F;
   public static float doubleClickTime = 0.5F;
   public static float singleClickTime = 0.2F;
   public static float tFriendsTriggerInterval = 5.0F;
   public static float tCorruptedTextInterval = 0.08F;
   public static int corruptedMessageDuplicates = 10;
   public static int corruptedMessageWordMaxLength = 10;
   public static boolean compileVoiceProfiles = false;
   public static boolean recompileVoiceProfiles = false;
   public static boolean compileCallVoiceProfiles = true;
   public static float idleMinTimeInterval = 0.1F;
   public static float inputMaxFramerateTime = 5.0F;
   public static float renderChangeMaxFramerateTime = 5.0F;
   public static long gameTimeOffset = 1502781328000L;
   public static float batteryStartLevel = 1.0F;
   public static float batteryDrainRate = 7.9365076E-5F;
   public static float batteryMinLevel = 0.15F;
   public static float tRestoreSkipDelay = 10.0F;
   public static Gson gson = new Gson();
   public static SheetsParser sheets = new SheetsParser();
   public static final String IRIS_BEHAVIOUR_NORMAL = "IRIS_BEHAVIOUR_NORMAL";
   public static final String IRIS_BEHAVIOUR_CURSED = "IRIS_BEHAVIOUR_CURSED";
   public static final String DEFAULT_CONTEXT_NAME = "context_default";
   public static final String CONTEXT_DEFAULT_HOMESCREEN = "context_default_homescreen";
   public static final String CONTEXT_DEFAULT_IRIS_THREAD = "context_default_iris_thread";
   public static final String CONTEXT_DEFAULT_IRIS_MEMO = "context_default_iris_memo";
   public static final String CONTEXT_DEFAULT_WHATSUP_CONTACTS = "context_default_whatsup_contacts";
   public static final String CONTEXT_DEFAULT_WHATSUP_THREAD = "context_default_whatsup_thread";
   public static final String CONTEXT_DEFAULT_MAIL_CONTACTS = "context_default_mail_contacts";
   public static final String CONTEXT_DEFAULT_MAIL_THREAD = "context_default_mail_thread";
   public static final String CONTEXT_APP_OPTIONS = "CONTEXT_APP_OPTIONS";
   public static final String CONTEXT_APP_PRIVATE = "CONTEXT_APP_PRIVATE";
   public static final String CONTEXT_APP_NOTES = "CONTEXT_APP_NOTES";
   public static final String CONTEXT_APP_CHATS = "CONTEXT_APP_CHATS";
   public static final String CONTEXT_APP_MAPS = "CONTEXT_APP_MAPS";
   public static final String CONTEXT_APP_FRIENDS = "CONTEXT_APP_FRIENDS";
   public static final String CONTEXT_APP_MUSIC = "CONTEXT_APP_MUSIC";
   public static final String CONTEXT_APP_CALLS = "CONTEXT_APP_CALLS";
   public static final String CONTEXT_APP_GALLERY = "CONTEXT_APP_GALLERY";
   public static final String CONTEXT_APP_MAIL = "CONTEXT_APP_MAIL";
   public static final String CONTEXT_APP_SPARK = "CONTEXT_APP_SPARK";
   public static final String CONTEXT_APP_BROWSER = "CONTEXT_APP_BROWSER";
   public static final String CONTEXT_APP_VLOGGR = "CONTEXT_APP_VLOGGR";
   public static final String CONTEXT_APP_MALWARE = "CONTEXT_APP_MALWARE1";
   public static final String TRIGGER_OPEN_VIDEO_FROM_MESSAGES = "TRIGGER_OPEN_VIDEO_FROM_MESSAGES";
   public static final String TRIGGER_BACK_TO_INBOX = "TRIGGER_BACK_TO_INBOX";
   public static final String TRIGGER_LEAVE_CHAT_THREAD_SCREEN = "TRIGGER_LEAVE_CHAT_THREAD_SCREEN";
   public static final String TRIGGER_OPEN_IRIS_FROM_HOMESCREEN = "TRIGGER_OPEN_IRIS_FROM_HOMESCREEN";
   public static final String TRIGGER_BACK_TO_HOMESCREEN = "TRIGGER_BACK_TO_HOMESCREEN";
   public static final String TRIGGER_HOMESCREEN_OPENED = "TRIGGER_HOMESCREEN_OPENED";
   public static final String TRIGGER_UNLOCK_TO_HOMESCREEN = "TRIGGER_UNLOCK_TO_HOMESCREEN";
   public static final String TRIGGER_IRIS_OVERLAY_CLOSING = "TRIGGER_IRIS_OVERLAY_CLOSING";
   public static final String TRIGGER_PHONECALL_ENDED = "TRIGGER_PHONECALL_ENDED";
   public static final String TRIGGER_PHONECALL_CANCELLED = "TRIGGER_PHONECALL_CANCELLED";
   public static final String TRIGGER_PHONECALL_ACCEPTED = "TRIGGER_PHONECALL_ACCEPTED";
   public static final String TRIGGER_PHONECALL_DECLINED = "TRIGGER_PHONECALL_DECLINED";
   public static final String TRIGGER_BACK_FROM_VIDEO_PLAYER = "TRIGGER_BACK_FROM_VIDEO_PLAYER";
   public static final String TRIGGER_VIDEO_PLAYBACK_FINISHED = "TRIGGER_VIDEO_PLAYBACK_FINISHED";
   public static final String TRIGGER_OPEN_GALLERY_FROM_HOMESCREEN = "TRIGGER_OPEN_GALLERY_FROM_HOMESCREEN";
   public static final String TRIGGER_PHOTOROLL_VIEWER_NAVIGATE = "TRIGGER_PHOTOROLL_VIEWER_NAVIGATE";
   public static final String TRIGGER_PHOTOROLL_OPEN_MEDIA = "TRIGGER_PHOTOROLL_OPEN_MEDIA";
   public static final String TRIGGER_VIDEOAPP_PLAYER_NAVIGATE = "TRIGGER_VIDEOAPP_PLAYER_NAVIGATE";
   public static final String TRIGGER_PRIVATE_ITEM_OPENED = "TRIGGER_PRIVATE_ITEM_OPENED";
   public static final String TRIGGER_FRIENDS_FORGOT_PASSWORD = "TRIGGER_FRIENDS_FORGOT_PASSWORD";
   public static final String TRIGGER_FRIENDS_LOGIN_OPENED = "TRIGGER_FRIENDS_LOGIN_OPENED";
   public static final String TRIGGER_LOCKSCREEN_KEY_SHOWN = "TRIGGER_LOCKSCREEN_KEY_SHOWN";
   public static final String TRIGGER_LOCKSCREEN_KEY_CLICKED = "TRIGGER_LOCKSCREEN_KEY_CLICKED";
   public static final String TRIGGER_LOCKSCREEN_UNLOCK = "TRIGGER_LOCKSCREEN_UNLOCK";
   public static final String TRIGGER_SPARK_REFRESH_STATS = "TRIGGER_SPARK_REFRESH_STATS";
   public static final String TRIGGER_SPARK_SUBMIT_PROFILE = "TRIGGER_SPARK_SUBMIT_PROFILE";
   public static final String TRIGGER_LEAVE_SPARK_EDIT_SCREEN = "TRIGGER_LEAVE_SPARK_EDIT_SCREEN";
   public static final String TRIGGER_SPARK_MATCH_SCREEN_REFRESHED = "TRIGGER_SPARK_MATCH_SCREEN_REFRESHED";
   public static final String TRIGGER_LEAVE_SPARK_MATCH_SCREEN = "TRIGGER_LEAVE_SPARK_MATCH_SCREEN";
   public static final String TRIGGER_LEAVE_SPARK_THREAD_SCREEN = "TRIGGER_LEAVE_SPARK_THREAD_SCREEN";
   public static final String TRIGGER_SPARK_MATCH_LIKE = "TRIGGER_SPARK_MATCH_LIKE";
   public static final String TRIGGER_SPARK_MATCH_NOPE = "TRIGGER_SPARK_MATCH_NOPE";
   public static final String TRIGGER_SPARK_THREAD_SCREEN_SHOWN = "TRIGGER_SPARK_THREAD_SCREEN_SHOWN";
   public static String SAVE_FILENAME = "save20170902.fs";
   public static final String PREF_FILENAME = "preferences";
   public static final String STATE_FINISHED_GAME = "STATE_FINISHED_GAME";
   public static final String STATE_GAMEPLUS_MODE = "STATE_GAMEPLUS_MODE";
   public static final String STATE_SUBTITLE_ENABLED = "STATE_SUBTITLE_ENABLED";
   public static final String STATE_HQ_VIDEOS_ENABLED = "STATE_HQ_VIDEOS_ENABLED";
   public static final String STATE_LANGUAGE = "STATE_LANGUAGE";
   public static final String STATE_HAS_DISCORD_OPENED = "STATE_HAS_DISCORD_OPENED";
   public static final String STATE_HAS_OPINION_ENJOYED = "STATE_HAS_OPINION_ENJOYED";
   public static final String SAVE_CHECKPOINT = "SAVE_CHECKPOINT";
   public static final String SAVE_TIME_ELAPSED = "SAVE_TIME_ELAPSED";
   public static final String SAVE_BATTERY_LEVEL = "SAVE_BATTERY_LEVEL";
   public static final String STATE_ACHIEVEMENTS_PREFIX = "ACHIEVEMENTS.";
   public static final String STATE_INTRO_LOCK_GLITCH_STARTED = "STATE_INTRO_LOCK_GLITCH_STARTED";
   public static final String STATE_IDLE_SCARE_COUNT = "STATE_IDLE_SCARE_COUNT";
   public static final String STATE_IDLE_SCARE_LAST_TIME = "STATE_IDLE_SCARE_LAST_TIME";
   public static final String STATE_SEEN_FARADAY_EMAIL = "STATE_SEEN_FARADAY_EMAIL";
   public static final String STATE_SEEN_MOM_EMAIL = "STATE_SEEN_MOM_EMAIL";
   public static final String STATE_DEMON_ANNA_POST_SEEN = "STATE_DEMON_ANNA_POST_SEEN";
   public static final String STATE_DEMON_ANNA_POST_SEEN_ACT2 = "STATE_DEMON_ANNA_POST_SEEN_ACT2";
   public static final String STATE_ACT2_BOOT_STARTED = "STATE_ACT2_BOOT_STARTED";
   public static final String STATE_ACT2_LOCKING_GREG_CHAT = "STATE_ACT2_LOCKING_GREG_CHAT";
   public static final String STATE_ACT2_RESTORING_FROM_ANNA_PC = "STATE_ACT2_RESTORING_FROM_ANNA_PC";
   public static final String STATE_ACT2_FULLNAME_REQUIREMENT = "STATE_ACT2_FULLNAME_REQUIREMENT";
   public static final String STATE_ACT2_AGE_LOCATION_REQUIREMENT = "STATE_ACT2_AGE_LOCATION_REQUIREMENT";
   public static final String STATE_ACT2_SEEN_TAYLOR_RECORDS = "STATE_ACT2_SEEN_TAYLOR_RECORDS";
   public static final String STATE_ACT2_SEEN_CBB_ARTICLE = "STATE_ACT2_SEEN_CBB_ARTICLE";
   public static final String STATE_ACT2_SOLVED_MURV_EMAIL = "STATE_ACT2_SOLVED_MURV_EMAIL";
   public static final String TRIGGER_BOOT_JAMES_CHAT_DONE = "TRIGGER_BOOT_JAMES_CHAT_DONE";
   public static final String STATE_ACT3_RESTORING_FROM_ANNA_WORKPC = "STATE_ACT3_RESTORING_FROM_ANNA_WORKPC";
   public static final String STATE_ACT3_SEEN_PHRESHIDEAS_SITE = "STATE_ACT3_SEEN_PHRESHIDEAS_SITE";
   public static final String STATE_ACT3_SEEN_CONSPIRACY_SITE = "STATE_ACT3_SEEN_CONSPIRACY_SITE";
   public static final String JABBR_IRIS_PROFANITY_MAIL = "mail.irisprofanity.show";
   public static final String CHECKPOINT_NONE = "CHECKPOINT_NONE";
   public static final String CHECKPOINT_0 = "CHECKPOINT_0";
   public static final String CHECKPOINT_1 = "CHECKPOINT_1";
   public static final String CHECKPOINT_2 = "CHECKPOINT_2";
   public static final String CHECKPOINT_3 = "CHECKPOINT_3";
   public static final String CHECKPOINT_4 = "CHECKPOINT_4";
   public static final String CHECKPOINT_5 = "CHECKPOINT_5";
   public static final String CHECKPOINT_6 = "CHECKPOINT_6";
   public static final String CHECKPOINT_7 = "CHECKPOINT_7";
   public static final String CHECKPOINT_8A = "CHECKPOINT_8A";
   public static final String CHECKPOINT_8B = "CHECKPOINT_8B";
   public static final String CHECKPOINT_8 = "CHECKPOINT_8";
   public static final String CHECKPOINT_9 = "CHECKPOINT_9";
   public static final String CHECKPOINT_9A = "CHECKPOINT_9A";
   public static final String CHECKPOINT_10 = "CHECKPOINT_10";
   public static final String CHECKPOINT_11A = "CHECKPOINT_11A";
   public static final String CHECKPOINT_11 = "CHECKPOINT_11";
   public static final String CHECKPOINT_2_1 = "CHECKPOINT_2_1";
   public static final String CHECKPOINT_2_2 = "CHECKPOINT_2_2";
   public static final String CHECKPOINT_2_3 = "CHECKPOINT_2_3";
   public static final String CHECKPOINT_2_4 = "CHECKPOINT_2_4";
   public static final String CHECKPOINT_2_5 = "CHECKPOINT_2_5";
   public static final String CHECKPOINT_2_6 = "CHECKPOINT_2_6";
   public static final String CHECKPOINT_2_6A = "CHECKPOINT_2_6A";
   public static final String CHECKPOINT_2_7 = "CHECKPOINT_2_7";
   public static final String CHECKPOINT_2_8 = "CHECKPOINT_2_8";
   public static final String CHECKPOINT_2_9 = "CHECKPOINT_2_9";
   public static final String CHECKPOINT_2_10 = "CHECKPOINT_2_10";
   public static final String CHECKPOINT_2_11 = "CHECKPOINT_2_11";
   public static final String CHECKPOINT_2_12 = "CHECKPOINT_2_12";
   public static final String CHECKPOINT_2_13 = "CHECKPOINT_2_13";
   public static final String CHECKPOINT_3_1 = "CHECKPOINT_3_1";
   public static final String CHECKPOINT_3_2 = "CHECKPOINT_3_2";
   public static final String CHECKPOINT_3_3 = "CHECKPOINT_3_3";
   public static final String CHECKPOINT_3_4 = "CHECKPOINT_3_4";
   public static final String CHECKPOINT_3_5 = "CHECKPOINT_3_5";
   public static final String CHECKPOINT_3_6 = "CHECKPOINT_3_6";
   public static final String CHECKPOINT_3_7 = "CHECKPOINT_3_7";
   public static final String CHECKPOINT_3_7A = "CHECKPOINT_3_7A";
   public static final String CHECKPOINT_3_8 = "CHECKPOINT_3_8";
   public static final String CHECKPOINT_3_9 = "CHECKPOINT_3_9";
   public static final String CHECKPOINT_3_10 = "CHECKPOINT_3_10";
   public static final String CHECKPOINT_3_11 = "CHECKPOINT_3_11";
   public static final String CHECKPOINT_3_12 = "CHECKPOINT_3_12";
   public static final String CHECKPOINT_3_13 = "CHECKPOINT_3_13";
   public static final String QUEST_0 = "QUEST_0";
   public static final String QUEST_1 = "QUEST_1";
   public static final String QUEST_2 = "QUEST_2";
   public static final String QUEST_3 = "QUEST_3";
   public static final String QUEST_4 = "QUEST_4";
   public static final String QUEST_5 = "QUEST_5";
   public static final String QUEST_6 = "QUEST_6";
   public static final String QUEST_7 = "QUEST_7";
   public static final String QUEST_8 = "QUEST_8";
   public static final String QUEST_9 = "QUEST_9";
   public static final String QUEST_10 = "QUEST_10";
   public static final String QUEST_11 = "QUEST_11";
   public static final String QUEST_12 = "QUEST_12";
   public static final String QUEST_13 = "QUEST_13";
   public static final String QUEST_14 = "QUEST_14";
   public static final String QUEST_15 = "QUEST_15";
   public static final String QUEST_16 = "QUEST_16";
   public static final String QUEST_17 = "QUEST_17";
   public static final String QUEST_18 = "QUEST_18";
   public static final String QUEST_19 = "QUEST_19";
   public static final String QUEST_20 = "QUEST_20";
   public static final String QUEST_21 = "QUEST_21";
   public static final String QUEST2_1 = "QUEST2_1";
   public static final String QUEST2_1_1 = "QUEST2_1_1";
   public static final String QUEST2_2 = "QUEST2_2";
   public static final String QUEST2_3 = "QUEST2_3";
   public static final String QUEST2_4 = "QUEST2_4";
   public static final String QUEST2_5 = "QUEST2_5";
   public static final String QUEST2_6 = "QUEST2_6";
   public static final String QUEST2_7 = "QUEST2_7";
   public static final String QUEST2_8 = "QUEST2_8";
   public static final String QUEST2_9 = "QUEST2_9";
   public static final String QUEST2_10 = "QUEST2_10";
   public static final String QUEST2_11 = "QUEST2_11";
   public static final String QUEST2_12 = "QUEST2_12";
   public static final String QUEST2_13 = "QUEST2_13";
   public static final String QUEST2_14 = "QUEST2_14";
   public static final String QUEST2_15 = "QUEST2_15";
   public static final String QUEST2_16 = "QUEST2_16";
   public static final String QUEST3_1 = "QUEST3_1";
   public static final String QUEST3_2 = "QUEST3_2";
   public static final String QUEST3_3 = "QUEST3_3";
   public static final String QUEST3_4 = "QUEST3_4";
   public static final String QUEST3_5 = "QUEST3_5";
   public static final String QUEST3_6 = "QUEST3_6";
   public static final String QUEST3_7 = "QUEST3_7";
   public static final String QUEST3_8 = "QUEST3_8";
   public static final String QUEST3_9 = "QUEST3_9";
   public static final String QUEST3_10 = "QUEST3_10";
   public static final String QUEST3_11 = "QUEST3_11";
   public static final String QUEST3_12 = "QUEST3_12";
   public static float tKeyboardAnimationSpeedMultiplier = 1.0F;
   public static float tChatTimingMultiplier = 0.9F;
   public static boolean allowSkipChatVoice = false;
   public static boolean allowSkipFreakoutVideo = false;
   public static float tLockScreenWaitBeforeGlitch = 7.0F;
   public static boolean ignoreSaveErrors = false;
   public static boolean autoresolveRestoreScreens = false;
   public static float restoreWinDelay = 3.0F;
   public static float a1_demon_post_delay = 5.0F;
   public static float a2_demon_post_delay = 5.0F;
   public static float a1_taylor_impatient_time = 20.0F;
   public static float a1_taylor_impatient_time_from_save = 5.0F;
   public static int a2_memory_wipe_timeout = 120;
   public static int a2_boot_homescreen_count = 3;
   public static float a2_murilo_call_delay = 180.0F;
   public static float a2_murilo_call_delay_from_save = 20.0F;
   public static float a2_murilo_call_retry_delay = 8.0F;
   public static float a2_greg_call_delay = 5.0F;
   public static float a2_taylor_call_delay = 5.0F;
   public static float a2_greg_followup_taylor_time = 300.0F;
   public static float a2_greg_followup_taylor_time_from_save = 60.0F;
   public static float a2_james_haunted_end_delay = 8.0F;
   public static float a3_james_haunted_end_delay = 8.0F;
   public static float a3_murilo_call_delay = 120.0F;
   public static float a3_murilo_call_delay_from_save = 20.0F;
   public static float a3_murilo_call_retry_delay = 8.0F;
   public static float a3_murilo_ashleyreported_call_delay = 120.0F;
   public static float a3_murilo_ashleyreported_call_delay_from_save = 20.0F;
   public static float a3_murilo_ashleyreported_call_retry_delay = 5.0F;
   public static float a3_taylor_followup_james_time = 300.0F;
   public static float sparkVoiceInitialMessageDelay = 0.8F;
   public static float restoreImageLength = 1.0F;
   public static int restoreImageFragments = 9;
   public static int restoreImageMaxProfiles = 6;
   public static String subtitlesConfigFilename = "content/subtitles/config";
   public static String galleryConfigFilename = "content/gallery/config";
   public static String chatsConfigFilename = "content/chats/config";
   public static String sparkConfigFilename = "content/spark/config";
   public static String mailConfigFilename = "content/mail/config";
   public static String phoneConfigFilename = "content/calls/config";
   public static String jabbrConfigFilename = "content/jabbr/config";
   public static String browserConfigFilename = "content/web/config";
   public static String vloggrConfigFilename = "content/vloggr/config";
   public static String sparkNewConfigFilename = "content/spark/newconfig";
   public static String irisQuestSave = "iris.quests";
   public static boolean loadDialogueTreeSourcesFirst = false;
   public static boolean allowGlobalOnlineSources = false;
   public static boolean rebuildAllWebsites = false;
   public static boolean checkAllAssets = false;

   public static void addGoogleSource(String basePath, String filename, String sheetUrl) {
      if (LiveEditor.editor != null && allowGlobalOnlineSources) {
         String[] paths = sheetUrl.split("/");
         if (paths.length != 2) {
            throw new IllegalArgumentException("Malformed url: " + sheetUrl);
         } else {
            String url = String.format(Locale.US, "https://docs.google.com/spreadsheets/d/%s/export?format=csv&id=%s&gid=%s", paths[0], paths[0], paths[1]);
            NetRequest request = new NetRequest();
            request.setUrl(url);
            request.setMethod("GET");
            LiveEditor.editor.addOnlineSource(basePath, filename, request);
         }
      }
   }

   public static String[] splitCSV(String csv) {
      String[] tags = csv.trim().split("\\s*,\\s*");
      return tags.length == 1 && tags[0].isEmpty() ? new String[0] : tags;
   }

   public static void dumpTexture(String path) {
      TextureFile texture = new TextureFile();
      texture.load(path + ".texture");
      FIFormat.FragmentedImageData data = (FIFormat.FragmentedImageData)texture.getImageData(0);
      Pixmap pixmap = data.reconstruct()[0];
      PixmapIO.writePNG(File.openCache("dump/" + path), pixmap);
      pixmap.dispose();
      data.release();
   }

   public static enum Achievement {
      UNLOCKED_MAIL,
      UNLOCKED_JABBR,
      GOSSIP_GIRL,
      SHE_NEEDS_TO_KNOW,
      SHE_LOVES_ME,
      SHARING_IS_CARING,
      PUNKED,
      JUST_IN_TIME,
      THIS_IS_THE_POLICE,
      NSFW,
      WORDSMITH(25),
      DEREZZED(7),
      THAT_IS_NOT_A_COMPLIMENT,
      THAT_IS_A_COMPLIMENT,
      LOOKING_FOR_LOVE(2),
      ASK_HER_ANYTHING,
      CRIME_DOESNT_PAY,
      RUN_GREG_RUN,
      YOURE_HIRED,
      THIS_IS_TOO_MUCH,
      YOU_FOUND_ANNA,
      YOU_KILLED_ANNA,
      A_HAPPY_ENDING,
      WINDY_CONVERGENCE;

      public final int count;

      private Achievement() {
         this(1);
      }

      private Achievement(int count) {
         this.count = count;
      }
   }
}
