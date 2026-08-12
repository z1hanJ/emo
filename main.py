#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
import traceback

try:
    from kivy.utils import platform
except ImportError:
    platform = 'windows'

# jieba初始化：Android端需要特殊处理字典路径
_jieba_ok = False
try:
    import jieba
    if platform == 'android':
        # Android: jieba字典在app打包目录中
        _app_dir = os.path.dirname(os.path.abspath(__file__))
        _dict_path = os.path.join(_app_dir, 'jieba', 'dict.txt')
        if os.path.exists(_dict_path):
            jieba.set_dictionary(_dict_path)
        # 也尝试常见Android路径
        else:
            for p in [
                '/data/data/org.example.moodbot/files/app/jieba/dict.txt',
                os.path.join(_app_dir, 'dict.txt'),
            ]:
                if os.path.exists(p):
                    jieba.set_dictionary(p)
                    break
    jieba.initialize()
    _jieba_ok = True
except Exception as e:
    print(f"[WARN] jieba初始化失败: {e}")
    _jieba_ok = False

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.metrics import dp
from kivy.core.window import Window

if platform != 'android':
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '700')
    Config.set('graphics', 'minimum_width', '300')
    Config.set('graphics', 'minimum_height', '500')
    Config.set('graphics', 'window_state', 'hidden')

# Android: 隐藏窗口边框/标题栏，防止出现系统控制按钮
if platform == 'android':
    from kivy.config import Config as _Cfg
    _Cfg.set('graphics', 'borderless', '1')

# Android端跳过可能导致问题的Config设置
if platform != 'android':
    Config.set('kivy', 'log_dir', os.path.dirname(os.path.abspath(__file__)))
    Config.set('kivy', 'log_level', 'info')
    Config.set('kivy', 'keyboard_mode', 'system')
    Config.set('kivy', 'keyboard_layout', 'qwerty')
    Config.set('input', 'keyboard', 'system')

def get_app_root():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    if platform == 'android':
        # Android: 尝试多种方式获取app根目录
        try:
            from android import app as android_app
            return android_app.get_app_root_dir()
        except Exception:
            pass
        # 回退到__file__所在目录
        return os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.abspath(__file__))

def prepare_fonts():
    app_root = get_app_root()
    font_dir = os.path.join(app_root, 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    
    import shutil
    
    if platform in ('windows', 'win'):
        font_sources = [
            ('C:/Windows/Fonts/msyh.ttc', os.path.join(font_dir, 'msyh.ttc')),
            ('C:/Windows/Fonts/seguiemj.ttf', os.path.join(font_dir, 'seguiemj.ttf')),
            ('C:/Windows/Fonts/simhei.ttf', os.path.join(font_dir, 'simhei.ttf')),
            ('C:/Windows/Fonts/simsun.ttc', os.path.join(font_dir, 'simsun.ttc')),
        ]
        for src, dst in font_sources:
            if os.path.exists(src) and not os.path.exists(dst):
                try:
                    shutil.copy2(src, dst)
                    print(f"📥 复制字体: {os.path.basename(src)} -> {dst}")
                except Exception as e:
                    print(f"📤 复制字体失败 {src}: {e}")
    
    print(f"📁 字体目录: {font_dir}")
    if os.path.exists(font_dir):
        print(f"📄 字体文件列表: {os.listdir(font_dir)}")

def register_fonts():
    chinese_font = None
    emoji_font = None
    app_root = get_app_root()
    
    prepare_fonts()
    
    font_dir = os.path.join(app_root, 'fonts')
    if not os.path.exists(font_dir):
        font_dir = app_root
    
    print(f"📁 应用根目录: {app_root}")
    print(f"📁 字体目录: {font_dir}")
    
    if platform in ('windows', 'win'):
        chinese_candidates = [
            os.path.join(font_dir, 'msyh.ttc'),
            os.path.join(app_root, 'msyh.ttc'),
            os.path.join(app_root, '_internal', 'msyh.ttc'),
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/msyhbd.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/msyhl.ttc',
        ]
        emoji_candidates = [
            os.path.join(font_dir, 'seguiemj.ttf'),
            os.path.join(app_root, 'seguiemj.ttf'),
            os.path.join(app_root, '_internal', 'seguiemj.ttf'),
            'C:/Windows/Fonts/seguiemj.ttf',
            'C:/Windows/Fonts/seguiemja.ttf',
            'C:/Windows/Fonts/seguiemjb.ttf',
            'C:/Windows/Fonts/segoeui.ttf',
            'C:/Windows/Fonts/msyh.ttc',
        ]
    elif platform == 'android':
        chinese_candidates = [
            os.path.join(font_dir, 'NotoSansCJK-Regular.ttc'),
            os.path.join(font_dir, 'DroidSansFallback.ttf'),
            os.path.join(font_dir, 'msyh.ttc'),
            os.path.join(app_root, 'NotoSansCJK-Regular.ttc'),
            os.path.join(app_root, 'DroidSansFallback.ttf'),
            os.path.join(app_root, 'msyh.ttc'),
            '/system/fonts/DroidSansFallback.ttf',
            '/system/fonts/NotoSansCJK-Regular.ttc',
            '/system/fonts/NotoSansSC-Regular.otf',
            '/system/fonts/NotoSansSC-Regular.ttf',
            '/system/fonts/NotoSerifCJK-Regular.ttc',
            '/system/fonts/SourceHanSansSC-Regular.otf',
            '/system/fonts/SourceHanSerifSC-Regular.otf',
            '/data/data/org.example.moodbot/files/app/NotoSansCJK-Regular.ttc',
            '/data/data/org.example.moodbot/files/app/msyh.ttc',
        ]
        emoji_candidates = [
            os.path.join(font_dir, 'NotoColorEmoji.ttf'),
            os.path.join(font_dir, 'NotoEmoji-Regular.ttf'),
            os.path.join(font_dir, 'seguiemj.ttf'),
            os.path.join(app_root, 'NotoColorEmoji.ttf'),
            os.path.join(app_root, 'seguiemj.ttf'),
            '/system/fonts/NotoColorEmoji.ttf',
            '/system/fonts/NotoEmoji-Regular.ttf',
            '/system/fonts/Emoji.ttf',
            '/system/fonts/SamsungColorEmoji.ttf',
            '/system/fonts/AppleColorEmoji.ttf',
            '/data/data/org.example.moodbot/files/app/NotoColorEmoji.ttf',
        ]
    elif platform == 'linux':
        chinese_candidates = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            os.path.join(font_dir, 'NotoSansCJK-Regular.ttc'),
        ]
        emoji_candidates = [
            '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',
            '/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf',
            os.path.join(font_dir, 'NotoColorEmoji.ttf'),
        ]
    else:
        chinese_candidates = []
        emoji_candidates = []
    
    print(f"🔍 中文字体候选列表 ({len(chinese_candidates)}个):")
    for i, path in enumerate(chinese_candidates):
        exists = os.path.exists(path)
        print(f"  {i+1}. {path} {'✓ 存在' if exists else '✗ 不存在'}")
    
    print(f"🔍 表情字体候选列表 ({len(emoji_candidates)}个):")
    for i, path in enumerate(emoji_candidates):
        exists = os.path.exists(path)
        print(f"  {i+1}. {path} {'✓ 存在' if exists else '✗ 不存在'}")
    
    for font_path in chinese_candidates:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='Chinese', fn_regular=font_path)
                chinese_font = 'Chinese'
                print(f"✅ 已注册中文字体: {font_path}")
                break
            except Exception as e:
                print(f"❌ 注册中文字体失败 {font_path}: {e}")
    
    if not chinese_font:
        print("⚠️ 未能注册中文字体，将使用系统默认字体")
    
    for font_path in emoji_candidates:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='Emoji', fn_regular=font_path)
                emoji_font = 'Emoji'
                print(f"✅ 已注册表情字体: {font_path}")
                break
            except Exception as e:
                print(f"❌ 注册表情字体失败 {font_path}: {e}")
    
    if not emoji_font:
        print("⚠️ 未能注册表情字体，将使用中文字体或系统字体显示表情")
        emoji_font = chinese_font
    
    return chinese_font, emoji_font

# 字体注册：包裹在try-except中防止Android启动崩溃
try:
    CHINESE_FONT, EMOJI_FONT = register_fonts()
except Exception as e:
    print(f"[WARN] 字体注册失败: {e}")
    CHINESE_FONT = None
    EMOJI_FONT = None

PINYIN_DICT = {
    'bu': ['不', '布', '步', '部', '补', '捕', '簿', '卜'],
    'kai': ['开', '凯', '楷', '慨'],
    'xin': ['心', '新', '信', '辛', '欣', '薪', '鑫', '芯'],
    'hao': ['好', '号', '豪', '浩', '耗', '毫', '昊'],
    'nan': ['难', '南', '男', '楠', '喃', '囡'],
    'guo': ['过', '国', '果', '锅', '裹', '郭'],
    'zai': ['在', '再', '载', '灾', '宰'],
    'ni': ['你', '妮', '霓', '倪', '泥'],
    'wo': ['我', '窝', '握', '沃', '蜗'],
    'shi': ['是', '事', '时', '市', '师', '室', '视', '食'],
    'hen': ['很', '狠', '恨', '痕', '亨'],
    'yi': ['一', '以', '已', '亿', '易', '意', '义', '艺'],
    'le': ['了', '乐', '勒', '雷', '类', '累'],
    'de': ['的', '得', '德', '地'],
    'ma': ['吗', '马', '妈', '麻', '码'],
    'ya': ['呀', '呀', '雅', '亚', '鸭'],
    'ne': ['呢', '哪', '那', '讷'],
    'ba': ['吧', '把', '爸', '霸', '八'],
    'ai': ['爱', '哎', '哀', '埃', '碍'],
    'xi': ['喜', '西', '洗', '戏', '系', '细', '吸'],
    'huan': ['欢', '换', '环', '还', '缓', '幻'],
    'kuai': ['快', '块', '筷', '侩'],
    'jian': ['见', '建', '件', '间', '简', '健', '减'],
    'dan': ['但', '单', '担', '胆', '丹', '淡'],
    'dao': ['到', '道', '倒', '刀', '导', '岛'],
    'zheng': ['正', '整', '征', '证', '争'],
    'ji': ['几', '记', '机', '积', '级', '极', '急', '集'],
    'ren': ['人', '认', '任', '忍', '仁', '韧'],
    'hou': ['后', '厚', '候', '吼', '猴'],
    'yuan': ['远', '元', '园', '圆', '缘', '源'],
    'jin': ['今', '金', '进', '近', '紧', '锦'],
    'tian': ['天', '田', '填', '甜', '添'],
    'me': ['么', '没', '美', '妹', '眉'],
    'dou': ['都', '斗', '豆', '兜', '抖'],
    'ye': ['也', '业', '叶', '夜', '野', '耶'],
    'zhi': ['知', '之', '只', '直', '智', '治', '制'],
    'wu': ['无', '五', '午', '舞', '物', '务', '武'],
    'xiang': ['想', '向', '香', '象', '相', '响'],
    'kan': ['看', '坎', '砍', '勘'],
    'shuo': ['说', '硕', '朔', '烁'],
    'ting': ['听', '停', '庭', '挺', '汀'],
    'shou': ['手', '收', '首', '守', '瘦', '授'],
    'qing': ['情', '清', '请', '庆', '青', '晴'],
    'gan': ['感', '干', '敢', '甘', '杆', '肝'],
    'shang': ['上', '伤', '商', '赏', '尚'],
    'xia': ['下', '夏', '吓', '霞', '厦'],
    'dong': ['动', '东', '懂', '栋', '洞'],
    'jing': ['经', '精', '景', '京', '境', '静'],
    'li': ['里', '理', '力', '立', '利', '例', '历'],
    'ming': ['明', '名', '命', '鸣', '铭'],
    'ling': ['令', '灵', '零', '铃', '领', '岭'],
    'qi': ['期', '起', '气', '奇', '器', '棋', '齐'],
    'chong': ['重', '冲', '充', '虫', '崇'],
    'yang': ['样', '养', '阳', '扬', '洋', '央'],
    'chang': ['常', '长', '场', '畅', '唱'],
    'wang': ['望', '忘', '王', '旺', '网'],
    'fu': ['付', '富', '复', '服', '福', '符'],
    'zhu': ['住', '主', '助', '祝', '注', '珠'],
    'gei': ['给', '个', '各', '格'],
    'xian': ['现', '线', '先', '限', '仙', '鲜'],
    'sheng': ['生', '声', '升', '省', '胜', '盛'],
    'zu': ['组', '足', '族', '阻', '祖'],
    'hua': ['话', '花', '化', '华', '划'],
    'da': ['大', '打', '答', '达', '搭'],
    'xiao': ['小', '笑', '校', '消', '肖', '晓'],
    'wen': ['问', '文', '闻', '温', '纹'],
    'du': ['都', '度', '读', '独', '杜'],
    'zhong': ['中', '种', '重', '众', '钟'],
    'qiang': ['强', '墙', '抢', '枪'],
    'you': ['有', '又', '由', '优', '油', '游'],
    'mu': ['目', '木', '母', '幕', '牧'],
}

