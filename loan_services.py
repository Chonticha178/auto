import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys

CONFIG_FILE = "config.ini"

# ==================== CONFIG & HELPER FUNCTIONS ====================

def read_config(filename=CONFIG_FILE):
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] ไม่พบไฟล์ config ที่: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        return config
    except Exception as e:
        print(f"[X] FAILED: ไม่สามารถอ่านไฟล์ {filename} ได้: {e}")
        return configparser.ConfigParser()

CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้ โปรดตรวจสอบไฟล์")
    exit()

WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE']
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

B_CFG = CONFIG['LOAN_MAIN']
S_CFG = CONFIG['LOAN_SERVICES']

# ==================== SCROLL HELPERS ====================

def force_scroll_down(window, scroll_dist=-10):
    """เลื่อนหน้าจอลง (เสถียรกับ POS)"""
    try:
        window.set_focus()
        time.sleep(0.2)

        rect = window.rectangle()
        x = rect.left + rect.width() // 2
        y = rect.bottom - 50

        mouse.move(coords=(x, y))
        mouse.scroll(coords=(x, y), wheel_dist=scroll_dist)
        time.sleep(0.5)

    except Exception:
        window.type_keys("{PGDN}")
        time.sleep(0.5)

def scroll_to_bottom(window, max_scrolls=10):
    """เลื่อนหน้าจอลงจนสุด"""
    print("[*] กำลังเลื่อนหน้าจอลงล่างสุด...")
    for _ in range(max_scrolls):
        force_scroll_down(window)
    print("[/] เลื่อนถึงด้านล่างแล้ว")

# ==================== MAIN FUNCTION ====================

def loan_main():
    BT_A_TITLE = B_CFG['BT_A_TITLE']
    BT_L_TITLE = B_CFG['BT_L_TITLE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']

    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        main_window.child_window(title=BT_A_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        main_window.child_window(title=BT_L_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # อ่านบัตรประชาชน
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(1)

        # ✅ เลื่อนลงล่างสุด
        scroll_to_bottom(main_window)

        # ===== Postal Code =====
        postal_control = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")

        found = False
        for _ in range(3):
            if postal_control.exists(timeout=1):
                found = True
                break
            force_scroll_down(main_window)

        if not found:
            print("[X] ไม่พบช่องไปรษณีย์")
            return False

        if not postal_control.texts()[0].strip():
            postal_control.click_input()
            main_window.type_keys(POSTAL_CODE)

        # ===== Phone =====
        phone_control = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")

        found = False
        for _ in range(3):
            if phone_control.exists(timeout=1):
                found = True
                break
            force_scroll_down(main_window)

        if not found:
            print("[X] ไม่พบช่องเบอร์โทรศัพท์")
            return False

        if not phone_control.texts()[0].strip():
            phone_control.click_input()
            main_window.type_keys(PHONE_NUMBER)

        # Next
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[V] SUCCESS")
        return True

    except Exception as e:
        print(f"[X] FAILED: {e}")
        return False

# ==================== TRANSACTION ====================

def loan_transaction(main_window, transaction_title):
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']

    try:
        main_window.child_window(
            title=transaction_title,
            auto_id=TRANSACTION_CONTROL_TYPE,
            control_type="Text"
        ).click_input()

        time.sleep(WAIT_TIME)

        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

    except Exception as e:
        print(f"[X] FAILED {transaction_title}: {e}")

# ==================== SERVICES ====================

def run_service(service_key):
    if not loan_main():
        return
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    main_window = app.top_window()

    title = S_CFG[service_key]
    target = main_window.child_window(
        title=title,
        auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'],
        control_type="Text"
    )

    found = False
    for _ in range(5):
        if target.exists(timeout=1):
            found = True
            break
        force_scroll_down(main_window)

    if not found:
        print(f"[X] ไม่พบ {title}")
        return

    loan_transaction(main_window, title)

def loan_services1(): run_service('LOAN_1_TITLE')
def loan_services2(): run_service('LOAN_2_TITLE')
def loan_services3(): run_service('LOAN_3_TITLE')
def loan_services4(): run_service('LOAN_4_TITLE')
def loan_services5(): run_service('LOAN_5_TITLE')
def loan_services6(): run_service('LOAN_6_TITLE')
def loan_services7(): run_service('LOAN_7_TITLE')
def loan_services8(): run_service('LOAN_8_TITLE')
def loan_services9(): run_service('LOAN_9_TITLE')
def loan_services10(): run_service('LOAN_10_TITLE')
def loan_services11(): run_service('LOAN_11_TITLE')
def loan_services12(): run_service('LOAN_12_TITLE')
def loan_services13(): run_service('LOAN_13_TITLE')
def loan_services14(): run_service('LOAN_14_TITLE')
def loan_services15(): run_service('LOAN_15_TITLE')
def loan_services16(): run_service('LOAN_16_TITLE')
def loan_services17(): run_service('LOAN_17_TITLE')
def loan_services18(): run_service('LOAN_18_TITLE')
def loan_services19(): run_service('LOAN_19_TITLE')

if __name__ == "__main__":
    loan_main()
