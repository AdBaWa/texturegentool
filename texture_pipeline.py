import random
from PIL import Image, ImageDraw
import os
import numpy as np
from scipy import ndimage
from matplotlib import pyplot
from pathlib import Path

# Funktion zur Anwendung einer gaußschen Glättung auf ein Bild
def smooth_gaussian(im: np.ndarray, sigma) -> np.ndarray:
    """
    Wendet eine Gaußsche Glättung auf ein Bild an, um das Bildrauschen zu reduzieren.
    Dies wird typischerweise vor der Kantenfindung angewendet, um die Genauigkeit zu verbessern.

    Parameter:
    im (np.ndarray): Das Bild als NumPy-Array.
    sigma (float): Standardabweichung des Gaußschen Kernels, steuert die Glättungsstärke.

    Rückgabe:
    np.ndarray: Das geglättete Bild.
    """
    # Wenn sigma 0 ist, wird das Bild nicht geglättet
    if sigma == 0:
        return im

    # Umwandlung des Bildes in Fließkommazahlen
    im_smooth = im.astype(float)
    
    # Erstellung eines gaußschen Kernels
    kernel_x = np.arange(-3*sigma, 3*sigma+1).astype(float)
    kernel_x = np.exp((-(kernel_x**2))/(2*(sigma**2)))

    # Anwendung des Filters auf das Bild
    im_smooth = ndimage.convolve(im_smooth, kernel_x[np.newaxis])
    im_smooth = ndimage.convolve(im_smooth, kernel_x[np.newaxis].T)

    return im_smooth

# Funktion zur Anwendung des Sobel-Operators auf ein Bild
def sobel(im_smooth):
    """
    Wendet den Sobel-Operator an, um die horizontalen und vertikalen Kanten eines Bildes hervorzuheben.
    Dies wird genutzt, um die Richtung und Stärke der Kanten zu bestimmen.

    Parameter:
    im_smooth (np.ndarray): Das geglättete Bild.

    Rückgabe:
    Tuple[np.ndarray, np.ndarray]: Die Gradienten des Bildes in X- und Y-Richtung.
    """
    gradient_x = im_smooth.astype(float)
    gradient_y = im_smooth.astype(float)

    # Definition des Sobel-Kernels
    kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])

    # Anwendung des Sobel-Operators auf das Bild
    gradient_x = ndimage.convolve(gradient_x, kernel)
    gradient_y = ndimage.convolve(gradient_y, kernel.T)

    return gradient_x, gradient_y

# Funktion zur Berechnung der Normalenabbildung aus den Gradienten
def compute_normal_map(gradient_x: np.ndarray, gradient_y: np.ndarray, intensity=1):
    """
    Errechnet aus den Gradienten eines Bildes eine Normalenabbildung, die für visuelle Effekte in der
    3D-Grafik genutzt werden kann, um eine Oberflächentextur mit mehr Tiefe und Detail darzustellen.

    Parameter:
    gradient_x (np.ndarray): Der Gradient des Bildes in X-Richtung.
    gradient_y (np.ndarray): Der Gradient des Bildes in Y-Richtung.
    intensity (float): Ein Skalierungsfaktor, der die Stärke der Normalen beeinflusst.

    Rückgabe:
    np.ndarray: Die Normalenabbildung des Bildes.
    """
    # Bestimmung der Bildgröße und des maximalen Gradientenwerts
    width = gradient_x.shape[1]
    height = gradient_x.shape[0]
    max_x = np.max(gradient_x)
    max_y = np.max(gradient_y)

    max_value = max_x if max_x >= max_y else max_y

    # Initialisierung der Normalenabbildung
    normal_map = np.zeros((height, width, 3), dtype=np.float32)
    intensity = 1 / intensity
    strength = max_value / (max_value * intensity)

    # Berechnung der Normalenabbildung aus den Gradienten
    normal_map[..., 0] = gradient_x / max_value
    normal_map[..., 1] = gradient_y / max_value
    normal_map[..., 2] = 1 / strength

    norm = np.sqrt(np.power(normal_map[..., 0], 2) + np.power(normal_map[..., 1], 2) + np.power(normal_map[..., 2], 2))

    normal_map[..., 0] /= norm
    normal_map[..., 1] /= norm
    normal_map[..., 2] /= norm

    normal_map *= 0.5
    normal_map += 0.5

    return normal_map

