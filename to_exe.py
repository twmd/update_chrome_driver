import PyInstaller.__main__

PyInstaller.__main__.run([
    'ucd.py',
    '--name=UpdateChromeDriver_v2',
    '--onefile',
    # '--debug=all',
])
