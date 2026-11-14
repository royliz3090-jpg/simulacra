import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.zip.*;
import javax.crypto.*;
import javax.crypto.spec.*;

// Carga clases directamente desde core.binary replicando CodeBlob del juego:
// SHA-1(name) -> mascara unlock; AES/CTR (key=MD5(name), IV=16 bytes) -> CRC32 -> inflate.
public class BlobLoad extends ClassLoader {
  static int num;
  static int[] desc;
  static byte[] blob;
  static int[] unlock = new int[5];

  // Igual que blob_tool._sha1_words: bytes CON signo, palabras [16..19],[12..15],...
  static int[] sha1words(String name) throws Exception {
    byte[] h = MessageDigest.getInstance("SHA-1").digest(name.getBytes("UTF-8"));
    int[] r = new int[5];
    for (int k=0;k<5;k++){
      int b = 16 - 4*k;
      r[k] = (h[b+3]<<24) | (h[b+2]<<16) | (h[b+1]<<8) | h[b];
    }
    return r;
  }

  static void load(String path) throws Exception {
    byte[] raw = Files.readAllBytes(Paths.get(path));
    ByteBuffer bb = ByteBuffer.wrap(raw).order(ByteOrder.BIG_ENDIAN);
    int magic = bb.getInt(); num = bb.getInt();
    desc = new int[num*9];
    for (int i=0;i<num*9;i++) desc[i]=bb.getInt();
    int blobSize = bb.getInt();
    blob = new byte[blobSize];
    bb.get(blob);
  }

  static byte[] entryData(String name) throws Exception {
    int[] real = sha1words(name);
    byte[] key = MessageDigest.getInstance("MD5").digest(name.getBytes("UTF-8"));
    for (int i=0;i<num;i++){
      int b=i*9;
      boolean match=true;
      for(int k=0;k<5;k++){ if(desc[b+k] != (real[k]^unlock[k])) { match=false; break; } }
      if(!match) continue;
      int off=desc[b+5], csize=desc[b+6], usize=desc[b+7], crc=desc[b+8];
      if(csize<=0) return null;
      byte[] iv=Arrays.copyOfRange(blob, off, off+16);
      byte[] ct=Arrays.copyOfRange(blob, off+16, off+16+csize);
      Cipher c=Cipher.getInstance("AES/CTR/NoPadding");
      c.init(Cipher.DECRYPT_MODE, new SecretKeySpec(key,"AES"), new IvParameterSpec(iv));
      byte[] comp=c.doFinal(ct);
      CRC32 z=new CRC32(); z.update(comp);
      if((int)z.getValue()!=crc) return null;
      Inflater inf=new Inflater();
      inf.setInput(comp);
      byte[] out=new byte[usize];
      int n=inf.inflate(out); inf.end();
      if(n!=usize) throw new IOException("inflate "+n+"!="+usize);
      return out;
    }
    return null;
  }

  static void deriveUnlock() throws Exception {
    int[] real = sha1words("game27.DesktopMain");
    byte[] key = MessageDigest.getInstance("MD5").digest("game27.DesktopMain".getBytes("UTF-8"));
    int found=-1;
    for(int i=0;i<num;i++){
      int b=i*9; int off=desc[b+5], csize=desc[b+6], crc=desc[b+8];
      if(csize<=0) continue;
      byte[] iv=Arrays.copyOfRange(blob,off,off+16);
      byte[] ct=Arrays.copyOfRange(blob,off+16,off+16+csize);
      Cipher c=Cipher.getInstance("AES/CTR/NoPadding");
      c.init(Cipher.DECRYPT_MODE,new SecretKeySpec(key,"AES"),new IvParameterSpec(iv));
      byte[] comp=c.doFinal(ct);
      CRC32 z=new CRC32(); z.update(comp);
      if((int)z.getValue()==crc){ found=i; break; }
    }
    if(found<0) throw new IOException("no se pudo derivar unlock");
    int b=found*9;
    for(int k=0;k<5;k++) unlock[k]=real[k]^desc[b+k];
  }

  static Map<String,byte[]> cache = new HashMap<>();
  protected Class<?> findClass(String name) throws ClassNotFoundException {
    try{
      byte[] d=cache.get(name);
      if(d==null){ d=entryData(name); if(d==null) throw new ClassNotFoundException(name); cache.put(name,d); }
      return defineClass(name, d, 0, d.length);
    }catch(Exception e){ throw new ClassNotFoundException(name, e); }
  }

  public static void main(String[] a) throws Exception {
    load(a[0]);
    deriveUnlock();
    BlobLoad cl = new BlobLoad();
    Class<?> gb = cl.loadClass("game27.gbeslatam.GBESLATAM");
    gb.getMethod("setup").invoke(null);
    Class<?> gt = cl.loadClass("game27.GlobalTexts");
    Object t1 = gt.getField("text1").get(null);
    Object t12 = gt.getField("text12").get(null);
    Object q1a = gt.getField("quest1a").get(null);
    System.out.println("text1="+t1+" text12="+t12+" quest1a="+q1a);
    for(String cn : new String[]{"game27.gb.GBMainMenu","game27.gbeslatam.GBCreditsMenu",
        "game27.gbeslatam.GBNotification","game27.gbeslatam.restore.GBRestorePhraseScreen",
        "game27.gbeslatam.GBESLATAMOverrides"}){
      cl.loadClass(cn);
      System.out.println("cargada "+cn+" OK");
    }
    if(!"Galería".equals(t1)) throw new RuntimeException("text1 != Galería");
    System.out.println("BLOB-SMOKE OK");
  }
}