# Funktion zum Konvertieren eines Eingabebildes in eine Normalenabbildung
def Convert(input_file, smoothness, intensity, output_file):
    """
    Liest ein Bild, verarbeitet es, um eine Normalenabbildung zu erstellen, und speichert das Ergebnis.

    Parameter:
    input_file (str): Pfad zur Bilddatei, die verarbeitet werden soll.
    smoothness (float): Gibt an, wie stark das Bild vor der Verarbeitung geglättet werden soll.
    intensity (float): Gibt an, wie stark die Normalen hervorgehoben werden sollen.
    output_file (str): Pfad, unter dem das Ergebnis gespeichert werden soll.
    """
    # Einlesen des Eingabebildes
    im = pyplot.imread(input_file)

    # Falls das Bild 3 Kanäle hat (RGB), wird es in Graustufen konvertiert
    if im.ndim == 3:
        im_grey = np.zeros((im.shape[0], im.shape[1])).astype(float)
        im_grey = (im[..., 0] * 0.3 + im[..., 1] * 0.6 + im[..., 2] * 0.1)
        im = im_grey

    # Glättung des Bildes
    im_smooth = smooth_gaussian(im, smoothness)

    # Berechnung der Gradienten mit dem Sobel-Operator
    sobel_x, sobel_y = sobel(im_smooth)

    # Berechnung der Normalenabbildung
    normal_map = compute_normal_map(sobel_x, sobel_y, intensity)

    # Speichern der Normalenabbildung
    pyplot.imsave(output_file, normal_map)

# Startfunktion zum Konvertieren von Bildern im angegebenen Verzeichnis
def startConvert():
    """
    Durchsucht ein Verzeichnis nach Bildern und konvertiert jedes gefundene Bild in eine Normalenabbildung.
    Die resultierenden Bilder werden in einem Ausgabeverzeichnis gespeichert.

    Parameter:
    input_dir (str): Pfad zum Eingabeverzeichnis, das die zu konvertierenden Bilder enthält.
    output_dir (str): Pfad zum Ausgabeverzeichnis, in dem die Normalenabbildungen gespeichert werden.
    smoothness (float): Stärke der Glättung, die vor der Konvertierung auf die Bilder angewendet wird.
    intensity (float): Intensität der Normalen in der resultierenden Normalenabbildung.

    Rückgabe:
    None
    """
    if not os.path.isdir(input_dir):
        raise ValueError(f"Directory '{input_dir}' does not exist.")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    converted_files = set()
    total_files = set()
    for root, _, files in os.walk(input_dir):
        for name in files:
            file_path = os.path.join(root, name)
            if file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
                total_files.add(file_path)
    
    for file_path in total_files:
        output_name = f"{Path(file_path).stem}_normal.png"
        output_path = os.path.join(output_dir, output_name)

        if output_path in converted_files:
            continue

        # Konvertierung des Bildes und Speichern der Normalenabbildung
        Convert(file_path, smoothness, intensity, output_path)
        converted_files.add(output_path)

# Funktion zum Erstellen einer elliptischen Maske
def create_cylinder_mask(image_shape, x, y, inner_radius, outer_radius):
    """
    Erstellt eine zylindrische Maske, die als elliptische Form in einem Bild dargestellt wird.
    Dies kann verwendet werden, um bestimmte Bereiche eines Bildes hervorzuheben oder auszublenden.

    Parameter:
    image_shape (Tuple[int, int]): Die Dimensionen des Bildes (Breite, Höhe).
    x (int): X-Position des Mittelpunktes der Ellipse im Bild.
    y (int): Y-Position des Mittelpunktes der Ellipse im Bild.
    inner_radius (int): Der innere Radius der Ellipse, innerhalb dessen das Bild unverändert bleibt.
    outer_radius (int): Der äußere Radius der Ellipse, außerhalb dessen das Bild unverändert bleibt.

    Rückgabe:
    Image: Ein PIL-Image-Objekt, das die Maske darstellt.
    """
    mask = Image.new('L', image_shape, 0)
    draw = ImageDraw.Draw(mask)

    # Erstellung der Ellipse für die Maske
    draw.ellipse([(x - outer_radius, y - outer_radius), (x + outer_radius, y + outer_radius)], fill=255)
    draw.ellipse([(x - inner_radius, y - inner_radius), (x + inner_radius, y + inner_radius)], fill=0)

    return mask

