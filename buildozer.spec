[app]

title = MoodBot
package.name = moodbot
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt,ttf,ttc,cfg
version = 0.3.0

# 注意：onnxruntime-python不能直接安卓编译，若要用onnxruntime-android需要特殊whl；
# jieba是纯Python库，不需要numpy
requirements = python3,kivy,jieba

android.api = 33
android.ndk = 25b

android.permissions = INTERNET,ACCESS_NETWORK_STATE

android.icon = icon.png
android.adaptive_icon_foreground = icon_foreground.png
android.adaptive_icon_background = icon_background.png

android.build_type = debug
android.minapi = 24

android.archs = arm64-v8a

p4a.bootstrap = sdl2

fullscreen = 0
orientation = portrait

# 软键盘模式：adjustResize 让窗口在键盘弹出时自动缩小，
# 配合Kivy的Window.size监听实现输入框跟随键盘联动
android.windowsoftinputmode = adjustResize

android.use_aapt2 = True
android.copy_libs = True
android.delete_android_assets = True

# 字体不要放assets！放到source.dir，source.include_exts会打包进app私有目录，代码直接相对路径加载
# fonts/msyh.ttc fonts/seguiemj.ttf 保留在项目目录，不需要add_assets

[buildozer]
log_level = 2
warn_on_root = 1