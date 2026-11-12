package game27.gb;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Application.ApplicationType;
import game27.Globals;
import game27.MainMenu;
import game27.renderer.SaraRenderer;
import sengine.animation.Animation;
import sengine.animation.ColorAnim;
import sengine.animation.CompoundAnim;
import sengine.animation.FadeAnim;
import sengine.animation.NullAnim;
import sengine.animation.RotateAnim;
import sengine.animation.ScaleAnim;
import sengine.animation.SequenceAnim;
import sengine.calc.ConstantGraph;
import sengine.calc.LinearGraph;
import sengine.calc.QuadraticGraph;
import sengine.calc.Range;
import sengine.calc.SetRandomizedSelector;
import sengine.calc.SineGraph;
import sengine.calc.VibrationGraph;
import sengine.graphics2d.Font;
import sengine.graphics2d.PatchedSprite;
import sengine.graphics2d.Sprite;
import sengine.graphics2d.Text;
import sengine.materials.ColorAttribute;
import sengine.ui.Clickable;
import sengine.ui.StaticSprite;
import sengine.ui.TextBox;
import sengine.ui.UIElement;
import sengine.utils.LoadingMenu;

public class GBMainMenu {
   // Textos de UI del menu que no viven en el .fs: se eligen en tiempo de
   // construccion segun el idioma activo (Globals.contentPrefix ya esta fijado
   // por Grid antes de crear MainMenu).
   private static boolean es() {
      return Globals.contentPrefix != null
         && Globals.contentPrefix.equals(Globals.CONTENT_PREFIX_ES_LATAM);
   }

   private static String L(String en, String es) {
      return es() ? es : en;
   }

   public static Animation startAnim(float tDelay) {
      return new SequenceAnim(
         new ScaleAnim(tDelay),
         new CompoundAnim(
            0.15F,
            new ScaleAnim(1.0F, new QuadraticGraph(0.8F, 1.0F, true)),
            new FadeAnim(1.0F, QuadraticGraph.zeroToOneInverted),
            new FadeAnim(1.0F, QuadraticGraph.zeroToOneInverted, 1)
         )
      );
   }