# Funktion zum Einfügen einer Textur unter Berücksichtigung der Maske
def insert_texture(background, mask, texture, x_texture, y_texture):
        """
        Fügt eine Textur in ein Hintergrundbild ein, basierend auf der Position und der Maske.

        Parameter:
        background (Image): Das Hintergrundbild, in das die Textur eingefügt wird.
        mask (Image): Die Maske, die definiert, wo die Textur eingefügt wird.
        texture (Image): Die Textur, die eingefügt wird.
        x_texture (int): X-Position, an der die obere linke Ecke der Textur platziert wird.
        y_texture (int): Y-Position, an der die obere linke Ecke der Textur platziert wird.
        """
        background.paste(texture, (x_texture, y_texture), mask=texture.split()[3])

# Funktion zum Einfügen zufälliger Texturen unter Verwendung der Maske
def insert_random_textures(background_image, defect_folder, x, y, inner_radius, outer_radius, index, output_basecolor_image_dir, output_normal, smoothness, intensity):
    """
    Fügt zufällige Texturen aus einem Ordner in ein Hintergrundbild ein. Die Texturen werden innerhalb einer spezifischen Region platziert,
    basierend auf einer elliptischen Maske. Die Anzahl der Texturen und ihre Positionen werden zufällig gewählt. Die Texturen können überlappen,
    und jede Textur wird in eine Bounding-Box-Datei geschrieben, die für maschinelles Lernen verwendet werden kann.

    Parameter:
    background_image (str): Pfad zum Hintergrundbild, auf dem die Texturen platziert werden.
    defect_folder (str): Pfad zum Ordner, der die Texturen enthält, die in das Hintergrundbild eingefügt werden sollen.
    x (int): X-Position des Zentrums der zylindrischen Region auf dem Hintergrundbild.
    y (int): Y-Position des Zentrums der zylindrischen Region auf dem Hintergrundbild.
    inner_radius (int): Innerer Radius der zylindrischen Region, innerhalb dessen keine Texturen platziert werden, um ein Freifeld zu schaffen.
    outer_radius (int): Äußerer Radius der zylindrischen Region, innerhalb dessen Texturen platziert werden können.
    index (int): Numerischer Index, der zur eindeutigen Benennung der Ausgabedateien verwendet wird. Beeinflusst den Namen der gespeicherten Bilder und der entsprechenden Label-Dateien.
    output_basecolor_image_dir (str): Verzeichnis, in dem das bearbeitete Hintergrundbild mit den eingefügten Texturen gespeichert wird.
    output_normal (str): Verzeichnis, in dem die Normalenabbildung des bearbeiteten Hintergrundbildes gespeichert wird.
    smoothness (float): Gibt an, wie stark das Bild vor der Erstellung der Normalenabbildung geglättet werden soll.
    intensity (float): Stärke der Normalen in der resultierenden Normalenabbildung, beeinflusst die visuelle Tiefe der Textur.

    Rückgabe:
    None. Das bearbeitete Bild wird im output_basecolor_image_dir gespeichert und die Normalenabbildung im output_normal Verzeichnis.
    Die Bounding-Box-Daten für jede platzierte Textur werden in einer separaten Datei im 'labels'-Unterverzeichnis gespeichert.

    Nebeneffekte:
    - Erstellung von Bilddateien im output_basecolor_image_dir.
    - Erstellung von Normalenabbildungsdateien im output_normal Verzeichnis.
    - Erstellung oder Erweiterung von Label-Dateien im 'labels'-Unterverzeichnis, die die Koordinaten der Bounding Boxes enthalten.
    """
    background = Image.open(background_image)
    image_shape = background.size
    mask = create_cylinder_mask(image_shape, x, y, inner_radius, outer_radius)
    texture_files = os.listdir(defect_folder)

    # Zuerst wird eine Zufallszahl zwischen 0 und 1 generiert und in der Variable 'random_value' gespeichert
    random_value = random.random()  
    # Danach wird die Anzahl der einzufügenden Texturen basierend auf dem Wert von 'random_value' bestimmt.
    # Wird mit einer Wahrscheinlichkeit von 10% (wenn random_value kleiner als 0.1 ist) eine dreifache Textur eingefügt.
    # Wird mit einer Wahrscheinlichkeit von 20% (wenn random_value größer oder gleich 0.1 aber kleiner als 0.3 ist) eine doppelte Textur eingefügt.
    # Wird mit einer Wahrscheinlichkeit von 70% (wenn random_value größer oder gleich 0.3 ist) eine einzelne Textur eingefügt.
    num_textures = 3 if random_value < 0.1 else 2 if random_value < 0.3 else 1

    inserted_textures = 0
    
    #Für Debugging
    #print(f"Random Value: {random_value}")
    #print(f"Number of Textures: {num_textures}")
    
    for _ in range(3):
        random_x = random.randint(x - outer_radius + 10, x + outer_radius - 10)
        random_y = random.randint(y - outer_radius + 10, y + outer_radius - 10)

        if mask.getpixel((random_x, random_y)) == 255 and inserted_textures < num_textures:
            random_texture_path = os.path.join(defect_folder, random.choice(texture_files))
            texture = Image.open(random_texture_path)

            x_texture = random_x - texture.width // 2
            y_texture = random_y - texture.height // 2
            x_end = min(x_texture + texture.width, image_shape[0])
            y_end = min(y_texture + texture.height, image_shape[1])

            texture = texture.crop((0, 0, x_end - x_texture, y_end - y_texture))

            insert_texture(background, mask, texture, x_texture, y_texture)

            bbox_x = x_texture / image_shape[0]
            bbox_y = y_texture / image_shape[1]
            bbox_width = texture.width / image_shape[0]
            bbox_height = texture.height / image_shape[1]

            with open(f"texture/labels/label_{index}.txt", "a") as file:
                file.write(f"0 {bbox_x} {bbox_y} {bbox_width} {bbox_height}\n")

            inserted_textures += 1
    
    # Pfad für das Speichern des bearbeiteten Bildes und der Normalenabbildung.  
    output_image_path = os.path.join(output_basecolor_image_dir, f"basecolor_{index}.png")
    background.save(output_image_path)
    print(f"Das Bild wurde erfolgreich unter {output_image_path} gespeichert.")

    # Erstelle die Normalenabbildung für das bearbeitete Bild.  
    normal_map_output_path = os.path.join(output_normal, f"basecolor_{index}_normal.png")  
    Convert(output_image_path, smoothness, intensity, normal_map_output_path)

