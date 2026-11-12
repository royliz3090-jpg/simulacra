package game27;

// Variante SOLO PARA PRUEBAS en sandbox (sin Steam).
//
// El DesktopMain original llama a SteamAPI.init(); en un entorno sin Steam eso
// lanza "Unable to initialize steam and failed to restart" y el juego no
// arranca. Esta version:
//   - omite por completo Steam (no toca SteamAPI ni steamworks4j),
//   - guarda la partida en un archivo local (Globals.SAVE_FILENAME),
//   - implementa el resto de Game.PlatformInterface igual que el original.
//
// NO se distribuye: sirve para validar que los recursos es-LATAM cargan.
//
// Se compila y se inyecta con tools/build_test_binary.sh.

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Files.FileType;
import com.badlogic.gdx.Graphics.DisplayMode;
import com.badlogic.gdx.backends.lwjgl.LwjglApplication;
import com.badlogic.gdx.backends.lwjgl.LwjglApplicationConfiguration;
import com.badlogic.gdx.backends.lwjgl.LwjglGraphics;
import com.badlogic.gdx.backends.lwjgl.audio.OggInputStream;
import com.badlogic.gdx.utils.StreamUtils;
import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.ShortBuffer;
import java.nio.file.Paths;
import sengine.File;
import sengine.Sys;
import sengine.graphics2d.Fonts;
import sengine.mass.MassFile;
import sengine.mass.io.Input;
import sengine.mass.io.Output;

public class DesktopMain implements Game.PlatformInterface {
   private static final String TAG = "DesktopMain";
   public static DesktopMain main;
   public static int hdpiHeightThreshold = 1000;
   public static int textVoiceSampleRate = 30;
   private boolean userStatsRetrieved = false;
   private final LwjglApplication application;

   public DesktopMain(String... args) {
      main = this;
      String workingPath = Paths.get(".").toAbsolutePath().normalize().toString();
      System.out.println("[TEST] no-Steam workingPath=" + workingPath);
      LwjglApplicationConfiguration config = new LwjglApplicationConfiguration();
      config.audioDeviceBufferCount = 10;
      config.audioDeviceBufferSize = 4096;
      config.audioDeviceSimultaneousSources = 16;
      DisplayMode display = LwjglApplicationConfiguration.getDesktopDisplayMode();
      if (display.height >= hdpiHeightThreshold) {
         Fonts.resolutionMultiplier = 2;
      }
      config.foregroundFPS = 0;
      config.useHDPI = true;
      config.vSyncEnabled = true;
      config.title = "SIMULACRA";
      config.addIcon("launcher128.png", FileType.Internal);
      config.addIcon("launcher64.png", FileType.Internal);
      config.addIcon("launcher32.png", FileType.Internal);
      config.addIcon("launcher16.png", FileType.Internal);
      config.allowSoftwareMode = true;
      config.width = display.width;
      config.height = display.height;
      if (!Globals.isWindowed) {
         config.fullscreen = true;
      } else {
         config.fullscreen = false;
         config.resizable = true;
      }
      Game game = new Game(this);
      this.application = new LwjglApplication(game.applicationListener, config);
   }

   @Override
   public void setWindowed() {
      LwjglGraphics graphics = (LwjglGraphics)Gdx.graphics;
      graphics.setWindowedMode(graphics.getWidth(), graphics.getHeight());
   }

   @Override
   public void reportLog(String source, String text) {
      Gdx.app.log(source, text);
   }

   @Override
   public void reportLog(String source, String text, Throwable exception) {
      Gdx.app.log(source, text, exception);
   }

   @Override
   public void reportLogDebug(String source, String text) {
      Gdx.app.debug(source, text);
   }

   @Override
   public void reportLogDebug(String source, String text, Throwable exception) {
      Gdx.app.debug(source, text, exception);
   }

   @Override
   public void reportLogError(String source, String text) {
      Gdx.app.error(source, text);
   }

   @Override
   public void reportLogError(String source, String text, Throwable exception) {
      Gdx.app.error(source, text, exception);
   }