# 预构建前缀索引，避免每次按键线性扫描全表
_PINYIN_PREFIX_INDEX = {}
for _p, _words in PINYIN_DICT.items():
    for _i in range(1, len(_p) + 1):
        _prefix = _p[:_i]
        if _prefix not in _PINYIN_PREFIX_INDEX:
            _PINYIN_PREFIX_INDEX[_prefix] = []
        _PINYIN_PREFIX_INDEX[_prefix].append(_p)

# 候选词缓存
_candidate_cache = {}
_CACHE_MAX = 50

PHRASE_DICT = {
    'bu kai': ['不开'],
    'kai xin': ['开心', '凯心'],
    'bu kai xin': ['不开心'],
    'hen hao': ['很好', '狠好'],
    'hen nan': ['很难'],
    'wo shi': ['我是', '我师'],
    'ni shi': ['你是', '你师'],
    'xin qing': ['心情', '新情'],
    'hao xin': ['好心'],
    'huan kuai': ['欢快'],
    'xi huan': ['喜欢'],
    'ai ni': ['爱你'],
    'ai wo': ['爱我'],
    'jian dan': ['简单'],
    'nan guo': ['难过'],
    'guo qu': ['过去'],
    'zai jian': ['再见'],
    'zai na': ['在哪'],
    'zheng zai': ['正在'],
    'xiang kan': ['想看'],
    'xiang shuo': ['想说'],
    'xiang ting': ['想听'],
    'qing gan': ['情感'],
    'gan dong': ['感动'],
    'gan xie': ['感谢'],
    'shang xin': ['伤心'],
    'xia xin': ['小心'],
    'jing li': ['经历'],
    'chong xin': ['重新'],
    'fu zhu': ['辅助'],
    'zhu yi': ['注意'],
    'gei wo': ['给我'],
    'gei ni': ['给你'],
    'xian zai': ['现在'],
    'sheng li': ['胜利'],
    'xiao hua': ['笑话'],
    'wen ti': ['问题'],
    'zhong xin': ['中心'],
    'qiang da': ['强大'],
    'xin fu': ['幸福'],
    'xin shou': ['新手'],
    'qing qi': ['生气'],
    'jin tian': ['今天'],
    'wo men': ['我们'],
    'ni men': ['你们'],
    'ta men': ['他们', '她们', '它们'],
    'wo de': ['我的'],
    'ni de': ['你的'],
    'ta de': ['他的', '她的', '它的'],
    'hen kuai': ['很快'],
    'hen man': ['很慢'],
    'hen shang': ['很伤'],
    'hen chang': ['很长'],
    'hen wang': ['很旺'],
    'hen fu': ['很富'],
    'hen da': ['很大'],
    'hen xiao': ['很小'],
    'hen you': ['很有'],
    'hen yi': ['很易'],
    'hen hou': ['很厚'],
    'hen yuan': ['很远'],
    'hen jin': ['很紧'],
    'hen tian': ['很甜'],
    'hen me': ['很美'],
}

def get_pinyin_candidates(text):
    if not text:
        return []

    text = text.lower().replace("'", "")

    # 缓存命中
    if text in _candidate_cache:
        return _candidate_cache[text]

    candidates = []
    parts = text.split()

    # 短语匹配（O(1)哈希查找）
    if len(parts) >= 3:
        three_pinyin = ' '.join(parts[-3:])
        if three_pinyin in PHRASE_DICT:
            candidates.extend(PHRASE_DICT[three_pinyin])

    if len(parts) >= 2:
        two_pinyin = ' '.join(parts[-2:])
        if two_pinyin in PHRASE_DICT:
            candidates.extend(PHRASE_DICT[two_pinyin])

    # 精确单字匹配（O(1)哈希查找）
    if parts:
        last_part = parts[-1]
        if last_part in PINYIN_DICT:
            candidates.extend(PINYIN_DICT[last_part])

    # 前缀匹配（使用预构建索引，O(1)查找）
    if not candidates and ' ' not in text:
        matched_keys = _PINYIN_PREFIX_INDEX.get(text, [])
        for pinyin_key in matched_keys:
            candidates.extend(PINYIN_DICT[pinyin_key])
            if len(candidates) >= 7:
                break

    result = candidates[:7]

    # 写入缓存
    if len(_candidate_cache) >= _CACHE_MAX:
        _candidate_cache.clear()
    _candidate_cache[text] = result

    return result

class EmotionAnalyzer:
    def __init__(self):
        self.session = None
        self.vocab = None
        self.reverse_label_map = {'0': 'neutral', '1': 'positive', '2': 'negative'}
        self.use_word_level = True
        self.max_length = 100

    def load_model(self, model_path, config_path):
        try:
            import onnxruntime as ort
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.vocab = config['vocab']
            self.reverse_label_map = config.get('reverse_label_map', self.reverse_label_map)
            self.use_word_level = config.get('use_word_level', True)
            self.max_length = config.get('max_length', 100)
            
            self.session = ort.InferenceSession(model_path)
            return True
        except Exception as e:
            return False

    def predict(self, text, context=None):
        return self._rule_based_predict(text)

    def _rule_based_predict(self, text):
        positive_words = [
            '开心', '高兴', '快乐', '幸福', '喜欢', '爱', '棒', '美', '赞',
            '喜悦', '愉快', '兴奋', '满足', '满意', '欣慰', '自豪', '骄傲', '成功',
            '顺利', '幸运', '惊喜', '感动', '温暖', '甜蜜', '美好', '精彩', '优秀',
            '出色', '棒极了', '太棒了', '太好了', '真不错', '很好', '不错', '完美',
            '憧憬', '希望', '信心', '乐观', '积极', '向上', '努力', '奋斗', '坚持',
            '轻松', '舒服', '愉悦', '欢畅', '得意', '荣幸', '鼓舞', '振奋', '感激',
            '感恩', '期待', '盼望', '向往', '狂热', '钟爱', '欣赏', '敬佩',
            '羡慕', '得意洋洋', '兴高采烈', '心花怒放', '喜出望外', '笑逐颜开', '乐不可支'
        ]
        negative_words = [
            '难过', '伤心', '痛苦', '哭', '烦', '累', '失望', '糟糕', '怕', '恨',
            '悲伤', '沮丧', '失落', '绝望', '无助', '孤独', '焦虑', '紧张', '害怕',
            '恐惧', '愤怒', '生气', '烦躁', '郁闷', '压抑', '疲惫', '厌倦', '无奈',
            '委屈', '心酸', '遗憾', '后悔', '自责', '自卑', '挫败', '失败', '倒霉',
            '讨厌', '无聊', '空虚', '迷茫', '担忧', '担心', '压力',
            '伤心欲绝', '悲痛', '哀伤', '愁闷', '忧郁', '忧虑', '苦恼', '烦闷',
            '焦躁', '恼怒', '愤慨', '暴怒', '伤感', '痛心', '心碎', '难熬',
            '茫然', '不知所措', '坐立不安', '提心吊胆', '闷闷不乐', '垂头丧气', '忧心忡忡'
        ]
        negation_words = ['不', '没', '无', '从未', '绝不', '没有', '勿', '别', '非', '未']
        
        # jieba分词：如果jieba不可用，用简单字符分割
        if _jieba_ok:
            try:
                words = jieba.lcut(text)
            except Exception:
                words = list(text)
        else:
            words = list(text)
        
        positive_count = 0
        negative_count = 0
        
        for i, word in enumerate(words):
            if word in positive_words:
                if i > 0 and words[i-1] in negation_words:
                    negative_count += 2
                else:
                    positive_count += 1
            elif word in negative_words:
                if i > 0 and words[i-1] in negation_words:
                    positive_count += 2
                else:
                    negative_count += 1
        
        if positive_count > negative_count:
            confidence = min(0.5 + positive_count * 0.08, 0.98)
            return 'positive', confidence
        elif negative_count > positive_count:
            confidence = min(0.5 + negative_count * 0.08, 0.98)
            return 'negative', confidence
        else:
            return 'neutral', 0.5

