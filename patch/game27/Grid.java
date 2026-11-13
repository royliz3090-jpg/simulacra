package game27;

import bsh.Interpreter;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Application.ApplicationType;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.utils.Array;
import com.badlogic.gdx.utils.ObjectMap;
import game27.app.boot.BootScreen;
import game27.app.browser.BrowserScreen;
import game27.app.chats.WhatsupApp;
import game27.app.friends.FriendsApp;
import game27.app.gallery.PhotoRollApp;
import game27.app.homescreen.Homescreen;
import game27.app.mail.MailApp;
import game27.app.phone.PhoneApp;
import game27.app.restore.RestoreImageScreen;
import game27.app.restore.RestorePhraseScreen;
import game27.app.spark.SparkApp;
import game27.app.vloggr.VloggrScreen;
import game27.gb.GBENUS;
import game27.gb.GBPrecacher;
import game27.gbeslatam.GBESLATAM;
import game27.gbzhcn.GBZHCN;
import game27.model.ConfigModel;
import game27.renderer.SaraRenderer;
import game27.triggers.ACT1;
import game27.triggers.ACT2;
import game27.triggers.ACT3;
import game27.triggers.Triggers;
import java.io.ByteArrayInputStream;
import java.util.Locale;
import java.util.Map;
import java.util.TimeZone;
import sengine.Entity;
import sengine.File;
import sengine.Sys;
import sengine.Universe;
import sengine.audio.Audio;
import sengine.graphics2d.Fonts;
import sengine.graphics2d.Matrices;
import sengine.graphics2d.Sprite;
import sengine.mass.MassFile;
import sengine.materials.ColorAttribute;
import sengine.sheets.SheetParser;
import sengine.ui.UIElement;
import sengine.utils.Builder;
import sengine.utils.LoadingMenu;
import sengine.utils.NetRequest;
import sengine.utils.StreamablePrecacher;
import sengine.utils.Universe2D;

public class Grid extends Universe2D implements LoadingMenu.Handler {
   public static final String TAG = "Grid";
   public static final float TIMESTEP = 0.04F;
   public boolean skipIntoMainMenu;
   public Grid.ScreenCompositor compositor;
   public Entity.Group underlayGroup;
   public Entity.Group screensGroupContainer;
   public Entity.Group screensGroup;
   public Entity.Group overlayGroup;
   public PhotoRollApp photoRollApp;
   public WhatsupApp whatsupApp;
   public SparkApp sparkApp;
   public MailApp mailApp;
   public PhoneApp phoneApp;
   public FriendsApp friendsApp;
   public RestoreImageScreen restoreImageApp;
   public RestorePhraseScreen restorePhraseApp;
   public BrowserScreen browserApp;
   public VloggrScreen vloggrApp;
   public BootScreen bootScreen;
   public LockScreen lockScreen;
   public Homescreen homescreen;
   public Notification notification;
   public MemoryWipeDialog memoryWipeDialog;
   public Screen screen;
   public Keyboard keyboard;
   public IdleScareScheduler idleScare;
   public LoadingMenu loadingMenu;
   public MainMenu mainMenu;
   public CreditsMenu creditsMenu;
   public final ScriptState state = new ScriptState();
   private String queuedSavePoint = null;
   public Interpreter interpreter;
   private long timeStarted = 0L;
   private long timeOffset = Globals.gameTimeOffset;
   private long timeElapsed = 0L;
   public TimeZone timeZone = TimeZone.getTimeZone("GMT+8:00");
   public final StreamablePrecacher precacher;
   float batteryLevel = Globals.batteryStartLevel;
   private float minBatteryLevel = Globals.batteryMinLevel;
   private float batteryDrain = Globals.batteryDrainRate;
   public Sprite wallpaperSprite;
   public final ObjectMap<String, Grid.Trigger> triggers = new ObjectMap();
   public final Array<Grid.ScheduledRunnable> scheduledRunnables = new Array(Grid.ScheduledRunnable.class);

