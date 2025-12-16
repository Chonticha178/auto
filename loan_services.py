import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os
import sys

CONFIG_FILE = "config.ini"

# ==================== CONFIG & HELPER FUNCTIONS ====================

def read_config(filename=CONFIG_FILE):
    """อ่านและโหลดค่าจากไฟล์ config.ini"""
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

# โหลด Config
CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้ โปรดตรวจสอบไฟล์")
    exit() # ใช้ exit() ตามโค้ดเดิม

# ดึงค่า Global ที่ใช้ร่วมกัน
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID'] 
SEARCH_BOX_ID = CONFIG.get('GLOBAL', 'SEARCH_BOX_AUTO_ID', fallback='SearchTextBox') 

# ดึง Section หลัก
B_CFG = CONFIG['LOAN_MAIN']
S_CFG = CONFIG['LOAN_SERVICES']

# ==================== SCROLL HELPERS mouse ====================

def force_scroll_down(window, scroll_dist=-5):
    """ฟังก์ชันช่วยเลื่อนหน้าจอลงโดยใช้ Mouse Wheel"""
    try:
        rect = window.rectangle()
        # หาจุดกลางหน้าจอเพื่อวางเมาส์
        center_x = rect.left + 300
        center_y = rect.top + 300
        
        # คลิกเพื่อให้หน้าจอ Focus ก่อนเลื่อน
        mouse.click(coords=(center_x, center_y))
        time.sleep(0.5)
        # สั่งเลื่อนเมาส์
        mouse.scroll(coords=(center_x, center_y), wheel_dist=scroll_dist)
        time.sleep(1)
    except Exception as e:
        # ถ้าใช้เมาส์ไม่ได้ ให้ลองกดปุ่ม Page Down แทน
        window.type_keys("{PGDN}")

# ==================== SEARCH HELPER ====================

