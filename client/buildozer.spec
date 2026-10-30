[app]
title = Avtomoyka
package.name = autowash
package.domain = org.kuts
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.3.1,requests,urllib3,idna,chardet,certifi,openssl
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = 1
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0
