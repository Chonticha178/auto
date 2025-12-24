import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os

# ================= CONFIG =================
CONFIG_FILE = "config.ini"

def read_config(filename=CONFIG_FILE):
    config = configparser.ConfigParser()
    config.read(filename, encoding="utf-8")
    return config

CONFIG = read_config()

WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')

B_CFG = CONFIG['LOAN_MAIN']
S_CFG = CONFIG['LOAN_SERVICES']

# ================= HELPERS =================

def force_scroll_down(window, scroll_dist=-5):
    try:
        rect = window.rectangle()
        mouse.click(coords=(rect.left+300, rect.top+300))
        time.sleep(0.3)
        mouse.scroll(coords=(rect.left+300, rect.top+300), wheel_dist=scroll_dist)
    except:
        window.type_keys("{PGDN}")

# ================= CORE =================

def loan_main():
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    main_window = app.top_window()

    main_window.child_window(
        title=B_CFG['BT_A_TITLE'], control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    main_window.child_window(
        title=B_CFG['BT_L_TITLE'], control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    return main_window


def loan_transaction(main_window, service_title):
    main_window.child_window(
        title=service_title,
        auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    main_window.child_window(
        title=B_CFG['NEXT_TITLE'],
        auto_id=B_CFG['NEXT_AUTO_ID'],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    main_window.child_window(
        title=B_CFG['FINISH_BUTTON_TITLE'],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)


def run_service(service_no: int):
    """
    ฟังก์ชันกลาง เรียก service ตามเลข
    """
    main_window = loan_main()

    title_key = f"LOAN_{service_no}_TITLE"
    service_title = S_CFG[title_key]

    loan_transaction(main_window, service_title)