   public GBMainMenu(MainMenu menu) {
      MainMenu.Internal s = new MainMenu.Internal();
      Font volumeFont = new Font("opensans-light.ttf", 48, -218959105);
      Font headphonesFont = new Font("opensans-regular.ttf", 48, -218959105);
      Font noticeFont = new Font("opensans-semibold.ttf", 48, -1);
      Font warningFont = new Font("opensans-regular.ttf", 48, -103);
      Font loadingFont = new Font("opensans-light.ttf", 32, -1);
      Font copyrightFont = new Font("opensans-light.ttf", 32, -205);
      Font helpButtonFont = new Font("opensans-semibold.ttf", 32, -188);
      Font noticeZHCNFont = new Font("notosans-regular.otf", 48, -1);
      Font dialogFont = new Font("opensans-regular.ttf", 48, 255);
      Font dialogButtonFont = new Font("opensans-semibold.ttf", 48, 1179011583);
      new Font("opensans-bold.ttf", 48, -1).color("MAIN_GAMEPLUS", -585255681);
      int pressedColor = -1431655681;
      Animation pressedAnim = new ColorAnim(pressedColor);
      Animation releasedAnim = new SequenceAnim(
         new NullAnim(0.04F), new ColorAnim(0.08F, pressedColor, true), new NullAnim(0.04F), new ColorAnim(0.03F, pressedColor, true)
      );
      Animation titleHideAnim = new CompoundAnim(0.5F, new FadeAnim(0.5F, QuadraticGraph.oneToZero), new FadeAnim(0.5F, QuadraticGraph.oneToZero, 1));
      s.window = new UIElement.Group();
      float windowY = -0.1F;
      s.screenGroup = new UIElement.Group().viewport(s.window);
      Sprite sprite = new Sprite(Globals.LENGTH, SaraRenderer.renderer.screenNoiseMaterial);
      ColorAttribute.of(sprite).set(572662527);
      new StaticSprite().viewport(s.screenGroup).visual(sprite, 0).attach();
      sprite = new Sprite(0.157F, SaraRenderer.renderer.coloredMaterial);
      ColorAttribute.of(sprite).set(33686271);
      new StaticSprite().viewport(s.screenGroup).metrics(new UIElement.Metrics().anchorBottom()).visual(sprite, 0).attach();
      s.screen = new StaticSprite()
         .viewport(s.screenGroup)
         .metrics(new UIElement.Metrics().scale(0.98044443F).anchorBottom().move(0.0F, 0.23066667F + windowY))
         .visual(Sprite.load("menu/screen.png"), 1)
         .animation(null, new FadeAnim(1.0F, new VibrationGraph(1.0F, 0.2F, 0.8F)), null)
         .attach();
      s.baseGlow = new StaticSprite()
         .viewport(s.screenGroup)
         .metrics(new UIElement.Metrics().scale(1.0F).anchorBottom().move(0.0F, 0.25644445F + windowY))
         .visual(Sprite.load("menu/glow-base.png"), 0)
         .attach();
      s.fullGlow = new StaticSprite()
         .viewport(s.screenGroup)
         .metrics(new UIElement.Metrics().scale(1.0F).scale(1.0F, 1.2F).anchorBottom().move(0.0F, 0.25644445F + windowY))
         .visual(Sprite.load("menu/glow-full.png"), 0)
         .animation(null, new CompoundAnim(20.0F, new FadeAnim(1.0F, new SineGraph(1.0F, 5.0F, 0.0F, 0.1F, 0.9F))), null)
         .attach();
      ConstantGraph lowGraph = new ConstantGraph(0.9F);
      ConstantGraph veryLowGraph = new ConstantGraph(0.6F);
      s.fullGlow
         .windowAnimation(
            new SequenceAnim(
                  new FadeAnim(1.4F, ConstantGraph.one),
                  new FadeAnim(0.8F, lowGraph),
                  new FadeAnim(3.4F, ConstantGraph.one),
                  new FadeAnim(1.2F, lowGraph),
                  new FadeAnim(0.9F, ConstantGraph.one),
                  new FadeAnim(0.6F, veryLowGraph),
                  new FadeAnim(2.6F, ConstantGraph.one),
                  new FadeAnim(1.6F, lowGraph),
                  new FadeAnim(4.2F, ConstantGraph.one),
                  new FadeAnim(0.4F, veryLowGraph)
               )
               .loopAndReset(),
            true,
            true
         );
      sprite = new Sprite(Globals.LENGTH, SaraRenderer.renderer.coloredMaterial);
      ColorAttribute.of(sprite).set(255).alpha(0.6F);
      s.offShadow = new StaticSprite()
         .viewport(s.window)
         .visual(sprite, 21)
         .animation(
            new SequenceAnim(
               new ColorAnim(0.05F, 170, false),
               new ColorAnim(0.07F, 68, false),
               new ColorAnim(0.025F, 255, false),
               new ColorAnim(0.025F, 34, false),
               new ColorAnim(0.3F, null, new QuadraticGraph(1.0F, 0.0F, false), false)
            ),
            new FadeAnim(4.1F, ConstantGraph.zero),
            new SequenceAnim(
               new ColorAnim(0.1F, 68, false),
               new ColorAnim(0.05F, 0, false),
               new ColorAnim(0.1F, 170, false),
               new ColorAnim(0.07F, 0, false),
               new ColorAnim(0.75F, 255, false)
            )
         );
      s.particle = new MainMenu.ParticleType();
      s.particle.mats = new SetRandomizedSelector<>(Sprite.load("menu/particle1.png"));
      s.particle.target = 1;
      s.particle.x = new Range(0.0F, 1.0F);
      s.particle.y = new Range(0.0F, Globals.LENGTH);
      s.particle.scale = new Range(0.9F, 0.3F);
      s.particle.xSpeed = new Range(0.040000003F, 0.020000001F, true);
      s.particle.ySpeed = new Range(0.020000001F, 0.020000001F, true);
      s.particle.rotateSpeed = new Range(8.0F, 4.0F, true);
      s.particle.startAnim = new FadeAnim(2.0F, LinearGraph.zeroToOne);
      s.particle.endAnim = new FadeAnim(2.0F, LinearGraph.oneToZero);
      s.particle.idleAnim = new CompoundAnim(
         10.0F, new ScaleAnim(1.0F, new SineGraph(1.0F, 2.0F, 0.0F, 0.1F, 1.0F)), new FadeAnim(1.0F, new SineGraph(1.0F, 4.0F, 0.0F, 0.05F, 0.15F))
      );
      s.particle.tLifeTime = new Range(6.0F, 4.0F);
      s.numParticles = 10;
      s.title = new StaticSprite()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(1.0F).move(-0.015F, 0.5555556F + windowY))
         .visual(Sprite.load("menu/title.png"), 2)
         .animation(startAnim(1.0F), null, titleHideAnim);
      s.quitButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.33644444F).move(0.0F, -0.36355555F + windowY))
         .visuals(Sprite.load("menu/quit.png"), 2)
         .animation(startAnim(1.8F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.creditsButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.52577776F).move(0.0F, -0.176F + windowY))
         .visuals(Sprite.load("menu/credits.png"), 2)
         .animation(startAnim(1.6F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.newGameButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.44133332F).move(0.0F, 0.010666667F + windowY))
         .visuals(Sprite.load("menu/begin.png"), 2)
         .animation(startAnim(1.4F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.newGamePlusButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.5053333F).move(0.0F, 0.010666667F + windowY))
         .visuals(Sprite.load("menu/beginplus.png"), 2)
         .animation(startAnim(1.4F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.restartButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.56622225F).move(0.0F, 0.010666667F + windowY))
         .visuals(Sprite.load("menu/restart.png"), 2)
         .animation(startAnim(1.4F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.continueButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.62222224F).move(0.0F, 0.17866667F + windowY))
         .visuals(Sprite.load("menu/continue.png"), 2)
         .animation(startAnim(1.2F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.tTitleHideTime = 2.0F;
      s.tNewGameMusicDelay = 6.1F;
      s.newGameWarningView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.95F).move(0.0F, 0.0F))
         .text(new Text().font(noticeFont, 3).position(1.0F, -14.0F).text(L("Are you sure you\nwant to restart ?\nYou will lose your\ncurrent progress.", "¿Seguro que quieres\nreiniciar?\nPerderás tu\nprogreso actual.")))
         .animation(startAnim(1.0F), null, titleHideAnim);
      s.newGameYesButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.27911112F).move(0.2897778F, -0.40266666F))
         .visuals(Sprite.load("menu/yes.png"), 2)
         .animation(startAnim(1.2F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.newGameNoButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.26577777F).move(-0.28266665F, -0.40266666F))
         .visuals(Sprite.load("menu/no.png"), 2)
         .animation(startAnim(1.4F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.newGamePlusTextView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.95F).move(0.0F, 0.15F))
         .text(
            new Text()
               .font(noticeFont, 3)
               .position(1.0F, -14.0F)
               .text(
                  "You can now enable\n[MAIN_GAMEPLUS]BEGIN+[] mode\n\nIn this mode, text speed\nwill be increased\ndramatically\n\nDo you wish to\nenable this mode?"
               )
         )
         .animation(startAnim(1.0F), null, titleHideAnim);
      s.newGamePlusYesButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.27911112F).move(0.2897778F, -0.40266666F))
         .visuals(Sprite.load("menu/yes.png"), 2)
         .animation(startAnim(1.4F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.newGamePlusNoButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.26577777F).move(-0.28266665F, -0.40266666F))
         .visuals(Sprite.load("menu/no.png"), 2)
         .animation(startAnim(1.4F), null, pressedAnim, releasedAnim, titleHideAnim);
      sprite = Sprite.load("menu/discord.png").instantiate();
      ColorAttribute.of(sprite).set(1549556991);
      s.discordButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.055555556F).anchorTop().anchorRight().move(-0.295F, -0.025F))
         .visuals(sprite, 2)
         .animation(startAnim(1.8F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(5.0F, 2.0F, 0.5F, 2.0F);
      s.discordNewAnim = new SequenceAnim(new ColorAnim(0.2F, 10.0F, 10.0F, 10.0F, 1.0F, true), new NullAnim(0.2F));
      s.helpButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.055555556F).anchorTop().anchorRight().move(-0.195F, -0.025F))
         .visuals(Sprite.load("menu/help.png"), 2)
         .animation(startAnim(1.8F), null, pressedAnim, releasedAnim, titleHideAnim)
         .text(new Text().font(helpButtonFont, 3).position(2.2F, 0.0F, 2.5F, 0.3F, 0.0F).text("OPTIONS"))
         .inputPadding(0.5F, 2.0F, 10.0F, 2.0F);
      s.helpTitleView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.7F).anchorLeft().move(0.04F, 0.65F))
         .text(new Text().font(noticeFont, 3).position(1.0F, -12.0F).centerLeft())
         .autoLengthText("Talk to us if you need\nhelp or find any issues\nwith SIMULACRA")
         .animation(startAnim(1.0F), null, titleHideAnim);
      s.helpDiscordButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.2962963F).anchorRight().move(0.0F, 0.7F))
         .visuals(Sprite.load("menu/discord-button.png"), 2)
         .animation(startAnim(1.2F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.subtitleLabelView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4F).move(0.0F, 0.42F))
         .text(new Text().font(noticeFont, 3).position(0.2F, -6.0F).centerLeft().text(L("Subtitles", "Subtítulos")))
         .animation(startAnim(1.4F), null, titleHideAnim);
      s.subtitleButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.07F).move(0.2F, 0.42F))
         .visuals(Sprite.load("apps/chats/circle-empty.png"), 2)
         .animation(startAnim(1.4F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(10.0F, 1.0F, 10.0F, 1.0F);
      sprite = Sprite.load("system/circle.png").instantiate();
      ColorAttribute.of(sprite).set(-16711681);
      s.subtitleEnabledView = new StaticSprite().viewport(s.subtitleButton).metrics(new UIElement.Metrics().scale(0.4F)).visual(sprite, 2);
      s.hqVideosLabelView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4F).move(0.0F, 0.27F))
         .text(new Text().font(noticeFont, 3).position(0.2F, -6.0F).centerLeft().text(L("HD Videos", "Videos HD")))
         .animation(startAnim(1.4F), null, titleHideAnim);
      s.hqVideosButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.07F).move(0.2F, 0.27F))
         .visuals(Sprite.load("apps/chats/circle-empty.png"), 2)
         .animation(startAnim(1.4F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(10.0F, 1.0F, 10.0F, 1.0F);
      s.hqVideosEnabledView = s.subtitleEnabledView.instantiate().viewport(s.hqVideosButton);
      s.helpLanguageTitleView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.95F).move(0.0F, 0.1F))
         .text(new Text().font(noticeFont, 3).position(1.0F, -14.0F).text(L("Language Selection", "Selección de idioma")))
         .animation(startAnim(1.6F), null, titleHideAnim);
      s.helpLanguageEnglishLabel = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4F).move(0.0F, -0.1F))
         .text(new Text().font(noticeFont, 3).position(0.2F, -6.0F).centerLeft().text("English"))
         .animation(startAnim(1.8F), null, titleHideAnim);
      s.helpLanguageEnglishButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.07F).move(0.2F, -0.1F))
         .visuals(Sprite.load("apps/chats/circle-empty.png"), 2)
         .animation(startAnim(1.8F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(10.0F, 1.0F, 10.0F, 1.0F);
      s.helpLanguageEnglishEnabledView = s.subtitleEnabledView.instantiate().viewport(s.helpLanguageEnglishButton);
      s.helpLanguageChineseLabel = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4F).move(0.0F, -0.25F))
         .text(new Text().font(noticeZHCNFont, 3).position(0.2F, -6.0F).centerLeft().text("简体中文"))
         .animation(startAnim(1.8F), null, titleHideAnim);
      s.helpLanguageChineseButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.07F).move(0.2F, -0.25F))
         .visuals(Sprite.load("apps/chats/circle-empty.png"), 2)
         .animation(startAnim(1.8F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(10.0F, 1.0F, 10.0F, 1.0F);
      s.helpLanguageChineseEnabledView = s.subtitleEnabledView.instantiate().viewport(s.helpLanguageChineseButton);
      s.helpLanguageSpanishLabel = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4F).move(0.0F, -0.4F))
         .text(new Text().font(noticeFont, 3).position(0.2F, -6.0F).centerLeft().text("Español (Latinoamérica)"))
         .animation(startAnim(1.8F), null, titleHideAnim);
      s.helpLanguageSpanishButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.07F).move(0.2F, -0.4F))
         .visuals(Sprite.load("apps/chats/circle-empty.png"), 2)
         .animation(startAnim(1.8F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(10.0F, 1.0F, 10.0F, 1.0F);
      s.helpLanguageSpanishEnabledView = s.subtitleEnabledView.instantiate().viewport(s.helpLanguageSpanishButton);
      s.helpLanguageSaveWarningTitle = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.95F).move(0.0F, -0.55F))
         .text(new Text().font(warningFont, 3).position(1.0F, -26.0F).text(L("(Saves are stored separately for each language.)", "(Las partidas se guardan por separado para cada idioma.)")))
         .animation(startAnim(2.0F), null, titleHideAnim);
      s.languageEnglishTitleView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.95F).move(0.0F, 0.3F))
         .text(new Text().font(noticeFont, 3).position(1.0F, -14.0F).text(L("Language Selection", "Selección de idioma")))
         .animation(startAnim(0.2F), null, titleHideAnim);
      s.languageChineseTitleView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.95F).move(0.0F, 0.3F))
         .text(new Text().font(noticeZHCNFont, 3).position(1.0F, -14.0F).text("语言选择"))
         .animation(startAnim(0.2F), null, titleHideAnim);
      s.languageEnglishLabel = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4F).move(0.0F, 0.1F))
         .text(new Text().font(noticeFont, 3).position(0.2F, -6.0F).centerLeft().text("English"))
         .animation(startAnim(0.2F), null, titleHideAnim);
      s.languageEnglishButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.07F).move(0.2F, 0.1F))
         .visuals(Sprite.load("apps/chats/circle-empty.png"), 2)
         .animation(startAnim(0.2F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(10.0F, 1.0F, 10.0F, 1.0F);
      s.languageEnglishEnabledView = s.subtitleEnabledView.instantiate().viewport(s.languageEnglishButton);
      s.languageChineseLabel = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4F).move(0.0F, -0.07F))
         .text(new Text().font(noticeZHCNFont, 3).position(0.2F, -6.0F).centerLeft().text("简体中文"))
         .animation(startAnim(0.2F), null, titleHideAnim);
      s.languageChineseButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.07F).move(0.2F, -0.07F))
         .visuals(Sprite.load("apps/chats/circle-empty.png"), 2)
         .animation(startAnim(0.2F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(10.0F, 1.0F, 10.0F, 1.0F);
      s.languageChineseEnabledView = s.subtitleEnabledView.instantiate().viewport(s.languageChineseButton);
      s.languageSpanishTitleView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.95F).move(0.0F, 0.3F))
         .text(new Text().font(noticeFont, 3).position(1.0F, -14.0F).text("Selección de idioma"))
         .animation(startAnim(0.2F), null, titleHideAnim);
      s.languageSpanishLabel = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4F).move(0.0F, -0.24F))
         .text(new Text().font(noticeFont, 3).position(0.2F, -6.0F).centerLeft().text("Español (Latinoamérica)"))
         .animation(startAnim(0.2F), null, titleHideAnim);
      s.languageSpanishButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.07F).move(0.2F, -0.24F))
         .visuals(Sprite.load("apps/chats/circle-empty.png"), 2)
         .animation(startAnim(0.2F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(10.0F, 1.0F, 10.0F, 1.0F);
      s.languageSpanishEnabledView = s.subtitleEnabledView.instantiate().viewport(s.languageSpanishButton);
      s.languageOkEnglishButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.44133332F).move(0.0F, -0.4F))
         .visuals(Sprite.load("menu/begin.png"), 2)
         .animation(startAnim(0.2F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.languageOkChineseButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.4888889F).move(0.0F, -0.4F))
         .visuals(Sprite.load("zhcn/menu/begin.png"), 2)
         .animation(startAnim(0.2F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.languageOkSpanishButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.44133332F).move(0.0F, -0.4F))
         .visuals(Sprite.load("menu/begin.png"), 2)
         .animation(startAnim(0.2F), null, pressedAnim, releasedAnim, titleHideAnim);
      s.helpBackButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.41111112F).move(0.0F, -0.5F))
         .visuals(Sprite.load("menu/back-button.png"), 2)
         .animation(startAnim(2.2F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(0.5F, 0.0F, 0.5F, 0.2F);
      s.versionView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().anchorBottom())
         .text(new Text().font(copyrightFont, 3).position(0.97F, 0.1F, -23.0F).centerRight().text(Globals.version))
         .animation(startAnim(1.0F), null, titleHideAnim);
      s.loadingView = new TextBox()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().anchorBottom().move(0.0F, 0.35F))
         .text(new Text().font(loadingFont, 3).position(0.1F, -18.0F).text(L("Please Wait", "Espera")))
         .animation(new FadeAnim(3.0F, LinearGraph.zeroToOne), new FadeAnim(1.0F, new SineGraph(1.0F, 1.0F, 0.0F, 0.1F, 0.5F)), null);
      s.tLoadingViewDelay = 2.0F;
      s.headphonesGroup = new UIElement.Group().viewport(s.window);
      sprite = new Sprite(Globals.LENGTH, SaraRenderer.renderer.coloredMaterial);
      ColorAttribute.of(sprite).set(255);
      new StaticSprite().viewport(s.headphonesGroup).visual(sprite, 0).attach();
      new TextBox()
         .viewport(s.headphonesGroup)
         .metrics(new UIElement.Metrics().scale(0.644F).move(0.0F, 0.5222222F))
         .text(new Text().font(volumeFont, 3).position(0.19668737F, 0.0F).text(L("For the best experience\nplease turn on the volume", "Para una mejor experiencia,\nsube el volumen")))
         .attach();
      new StaticSprite()
         .viewport(s.headphonesGroup)
         .metrics(new UIElement.Metrics().scale(0.5751111F).move(0.0F, 0.0F))
         .visual(Sprite.load("menu/headphones.png"), 2)
         .attach();
      new TextBox()
         .viewport(s.headphonesGroup)
         .metrics(new UIElement.Metrics().scale(0.7408889F).move(0.0F, -0.53022224F))
         .text(new Text().font(headphonesFont, 3).position(0.08578284F, 0.0F).text(L("Headphones recommended", "Se recomiendan audífonos")))
         .attach();
      if (Gdx.app.getType() == ApplicationType.Android) {
         s.tHeadphonesTime = 2.5F;
      } else if (Gdx.app.getType() == ApplicationType.iOS) {
         s.tHeadphonesTime = 0.5F;
      } else {
         s.tHeadphonesTime = 3.0F;
      }

      s.kaiganGroup = new UIElement.Group().viewport(s.window);
      new StaticSprite()
         .viewport(s.kaiganGroup)
         .metrics(new UIElement.Metrics().scale(0.6804444F).move(0.0F, 0.052444443F))
         .visual(Sprite.load("menu/kaigan.png"), 2)
         .attach();
      s.tKaiganTime = 5.0F;
      s.themeMusic = "sounds/theme.ogg";
      s.tThemeTime = 2.5F;
      s.tThemeFadeOutTime = 3.0F;
      s.tLeaveTitleDelay = 1.2F;
      s.loadingMenu = new LoadingMenu(null, null, 0.0F, 0.0F, 0.0F, 1.0F, true, false);
      Sprite headerAndroidSprite = Sprite.load("platform/android/dialog-header.png");
      Sprite buttonAndroidSprite = Sprite.load("platform/android/signin.png");
      Sprite headerAppleSprite = Sprite.load("platform/apple/dialog-header.png");
      Sprite buttonAppleSprite = Sprite.load("platform/apple/signin.png");
      Sprite headerSprite;
      Sprite buttonSprite;
      if (Gdx.app.getType() == ApplicationType.Android) {
         headerSprite = headerAndroidSprite;
         buttonSprite = buttonAndroidSprite;
      } else {
         headerSprite = headerAppleSprite;
         buttonSprite = buttonAppleSprite;
      }

      sprite = Sprite.load("platform/android/playservices.png").instantiate();
      ColorAttribute.of(sprite).set(-871665665);
      s.googlePlayButton = new Clickable()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().anchorTop().anchorLeft().scale(0.11F).move(0.02F, -0.02F))
         .visuals(sprite, 2)
         .animation(startAnim(1.8F), null, pressedAnim, releasedAnim, titleHideAnim)
         .inputPadding(0.1F, 0.1F, 0.1F, 0.1F);
      sprite = new Sprite(Globals.LENGTH, SaraRenderer.renderer.coloredMaterial);
      ColorAttribute.of(sprite).set(255).alpha(0.5F);
      s.googlePlayBg = new StaticSprite()
         .viewport(s.window)
         .visual(sprite, 6)
         .animation(new FadeAnim(1.0F, LinearGraph.zeroToOne), null, new FadeAnim(1.0F, LinearGraph.oneToZero))
         .passThroughInput(false);
      sprite = Sprite.load("system/loading-circle.png").instantiate();
      ColorAttribute.of(sprite).set(-871665665);
      s.googlePlayLoadingView = new StaticSprite()
         .viewport(s.googlePlayBg)
         .metrics(new UIElement.Metrics().scale(0.18F))
         .visual(sprite, 2)
         .animation(new FadeAnim(1.0F, LinearGraph.zeroToOne), new RotateAnim(1.0F, new LinearGraph(0.0F, 360.0F)), new FadeAnim(1.0F, LinearGraph.oneToZero));
      sprite = new Sprite(0.7645212F, SaraRenderer.renderer.coloredMaterial);
      s.googlePlayPrompt = new StaticSprite()
         .viewport(s.window)
         .metrics(new UIElement.Metrics().scale(0.84933335F))
         .visual(sprite, 8)
         .animation(new ScaleAnim(0.15F, QuadraticGraph.zeroToOneInverted), null, new ScaleAnim(0.15F, QuadraticGraph.oneToZero));
      StaticSprite headerView = new StaticSprite()
         .viewport(s.googlePlayPrompt)
         .metrics(new UIElement.Metrics().anchor(0.0F, 0.5F))
         .visual(headerSprite, 8)
         .attach();
      new StaticSprite()
         .viewport(headerView)
         .metrics(new UIElement.Metrics().scale(0.18F))
         .visual(Sprite.load("platform/android/playservices.png"), 8)
         .attach();
      new TextBox()
         .viewport(s.googlePlayPrompt)
         .metrics(new UIElement.Metrics().scale(0.71323913F).move(0.0F, 0.1F))
         .text(new Text().font(dialogFont, 9).position(0.1841526F, 0.0F).text(L("Login to enable cloud\nsave and achievements", "Inicia sesión para activar el guardado\nen la nube y los logros")))
         .attach();
      s.googlePlayPromptLoginButton = new Clickable()
         .viewport(s.googlePlayPrompt)
         .metrics(new UIElement.Metrics().scale(0.7106227F).move(0.0F, -0.135F))
         .visuals(buttonSprite, 8)
         .animation(null, null, pressedAnim, releasedAnim, null)
         .inputPadding(1.0F, 0.2F, 1.0F, 0.1F)
         .attach();
      PatchedSprite patch = PatchedSprite.create("system/rounded.png", 0.1789639F, 0.02F, 0.02F, 0.0F, 0.02F);
      s.googlePlayPromptContinueButton = new Clickable()
         .viewport(s.googlePlayPrompt)
         .metrics(new UIElement.Metrics().anchor(0.0F, -0.5F))
         .visuals(patch, 8)
         .text(new Text().font(dialogButtonFont, 9).position(patch.length, -17.0F).text("SKIP"))
         .animation(null, null, pressedAnim, releasedAnim, null)
         .inputPadding(1.0F, 0.05F, 1.0F, 0.1F)
         .attach();
      sprite = new Sprite(0.004166667F, SaraRenderer.renderer.coloredMaterial);
      ColorAttribute.of(sprite).set(-1094529793);
      new StaticSprite().viewport(s.googlePlayPromptContinueButton).metrics(new UIElement.Metrics().anchorTop()).visual(sprite, 11).attach();
      menu.internal(s);
   }
}
