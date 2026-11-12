package game27;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Application.ApplicationType;
import com.badlogic.gdx.math.Matrix4;
import game27.gb.GBMainMenu;
import sengine.Entity;
import sengine.Sys;
import sengine.animation.Animation;
import sengine.audio.Audio;
import sengine.audio.Stream;
import sengine.calc.Range;
import sengine.calc.SetRandomizedSelector;
import sengine.graphics2d.Matrices;
import sengine.graphics2d.Mesh;
import sengine.graphics2d.Sprite;
import sengine.ui.Clickable;
import sengine.ui.Menu;
import sengine.ui.OnClick;
import sengine.ui.StaticSprite;
import sengine.ui.TextBox;
import sengine.ui.UIElement;
import sengine.utils.Builder;
import sengine.utils.LoadingMenu;

public class MainMenu extends Menu<Grid> implements OnClick<Grid> {
   private final Builder<Object> builder;
   private MainMenu.Internal s;
   private final Entity.Group particleGroup;
   private float tHeadphonesEndScheduled = Float.MAX_VALUE;
   private float tKaiganEndScheduled = Float.MAX_VALUE;
   private float tThemeScheduled = Float.MAX_VALUE;
   private float tLoadingViewScheduled = Float.MAX_VALUE;
   private boolean showingCredits = false;
   private boolean doneLoading = false;
   private boolean isFoundSave = false;
   private boolean allowNewGamePlus = false;
   private boolean isQueuedOpenAchievements = false;
   private boolean isQueuedStartGame = false;
   private boolean isLoadedSaves = false;
   private boolean isShowingLanguageSelect = false;
   private String currentContentPrefix;

   private void showGooglePrompt() {
      this.s.googlePlayBg.attach();
      this.s.googlePlayPrompt.attach();
      this.s.googlePlayLoadingView.detach();
   }

   private void hideGooglePrompt() {
      this.s.googlePlayBg.detachWithAnim();
      this.s.googlePlayPrompt.detachWithAnim();
      this.s.googlePlayLoadingView.detachWithAnim();
   }

   private void showTitleMenu() {
      if (Gdx.app.getType() == ApplicationType.Desktop) {
         this.s.quitButton.attach();
      }

      if (Game.game.platform.showGameCenter()) {
         this.s.googlePlayButton.attach();
      }

      this.s.creditsButton.attach();
      this.s.title.attach();
      if (this.isFoundSave) {
         if (this.allowNewGamePlus) {
            this.s.newGamePlusButton.attach();
            this.s.restartButton.detach();
         } else {
            this.s.restartButton.attach();
            this.s.newGamePlusButton.detach();
         }

         this.s.continueButton.attach();
         this.s.newGameButton.detach();
      } else {
         if (this.allowNewGamePlus) {
            this.s.newGamePlusButton.attach();
            this.s.newGameButton.detach();
         } else {
            this.s.newGameButton.attach();
            this.s.newGamePlusButton.detach();
         }

         this.s.continueButton.detach();
         this.s.restartButton.detach();
      }

      this.s.versionView.attach();
      this.s.helpButton.attach();
      this.s.discordButton.attach();
      if (Gdx.app.getPreferences("preferences").getBoolean("STATE_HAS_DISCORD_OPENED", false)) {
         this.s.discordButton.windowAnimation(null, false, false);
      } else {
         this.s.discordButton.windowAnimation(this.s.discordNewAnim.loopAndReset(), true, true);
      }
   }

   private void hideTitleMenu() {
      this.s.title.detachWithAnim();
      this.s.continueButton.detachWithAnim();
      this.s.restartButton.detachWithAnim();
      this.s.newGameButton.detachWithAnim();
      this.s.newGamePlusButton.detachWithAnim();
      this.s.creditsButton.detachWithAnim();
      this.s.quitButton.detachWithAnim();
      this.s.versionView.detachWithAnim();
      this.s.helpButton.detachWithAnim();
      this.s.discordButton.detachWithAnim();
      this.s.googlePlayButton.detachWithAnim();
   }

