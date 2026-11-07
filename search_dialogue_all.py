#!/usr/bin/env python3
"""Buscar texto de diálogo legible en TODOS los archivos del juego."""
import os
import re

base = 'C:/IA-Prueba/SIMULACRA/extracted'

# Palabras que deberían aparecer en diálogos
dialogue_words = ['hello', 'help', 'please', 'yes', 'no', 'call', 'message', 
                   'email', 'password', 'login', 'delete', 'save', 'send',
                   'calling', 'answer', 'hang', 'text', 'photo', 'video',
                   'spark', 'jabbr', 'mail', 'phone', 'contact', 'dialogue',
                   'subtitle', 'error', 'warning', 'confirm', 'cancel',
                   'anna', 'taylor', 'ashley', 'greg', 'iris', 'murilo',
                   'peace', 'cassie', 'chaosstar', 'fariskane']

results = []

for root, dirs, files in os.walk(base):
    # Skip extracted subdirectories we already know about
    if 'decompressed' in root:
        continue
    for f in files:
        path = os.path.join(root, f)
        try:
            data = open(path, 'rb').read()
            # Skip very large files (>50MB) for quick scan
            if len(data) > 50 * 1024 * 1024:
                continue
            text = data.decode('ascii', errors='replace')
            # Count dialogue words
            count = 0
            found_words = []
            for word in dialogue_words:
                if word in text.lower():
                    count += 1
                    found_words.append(word)
            if count >= 3:
                results.append({
                    'path': path,
                    'size': len(data),
                    'word_count': count,
                    'words': found_words[:10]
                })
        except:
            pass

print('Archivos con palabras de diálogo (>=3):')
for r in sorted(results, key=lambda x: -x['word_count']):
    print('  {} ({} bytes, {} palabras: {})'.format(
        r['path'], r['size'], r['word_count'], ', '.join(r['words'])))
