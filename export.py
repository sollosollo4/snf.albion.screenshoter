import cv2
import pytesseract
import numpy as np
import os
import discord
from discord.ext import commands

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    cv2.imwrite('original_image.png', image)  # Сохранение оригинального изображения
    
    # Конвертация изображения в цветовое пространство HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    cv2.imwrite('hsv_image.png', hsv)  # Сохранение изображения в формате HSV
    
    # Определение диапазонов цвета для маски
    # Маска для белого текста
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([255, 99, 255], dtype=np.uint8)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    cv2.imwrite('mask_white.png', mask_white)  # Сохранение маски для белого текста
    
    # Маска для желтого текста
    lower_yellow = np.array([10, 180, 90], dtype=np.uint8)
    upper_yellow = np.array([30, 245, 245], dtype=np.uint8)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    cv2.imwrite('mask_yellow.png', mask_yellow)  # Сохранение маски для желтого текста
    
    # Объединение масок
    mask = cv2.bitwise_or(mask_white, mask_yellow)
    cv2.imwrite('combined_mask.png', mask)  # Сохранение объединенной маски
    
    # Применение маски к изображению
    result = cv2.bitwise_and(image, image, mask=mask)
    cv2.imwrite('masked_image.png', result)  # Сохранение изображения с примененной маской
    
    # Преобразование в серое изображение и бинаризация
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('gray_image.png', gray)  # Сохранение серого изображения

    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite('binary_image.png', binary)  # Сохранение бинарного изображения

    return binary

def extract_player_names(image_path):
    print("Current working directory:", os.getcwd())  # Проверка текущей рабочей директории

    # Предварительная обработка изображения
    preprocessed_image = preprocess_image(image_path)

    # Сохранение предварительно обработанного изображения
    cv2.imwrite('preprocessed_image.png', preprocessed_image)

    # Использование Tesseract с пользовательским словарем
    custom_config = r'--oem 3 --psm 6 --psm 11 --user-words D:\\SourceWorks\\python\\albion-party-export\\custom_words.txt'
    text = pytesseract.image_to_string(preprocessed_image, config=custom_config)

    # Разделение текста на строки и фильтрация
    player_names = [line.strip() for line in text.split('\n') if line.strip()]

    return player_names

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Команда для обработки изображений
@bot.command()
async def recognize(ctx):
    # Отправляем сообщение с просьбой загрузить изображение
    await ctx.send("Пожалуйста, загрузите изображение для распознавания имен...")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.attachments

    try:
        # Ожидание загрузки изображения
        message = await bot.wait_for('message', check=check, timeout=60)

        # Получение первого прикрепленного изображения
        attachment = message.attachments[0]
        image_path = f"temp_image{attachment.filename[-4:]}"
        await attachment.save(image_path)

        # Распознавание имен
        names = extract_player_names(image_path)

        # Удаление временного изображения
        import os
        os.remove(image_path)

        # Отправка списка имен обратно пользователю
        await ctx.send(f"Распознанные имена на изображении:\n{', '.join(names)}")

    except asyncio.TimeoutError:
        await ctx.send("Время ожидания истекло. Попробуйте еще раз.")

# Запуск бота
bot.run('SECRET_TOKEN')