if __name__ == "__main__":
    # Definiere die Pfade und Einstellungen für die Masken und die Normalenabbildung.
    background_image_path = 'texture/raw/raw_basecolor.png'  # Pfad zum Basisbild für die Textur.
    defect_folder_path = 'texture/defects/ps'              # Pfad zum Ordner mit den Defekten.
    output_basecolor_image_dir = 'texture/texture_maps'
    output_normal = 'texture/texture_maps/normal'
    x_position = 524  # X-Position des Zentrums für die Maske.
    y_position = 1524  # Y-Position des Zentrums für die Maske.
    inner_radius = 270  # Innerer Radius, innerhalb dessen keine Texturen platziert werden.
    outer_radius = 500  # Äußerer Radius, innerhalb dessen Texturen platziert werden können.
    anzahl_bilder = 5000  # Anzahl der zu erstellenden Bilder mit Texturen.

    # Pfade und Einstellungen für die Erstellung der Normalenabbildungen.
    input_dir = output_basecolor_image_dir  # Eingabeverzeichnis mit den Basisbildern.
    output_dir = "texture/texture_maps/normal"  # Ausgabeverzeichnis für die Normalenabbildungen.
    smoothness = 1.5  # Stärke der Glättung für die Normalenabbildung.
    intensity = 2.0  # Intensität der Normalen in der Normalenabbildung.

    # Erzeuge Bilder mit zufälligen Texturen und generiere Normalenabbildungen.
    for i in range(anzahl_bilder):
        insert_random_textures(background_image_path,
                               defect_folder_path,
                               x_position,y_position,
                               inner_radius,
                               outer_radius,
                               i+1,
                               output_basecolor_image_dir,
                               output_normal,
                               smoothness,
                               intensity,
                               )

