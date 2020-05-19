# -*- mode: python ; coding: utf-8 -*-
#
# used with command: pyinstaller MakeFortiusANT.spec
#
# Version info
# 2020-03-02    Firmware .hex added
# 2020-04-08    Gearbox.jpg added

block_cipher = None

a = Analysis(['FortiusANT.py'],
             pathex=['C:\\Github\\WouterJD\\FortiusANT\\pythoncode'],
             binaries=[
                ( 'C:\\Windows\\System32\\libusb0.dll', '.')
             ],
             datas=[
                ( './FortiusAnt.ico',                '.' ),
                ( './FortiusAnt.jpg',                '.' ),
                ( './Heart.jpg',                     '.' ),
                ( './tacxfortius_1942_firmware.hex', '.' ),
                ( './tacximagic_1902_firmware.hex',  '.' )
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='FortiusANT',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='FortiusANT.ico')