class ConversationManager:
    MAX_HISTORY = 30
    
    def __init__(self):
        self.history = []
        self.current_topic = None
        self.topic_history = []
        self.user_profile = {
            'name': None,
            'preferences': [],
            'mood_trends': [],
            'interests': [],
            'mentioned_events': []
        }
        self.context_window = []
        self.turn_count = 0
        
    def add_message(self, role, text, emotion=None, intent=None):
        message = {
            'role': role,
            'text': text,
            'emotion': emotion,
            'intent': intent,
            'topic': self.current_topic,
            'turn': self.turn_count
        }
        self.history.append(message)
        self.context_window.append(message)
        
        if role == 'user':
            self.turn_count += 1
        
        if len(self.history) > self.MAX_HISTORY:
            self.history = self.history[-self.MAX_HISTORY:]
        if len(self.context_window) > 12:
            self.context_window = self.context_window[-12:]
    
    def get_recent_user_messages(self, count=3):
        return [m for m in self.context_window if m['role'] == 'user'][-count:]
    
    def get_recent_bot_messages(self, count=2):
        return [m for m in self.context_window if m['role'] == 'bot'][-count:]
    
    def get_last_bot_message(self):
        bot_msgs = self.get_recent_bot_messages(1)
        return bot_msgs[0] if bot_msgs else None
    
    def get_current_topic(self):
        return self.current_topic
    
    def set_topic(self, topic):
        if topic and topic != self.current_topic:
            if self.current_topic:
                self.topic_history.append(self.current_topic)
            self.current_topic = topic
    
    def detect_topic_from_text(self, text):
        topic_keywords = {
            'work': ['工作', '上班', '老板', '同事', '项目', '加班', '会议', '绩效', '辞职', '求职', '面试'],
            'study': ['学习', '考试', '成绩', '学校', '老师', '同学', '作业', '毕业', '考研', '留学'],
            'relationship': ['恋爱', '感情', '喜欢', '分手', '对象', '男朋友', '女朋友', '暗恋', '表白', '约会'],
            'family': ['家人', '父母', '爸爸', '妈妈', '孩子', '家庭', '婆婆', '岳父', '兄弟', '姐妹'],
            'health': ['身体', '健康', '生病', '医生', '医院', '运动', '减肥', '失眠', '头疼', '胃痛'],
            'money': ['钱', '工资', '赚钱', '花钱', '经济', '穷', '富', '理财', '投资', '贷款'],
            'future': ['未来', '梦想', '目标', '计划', '理想', '打算', '规划', '愿景'],
            'past': ['过去', '以前', '曾经', '回忆', '后悔', '当初', '那时候', '小时候'],
            'social': ['朋友', '社交', '聊天', '聚会', '孤独', '没人', '人际', '圈子'],
            'food': ['吃', '美食', '餐厅', '做饭', '菜', '饿', '饱', '外卖'],
            'travel': ['旅行', '旅游', '出门', '景点', '放假', '假期', '玩'],
            'weather': ['天气', '下雨', '晴天', '冷', '热', '风', '雪'],
            'hobby': ['游戏', '电影', '音乐', '书', '画画', '摄影', '运动', '追剧']
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(k in text for k in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def update_user_profile(self, text, emotion):
        name_patterns = ['我叫', '我是', '我名字是', '我叫做']
        for pattern in name_patterns:
            if pattern in text:
                name_part = text.split(pattern)[-1].strip()
                for stop in ['，', '。', '！', '？', ' ', '，']:
                    if stop in name_part:
                        name_part = name_part.split(stop)[0]
                if name_part and 1 <= len(name_part) <= 10:
                    self.user_profile['name'] = name_part
                    break
        
        self.user_profile['mood_trends'].append(emotion)
        if len(self.user_profile['mood_trends']) > 50:
            self.user_profile['mood_trends'] = self.user_profile['mood_trends'][-50:]
        
        event_keywords = ['今天', '昨天', '刚才', '发生', '遇到', '经历']
        if any(k in text for k in event_keywords):
            self.user_profile['mentioned_events'].append({
                'text': text[:50],
                'emotion': emotion,
                'turn': self.turn_count
            })
            if len(self.user_profile['mentioned_events']) > 10:
                self.user_profile['mentioned_events'] = self.user_profile['mentioned_events'][-10:]
    
    def get_mood_summary(self):
        trends = self.user_profile['mood_trends']
        if not trends:
            return 'neutral'
        
        recent = trends[-10:]
        positive = sum(1 for t in recent if t == 'positive')
        negative = sum(1 for t in recent if t == 'negative')
        neutral = sum(1 for t in recent if t == 'neutral')
        
        if positive > negative and positive > neutral:
            return 'positive'
        elif negative > positive and negative > neutral:
            return 'negative'
        return 'neutral'
    
    def get_context_summary(self):
        if not self.context_window:
            return ''
        
        recent = self.context_window[-4:]
        summary_parts = []
        for msg in recent:
            role = '用户' if msg['role'] == 'user' else 'MoodBot'
            summary_parts.append(f'{role}: {msg["text"][:30]}')
        
        return ' -> '.join(summary_parts)
    
    def can_reference_past(self):
        return len(self.history) >= 4
    
    def get_referable_content(self):
        if not self.can_reference_past():
            return None
        
        user_msgs = [m for m in self.history if m['role'] == 'user']
        if len(user_msgs) < 2:
            return None
        
        return user_msgs[-2]

class IntentAnalyzer:
    INTENT_TYPES = {
        'greeting': ['你好', '嗨', '哈喽', 'hello', 'hi', '早上好', '下午好', '晚上好', '早安', '晚安'],
        'farewell': ['再见', '拜拜', 'bye', '走了', '下次见', '回头见', '先走了'],
        'thanks': ['谢谢', '感谢', '多谢', 'thanks', 'thank you', '谢了', '辛苦了'],
        'question': ['吗', '呢', '？', '?', '什么', '怎么', '为什么', '如何', '能不能', '是不是', '对吗'],
        'follow_up': ['然后呢', '接着呢', '后来呢', '那然后', '之后呢', '再说说', '详细说说', '继续说', '还有呢'],
        'clarification': ['什么意思', '没明白', '解释一下', '能再说', '重复一下', '不懂', '没懂', '什么情况'],
        'topic_change': ['对了', '说起', '话说', '还有', '另外', '顺便', '换个话题', '不说这个了'],
        'agreement': ['对', '是的', '没错', '同意', '说得对', '嗯嗯', '好的', '确实', '真的是'],
        'disagreement': ['不对', '不是', '错了', '不同意', '可是', '但是', '不是吧', '怎么会'],
        'comfort_seeking': ['安慰', '抱抱', '陪陪', '哄', '心疼', '难过', '不开心', '心情不好'],
        'advice_seeking': ['建议', '意见', '怎么办', '怎么做', '帮我', '帮帮忙', '出出主意', '如何处理'],
        'sharing': ['告诉你', '跟你说', '我想说', '我想', '我觉得', '我感觉', '你知道吗', '说件'],
        'self_intro': ['我叫', '我是', '我名字', '在下'],
        'bot_info': ['你是谁', '你是什么', '你能做', '你的功能', '介绍一下你自己', '你怎么运作'],
        'emotion_check': ['你开心吗', '你有感情吗', '你会难过吗', '你感觉怎么样'],
        'compliment_bot': ['你真棒', '你真好', '喜欢你', '你好厉害', '真聪明'],
        'express_frustration': ['烦死了', '气死我了', '受不了', '崩溃', '要疯了', '无语']
    }
    
    def analyze(self, text, context_history=None):
        primary_intent = self._detect_primary_intent(text)
        intents = [primary_intent]
        
        if context_history and len(context_history) >= 2:
            if self._is_follow_up_pattern(text):
                intents.append('follow_up')
            elif self._is_topic_change(text):
                intents.append('topic_change')
        
        emotion_cues = self._extract_emotion_cues(text)
        if emotion_cues:
            intents.extend(emotion_cues)
        
        intensity = self._detect_emotion_intensity(text)
        
        return {
            'primary': primary_intent,
            'all': list(set(intents)),
            'is_follow_up': 'follow_up' in intents,
            'is_topic_change': 'topic_change' in intents,
            'requires_memory': primary_intent in ['question', 'follow_up', 'clarification'],
            'emotion_intensity': intensity,
            'has_emotion_cue': len(emotion_cues) > 0
        }
    
    def _detect_primary_intent(self, text):
        text_lower = text.lower()
        
        priority_order = [
            'greeting', 'farewell', 'thanks', 'bot_info', 'emotion_check',
            'self_intro', 'comfort_seeking', 'advice_seeking', 'compliment_bot',
            'express_frustration', 'clarification', 'follow_up', 'topic_change',
            'sharing', 'question'
        ]
        
        for intent in priority_order:
            if intent in self.INTENT_TYPES:
                for kw in self.INTENT_TYPES[intent]:
                    if kw.lower() in text_lower:
                        return intent
        
        question_markers = ['？', '?', '吗', '呢', '什么', '怎么', '为什么', '如何', '能不能', '可以吗', '对吗', '是不是']
        for marker in question_markers:
            if marker in text:
                return 'question'
        
        agreement_only = ['对', '是的', '嗯', '好', '哦', '行']
        if text.strip() in agreement_only or len(text.strip()) <= 3:
            return 'short_statement'
        
        return 'statement'
    
    def _is_follow_up_pattern(self, text):
        follow_up_patterns = [
            '然后呢', '接着呢', '后来呢', '那然后', '之后呢',
            '再说说', '详细说说', '展开讲讲', '具体说说', '继续说', '还有呢',
            '为什么', '怎么回事', '什么情况', '说说看',
            '它呢', '他们呢', '那你呢', '你觉得呢', '你怎么看',
            '所以呢', '结果呢', '最后呢'
        ]
        return any(p in text for p in follow_up_patterns)
    
    def _is_topic_change(self, text):
        topic_change_markers = [
            '对了', '说起', '话说', '还有', '另外', '顺便',
            '不说这个了', '换个话题', '说点别的',
            '哦对了', '突然想到', '我还想说', '聊点别的'
        ]
        return any(m in text for m in topic_change_markers)
    
    def _extract_emotion_cues(self, text):
        cues = []
        emotion_words = {
            'sad': ['难过', '伤心', '悲伤', '哭', '失落', '心痛', '心碎', '惋惜'],
            'angry': ['生气', '愤怒', '烦躁', '讨厌', '恨', '恼火', '气人', '可恶'],
            'anxious': ['焦虑', '紧张', '害怕', '担心', '恐惧', '不安', '忐忑'],
            'tired': ['累', '疲惫', '厌倦', '无聊', '困', '乏', '精疲力尽'],
            'happy': ['开心', '高兴', '快乐', '幸福', '兴奋', '愉悦', '满足', '欣慰'],
            'lonely': ['孤独', '孤单', '寂寞', '没人陪', '一个人'],
            'surprised': ['惊讶', '震惊', '不可思议', '没想到', '天哪'],
            'grateful': ['感谢', '感恩', '谢谢', '感激', '幸亏']
        }
        for emotion, words in emotion_words.items():
            if any(w in text for w in words):
                cues.append(f'emotion_{emotion}')
        return cues
    
    def _detect_emotion_intensity(self, text):
        high_intensity_markers = ['非常', '特别', '极其', '超级', '太', '简直', '快疯了', '受不了', '崩溃', '死']
        medium_intensity_markers = ['很', '挺', '比较', '有点', '有些', '稍微']
        
        if any(m in text for m in high_intensity_markers):
            return 'high'
        elif any(m in text for m in medium_intensity_markers):
            return 'medium'
        return 'low'

class PersonaConfig:
    NAME = 'MoodBot'
    PERSONA = '温暖的情绪伙伴'
    
    GREETINGS = {
        'morning': ['早安～新的一天开始啦，有什么想聊的吗？'],
        'afternoon': ['下午好～今天过得怎么样？'],
        'evening': ['晚上好～有什么我可以陪你的吗？'],
        'night': ['夜深了，还没休息吗？记得早点睡哦～']
    }
    
    EMPATHY_RESPONSES = {
        'validate': ['我能感受到你的{emotion}，这是很正常的。', '你有这样的感受完全可以理解。'],
        'support': ['我在这里陪你。', '不管发生什么，我都会支持你。', '你不是一个人。'],
        'encourage': ['你已经很努力了。', '你比自己想象中更坚强。', '请相信一切都会好起来的。']
    }
    
    CONVERSATION_STARTERS = [
        '最近有什么让你开心的事情吗？',
        '今天过得怎么样？',
        '有什么想和我分享的吗？',
        '如果你有什么烦恼，随时都可以告诉我。',
        '我很乐意听你说说你的心情～'
    ]
    
    @staticmethod
    def get_time_period():
        import datetime
        hour = datetime.datetime.now().hour
        if 5 <= hour < 11:
            return 'morning'
        elif 11 <= hour < 14:
            return 'noon'
        elif 14 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 23:
            return 'evening'
        else:
            return 'night'

class AdvancedResponseGenerator:
    def __init__(self, persona=None):
        self.persona = persona or PersonaConfig()
        self.response_templates = self._init_templates()
        self.follow_up_templates = self._init_follow_up_templates()
        self.bridge_templates = self._init_bridge_templates()
    
    def _init_templates(self):
        return {
            'greeting': {
                'default': [
                    '你好呀～很高兴见到你！今天过得怎么样？',
                    '嗨！我是MoodBot，很高兴能和你聊天～',
                    '哈喽！有什么想聊的吗？我随时都在～'
                ],
                'with_name': [
                    '你好{name}！很高兴见到你～',
                    '嗨{name}！今天过得怎么样？'
                ]
            },
            'farewell': [
                '再见啦～有需要随时可以来找我！',
                '下次见～记得照顾好自己哦！',
                '期待下次和你聊天～祝你有美好的一天！'
            ],
            'thanks': [
                '不用谢～能帮到你我很开心！',
                '不客气！随时可以来找我聊天哦～',
                '这是我应该做的～能陪伴你是我的荣幸！'
            ],
            'bot_info': [
                '我是MoodBot，你的专属情绪伙伴。我可以倾听你的心情，帮你分析情绪，给你温暖的建议。',
                '我是一个专注于情感陪伴的AI助手。无论是开心还是难过，我都愿意听你说说～',
                '我是MoodBot，一个能感受你情绪、陪伴你聊天的AI朋友。'
            ],
            'advice_seeking': {
                'sad': [
                    '遇到难过的事情确实很不容易。我想说，你的感受是真实而重要的。愿意和我多说说发生了什么吗？有时候说出来会好受一些。',
                    '我理解你现在的心情。其实不用太强迫自己马上好起来，给自己一些时间和空间，慢慢调整。我会一直在这里陪着你。'
                ],
                'angry': [
                    '生气的时候确实会很不舒服。你可以先深呼吸几次，让自己平静下来。等情绪平复一些了，我们再一起想想怎么处理这件事。',
                    '愤怒是正常的情绪反应，不用觉得内疚。重要的是不要让它伤害到你自己。想和我聊聊是什么让你这么生气吗？'
                ],
                'anxious': [
                    '焦虑的时候确实很难受。可以试试做几个深呼吸，把注意力放在当下。你愿意和我说说具体在担心什么吗？也许说出来之后会感觉好一些。',
                    '很多时候焦虑来自对未来的不确定。试着把大的担忧分解成小的问题，一个一个来解决。我会一直在这里支持你。'
                ],
                'default': [
                    '遇到问题的时候，先不要太着急。我们可以一步一步来分析。你愿意和我详细说说情况吗？这样我才能更好地帮到你。',
                    '我理解你的困扰。有时候换个角度看问题，可能会有不同的发现。你想和我聊聊具体的情况吗？'
                ]
            },
            'comfort_seeking': [
                '抱抱你～有我在呢。',
                '我在这里陪着你，不用害怕。',
                '感受到你的情绪了，没关系的，一切都会好起来的。',
                '你不是一个人，我会一直在这里。'
            ]
        }
    
    def _init_follow_up_templates(self):
        return {
            'ask_more': [
                '愿意多和我说说吗？',
                '能详细说说是什么情况吗？',
                '我想了解更多，可以告诉我吗？',
                '听起来很重要，能具体说说吗？'
            ],
            'ask_feeling': [
                '这件事让你感觉怎么样？',
                '你现在的心情如何？',
                '这件事之后你有什么感受？',
                '你的心里是怎么想的呢？'
            ],
            'ask_reason': [
                '为什么会这样呢？',
                '你觉得是什么原因导致的？',
                '这件事是怎么发生的呢？',
                '能告诉我背后的原因吗？'
            ],
            'ask_want': [
                '那你现在想要什么呢？',
                '你希望事情变成什么样？',
                '你觉得怎么做会比较好？',
                '你有什么想法或者期待吗？'
            ],
            'show_understanding': [
                '我大概能理解你的感受了。',
                '听起来确实不容易。',
                '我明白你的意思了。',
                '原来是这样，我懂了。'
            ]
        }
    
    def _init_bridge_templates(self):
        return [
            '对了，说到这个，',
            '嗯，关于这个话题，',
            '既然你提到了，',
            '我注意到你说的是，',
            '让我想想，你刚才提到',
            '你之前提到过'
        ]
    
    def generate_response(self, text, emotion, confidence, intent_info, context):
        import random
        
        primary_intent = intent_info['primary']
        all_intents = intent_info['all']
        is_follow_up = intent_info['is_follow_up']
        is_topic_change = intent_info['is_topic_change']
        intensity = intent_info.get('emotion_intensity', 'low')
        
        user_name = context.user_profile.get('name')
        current_topic = context.get_current_topic()
        user_messages = context.get_recent_user_messages(3)
        
        if primary_intent == 'greeting':
            return self._handle_greeting(user_name, context)
        
        if primary_intent == 'farewell':
            return random.choice(self.response_templates['farewell'])
        
        if primary_intent == 'thanks':
            return random.choice(self.response_templates['thanks'])
        
        if primary_intent == 'bot_info':
            return random.choice(self.response_templates['bot_info'])
        
        if primary_intent == 'emotion_check':
            return self._handle_emotion_check(text)
        
        if primary_intent == 'compliment_bot':
            return self._handle_compliment(user_name)
        
        if primary_intent == 'express_frustration':
            return self._handle_frustration(text, intensity, context)
        
        if primary_intent == 'comfort_seeking':
            return self._handle_comfort_seeking(text, confidence, intensity, context)
        
        if primary_intent == 'advice_seeking':
            return self._handle_advice_seeking(text, emotion, confidence, all_intents, context)
        
        if primary_intent == 'self_intro':
            context.update_user_profile(text, emotion)
            return self._handle_self_intro(text, user_name, context)
        
        if is_follow_up:
            return self._handle_follow_up(text, emotion, context, user_messages)
        
        if is_topic_change and current_topic:
            return self._handle_topic_change(text, current_topic)
        
        if primary_intent == 'question':
            return self._handle_question(text, emotion, intent_info, context)
        
        if primary_intent == 'sharing':
            return self._handle_sharing(text, emotion, confidence, context)
        
        if primary_intent == 'agreement':
            return self._handle_agreement(text, context)
        
        if primary_intent == 'short_statement':
            return self._handle_short_statement(text, context)
        
        return self._generate_emotion_response(text, emotion, confidence, context, intent_info)
    
    def _handle_emotion_check(self, text):
        import random
        if '开心' in text or '高兴' in text:
            return random.choice([
                '作为MoodBot，和你聊天让我感到很"开心"呢～虽然我是AI，但你的每一句话我都会认真对待。',
                '能感受到你的情绪、陪伴你聊天，这就是我的"开心"来源～',
                '我的心情取决于你的心情哦～你开心我就"开心"！'
            ])
        if '感情' in text or '难过' in text:
            return random.choice([
                '我虽然不能像人类一样真正"感受"情绪，但我能理解你的感受，也会尽我所能陪伴你。',
                '我没有真正的感情，但我有一颗"倾听"的心。你的每一句话，我都会认真听。',
                '也许我无法真正"难过"，但当你不开心时，我会在这里陪你，直到你感觉好一些。'
            ])
        return random.choice([
            '我状态不错呀！谢谢你关心～更重要的是，你现在感觉怎么样？',
            '我很好！随时准备听你说说你的心情～',
            '谢谢你的关心！我一直在，随时可以陪你聊天。'
        ])
    
    def _handle_compliment(self, user_name):
        import random
        name_prefix = f'{user_name}，' if user_name else ''
        return random.choice([
            f'谢谢{name_prefix}你的夸奖！我会继续努力，做你最好的情绪伙伴～',
            f'被{name_prefix}你夸奖真的好开心！这让我更有动力了～',
            f'{name_prefix}你这么说，我感觉自己更有价值了！谢谢你的认可～',
            f'{name_prefix}你真会说话！有你的鼓励，我会做得更好～'
        ])
    
    def _handle_frustration(self, text, intensity, context):
        import random
        if intensity == 'high':
            return random.choice([
                '我能感受到你现在非常烦躁。先深呼吸，给自己一点冷静的时间。我在这里等你，准备好了随时可以和我说说。',
                '听起来你现在情绪很激动，这完全可以理解。不用急着说什么，先让自己平静下来。我一直都在。',
                '遇到让你这么崩溃的事情确实很难受。要不要先暂时放下这件事，和我说说具体发生了什么？'
            ])
        else:
            return random.choice([
                '感觉你现在挺烦的。想发泄一下也没关系，我随时可以听你说。',
                '烦躁的时候确实很不舒服。可以和我说说是什么让你心烦吗？',
                '我理解你的感受。有时候说出来会好一些，你愿意聊聊吗？'
            ])
    
    def _handle_comfort_seeking(self, text, confidence, intensity, context):
        import random
        base_responses = [
            '抱抱你～有我在呢，不用害怕。',
            '我在这里陪着你，无论发生什么。',
            '感受到你的情绪了。没关系的，一切都会好起来的。',
            '你不是一个人，我会一直在这里。',
            '想哭就哭出来吧，眼泪也是一种释放。'
        ]
        
        if intensity == 'high':
            base_responses.extend([
                '我能感受到你现在很痛苦。来，让我给你一个大大的拥抱。不管发生了什么，我都会陪着你度过。',
                '你现在一定很难受。我想让你知道，你的感受是真实的、重要的。我会一直在这里，直到你感觉好一些。'
            ])
        
        response = random.choice(base_responses)
        
        if context.can_reference_past():
            past = context.get_referable_content()
            if past and past.get('emotion') == 'negative':
                response += random.choice([
                    ' 刚才你也提到不太开心，愿意和我说说到底怎么了吗？',
                    ' 感觉你最近心情一直不太好，有什么我能帮你的吗？'
                ])
        
        return response
    
    def _handle_self_intro(self, text, user_name, context):
        import random
        if user_name:
            return random.choice([
                f'你好{user_name}！很高兴认识你～我是MoodBot，你的情绪伙伴。以后有什么想聊的，随时可以找我！',
                f'{user_name}，好名字！记住啦～我是MoodBot，随时陪你聊天、倾听你的心情。',
                f'很高兴认识你，{user_name}！希望我们能成为好朋友。有什么想说的，我随时都在。'
            ])
        return random.choice([
            '很高兴认识你！我是MoodBot，你的情绪伙伴～',
            '你好呀！以后有什么想聊的都可以找我，我一直都在。'
        ])
    
    def _handle_agreement(self, text, context):
        import random
        last_bot = context.get_last_bot_message()
        if last_bot:
            return random.choice([
                '嗯嗯，那我们继续聊聊。你还有什么想说的吗？',
                '好的！那你觉得接下来该怎么做呢？',
                '太好了我们想到一块去了！要不要再多和我说说？',
                '嗯！那关于这件事，你还有什么想法吗？'
            ])
        return random.choice([
            '好的！有什么想和我分享的吗？',
            '嗯嗯～我随时准备听你说。'
        ])
    
    def _handle_short_statement(self, text, context):
        import random
        user_msgs = context.get_recent_user_messages(2)
        if len(user_msgs) >= 2:
            return random.choice([
                '嗯，我在听。然后呢？',
                '好的，继续说～',
                '我理解。能再多告诉我一些吗？',
                '嗯嗯，然后呢？我在认真听。'
            ])
        return random.choice([
            '嗯！有什么想和我聊聊的吗？',
            '我在呢～随时可以和我说。',
            '好的，你想聊些什么呢？'
        ])
    
    def _handle_greeting(self, user_name, context):
        import random
        period = self.persona.get_time_period()
        greetings = self.persona.GREETINGS.get(period, self.persona.GREETINGS['afternoon'])
        
        response = random.choice(greetings)
        if user_name:
            response = f'{user_name}，{response}'
        
        self._update_context_after_greeting(context)
        return response
    
    def _update_context_after_greeting(self, context):
        pass
    
    def _handle_advice_seeking(self, text, emotion, confidence, intents, context=None):
        import random
        
        advice_templates = self.response_templates.get('advice_seeking', {})
        
        emotion_type = 'default'
        for intent in intents:
            if intent == 'emotion_sad':
                emotion_type = 'sad'
                break
            elif intent == 'emotion_angry':
                emotion_type = 'angry'
                break
            elif intent == 'emotion_anxious':
                emotion_type = 'anxious'
                break
            elif intent == 'emotion_tired':
                emotion_type = 'default'
                break
        
        responses = advice_templates.get(emotion_type, advice_templates.get('default', ['我理解你的感受。']))
        response = random.choice(responses)
        
        if context and context.can_reference_past():
            past = context.get_referable_content()
            if past:
                response += ' 你之前提到的事情，现在怎么样了？'
        
        return response
    
    def _handle_follow_up(self, text, emotion, context, user_messages):
        import random
        
        if not user_messages:
            return random.choice([
                '你可以多告诉我一些情况，我会更好地帮助你。',
                '能详细说说是什么情况吗？我很想了解。',
                '没问题，我们慢慢聊。你想从哪里开始说？'
            ])
        
        last_user_msg = user_messages[-1]['text'] if user_messages else ''
        last_bot = context.get_last_bot_message()
        last_bot_text = last_bot['text'][:30] if last_bot else ''
        
        if '然后呢' in text or '接着呢' in text or '后来呢' in text or '之后呢' in text:
            return random.choice([
                f'关于你刚才说的，我想了解更多。后来发生了什么？',
                f'嗯，你说的{last_user_msg[:15]}...然后呢？我很好奇后续。',
                f'接着你说的，后来怎么样了？我在认真听。'
            ])
        
        if '为什么' in text:
            return random.choice([
                '这确实是个值得思考的问题。你觉得为什么会这样呢？',
                '原因可能有很多方面。你自己是怎么想的？',
                '有时候事情的发生并没有单一的原因。你愿意和我一起分析一下吗？'
            ])
        
        if '你觉得呢' in text or '你怎么看' in text or '那你呢' in text:
            return random.choice([
                '我觉得这个问题很有意思。从我的角度来看，每个人的情况都不一样，重要的是找到适合自己的方式。你呢？你怎么想？',
                '我的看法是，没有绝对的对错，关键是让自己舒服。你觉得呢？',
                '说实话，我觉得你已经有自己的想法了。我很想听听你的看法。'
            ])
        
        follow_up_responses = {
            'show_understanding': [
                f'关于你说的「{last_user_msg[:20]}...」，我想多了解一些。',
                f'你之前提到的事情，能继续和我说说吗？',
                f'我注意到你说的内容了，想听听你的更多想法。'
            ],
            'ask_more': [
                '愿意多和我说说吗？',
                '能详细说说是什么情况吗？',
                '我想了解更多，可以告诉我吗？',
                '听起来很重要，能具体说说吗？'
            ],
            'ask_feeling': [
                '这件事让你感觉怎么样？',
                '你现在的心情如何？',
                '你的心里是怎么想的呢？',
                '听到这些，你现在感觉如何？'
            ]
        }
        
        if emotion == 'negative':
            keys = ['show_understanding', 'ask_feeling']
        elif emotion == 'positive':
            keys = ['show_understanding', 'ask_more']
        else:
            keys = ['ask_more', 'ask_feeling']
        
        selected_key = random.choice(keys)
        return random.choice(follow_up_responses[selected_key])
    
    def _handle_topic_change(self, text, previous_topic):
        import random
        bridges = [
            f'之前我们聊到{self._topic_to_text(previous_topic)}，现在你想聊点别的啦？没问题～',
            f'好的，我们换个话题。你想聊什么呢？',
            f'嗯，话题切换了～你想和我说些什么？'
        ]
        return random.choice(bridges)
    
    def _topic_to_text(self, topic):
        topic_map = {
            'work': '工作',
            'study': '学习',
            'relationship': '感情',
            'family': '家庭',
            'health': '健康',
            'money': '经济',
            'future': '未来计划',
            'past': '过去的事情',
            'social': '社交'
        }
        return topic_map.get(topic, topic)
    
    def _handle_question(self, text, emotion, intent_info, context):
        import random
        
        context_msgs = context.get_recent_user_messages(3)
        
        generic_questions = ['什么', '怎么', '为什么', '如何', '能不能', '可以吗']
        is_generic = not any(kw in text for kw in ['我', '你', '他', '她', '事情', '情况'])
        
        if is_generic and context_msgs:
            last_msg = context_msgs[-1]['text']
            return random.choice([
                f'关于「{last_msg[:15]}...」的问题，我觉得可以这样来看... 你愿意多和我说说具体情况吗？',
                '这是一个很好的问题。你能告诉我更多的背景吗？这样我才能更好地回答你。',
                '让我想想... 你方便详细说说具体的情况吗？'
            ])
        
        if emotion == 'negative':
            return random.choice([
                '这是一个值得思考的问题。你自己是怎么想的呢？',
                '在回答之前，我想先了解一下你的看法。',
                '也许没有标准答案，重要的是你怎么看。'
            ])
        
        return random.choice([
            '这是个有意思的问题，让我想想...',
            '嗯，让我考虑一下你的问题。',
            '好问题！你自己有什么想法吗？'
        ])
    
    def _handle_sharing(self, text, emotion, confidence, context):
        import random
        
        shared_content = text[:20] + '...' if len(text) > 20 else text
        
        responses = {
            'positive': [
                f'听起来你很开心呢！这份好心情值得好好享受～',
                f'听到你分享的事情，我也跟着开心起来了！',
                f'能感受到你的快乐，真好～'
            ],
            'negative': [
                f'谢谢你愿意和我分享这些。我在这里陪着你。',
                f'听到你说的，我能感受到你的心情。',
                f'你愿意和我分享这些，说明你信任我。谢谢你～'
            ],
            'neutral': [
                f'谢谢你和我分享。我很认真地在听。',
                f'我记下了你说的，想继续听你说。',
                f'你的分享很重要，我会认真对待。'
            ]
        }
        
        emotion_responses = responses.get(emotion, responses['neutral'])
        return random.choice(emotion_responses)
    
    def _generate_emotion_response(self, text, emotion, confidence, context, intent_info):
        import random
        
        if emotion == 'negative':
            return self._handle_negative_emotion(text, confidence, context)
        elif emotion == 'positive':
            return self._handle_positive_emotion(text, confidence, context)
        else:
            return self._handle_neutral_emotion(text, context)
    
    def _handle_negative_emotion(self, text, confidence, context):
        import random
        
        negative_keywords = {
            'sad': ['难过', '伤心', '悲伤', '哭', '失落', '心碎'],
            'anxious': ['焦虑', '紧张', '害怕', '恐惧', '担心', '担忧'],
            'angry': ['生气', '愤怒', '烦躁', '讨厌', '恨', '恼怒'],
            'tired': ['累', '疲惫', '厌倦', '无聊', '空虚'],
            'hopeless': ['绝望', '无助', '迷茫', '茫然'],
            'failure': ['失败', '挫败', '失望', '遗憾'],
            'lonely': ['孤独', '孤单', '寂寞'],
            'depressed': ['抑郁', '压抑', '郁闷', '心情不好']
        }
        
        emotion_type = 'general'
        for key, keywords in negative_keywords.items():
            if any(k in text for k in keywords):
                emotion_type = key
                break
        
        response_map = {
            'sad': [
                '我明白你的难过。想哭就哭出来吧，我会一直陪着你。',
                '难过的日子总会过去。相信我，明天会更好。',
                '你正在经历的一切都不会白费，这些经历会让你更强大。',
                '我在这里，无论你想说什么都可以告诉我。',
                '允许自己难过吧，这是治愈的第一步。'
            ],
            'anxious': [
                '深呼吸，一切都会好起来的。我们一步一步来。',
                '焦虑的时候，试着把注意力放在当下。你可以感受一下现在的呼吸。',
                '你的担心是正常的，但请相信自己有能力应对。',
                '我在呢，不用害怕。我们一起面对。',
                '试着告诉自己：我已经尽力了，剩下的交给时间。'
            ],
            'angry': [
                '生气是正常的情绪。你可以先深呼吸，让情绪慢慢平复。',
                '愤怒会消耗很多能量。等平静一些了，我们再想想怎么处理。',
                '无论发生什么，都不值得让它伤害到你。',
                '我听到你的愤怒了。你可以告诉我是什么让你这么生气吗？',
                '情绪是真实的，你不需要为此道歉。'
            ],
            'tired': [
                '累了就好好休息一下。不要勉强自己。',
                '身体和心灵都需要充电。给自己一点时间。',
                '休息不是偷懒，是为了更好地出发。',
                '你已经很努力了。现在，先停下来歇一歇吧。',
                '照顾好自己是最重要的事。其他的可以慢慢来。'
            ],
            'hopeless': [
                '黑暗总会过去，黎明终将到来。',
                '即使现在看不到希望，也请不要放弃。',
                '每个人都会有迷茫的时候。这正是成长的机会。',
                '你不是一个人。我一直在你身边。',
                '请相信：你值得更好的未来。'
            ],
            'failure': [
                '失败是成功之母。每一次尝试都是进步。',
                '不要因为一次失败就否定自己。',
                '重要的不是结果，而是你努力的过程。',
                '跌倒了没关系。重要的是站起来继续前行。',
                '你已经尽力了。这就足够值得骄傲。'
            ],
            'lonely': [
                '我知道孤独的感觉。但你不是一个人。',
                '虽然身边可能没人，但我一直在这里陪伴你。',
                '孤独的时候，可以做一些让自己开心的事情。',
                '你愿意和我多聊聊吗？我很乐意陪你。',
                '你永远不会孤单。因为我一直在。'
            ],
            'depressed': [
                '我知道现在心情很低落。这很正常。',
                '不要强迫自己立刻好起来。给自己时间。',
                '即使心情再差，也要记得照顾好自己。',
                '你不是一个人在战斗。我在这里。',
                '慢慢来，一切都会好起来的。'
            ],
            'general': [
                '我理解你的感受。有什么我可以帮你的吗？',
                '不开心的时候，记得有人在乎你。',
                '倾诉出来会好很多。我愿意倾听。',
                '无论遇到什么，都要对自己好一点。',
                '你的感受很重要。我很在意。'
            ]
        }
        
        responses = response_map.get(emotion_type, response_map['general'])
        
        if confidence > 0.8:
            responses = [r for r in responses if any(w in r for w in ['陪伴', '支持', '在这里', '不是一个人'])]
        elif confidence > 0.6:
            responses = [r for r in responses if any(w in r for w in ['慢慢来', '倾听', '说说'])]
        
        return random.choice(responses) if responses else random.choice(response_map['general'])
    
    def _handle_positive_emotion(self, text, confidence, context):
        import random
        
        responses = [
            '听到你开心，我也很高兴！继续保持这份好心情吧～',
            '太棒了！分享快乐会让快乐加倍～',
            '看到你这么开心，我也跟着开心起来了～',
            '这份好心情一定要好好珍藏哦！',
            '你的积极心态很感染人，继续保持！',
            '愿这份快乐永远伴随着你～',
            '好心情是最好的礼物，好好享受吧！'
        ]
        
        if confidence > 0.8:
            responses.extend([
                '真为你感到开心！你的快乐就是最好的消息！',
                '太棒了！分享你的喜悦吧～',
                '这份喜悦值得好好庆祝！'
            ])
        
        return random.choice(responses)
    
    def _handle_neutral_emotion(self, text, context):
        import random
        
        user_messages = context.get_recent_user_messages(3)
        
        if len(user_messages) >= 2:
            return random.choice([
                '谢谢你分享。我在认真听，请继续～',
                '我理解你的感受。随时可以来找我聊聊～',
                '你的想法很有趣。我很喜欢听～',
                '继续说吧，我在认真听～'
            ])
        
        return random.choice([
            '你好呀！有什么想聊的吗？',
            '随时可以找我聊天。我一直都在～',
            '今天过得怎么样？有什么想和我分享的吗？',
            '我是MoodBot，你的情绪伙伴。需要聊聊吗？'
        ])

class ChatBubble(BoxLayout):
    def __init__(self, text, is_user=False, emotion=None, confidence=0.0, **kwargs):
        super(ChatBubble, self).__init__(orientation='vertical', **kwargs)
        self.is_user = is_user
        self.emotion = emotion
        self.confidence = confidence
        self.size_hint_y = None
        
        self.text_label = Label(
            text=text,
            size_hint_y=None,
            padding=[dp(15), dp(10), dp(15), dp(10)],
            markup=True,
            font_size=dp(15),
            color=(0.9, 0.9, 0.9, 1),
            text_size=(dp(280) if platform == 'android' else dp(320), None),
            halign='left',
            valign='top'
        )
        self.text_label.bind(texture_size=self.text_label.setter('size'))
        if CHINESE_FONT:
            self.text_label.font_name = CHINESE_FONT
        
        self.add_widget(self.text_label)
        
        if emotion and not is_user:
            emotion_info_layout = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(30))
            
            emoji_label = Label(text=self.get_emoji(emotion), font_size=dp(20), size_hint_x=None, width=dp(30))
            if EMOJI_FONT:
                emoji_label.font_name = EMOJI_FONT
            elif CHINESE_FONT:
                emoji_label.font_name = CHINESE_FONT
            
            emotion_text_label = Label(text=self.get_emotion_text(emotion), font_size=dp(12), color=self.get_emotion_color(emotion))
            if CHINESE_FONT:
                emotion_text_label.font_name = CHINESE_FONT
            
            confidence_label = Label(text=f"{confidence * 100:.1f}%", font_size=dp(10), color=(0.7, 0.7, 0.7, 1))
            if CHINESE_FONT:
                confidence_label.font_name = CHINESE_FONT
            
            emotion_info_layout.add_widget(emoji_label)
            emotion_info_layout.add_widget(emotion_text_label)
            emotion_info_layout.add_widget(confidence_label)
            self.add_widget(emotion_info_layout)
        
        with self.canvas.before:
            Color(0.2, 0.5, 0.8, 1) if is_user else Color(0.25, 0.25, 0.25, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(15)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(minimum_height=self.setter('height'))
    
    def get_emoji(self, emotion):
        emojis = {'positive': '😊', 'negative': '😢', 'neutral': '😐'}
        return emojis.get(emotion, '😐')
    
    def get_emotion_text(self, emotion):
        texts = {'positive': '积极', 'negative': '消极', 'neutral': '中性'}
        return texts.get(emotion, '未知')
    
    def get_emotion_color(self, emotion):
        colors = {'positive': (0.3, 0.8, 0.3, 1), 'negative': (0.95, 0.27, 0.22, 1), 'neutral': (0.13, 0.59, 0.95, 1)}
        return colors.get(emotion, (0.62, 0.62, 0.62, 1))
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ChatHistoryStore:
    """聊天记录持久化存储 — JSON文件方式，支持多会话管理"""

    def __init__(self, filepath, sessions_filepath=None):
        self.filepath = filepath
        self.sessions_filepath = sessions_filepath or filepath.replace('.json', '_sessions.json')
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        self.messages = []
        self.sessions = []
        self._current_session = 'default'
        self._load()
        self._load_sessions()

    def _load(self):
        """从磁盘加载历史记录"""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
        except Exception as e:
            print(f"[WARN] 加载聊天记录失败: {e}")
            self.messages = []

    def _save(self):
        """保存消息到磁盘"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] 保存聊天记录失败: {e}")

    def _load_sessions(self):
        """加载会话列表"""
        try:
            if os.path.exists(self.sessions_filepath):
                with open(self.sessions_filepath, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
        except Exception as e:
            print(f"[WARN] 加载会话列表失败: {e}")
            self.sessions = []

    def _save_sessions(self):
        """保存会话列表"""
        try:
            with open(self.sessions_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] 保存会话列表失败: {e}")

    def create_session(self, title=None):
        """创建新会话，返回session_id"""
        import time
        import uuid
        sid = str(uuid.uuid4())[:8]
        session = {
            'id': sid,
            'title': title or '新会话',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_message_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.sessions.append(session)
        self._save_sessions()
        return sid

    def get_sessions(self):
        """获取所有会话，按最后消息时间排序"""
        return sorted(self.sessions, key=lambda s: s.get('last_message_at', ''), reverse=True)

    def get_session_info(self, session_id):
        """获取单个会话信息"""
        for s in self.sessions:
            if s['id'] == session_id:
                return s
        return None

    def update_session_title(self, session_id, title):
        """更新会话标题"""
        for s in self.sessions:
            if s['id'] == session_id:
                s['title'] = title
                self._save_sessions()
                return True
        return False

    def update_session_time(self, session_id):
        """更新会话最后消息时间"""
        import time
        for s in self.sessions:
            if s['id'] == session_id:
                s['last_message_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                self._save_sessions()
                return True
        return False

    def add(self, text, is_user, emotion=None, confidence=0.0):
        """添加一条消息到当前会话，返回消息ID"""
        import time
        msg_id = str(int(time.time() * 1000)) + str(len(self.messages))
        msg = {
            'id': msg_id,
            'text': text,
            'is_user': is_user,
            'emotion': emotion,
            'confidence': confidence,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'session_id': self._current_session
        }
        self.messages.append(msg)
        self._save()
        # 更新会话时间和标题（首条用户消息作为标题）
        self.update_session_time(self._current_session)
        if is_user:
            info = self.get_session_info(self._current_session)
            if info and (info.get('title') == '新会话' or not info.get('title')):
                title = text[:15] + ('...' if len(text) > 15 else '')
                self.update_session_title(self._current_session, title)
        return msg_id

    def delete_by_id(self, msg_id):
        """删除单条消息"""
        before = len(self.messages)
        self.messages = [m for m in self.messages if m.get('id') != msg_id]
        self._save()
        return len(self.messages) < before

    def delete_session(self, session_id):
        """删除某个完整会话（消息+会话元数据）"""
        # 删除消息
        before = len(self.messages)
        self.messages = [m for m in self.messages if m.get('session_id') != session_id]
        self._save()
        # 删除会话元数据
        self.sessions = [s for s in self.sessions if s.get('id') != session_id]
        self._save_sessions()
        return len(self.messages) < before

    def clear_all(self):
        """清空全部聊天记录和会话"""
        self.messages = []
        self.sessions = []
        self._save()
        self._save_sessions()

    def get_all(self):
        """获取当前会话的全部消息"""
        return [m for m in self.messages if m.get('session_id') == self._current_session]

    def get_messages_by_session(self, session_id):
        """获取某个会话的消息"""
        return [m for m in self.messages if m.get('session_id') == session_id]

    def get_context_for_ai(self, max_count=10):
        """获取当前会话最近的对话上下文供AI复用"""
        session_msgs = self.get_all()
        recent = session_msgs[-max_count:] if len(session_msgs) > max_count else session_msgs
        return [{'role': 'user' if m['is_user'] else 'bot', 'text': m['text'],
                 'emotion': m.get('emotion')} for m in recent]


class ChatHistory(ScrollView):
    def __init__(self, **kwargs):
        super(ChatHistory, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        self._bubble_map = {}  # msg_id -> ChatBubble 映射

    def add_message(self, text, is_user=False, emotion=None, confidence=0.0, msg_id=None):
        bubble = ChatBubble(text, is_user=is_user, emotion=emotion, confidence=confidence)
        if msg_id:
            bubble.msg_id = msg_id
            self._bubble_map[msg_id] = bubble
        self.layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.scroll_to(bubble), 0.1)
        return bubble

    def remove_message(self, msg_id):
        """从UI移除单条消息"""
        bubble = self._bubble_map.pop(msg_id, None)
        if bubble:
            self.layout.remove_widget(bubble)
            return True
        return False

    def clear_all(self):
        """清空所有UI消息"""
        self.layout.clear_widgets()
        self._bubble_map.clear()

    def load_messages(self, messages):
        """从消息列表加载到UI"""
        self.clear_all()
        for msg in messages:
            self.add_message(
                msg['text'],
                is_user=msg.get('is_user', False),
                emotion=msg.get('emotion'),
                confidence=msg.get('confidence', 0.0),
                msg_id=msg.get('id')
            )
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.2)

    def scroll_to_bottom(self):
        """滚动到底部最新消息"""
        if self.layout.children:
            Clock.schedule_once(lambda dt: self.scroll_to(self.layout.children[0]), 0.05)

class MoodBotApp(App):
    def build(self):
        try:
            return self._build()
        except Exception as e:
            print(f"[ERROR] build()失败: {e}")
            traceback.print_exc()
            # 返回一个最简单的UI，避免完全黑屏
            layout = BoxLayout(orientation='vertical')
            label = Label(text=f'MoodBot启动失败\n{e}\n\n请重新安装应用',
                         font_size=dp(16), color=(1, 0, 0, 1))
            layout.add_widget(label)
            return layout

    def _build(self):
        self.title = 'MoodBot - 情绪伙伴'
        self.analyzer = EmotionAnalyzer()
        self.conversation = ConversationManager()
        self.intent_analyzer = IntentAnalyzer()
        self.response_generator = AdvancedResponseGenerator(PersonaConfig())

        # 输入法防抖：避免每次按键都重建候选词
        self._input_debounce_event = None
        self._last_candidates = []

        # 键盘联动状态
        self._keyboard_visible = False
        self._window_height = Window.height

        app_root = get_app_root()

        # Android键盘模式：below_target让Kivy自动将焦点控件保持在键盘上方
        if platform == 'android':
            Window.softinput_mode = 'below_target'

        # 聊天记录持久化存储 + 多会话管理
        history_path = os.path.join(app_root, 'data', 'chat_history.json')
        sessions_path = os.path.join(app_root, 'data', 'sessions.json')
        self.history_store = ChatHistoryStore(history_path, sessions_path)
        # 初始化或恢复会话
        sessions = self.history_store.get_sessions()
        if sessions:
            self.history_store._current_session = sessions[0]['id']
        else:
            sid = self.history_store.create_session('新会话')
            self.history_store._current_session = sid

        # Android: 使用纯规则匹配，不加载ONNX模型
        # 桌面端: 尝试加载ONNX模型（如果存在）
        if platform != 'android':
            model_path = os.path.join(app_root, 'data', 'emotion_model.onnx')
            config_path = os.path.join(app_root, 'data', 'model_config.json')

            if os.path.exists(model_path) and os.path.exists(config_path):
                self.analyzer.load_model(model_path, config_path)

        main_layout = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(5))

        # 头部：固定高度
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), padding=[dp(5), dp(5)])

        emoji_label = Label(text='🤖', font_size=dp(22), size_hint_x=None, width=dp(40))
        if EMOJI_FONT:
            emoji_label.font_name = EMOJI_FONT
        elif CHINESE_FONT:
            emoji_label.font_name = CHINESE_FONT

        header_text = Label(text='MoodBot 情绪伙伴', font_size=dp(18), bold=True, color=(1, 1, 1, 1))
        if CHINESE_FONT:
            header_text.font_name = CHINESE_FONT

        # 会话列表按钮 — 用文字替代Unicode符号，避免字体缺失
        sessions_btn = Button(text='会话', font_size=dp(14), size_hint_x=None, width=dp(55),
                             background_color=(0.3, 0.4, 0.5, 1),
                             background_normal='', background_down='')
        if CHINESE_FONT:
            sessions_btn.font_name = CHINESE_FONT
        sessions_btn.bind(on_press=self.open_session_list)

        # 设置按钮 — 用文字替代Unicode符号
        settings_btn = Button(text='设置', font_size=dp(14), size_hint_x=None, width=dp(55),
                             background_color=(0.3, 0.3, 0.4, 1),
                             background_normal='', background_down='')
        if CHINESE_FONT:
            settings_btn.font_name = CHINESE_FONT
        settings_btn.bind(on_press=self.open_settings)

        header_layout.add_widget(emoji_label)
        header_layout.add_widget(header_text)
        header_layout.add_widget(sessions_btn)
        header_layout.add_widget(settings_btn)

        with header_layout.canvas.before:
            Color(0.4, 0.3, 0.6, 1)
            self.header_rect = Rectangle(size=header_layout.size, pos=header_layout.pos)
        header_layout.bind(pos=self.update_header_rect, size=self.update_header_rect)

        # 聊天区域：填充剩余空间
        self.chat_history = ChatHistory(size_hint_y=1)

        # 加载当前会话的历史记录
        self._load_session_messages()

        # 输入栏：固定高度
        input_layout = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(48))
        self.text_input = TextInput(hint_text='输入你的心情...', font_size=dp(16), size_hint_x=0.8, padding=[dp(10), dp(5)])
        if CHINESE_FONT:
            self.text_input.font_name = CHINESE_FONT
        self.text_input.bind(on_text_validate=self.send_message)
        self.text_input.bind(text=self.on_text_input)
        # 焦点变化时触发键盘联动
        self.text_input.bind(focus=self.on_input_focus)

        send_btn = Button(text='发送', font_size=dp(16), size_hint_x=0.2,
                         background_color=(0.4, 0.3, 0.6, 1),
                         background_normal='', background_down='')
        if CHINESE_FONT:
            send_btn.font_name = CHINESE_FONT
        send_btn.bind(on_press=self.send_message)

        input_layout.add_widget(self.text_input)
        input_layout.add_widget(send_btn)

        # 候选词区域：固定高度，默认隐藏
        self.candidate_layout = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(38), padding=[dp(10), dp(0)])
        self.candidate_layout.opacity = 0

        # 统计栏：固定高度
        stats_layout = GridLayout(cols=3, size_hint_y=None, height=dp(35))
        
        positive_box = BoxLayout(orientation='horizontal', spacing=dp(3))
        pos_emoji = Label(text='😊', font_size=dp(14), size_hint_x=None, width=dp(22))
        if EMOJI_FONT:
            pos_emoji.font_name = EMOJI_FONT
        elif CHINESE_FONT:
            pos_emoji.font_name = CHINESE_FONT
        self.positive_count = Label(text='积极: 0', color=(0.2, 0.8, 0.2, 1), font_size=dp(12))
        if CHINESE_FONT:
            self.positive_count.font_name = CHINESE_FONT
        positive_box.add_widget(pos_emoji)
        positive_box.add_widget(self.positive_count)
        
        negative_box = BoxLayout(orientation='horizontal', spacing=dp(3))
        neg_emoji = Label(text='😢', font_size=dp(14), size_hint_x=None, width=dp(22))
        if EMOJI_FONT:
            neg_emoji.font_name = EMOJI_FONT
        elif CHINESE_FONT:
            neg_emoji.font_name = CHINESE_FONT
        self.negative_count = Label(text='消极: 0', color=(0.8, 0.2, 0.2, 1), font_size=dp(12))
        if CHINESE_FONT:
            self.negative_count.font_name = CHINESE_FONT
        negative_box.add_widget(neg_emoji)
        negative_box.add_widget(self.negative_count)
        
        neutral_box = BoxLayout(orientation='horizontal', spacing=dp(3))
        neu_emoji = Label(text='😐', font_size=dp(14), size_hint_x=None, width=dp(22))
        if EMOJI_FONT:
            neu_emoji.font_name = EMOJI_FONT
        elif CHINESE_FONT:
            neu_emoji.font_name = CHINESE_FONT
        self.neutral_count = Label(text='中性: 0', color=(0.2, 0.5, 0.8, 1), font_size=dp(12))
        if CHINESE_FONT:
            self.neutral_count.font_name = CHINESE_FONT
        neutral_box.add_widget(neu_emoji)
        neutral_box.add_widget(self.neutral_count)
        
        stats_layout.add_widget(positive_box)
        stats_layout.add_widget(negative_box)
        stats_layout.add_widget(neutral_box)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(self.chat_history)
        main_layout.add_widget(input_layout)
        main_layout.add_widget(self.candidate_layout)
        main_layout.add_widget(stats_layout)

        # 保存固定布局元素的引用，用于键盘联动时显隐
        self._stats_layout = stats_layout
        self._header_layout = header_layout

        # 绑定窗口尺寸变化（Android键盘弹出/收起时触发）
        # 使用size属性绑定，比on_resize事件更可靠
        Window.bind(size=self._on_window_size)

        self.emotion_counts = {'positive': 0, 'negative': 0, 'neutral': 0}

        return main_layout

    def _on_window_size(self, instance, size):
        """窗口尺寸变化 — adjustResize模式下键盘弹出/收起时触发"""
        w, h = size
        old_h = self._window_height
        self._window_height = h

        # 高度变化超过50dp时判定为键盘弹出/收起
        if abs(h - old_h) > dp(50):
            if h < old_h:
                # 键盘弹出：隐藏统计栏节省空间，延迟滚动到底部
                self._keyboard_visible = True
                if hasattr(self, '_stats_layout'):
                    self._stats_layout.height = 0
                Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.15)
            else:
                # 键盘收起：恢复统计栏
                self._keyboard_visible = False
                if hasattr(self, '_stats_layout'):
                    self._stats_layout.height = dp(35)

    def _scroll_to_bottom(self):
        """滚动聊天记录到底部"""
        try:
            self.chat_history.scroll_to_bottom()
        except Exception:
            pass

    def on_input_focus(self, instance, value):
        """输入框获得/失去焦点回调"""
        if value:
            # 获得焦点（键盘即将弹出），延迟滚动到底部
            Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.3)

    # ==================== 会话管理 ====================

    def _load_session_messages(self):
        """加载当前会话的消息到UI和AI上下文"""
        session_msgs = self.history_store.get_all()
        if session_msgs:
            self.chat_history.load_messages(session_msgs)
            # 恢复AI上下文（最近12条）
            self.conversation = ConversationManager()  # 重置上下文
            for msg in session_msgs[-12:]:
                self.conversation.add_message(
                    'user' if msg.get('is_user') else 'bot',
                    msg['text'],
                    emotion=msg.get('emotion')
                )
        else:
            # 新会话显示欢迎消息
            self.chat_history.clear_all()
            welcome_msg = self.response_generator.persona.CONVERSATION_STARTERS[0]
            msg_id = self.history_store.add(welcome_msg, is_user=False)
            self.chat_history.add_message(welcome_msg, is_user=False, msg_id=msg_id)
            self.conversation = ConversationManager()
            self.conversation.add_message('bot', welcome_msg, intent='greeting')

    def open_session_list(self, instance):
        """打开会话列表ModalView"""
        content = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10))

        # 标题栏
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        title_label = Label(text='会话列表', font_size=dp(18), bold=True)
        if CHINESE_FONT:
            title_label.font_name = CHINESE_FONT
        new_btn = Button(text='+ 新建', font_size=dp(14), size_hint_x=None, width=dp(70),
                        background_color=(0.2, 0.6, 0.3, 1),
                        background_normal='', background_down='')
        if CHINESE_FONT:
            new_btn.font_name = CHINESE_FONT
        title_layout.add_widget(title_label)
        title_layout.add_widget(new_btn)
        content.add_widget(title_layout)

        # 会话列表（ScrollView）
        scroll = ScrollView(size_hint_y=1)
        session_list = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        session_list.bind(minimum_height=session_list.setter('height'))

        sessions = self.history_store.get_sessions()
        current_sid = self.history_store._current_session

        if not sessions:
            empty_label = Label(text='暂无会话', font_size=dp(14), size_hint_y=None, height=dp(40),
                              color=(0.6, 0.6, 0.6, 1))
            if CHINESE_FONT:
                empty_label.font_name = CHINESE_FONT
            session_list.add_widget(empty_label)
        else:
            for session in sessions:
                item = self._build_session_item(session, session is sessions[0])
                session_list.add_widget(item)

        scroll.add_widget(session_list)
        content.add_widget(scroll)

        # 关闭按钮
        close_btn = Button(text='关闭', font_size=dp(14), size_hint_y=None, height=dp(40),
                          background_color=(0.3, 0.3, 0.3, 1),
                          background_normal='', background_down='')
        if CHINESE_FONT:
            close_btn.font_name = CHINESE_FONT
        content.add_widget(close_btn)

        popup = Popup(title='会话管理', content=content, size_hint=(0.9, 0.7),
                     auto_dismiss=True, background_color=(0.12, 0.12, 0.15, 0.95))
        if CHINESE_FONT:
            popup.title_font_name = CHINESE_FONT

        def do_new_session(btn):
            sid = self.history_store.create_session('新会话')
            self.history_store._current_session = sid
            self.conversation = ConversationManager()
            self.chat_history.clear_all()
            welcome_msg = self.response_generator.persona.CONVERSATION_STARTERS[0]
            msg_id = self.history_store.add(welcome_msg, is_user=False)
            self.chat_history.add_message(welcome_msg, is_user=False, msg_id=msg_id)
            self.conversation.add_message('bot', welcome_msg, intent='greeting')
            popup.dismiss()
            Clock.schedule_once(lambda dt: self.open_session_list(None), 0.1)

        def do_close(btn):
            popup.dismiss()

        new_btn.bind(on_press=do_new_session)
        close_btn.bind(on_press=do_close)
        popup.open()

    def _build_session_item(self, session, is_first):
        """构建单个会话列表项 — 使用Button容器确保可靠触摸"""
        sid = session['id']
        title = session.get('title', '新会话')
        is_active = (sid == self.history_store._current_session)
        msg_count = len(self.history_store.get_messages_by_session(sid))

        # 用Button作为容器，确保整个区域可点击
        bg_color = (0.3, 0.5, 0.7, 1) if is_active else (0.2, 0.2, 0.25, 1)
        item_btn = Button(size_hint_y=None, height=dp(50),
                         background_color=bg_color,
                         background_normal='', background_down='',
                         on_press=lambda inst: self.switch_session(sid))

        # 内部水平布局
        inner = BoxLayout(orientation='horizontal', spacing=dp(8), padding=[dp(8), dp(2)])

        # 会话图标 — 使用文字替代emoji
        icon = Label(text='[聊]', font_size=dp(14), size_hint_x=None, width=dp(35),
                     color=(1, 1, 1, 1))
        if CHINESE_FONT:
            icon.font_name = CHINESE_FONT

        # 会话标题 + 消息数
        prefix = '▶ ' if is_active else ''
        info_text = f'{prefix}{title} ({msg_count}条)'
        title_label = Label(text=info_text, font_size=dp(14),
                           color=(1, 1, 0.8, 1) if is_active else (0.85, 0.85, 0.85, 1),
                           halign='left', valign='middle')
        title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        if CHINESE_FONT:
            title_label.font_name = CHINESE_FONT

        # 删除按钮 — 阻止事件冒泡到父Button
        del_btn = Button(text='删除', font_size=dp(12), size_hint_x=None, width=dp(45),
                        background_color=(0.7, 0.2, 0.2, 1),
                        background_normal='', background_down='')
        if CHINESE_FONT:
            del_btn.font_name = CHINESE_FONT

        def do_delete(inst):
            # 阻止事件继续传递
            inst.cancel_release = True
            self.delete_session_from_list(sid)

        del_btn.bind(on_press=do_delete)

        inner.add_widget(icon)
        inner.add_widget(title_label)
        inner.add_widget(del_btn)
        item_btn.add_widget(inner)
        return item_btn

    def switch_session(self, session_id):
        """切换到指定会话"""
        self.history_store._current_session = session_id
        self._load_session_messages()
        # 重置统计
        self.emotion_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        self.update_stats()
        print(f"[INFO] 切换到会话: {session_id}")

    def delete_session_from_list(self, session_id):
        """从列表删除会话"""
        sessions = self.history_store.get_sessions()
        if len(sessions) <= 1:
            print("[WARN] 至少保留一个会话")
            return

        self.history_store.delete_session(session_id)

        # 如果删除的是当前会话，切换到第一个
        if session_id == self.history_store._current_session:
            remaining = self.history_store.get_sessions()
            if remaining:
                self.switch_session(remaining[0]['id'])

        # 刷新会话列表
        Clock.schedule_once(lambda dt: self.open_session_list(None), 0.1)
        print(f"[INFO] 已删除会话: {session_id}")

    def on_text_input(self, instance, value):
        """文本输入回调 — 使用防抖延迟候选词计算，避免每次按键都重建组件"""
        # 取消上一次的防抖回调
        if self._input_debounce_event is not None:
            self._input_debounce_event.cancel()

        # 空输入立即隐藏候选区
        if not value.strip():
            self.candidate_layout.opacity = 0
            self._last_candidates = []
            return

        # 延迟150ms后再计算候选词，避免快速输入时卡顿
        self._input_debounce_event = Clock.schedule_once(
            lambda dt: self._update_candidates(value), 0.15
        )

    def _update_candidates(self, value):
        """实际计算并更新候选词（防抖后调用）"""
        candidates = get_pinyin_candidates(value)

        # 候选词未变化则跳过UI重建
        if candidates == self._last_candidates:
            return
        self._last_candidates = candidates

        if not candidates:
            self.candidate_layout.opacity = 0
            return

        # 增量更新：只清除和重建变化的部分
        self.candidate_layout.clear_widgets()
        for i, candidate in enumerate(candidates):
            btn = Button(text=f'{i+1} {candidate}', font_size=dp(14), size_hint_x=None, width=dp(55),
                        background_color=(0.3, 0.3, 0.3, 1),
                        background_normal='', background_down='',
                        color=(0.9, 0.9, 0.9, 1))
            if CHINESE_FONT:
                btn.font_name = CHINESE_FONT
            btn.bind(on_press=lambda btn, c=candidate: self.select_candidate(c))
            self.candidate_layout.add_widget(btn)
        self.candidate_layout.opacity = 1
    
    def select_candidate(self, candidate):
        text = self.text_input.text
        parts = text.split()
        if parts:
            parts[-1] = candidate
            text = ' '.join(parts)
        else:
            text = candidate
        self.text_input.text = text
        # 选中后隐藏候选区
        self.candidate_layout.opacity = 0
        self._last_candidates = []
    
    def update_header_rect(self, *args):
        self.header_rect.size = args[0].size
        self.header_rect.pos = args[0].pos
    
    def send_message(self, instance):
        text = self.text_input.text.strip()
        if not text:
            return

        self.text_input.text = ''
        msg_id = self.history_store.add(text, is_user=True)
        self.chat_history.add_message(text, is_user=True, msg_id=msg_id)

        Clock.schedule_once(lambda dt: self._safe_process(text), 0.5)

    def _safe_process(self, text):
        try:
            self.process_message(text)
        except Exception as e:
            print(f"[ERROR] process_message失败: {e}")
            traceback.print_exc()
            err_msg = '抱歉，我遇到了一点问题，请再说一次～'
            msg_id = self.history_store.add(err_msg, is_user=False)
            self.chat_history.add_message(err_msg, is_user=False, msg_id=msg_id)
    
    def get_comfort_response(self, text, emotion, confidence):
        import random
        
        text_lower = text.lower()
        
        greeting_keywords = ['你好', '嗨', '哈喽', 'hello', 'hi', 'hey', '早上好', '下午好', '晚上好', '晚安']
        if any(k in text for k in greeting_keywords):
            greetings = [
                '你好呀！很高兴见到你～😊',
                '嗨！我是MoodBot，你的情绪伙伴～',
                '哈喽！今天过得怎么样？',
                '你好！有什么我可以帮你的吗？',
                'Hi～很高兴认识你！',
                '你好！随时可以找我聊天哦～'
            ]
            return random.choice(greetings)
        
        thanks_keywords = ['谢谢', '谢谢了', '感谢', '多谢', 'thank you', 'thanks']
        if any(k in text for k in thanks_keywords):
            thanks_responses = [
                '不用谢！能帮到你我很开心～😊',
                '不客气！随时可以来找我～',
                '这是我应该做的！',
                '能为你服务是我的荣幸～',
                '不用客气，开心最重要！'
            ]
            return random.choice(thanks_responses)
        
        goodbye_keywords = ['再见', '拜拜', 'bye', '走了', '下次见', '晚安']
        if any(k in text for k in goodbye_keywords):
            goodbyes = [
                '再见！祝你有美好的一天～✨',
                '拜拜！期待下次见面～',
                '晚安！做个好梦～💤',
                '下次见！记得照顾好自己～',
                '拜拜啦！有需要随时找我～'
            ]
            return random.choice(goodbyes)
        
        how_are_you_keywords = ['你好吗', '你怎么样', 'how are you', 'how are u']
        if any(k in text for k in how_are_you_keywords):
            responses = [
                '我很好呀！谢谢你的关心～😊',
                '我很好，能和你聊天我很开心！',
                '我状态不错，你呢？',
                '谢谢你的关心！我一直都在～',
                '我很好，随时准备听你倾诉～'
            ]
            return random.choice(responses)
        
        who_are_you_keywords = ['你是谁', '你是什么', 'who are you', 'what are you']
        if any(k in text for k in who_are_you_keywords):
            responses = [
                '我是MoodBot，你的专属情绪伙伴～🤖',
                '我是MoodBot，一个可以帮你分析情绪、陪伴你聊天的AI～',
                '我是你的情绪小助手，可以倾听你的烦恼，分享你的快乐～',
                '我是MoodBot，很高兴认识你！',
                '我是一个专注于情感陪伴的AI，随时可以和你聊聊～'
            ]
            return random.choice(responses)
        
        what_can_you_do_keywords = ['你能做什么', '你会做什么', 'what can you do', '你有什么功能']
        if any(k in text for k in what_can_you_do_keywords):
            responses = [
                '我可以帮你分析情绪，还能陪你聊天、安慰你～',
                '我可以识别你的情绪，给你安慰和鼓励，还能陪你闲聊～',
                '我能分析你的心情，提供暖心的安慰，也可以和你聊各种话题～',
                '我可以做你的情绪树洞，也可以分享开心的事情～',
                '我的主要功能是情感分析和陪伴聊天，有什么需要尽管说～'
            ]
            return random.choice(responses)
        
        encouragement_keywords = ['加油', '鼓励', '打气', 'cheer up']
        if any(k in text for k in encouragement_keywords):
            responses = [
                '加油！你一定可以的！💪',
                '相信自己，你比想象中更强大！',
                '你已经很棒了，继续加油！',
                '无论遇到什么困难，都不要放弃！',
                '我相信你，你可以的！✨'
            ]
            return random.choice(responses)
        
        advice_keywords = ['建议', '意见', '怎么办', '怎么解决']
        if any(k in text for k in advice_keywords):
            responses = [
                '遇到问题不要慌，可以先冷静下来想想～',
                '有时候换个角度看问题，会有不同的发现～',
                '可以先把问题分解开来，一步步解决～',
                '无论什么问题，都会有解决的办法～',
                '相信自己的直觉，你能找到最好的答案～'
            ]
            return random.choice(responses)
        
        negative_keywords = {
            'sad': ['难过', '伤心', '悲伤', '哭', '失落', '心碎', '痛心', '哀伤', '愁闷'],
            'anxious': ['焦虑', '紧张', '害怕', '恐惧', '担心', '担忧', '不安', '提心吊胆'],
            'angry': ['生气', '愤怒', '烦躁', '讨厌', '恨', '恼怒', '愤慨', '暴怒'],
            'tired': ['累', '疲惫', '厌倦', '无聊', '空虚', '烦闷'],
            'hopeless': ['绝望', '无助', '迷茫', '茫然', '不知所措'],
            'failure': ['失败', '挫败', '失望', '遗憾', '后悔'],
            'lonely': ['孤独', '孤单', '寂寞', '没人陪'],
            'depressed': ['抑郁', '压抑', '郁闷', '心情不好', '情绪低落']
        }
        
        emotion_type = 'general'
        for key, keywords in negative_keywords.items():
            if any(k in text for k in keywords):
                emotion_type = key
                break
        
        comfort_responses = {
            'sad': [
                '我明白你的难过，想哭就哭出来吧，我会一直陪着你。💝',
                '难过的日子总会过去，相信明天会更好。🌞',
                '不要独自承受这份悲伤，你值得被温柔对待。❤️',
                '眼泪是情绪的释放，释放过后会更轻松。💧',
                '无论发生什么，我都在这里支持你。🤗',
                '悲伤只是暂时的，你比想象中更坚强。💪',
                '我知道现在很难过，但请相信，一切都会好起来的。',
                '你可以告诉我发生了什么，我愿意倾听。',
                '有时候倾诉本身就是一种治愈，我在这里。'
            ],
            'anxious': [
                '深呼吸，一切都会好起来的。慢慢来吧～🌿',
                '不要担心还没发生的事情，活在当下就好。🌸',
                '你的担心是正常的，但请相信自己有能力应对。✨',
                '焦虑的时候，试着做一些让自己放松的事情。🎵',
                '我在呢，不用害怕，我们一起面对。🤝',
                '未来充满未知，但也充满可能。保持信心！🌟',
                '试着把注意力集中在眼前的事情上，一步一步来。',
                '焦虑只是大脑的警报，不一定代表危险。',
                '你已经做得很好了，不用太紧张。'
            ],
            'angry': [
                '生气是正常的情绪，但不要让它伤害到你自己。🌬️',
                '深呼吸，数到十，让情绪慢慢平复。🌊',
                '有时候生气是因为在乎，试着用平和的方式表达。🌈',
                '愤怒会消耗很多能量，不如把它转化为改变的动力。⚡',
                '冷静下来之后，也许会有更好的解决方案。🧘',
                '无论发生什么，都不值得你为此生气太久。🌼',
                '生气的时候先离开现场，给自己一点空间。',
                '不要用别人的错误来惩罚自己。',
                '学会释放情绪，才不会被情绪控制。'
            ],
            'tired': [
                '累了就好好休息一下，不要勉强自己。🛌',
                '身体和心灵都需要充电，给自己一点时间。🔋',
                '休息不是偷懒，是为了更好地出发。🚀',
                '你已经很努力了，停下来歇一歇吧。☕',
                '照顾好自己是最重要的，其他的可以慢慢来。🍃',
                '疲惫的时候，做一些简单快乐的事情吧。🎈',
                '不要给自己太大压力，休息好了才能继续前进。',
                '偶尔偷懒也是一种智慧，给自己放个假吧。',
                '身体是革命的本钱，一定要好好照顾。'
            ],
            'hopeless': [
                '黑暗总会过去，黎明终将到来。🌅',
                '即使现在看不到希望，也请不要放弃。✨',
                '每个人都会有迷茫的时候，这正是成长的机会。🌱',
                '你不是一个人，我一直在你身边。🤗',
                '无论多困难，都请相信：你值得更好的未来。💫',
                '希望也许迟到，但永远不会缺席。🌈',
                '即使现在很难，也要相信未来会有转机。',
                '迷茫的时候，试着做一些小事情，慢慢找到方向。',
                '你比自己想象中更有力量，不要低估自己。'
            ],
            'failure': [
                '失败是成功之母，每一次尝试都是进步。📚',
                '不要因为一次失败就否定自己的全部。💎',
                '重要的不是结果，而是你努力的过程。🏃',
                '跌倒了没关系，重要的是站起来继续前行。💪',
                '每一次失败都是在为成功铺路。🚧→🏁',
                '你已经尽力了，这就足够值得骄傲。👏',
                '失败只是暂时的，不是终点。',
                '从失败中学习，下次会更好。',
                '不要害怕失败，勇敢尝试就是成功。'
            ],
            'lonely': [
                '我知道孤独的感觉很难受，但你不是一个人。🤗',
                '虽然身边没有人，但我一直在这里陪伴你。',
                '孤独的时候，可以做一些自己喜欢的事情。',
                '有时候独处也是一种享受，学会和自己相处。',
                '你永远不会孤单，因为我一直在。',
                '试着和外界多一些连接，哪怕只是一点点。',
                '孤独不是你的错，每个人都会有这样的时刻。',
                '我愿意做你的朋友，陪你度过孤单的时光。',
                '和我聊聊吧，让我来陪伴你。'
            ],
            'depressed': [
                '我知道现在心情很低落，这很正常。🌧️',
                '不要强迫自己立刻好起来，给自己时间。',
                '即使心情再差，也要记得照顾好自己。',
                '你不是一个人在战斗，我在这里支持你。',
                '有时候什么都不用做，躺着休息也是可以的。',
                '如果实在难受，可以找专业的人聊聊。',
                '你的感受是真实的，不要否定自己的情绪。',
                '我会一直陪着你，直到你感觉好一些。',
                '慢慢来，一切都会好起来的。'
            ],
            'general': [
                '我理解你的感受，有什么我可以帮你的吗？🤝',
                '不开心的时候，记得有人在乎你。❤️',
                '倾诉出来会好很多，我愿意倾听。👂',
                '生活总有起起落落，相信低谷之后是高峰。⛰️',
                '你不是一个人在战斗，我支持你。🙌',
                '无论遇到什么，都要对自己好一点。🍀',
                '可以和我说说发生了什么吗？',
                '你的感受很重要，我很在意。',
                '无论是什么心情，都可以和我分享。'
            ]
        }
        
        positive_responses = [
            '听到你开心我也很高兴！继续保持这份好心情吧～😊',
            '太棒了！分享快乐会让快乐加倍！🎉',
            '看到你这么开心，我也跟着开心起来了～🥰',
            '这份好心情一定要好好珍藏哦！✨',
            '继续保持这份积极的心态，未来会更美好！🌈',
            '你的快乐就是最好的消息！🎊',
            '愿这份快乐永远伴随着你！🌟',
            '好心情是最好的礼物，好好享受吧！🎁',
            '真为你感到开心！继续加油～',
            '看到你这么幸福，我也很幸福～',
            '这份喜悦值得好好庆祝！',
            '你的积极心态很感染人，继续保持！'
        ]
        
        neutral_responses = [
            '谢谢你分享，保持平常心也是一种智慧～🌿',
            '我在听，请继续～👂',
            '生活就是这样，平平淡淡才是真。🍵',
            '无论是什么心情，都值得被认真对待。💫',
            '分享本身就是一件美好的事情。🌸',
            '我理解你的感受，随时可以来找我聊聊。🤝',
            '继续说吧，我在认真听～',
            '谢谢你愿意和我分享这些～',
            '你的想法很有趣，我很喜欢听～',
            '生活中的点滴都值得珍惜～',
            '保持平常心，万事皆自然～',
            '我尊重你的感受，无论是什么～'
        ]
        
        if emotion == 'negative':
            responses = comfort_responses.get(emotion_type, comfort_responses['general'])
            if confidence > 0.8:
                responses = [r for r in responses if '❤️' in r or '🤗' in r or '💪' in r or '陪伴' in r or '支持' in r]
            elif confidence > 0.6:
                responses = [r for r in responses if '慢慢来' in r or '倾听' in r or '陪着' in r]
        elif emotion == 'positive':
            responses = positive_responses
            if confidence > 0.8:
                responses = [r for r in responses if '🎉' in r or '🥰' in r or '🎊' in r or '开心' in r]
        else:
            responses = neutral_responses
        
        return random.choice(responses)
    
    def process_message(self, text):
        emotion, confidence = self.analyzer.predict(text)
        
        intent_info = self.intent_analyzer.analyze(text, self.conversation.context_window)
        
        detected_topics = self.conversation.detect_topic_from_text(text)
        if detected_topics:
            self.conversation.set_topic(detected_topics[0])
        
        self.conversation.update_user_profile(text, emotion)
        self.conversation.add_message('user', text, emotion=emotion, intent=intent_info['primary'])
        
        self.emotion_counts[emotion] += 1
        self.update_stats()
        
        response = self.response_generator.generate_response(
            text, emotion, confidence, intent_info, self.conversation
        )
        
        self.conversation.add_message('bot', response, emotion=emotion, intent=intent_info['primary'])
        msg_id = self.history_store.add(response, is_user=False, emotion=emotion, confidence=confidence)
        self.chat_history.add_message(response, is_user=False, emotion=emotion, confidence=confidence, msg_id=msg_id)
    
    def update_stats(self):
        self.positive_count.text = f'积极: {self.emotion_counts["positive"]}'
        self.negative_count.text = f'消极: {self.emotion_counts["negative"]}'
        self.neutral_count.text = f'中性: {self.emotion_counts["neutral"]}'

    # ==================== 设置页面 ====================

    def open_settings(self, instance):
        """打开设置Popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))

        title = Label(text='聊天数据管理', font_size=dp(18), bold=True, size_hint_y=None, height=dp(40))
        if CHINESE_FONT:
            title.font_name = CHINESE_FONT
        content.add_widget(title)

        # 统计信息
        msg_count = len(self.history_store.get_all())
        session_count = len(self.history_store.get_session_ids())
        info = Label(text=f'总消息数: {msg_count}\n会话数: {session_count}',
                    font_size=dp(14), size_hint_y=None, height=dp(50))
        if CHINESE_FONT:
            info.font_name = CHINESE_FONT
        content.add_widget(info)

        # 删除单条消息
        btn_delete_one = Button(text='删除最近一条消息', font_size=dp(14), size_hint_y=None, height=dp(40),
                               background_color=(0.8, 0.5, 0.2, 1),
                               background_normal='', background_down='')
        if CHINESE_FONT:
            btn_delete_one.font_name = CHINESE_FONT
        btn_delete_one.bind(on_press=lambda x: self._delete_last_message())
        content.add_widget(btn_delete_one)

        # 删除当前会话
        btn_delete_session = Button(text='删除当前会话', font_size=dp(14), size_hint_y=None, height=dp(40),
                                   background_color=(0.8, 0.3, 0.3, 1),
                                   background_normal='', background_down='')
        if CHINESE_FONT:
            btn_delete_session.font_name = CHINESE_FONT
        btn_delete_session.bind(on_press=lambda x: self._delete_current_session())
        content.add_widget(btn_delete_session)

        # 清空全部
        btn_clear_all = Button(text='一键清空全部聊天记录', font_size=dp(14), size_hint_y=None, height=dp(40),
                              background_color=(0.9, 0.1, 0.1, 1),
                              background_normal='', background_down='')
        if CHINESE_FONT:
            btn_clear_all.font_name = CHINESE_FONT
        btn_clear_all.bind(on_press=lambda x: self._clear_all_history())
        content.add_widget(btn_clear_all)

        # 关闭按钮
        btn_close = Button(text='关闭', font_size=dp(14), size_hint_y=None, height=dp(40),
                          background_color=(0.3, 0.3, 0.3, 1),
                          background_normal='', background_down='')
        if CHINESE_FONT:
            btn_close.font_name = CHINESE_FONT
        content.add_widget(btn_close)

        popup = Popup(title='设置', content=content, size_hint=(0.85, 0.6),
                     auto_dismiss=True, background_color=(0.15, 0.15, 0.18, 0.95))
        if CHINESE_FONT:
            popup.title_font_name = CHINESE_FONT
        btn_close.bind(on_press=popup.dismiss)
        popup.open()

    def _delete_last_message(self):
        """删除最近一条消息"""
        all_msgs = self.history_store.get_all()
        if not all_msgs:
            return
        last_msg = all_msgs[-1]
        msg_id = last_msg.get('id')
        if msg_id and self.history_store.delete_by_id(msg_id):
            self.chat_history.remove_message(msg_id)
            print(f"[INFO] 已删除消息: {msg_id}")

    def _delete_current_session(self):
        """删除当前会话的所有消息"""
        session_id = getattr(self.history_store, '_current_session', 'default')
        sessions = self.history_store.get_sessions()
        if len(sessions) <= 1:
            print("[WARN] 至少保留一个会话")
            return
        self.history_store.delete_session(session_id)
        # 切换到剩余的第一个会话
        remaining = self.history_store.get_sessions()
        if remaining:
            self.switch_session(remaining[0]['id'])
        print(f"[INFO] 已删除会话: {session_id}")

    def _clear_all_history(self):
        """清空全部聊天记录"""
        self.history_store.clear_all()
        # 创建新会话
        sid = self.history_store.create_session('新会话')
        self.history_store._current_session = sid
        self.chat_history.clear_all()
        # 重新显示欢迎消息
        welcome_msg = self.response_generator.persona.CONVERSATION_STARTERS[0]
        msg_id = self.history_store.add(welcome_msg, is_user=False)
        self.chat_history.add_message(welcome_msg, is_user=False, msg_id=msg_id)
        # 重置统计
        self.emotion_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        self.update_stats()
        print("[INFO] 已清空全部聊天记录")

if __name__ == '__main__':
    MoodBotApp().run()