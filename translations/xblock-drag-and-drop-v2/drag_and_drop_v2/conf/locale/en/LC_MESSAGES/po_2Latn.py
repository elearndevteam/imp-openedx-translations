import cyrtranslit



def translate(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    converted = []
    in_msgstr_block = False

    for line in lines:
        stripped = line.strip()

        # Kraj msgstr bloka ako naiđeš na komentar ili novi msgid
        if stripped.startswith("#") or stripped.startswith("msgid"):
            in_msgstr_block = False
            converted.append(line)
            continue

        # Početak msgstr bloka
        if stripped.startswith("msgstr"):
            in_msgstr_block = True

        if in_msgstr_block and '"' in line:
            parts = line.split('"')
            for i in range(len(parts)):
                if i % 2 == 1:  # quoted segment
                    parts[i] = cyrtranslit.to_latin(parts[i])
            line = '"'.join(parts)

        converted.append(line)

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(converted)

    print("✅ Transliteration complete:", output_path)

input_path = "django.translated.po"
output_path = "django_Latn.translated.po"
translate(input_path, output_path)

input_path = "djangojs.translated.po"
output_path = "djangojs_Latn.translated.po"
translate(input_path, output_path)