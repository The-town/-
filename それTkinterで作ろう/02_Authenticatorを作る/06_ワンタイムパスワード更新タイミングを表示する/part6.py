import hmac
import time
import base64
import struct
import hashlib

import tkinter
from tkinter import ttk
from qreader import QReader
from PIL import ImageGrab
import numpy as np
import re


class TOTPAuthenticator:
    def __init__(self, secret_key: str, digits: int = 6, time_step: int = 30, hash_algorithm: str = 'sha1'):
        """
        TOTPオーセンティケーターの初期化
        
        Args:
            secret_key: Base32エンコードされた秘密鍵
            digits: TOTPコードの桁数（デフォルト: 6）
            time_step: タイムステップ（秒）（デフォルト: 30）
            hash_algorithm: ハッシュアルゴリズム（デフォルト: sha1）
        """
        self.secret_key = self._decode_base32(secret_key)
        self.digits = digits
        self.time_step = time_step
        self.hash_algorithm = hash_algorithm

    def _decode_base32(self, secret_key: str) -> bytes:
        """Base32エンコードされた秘密鍵をデコード"""
        # パディングを追加
        padding = '=' * ((8 - len(secret_key)) % 8)
        return base64.b32decode(secret_key.upper() + padding)

    def _get_counter(self, timestamp: int = None) -> bytes:
        """現在時刻からカウンター値を生成"""
        if timestamp is None:
            timestamp = int(time.time())
        counter = timestamp // self.time_step
        return struct.pack('>Q', counter)

    def generate_totp(self, timestamp: int = None) -> str:
        """
        TOTPコードを生成
        
        Args:
            timestamp: Unix時間（省略時は現在時刻）
            
        Returns:
            生成されたTOTPコード
        """
        # カウンター値の生成
        counter = self._get_counter(timestamp)
        
        # HMACの計算
        hmac_obj = hmac.new(
            self.secret_key,
            counter,
            getattr(hashlib, self.hash_algorithm)
        )
        hmac_result = hmac_obj.digest()
        
        # 動的切り捨て
        offset = hmac_result[-1] & 0xf
        code_bytes = hmac_result[offset:offset + 4]
        code_int = struct.unpack('>I', code_bytes)[0]
        code_int &= 0x7fffffff
        
        # 指定桁数に変換
        code = str(code_int % (10 ** self.digits))
        return code.zfill(self.digits)

    def verify_totp(self, code: str, timestamp: int = None, window: int = 1) -> bool:
        """
        TOTPコードを検証
        
        Args:
            code: 検証するTOTPコード
            timestamp: Unix時間（省略時は現在時刻）
            window: 検証する時間窓の数（前後）
            
        Returns:
            検証結果（True/False）
        """
        if timestamp is None:
            timestamp = int(time.time())
            
        for i in range(-window, window + 1):
            current_timestamp = timestamp + (i * self.time_step)
            if self.generate_totp(current_timestamp) == code:
                return True
        return False


class QrCodeReader:
    def __init__(self, master) -> None:
        self.frame = tkinter.Frame(master)
        self.frame.grid(column=0, row=0)
        
        qr_img = tkinter.PhotoImage(file="./code/02/qrcode.png").subsample(3, 3)

        self.qr_read_button = tkinter.Button(self.frame, command=self.qr_read, image=qr_img)
        self.qr_read_button.image = qr_img
        self.qr_read_button.grid(column=0, row=0, padx=10, pady=10)

    def qr_read(self, event=None):
        clipboard_img = ImageGrab.grabclipboard()
        if clipboard_img:
            pilimg = np.array(clipboard_img, dtype=np.uint8)

            qreader = QReader()

            qrdata = qreader.detect_and_decode(pilimg[..., :3])
            if len(qrdata) > 0:
                global _qrdata
                _qrdata = qrdata[0]
                root.event_generate("<<qrread>>")


class OTPPreviewer:
    def __init__(self, master) -> None:
        self.frame = tkinter.Frame(master)
        self.frame.grid(column=0, row=1, sticky="ew")
        self.frame.grid_columnconfigure(index=0, weight=1)
        self.frame.grid_rowconfigure(index=[0, 1], weight=1)
        self.frame.anchor("center")
        
        self.progressbar_var = tkinter.DoubleVar(self.frame, value=time.time() % 30)
        self.progressbar = ttk.Progressbar(self.frame, orient="horizontal", length=200, maximum=30, 
                                           mode="determinate", variable=self.progressbar_var)
        self.progressbar.grid(column=0, row=0, columnspan=2, padx=20, pady=10, sticky="ew")

        scrollbar = tkinter.Scrollbar(self.frame)
        scrollbar.grid(column=1, row=1, sticky="ns")
        self.otp_list = tkinter.StringVar(self.frame)
        self.otp_listbox = tkinter.Listbox(self.frame, listvariable=self.otp_list, width=40, font=("メイリオ", 11),
                                           yscrollcommand=scrollbar.set, activestyle="none")
        scrollbar["command"] = self.otp_listbox.yview
        self.otp_listbox.grid(column=0, row=1, padx=20, pady=10, sticky="ew")        

        root.bind("<<qrread>>", self.add_qrdata)

        self.authenticators = {}

        self.create_totp()

    def add_qrdata(self, event=None):
        result = self.validate(_qrdata)
        if result:
            self.add_authenticator(result["name"], result["secret"])

    def validate(self, data):
        match = re.match(r"otpauth://totp/(?P<name>[^/?]*)\?secret=(?P<secret>.*)\&issuer=(?P<issuer>.*)", data)
        if match:
            return {"name": match.group("name"), "secret": match.group("secret"), "issuer": match.group("issuer")}
        
    def add_authenticator(self, name, secret):
        self.authenticators[name] = TOTPAuthenticator(secret)

    def create_totp(self):
        tmp = []
        for name in self.authenticators.keys():
            tmp.append(f"{name}：{self.authenticators[name].generate_totp()}")
        
        self.otp_list.set(" ".join(tmp))

        self.progressbar_var.set(time.time() % 30)
        root.after(100, self.create_totp)


root = tkinter.Tk()
root.geometry("300x500")
root.title("Authenticator")
root.anchor("center")

root.grid_columnconfigure(index=0, weight=1)
root.grid_rowconfigure(index=[0, 1], weight=1)

qrcodereader = QrCodeReader(root)
otppreviwer = OTPPreviewer(root)

_qrdata = ""

root.mainloop()
