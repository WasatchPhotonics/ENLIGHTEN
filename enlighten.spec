# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/enlighten/Enlighten.py'],
    pathex=['src/enlighten/assets/uic_qrc'],
    binaries=[],
    datas=[('scripts\\support_files\\libusb_drivers\\amd64\\libusb0.dll', '.'),
            ('src/enlighten/assets/stylesheets', 'src/enlighten/assets/stylesheets')],
    hiddenimports=[
        'numpy.core._multiarray_umath',
        'scipy._lib.messagestream',
        'scipy._lib.array_api_compat.numpy.fft',
        'scipy.special._special_ufuncs',
        'scipy.special.cython_special',
        'tensorflow',
        'tensorflow.python.data.ops.shuffle_op'
    ],
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
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\enlighten\\assets\\uic_qrc\\images\\EnlightenIcon.ico'],
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
