#!/usr/bin/env python3
import re

data = open('C:/IA-Prueba/SIMULACRA/extracted/simulacra.exe', 'rb').read()
print('simulacra.exe: {} bytes'.format(len(data)))

strings = []
current = bytearray()
start = 0
for i, b in enumerate(data):
    if 32 <= b <= 126:
        if not current:
            start = i
        current.append(b)
    else:
        if len(current) >= 8:
            s = current.decode('ascii', errors='replace')
            strings.append({'s': s, 'p': start, 'l': len(s)})
        current = bytearray()
if len(current) >= 8:
    s = current.decode('ascii', errors='replace')
    strings.append({'s': s, 'p': start, 'l': len(s)})

skip_re = re.compile(r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.dll|\.exe|\.png|\.jpg|\.ogg|\.mp4|\.web|DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|Short|Int|String|HashMap|VoiceProfile|^[A-Z]-en-us|L[A-Z]|^[A-Z]engine|^[A-Z]sengine|com\.badlogic|java\.lang|^[0-9A-Fa-f]{3,}$|^[A-Z][a-z]{1,2}$|Microsoft|Windows|Visual|Runtime|Kernel|System|Program|Files|Common|Android|IOS|LWJGL|OpenAL|jinput|steam|Steam|API|DLL|EXE|Manifest|Version|Product|Company|Copyright|Description|Internal|File|Original|Build|Special|Private|Debug|Release|String|Integer|Boolean|Class|Method|Field|Constructor|Interface|Enum|Exception|Error|Warning|Info|Trace|Log|Output|Input|Stream|Reader|Writer|Buffer|Socket|Server|Client|Connection|Request|Response|Header|Content|Type|Length|Status|Code|Message|Data|Value|Name|Id|Key|Path|Dir|File|Folder|Temp|Cache|Config|Setting|Option|Preference|Property|Attribute|Parameter|Argument|Variable|Constant|Literal|Operator|Expression|Statement|Block|Scope|Namespace|Package|Module|Library|Framework|Component|Service|Factory|Builder|Parser|Generator|Renderer|Processor|Handler|Listener|Observer|Subject|Publisher|Subscriber|Queue|Stack|List|Map|Set|Array|Collection|Iterator|Enumerator|Comparable|Comparator|Cloneable|Serializable|Externalizable|Transient|Volatile|Synchronized|Strictfp|Native|Abstract|Final|Static|Public|Private|Protected|Default|Interface|Class|Enum|Annotation|Record|Sealed|Nonsealed|Permits|Module|Open|Exports|Uses|Provides|With|To|Require|Transitive|Bridge|Varargs|Synthetic|Deprecated|SuppressWarnings|SafeVarargs|FunctionalInterface|Instanceof|Pattern|Match|Switch|Yield)')

filtered = [x for x in strings if not skip_re.search(x['s'])]
print('Total strings: {}, filtrados: {}'.format(len(strings), len(filtered)))

vowel_re = re.compile(r'[aeiouAEIOU]{2,}')
real = [x for x in filtered if vowel_re.search(x['s']) and len(x['s']) >= 8]
print('Con múltiples vocales: {}'.format(len(real)))

for x in real[:50]:
    print('  [{}] {}'.format(x['p'], x['s']))