def search_and_select_transaction(main_window, search_text, target_title):
    """
    ฟังก์ชันสำหรับค้นหาด้วยตัวเลข แล้วคลิกรายการ
    """
    # ดึง ID ช่องค้นหาจาก Config (ต้องเพิ่มใน config.ini)
    # ถ้าไม่มีใน config ให้ลองใช้ค่า default หรือปล่อยว่าง
    # SEARCH_BOX_ID = CONFIG.get('GLOBAL', 'SEARCH_BOX_AUTO_ID', fallback='SearchTextBox') 
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']

    print(f"[*] กำลังค้นหารายการด้วยรหัส: {search_text} ...")

    try:
        # 1. หาช่องค้นหาและพิมพ์ตัวเลข
        search_box = main_window.child_window(auto_id=SEARCH_BOX_ID, control_type="Edit")
        
        if search_box.exists(timeout=2):
            search_box.click_input()
            search_box.type_keys("^a{DELETE}") # ล้างค่าเก่า (Ctrl+A -> Delete)
            search_box.type_keys(search_text)  # พิมพ์เลข เช่น 11
            time.sleep(1) # รอให้ระบบ Filter รายการ
        else:
            print(f"[!] ไม่พบช่องค้นหา ID: {SEARCH_BOX_ID} ลองพิมพ์ลงหน้าจอโดยตรง")
            main_window.type_keys(search_text)
            time.sleep(1)

        # 2. ตรวจสอบว่ารายการขึ้นมาหรือไม่
        target_control = main_window.child_window(title=target_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        if target_control.exists(timeout=2):
            print(f"[/] พบรายการ '{target_title}' แล้ว")
            # เรียกใช้ฟังก์ชันทำรายการเดิม
            loan_transaction(main_window, target_title)
        else:
            print(f"[X] FAILED: ค้นหา '{search_text}' แล้วแต่ไม่พบรายการ '{target_title}'")
            
    except Exception as e:
        print(f"[X] Error ในขั้นตอนค้นหา: {e}")


# ==================== MAIN TEST FUNCTION ====================

def loan_main():
    # 1. กำหนดตัวแปรจาก Config
    BT_A_TITLE = B_CFG['BT_A_TITLE']
    BT_L_TITLE = B_CFG['BT_L_TITLE']
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE'] # ไม่ได้ใช้ใน main แต่ดึงมา  
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID'] # ไม่ได้ใช้ใน main แต่ดึงมา
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']

    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' โดยการกดปุ่ม '{BT_A_TITLE}'...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        print("[/] เชื่อมต่อหน้าจอสำเร็จ ")

        # 2. กด A
        main_window.child_window(title=BT_A_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] เข้าสู่หน้า 'บริการสินเชื่อ'...")

        # 3. กด L
        main_window.child_window(title=BT_L_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] กำลังดำเนินการในหน้า 'บริการสินเชื่อ...")

        # --- กด 'อ่านบัตรประชาชน' ---
        print(f"[*] 2.1. ค้นหาและคลิกปุ่ม '{ID_CARD_BUTTON_TITLE}'...")
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

       # --- ค้นหาช่องเลขไปรษณีย์และกรอกข้อมูล ---
        print(f"[*] 2.2.5. กำลังตรวจสอบ/กรอกเลขไปรษณีย์ ID='{POSTAL_CODE_EDIT_AUTO_ID}'")
        postal_control = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    
        #  [จุดที่ 1] ตรวจสอบว่าช่องปรากฏหรือไม่ ก่อน Scroll
        if not postal_control.exists(timeout=1):
            print("[!] ช่องไปรษณีย์ไม่ปรากฏทันที, กำลังเลื่อนหน้าจอลง...")
        
        # ใช้การวนลูป Scroll & Check เพื่อความแม่นยำสูงสุด
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window, CONFIG)
            if postal_control.exists(timeout=1):
                print("[/] ช่องไปรษณีย์พบแล้วหลังการ Scroll")
                found = True
                break

            # ถ้ายังไม่เจอ ให้เลื่อนจอลง
            print(f"[Rotate {i+1}] หาช่องไม่เจอ... กำลังเลื่อนหน้าจอลง...")
            force_scroll_down(main_window, scroll_dist=-5)
            time.sleep(1)
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถหาช่องไปรษณีย์ '{POSTAL_CODE_EDIT_AUTO_ID}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return False # ยกเลิกการทำงานหากหาไม่พบ

        # [จุดที่ 2] ดำเนินการกรอกข้อมูล (เมื่อแน่ใจว่าพบแล้ว)
        if not postal_control.texts()[0].strip():
            # ถ้าช่องว่าง (Empty) ให้ทำการกรอก
            print(f" [-] -> ช่องว่าง, กรอก: {POSTAL_CODE}")
            postal_control.click_input() 
            main_window.type_keys(POSTAL_CODE)
        else:
            print(f" [-] -> ช่องมีค่าอยู่แล้ว: {postal_control.texts()[0].strip()}, ข้ามการกรอก")
        time.sleep(0.5)
    
        # --- ค้นหาช่องหมายเลขโทรศัพท์และกรอกข้อมูล ---
        print(f"[*] 2.2. กำลังตรวจสอบ/กรอกเบอร์โทรศัพท์ ID='{PHONE_EDIT_AUTO_ID}'")
        phone_control = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    
        # [จุดที่ 2] ตรวจสอบ/Scroll ซ้ำเพื่อหาช่องเบอร์โทรศัพท์
        if not phone_control.exists(timeout=1):
            print("[!] ช่องเบอร์โทรศัพท์ไม่ปรากฏทันที, กำลังตรวจสอบ/เลื่อนหน้าจอซ้ำ...")
        
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window, CONFIG)
            if phone_control.exists(timeout=1):
                print("[/] ช่องเบอร์โทรศัพท์พบแล้วหลังการ Scroll")
                found = True
                break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถหาช่องเบอร์โทรศัพท์ '{PHONE_EDIT_AUTO_ID}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return False # ยกเลิกการทำงานหากหาไม่พบ
    
        #  [จุดที่ 3] ดำเนินการกรอกข้อมูล (เมื่อแน่ใจว่าพบแล้ว)
        if not phone_control.texts()[0].strip():
            print(f" [-] -> ช่องว่าง, กรอก: {PHONE_NUMBER}")
            phone_control.click_input()
            main_window.type_keys(PHONE_NUMBER)
        else:
            print(f" [-] -> ช่องมีค่าอยู่แล้ว: {phone_control.texts()[0].strip()}, ข้ามการกรอก")
        time.sleep(0.5)

    # --- กด 'ถัดไป' เพื่อยืนยัน ---
        print(f"[*] 2.3. กดปุ่ม '{NEXT_TITLE}' เพื่อไปหน้าถัดไป...")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
    
        print("\n[V] SUCCESS: ดำเนินการขั้นตอน สำเร็จ!")
        return True
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดใน : {e}")
        return False
    
# ----------------- ฟังก์ชันแม่แบบสำหรับรายการย่อย -----------------

