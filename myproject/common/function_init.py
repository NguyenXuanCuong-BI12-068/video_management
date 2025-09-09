import os
import logging
import logging.handlers
from datetime import datetime
import random
import pyfiglet

logger = logging.getLogger()

def init_logging():
    global logger
    now = datetime.now()

    # logger = logging.getLogger()
    log_directory = f'backend-logs/logs/{now.year}/{now.month:02d}/{now.day:02d}'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logfile = os.path.join(log_directory, 'backend-log.log')
    # handler = logging.handlers.TimedRotatingFileHandler(logfile, interval=1, when='midnight', backupCount=31)
    formatter = logging.Formatter('%(asctime)s ~ %(message)s')
    # handler.setFormatter(formatter)

    # logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    return logger


def start_service(text):
    # Danh sách các kiểu chữ Figlet có sẵn
    fonts = pyfiglet.FigletFont.getFonts()

    # Chọn ngẫu nhiên một kiểu chữ từ danh sách
    random_font = random.choice(fonts)

    # Tạo đối tượng Figlet với kiểu chữ ngẫu nhiên
    figlet = pyfiglet.Figlet(font=random_font)

    # Sinh ra chuỗi chữ kiểu Figlet
    ascii_art = figlet.renderText(text)

    return ascii_art