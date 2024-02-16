## Hier werden Kratzer und Dellen generiert ##
## Es sind die Fehler aus defects/PS zu bevorzugen ##
import random
from PIL import Image, ImageDraw

def create_texture(size, index):
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # Zufällig auswählen, ob eine Delle oder ein Kratzer erzeugt wird
    create_dent = random.choice([True, False])

    if create_dent:
        # Erzeuge eine zufällige Delle
        center_x = random.randint(size // 4, size * 3 // 4)
        center_y = random.randint(size // 4, size * 3 // 4)
        radius = random.randint(1, min(size // 10, 12)) # Radius Dellen

        shade = random.randint(0, 100)  # Zufälliger Farbton von Schwarz (0) bis Dunkelgrau (100)
        color = (shade, shade, shade)

        # Zeichne die zufällige Delle
        draw.ellipse([(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)], fill=color)
    else:
        # Erzeuge einen zufälligen Kratzer
        start_x = random.randint(0, size - 1)
        start_y = random.randint(0, size - 1)
        end_x = random.randint(0, size - 1)
        end_y = random.randint(0, size - 1)

        # Stelle sicher, dass der Kratzer im Bild bleibt
        start_x = max(min(start_x, size - 1), 0)
        start_y = max(min(start_y, size - 1), 0)
        end_x = max(min(end_x, size - 1), 0)
        end_y = max(min(end_y, size - 1), 0)

        shade = random.randint(0, 100)  # Zufälliger Farbton von Schwarz (0) bis Dunkelgrau (100)
        color = (shade, shade, shade)

        # Zeichne den zufälligen Kratzer
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(color[0], color[1], color[2], 128), width=random.randint(1, 5)) #Breite Kratzer

    img.save(f"defect_{index}.png")  # Speichert das Bild als "texture_1.png", "texture_2.png", usw.

# Ändere die gewünschte Anzahl an Texturen hier:
anzahl_defects = 5
bildfläche_größe = random.randint(100, 200)

for i in range(1, anzahl_defects + 1):
    create_texture(bildfläche_größe, i)