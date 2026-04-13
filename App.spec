# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['App.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('credentials.json', '.'),   # bundled alongside the app
    ],
    hiddenimports=[
        'google.auth.transport.requests',
        'google.oauth2.credentials',
        'google_auth_oauthlib.flow',
        'googleapiclient.discovery',
        'googleapiclient._helpers',
        'googleapiclient.errors',
        'googleapiclient.http',
        'google.auth.crypt',
        'google.auth.crypt._python_rsa',
        'google.auth.crypt._helpers',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RotationsManagementApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,    # no terminal window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RotationsManagementApp',
)

app = BUNDLE(
    coll,
    name='RotationsManagementApp.app',
    icon=None,
    bundle_identifier='com.rotations.management',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
    },
)
