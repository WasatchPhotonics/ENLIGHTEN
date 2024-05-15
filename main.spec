# -*- mode: python ; coding: utf-8 -*-


a = Analysis(   ['scripts/Enlighten.py'],
                pathex=['../Wasatch.PY',
                        '.',
                        'enlighten',
                        'enlighten/assets/uic_qrc',
                        'enlighten/assets/stylesheets',
                        'enlighten/measurement',
                        'enlighten/Plugins',
                        'plugins'],
                binaries=[],
                datas=[('scripts/support_files/libusb_drivers/amd64/libusb0.dll', '.'),
                       ('enlighten/assets/stylesheets', './enlighten/assets/stylesheets/')],
                hiddenimports=[ 'scipy._lib.messagestream', 
                                'scipy.special.cython_special', 
                                'tensorflow', 
                                'tensorflow.python.data.ops.shuffle_op'],
                hookspath=[],
                hooksconfig={},
                runtime_hooks=[],
                excludes=['_bootlocale'],
                noarchive=False,
                optimize=0,
)


pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('X utf8', None, 'OPTION')],
    exclude_binaries=True,
    name='Enlighten',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['enlighten\\assets\\uic_qrc\\images\\EnlightenIcon.ico'],
    hide_console='hide-early',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Enlighten',
)