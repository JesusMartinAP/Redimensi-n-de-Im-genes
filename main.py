import os
import shutil
import tkinter as tk 
from tkinter import filedialog, messagebox
from tqdm import tqdm
from PIL import Image
import cv2
import subprocess

# Función para seleccionar carpeta
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_name.set(folder_path)
        process_images(folder_path)

# Función para eliminar transparencia
def remove_transparency(path, output_path, bg_colour=(255, 255, 255)):
    try:
        im = Image.open(path)
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            alpha = im.convert('RGBA').split()[-1]
            bg = Image.new("RGBA", im.size, bg_colour + (255,))
            bg.paste(im, mask=alpha)
            bg = bg.convert('RGB')
        else:
            bg = im.convert('RGB')
        bg.save(output_path)
    except Exception as e:
        print(f"Error {e} en {path}")

# Función para procesar imágenes
def process_images(input_folder):
    # Crear carpetas temporales y de salida en el mismo lugar que se ejecuta el script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = os.path.basename(input_folder)
    temp_folder = os.path.join(script_dir, "Temp")
    output_folder = os.path.join(script_dir, folder_name)
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # Listar imágenes en la carpeta de entrada
    image_files = [x for x in os.listdir(input_folder) if x.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]

    # Eliminar transparencia de todas las imágenes
    for image_file in tqdm(image_files, desc="Eliminando transparencia"):
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(temp_folder, os.path.splitext(image_file)[0] + '.jpg')
        remove_transparency(input_path, output_path)

    # Redimensionar y renombrar imágenes
    temp_images = os.listdir(temp_folder)

    for index, image_file in enumerate(tqdm(temp_images, desc="Redimensionando imágenes"), start=1):
        img = cv2.imread(os.path.join(temp_folder, image_file))
        img = cv2.resize(img, (2500, 2500), interpolation=cv2.INTER_AREA)
        new_name = f"{folder_name}_{index}.jpg"
        cv2.imwrite(os.path.join(output_folder, new_name), img)

    # Limpiar carpeta temporal
    shutil.rmtree(temp_folder)
    messagebox.showinfo("Proceso completado", f"Las imágenes han sido procesadas y guardadas en {output_folder}")

    # Abrir carpeta de salida
    open_folder(output_folder)

# Función para abrir la carpeta
def open_folder(path):
    if os.name == 'nt':  # Para Windows
        os.startfile(path)
    elif os.name == 'posix':  # Para macOS y Linux
        subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', path])

# Configurar interfaz gráfica
root = tk.Tk()
root.title("Procesador de Imágenes")

folder_name = tk.StringVar()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="Seleccione la carpeta con las imágenes:")
label.grid(row=0, column=0, padx=5, pady=5)

entry = tk.Entry(frame, textvariable=folder_name, width=50)
entry.grid(row=1, column=0, padx=5, pady=5)

button = tk.Button(frame, text="Seleccionar carpeta", command=select_folder)
button.grid(row=1, column=1, padx=5, pady=5)

root.mainloop()

# Nota: Este script se ejecuta en una interfaz gráfica, por lo que no se puede ejecutar directamente en un entorno de consola.
