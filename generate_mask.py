import os
import sys

import numpy as np
from PIL import Image, ImageDraw
import json
import shutil


def copy_files_with_suffix(source_folder, destination_folder, num_copies):
    """
    Копирует все файлы в папке source_folder в папку destination_folder, добавляя _{number} к названию.

    Parameters:
    - source_folder (str): Путь к исходной папке.
    - destination_folder (str): Путь к папке, в которую будут скопированы файлы.
    - num_copies (int): Количество копий, которые нужно создать для каждого файла.
    """
    # Проверка существования папки destination_folder, и создание, если её нет
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Проход по всем файлам в source_folder
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)

        # Исключение папок из обработки
        if os.path.isdir(source_path):
            continue

        # Получение имени и расширения файла
        base_name, file_extension = os.path.splitext(filename)

        # Проход по количеству копий
        for i in range(1, num_copies + 1):
            # Формирование нового имени файла с добавлением _{number}
            new_filename = f"{base_name}_{i}{file_extension}"

            # Формирование полного пути к новому файлу в destination_folder
            destination_path = os.path.join(destination_folder, new_filename)

            # Копирование файла
            shutil.copy2(source_path, destination_path)

def read_json(json_filepath):
    with open(json_filepath, 'r') as file:
        data = json.load(file)
    filename_without_extension = os.path.splitext(os.path.basename(json_filepath))[0]
    return data, filename_without_extension

def jpg_to_png(src, dst):
    for filename in os.listdir(src):
        if filename.endswith('.jpg'):
            # Формирование полного пути к исходному файлу
            input_path = os.path.join(src, filename)

            # Формирование полного пути к выходному png-файлу с таким же названием
            output_path = os.path.join(dst, os.path.splitext(filename)[0] + '.png')

            # Открытие jpg-файла и сохранение в формате png
            with Image.open(input_path) as img:
                img.save(output_path, format='PNG')

def create_mask_from_data(data, json_filename, save_png_folder, save_npy_folder):
    # Создание изображения с заполненными полигонами
    image = Image.new('L', (data['imageWidth'], data['imageHeight']), 0)
    draw = ImageDraw.Draw(image)
    imagePng = Image.new('RGB', (data['imageWidth'], data['imageHeight']), (0,0,0))
    drawPng = ImageDraw.Draw(imagePng)

    for shape in data['shapes']:
        polygon_points = [(float(x), float(y)) for x, y in shape['points']]
        fill = (0,0,255)
        drawPng.polygon(polygon_points, outline=tuple(fill), fill=tuple(fill))
        draw.polygon(polygon_points, outline=1, fill=1)

    # Сохранение изображения
    png_filename = f"{json_filename}.png"
    png_filepath = os.path.join(save_png_folder, png_filename)
    imagePng.save(png_filepath)

    # Загрузка изображения в массив NumPy и сохранение в .npy маску
    mask_array = np.array(image)

    npy_filename = f"{json_filename}.npy"
    npy_filepath = os.path.join(save_npy_folder, npy_filename)
    np.save(npy_filepath, mask_array)


json_folder = sys.argv[1]
img_folder = sys.argv[2]
png_folder = sys.argv[3]
save_png_mask_folder = sys.argv[4]
save_npy_folder = sys.argv[5]
dup = int(sys.argv[6])


jpg_to_png(img_folder, png_folder)

copy_files_with_suffix(json_folder, json_folder, dup)
copy_files_with_suffix(png_folder, png_folder, dup)

json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

for json_file in json_files:

    json_filepath = os.path.join(json_folder, json_file)
    data, name = read_json(json_filepath)

    create_mask_from_data(data, name, save_png_mask_folder, save_npy_folder)