   public String format(String string) {
      if (string == null) {
         return null;
      } else {
         String s = string;

         int c;
         while ((c = s.indexOf("#state:")) != -1) {
            int start = c + "#state:".length();
            int end = s.indexOf("#", start);
            String name = s.substring(start, end);
            String var = this.state.get(name, null);
            if (var == null) {
               Sys.error("Grid", "Unable to state \"" + name + "\" to format \"" + string + "\"");
            }

            s = s.substring(0, c) + var + s.substring(end + 1);
         }

         return s;
      }
   }

   public void setBattery(float level, float minLevel, float drain) {
      this.batteryLevel = level;
      this.minBatteryLevel = minLevel;
      this.batteryDrain = drain;
   }

   public long getSystemTime() {
      return System.currentTimeMillis() - this.timeStarted + this.timeOffset + this.timeElapsed;
   }

   public void setSystemTime(long targetTime) {
      this.timeElapsed = this.timeElapsed + (targetTime - this.getSystemTime());
   }

   public boolean isStateUnlocked(String name) {
      return this.state.get(name, false);
   }

   public boolean unlockState(String name) {
      if (this.state.get(name, false)) {
         return false;
      } else {
         this.state.set(name, true);
         return true;
      }
   }

   public boolean resetState(String name) {
      boolean previous = this.state.get(name, false);
      this.state.set(name, false);
      return previous;
   }

   public boolean trigger(String name) {
      Grid.Trigger trigger = (Grid.Trigger)this.triggers.get(name);
      return trigger == null ? true : trigger.trigger(name);
   }

   public void addTrigger(String name, Grid.Trigger trigger) {
      this.triggers.put(name, trigger);
   }

   public void removeTrigger(String name) {
      this.triggers.remove(name);
   }

   public void scheduleRunnable(Runnable runnable, float tDelay) {
      Grid.ScheduledRunnable scheduledRunnable = new Grid.ScheduledRunnable(runnable, tDelay);
      scheduledRunnable.tTriggerScheduled = this.getRenderTime() + tDelay;
      this.scheduledRunnables.add(scheduledRunnable);
   }

   public Object eval(String tag, String code) {
      try {
         return this.interpreter.eval(code);
      } catch (Throwable var4) {
         Sys.error(tag, "Unable to eval code:\n" + code, var4);
         return null;
      }
   }

   public void stopProcesses() {
      this.whatsupApp.renderingEnabled = false;
   }

   public void resumeProcesses() {
      this.whatsupApp.renderingEnabled = true;
   }

   public void stopAmbiance() {
      Audio.pauseMusic();
   }

   public void resumeAmbiance() {
      Audio.resumeMusic();
   }

   public Grid() {
      this(false);
   }

