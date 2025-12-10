from pywinauto.application import Application
import time
import configparser
import os
import sys

# Config
CONFIG_FILE = "config.ini"

# ส่วนจัดการ Config 

def read_config(filename=CONFIG_FILE):
    """อ่านและโหลดค่าจากไฟล์ config.ini"""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] FAILED: ไม่พบไฟล์ {filename} ที่พาธ: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        return config
    except Exception as e:
        print(f"[X] FAILED: ไม่สามารถอ่านไฟล์ {filename} ได้: {e}")
        return configparser.ConfigParser()

# โหลด config ล่วงหน้า
CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้ โปรดตรวจสอบไฟล์และพาธ")
    sys.exit(1)

# ดึงค่า Global ที่ใช้ร่วมกัน
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE']
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

# ดึง Section หลัก
B_CFG = CONFIG['INSURANCE_BT']
S_CFG = CONFIG['INSURANCE_POS_SUB_TRANSACTIONS']

def insurance_main():
    BT_A_TITLE = B_CFG['BT_A_TITLE']
    BT_I_TITLE = B_CFG['BT_I_TITLE']
    ID_CARD_BUTTON_TITLE = B_CFG['ID_CARD_BUTTON_TITLE']
    PHONE_EDIT_AUTO_ID = B_CFG['PHONE_EDIT_AUTO_ID']
    NEXT_BUTTON_TITLE = B_CFG['NEXT_BUTTON_TITLE']
    NEXT_BUTTON_AUTO_ID = B_CFG['NEXT_BUTTON_AUTO_ID']
    

    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่ ... '{BT_A_TITLE}'...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window= app.top_window()
        print("[/] เชื่อมต่อหน้าจอสำเร็จ")

        main_window.child_window(title=BT_A_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] กำลังดำเนินการในหน้า ...")

        main_window.child_window(title=BT_I_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] กำลังดำเนินการในหน้า ...")

        # อ่านปชช
        print(f"[*] 2.1. ค้นหาและคลิกปุ่ม '{ID_CARD_BUTTON_TITLE}'...")
        main_window.child_window(title=ID_CARD_BUTTON_TITLE,control_type="Text").click_input()

        # หมายเลขทศ.
        print(f"[*] 2.3. กำลังค้นหาช่องกรอกด้วย ID='{PHONE_EDIT_AUTO_ID}' และกรอก: {PHONE_NUMBER}...")
        main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit").click_input()
        main_window.type_keys(PHONE_NUMBER)

        print(f"[*] 2.3. กำลังค้นหาช่องกรอกเลขไปรษณีย์ ID='{POSTAL_CODE_EDIT_AUTO_ID}' และกรอก: {POSTAL_CODE}...")
        # โค้ดใช้ตัวแปร Global ที่ดึงมาจากด้านบน
        main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit").click_input() 
        main_window.type_keys(POSTAL_CODE)

        # --- กด 'ถัดไป' เพื่อยืนยัน ---
        print(f"[*] 2.4. กดปุ่ม '{NEXT_BUTTON_TITLE}' เพื่อไปหน้าถัดไป...")
        main_window.child_window(title=NEXT_BUTTON_TITLE, auto_id=NEXT_BUTTON_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print("\n[V] SUCCESS: ดำเนินการขั้นตอน Bank POS (ผู้ฝากส่ง) สำเร็จ!")
        return True
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดใน bank_pos_navigate_main: {e}")
        return False
    
# -------------------------------------------------------
def run_insurance_service(main_window, transaction_title):
    """ฟังก์ชันที่ใช้ร่วมกันสำหรับรายการย่อยทั้งหมด"""
    
    # ตัวแปร config
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_BUTTON_TITLE = B_CFG['NEXT_BUTTON_TITLE']
    NEXT_BUTTON_AUTO_ID = B_CFG['NEXT_BUTTON_AUTO_ID']
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
    
    try:
        # 2. คลิกรายการย่อย
        print(f"[*] 2. ค้นหาและคลิกรายการ: {transaction_title}")
        main_window.child_window(title=transaction_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 3. 'ถัดไป'
        print(f"[*] 3. กดปุ่ม '{NEXT_BUTTON_TITLE}'")
        main_window.child_window(title=NEXT_BUTTON_TITLE, auto_id=NEXT_BUTTON_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 4. 'เสร็จสิ้น'
        print(f"[*] 4. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดในการทำรายการย่อย {transaction_title}: {e}")

# -------------------------------------------

def insurance_navigate1():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 1)...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_1_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def insurance_navigate2():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 2)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_2_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def insurance_navigate3():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 3)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_3_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def insurance_navigate4():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 4)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_4_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def insurance_navigate5():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 5)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_5_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def insurance_navigate6():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 6)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_6_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate7():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 7)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_7_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")           

def insurance_navigate8():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 8)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_8_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate9():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 9)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_9_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")       

def insurance_navigate10():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 10)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_10_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate11():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 11)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_11_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")    

def insurance_navigate12():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 12)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_12_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate13():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 13)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_13_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate14():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 14)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_14_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate15():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 15)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_15_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")    

def insurance_navigate16():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 16)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_16_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate17():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 17)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_17_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")    

def insurance_navigate18():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 18)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_18_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate19():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 19)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_19_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")    

def insurance_navigate20():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 20)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_20_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate21():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 21)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_21_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")    

def insurance_navigate22():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 22)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_22_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")  

def insurance_navigate23():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'ตัวแทนธนาคาร' (รายการ 23)...")
    try:
        if not insurance_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        run_insurance_service(main_window, S_CFG['TRANSACTION_23_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")    



# ----------------- Main Execution -----------------

if __name__ == "__main__":
    insurance_main()



