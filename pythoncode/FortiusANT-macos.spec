# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['FortiusAnt.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                ( './FortiusAnt.icns',               '.' ),
                ( './FortiusAnt.ico',                '.' ),
                ( './FortiusAnt.jpg',                '.' ),
                ( './heart.jpg',                     '.' ),
                ( './settings.bmp',                  '.' ),
                ( './sponsor.bmp',                   '.' ),
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
          [],
          exclude_binaries=True,
          name='FortiusAnt',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='FortiusAnt')

app = BUNDLE(coll,
         name='FortiusAnt.app',
         icon='FortiusAnt.icns',
         bundle_identifier=None)               