def loan_transaction(main_window, transaction_title):
    """ฟังก์ชันที่ใช้ร่วมกันสำหรับรายการย่อยทั้งหมด"""
    
    # 1. กำหนดตัวแปรจาก Config
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
    
    try:
        # 2. คลิกรายการย่อย
        print(f"[*] 2. ค้นหาและคลิกรายการ: {transaction_title}")
        main_window.child_window(title=transaction_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 3. คลิก 'ถัดไป'
        print(f"[*] 3. กดปุ่ม '{NEXT_TITLE}'")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 4. คลิก 'เสร็จสิ้น'
        print(f"[*] 4. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดในการทำรายการย่อย {transaction_title}: {e}")
        

# ---------------ฟังก์ชันย่อยตามโครงสร้างเดิม (เรียกใช้ Config)---------------------

def loan_services1():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 1)...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        loan_transaction(main_window, S_CFG['LOAN_1_TITLE'])

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services2():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 2)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        loan_transaction(main_window, S_CFG['LOAN_2_TITLE'])

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services3():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 3)...")
    try:
        if not loan_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        loan_transaction(main_window, S_CFG['LOAN_3_TITLE'])

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services4():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 4)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        loan_transaction(main_window, S_CFG['LOAN_4_TITLE'])

    except Exception as e:

        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services5():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 5)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()


        loan_transaction(main_window, S_CFG['LOAN_5_TITLE'])

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services6():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 6)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

       
        loan_transaction(main_window, S_CFG['LOAN_6_TITLE'])

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services7():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 7)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        
        loan_transaction(main_window, S_CFG['LOAN_7_TITLE'])

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services8():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 8)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        loan_transaction(main_window, S_CFG['LOAN_8_TITLE'])

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services9():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 9)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        loan_transaction(main_window, S_CFG['LOAN_9_TITLE'])

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")
    
