#!/usr/bin/env python3
"""Extraer texto de la memoria del proceso SIMULACRA."""
import ctypes
import ctypes.wintypes
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

PID = 1504

kernel32 = ctypes.windll.kernel32

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

hProcess = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, PID)
if hProcess == 0:
    print('No se pudo abrir el proceso: {}'.format(ctypes.GetLastError()))
    sys.exit(1)

print('Proceso abierto exitosamente')

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BaseAddress', ctypes.c_void_p),
        ('AllocationBase', ctypes.c_void_p),
        ('AllocationProtect', ctypes.wintypes.DWORD),
        ('RegionSize', ctypes.c_size_t),
        ('State', ctypes.wintypes.DWORD),
        ('Protect', ctypes.wintypes.DWORD),
        ('Type', ctypes.wintypes.DWORD),
    ]

mbi = MEMORY_BASIC_INFORMATION()
address = 0
found_strings = []
scan_count = 0

PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100

while True:
    result = kernel32.VirtualQueryEx(
        hProcess, 
        ctypes.c_void_p(address), 
        ctypes.byref(mbi), 
        ctypes.sizeof(mbi)
    )
    if result == 0:
        break
    
    base_addr = mbi.BaseAddress  # Keep as c_void_p
    
    # Check if region is readable and committed
    if (mbi.State == 0x1000 and  # MEM_COMMIT
        not (mbi.Protect & PAGE_NOACCESS) and
        not (mbi.Protect & PAGE_GUARD)):
        
        region_size = mbi.RegionSize
        if region_size > 0 and region_size < 50 * 1024 * 1024:  # Skip regions > 50MB
            buffer = ctypes.create_string_buffer(region_size)
            bytes_read = ctypes.c_size_t(0)
            
            # Use c_void_p for the address parameter
            addr_param = ctypes.c_void_p(ctypes.addressof(ctypes.pointer(mbi.contents))) if False else base_addr
            try:
                if kernel32.ReadProcessMemory(hProcess, base_addr, buffer, region_size, ctypes.byref(bytes_read)):
                    data = buffer.raw[:bytes_read.value]
                    scan_count += 1
                    
                    # Search for ASCII strings >= 10 chars
                    current = bytearray()
                    for b in data:
                        if 32 <= b <= 126:
                            current.append(b)
                        else:
                            if len(current) >= 10:
                                s = current.decode('ascii', errors='replace')
                                vowel_re = re.compile(r'[aeiouAEIOU]{2,}')
                                if vowel_re.search(s):
                                    found_strings.append(s)
                            current = bytearray()
                    if len(current) >= 10:
                        s = current.decode('ascii', errors='replace')
                        vowel_re = re.compile(r'[aeiouAEIOU]{2,}')
                        if vowel_re.search(s):
                            found_strings.append(s)
            except Exception as e:
                pass  # Skip regions that can't be read
    
    address += mbi.RegionSize
    
    if scan_count % 200 == 0 and scan_count > 0:
        print('Escaneadas {} regiones, {} strings encontrados...'.format(scan_count, len(found_strings)))

kernel32.CloseHandle(hProcess)

# Deduplicate
unique_strings = list(set(found_strings))
print('\nStrings únicos en memoria: {}'.format(len(unique_strings)))

# Filter for dialogue-like text
dialogue = []
skip_re = re.compile(r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|Microsoft|Windows|Visual|Runtime|Kernel|System|Program|Files|Common|Android|IOS|LWJGL|OpenAL|jinput|steam|Steam|API|DLL|EXE|Manifest|Version|Copyright|Description)')
for s in unique_strings:
    if not skip_re.search(s) and len(s) >= 10:
        dialogue.append(s)

dialogue.sort()
print('Strings de diálogo posibles: {}'.format(len(dialogue)))
for s in dialogue[:100]:
    print('  {}'.format(s))
