# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None
pg_datas, pg_binaries, pg_hiddenimports = collect_all('pygame')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=pg_binaries,
    datas=[
        ('tour_teresina_golf/assets/fonts/PressStart2P-Regular.ttf', 'tour_teresina_golf/assets/fonts'),
        ('fases/fase1/fase1.png', 'fases/fase1'),
        ('fases/fase1/fase1_mapa_colisoes.png', 'fases/fase1'),
        ('fases/fase2/fase2.png', 'fases/fase2'),
        ('fases/fase2/fase2_mapa_colisao.png', 'fases/fase2'),
        ('fases/fase2/fase2_mapa_colisoes.png', 'fases/fase2'),
        ('fases/fase3/fase3.png', 'fases/fase3'),
        ('fases/fase3/fase3_mapa_colisao.png', 'fases/fase3'),
        ('acessorios/bandeira.png', 'acessorios'),
        ('Menus/intro.png', 'Menus'),
        ('telas/Tela de Derrota.png', 'telas'),
        ('telas/Tela de vitória.png', 'telas'),
        ('botoes/Voltar_ao_Menu-removebg-preview.png', 'botoes'),
        ('botoes/Reiniciar_Fase-removebg-preview.png', 'botoes'),
        ('botoes/Proxima_Fase-removebg-preview.png', 'botoes'),
    ] + pg_datas,
    hiddenimports=[
        'fases',
        'fases.fase1',
        'fases.fase1.fase1_colisoes',
        'fases.fase2',
        'fases.fase2.fase2_colisoes',
        'fases.fase3',
        'fases.fase3.fase3_colisoes',
    ] + pg_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'email', 'html', 'http', 'urllib', 'xml', 'pydoc', 'doctest', 'difflib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TourTeresinaGolf',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