def loan_services10():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 10)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # เพิ่มการตรวจสอบ/Scroll
        SERVICE_TITLE = S_CFG['LOAN_10_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
        
        loan_transaction(main_window,SERVICE_TITLE)

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

# # ==================== SERVICES 11-19 (SEARCH MODE) ====================

# def loan_services11():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 11)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         # ใช้การค้นหาด้วยเลข "11"
#         search_and_select_transaction(main_window, "50672", S_CFG['LOAN_11_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# def loan_services12():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 12)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         search_and_select_transaction(main_window, "50672", S_CFG['LOAN_12_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# def loan_services13():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 13)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         search_and_select_transaction(main_window, "50696", S_CFG['LOAN_13_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# def loan_services14():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 14)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         search_and_select_transaction(main_window, "50836", S_CFG['LOAN_14_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# def loan_services15():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 15)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         search_and_select_transaction(main_window, "50856", S_CFG['LOAN_15_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# def loan_services16():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 16)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         search_and_select_transaction(main_window, "50930", S_CFG['LOAN_16_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# def loan_services17():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 17)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         search_and_select_transaction(main_window, "51008", S_CFG['LOAN_17_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# def loan_services18():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 18)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         search_and_select_transaction(main_window, "52040", S_CFG['LOAN_18_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# def loan_services19():
#     print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 19)...")
#     try:
#         if not loan_main(): return
#         app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
#         main_window = app.top_window()

#         search_and_select_transaction(main_window, "52043", S_CFG['LOAN_19_TITLE'])

#     except Exception as e:
#         print(f"\n[x] FAILED: {e}")

# ==================== SERVICES 11-19 (Config Variable Mode) ====================

def run_service_by_config(service_num):
    """ฟังก์ชันช่วยรัน โดยดึงค่า CODE และ TITLE จาก Config ตามเลขข้อ"""
    print(f"\n{'='*50}\n[*] กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ {service_num})...")
    try:
        # 1. เข้าหน้า Main
        if not loan_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # 2. ดึงค่าจาก Config
        # สร้าง Key อัตโนมัติ เช่น 'LOAN_18_CODE' และ 'LOAN_18_TITLE'
        code_key = f'LOAN_{service_num}_CODE'
        title_key = f'LOAN_{service_num}_TITLE'
        
        search_code = S_CFG[code_key]   # ดึงเลขรหัส (เช่น 52040)
        target_title = S_CFG[title_key] # ดึงชื่อปุ่ม (เช่น 52040)

        # 3. ส่งค่าตัวแปรไปค้นหาและคลิก
        search_and_select_transaction(main_window, search_code, target_title)

    except Exception as e:
        print(f"\n[x] FAILED รายการ {service_num}: {e}")

# ----- ฟังก์ชันเรียกใช้งาน -----

def loan_services11():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 11)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [จุดที่แก้ไข]: เรียกใช้ฟังก์ชันค้นหาแทน loan_transaction เดิม
        # โดยดึงค่า Code และ Title มาจากตัวแปร S_CFG (Config) โดยตรง
        search_and_select_transaction(
            main_window, 
            S_CFG['LOAN_11_CODE'],   # รหัสค้นหา (เช่น 50636)
            S_CFG['LOAN_11_TITLE']   # ชื่อปุ่ม (เช่น 50636)
        )

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services12():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 12)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [จุดที่แก้ไข]: เรียกใช้ฟังก์ชันค้นหาแทน loan_transaction เดิม
        # โดยดึงค่า Code และ Title มาจากตัวแปร S_CFG (Config) โดยตรง
        search_and_select_transaction(
            main_window, 
            S_CFG['LOAN_12_CODE'],   # รหัสค้นหา (เช่น 50636)
            S_CFG['LOAN_12_TITLE']   # ชื่อปุ่ม (เช่น 50636)
        )

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services13():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 12)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [จุดที่แก้ไข]: เรียกใช้ฟังก์ชันค้นหาแทน loan_transaction เดิม
        # โดยดึงค่า Code และ Title มาจากตัวแปร S_CFG (Config) โดยตรง
        search_and_select_transaction(
            main_window, 
            S_CFG['LOAN_13_CODE'],   # รหัสค้นหา (เช่น 50636)
            S_CFG['LOAN_13_TITLE']   # ชื่อปุ่ม (เช่น 50636)
        )

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services14():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 12)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [จุดที่แก้ไข]: เรียกใช้ฟังก์ชันค้นหาแทน loan_transaction เดิม
        # โดยดึงค่า Code และ Title มาจากตัวแปร S_CFG (Config) โดยตรง
        search_and_select_transaction(
            main_window, 
            S_CFG['LOAN_14_CODE'],   # รหัสค้นหา (เช่น 50636)
            S_CFG['LOAN_14_TITLE']   # ชื่อปุ่ม (เช่น 50636)
        )

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services15():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 12)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [จุดที่แก้ไข]: เรียกใช้ฟังก์ชันค้นหาแทน loan_transaction เดิม
        # โดยดึงค่า Code และ Title มาจากตัวแปร S_CFG (Config) โดยตรง
        search_and_select_transaction(
            main_window, 
            S_CFG['LOAN_15_CODE'],   # รหัสค้นหา (เช่น 50636)
            S_CFG['LOAN_15_TITLE']   # ชื่อปุ่ม (เช่น 50636)
        )

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services16():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 12)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [จุดที่แก้ไข]: เรียกใช้ฟังก์ชันค้นหาแทน loan_transaction เดิม
        # โดยดึงค่า Code และ Title มาจากตัวแปร S_CFG (Config) โดยตรง
        search_and_select_transaction(
            main_window, 
            S_CFG['LOAN_16_CODE'],   # รหัสค้นหา (เช่น 50636)
            S_CFG['LOAN_16_TITLE']   # ชื่อปุ่ม (เช่น 50636)
        )

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services17():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 12)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [จุดที่แก้ไข]: เรียกใช้ฟังก์ชันค้นหาแทน loan_transaction เดิม
        # โดยดึงค่า Code และ Title มาจากตัวแปร S_CFG (Config) โดยตรง
        search_and_select_transaction(
            main_window, 
            S_CFG['LOAN_17_CODE'],   # รหัสค้นหา (เช่น 50636)
            S_CFG['LOAN_17_TITLE']   # ชื่อปุ่ม (เช่น 50636)
        )

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services18():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการสินเชื่อ' (รายการ 12)...")
    try:
        if not loan_main(): return

        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [จุดที่แก้ไข]: เรียกใช้ฟังก์ชันค้นหาแทน loan_transaction เดิม
        # โดยดึงค่า Code และ Title มาจากตัวแปร S_CFG (Config) โดยตรง
        search_and_select_transaction(
            main_window, 
            S_CFG['LOAN_18_CODE'],   # รหัสค้นหา (เช่น 50636)
            S_CFG['LOAN_18_TITLE']   # ชื่อปุ่ม (เช่น 50636)
        )

    except Exception as e:
        print(f"\n[x] FAILED ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def loan_services19():
    print(f"\n{'='*50}\n[*] พิเศษ: กำลังทำรายการ 19 (แบบเขียนแยกเอง)...")
    
    # 1. เรียก Logic ส่วนกลางมาใช้ (ถ้าต้องการ)
    if not loan_main(): return
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    
    # 2. ดึงค่า Config มาเอง
    code = S_CFG['LOAN_19_CODE']
    title = S_CFG['LOAN_19_TITLE']
    
    # 3. สั่งค้นหาและทำรายการ
    # (ตรงนี้คุณสามารถแทรกคำสั่งพิเศษเฉพาะของข้อ 19 ได้)
    print("--- ขั้นตอนพิเศษเฉพาะข้อ 19 ---")
    time.sleep(5) 
    
    search_and_select_transaction(app.top_window(), code, title)

if __name__ == "__main__":
    loan_main()
    loan_services1()
    loan_services2()
    loan_services3()
    loan_services4()
    loan_services5()
    loan_services6()
    loan_services7()
    loan_services8()
    loan_services9()
    loan_services10()
    loan_services11()
    loan_services12()
    loan_services13()
    loan_services14()
    loan_services15()
    loan_services16()
    loan_services17()
    loan_services18()
    loan_services19()  