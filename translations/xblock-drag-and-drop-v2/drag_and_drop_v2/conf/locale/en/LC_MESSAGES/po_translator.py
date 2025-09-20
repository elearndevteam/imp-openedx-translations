from deep_translator import GoogleTranslator
import polib
import os
import sys
import re

def protect_placeholders(text):
    protected = {}
    counter = 0

    patterns = [
    r"#",                                # hash simbol
    r"(\n)",                         # literalni \n i stvarni newline
    r"( {2,})",                           # višestruki razmaci
    r"<[^>]+>",                          # HTML tagovi
    r"&[^;]+;",                          # HTML entiteti
    r"%\([^)]+\)[sdifouxXeEgGcr]",       # imenovani % placeholderi
    r"%[-+0-9.\d]*[sdifouxXeEgGcr]",     # obični % placeholderi
    r"\{[^{}]+\}",                       # format-style: {name}, {0}
    r'"[^"]+"',                          # dvostruki navodnici
    r"'[^']+'",                          # jednostruki navodnici
    ]

    for pattern in patterns:
        for match in re.findall(pattern, text):
            key = f"ППП_{counter}__"
            protected[key] = match
            text = text.replace(match, key)
            counter += 1

    return text, protected

def restore_placeholders(text, protected):
    for key, value in protected.items():
        text = text.replace(key, value)
        text = text.replace(key.lower(), value)
    return text

def translate_text_preserving_format(original_text):
    lines = original_text.split("\n")
    translated_lines = []

    for line in lines:
        stripped = line.strip()

        # Preskoči ako je linija HTML entitet, tag, ili prazna
        if not stripped or re.match(r"^(&[^;]+;|<[^>]+>)", stripped):
            translated_lines.append(line)
            continue

        safe_text, protected = protect_placeholders(stripped)

        try:
            translated = GoogleTranslator(source='en', target='sr').translate(safe_text)
            translated = restore_placeholders(translated, protected)
            print(translated)

            leading_spaces = len(line) - len(line.lstrip())
            translated_lines.append(" " * leading_spaces + translated)
        except Exception:
            translated_lines.append(line)

    return "\n".join(translated_lines)

def translate_po_file(file_path):
    if not os.path.isfile(file_path):
        print(f"❌ Fajl '{file_path}' ne postoji.")
        return

    try:
        po = polib.pofile(file_path)
    except Exception as e:
        print(f"❌ Greška pri učitavanju .po fajla: {e}")
        return

    print(f"🔄 Prevodim poruke iz fajla: {file_path}")
    for entry in po:
        if not entry.translated():
            original_text = entry.msgid
            if not original_text:
                continue

            translated = translate_text_preserving_format(original_text)

            if entry.msgid_plural:
                entry.msgstr[0] = translated
                original_plural = entry.msgid_plural.strip()
                translated_plural = translate_text_preserving_format(original_plural)
                entry.msgstr[1] = translated_plural

            entry.msgstr = translated

    output_path = file_path.replace(".po", ".translated.po")
    po.save(output_path)
    print(f"✅ Prevedeni fajl sačuvan kao: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("📄 Unesi putanju do .po fajla: ").strip()

    translate_po_file(input_file)