   @Override
   public VoiceProfile createTextVoice(String path) {
      OggInputStream input = new OggInputStream(File.open(path).read(1024));
      ByteArrayOutputStream output = new ByteArrayOutputStream(4096);
      byte[] readBuffer = new byte[2048];
      while (!input.atEnd()) {
         int length = input.read(readBuffer);
         if (length == -1) {
            break;
         }
         output.write(readBuffer, 0, length);
      }
      StreamUtils.closeQuietly(input);
      byte[] pcm = output.toByteArray();
      int channels = input.getChannels();
      int sampleRate = input.getSampleRate();
      int bytes = pcm.length - pcm.length % (channels > 1 ? 4 : 2);
      int audioSamples = bytes / (2 * channels);
      float duration = (float)audioSamples / (float)sampleRate;
      ByteBuffer buffer = ByteBuffer.wrap(pcm, 0, bytes);
      buffer.order(ByteOrder.nativeOrder());
      buffer.put(pcm, 0, bytes);
      ((Buffer)buffer).flip();
      ShortBuffer shorts = buffer.asShortBuffer();
      int sampleDistance = sampleRate / textVoiceSampleRate * channels;
      int totalSamples = audioSamples / sampleDistance;
      byte[] samples = new byte[totalSamples];
      int audioIndex = 0;
      label54:
      for (int sampleIndex = 0; audioIndex < audioSamples && sampleIndex < totalSamples; sampleIndex++) {
         int sampled = 0;
         int highest = 0;
         while (sampled < sampleDistance && audioIndex < audioSamples) {
            for (int ch = 0; ch < channels; ch++) {
               int s = shorts.get();
               if (s < 0) {
                  s = -s;
               }
               if (s > highest) {
                  highest = s;
               }
            }
            sampled++;
            audioIndex++;
            highest /= 128;
            if (highest > 255) {
               highest = 255;
            }
            samples[sampleIndex] = (byte)highest;
            continue label54;
         }
         break;
      }
      return new VoiceProfile(path, samples, duration);
   }

   @Override
   public void linkGameData() {
   }

   @Override
   public void prepareSaveGame() {
      Globals.grid.mainMenu.doneLogin(false, this.existsSaveGame());
   }

   @Override
   public void writeSaveGame(MassFile save) {
      Sys.info("DesktopMain", "Writing local save file: " + Globals.SAVE_FILENAME);
      Output output = new Output(262144);
      save.save(output);
      int size = output.position();
      byte[] bytes = output.getBuffer();
      try (FileOutputStream fos = new FileOutputStream(Globals.SAVE_FILENAME)) {
         fos.write(bytes, 0, size);
      } catch (Exception e) {
         throw new RuntimeException("Failed to write save file: " + Globals.SAVE_FILENAME, e);
      }
   }

   @Override
   public boolean existsSaveGame() {
      return new java.io.File(Globals.SAVE_FILENAME).exists();
   }

   @Override
   public MassFile readSaveGame() {
      try {
         Sys.info("DesktopMain", "Loading local save file: " + Globals.SAVE_FILENAME);
         byte[] bytes = new byte[(int)new java.io.File(Globals.SAVE_FILENAME).length()];
         try (FileInputStream fis = new FileInputStream(Globals.SAVE_FILENAME)) {
            int off = 0;
            while (off < bytes.length) {
               int r = fis.read(bytes, off, bytes.length - off);
               if (r < 0) {
                  break;
               }
               off += r;
            }
         }
         Input input = new Input(bytes);
         MassFile saveFile = new MassFile();
         saveFile.load(input);
         return saveFile;
      } catch (Exception e) {
         throw new RuntimeException("Failed to read save file: " + Globals.SAVE_FILENAME, e);
      }
   }

   @Override
   public void deleteSaveGame() {
      new java.io.File(Globals.SAVE_FILENAME).delete();
   }

   @Override
   public boolean showGameCenter() {
      return false;
   }

   @Override
   public boolean promptGameCenterLogin() {
      return false;
   }

   @Override
   public void openGameCenter() {
   }

   @Override
   public void loginGameCenter() {
   }

   @Override
   public void unlockAchievement(Globals.Achievement achievement) {
      Sys.info("DesktopMain", "Achievement (local, ignored): " + achievement.name());
   }

   @Override
   public void processCallbacks() {
   }

   @Override
   public void exitGame() {
      Gdx.app.exit();
   }

   @Override
   public void openReviewPage() {
      Gdx.net.openURI("https://store.steampowered.com/recommended/recommendgame/712730");
   }

   @Override
   public void destroyed() {
   }
}