   private void hideLanguageMenu() {
      this.s.languageEnglishTitleView.detachWithAnim();
      this.s.languageChineseTitleView.detachWithAnim();
      this.s.languageSpanishTitleView.detachWithAnim();
      this.s.languageEnglishLabel.detachWithAnim();
      this.s.languageEnglishButton.detachWithAnim();
      this.s.languageChineseLabel.detachWithAnim();
      this.s.languageChineseButton.detachWithAnim();
      this.s.languageSpanishLabel.detachWithAnim();
      this.s.languageSpanishButton.detachWithAnim();
      this.s.languageOkEnglishButton.detachWithAnim();
      this.s.languageOkChineseButton.detachWithAnim();
      this.s.languageOkSpanishButton.detachWithAnim();
   }

   private void showLanguageMenu(boolean showNext) {
      boolean isEnglish = Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_EN_US);
      boolean isSpanish = Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_ES_LATAM);
      this.s.languageEnglishLabel.attach();
      this.s.languageEnglishButton.attach();
      this.s.languageChineseLabel.attach();
      this.s.languageChineseButton.attach();
      this.s.languageSpanishLabel.attach();
      this.s.languageSpanishButton.attach();
      this.s.languageEnglishTitleView.attach();
      this.s.languageChineseTitleView.detach();
      this.s.languageSpanishTitleView.detach();
      if (showNext) {
         if (isEnglish) {
            this.s.languageEnglishEnabledView.attach();
         } else {
            this.s.languageEnglishEnabledView.detach();
         }

         if (isSpanish) {
            this.s.languageSpanishEnabledView.attach();
         } else {
            this.s.languageSpanishEnabledView.detach();
         }

         if (!isEnglish && !isSpanish) {
            this.s.languageChineseEnabledView.attach();
         } else {
            this.s.languageChineseEnabledView.detach();
         }

         if (isEnglish) {
            this.s.languageOkEnglishButton.attach();
            this.s.languageOkChineseButton.detach();
            this.s.languageOkSpanishButton.detach();
         } else if (isSpanish) {
            this.s.languageOkEnglishButton.detach();
            this.s.languageOkChineseButton.detach();
            this.s.languageOkSpanishButton.attach();
         } else {
            this.s.languageOkEnglishButton.detach();
            this.s.languageOkChineseButton.attach();
            this.s.languageOkSpanishButton.detach();
         }
      } else {
         this.s.languageEnglishEnabledView.detach();
         this.s.languageChineseEnabledView.detach();
         this.s.languageSpanishEnabledView.detach();
         this.s.languageOkEnglishButton.detach();
         this.s.languageOkChineseButton.detach();
         this.s.languageOkSpanishButton.detach();
      }
   }

   private void refreshLanguageStatus() {
      Globals.contentPrefix = Gdx.app.getPreferences("preferences").getString("STATE_LANGUAGE", "en-us://");
      boolean isEnglish = Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_EN_US);
      boolean isSpanish = Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_ES_LATAM);
      if (isEnglish) {
         this.s.helpLanguageEnglishEnabledView.attach();
         this.s.languageEnglishEnabledView.attach();
         this.s.helpLanguageChineseEnabledView.detachWithAnim();
         this.s.languageChineseEnabledView.detachWithAnim();
      } else if (isSpanish) {
         this.s.helpLanguageSpanishEnabledView.attach();
         this.s.languageSpanishEnabledView.attach();
         this.s.helpLanguageEnglishEnabledView.detachWithAnim();
         this.s.languageEnglishEnabledView.detachWithAnim();
         this.s.helpLanguageChineseEnabledView.detachWithAnim();
         this.s.languageChineseEnabledView.detachWithAnim();
      } else {
         this.s.helpLanguageChineseEnabledView.attach();
         this.s.languageChineseEnabledView.attach();
         this.s.helpLanguageEnglishEnabledView.detachWithAnim();
         this.s.languageEnglishEnabledView.detachWithAnim();
         this.s.helpLanguageSpanishEnabledView.detachWithAnim();
         this.s.languageSpanishEnabledView.detachWithAnim();
         Gdx.app.getPreferences("preferences").putBoolean("STATE_SUBTITLE_ENABLED", true).flush();
         this.refreshSubtitleStatus();
      }
   }

   private void showHelpMenu() {
      this.s.helpTitleView.attach();
      this.s.helpDiscordButton.attach();
      this.s.helpBackButton.attach();
      this.s.subtitleLabelView.attach();
      this.s.subtitleButton.attach();
      this.s.hqVideosLabelView.attach();
      this.s.hqVideosButton.attach();
      this.s.helpLanguageTitleView.attach();
      this.s.helpLanguageEnglishLabel.attach();
      this.s.helpLanguageEnglishButton.attach();
      this.s.helpLanguageChineseLabel.attach();
      this.s.helpLanguageChineseButton.attach();
      this.s.helpLanguageSpanishLabel.attach();
      this.s.helpLanguageSpanishButton.attach();
      this.s.helpLanguageSaveWarningTitle.attach();
      this.refreshSubtitleStatus();
      this.refreshHighQualityVideosStatus();
   }

   private void refreshSubtitleStatus() {
      boolean showSubtitles = Gdx.app.getPreferences("preferences").getBoolean("STATE_SUBTITLE_ENABLED", false);
      if (showSubtitles) {
         this.s.subtitleEnabledView.attach();
      } else {
         this.s.subtitleEnabledView.detach();
      }
   }

   private void refreshHighQualityVideosStatus() {
      Globals.r_highQuality = Gdx.app.getPreferences("preferences").getBoolean("STATE_HQ_VIDEOS_ENABLED", true);
      if (Globals.r_highQuality) {
         this.s.hqVideosEnabledView.attach();
      } else {
         this.s.hqVideosEnabledView.detach();
      }
   }

   private void hideHelpMenu() {
      this.s.helpTitleView.detachWithAnim();
      this.s.helpDiscordButton.detachWithAnim();
      this.s.subtitleLabelView.detachWithAnim();
      this.s.subtitleButton.detachWithAnim();
      this.s.hqVideosLabelView.detachWithAnim();
      this.s.hqVideosButton.detachWithAnim();
      this.s.helpLanguageTitleView.detachWithAnim();
      this.s.helpLanguageEnglishLabel.detachWithAnim();
      this.s.helpLanguageEnglishButton.detachWithAnim();
      this.s.helpLanguageChineseLabel.detachWithAnim();
      this.s.helpLanguageChineseButton.detachWithAnim();
      this.s.helpLanguageSpanishLabel.detachWithAnim();
      this.s.helpLanguageSpanishButton.detachWithAnim();
      this.s.helpLanguageSaveWarningTitle.detachWithAnim();
      this.s.helpBackButton.detachWithAnim();
   }

   private void showNewGameWarning() {
      this.s.newGameYesButton.attach();
      this.s.newGameNoButton.attach();
      this.s.newGameWarningView.attach();
   }

   private void hideNewGameWarning() {
      this.s.newGameYesButton.detachWithAnim();
      this.s.newGameNoButton.detachWithAnim();
      this.s.newGameWarningView.detachWithAnim();
   }

   private void showNewGamePlusWarning() {
      this.s.newGamePlusYesButton.attach();
      this.s.newGamePlusNoButton.attach();
      this.s.newGamePlusTextView.attach();
   }

   private void hideNewGamePlusWarning() {
      this.s.newGamePlusYesButton.detachWithAnim();
      this.s.newGamePlusNoButton.detachWithAnim();
      this.s.newGamePlusTextView.detachWithAnim();
   }

   private void startGameLoad() {
      this.hideTitleMenu();
      this.tLoadingViewScheduled = this.getRenderTime() + this.s.tLoadingViewDelay;
      boolean isNewGamePlus = Gdx.app.getPreferences("preferences").getBoolean("STATE_GAMEPLUS_MODE", false);
      if (isNewGamePlus) {
         Globals.allowSkipFreakoutVideo = true;
         Globals.a1_taylor_impatient_time = 5.0F;
         Globals.tKeyboardAnimationSpeedMultiplier = 0.3F;
         Globals.tChatTimingMultiplier = 0.1F;
         Globals.restoreWinDelay = 1.5F;
         Globals.a2_murilo_call_delay = 10.0F;
         Globals.a2_murilo_call_delay_from_save = 10.0F;
         Globals.a3_murilo_call_delay = 10.0F;
         Globals.a3_murilo_call_delay_from_save = 10.0F;
         Globals.a3_murilo_ashleyreported_call_delay = 10.0F;
      } else {
         Globals.allowSkipFreakoutVideo = false;
         Globals.a1_taylor_impatient_time = 20.0F;
         Globals.tKeyboardAnimationSpeedMultiplier = 1.0F;
         Globals.tChatTimingMultiplier = 0.9F;
         Globals.restoreWinDelay = 3.0F;
         Globals.a2_murilo_call_delay = 180.0F;
         Globals.a2_murilo_call_delay_from_save = 20.0F;
         Globals.a3_murilo_call_delay = 120.0F;
         Globals.a3_murilo_call_delay_from_save = 20.0F;
         Globals.a3_murilo_ashleyreported_call_delay = 120.0F;
      }

      Globals.grid.startLoad(this.s.loadingMenu);
   }

   public void doneLogin(boolean success, boolean savegameFound) {
      this.isLoadedSaves = true;
      this.hideGooglePrompt();
      if (this.isFoundSave != savegameFound) {
         this.isQueuedOpenAchievements = false;
         this.isQueuedStartGame = false;
         this.isFoundSave = savegameFound;
         if (this.s.title.isAttached()) {
            this.showTitleMenu();
         }
      } else if (!success) {
         this.isQueuedOpenAchievements = false;
         this.isQueuedStartGame = false;
      } else {
         if (this.isQueuedOpenAchievements) {
            this.isQueuedOpenAchievements = false;
            Game.game.platform.openGameCenter();
         } else if (this.isQueuedStartGame) {
            this.isQueuedStartGame = false;
            this.startGameLoad();
         }
      }
   }

   void doneLoading() {
      this.doneLoading = true;
      this.s.offShadow.detachWithAnim();
   }

   private void refreshParticles() {
      this.particleGroup.detachChilds(new Entity[0]);

      for (int c = 0; c < this.s.numParticles; c++) {
         MainMenu.Particle p = new MainMenu.Particle(this.s.particle);
         p.startAnim.stop();
         p.attach(this.particleGroup);
      }
   }

   public void internal(MainMenu.Internal internal) {
      if (this.s != null) {
         this.s.window.detach();
      }

      this.s = internal;
      this.s.window.viewport(this.viewport).attach();
      if (this.isAttached()) {
         this.refreshParticles();
      }
   }

   public MainMenu() {
      this.builder = new Builder<>(GBMainMenu.class, this);
      this.builder.build();
      this.particleGroup = new Entity.Group();
      this.particleGroup.attach(this);
   }

   protected void recreate(Grid grid) {
      super.recreate(grid);
      this.builder.start();
      this.refreshParticles();
      this.currentContentPrefix = Globals.contentPrefix;
      this.refreshLanguageStatus();
      this.refreshHighQualityVideosStatus();
      this.isFoundSave = Game.game.platform.existsSaveGame();
      this.allowNewGamePlus = Gdx.app.getPreferences("preferences").getBoolean("STATE_FINISHED_GAME", false);
      Stream.stopAllStreams();
      if (grid.skipIntoMainMenu) {
         this.isLoadedSaves = true;
         this.s.screenGroup.attach();
         this.showTitleMenu();
         this.tThemeScheduled = this.getRenderTime();
      } else {
         this.isLoadedSaves = false;
         this.tHeadphonesEndScheduled = this.getRenderTime() + this.s.tHeadphonesTime;
         this.tKaiganEndScheduled = Float.MAX_VALUE;
         this.s.headphonesGroup.attach();
      }

      this.isQueuedOpenAchievements = false;
      this.isQueuedStartGame = false;
      this.showingCredits = false;
   }

   protected void release(Grid grid) {
      super.release(grid);
      this.builder.stop();
   }

   protected void render(Grid grid, float r, float renderTime) {
      super.render(grid, r, renderTime);
      if (!this.s.offShadow.isAttached() && this.tHeadphonesEndScheduled == Float.MAX_VALUE) {
         if (this.isShowingLanguageSelect) {
            this.s.headphonesGroup.detach();
            this.s.screenGroup.attach();
            this.showLanguageMenu(false);
         } else if (this.tKaiganEndScheduled != Float.MAX_VALUE) {
            this.s.headphonesGroup.detach();
            this.s.kaiganGroup.attach();
            this.s.screenGroup.attach();
         } else {
            if (this.showingCredits) {
               this.s.screenGroup.detach();
               this.detach();
               Globals.grid.creditsMenu.show(new Runnable() {
                  @Override
                  public void run() {
                     Globals.grid.creditsMenu.detach();
                     Globals.grid.skipIntoMainMenu = true;
                     Globals.grid.mainMenu.attach(Globals.grid.compositor);
                  }
               });
               return;
            }

            if (this.doneLoading) {
               this.s.screenGroup.detach();
               this.detach();
               MainMenu.MusicFadeOutEntity fadeOutEntity = new MainMenu.MusicFadeOutEntity(0.0F, this.s.tThemeFadeOutTime);
               fadeOutEntity.attach(grid);
               grid.start();
               return;
            }

            this.s.kaiganGroup.detach();
            this.showTitleMenu();
         }

         this.s.offShadow.attach();
      }

      if (renderTime > this.tHeadphonesEndScheduled && this.isLoadedSaves) {
         this.tHeadphonesEndScheduled = Float.MAX_VALUE;
         this.s.offShadow.attach();
         this.s.offShadow.detachWithAnim();
         boolean isLanguageSet = Gdx.app.getPreferences("preferences").contains("STATE_LANGUAGE");
         if (!isLanguageSet) {
            if (!this.isFoundSave) {
               this.isShowingLanguageSelect = true;
               return;
            }

            Gdx.app.getPreferences("preferences").putString("STATE_LANGUAGE", Globals.contentPrefix).flush();
         }

         this.tKaiganEndScheduled = this.getRenderTime() + this.s.tKaiganTime;
         this.tThemeScheduled = this.getRenderTime() + this.s.tThemeTime;
      }

      if (renderTime > this.tKaiganEndScheduled) {
         this.tKaiganEndScheduled = Float.MAX_VALUE;
         this.s.offShadow.detachWithAnim();
      }

      if (renderTime > this.tThemeScheduled) {
         this.tThemeScheduled = Float.MAX_VALUE;
         Audio.playMusic(this.s.themeMusic, true, 1.0F);
      }

      if (renderTime > this.tLoadingViewScheduled) {
         this.tLoadingViewScheduled = Float.MAX_VALUE;
         this.s.loadingView.attach();
      }
   }

   public void onClick(Grid v, UIElement<?> view, int button) {
      if (view == this.s.continueButton || view == this.s.newGameButton || view == this.s.newGamePlusButton && !this.isFoundSave) {
         if (Game.game.platform.promptGameCenterLogin()) {
            this.isQueuedStartGame = true;
            this.showGooglePrompt();
         } else if (view == this.s.newGamePlusButton && !this.isFoundSave) {
            this.hideTitleMenu();
            this.showNewGamePlusWarning();
         } else {
            this.startGameLoad();
         }
      } else if (view == this.s.restartButton || view == this.s.newGamePlusButton) {
         this.hideTitleMenu();
         this.showNewGameWarning();
      } else if (view == this.s.newGameYesButton) {
         Game.game.platform.deleteSaveGame();
         this.isFoundSave = false;
         this.hideNewGameWarning();
         if (this.allowNewGamePlus) {
            this.showNewGamePlusWarning();
         } else {
            this.startGameLoad();
         }
      } else if (view == this.s.newGameNoButton) {
         this.hideNewGameWarning();
         this.showTitleMenu();
      } else if (view == this.s.newGamePlusYesButton) {
         this.hideNewGamePlusWarning();
         Gdx.app.getPreferences("preferences").putBoolean("STATE_GAMEPLUS_MODE", true).flush();
         this.startGameLoad();
      } else if (view == this.s.newGamePlusNoButton) {
         this.hideNewGamePlusWarning();
         Gdx.app.getPreferences("preferences").putBoolean("STATE_GAMEPLUS_MODE", false).flush();
         this.startGameLoad();
      } else if (view == this.s.creditsButton) {
         this.hideTitleMenu();
         this.showingCredits = true;
         this.s.offShadow.detachWithAnim();
      } else if (view == this.s.quitButton) {
         Game.game.platform.exitGame();
      } else if (view == this.s.googlePlayButton) {
         if (Game.game.platform.promptGameCenterLogin()) {
            this.isQueuedOpenAchievements = true;
            this.showGooglePrompt();
         } else {
            Game.game.platform.openGameCenter();
         }
      } else if (view == this.s.googlePlayPromptLoginButton) {
         this.s.googlePlayPrompt.detachWithAnim();
         this.s.googlePlayLoadingView.attach();
         Game.game.platform.loginGameCenter();
      } else if (view == this.s.googlePlayPromptContinueButton) {
         this.doneLogin(true, this.isFoundSave);
      } else if (view == this.s.helpButton) {
         this.hideTitleMenu();
         this.showHelpMenu();
      } else if (view == this.s.discordButton || view == this.s.helpDiscordButton) {
         Gdx.net.openURI(Globals.helpDiscordURL);
         Gdx.app.getPreferences("preferences").putBoolean("STATE_HAS_DISCORD_OPENED", true).flush();
         this.s.discordButton.windowAnimation(null, false, false);
      } else if (view == this.s.subtitleButton) {
         boolean showSubtitles = Gdx.app.getPreferences("preferences").getBoolean("STATE_SUBTITLE_ENABLED", false);
         Gdx.app.getPreferences("preferences").putBoolean("STATE_SUBTITLE_ENABLED", !showSubtitles).flush();
         this.refreshSubtitleStatus();
      } else if (view == this.s.hqVideosButton) {
         Gdx.app.getPreferences("preferences").putBoolean("STATE_HQ_VIDEOS_ENABLED", !Globals.r_highQuality).flush();
         this.refreshHighQualityVideosStatus();
      } else if (view == this.s.languageEnglishButton) {
         Globals.contentPrefix = Globals.CONTENT_PREFIX_EN_US;
         Gdx.app.getPreferences("preferences").putString("STATE_LANGUAGE", Globals.contentPrefix).flush();
         this.refreshLanguageStatus();
         this.showLanguageMenu(true);
      } else if (view == this.s.languageChineseButton) {
         Globals.contentPrefix = Globals.CONTENT_PREFIX_ZH_CN;
         Gdx.app.getPreferences("preferences").putString("STATE_LANGUAGE", Globals.contentPrefix).flush();
         this.refreshLanguageStatus();
         this.showLanguageMenu(true);
      } else if (view == this.s.languageSpanishButton) {
         Globals.contentPrefix = Globals.CONTENT_PREFIX_ES_LATAM;
         Gdx.app.getPreferences("preferences").putString("STATE_LANGUAGE", Globals.contentPrefix).flush();
         this.refreshLanguageStatus();
         this.showLanguageMenu(true);
      } else if (view == this.s.helpLanguageEnglishButton) {
         Globals.contentPrefix = Globals.CONTENT_PREFIX_EN_US;
         Gdx.app.getPreferences("preferences").putString("STATE_LANGUAGE", Globals.contentPrefix).flush();
         this.refreshLanguageStatus();
      } else if (view == this.s.helpLanguageChineseButton) {
         Globals.contentPrefix = Globals.CONTENT_PREFIX_ZH_CN;
         Gdx.app.getPreferences("preferences").putString("STATE_LANGUAGE", Globals.contentPrefix).flush();
         this.refreshLanguageStatus();
      } else if (view == this.s.helpLanguageSpanishButton) {
         Globals.contentPrefix = Globals.CONTENT_PREFIX_ES_LATAM;
         Gdx.app.getPreferences("preferences").putString("STATE_LANGUAGE", Globals.contentPrefix).flush();
         this.refreshLanguageStatus();
      } else if (view != this.s.languageOkEnglishButton && view != this.s.languageOkChineseButton && view != this.s.languageOkSpanishButton) {
         if (view == this.s.helpBackButton) {
            if (!Globals.contentPrefix.equals(this.currentContentPrefix)) {
               Sys.system.activate(null);
               Gdx.app.postRunnable(new Runnable() {
                  @Override
                  public void run() {
                     Grid grid = new Grid(false);
                     Sys.system.activate(grid);
                     Game.game.platform.prepareSaveGame();
                  }
               });
            }

            this.hideHelpMenu();
            this.showTitleMenu();
         }
      } else {
         this.hideLanguageMenu();
         this.isShowingLanguageSelect = false;
         if (!Globals.contentPrefix.equals(this.currentContentPrefix)) {
            Sys.system.activate(null);
            Gdx.app.postRunnable(new Runnable() {
               @Override
               public void run() {
                  Grid grid = new Grid(false);
                  Sys.system.activate(grid);
                  Game.game.platform.prepareSaveGame();
               }
            });
         }

         this.s.offShadow.attach();
         this.s.offShadow.detachWithAnim();
         this.tKaiganEndScheduled = this.getRenderTime() + this.s.tKaiganTime;
         this.tThemeScheduled = this.getRenderTime() + this.s.tThemeTime;
      }
   }

   protected boolean input(Grid v, int inputType, int key, char character, int scrolledAmount, int pointer, float x, float y, int button) {
      if (inputType == 32 && key == 4) {
         Game.game.platform.exitGame();
         return true;
      } else {
         return false;
      }
   }

   public static class Internal {
      public UIElement<?> window;
      public UIElement<?> screenGroup;
      public StaticSprite offShadow;
      public StaticSprite baseGlow;
      public StaticSprite fullGlow;
      public StaticSprite screen;
      public MainMenu.ParticleType particle;
      public int numParticles;
      public StaticSprite title;
      public Clickable continueButton;
      public Clickable restartButton;
      public Clickable newGameButton;
      public Clickable newGamePlusButton;
      public Clickable creditsButton;
      public Clickable quitButton;
      public TextBox versionView;
      public float tTitleHideTime;
      public float tNewGameMusicDelay;
      public TextBox newGameWarningView;
      public Clickable newGameYesButton;
      public Clickable newGameNoButton;
      public Clickable googlePlayButton;
      public UIElement<?> googlePlayPrompt;
      public UIElement<?> googlePlayBg;
      public StaticSprite googlePlayLoadingView;
      public Clickable googlePlayPromptLoginButton;
      public Clickable googlePlayPromptContinueButton;
      public TextBox newGamePlusTextView;
      public Clickable newGamePlusYesButton;
      public Clickable newGamePlusNoButton;
      public Clickable helpButton;
      public TextBox helpTitleView;
      public Clickable helpDiscordButton;
      public Clickable subtitleButton;
      public UIElement<?> subtitleEnabledView;
      public TextBox subtitleLabelView;
      public Clickable hqVideosButton;
      public UIElement<?> hqVideosEnabledView;
      public TextBox hqVideosLabelView;
      public TextBox helpLanguageTitleView;
      public TextBox helpLanguageEnglishLabel;
      public Clickable helpLanguageEnglishButton;
      public UIElement<?> helpLanguageEnglishEnabledView;
      public TextBox helpLanguageChineseLabel;
      public Clickable helpLanguageChineseButton;
      public UIElement<?> helpLanguageChineseEnabledView;
      public TextBox helpLanguageSpanishLabel;
      public Clickable helpLanguageSpanishButton;
      public UIElement<?> helpLanguageSpanishEnabledView;
      public TextBox helpLanguageSaveWarningTitle;
      public Clickable helpBackButton;
      public TextBox languageEnglishTitleView;
      public TextBox languageChineseTitleView;
      public TextBox languageSpanishTitleView;
      public TextBox languageEnglishLabel;
      public Clickable languageEnglishButton;
      public UIElement<?> languageEnglishEnabledView;
      public TextBox languageChineseLabel;
      public Clickable languageChineseButton;
      public UIElement<?> languageChineseEnabledView;
      public TextBox languageSpanishLabel;
      public Clickable languageSpanishButton;
      public UIElement<?> languageSpanishEnabledView;
      public Clickable languageOkEnglishButton;
      public Clickable languageOkChineseButton;
      public Clickable languageOkSpanishButton;
      public Clickable discordButton;
      public Animation discordNewAnim;
      public UIElement<?> headphonesGroup;
      public float tHeadphonesTime;
      public UIElement<?> kaiganGroup;
      public float tKaiganTime;
      public String themeMusic;
      public float tThemeTime;
      public float tThemeFadeOutTime;
      public UIElement<?> loadingView;
      public float tLoadingViewDelay;
      public LoadingMenu loadingMenu;
      public float tLeaveTitleDelay;
   }

   public static class MusicFadeOutEntity extends Entity<Grid> {
      private final float tFadeOutTime;
      private final float tStartDelay;

      public MusicFadeOutEntity(float tStartDelay, float tFadeOutTime) {
         this.tStartDelay = tStartDelay;
         this.tFadeOutTime = tFadeOutTime;
      }

      protected void render(Grid v, float r, float renderTime) {
         renderTime -= this.tStartDelay;
         if (!(renderTime < 0.0F)) {
            float volume = 1.0F - renderTime / this.tFadeOutTime;
            if (volume <= 0.0F) {
               Audio.stopMusic();
               this.detach();
            } else {
               Audio.setMusicVolume(volume);
            }
         }
      }
   }

   private static class Particle extends Entity<Grid> {
      private final MainMenu.ParticleType type;
      private final Mesh mat;
      private final float scale;
      private final float x;
      private final float y;
      private final float rotate;
      private final float xSpeed;
      private final float ySpeed;
      private final float rotateSpeed;
      private final Animation.Instance startAnim;
      private final Animation.Loop idleAnim;
      private final Animation.Instance endAnim;
      private float tEndScheduled;

      public Particle(MainMenu.ParticleType type) {
         this.type = type;
         this.mat = type.mats.select();
         this.scale = type.scale.generate();
         this.x = type.x.generate();
         this.y = type.y.generate();
         this.rotate = (float)(Math.random() * 360.0);
         this.xSpeed = type.xSpeed.generate();
         this.ySpeed = type.ySpeed.generate();
         this.rotateSpeed = type.rotateSpeed.generate();
         this.startAnim = type.startAnim.startAndReset();
         this.idleAnim = type.idleAnim.loopAndReset();
         this.idleAnim.setProgress((float)Math.random());
         this.endAnim = type.endAnim.start();
         this.tEndScheduled = type.tLifeTime.generate();
      }

      protected void render(Grid v, float r, float renderTime) {
         Matrices.push();
         Matrices.target = this.type.target;
         Matrix4 m = Matrices.model;
         m.translate(this.x + this.xSpeed * renderTime, this.y + this.ySpeed * renderTime, 0.0F);
         m.scale(this.scale, this.scale, this.scale);
         m.rotate(0.0F, 0.0F, -1.0F, this.rotate + this.rotateSpeed * renderTime);
         if (this.startAnim.isActive()) {
            this.startAnim.updateAndApply(this.mat, this.getRenderDeltaTime());
         }

         this.idleAnim.updateAndApply(this.mat, this.getRenderDeltaTime());
         if (this.endAnim.isActive() && !this.endAnim.updateAndApply(this.mat, this.getRenderDeltaTime())) {
            MainMenu.Particle p = new MainMenu.Particle(this.type);
            p.attach(this.getEntityParent());
            this.detach();
         }

         if (renderTime > this.tEndScheduled) {
            this.endAnim.reset();
            this.tEndScheduled = Float.MAX_VALUE;
         }

         this.mat.render();
         Matrices.pop();
      }
   }

   public static class ParticleType {
      public SetRandomizedSelector<Sprite> mats;
      public int target;
      public Range scale;
      public Range x;
      public Range y;
      public Range xSpeed;
      public Range ySpeed;
      public Range rotateSpeed;
      public Animation startAnim;
      public Animation idleAnim;
      public Animation endAnim;
      public Range tLifeTime;
   }
}