   public Grid(boolean skipIntoMainMenu) {
      super(0.04F, -1.0F);
      this.skipIntoMainMenu = skipIntoMainMenu;
      Globals.grid = this;
      this.interpreter = File.interpreter();

      try {
         this.interpreter.set("v", this);
         this.interpreter.set("state", this.state);
         this.interpreter.eval(Game.configConsoleDefaults);
      } catch (Throwable var3) {
         Sys.error("Grid", "Unable to initialize state interpreter", var3);
      }

      this.precacher = new StreamablePrecacher();
      this.precacher.attach(this);
      Builder.overrides.clear();
      Globals.contentPrefix = Gdx.app.getPreferences("preferences").getString("STATE_LANGUAGE", "en-us://");
      if (Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_ES_LATAM)) {
         GBESLATAM.setup();
      } else if (Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_EN_US)) {
         GBENUS.setup();
      } else {
         GBZHCN.setup();
      }

      this.timeStarted = System.currentTimeMillis();
      this.prepareSceneGraph();
      this.mainMenu = new MainMenu();
      this.creditsMenu = new CreditsMenu();
      this.mainMenu.attach(this.compositor);
   }

   public void startLoad(LoadingMenu menu) {
      Fonts.multithreading(true);
      this.loadingMenu = menu;
      this.loadingMenu.setHandler(this);
      this.loadingMenu.attach(this.compositor);
   }

   private void prepareSceneGraph() {
      this.compositor = new Grid.ScreenCompositor();
      this.compositor.attach(this);
      this.underlayGroup = new Entity.Group(true, true, true);
      this.screensGroupContainer = new Entity.Group(true, true, true);
      this.screensGroup = new Entity.Group(true, true, true);
      this.overlayGroup = new Entity.Group(true, true, true);
      this.underlayGroup.attach(this.compositor);
      this.screensGroupContainer.attach(this.compositor);
      this.screensGroup.attach(this.screensGroupContainer);
      this.overlayGroup.attach(this.compositor);
      this.screen = new Screen();
      this.screen.attach(this);
   }

   public void writeSaveGame(String checkpoint) {
      this.queuedSavePoint = checkpoint;
      if (this.whatsupApp.pack(this.state)) {
         if (this.sparkApp.pack(this.state)) {
            if (this.mailApp.pack(this.state)) {
               if (this.phoneApp.pack(this.state)) {
                  this.friendsApp.pack(this.state);
                  this.notification.pack(this.state);
                  this.vloggrApp.pack(this.state);
                  this.browserApp.pack(this.state);
                  this.idleScare.pack(this.state);
                  this.state.set("SAVE_CHECKPOINT", checkpoint);
                  long currentTimeMillis = System.currentTimeMillis();
                  this.timeElapsed = this.timeElapsed + (currentTimeMillis - this.timeStarted);
                  this.timeStarted = currentTimeMillis;
                  this.state.set("SAVE_TIME_ELAPSED", this.timeElapsed);
                  this.state.set("SAVE_BATTERY_LEVEL", this.batteryLevel);
                  this.queuedSavePoint = null;
                  MassFile saveFile = new MassFile();
                  this.state.save(saveFile);
                  Game.game.platform.writeSaveGame(saveFile);
                  this.notification.showSavedIndicator();
               }
            }
         }
      }
   }

   private void loadSaveGame() {
      this.state.clear();
      if (Game.game.platform.existsSaveGame()) {
         try {
            MassFile saveFile = Game.game.platform.readSaveGame();
            this.state.load(saveFile);
         } catch (Throwable var2) {
            Sys.error("Grid", "Unable to load save", var2);
            this.state.clear();
         }
      }

      this.timeElapsed = this.state.get("SAVE_TIME_ELAPSED", 0L);
      this.timeStarted = System.currentTimeMillis();
      this.batteryLevel = this.state.get("SAVE_BATTERY_LEVEL", Globals.batteryStartLevel);
   }

   public void restoreSaveGame() {
      String checkpoint = this.state.get("SAVE_CHECKPOINT", null);
      if (checkpoint == null) {
         checkpoint = "CHECKPOINT_NONE";
         Sys.info("Grid", "Starting new game checkpoint");
      } else {
         Sys.info("Grid", "Restoring checkpoint \"" + checkpoint + "\"");
      }

      if (checkpoint.equals("CHECKPOINT_0")) {
         ACT1.checkpoint_0();
      } else if (checkpoint.equals("CHECKPOINT_1")) {
         ACT1.checkpoint_1();
      } else if (checkpoint.equals("CHECKPOINT_2")) {
         ACT1.checkpoint_2();
      } else if (checkpoint.equals("CHECKPOINT_3")) {
         ACT1.checkpoint_3();
      } else if (checkpoint.equals("CHECKPOINT_4")) {
         ACT1.checkpoint_4();
      } else if (checkpoint.equals("CHECKPOINT_5")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_6")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_7")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_8A")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_8B")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_8")) {
         ACT1.checkpoint_8();
      } else if (checkpoint.equals("CHECKPOINT_9")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_9A")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_10")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_11A")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_11")) {
         ACT1.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_1")) {
         ACT2.checkpoint_1();
      } else if (checkpoint.equals("CHECKPOINT_2_2")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_3")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_4")) {
         ACT2.checkpoint_4();
      } else if (checkpoint.equals("CHECKPOINT_2_5")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_6")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_6A")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_7")) {
         ACT2.checkpoint_7();
      } else if (checkpoint.equals("CHECKPOINT_2_8")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_9")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_10")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_11")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_12")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_2_13")) {
         ACT2.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_1")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_2")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_3")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_4")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_5")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_6")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_7")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_7A")) {
         ACT3.checkpoint_notAnnaRevealedToAshley();
      } else if (checkpoint.equals("CHECKPOINT_3_8")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_9")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_10")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_11")) {
         ACT3.checkpoint_openHomescreen();
      } else if (checkpoint.equals("CHECKPOINT_3_12")) {
         ACT3.checkpoint_waitingDemon();
      } else if (checkpoint.equals("CHECKPOINT_3_13")) {
         ACT3.checkpoint_demonMatched();
      } else {
         Triggers.boot();
      }
   }

   private void prepareContent() {
      this.wallpaperSprite = new Sprite(Globals.LENGTH, SaraRenderer.renderer.screenNoiseMaterial);
      ColorAttribute.of(this.wallpaperSprite).set(858993663);
      this.loadSaveGame();
      this.keyboard = Globals.CONTENT_PREFIX_ES_LATAM.equals(Globals.contentPrefix) ? GBESLATAM.newKeyboard() : new Keyboard();
      this.notification = new Notification();
      this.homescreen = new Homescreen();
      this.photoRollApp = new PhotoRollApp();
      this.whatsupApp = new WhatsupApp();
      this.sparkApp = new SparkApp();
      this.mailApp = new MailApp();
      this.phoneApp = new PhoneApp();
      this.friendsApp = new FriendsApp();
      this.browserApp = new BrowserScreen();
      this.vloggrApp = new VloggrScreen();
      this.restoreImageApp = new RestoreImageScreen();
      this.restorePhraseApp = new RestorePhraseScreen();
      this.bootScreen = new BootScreen();
      this.lockScreen = new LockScreen();
      this.idleScare = new IdleScareScheduler();
      Triggers.load();
   }

   public void loadOnlineSource() {
      String url = String.format(Locale.US, "https://docs.google.com/spreadsheets/d/%s/export?format=xlsx", Globals.googleConfigID);
      NetRequest request = new NetRequest("Story Config");
      request.setUrl(url);
      request.setMethod("GET");
      byte[] xlsx = request.readBytes();
      Map<String, String[][]> sheets = SheetParser.convertXLSX(new ByteArrayInputStream(xlsx));
      ConfigModel config = new ConfigModel(Globals.contentPrefix, sheets);
      config.insert("main.v1");
   }

   @Override
   public void load() {
      Sys.system.minTimeInterval = Globals.loadingFrameRate;
      File.unpackFS("videos.fs", "web.fs", "content.fs", "emojis.fs");
      if (Globals.allowGlobalOnlineSources) {
         this.loadOnlineSource();
      }

      if (Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_ES_LATAM)) {
         File.unpackFS("es-latam.fs");
      } else if (Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_EN_US)) {
         File.unpackFS("en-us.fs");
      } else {
         File.unpackFS("zh-cn.fs");
      }

      Builder<Object> builder = new Builder<>(GBPrecacher.class, this.precacher);
      builder.build();
      this.prepareContent();
      Sys.system.minTimeInterval = 0.0F;
   }

   @Override
   public void complete(LoadingMenu menu) {
      Fonts.multithreading(false);
      this.mainMenu.doneLoading();
   }

   public void start() {
      if (Gdx.app.getType() != ApplicationType.Desktop) {
         Sys.system.idleMinTimeInterval = Globals.idleMinTimeInterval;
         Sys.system.inputMaxFramerateTime = Globals.inputMaxFramerateTime;
         Sys.system.renderChangeMaxFramerateTime = Globals.renderChangeMaxFramerateTime;
      }

      this.notification.attach(this.overlayGroup);
      this.photoRollApp.attach(this);
      this.whatsupApp.attach(this);
      this.sparkApp.attach(this);
      this.mailApp.attach(this);
      this.phoneApp.attach(this);
      this.friendsApp.attach(this);
      this.idleScare.attach(this);
      this.restoreSaveGame();
   }

   @Override
   public void exception(LoadingMenu menu, Throwable e) {
      throw new RuntimeException("Initial loading failed", e);
   }

   @Override
   protected void render(Universe v, float r, float renderTime) {
      super.render(v, r, renderTime);
      if (this.queuedSavePoint != null) {
         this.writeSaveGame(this.queuedSavePoint);
      }

      this.batteryLevel = this.batteryLevel - this.batteryDrain * this.getRenderDeltaTime();
      if (this.batteryLevel < this.minBatteryLevel) {
         this.batteryLevel = this.minBatteryLevel;
      }

      for (int c = 0; c < this.scheduledRunnables.size; c++) {
         Grid.ScheduledRunnable scheduledRunnable = ((Grid.ScheduledRunnable[])this.scheduledRunnables.items)[c];
         if (renderTime > scheduledRunnable.tTriggerScheduled) {
            scheduledRunnable.runnable.run();
            this.scheduledRunnables.removeIndex(c);
            c--;
         }
      }

      if (this.wallpaperSprite != null) {
         this.wallpaperSprite.load();
      }
   }

   @Override
   protected void process(Universe v, float renderTime) {
      super.process(v, renderTime);
      Game.game.platform.processCallbacks();
   }

   @Override
   protected float resize(int width, int height) {
      float length = super.resize(width, height);
      float insetHeight = (float)(Globals.topSafeAreaInset + Globals.bottomSafeAreaInset);
      float viewportHeight = (float)height - insetHeight;
      float viewportLength = viewportHeight / (float)width;
      float paddingY = 0.0F;
      float inputWidth;
      if (viewportLength < Globals.LENGTH) {
         inputWidth = viewportLength / Globals.LENGTH;
      } else {
         inputWidth = 1.0F;
         paddingY = (viewportLength - Globals.LENGTH) / 2.0F;
         viewportLength = Globals.LENGTH;
      }

      this.compositor.inputScale = 1.0F / inputWidth;
      this.compositor.inputOffsetX = -0.5F + inputWidth / 2.0F;
      this.compositor.inputOffsetY = -Globals.LENGTH / 2.0F
         + viewportLength / 2.0F
         - (length - viewportLength) / 2.0F
         + (float)Globals.topSafeAreaInset / (float)width
         + paddingY;
      SaraRenderer.renderer.refreshRenderBuffers();
      return length;
   }

   @Override
   protected void pause() {
      super.pause();
      this.timeElapsed = this.timeElapsed + (System.currentTimeMillis() - this.timeStarted);
   }

   @Override
   protected void resume() {
      super.resume();
      this.timeStarted = System.currentTimeMillis();
   }

   public static class EvalTrigger implements Grid.Trigger {
      static final String TAG = "EvalTrigger";
      public final String eval;

      public EvalTrigger(String eval) {
         this.eval = eval;
      }

      @Override
      public boolean trigger(String name) {
         try {
            return (Boolean)Globals.grid.interpreter.eval(this.eval);
         } catch (Throwable var3) {
            return false;
         }
      }
   }

   public static class ScheduledRunnable {
      public final Runnable runnable;
      public final float tDelay;
      private float tTriggerScheduled = -1.0F;

      public ScheduledRunnable(Runnable runnable, float tDelay) {
         this.runnable = runnable;
         this.tDelay = tDelay;
      }
   }

   public class ScreenCompositor extends Entity.Group {
      public final OrthographicCamera camera = new OrthographicCamera(1.0F, Globals.LENGTH);
      public float inputOffsetX;
      public float inputOffsetY;
      public float inputScale;

      private ScreenCompositor() {
         super(true, true, true);
         this.camera.position.set(0.5F, Globals.LENGTH / 2.0F, 0.0F);
         this.camera.update();
      }

      @Override
      protected void render(Universe v, float r, float renderTime) {
         super.render(v, r, renderTime);
         Matrices.camera = this.camera;
         UIElement.Viewport viewport = null;

         while ((viewport = this.iterate(viewport, UIElement.Viewport.class, false, null)) != null) {
            if (viewport.metrics == null) {
               viewport.metrics = new UIElement.Metrics();
            }

            viewport.metrics.clear();
            if (!Grid.this.screen.isInFullscreen()) {
               viewport.metrics.offsetInput(this.inputOffsetX, this.inputOffsetY).scaleInput(this.inputScale, this.inputScale);
            } else {
               viewport.metrics.offsetInput(0.0F, this.inputOffsetY).scaleInput(0.0F, this.inputScale);
            }
         }
      }
   }

   public interface Trigger {
      boolean trigger(String var1);
   }
}
