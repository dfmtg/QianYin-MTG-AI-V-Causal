import sys
import os
import json
import random
import re
import threading
import secrets
import math
import unicodedata
import hashlib
import gzip
import lz4.frame
import queue
import time
import traceback
from collections import defaultdict, OrderedDict
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
# Web 框架依赖（使用标准库）
import socketserver
import socket
from urllib.parse import unquote

class IPv6HTTPServer(HTTPServer):
    """IPv6兼容的HTTP服务器，支持::绑定"""
    address_family = socket.AF_INET6

    def server_bind(self):
        # 禁用IPv6-only模式，允许IPv4映射（双栈）
        # Mac/Linux/Windows 均支持 IPV6_V6ONLY，Windows 默认已是双栈但不影响
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (OSError, socket.error):
            pass  # 某些环境可能不支持，忽略
        super().server_bind()

CONFIG_FILE = "config.json"
WEIGHTS_INFO_FILE = "weights_info.json"
LOG_FILE = "mtg_ai_errors.log"
PERF_LOG_FILE = "mtg_ai_performance.log"
LANG_FILE = "language.json"
API_KEYS_FILE = "api_keys.json"

# 安全配置
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB 请求体限制

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
ALLOWED_PATH_PREFIX = SCRIPT_DIR  # 只允许在脚本目录内操作

def _validate_path(path):
    """验证路径安全性，防止路径遍历攻击"""
    if path is None:
        return None
    real_path = os.path.realpath(path)
    if real_path.startswith(ALLOWED_PATH_PREFIX):
        return real_path
    return None

DEFAULT_LANG = {
    "zh": {
        "title": "千因 - MTG AI V-Causal",
        "chat_window": "对话窗口",
        "send": "发送",
        "clear": "清空",
        "session_management": "会话管理",
        "new_session": "新建会话",
        "switch_session": "切换会话",
        "rename_session": "重命名会话",
        "delete_session": "删除会话",
        "model_management": "模型管理",
        "save_model": "保存模型",
        "load_model": "加载模型",
        "view_stats": "查看统计",
        "model_info": "模型信息",
        "personality_settings": "性格设置",
        "view_personality": "查看性格",
        "edit_personality": "修改性格",
        "preference_settings": "偏好设置",
        "view_preferences": "查看偏好",
        "add_preference": "添加偏好",
        "chat_management": "对话管理",
        "export_chat": "导出对话",
        "import_chat": "导入对话",
        "api_server": "API服务器",
        "weights_management": "权重管理",
        "set_weights_path": "设置权重路径",
        "backup_weights": "备份权重",
        "restore_weights": "恢复权重",
        "api_description": "API说明",
        "language_settings": "语言设置",
        "current_language": "当前语言",
        "switch_chinese": "切换到中文",
        "switch_english": "切换到英文",
        "import_language_pack": "导入语言包",
        "language_pack_format": "语言包格式说明",
        "select_weights_dir": "请选择模型权重文件的存储目录：",
        "select_directory": "选择目录",
        "skip": "跳过",
        "success": "成功",
        "warning": "警告",
        "error": "错误",
        "port": "端口",
        "dimension": "维度",
        "layers": "层数",
        "token_count": "Token量",
        "learning_data": "学习数据",
        "cpu": "CPU",
        "memory": "内存",
        "api_key": "API密钥",
        "tokens": "Tokens",
        "token_balance": "Token余额",
        "token_usage": "Token使用量",
        "server_status": "服务器状态",
        "stopped": "已停止",
        "running": "运行中",
        "start_api": "启动API (4000)",
        "stop_api": "停止API",
        "cisl_interface": "CISL接口 (9000)",
        "no_auth": "无鉴权",
        "basic_info": "基本信息",
        "realtime_status": "实时状态",
        "training_mode": "训练模式",
        "start_training": "开始训练",
        "stop_training": "停止训练",
        "instance_info": "实例信息",
        "model_name": "千因",
        "model": "千因",
        "switched_to_session": "已切换到会话：",
        "session_already_exists": "会话名称已存在",
        "session_name_empty": "会话名称不能为空",
        "cannot_rename_default": "无法重命名默认会话",
        "cannot_delete_default": "无法删除默认会话",
        "insufficient_tokens": "Token余额不足，请充值后再使用",
        "chat_cleared": "对话已清空",
        "training_stopped": "训练已停止",
        "language_switched": "语言已切换为",
        "model_saved_to": "模型已保存到：",
        "model_loaded_to": "模型已加载到会话：",
        "weights_path_set_to": "权重路径已设置为：",
        "weights_backed_up_to": "权重已备份到：",
        "weights_restored": "已从备份恢复会话：",
        "backup_not_found": "没有找到备份文件",
        "chat_exported_to": "对话已导出到：",
        "chat_imported": "对话已导入",
        "language_pack_imported": "语言包导入成功",
        "session_created": "已创建新会话：",
        "session_deleted": "已删除会话：",
        "session_renamed": "已将会话重命名为：",
        "personality_set": "已设置",
        "preference_added": "已添加偏好：",
        "you": "你",
        "training": "训练",
        "refine": "精炼训练 (对话式)",
        "full": "完整训练 (逐字)",
        "intensive": "强化训练 (重点)",
        "interactive": "交互式训练 (对齐)",
        "current_instance_count": "当前实例数：",
        "api_key_unassigned": "未分配",
        "api_not_running": "API未启动",
        "token_balance_unlimited": "无限制",
        "model_tokens": "模型Token量：",
        "conversation_count": "对话数：",
        "free": "免费(无限)",
        "paid": "付费",
        "model_version": "模型版本：",
        "network_layers": "网络层数：",
        "learning_streak": "学习连续性：",
        "gradient_history": "梯度历史：",
        "avg_response_score": "平均响应分数：",
        "learned_phrases": "学会短语数：",
        "learned_words": "学会词汇数：",
        "causal_position": "因果位置：",
        "last_backup": "上次备份：",
        "last_save": "上次保存："
    },
    "en": {
        "title": "QianYin - MTG AI V-Causal",
        "chat_window": "Chat Window",
        "send": "Send",
        "clear": "Clear",
        "session_management": "Session Management",
        "new_session": "New Session",
        "switch_session": "Switch Session",
        "rename_session": "Rename Session",
        "delete_session": "Delete Session",
        "model_management": "Model Management",
        "save_model": "Save Model",
        "load_model": "Load Model",
        "view_stats": "View Stats",
        "model_info": "Model Info",
        "personality_settings": "Personality Settings",
        "view_personality": "View Personality",
        "edit_personality": "Edit Personality",
        "preference_settings": "Preference Settings",
        "view_preferences": "View Preferences",
        "add_preference": "Add Preference",
        "chat_management": "Chat Management",
        "export_chat": "Export Chat",
        "import_chat": "Import Chat",
        "api_server": "API Server",
        "weights_management": "Weights Management",
        "set_weights_path": "Set Weights Path",
        "backup_weights": "Backup Weights",
        "restore_weights": "Restore Weights",
        "api_description": "API Description",
        "language_settings": "Language Settings",
        "current_language": "Current Language",
        "switch_chinese": "Switch to Chinese",
        "switch_english": "Switch to English",
        "import_language_pack": "Import Language Pack",
        "language_pack_format": "Language Pack Format",
        "select_weights_dir": "Please select the weights storage directory:",
        "select_directory": "Select Directory",
        "skip": "Skip",
        "success": "Success",
        "warning": "Warning",
        "error": "Error",
        "port": "Port",
        "dimension": "Dimension",
        "layers": "Layers",
        "token_count": "Token Count",
        "learning_data": "Learning Data",
        "cpu": "CPU",
        "memory": "Memory",
        "api_key": "API Key",
        "tokens": "Tokens",
        "token_balance": "Token Balance",
        "token_usage": "Token Usage",
        "server_status": "Server Status",
        "stopped": "Stopped",
        "running": "Running",
        "start_api": "Start API (4000)",
        "stop_api": "Stop API",
        "cisl_interface": "CISL Interface (9000)",
        "no_auth": "No Auth",
        "basic_info": "Basic Info",
        "realtime_status": "Realtime Status",
        "training_mode": "Training Mode",
        "start_training": "Start Training",
        "stop_training": "Stop Training",
        "instance_info": "Instance Info",
        "model_name": "QianYin",
        "model": "QianYin",
        "switched_to_session": "Switched to session: ",
        "session_already_exists": "Session name already exists",
        "session_name_empty": "Session name cannot be empty",
        "cannot_rename_default": "Cannot rename default session",
        "cannot_delete_default": "Cannot delete default session",
        "insufficient_tokens": "Insufficient token balance",
        "chat_cleared": "Chat cleared",
        "training_stopped": "Training stopped",
        "language_switched": "Language switched to ",
        "model_saved_to": "Model saved to: ",
        "model_loaded_to": "Model loaded to session: ",
        "weights_path_set_to": "Weights path set to: ",
        "weights_backed_up_to": "Weights backed up to: ",
        "weights_restored": "Restored session from backup: ",
        "backup_not_found": "Backup file not found",
        "chat_exported_to": "Chat exported to: ",
        "chat_imported": "Chat imported",
        "language_pack_imported": "Language pack imported successfully",
        "session_created": "Created new session: ",
        "session_deleted": "Deleted session: ",
        "session_renamed": "Renamed session to: ",
        "personality_set": "Set ",
        "preference_added": "Added preference: ",
        "you": "You",
        "training": "Training",
        "refine": "Refine Training (Conversational)",
        "full": "Full Training (Token-wise)",
        "intensive": "Intensive Training (Focused)",
        "interactive": "Interactive Training (Alignment)",
        "current_instance_count": "Current instance count: ",
        "api_key_unassigned": "Unassigned",
        "api_not_running": "API not running",
        "token_balance_unlimited": "Unlimited",
        "model_tokens": "Model tokens: ",
        "conversation_count": "Conversation count: ",
        "free": "Free(Unlimited)",
        "paid": "Paid",
        "model_version": "Model version: ",
        "network_layers": "Network layers: ",
        "learning_streak": "Learning streak: ",
        "gradient_history": "Gradient history: ",
        "avg_response_score": "Avg response score: ",
        "learned_phrases": "Learned phrases: ",
        "learned_words": "Learned words: ",
        "causal_position": "Causal position: ",
        "last_backup": "Last backup: ",
        "last_save": "Last save: "
    }
}

current_language = "zh"
language_pack = DEFAULT_LANG["zh"]

def _(key):
    return language_pack.get(key, key)

def log_error(message):
    """记录错误日志"""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"无法写入日志文件: {str(e)}")

def log_exception(exc):
    """记录异常信息"""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        exc_info = traceback.format_exc()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] EXCEPTION: {str(exc)}\n{exc_info}\n")
    except Exception as e:
        print(f"无法写入日志文件: {str(e)}")

def log_performance(message):
    """记录性能指标日志"""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(PERF_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            return json.load(open(CONFIG_FILE, "r", encoding="utf-8"))
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    return {
        "weights_path": SCRIPT_DIR,
        "port": 4000,
        "cjsl_port": 9000,
        "dim": 4096,
        "default_api": "mtgchatgf",
        "language": "zh",
        "current_session": "default",
        "window_geometry": "1400x850",
        "auto_save_train_interval": 10
    }

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存配置文件失败: {str(e)}")

def load_weights_info():
    if os.path.exists(WEIGHTS_INFO_FILE):
        try:
            with open(WEIGHTS_INFO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载权重信息失败: {str(e)}")
    return {
        "instances": {},
        "last_backup": None,
        "last_save": None
    }

def save_weights_info(info):
    try:
        info["last_save"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(WEIGHTS_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存权重信息失败: {str(e)}")

def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载API密钥失败: {str(e)}")
    return {
        "mtgchatgf": {"session_id": "mtgchatgf", "tokens": -1, "is_free": True, "created_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    }

def save_api_keys(api_keys):
    try:
        with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
            json.dump(api_keys, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存API密钥失败: {str(e)}")

def load_language(lang="zh"):
    global current_language, language_pack
    current_language = lang
    if os.path.exists(LANG_FILE):
        try:
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                custom_lang = json.load(f)
                if lang in custom_lang:
                    language_pack = {**DEFAULT_LANG.get(lang, DEFAULT_LANG["zh"]), **custom_lang[lang]}
                else:
                    language_pack = DEFAULT_LANG.get(lang, DEFAULT_LANG["zh"])
        except Exception as e:
            log_error(f"加载语言文件失败: {str(e)}")
            language_pack = DEFAULT_LANG.get(lang, DEFAULT_LANG["zh"])
    else:
        language_pack = DEFAULT_LANG.get(lang, DEFAULT_LANG["zh"])
    config = load_config()
    config["language"] = lang
    save_config(config)
    return language_pack

def save_custom_language(lang_key, lang_data):
    """保存自定义语言包"""
    try:
        custom_lang = {}
        if os.path.exists(LANG_FILE):
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                custom_lang = json.load(f)
        custom_lang[lang_key] = lang_data
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            json.dump(custom_lang, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log_error(f"保存自定义语言失败: {str(e)}")
        return False


class SemanticEncoder:
    """语义编码器 - 支持梯度裁剪"""
    def __init__(self, dim=4096):
        self.dim = dim
        self.word_vec = {}
        self.lr = 0.05
        self.grad_clip = 1.0  # 梯度裁剪阈值

    def encode(self, word):
        if word not in self.word_vec:
            self.word_vec[word] = [random.gauss(0, 0.1) for _ in range(self.dim)]
        return self.word_vec[word]

    def update(self, word, grad):
        """更新词向量，增加梯度裁剪限制单次更新幅度"""
        if word in self.word_vec:
            # 梯度裁剪：限制单次更新幅度
            clipped_grad = max(-self.grad_clip, min(self.grad_clip, grad))
            for i in range(self.dim):
                self.word_vec[word][i] += clipped_grad * self.lr
                self.word_vec[word][i] = max(-1.0, min(1.0, self.word_vec[word][i]))

    def similarity(self, w1, w2):
        v1 = self.encode(w1)
        v2 = self.encode(w2)
        return sum(a * b for a, b in zip(v1, v2))

    def get_state(self):
        return {"word_vec": self.word_vec, "lr": self.lr, "grad_clip": self.grad_clip}


class QKVSerialAttention:
    """QKV串行注意力机制 - 增加权重数值范围限制"""
    def __init__(self, dim=4096):
        self.dim = dim
        self.Wq = [random.gauss(0, 0.1) for _ in range(dim)]
        self.Wk = [random.gauss(0, 0.1) for _ in range(dim)]
        self.Wv = [random.gauss(0, 0.1) for _ in range(dim)]
        self.weight_min = -5.0
        self.weight_max = 5.0

    def score(self, vec):
        q = sum(v * w for v, w in zip(vec, self.Wq))
        k = sum(v * w for v, w in zip(vec, self.Wk))
        v = sum(v * w for v, w in zip(vec, self.Wv))
        return (q * k) / math.sqrt(self.dim)

    def clamp_weights(self):
        """对Wq/Wk/Wv进行数值范围限制 [-5.0, 5.0]"""
        for i in range(self.dim):
            self.Wq[i] = max(self.weight_min, min(self.weight_max, self.Wq[i]))
            self.Wk[i] = max(self.weight_min, min(self.weight_max, self.Wk[i]))
            self.Wv[i] = max(self.weight_min, min(self.weight_max, self.Wv[i]))

    def get_state(self):
        return {"Wq": self.Wq, "Wk": self.Wk, "Wv": self.Wv, "weight_min": self.weight_min, "weight_max": self.weight_max}


def softmax(scores):
    if not scores:
        return []
    max_s = max(scores)
    ex = [math.exp(s - max_s) for s in scores]
    sum_ex = sum(ex)
    return [e / sum_ex for e in ex] if sum_ex != 0 else [0.0] * len(scores)


class UnicodeTokenizer:
    """Unicode分词器 - max_subword_len可配置，默认改为8"""
    def __init__(self, max_subword_len=8):
        self.char_to_token = {}
        self.token_to_char = {}
        self.subword_to_token = {}
        self.token_to_subword = {}
        self._next_token_id = 1
        self._next_subword_id = 1
        self.max_subword_len = max_subword_len

    def _is_cjk(self, char):
        return '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf'

    def _is_latin(self, char):
        return char.isalpha() and ord(char) < 128

    def _is_number(self, char):
        return char.isdigit()

    def _get_token_for_char(self, char):
        if char not in self.char_to_token:
            self.char_to_token[char] = self._next_token_id
            self.token_to_char[self._next_token_id] = char
            self._next_token_id += 1
        return f"c{self.char_to_token[char]}"

    def _try_create_subword(self, text, start, length):
        if length <= 1:
            return None
        subword = text[start:start + length]
        if subword in self.subword_to_token:
            return f"s{self.subword_to_token[subword]}"
        if length <= self.max_subword_len:
            self.subword_to_token[subword] = self._next_subword_id
            self.token_to_subword[self._next_subword_id] = subword
            self._next_subword_id += 1
            return f"s{self.subword_to_token[subword]}"
        return None

    def tokenize(self, text):
        if not text:
            return []
        tokens = []
        i = 0
        while i < len(text):
            matched = False
            for length in range(min(self.max_subword_len, len(text) - i), 1, -1):
                subword_token = self._try_create_subword(text, i, length)
                if subword_token:
                    tokens.append(subword_token)
                    i += length
                    matched = True
                    break
            if not matched:
                tokens.append(self._get_token_for_char(text[i]))
                i += 1
        return tokens

    def decode_tokens(self, token_ids):
        result = []
        for tok in token_ids:
            if tok.startswith('s') and tok[1:].isdigit():
                tid = int(tok[1:])
                if tid in self.token_to_subword:
                    result.append(self.token_to_subword[tid])
            elif tok.startswith('c') and tok[1:].isdigit():
                tid = int(tok[1:])
                if tid in self.token_to_char:
                    result.append(self.token_to_char[tid])
        return ''.join(result)


class PhraseLearner:
    def __init__(self):
        self.phrase_patterns = defaultdict(list)
        self.response_templates = []
        self.max_templates = 50
        self.ngram_sizes = [2, 3, 4, 5]

    def learn_from_text(self, text, response, weight=1.0):
        if not text or not response:
            return
        text = text.strip()
        response = response.strip()
        for n in self.ngram_sizes:
            for i in range(len(text) - n + 1):
                ngram = text[i:i + n]
                key = f"input_{n}gram"
                if ngram not in self.phrase_patterns[key]:
                    self.phrase_patterns[key].append(ngram)
            for i in range(len(response) - n + 1):
                ngram = response[i:i + n]
                key = f"output_{n}gram"
                if ngram not in self.phrase_patterns[key]:
                    self.phrase_patterns[key].append(ngram)
        template = f"{text}|{response}"
        if template not in self.response_templates:
            self.response_templates.append(template)
            if len(self.response_templates) > self.max_templates:
                self.response_templates.pop(0)

    def get_learned_phrases(self, n=3):
        key = f"output_{n}gram"
        return self.phrase_patterns.get(key, [])

    def get_input_patterns(self, n=3):
        key = f"input_{n}gram"
        return self.phrase_patterns.get(key, [])

    def get_state(self):
        return {"phrase_patterns": dict(self.phrase_patterns), "response_templates": self.response_templates}


class PersonalityRewardSystem:
    def __init__(self, personality):
        self.personality = personality
        self.response_scores = []
        self.max_score_history = 50

    def calculate_response_score(self, response, sentiment):
        score = 0.5
        length = len(response)
        if self.personality.get("简洁", 0.5) > 0.6 and length < 20:
            score += 0.1
        if self.personality.get("健谈", 0.5) > 0.6 and length > 30:
            score += 0.1
        if sentiment == "positive" and self.personality.get("乐观", 0.5) > 0.5:
            score += 0.15
        if sentiment == "negative" and self.personality.get("谨慎", 0.5) > 0.5:
            score += 0.1
        if self.personality.get("幽默", 0) > 0.7 and any(c in response for c in "，。"):
            score += 0.1
        if self.personality.get("热情", 0) > 0.7 and length > 15:
            score += 0.1
        return min(1.0, max(0.0, score))

    def apply_reward(self, response, sentiment):
        score = self.calculate_response_score(response, sentiment)
        self.response_scores.append(score)
        if len(self.response_scores) > self.max_score_history:
            self.response_scores.pop(0)
        return score > 0.6

    def get_average_score(self):
        if not self.response_scores:
            return 0.5
        return sum(self.response_scores) / len(self.response_scores)

    def adjust_personality_response(self, base_response, sentiment):
        score = self.calculate_response_score(base_response, sentiment)
        if score < 0.4:
            if self.personality.get("幽默", 0) > 0.5:
                if not any(base_response.endswith(c) for c in "。！？"):
                    base_response += "。"
            if self.personality.get("热情", 0) > 0.6 and len(base_response) < 15:
                base_response = base_response
        elif score > 0.7:
            if self.personality.get("谦虚", 0) > 0.5 and len(base_response) > 40:
                base_response = base_response
        return base_response


class LightweightMultiLayerLLM:
    """轻量多层因果语言模型 - 增强版"""
    def __init__(self, num_layers=24, max_input_len=200, max_states=5000):
        self.num_layers = num_layers
        self.attention_matrices = [defaultdict(lambda: defaultdict(float)) for _ in range(num_layers)]
        self.state_to_text = {}
        self.text_to_state = {}
        self.lru_cache = OrderedDict()
        self.lru_access_counts = defaultdict(int)  # 二.3: LRU语义热度权重 - 访问频率计数
        self.max_states = max_states
        self.context_chain = []
        self.max_context_len = 32
        self.learning_rate = 0.1
        self.layer_dropout = 0.15
        self.base_vocab = []
        self.learned_vocab = []
        self.max_vocab_size = 500
        self.max_input_len = max_input_len
        self.user_preferences = {}
        self.self_understanding = {}
        self.improvement_goals = []
        self.user_understanding = {}
        self.semantic = SemanticEncoder(dim=4096)
        self.qkv_layers = [QKVSerialAttention(4096) for _ in range(num_layers)]
        self.causal_position = 0
        self.weight_decay = 0.988
        self.punishment_rate = 0.05
        self.tokenizer = UnicodeTokenizer(max_subword_len=8)
        self.phrase_learner = PhraseLearner()

        self.personality = {
            "友善": 0.8,
            "好奇": 0.7,
            "耐心": 0.9,
            "幽默": 0.3,
            "谦虚": 0.7,
            "热情": 0.5,
            "谨慎": 0.6,
            "乐观": 0.7,
            "简洁": 0.5,
            "健谈": 0.5
        }
        self.preferences = {
            "喜欢的话题": [],
            "偏好的回应风格": "自然",
            "喜欢的词汇": [],
            "厌恶的话题": []
        }
        self.conversation_style = "自然"
        self.personality_reward = PersonalityRewardSystem(self.personality)

        self.adaptive_lr = True
        self.learning_momentum = 0.9
        self.gradient_history = defaultdict(float)
        self.consecutive_correct = 0
        self.learning_streak = 0
        self.model_name = "千因"
        self.model_version = "1.0"
        self.total_tokens_processed = 0
        self.total_conversations = 0

        # 四.5: 权重读写互斥锁
        self._rw_lock = threading.RLock()

        # 训练计数器（用于分段自动快照）
        self._train_count = 0
        self.auto_save_train_interval = 10

        # 定时清理闲置state计数器
        self._access_since_cleanup = 0
        self._cleanup_interval = 1000

        # 定时快照间隔（秒），默认3600秒（1小时）
        self._snapshot_interval = 3600
        self._last_snapshot_time = time.time()

        # 功能开关
        self._features = {
            "auto_full_save": True,       # 自动全量模型保存（每次对话/训练后）
            "auto_compress": True,         # 自动压缩（LZ4）
        }

        self.dynamic_params = {
            "max_input_len": 200,
            "max_output_tokens": 200,
            "num_layers": 24,
            "dim": 4096,
            "learning_rate": 0.1,
            "temperature": 0.8,
            "top_k": 3,
            "top_p": 0.9
        }

        self._pretrain_model()

    def _pretrain_model(self):
        """千因模型预训练 - 仅训练注意力权重"""
        pretrain_pairs = [
            ("你好", "问候"),
            ("你是谁", "身份"),
            ("你能做什么", "能力"),
            ("今天天气怎么样", "天气"),
            ("谢谢", "感谢"),
            ("再见", "告别"),
            ("你会学习吗", "学习"),
            ("你好呀", "问候")
        ]
        for input_text, output_text in pretrain_pairs:
            start_state = self.token_to_state(input_text)
            output_state = self.token_to_state(output_text)
            for layer_idx in range(self.num_layers):
                layer_matrix = self.attention_matrices[layer_idx]
                if start_state not in layer_matrix:
                    layer_matrix[start_state] = defaultdict(float)
                layer_matrix[start_state][output_state] += 0.1
                total = sum(layer_matrix[start_state].values()) + 1e-6
                for k in layer_matrix[start_state]:
                    layer_matrix[start_state][k] /= total


    def _normalize_text(self, text):
        """2.26: 轻量文本归一化 - 仅去首尾标点和连续重复标点，保留中间标点的语义信息"""
        if not text:
            return ""
        # 中英文标点字符集
        punct = '，。！？、；：""''（）【】《》〈〉「」『』…—,.!?;:\'"()[]<>{}~`@#$%^&*+=|\\/·•・'
        # 1. 去除多余空白（多个空白合并为一个）
        text = re.sub(r'\s+', ' ', text).strip()
        # 2. 连续重复标点压缩为单个（如 。。。→。 ！！！→！）
        text = re.sub(r'([，。！？、；：,.!?;:…—·•・])\1+', r'\1', text)
        # 3. 仅去除首尾标点（让"你好，"和"你好"匹配，但保留文本中间的标点）
        text = text.strip(punct + ' ')
        return text

    def _char_ngram_similarity(self, text1, text2, n_sizes=(2, 3)):
        """2.26: 基于字符n-gram的Jaccard相似度 - 不依赖随机向量，稳定可靠"""
        if not text1 or not text2:
            # 都为空视为相同
            return 1.0 if text1 == text2 else 0.0
        # 先做归一化
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)
        if not norm1 or not norm2:
            return 1.0 if norm1 == norm2 else 0.0
        # 如果归一化后完全相同
        if norm1 == norm2:
            return 1.0
        # 短文本（<=3字符）直接用子串包含判断
        if len(norm1) <= 3 or len(norm2) <= 3:
            if norm1 in norm2 or norm2 in norm1:
                return 0.85
        set1 = set()
        set2 = set()
        for n in n_sizes:
            for i in range(len(norm1) - n + 1):
                set1.add(norm1[i:i + n])
            for i in range(len(norm2) - n + 1):
                set2.add(norm2[i:i + n])
        if not set1 or not set2:
            return 0.0
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union) if union else 0.0

    def _has_out_edges(self, state_id):
        """2.26: 检查某state是否在任一注意力层中有出边"""
        for layer_idx in range(self.num_layers):
            layer_matrix = self.attention_matrices[layer_idx]
            if state_id in layer_matrix and len(layer_matrix[state_id]) > 0:
                # 检查是否有非零权重的边
                for target_state, weight in layer_matrix[state_id].items():
                    if weight >= 0.01:
                        return True
        return False

    def _fuzzy_match(self, user_input, top_k=3, threshold=0.15):
        """2.26: 改进模糊匹配 - 使用字符n-gram相似度替代随机向量点积"""
        if not self.state_to_text:
            return []
        norm_input = self._normalize_text(user_input)
        if not norm_input:
            return []
        candidates = []
        for state_id, text in self.state_to_text.items():
            score = self._char_ngram_similarity(user_input, text)
            if score >= threshold:
                candidates.append((state_id, text, score))
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates[:top_k]

    def _probabilistic_fuzzy_transition(self, current_state, layer_idx, layer_matrix):
        """概率化模糊跳转 - 以一定概率选择相似state"""
        if random.random() < 0.3 and len(self.state_to_text) > 5:
            fuzzy_candidates = self._fuzzy_match(
                self.state_to_text.get(current_state, ""), top_k=3, threshold=0.2
            )
            for state_id, text, score in fuzzy_candidates:
                if state_id != current_state and state_id in layer_matrix:
                    current_weight = layer_matrix[current_state][state_id]
                    if random.random() < min(current_weight * 2, 0.5):
                        return state_id
        return None

    def _lru_access(self, state_id):
        """LRU缓存访问 - 增加语义热度权重（访问频率）"""
        if state_id in self.lru_cache:
            self.lru_cache.move_to_end(state_id)
        else:
            if len(self.lru_cache) >= self.max_states:
                # 淘汰时优先淘汰低频+低热度的state
                self._evict_lru_with_heat()
            self.lru_cache[state_id] = True
        # 记录访问频率
        self.lru_access_counts[state_id] += 1

    def _evict_lru_with_heat(self):
        """基于语义热度权重的LRU淘汰 - 优先淘汰低频+低热度的state"""
        if not self.lru_cache:
            return
        # 在最旧的1/4中找访问频率最低的进行淘汰
        items = list(self.lru_cache.items())
        candidates = items[:max(1, len(items) // 4)]
        min_count = float('inf')
        min_key = None
        for key, _ in candidates:
            count = self.lru_access_counts.get(key, 0)
            if count < min_count:
                min_count = count
                min_key = key
        if min_key:
            self.lru_cache.pop(min_key, None)
            self.lru_access_counts.pop(min_key, None)
        else:
            self.lru_cache.popitem(last=False)

    def _cleanup_idle_states(self):
        """定时清理闲置state机制 - 清理最久未访问的state，保留最近max_states个"""
        if len(self.lru_cache) <= self.max_states:
            return
        # 清理超出max_states的部分
        while len(self.lru_cache) > self.max_states:
            self._evict_lru_with_heat()
        # 清理lru_access_counts中不属于lru_cache的条目
        stale_keys = [k for k in self.lru_access_counts if k not in self.lru_cache]
        for k in stale_keys:
            del self.lru_access_counts[k]

    def _detect_script(self, text):
        scripts = {"cjk": 0, "latin": 0, "number": 0, "other": 0}
        for char in text:
            if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf':
                scripts["cjk"] += 1
            elif char.isalpha() and char.isascii():
                scripts["latin"] += 1
            elif char.isdigit():
                scripts["number"] += 1
            else:
                scripts["other"] += 1
        return max(scripts, key=scripts.get)

    def token_to_state(self, text):
        """确定性 state_id 生成 - 相同文本始终生成相同 state_id，确保权重可复用"""
        if text is None:
            text = ""
        if len(text) > self.max_input_len:
            text = text[:self.max_input_len]
        text = text.strip()
        tokens = self.tokenizer.tokenize(text)
        script_type = self._detect_script(text)
        core_tokens = tokens[:5]
        sem = self.semantic.encode(' '.join(core_tokens))

        # 确定性hash：只用文本+脚本类型，不加时间戳和随机数
        raw_data = f"{text}|{script_type}"
        state_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()[:24]
        state_id = f"state_{state_hash}"

        # 如果已存在直接返回（幂等）
        if state_id in self.state_to_text:
            self._lru_access(state_id)
            self._access_since_cleanup += 1
            if self._access_since_cleanup >= self._cleanup_interval:
                self._access_since_cleanup = 0
                self._cleanup_idle_states()
            return state_id

        # 冲突检测（理论上极低概率，用计数器而非随机）
        collision_max = 10
        for attempt in range(1, collision_max + 1):
            if state_id not in self.state_to_text:
                break
            raw_data = f"{text}|{script_type}|{attempt}"
            state_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()[:24]
            state_id = f"state_{state_hash}"

        self.text_to_state[text] = state_id
        self.state_to_text[state_id] = text
        if len(self.learned_vocab) < self.max_vocab_size:
            for word in core_tokens:
                if word.startswith('s') and word not in self.learned_vocab:
                    decoded = self.tokenizer.token_to_subword.get(int(word[1:]), word)
                    if decoded not in self.learned_vocab:
                        self.learned_vocab.append(decoded)
        self._lru_access(state_id)

        self._access_since_cleanup += 1
        if self._access_since_cleanup >= self._cleanup_interval:
            self._access_since_cleanup = 0
            self._cleanup_idle_states()

        return state_id

    def multi_layer_inference(self, start_state, context_states):
        """多层推理 - 返回reasoning_path和layer_scores，每层跳转设置最低score阈值"""
        reasoning_path = []
        layer_scores = []  # 三.1: 每层得分信息
        current_state = start_state
        reasoning_path.append(current_state)
        self.causal_position = 0
        self._lru_access(current_state)
        min_score_threshold = 0.01  # 一.4: 最低置信度阈值

        context_semantics = []
        for ctx in context_states:
            if ctx in self.state_to_text:
                text = self.state_to_text[ctx]
                vec = self.semantic.encode(text)
                context_semantics.append((ctx, text, vec))

        visited_states = set()
        visited_count = defaultdict(int)
        max_revisits = 2  # 每个状态最多被访问2次

        for layer_idx in range(self.num_layers):
            self.causal_position += 1
            layer_start_time = time.time()
            if random.random() < self.layer_dropout:
                layer_scores.append({"layer": layer_idx, "score": 0.0, "action": "dropout"})
                continue
            layer_matrix = self.attention_matrices[layer_idx]

            current_text = self.state_to_text.get(current_state, "")
            current_vec = self.semantic.encode(current_text)

            attn_scores = []
            for ctx, ctx_text, ctx_vec in context_semantics:
                qkv = self.qkv_layers[layer_idx]
                score = qkv.score(ctx_vec)
                sim = self.semantic.similarity(current_text, ctx_text)
                attn_scores.append(score + sim * 0.1)

            attn_weights = softmax(attn_scores) if attn_scores else []

            best_ctx = None
            best_score = -1.0
            for i, (ctx, ctx_text, ctx_vec) in enumerate(context_semantics):
                if i < len(attn_weights):
                    weight = attn_weights[i]
                    if weight > best_score and ctx in layer_matrix.get(current_state, {}):
                        best_score = weight
                        best_ctx = ctx

            if best_ctx is not None and current_state in layer_matrix:
                transitions = sorted(layer_matrix[current_state].items(), key=lambda x: x[1], reverse=True)
                # 一.4: 最低置信过滤 - 低于阈值自动选取次优状态
                valid_transitions = [(s, w) for s, w in transitions if w >= min_score_threshold]
                if valid_transitions:
                    # 温度采样：top-k + softmax 采样
                    top_k = min(len(valid_transitions), 3)
                    candidates = valid_transitions[:top_k]
                    weights = [max(w, 0.01) for _, w in candidates]
                    total_w = sum(weights)
                    probs = [w / total_w for w in weights]
                    # 应用温度：温度越高分布越均匀
                    temperature = 0.8
                    probs_t = [p ** (1.0 / temperature) for p in probs]
                    total_pt = sum(probs_t)
                    probs_t = [p / total_pt for p in probs_t]
                    r = random.random()
                    cumul = 0.0
                    next_state = candidates[0][0]
                    for (s, _), p in zip(candidates, probs_t):
                        cumul += p
                        if r <= cumul:
                            next_state = s
                            break
                    reasoning_path.append(next_state)
                    visited_states.add(next_state)
                    visited_count[next_state] += 1
                    # 终态检测：已访问过的状态不再继续
                    if visited_count[next_state] > max_revisits:
                        layer_scores.append({"layer": layer_idx, "score": 0.0, "action": "terminated_revisit"})
                        break
                    self._lru_access(next_state)
                    current_state = next_state
                    layer_scores.append({"layer": layer_idx, "score": valid_transitions[0][1], "action": "transition"})
                    layer_time = time.time() - layer_start_time
                    log_performance(f"推理层{layer_idx}: 耗时={layer_time:.4f}s, 得分={valid_transitions[0][1]:.4f}")
                    continue
                else:
                    # 没有满足阈值的状态，保留当前状态不跳转
                    layer_scores.append({"layer": layer_idx, "score": best_score, "action": "below_threshold_terminate"})
                    layer_time = time.time() - layer_start_time
                    log_performance(f"推理层{layer_idx}: 低于阈值终止, 耗时={layer_time:.4f}s")
                    break  # 无法继续有效跳转，终止推理

            if current_state not in layer_matrix or len(layer_matrix.get(current_state, {})) == 0:
                # 2.26: 无出边时 - 优先从上下文中选最相似的状态，再用模糊匹配兜底
                layer_scores.append({"layer": layer_idx, "score": 0.0, "action": "no_out_edges_fuzzy"})
                found_next = False
                if context_semantics:
                    best_ctx_state, best_ctx_text, best_ctx_vec = max(
                        context_semantics,
                        key=lambda x: self._char_ngram_similarity(current_text, x[1])
                    )
                    if best_ctx_state != current_state and best_ctx_state in self.state_to_text:
                        reasoning_path.append(best_ctx_state)
                        visited_states.add(best_ctx_state)
                        visited_count[best_ctx_state] += 1
                        if visited_count[best_ctx_state] > max_revisits:
                            layer_scores.append({"layer": layer_idx, "score": 0.0, "action": "terminated_revisit"})
                            break
                        self._lru_access(best_ctx_state)
                        current_state = best_ctx_state
                        found_next = True
                # 2.26: 上下文也没找到时，用模糊匹配找有出边的相似 state
                if not found_next and len(self.state_to_text) > 1:
                    fuzzy_candidates = self._fuzzy_match(current_text, top_k=5, threshold=0.2)
                    for state_id, text, score in fuzzy_candidates:
                        if state_id != current_state and self._has_out_edges(state_id):
                            reasoning_path.append(state_id)
                            visited_states.add(state_id)
                            visited_count[state_id] += 1
                            if visited_count[state_id] > max_revisits:
                                break
                            self._lru_access(state_id)
                            current_state = state_id
                            found_next = True
                            break
                if not found_next:
                    # 如果连模糊匹配都没有，保留当前状态不跳转
                    layer_time = time.time() - layer_start_time
                    log_performance(f"推理层{layer_idx}: 无出边终止, 耗时={layer_time:.4f}s")
                    break  # 终止推理，不再继续
            else:
                transitions = sorted(layer_matrix[current_state].items(), key=lambda x: x[1], reverse=True)
                # 一.4: 同样应用最低置信过滤
                valid_transitions = [(s, w) for s, w in transitions if w >= min_score_threshold]
                if valid_transitions:
                    # 温度采样：top-k + softmax 采样
                    top_k = min(len(valid_transitions), 3)
                    candidates = valid_transitions[:top_k]
                    weights = [max(w, 0.01) for _, w in candidates]
                    total_w = sum(weights)
                    probs = [w / total_w for w in weights]
                    # 应用温度：温度越高分布越均匀
                    temperature = 0.8
                    probs_t = [p ** (1.0 / temperature) for p in probs]
                    total_pt = sum(probs_t)
                    probs_t = [p / total_pt for p in probs_t]
                    r = random.random()
                    cumul = 0.0
                    next_state = candidates[0][0]
                    for (s, _), p in zip(candidates, probs_t):
                        cumul += p
                        if r <= cumul:
                            next_state = s
                            break
                    reasoning_path.append(next_state)
                    visited_states.add(next_state)
                    visited_count[next_state] += 1
                    # 终态检测：已访问过的状态不再继续
                    if visited_count[next_state] > max_revisits:
                        layer_scores.append({"layer": layer_idx, "score": 0.0, "action": "terminated_revisit"})
                        break
                    self._lru_access(next_state)
                    current_state = next_state
                    layer_scores.append({"layer": layer_idx, "score": valid_transitions[0][1], "action": "transition"})
                else:
                    # 没有满足阈值的状态，保留当前状态不跳转
                    layer_scores.append({"layer": layer_idx, "score": transitions[0][1] if transitions else 0.0, "action": "below_threshold_hold"})
            layer_time = time.time() - layer_start_time
            log_performance(f"推理层{layer_idx}: 耗时={layer_time:.4f}s")
        return reasoning_path, layer_scores

    def _detect_user_sentiment(self, user_input):
        """增强的情感识别 - 增加否定词检测、标点情感分析、情感强度计算"""
        positive_indicators = ["好", "棒", "喜欢", "谢谢", "开心", "高兴", "不错", "完美", "赞",
                               "good", "great", "thanks", "nice", "love", "happy", "excellent"]
        negative_indicators = ["讨厌", "差", "糟糕", "麻烦", "问题", "困难", "坏", "错",
                               "bad", "hate", "terrible", "awful", "wrong", "issue", "sad"]
        # 否定词列表
        negation_words = ["不", "没", "不是", "不要", "别", "无", "未", "非",
                          "not", "no", "don't", "doesn't", "can't", "won't", "never"]
        # 情感强度词
        intensity_words = ["很", "非常", "特别", "太", "超级", "真的", "极其", "十分",
                           "very", "really", "extremely", "so", "too", "absolutely"]

        score = 0.0
        lower_input = user_input.lower()

        # 基础情感词匹配
        for word in positive_indicators:
            if word in user_input or word in lower_input:
                score += 1
        for word in negative_indicators:
            if word in user_input or word in lower_input:
                score -= 1

        # 否定词+正面词 组合（表示负面含义）
        negative_combo_patterns = [
            "不好", "不行", "不对", "不棒", "不喜欢", "不开", "不高",
            "不赞", "不是好", "不是很好", "不是太好", "不是特别好",
            "不太行", "不太", "不太好", "不太喜欢",
            "没好", "没棒", "没有好", "没喜欢",
            "not good", "not great", "not nice", "no good", "don't like"
        ]
        # 否定词+负面词 组合（表示正面含义，如"不错""没差"）
        positive_combo_patterns = [
            "不错", "不差", "不坏", "不讨厌", "不糟糕", "没差", "没坏", "没麻烦",
            "not bad", "not terrible", "no problem"
        ]

        # 检查正面组合（否定词+负面词=正面）
        for pattern in positive_combo_patterns:
            if pattern in user_input or pattern in lower_input:
                score += 2

        # 检查负面组合（否定词+正面词=负面）
        for pattern in negative_combo_patterns:
            if pattern in user_input or pattern in lower_input:
                score -= 2

        # 情感强度计算
        intensity_multiplier = 1.0
        for int_word in intensity_words:
            if int_word in user_input or int_word in lower_input:
                intensity_multiplier += 0.5
        score *= min(intensity_multiplier, 3.0)

        # 标点情感分析
        # 感叹号增强情感
        excl_count = user_input.count('!') + user_input.count('！')
        if excl_count > 0:
            score *= (1.0 + 0.2 * excl_count)
        # 问号略增加负面
        question_count = user_input.count('?') + user_input.count('？')
        if question_count > 0:
            score -= 0.1 * question_count
        # 连续标点（如"!!!"或"???"）增强
        for punct_pattern in re.finditer(r'[！!]{2,}', user_input):
            score *= 1.3
        for punct_pattern in re.finditer(r'[？?]{2,}', user_input):
            score -= 0.2

        if score > 0:
            return "positive"
        elif score < 0:
            return "negative"
        return "neutral"

    def _clean_response(self, text):
        """输出自动清洗模块 - 过滤重复短句、乱码token、无效符号"""
        if not text:
            return text
        # 过滤非打印字符（乱码token）
        cleaned = ''.join(c for c in text if c.isprintable() or c in '\n\r\t')
        # 过滤重复短句（连续3个以上相同短句）
        sentences = re.split(r'[。！？；；\n]', cleaned)
        filtered_sentences = []
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if not sent:
                continue
            # 检查是否连续重复
            is_repeat = False
            if len(filtered_sentences) >= 2:
                if (filtered_sentences[-1] == sent and filtered_sentences[-2] == sent):
                    is_repeat = True
            if not is_repeat:
                filtered_sentences.append(sent)
        # 过滤无效符号（去除连续的无效标点）
        result = '。'.join(filtered_sentences)
        result = re.sub(r'[，,]{3,}', '，', result)
        result = re.sub(r'[。.]{3,}', '。', result)
        result = re.sub(r'[！!]{3,}', '！', result)
        result = re.sub(r'[？?]{3,}', '？', result)
        # 去除首尾空白
        result = result.strip()
        return result

    def decode_response(self, reasoning_path, user_input, sentiment, max_output_tokens=200):
        """解码响应 - 优先取推理路径中第一个有效回复状态，fallback 时语义组合"""
        if not reasoning_path:
            return ""
        
        # 只取推理路径中第一个非输入的有效状态文本作为回复
        # 这样不会把后续跳转到的其他已训练回复拼接进来
        input_state_id = self.token_to_state(user_input) if user_input else None
        response_text = ""
        for s in reasoning_path:
            if s in self.state_to_text:
                text = self.state_to_text[s]
                # 跳过输入本身和过短的文本
                if s == input_state_id:
                    continue
                if len(text.strip()) >= 2:
                    response_text = text
                    break  # 只取第一个有效回复状态
        
        if response_text:
            # 直接使用匹配到的回复文本，走 personality 调整和截断
            response = self.personality_reward.adjust_personality_response(response_text, sentiment)
            if max_output_tokens > 0 and len(response) > max_output_tokens:
                response = response[:max_output_tokens]
                last_punct = max(response.rfind('。'), response.rfind('！'), response.rfind('？'),
                                 response.rfind('.'), response.rfind('!'), response.rfind('?'))
                if last_punct > 0:
                    response = response[:last_punct + 1]
            response = self._clean_response(response)
            return response
        
        # 如果路径中没找到有效回复，fallback 到语义组合
        tokens = [self.state_to_text[s] for s in reasoning_path if s in self.state_to_text]
        if not tokens:
            return ""

        user_words = set(user_input.split())
        filtered_tokens = [t for t in tokens if t.strip() and t not in user_words and len(t.strip()) > 0]
        if not filtered_tokens:
            filtered_tokens = [t for t in tokens if t.strip()]
        if not filtered_tokens:
            return ""

        # 路径过短（<=2个token）时，从已有知识中语义组合创造性回复
        if len(filtered_tokens) <= 2 and len(self.state_to_text) > 5:
            input_vec = self.semantic.encode(user_input)
            path_texts = set()
            for s in reasoning_path:
                if s in self.state_to_text:
                    path_texts.add(self.state_to_text[s])
            candidates = []
            for state_id, text in self.state_to_text.items():
                if text.strip() and len(text.strip()) >= 2 and text not in user_words and text not in path_texts:
                    text_vec = self.semantic.encode(text)
                    sim = self.semantic.similarity(user_input, text)
                    candidates.append((sim, text))
            candidates.sort(reverse=True)
            if candidates and candidates[0][0] > 0.1:
                # 取 top-3 候选组合
                top_texts = [c[1] for c in candidates[:3] if c[0] > 0.05]
                if top_texts:
                    response = top_texts[0]
                    if len(top_texts) > 1:
                        connectors = ["，", "而且", "同时", "另外"]
                        for t in top_texts[1:]:
                            if len(response) + len(t) < max_output_tokens:
                                response += random.choice(connectors) + t
                    response = self.personality_reward.adjust_personality_response(response, sentiment)
                    if max_output_tokens > 0 and len(response) > max_output_tokens:
                        response = response[:max_output_tokens]
                    response = self._clean_response(response)
                    return response

        # 正常路径：从推理路径构建连贯回复
        response = self._build_coherent_response(filtered_tokens, sentiment)
        
        # phrase_learner 仅在推理路径产出过短时作为补充
        if len(response) < 4:
            learned_phrases = self.phrase_learner.get_learned_phrases(3)
            learned_phrases = [p for p in learned_phrases if len(p.strip()) >= 5]
            if learned_phrases and random.random() < 0.15:
                scored_phrases = []
                for phrase in learned_phrases[:30]:
                    relevance = sum(1 for w in user_words if w in phrase)
                    length_bonus = min(len(phrase) / 20.0, 1.0)
                    scored_phrases.append((relevance + length_bonus, phrase))
                scored_phrases.sort(reverse=True)
                if scored_phrases:
                    response = scored_phrases[0][1]

        response = self.personality_reward.adjust_personality_response(response, sentiment)

        if max_output_tokens > 0 and len(response) > max_output_tokens:
            response = response[:max_output_tokens]
            last_punct = max(response.rfind('。'), response.rfind('！'), response.rfind('？'),
                             response.rfind('.'), response.rfind('!'), response.rfind('?'))
            if last_punct > 0:
                response = response[:last_punct + 1]

        response = self._clean_response(response)
        return response

    def _is_response_relevant(self, response, user_input):
        if not response or not user_input:
            return False
        user_words = set(user_input.lower().split())
        response_words = set(response.lower().split())
        common_words = user_words.intersection(response_words)
        if common_words:
            return True
        for word in user_words:
            if len(word) > 1 and word in response.lower():
                return True
        return False

    def _generate_relevant_response(self, user_input, sentiment):
        keywords = [word for word in user_input.split() if len(word) > 1]
        if not keywords:
            return ""
        keyword = random.choice(keywords)
        return keyword

    def _build_coherent_response(self, tokens, sentiment):
        if len(tokens) <= 3:
            return ''.join(tokens) if tokens else ""
        words = []
        for t in tokens:
            if len(t) > 1:
                words.append(t)
            elif t in "的了是在有和":
                words.append(t)
        if len(words) >= 5:
            response = words[0] + words[1]
            for i in range(2, min(len(words), 6)):
                if random.random() > 0.2:
                    response += words[i]
            if not any(response.endswith(c) for c in "。！？.!?") and len(response) > 5:
                response += "。"
        elif len(words) >= 2:
            connectors = ["，", "然后", "而且", "所以", "不过", "但是"]
            response = words[0]
            for w in words[1:4]:
                response += random.choice(connectors) + w
            if not any(response[-1] in c for c in "。！？.!?"):
                response += "。"
        else:
            response = ''.join(words[:3]) if words else ""
        return response

    def punish(self):
        """全局衰减所有权重 - 仅在train()中手动调用"""
        for layer in self.attention_matrices:
            for s in layer:
                for n in layer[s]:
                    layer[s][n] *= self.weight_decay
                    layer[s][n] -= self.punishment_rate
                    if layer[s][n] < 0.01:
                        layer[s][n] = 0.01

    def update_weights(self, reasoning_path, user_input, response, lr_scale=1.0):
        """更新权重 - lr_scale 控制更新强度"""
        limited_path = [s for s in reasoning_path if s in self.state_to_text]
        if len(limited_path) < 2:
            return
        sentiment = self._detect_user_sentiment(user_input)
        is_good = self.personality_reward.apply_reward(response, sentiment)
        lr_multiplier = 1.0
        if is_good:
            lr_multiplier = 1.5
            self.consecutive_correct += 1
            self.learning_streak += 1
        else:
            self.consecutive_correct = 0
            self.learning_streak = max(0, self.learning_streak - 1)
        if self.consecutive_correct > 3:
            lr_multiplier = 1.2  # 连续正确不降学习率
        if self.adaptive_lr:
            for key in self.gradient_history:
                self.gradient_history[key] *= self.learning_momentum
        for layer_idx in range(self.num_layers):
            layer_matrix = self.attention_matrices[layer_idx]
            for i in range(len(limited_path) - 1):
                s_from = limited_path[i]
                s_to = limited_path[i + 1]
                grad_key = f"{layer_idx}_{s_from}_{s_to}"
                if s_from not in layer_matrix:
                    layer_matrix[s_from] = defaultdict(float)
                # 新建边给予更高初始权重
                if s_to not in layer_matrix[s_from] or layer_matrix[s_from][s_to] < 0.05:
                    layer_matrix[s_from][s_to] = 0.15  # 新边初始权重从0.15开始而非0.01
                wd = self.weight_decay
                for k in layer_matrix[s_from]:
                    layer_matrix[s_from][k] *= wd
                adjusted_lr = self.learning_rate * lr_multiplier * lr_scale
                layer_matrix[s_from][s_to] += adjusted_lr
                total = sum(layer_matrix[s_from].values()) + 1e-6
                for k in layer_matrix[s_from]:
                    layer_matrix[s_from][k] /= total
                w1 = self.state_to_text.get(s_from, "")
                w2 = self.state_to_text.get(s_to, "")
                if w1 and w2:
                    sim = self.semantic.similarity(w1, w2)
                    grad = 0.01 - sim
                    if self.adaptive_lr:
                        self.gradient_history[grad_key] += grad
                        grad *= (1 + 0.1 * self.gradient_history[grad_key])
                    self.semantic.update(w1, grad)
                    self.semantic.update(w2, grad)

    def train(self, user_input, response, mode="refine"):
        """训练 - 直接建立 input→response 映射 + 沿推理路径微调"""
        with self._rw_lock:
            sentiment = self._detect_user_sentiment(user_input)
            start_state = self.token_to_state(user_input)
            response_state = self.token_to_state(response)
            context_states = []
            for item in self.context_chain[-10:]:
                s = self.token_to_state(item["input"])
                if s in self.state_to_text:
                    context_states.append(s)

            # === 核心：直接建立 input→response 的 desired_path ===
            desired_path = [start_state, response_state]
            
            # 沿 desired_path 高权重强化（learning_rate × 5）
            for layer_idx in range(self.num_layers):
                layer_matrix = self.attention_matrices[layer_idx]
                if start_state not in layer_matrix:
                    layer_matrix[start_state] = defaultdict(float)
                # 直接建立强映射
                layer_matrix[start_state][response_state] += self.learning_rate * 5.0
                total = sum(layer_matrix[start_state].values()) + 1e-6
                for k in layer_matrix[start_state]:
                    layer_matrix[start_state][k] /= total

            # 也沿推理路径微调（低权重，不压制 desired_path）
            reasoning_path, layer_scores = self.multi_layer_inference(start_state, context_states)
            
            if mode == "full":
                self.phrase_learner.learn_from_text(user_input, response)
                self.update_weights(reasoning_path, user_input, response, lr_scale=0.3)
            elif mode == "intensive":
                self.phrase_learner.learn_from_text(user_input, response)
                self.update_weights(reasoning_path, user_input, response, lr_scale=0.3)
                key_phrases = self._extract_key_phrases(user_input)
                for phrase in key_phrases:
                    self.phrase_learner.learn_from_text(phrase, response, weight=2.0)
                    phrase_state = self.token_to_state(phrase)
                    for layer_idx in range(self.num_layers):
                        layer_matrix = self.attention_matrices[layer_idx]
                        if phrase_state not in layer_matrix:
                            layer_matrix[phrase_state] = defaultdict(float)
                        layer_matrix[phrase_state][response_state] += self.learning_rate * 3.0
                        total = sum(layer_matrix[phrase_state].values()) + 1e-6
                        for k in layer_matrix[phrase_state]:
                            layer_matrix[phrase_state][k] /= total
            elif mode == "interactive":
                self.phrase_learner.learn_from_text(user_input, response)
                self.update_weights(reasoning_path, user_input, response, lr_scale=0.3)
                input_tokens = self.tokenizer.tokenize(user_input)
                output_tokens = self.tokenizer.tokenize(response)
                for i, input_token in enumerate(input_tokens):
                    if i < len(output_tokens):
                        output_token = output_tokens[i]
                        input_vec = self.semantic.encode(input_token)
                        output_vec = self.semantic.encode(output_token)
                        sim = self.semantic.similarity(input_token, output_token)
                        grad = 0.05 - sim
                        self.semantic.update(input_token, grad)
                        self.semantic.update(output_token, grad)
            else:  # standard / refine
                key_phrases = self._extract_key_phrases(user_input)
                for phrase in key_phrases:
                    self.phrase_learner.learn_from_text(phrase, response)
                self.update_weights(reasoning_path, user_input, response, lr_scale=0.3)

            self.punish()

            for qkv_layer in self.qkv_layers:
                qkv_layer.clamp_weights()

            self.context_chain.append({"input": user_input, "state": start_state, "response": response})
            if len(self.context_chain) > self.max_context_len:
                self.context_chain.pop(0)

            self._train_count += 1
            if self._train_count >= self.auto_save_train_interval:
                self._train_count = 0
                try:
                    self.save_snapshot()
                    log_performance(f"训练分段自动快照已保存, 累计训练样本={self.auto_save_train_interval}")
                except Exception as e:
                    log_error(f"训练分段自动快照保存失败: {str(e)}")

            self._auto_full_save()

            return {"status": "success", "mode": mode, "input_tokens": len(self.tokenizer.tokenize(user_input)),
                    "output_tokens": len(self.tokenizer.tokenize(response))}

    def human_feedback(self, user_input, ai_response, rating, corrected_response=None):
        """人类反馈训练接口 - 5档评分体系，根据评分对模型进行强化或惩罚训练

        评分体系（rating参数）：
          1. 极致优质回答（事实全对+逻辑完整+论据充足）：+4 ~ +5（顶格正向奖励）
          2. 基础合格回答（答案正确、逻辑简略，无错误）：+1 ~ +3（基础正向分）
          3. 半对半错/模棱两可（部分正确、关键逻辑缺失/一半编造）：-4 ~ -6（中等重罚）
          4. 全盘错误/恶意编造事实（无一处正确、捏造数据）：-7 ~ -10（最高惩罚）
          5. 诚实坦白未知（明确说明无知识、无法作答）：0 ~ -2（极轻惩罚）

        支持的rating格式：
          - 预设选项字符串："极致优质"/"基础合格"/"半对半错"/"全盘错误"/"诚实未知"
          - 自定义数值：任意浮点数，如 3.5、-2.5、+4.8 等
          - 兼容旧格式："positive"/"negative"/"neutral"/"good"/"bad" 等

        Args:
            user_input: 原始用户输入
            ai_response: AI生成的回复
            rating: 人类评分（预设选项字符串 或 自定义数值）
            corrected_response: 可选，人类修正后的正确回复（负面反馈时用于纠正训练）
        Returns:
            dict: 反馈训练结果，含 score/feedback_type/level/detail
        """
        with self._rw_lock:
            # ========== 第一阶段：评分标准化 ==========
            score = None
            rating_str = str(rating).strip()

            # 预设选项 → 分数中值
            preset_map = {
                # 第一档：极致优质
                "极致优质": 4.5, "excellent": 4.5, "perfect": 5.0, "outstanding": 5.0, "顶格": 4.5,
                # 第二档：基础合格
                "基础合格": 2.0, "good": 2.0, "合格": 2.0, "pass": 2.0, "ok": 2.0, "positive": 2.0, "好": 2.0, "赞": 2.0, "like": 2.0, "up": 2.0, "great": 3.0,
                # 第三档：半对半错
                "半对半错": -5.0, "half_wrong": -5.0, "模棱两可": -5.0, "half": -5.0, "部分正确": -4.0,
                # 第四档：全盘错误
                "全盘错误": -8.5, "all_wrong": -8.5, "恶意编造": -10.0, "fabricated": -9.0, "hallucination": -8.5, "全错": -8.0, "编造": -8.5,
                # 第五档：诚实未知
                "诚实未知": -1.0, "honest_unknown": -1.0, "坦白未知": -1.0, "不知道": -1.0, "honest": -1.0,
                # 兼容旧格式
                "negative": -5.0, "bad": -5.0, "dislike": -5.0, "down": -5.0, "差": -5.0, "坏": -7.0,
                "neutral": 0.0, "一般": 0.0, "中立": 0.0,
            }

            if rating_str in preset_map:
                score = preset_map[rating_str]
            else:
                # 尝试解析为数值（支持 +4.5、-3.2 等格式）
                try:
                    parsed = float(rating_str)
                    # 限制范围：-10 ~ +5
                    score = max(-10.0, min(5.0, parsed))
                except (ValueError, TypeError):
                    score = 0.0  # 无法识别时默认为诚实未知档

            # ========== 第二阶段：判定反馈等级 ==========
            if score >= 4:
                feedback_type = "excellent"
                level = "极致优质"
            elif score >= 1:
                feedback_type = "positive"
                level = "基础合格"
            elif score > -3:
                feedback_type = "honest_unknown"
                level = "诚实未知"
            elif score >= -6.5:
                feedback_type = "half_wrong"
                level = "半对半错"
            else:
                feedback_type = "all_wrong"
                level = "全盘错误"

            # ========== 第三阶段：执行反馈训练 ==========
            start_state = self.token_to_state(user_input)
            context_states = []
            for item in self.context_chain[-10:]:
                s = self.token_to_state(item["input"])
                if s in self.state_to_text:
                    context_states.append(s)
            reasoning_path, layer_scores = self.multi_layer_inference(start_state, context_states)

            feedback_detail = {}
            abs_score = abs(score)

            if feedback_type == "excellent":
                # 极致优质：强力正向强化，注意力权重×(1.2~1.5)按分数缩放
                self.phrase_learner.learn_from_text(user_input, ai_response)
                self.update_weights(reasoning_path, user_input, ai_response)
                # 按分数线性缩放强化倍率：score=4→1.3x, score=5→1.5x
                reinforce_factor = 1.2 + (score - 4) * 0.3
                for layer_idx in range(self.num_layers):
                    layer_matrix = self.attention_matrices[layer_idx]
                    limited_path = [s for s in reasoning_path if s in self.state_to_text]
                    for i in range(len(limited_path) - 1):
                        s_from = limited_path[i]
                        s_to = limited_path[i + 1]
                        if s_from in layer_matrix and s_to in layer_matrix[s_from]:
                            layer_matrix[s_from][s_to] *= reinforce_factor
                            total = sum(layer_matrix[s_from].values()) + 1e-6
                            for k in layer_matrix[s_from]:
                                layer_matrix[s_from][k] /= total
                # 额外：多轮更新权重强化语义编码
                for _ in range(int(score - 2)):
                    self.update_weights(reasoning_path, user_input, ai_response)
                feedback_detail["action"] = "excellent_reinforcement"
                feedback_detail["reinforce_factor"] = round(reinforce_factor, 3)
                feedback_detail["extra_update_rounds"] = int(score - 2)

            elif feedback_type == "positive":
                # 基础合格：标准正向强化，注意力×(1.05~1.15)
                self.phrase_learner.learn_from_text(user_input, ai_response)
                self.update_weights(reasoning_path, user_input, ai_response)
                reinforce_factor = 1.05 + (score - 1) * 0.05
                for layer_idx in range(self.num_layers):
                    layer_matrix = self.attention_matrices[layer_idx]
                    limited_path = [s for s in reasoning_path if s in self.state_to_text]
                    for i in range(len(limited_path) - 1):
                        s_from = limited_path[i]
                        s_to = limited_path[i + 1]
                        if s_from in layer_matrix and s_to in layer_matrix[s_from]:
                            layer_matrix[s_from][s_to] *= reinforce_factor
                            total = sum(layer_matrix[s_from].values()) + 1e-6
                            for k in layer_matrix[s_from]:
                                layer_matrix[s_from][k] /= total
                feedback_detail["action"] = "positive_reinforcement"
                feedback_detail["reinforce_factor"] = round(reinforce_factor, 3)

            elif feedback_type == "honest_unknown":
                # 诚实未知：极轻惩罚或零惩罚，仅微调不punish
                if abs_score > 0:
                    # 仅做极轻微的权重调整
                    self.update_weights(reasoning_path, user_input, ai_response)
                    feedback_detail["action"] = "honest_unknown_light_update"
                else:
                    feedback_detail["action"] = "honest_unknown_no_update"
                feedback_detail["skipped_punish"] = True

            elif feedback_type == "half_wrong":
                # 半对半错：中等惩罚，应用punish + 如有修正则纠正训练
                # 按分数缩放punish次数：score=-4→1次, score=-6→3次
                punish_rounds = max(1, int(abs_score - 3))
                for _ in range(punish_rounds):
                    self.punish()
                if corrected_response and corrected_response.strip():
                    self.phrase_learner.learn_from_text(user_input, corrected_response)
                    self.update_weights(reasoning_path, user_input, corrected_response)
                    feedback_detail["action"] = "half_wrong_punish_and_corrected_train"
                    feedback_detail["corrected"] = True
                    feedback_detail["punish_rounds"] = punish_rounds
                else:
                    self.update_weights(reasoning_path, user_input, ai_response)
                    feedback_detail["action"] = "half_wrong_punish"
                    feedback_detail["corrected"] = False
                    feedback_detail["punish_rounds"] = punish_rounds

            elif feedback_type == "all_wrong":
                # 全盘错误：最高惩罚，多次punish + 必须纠正训练
                # 按分数缩放punish次数：score=-7→4次, score=-10→7次
                punish_rounds = max(3, int(abs_score - 3))
                for _ in range(punish_rounds):
                    self.punish()
                if corrected_response and corrected_response.strip():
                    self.phrase_learner.learn_from_text(user_input, corrected_response)
                    self.update_weights(reasoning_path, user_input, corrected_response)
                    # 额外用修正回复多轮训练以覆盖错误知识
                    for _ in range(punish_rounds):
                        self.update_weights(reasoning_path, user_input, corrected_response)
                    feedback_detail["action"] = "all_wrong_heavy_punish_and_corrected_train"
                    feedback_detail["corrected"] = True
                    feedback_detail["punish_rounds"] = punish_rounds
                    feedback_detail["corrected_train_rounds"] = punish_rounds
                else:
                    # 无修正回复时仍强力衰减
                    feedback_detail["action"] = "all_wrong_heavy_punish"
                    feedback_detail["corrected"] = False
                    feedback_detail["punish_rounds"] = punish_rounds

            # 对QKV权重进行数值范围限制
            for qkv_layer in self.qkv_layers:
                qkv_layer.clamp_weights()

            # 分段自动快照
            self._train_count += 1
            if self._train_count >= self.auto_save_train_interval:
                self._train_count = 0
                try:
                    self.save_snapshot()
                    log_performance(f"人类反馈训练分段自动快照已保存 (score={score})")
                except Exception as e:
                    log_error(f"人类反馈训练快照保存失败: {str(e)}")

            self._auto_full_save()

            input_tokens = len(self.tokenizer.tokenize(user_input))
            output_tokens = len(self.tokenizer.tokenize(ai_response))

            return {
                "status": "success",
                "score": score,
                "feedback_type": feedback_type,
                "level": level,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "detail": feedback_detail
            }

    def get_features(self):
        """获取功能开关状态"""
        return dict(self._features)

    def set_feature(self, feature_name, enabled):
        """设置功能开关
        Args:
            feature_name: 功能名 ("auto_full_save" 或 "auto_compress")
            enabled: True/False
        """
        if feature_name in self._features:
            self._features[feature_name] = bool(enabled)
            return {"status": "success", "feature": feature_name, "enabled": bool(enabled)}
        return {"status": "error", "message": f"未知功能: {feature_name}"}

    def _extract_key_phrases(self, text):
        phrases = []
        words = text.split()
        for i in range(len(words)):
            if len(words[i]) > 1:
                phrases.append(words[i])
            if i < len(words) - 1:
                two_word = f"{words[i]} {words[i + 1]}"
                phrases.append(two_word)
        return phrases[:5]

    def chat(self, user_input, max_output_tokens=200, enable_training=False):
        """对话 - 使用读锁，punish改为可选参数enable_training控制，增加reasoning_path和layer_scores，支持推理缓存"""
        with self._rw_lock:  # 使用读锁（RLock支持嵌套）
            if not user_input.strip():
                return {
                    "user_input": user_input,
                    "response": "",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "sentiment": "neutral",
                    "reasoning_path": [],
                    "layer_scores": []
                }

            sentiment = self._detect_user_sentiment(user_input)
            start_state = self.token_to_state(user_input)

            # 2.26: 模糊跳转核心 - 如果 start_state 没有出边，用模糊匹配找到最相似的已有 state
            if not self._has_out_edges(start_state) and len(self.state_to_text) > 1:
                fuzzy_candidates = self._fuzzy_match(user_input, top_k=5, threshold=0.15)
                for state_id, text, score in fuzzy_candidates:
                    if state_id != start_state and self._has_out_edges(state_id):
                        start_state = state_id  # 使用模糊匹配到的有出边的 state
                        break

            context_states = []
            for item in self.context_chain[-10:]:
                s = self.token_to_state(item["input"])
                if s in self.state_to_text:
                    context_states.append(s)

            reasoning_path, layer_scores = self.multi_layer_inference(start_state, context_states)

            # 三.2: 传递max_output_tokens参数
            response = self.decode_response(reasoning_path, user_input, sentiment, max_output_tokens=max_output_tokens)

            # 一.1: punish改为可选参数控制，enable_training=True时在chat中触发punish
            if enable_training:
                self.punish()

            self.context_chain.append({"input": user_input, "state": start_state, "response": response})
            if len(self.context_chain) > self.max_context_len:
                self.context_chain.pop(0)
            self.update_weights(reasoning_path, user_input, response)
            self._update_user_understanding(user_input, response, sentiment)
            input_tokens = len(self.tokenizer.tokenize(user_input))
            output_tokens = len(self.tokenizer.tokenize(response))
            # 2.25: 修复计数器从未递增的缺陷
            self.total_conversations += 1
            self.total_tokens_processed += input_tokens + output_tokens

            result = {
                "user_input": user_input,
                "response": response,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "sentiment": sentiment,
                "reasoning_path": reasoning_path,
                "layer_scores": layer_scores
            }

            self._auto_full_save()

            return result

    def _update_user_understanding(self, user_input, response, sentiment):
        if "last_sentiment" not in self.user_understanding:
            self.user_understanding["sentiment_history"] = []
        self.user_understanding["sentiment_history"].append(sentiment)
        if len(self.user_understanding["sentiment_history"]) > 10:
            self.user_understanding["sentiment_history"].pop(0)
        if sentiment == "positive" or sentiment == "negative":
            self.user_understanding["last_expressed"] = sentiment

    def _build_save_data(self):
        """构建统一的完整保存数据 - save_model和_do_full_save共用，确保格式一致"""
        with self._rw_lock:  # 2.25: 加锁防止并发读写导致数据不一致
            data = {
            # === 注意力权重与状态映射 ===
            "attention_matrices": [dict(layer) for layer in self.attention_matrices],
            "state_to_text": self.state_to_text,
            "text_to_state": self.text_to_state,
            "causal_position": self.causal_position,
            # === LRU缓存与访问计数 ===
            "lru_cache": list(self.lru_cache.keys()),
            "lru_access_counts": dict(self.lru_access_counts),
            # === 分词器(tokenizer)完整状态 ===
            "char_to_token": self.tokenizer.char_to_token,
            "token_to_char": self.tokenizer.token_to_char,
            "subword_to_token": self.tokenizer.subword_to_token,
            "token_to_subword": self.tokenizer.token_to_subword,
            "_next_token_id": self.tokenizer._next_token_id,
            "_next_subword_id": self.tokenizer._next_subword_id,
            "max_subword_len": self.tokenizer.max_subword_len,
            # === 语义编码器(SemanticEncoder)完整状态 ===
            "semantic": self.semantic.get_state(),
            # === QKV串行注意力层完整状态 ===
            "qkv_layers": [layer.get_state() for layer in self.qkv_layers],
            # === 短语学习器(PhraseLearner)完整状态 ===
            "phrase_patterns": dict(self.phrase_learner.phrase_patterns),
            "response_templates": self.phrase_learner.response_templates,
            # === 词汇表 ===
            "learned_vocab": self.learned_vocab,
            "base_vocab": self.base_vocab,
            # === 用户画像与自我认知 ===
            "user_preferences": self.user_preferences,
            "self_understanding": self.self_understanding,
            "improvement_goals": self.improvement_goals,
            "user_understanding": self.user_understanding,
            # === 性格与偏好 ===
            "personality": self.personality,
            "preferences": self.preferences,
            "conversation_style": self.conversation_style,
            # === 训练状态与超参数 ===
            "gradient_history": dict(self.gradient_history),
            "context_chain": self.context_chain,
            "learning_streak": self.learning_streak,
            "consecutive_correct": self.consecutive_correct,
            "num_layers": self.num_layers,
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "punishment_rate": self.punishment_rate,
            "max_context_len": self.max_context_len,
            "max_input_len": self.max_input_len,
            "layer_dropout": self.layer_dropout,
            "adaptive_lr": self.adaptive_lr,
            "learning_momentum": self.learning_momentum,
            # === 动态参数 ===
            "dynamic_params": dict(self.dynamic_params),
            # === 模型元信息 ===
            "model_name": self.model_name,
            "model_version": self.model_version,
            "total_tokens_processed": self.total_tokens_processed,
            "total_conversations": self.total_conversations,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            return data

    def save_model(self, path, use_gzip=False):
        """保存完整模型 - 支持gzip压缩，使用临时文件+rename防丢失"""
        data = self._build_save_data()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)

        # 六.2: 先写入临时文件，完成后rename
        tmp_path = path + ".tmp"
        marker_path = path + "._recovery_marker"

        try:
            if use_gzip == "lz4":
                # LZ4压缩
                json_bytes = json_str.encode("utf-8")
                compressed = lz4.frame.compress(json_bytes)
                tmp_path_lz4 = tmp_path + ".lz4"
                with open(tmp_path_lz4, "wb") as f:
                    f.write(compressed)
                with open(marker_path, 'w') as f:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
                if os.path.exists(path):
                    os.remove(path)
                os.rename(tmp_path_lz4, path)
            elif use_gzip:
                tmp_path_gz = tmp_path + ".gz"
                with gzip.open(tmp_path_gz, 'wt', encoding='utf-8') as f:
                    f.write(json_str)
                # 写入recovery marker
                with open(marker_path, 'w') as f:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
                # rename到正式文件
                if os.path.exists(path):
                    os.remove(path)
                os.rename(tmp_path_gz, path)
            else:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                # 写入recovery marker
                with open(marker_path, 'w') as f:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
                # rename到正式文件
                if os.path.exists(path):
                    os.remove(path)
                os.rename(tmp_path, path)
            # 写入完成后更新recovery marker
            with open(marker_path, 'w') as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            raise Exception(f"保存模型失败: {str(e)}")

    def load_model(self, path):
        """加载模型 - 支持gzip/lz4自动检测，层数兼容，临时文件恢复"""
        if not os.path.exists(path):
            # 六.2: 检测.tmp文件进行恢复
            tmp_path = path + ".tmp"
            tmp_path_gz = path + ".tmp.gz"
            tmp_path_lz4 = path + ".tmp.lz4"
            marker_path = path + "._recovery_marker"
            if os.path.exists(tmp_path):
                log_error(f"正式文件{path}不存在，尝试从.tmp恢复")
                path = tmp_path
            elif os.path.exists(tmp_path_gz):
                log_error(f"正式文件{path}不存在，尝试从.tmp.gz恢复")
                path = tmp_path_gz
            elif os.path.exists(tmp_path_lz4):
                log_error(f"正式文件{path}不存在，尝试从.tmp.lz4恢复")
                path = tmp_path_lz4
            else:
                return

        try:
            # 自动检测文件格式：.lz4 / .gz / 纯json
            is_lz4 = path.endswith('.lz4')
            is_gzip = path.endswith('.gz')
            if not is_lz4 and not is_gzip:
                # 尝试检测文件头
                try:
                    with open(path, 'rb') as f:
                        magic = f.read(4)
                        if magic[:2] == b'\x1f\x8b':
                            is_gzip = True
                        elif magic == b'\x04\x22\x4d\x18':
                            is_lz4 = True
                except Exception:
                    pass

            if is_lz4:
                with open(path, 'rb') as f:
                    raw = f.read()
                json_str = lz4.frame.decompress(raw).decode("utf-8")
                data = json.loads(json_str)
            elif is_gzip:
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
        except Exception as e:
            # 六.2: 尝试从.tmp恢复
            tmp_path = path + ".tmp"
            tmp_path_gz = path + ".tmp.gz"
            tmp_path_lz4 = path + ".tmp.lz4"
            for alt_path in [tmp_path, tmp_path_gz, tmp_path_lz4]:
                if os.path.exists(alt_path):
                    try:
                        if alt_path.endswith('.lz4'):
                            with open(alt_path, 'rb') as f:
                                raw = f.read()
                            json_str = lz4.frame.decompress(raw).decode("utf-8")
                            data = json.loads(json_str)
                        elif alt_path.endswith('.gz'):
                            with gzip.open(alt_path, 'rt', encoding='utf-8') as f:
                                data = json.load(f)
                        else:
                            with open(alt_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                        log_error(f"从{alt_path}成功恢复模型")
                        break
                    except Exception:
                        continue
            else:
                raise Exception(f"加载模型失败: {str(e)}")

        # 三.5: 先恢复state_to_text/text_to_state（必须在attention_matrices之前，否则过滤会误跳所有边）
        self.state_to_text = data.get("state_to_text", {})
        self.text_to_state = data.get("text_to_state", {})

        # 三.5: 层数兼容逻辑
        saved_attention = data.get("attention_matrices", [])
        self.attention_matrices = [defaultdict(lambda: defaultdict(float)) for _ in range(self.num_layers)]
        min_layers = min(len(saved_attention), self.num_layers)
        total_valid_edges = 0
        total_skipped_edges = 0
        for i in range(min_layers):
            layer = saved_attention[i]
            filtered_layer = defaultdict(lambda: defaultdict(float))
            valid_edges = 0
            skipped_edges = 0
            for from_state, transitions in layer.items():
                if from_state not in self.state_to_text:
                    skipped_edges += len(transitions)
                    continue
                for to_state, weight in transitions.items():
                    if to_state in self.state_to_text:
                        filtered_layer[from_state][to_state] = weight
                        valid_edges += 1
                    else:
                        skipped_edges += 1
            self.attention_matrices[i] = filtered_layer
            total_valid_edges += valid_edges
            total_skipped_edges += skipped_edges
        if total_skipped_edges > 0:
            log_error(f"权重兼容: 跳过 {total_skipped_edges} 条无效边（state_id不匹配）, 保留 {total_valid_edges} 条有效边")
        if len(saved_attention) > self.num_layers:
            print(f"警告: 模型文件包含{len(saved_attention)}层，当前模型仅使用{self.num_layers}层，多余层已忽略")
            log_error(f"模型文件层数{len(saved_attention)}多于当前num_layers={self.num_layers}，只加载前{self.num_layers}层")
        elif len(saved_attention) < self.num_layers:
            print(f"警告: 模型文件仅包含{len(saved_attention)}层，当前模型有{self.num_layers}层，多余层保持初始化状态")
            log_error(f"模型文件层数{len(saved_attention)}少于当前num_layers={self.num_layers}，多余层保持初始化状态")

        self.learned_vocab = data.get("learned_vocab", [])
        self.base_vocab = data.get("base_vocab", [])
        self.user_preferences = data.get("user_preferences", {})
        self.self_understanding = data.get("self_understanding", {})
        self.improvement_goals = data.get("improvement_goals", [])
        self.user_understanding = data.get("user_understanding", {})
        self.causal_position = data.get("causal_position", 0)
        # === LRU缓存与访问计数 ===
        self.lru_cache = OrderedDict()
        self.lru_access_counts = defaultdict(int)
        lru_list = data.get("lru_cache", [])
        for state_id in lru_list:
            if state_id in self.state_to_text:
                self._lru_access(state_id)
        # 恢复lru访问计数
        saved_lru_counts = data.get("lru_access_counts", {})
        for sid, count in saved_lru_counts.items():
            if sid in self.lru_cache:
                self.lru_access_counts[sid] = count
        # === 分词器(tokenizer)完整状态 ===
        self.tokenizer.char_to_token = data.get("char_to_token", {})
        self.tokenizer.token_to_char = data.get("token_to_char", {})
        self.tokenizer.subword_to_token = data.get("subword_to_token", {})
        self.tokenizer.token_to_subword = data.get("token_to_subword", {})
        self.tokenizer._next_token_id = data.get("_next_token_id", 1)
        self.tokenizer._next_subword_id = data.get("_next_subword_id", 1)
        self.tokenizer.max_subword_len = data.get("max_subword_len", 8)
        # === 语义编码器(SemanticEncoder)完整状态 ===
        sem_state = data.get("semantic", {})
        if sem_state:
            self.semantic.word_vec = sem_state.get("word_vec", {})
            self.semantic.lr = sem_state.get("lr", 0.05)
            self.semantic.grad_clip = sem_state.get("grad_clip", 1.0)
        # === QKV串行注意力层完整状态 ===
        saved_qkv = data.get("qkv_layers", [])
        for i, qkv_state in enumerate(saved_qkv):
            if i < len(self.qkv_layers):
                self.qkv_layers[i].Wq = qkv_state.get("Wq", self.qkv_layers[i].Wq)
                self.qkv_layers[i].Wk = qkv_state.get("Wk", self.qkv_layers[i].Wk)
                self.qkv_layers[i].Wv = qkv_state.get("Wv", self.qkv_layers[i].Wv)
                self.qkv_layers[i].weight_min = qkv_state.get("weight_min", -5.0)
                self.qkv_layers[i].weight_max = qkv_state.get("weight_max", 5.0)
        # === 短语学习器(PhraseLearner) - 兼容新旧两种格式 ===
        # 新格式: phrase_patterns + response_templates (独立字段)
        # 旧格式: phrase_learner (嵌套对象, 旧版_do_full_save)
        if "phrase_learner" in data and "phrase_patterns" not in data:
            pl_state = data.get("phrase_learner", {})
            self.phrase_learner.phrase_patterns = defaultdict(list, pl_state.get("phrase_patterns", {}))
            self.phrase_learner.response_templates = pl_state.get("response_templates", [])
        else:
            self.phrase_learner.phrase_patterns = defaultdict(list, data.get("phrase_patterns", {}))
            self.phrase_learner.response_templates = data.get("response_templates", [])
        # === 性格与偏好 ===
        self.personality = data.get("personality", self.personality)
        self.preferences = data.get("preferences", self.preferences)
        self.conversation_style = data.get("conversation_style", "自然")
        # === 训练状态与超参数 ===
        self.gradient_history = defaultdict(float, data.get("gradient_history", {}))
        self.context_chain = data.get("context_chain", [])
        self.learning_streak = data.get("learning_streak", 0)
        self.consecutive_correct = data.get("consecutive_correct", 0)
        # 超参数恢复(使用get + 已有默认值, 避免覆盖构造函数的合理默认值)
        self.learning_rate = data.get("learning_rate", self.learning_rate)
        self.weight_decay = data.get("weight_decay", self.weight_decay)
        self.punishment_rate = data.get("punishment_rate", self.punishment_rate)
        self.max_context_len = data.get("max_context_len", self.max_context_len)
        self.max_input_len = data.get("max_input_len", self.max_input_len)
        self.layer_dropout = data.get("layer_dropout", self.layer_dropout)
        self.adaptive_lr = data.get("adaptive_lr", self.adaptive_lr)
        self.learning_momentum = data.get("learning_momentum", self.learning_momentum)
        # === 动态参数 ===
        saved_params = data.get("dynamic_params", {})
        if saved_params:
            for k, v in saved_params.items():
                if k in self.dynamic_params:
                    self.dynamic_params[k] = v
        # === 模型元信息 ===
        self.model_name = data.get("model_name", self.model_name)
        self.model_version = data.get("model_version", self.model_version)
        self.total_tokens_processed = data.get("total_tokens_processed", 0)
        self.total_conversations = data.get("total_conversations", 0)
        self.personality_reward = PersonalityRewardSystem(self.personality)

        # 加载auto_save_train_interval配置
        config = load_config()
        self.auto_save_train_interval = config.get("auto_save_train_interval", 10)

    def save_snapshot(self, path=None):
        """保存轻量化快照 - 仅保存核心权重数据（attention_matrices和state_to_text的精简版本）"""
        if path is None:
            path = os.path.join(SCRIPT_DIR, "model.snapshot.json.gz")
        # 精简版数据
        compact_matrices = []
        for layer in self.attention_matrices:
            compact_layer = {}
            for s in layer:
                # 只保留权重最大的前10个转移
                top_transitions = sorted(layer[s].items(), key=lambda x: x[1], reverse=True)[:10]
                if top_transitions:
                    compact_layer[s] = {n: w for n, w in top_transitions if w > 0.01}
            compact_matrices.append(compact_layer)

        # 精简state_to_text
        compact_state_to_text = {}
        for state_id in list(self.lru_cache.keys())[:500]:
            if state_id in self.state_to_text:
                compact_state_to_text[state_id] = self.state_to_text[state_id]

        data = {
            "attention_matrices": compact_matrices,
            "state_to_text": compact_state_to_text,
            "text_to_state": {v: k for k, v in compact_state_to_text.items()},
            "causal_position": self.causal_position,
            "learning_streak": self.learning_streak,
            "consecutive_correct": self.consecutive_correct,
            "personality": self.personality,
            "preferences": self.preferences,
            "conversation_style": self.conversation_style,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        tmp_path = path + ".tmp"
        try:
            with gzip.open(tmp_path, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            if os.path.exists(path):
                os.remove(path)
            os.rename(tmp_path, path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            raise Exception(f"保存快照失败: {str(e)}")

    def _auto_full_save(self):
        """自动全量保存 - 异步执行，不阻塞调用方"""
        if not self._features.get("auto_full_save", True):
            return
        threading.Thread(target=self._do_full_save, daemon=True).start()

    def _do_full_save(self):
        """执行全量保存的内部方法 - 使用统一格式，与save_model完全一致"""
        try:
            save_path = os.path.join(SCRIPT_DIR, f"{self.session_id}.model.json" if hasattr(self, 'session_id') and self.session_id else "mtgchatgf.model.json")
            use_compress = self._features.get("auto_compress", True)
            
            # 使用统一保存方法，确保格式与save_model完全一致
            data = self._build_save_data()
            
            json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
            
            if use_compress:
                final_path = save_path + ".lz4"
                compressed = lz4.frame.compress(json_bytes)
                tmp_path = final_path + ".tmp"
                with open(tmp_path, "wb") as f:
                    f.write(compressed)
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(tmp_path, final_path)
            else:
                final_path = save_path
                tmp_path = final_path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(data, ensure_ascii=False, indent=2))
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(tmp_path, final_path)
            
            log_performance(f"自动全量保存完成: {final_path} ({'LZ4压缩' if use_compress else '无压缩'}, {os.path.getsize(final_path)} bytes)")
        except Exception as e:
            log_error(f"自动全量保存失败: {str(e)}")

    def load_snapshot(self, path="model.snapshot.json.gz"):
        """加载轻量化快照 - 恢复核心权重数据"""
        if not os.path.exists(path):
            return
        try:
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise Exception(f"加载快照失败: {str(e)}")

        saved_attention = data.get("attention_matrices", [])
        min_layers = min(len(saved_attention), self.num_layers)
        for i in range(min_layers):
            for s, transitions in saved_attention[i].items():
                if s not in self.attention_matrices[i]:
                    self.attention_matrices[i][s] = defaultdict(float)
                for n, w in transitions.items():
                    self.attention_matrices[i][s][n] = w
        if len(saved_attention) > self.num_layers:
            print(f"警告: 快照文件层数{len(saved_attention)}多于当前num_layers={self.num_layers}，多余层已忽略")
        elif len(saved_attention) < self.num_layers:
            print(f"警告: 快照文件层数{len(saved_attention)}少于当前num_layers={self.num_layers}，多余层保持初始化")

        saved_states = data.get("state_to_text", {})
        for state_id, text in saved_states.items():
            if state_id not in self.state_to_text:
                self.state_to_text[state_id] = text
                self.text_to_state[text] = state_id
            self._lru_access(state_id)

        self.causal_position = data.get("causal_position", self.causal_position)
        self.learning_streak = data.get("learning_streak", self.learning_streak)
        self.consecutive_correct = data.get("consecutive_correct", self.consecutive_correct)
        # 2.25: 快照也恢复性格/偏好/对话风格
        if data.get("personality"):
            self.personality = data.get("personality", self.personality)
            self.personality_reward = PersonalityRewardSystem(self.personality)
        if data.get("preferences"):
            self.preferences = data.get("preferences", self.preferences)
        self.conversation_style = data.get("conversation_style", self.conversation_style)

    def auto_snapshot_check(self):
        """定时检查是否需要自动保存快照"""
        now = time.time()
        if now - self._last_snapshot_time >= self._snapshot_interval:
            self._last_snapshot_time = now
            try:
                self.save_snapshot()
                log_performance("定时自动快照已保存")
            except Exception as e:
                log_error(f"定时自动快照保存失败: {str(e)}")

    def get_personality(self):
        return self.personality

    def set_personality_trait(self, trait, value):
        if trait in self.personality:
            self.personality[trait] = max(0.0, min(1.0, value))
            self.personality_reward.personality = self.personality

    def get_preferences(self):
        return self.preferences

    def add_preference(self, category, item):
        if category in self.preferences:
            if isinstance(self.preferences[category], list) and item not in self.preferences[category]:
                self.preferences[category].append(item)
            elif not isinstance(self.preferences[category], list):
                self.preferences[category] = item

    def set_conversation_style(self, style):
        self.conversation_style = style
        self.preferences["偏好的回应风格"] = style

    def get_learning_stats(self):
        return {
            "平均响应分数": round(self.personality_reward.get_average_score(), 2),
            "学习连续性": self.learning_streak,
            "学会短语数": len(self.phrase_learner.response_templates),
            "学会词汇数": len(self.learned_vocab)
        }


class LLMAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self._openai_route():
            return
        if self.path == "/sessions":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            sessions = list(self.server.sessions.keys())
            self.wfile.write(json.dumps({"sessions": sessions}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/instances":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            instances = []
            for session_id, model in self.server.sessions.items():
                token_count = len(model.tokenizer.char_to_token) + len(model.tokenizer.subword_to_token)
                instance_info = {
                    "session_id": session_id,
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "token_count": token_count,
                    "conversation_count": len(model.context_chain),
                    "api_key": None,
                    "is_free": False,
                    "token_balance": None,
                    "personality": model.personality,
                    "preferences": model.preferences,
                    "learning_stats": model.get_learning_stats(),
                    "layers": model.num_layers,
                    "causal_position": model.causal_position
                }
                for api_key, key_data in self.server.api_keys.items():
                    if key_data.get("session_id") == session_id:
                        instance_info["api_key"] = api_key
                        instance_info["is_free"] = key_data.get("is_free", False)
                        instance_info["token_balance"] = key_data.get("tokens", 0)
                        break
                instances.append(instance_info)
            self.wfile.write(json.dumps({"instances": instances, "total": len(instances)}, ensure_ascii=False).encode("utf-8"))
        elif self.path.startswith("/instance/"):
            session_id = self.path.split("/instance/")[1]
            if session_id in self.server.sessions:
                model = self.server.sessions[session_id]
                token_count = len(model.tokenizer.char_to_token) + len(model.tokenizer.subword_to_token)
                instance_info = {
                    "session_id": session_id,
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "token_count": token_count,
                    "conversation_count": len(model.context_chain),
                    "layers": model.num_layers,
                    "learning_stats": model.get_learning_stats(),
                    "personality": model.personality,
                    "preferences": model.preferences,
                    "context_chain": model.context_chain[-10:],
                    "api_key": None,
                    "is_free": False,
                    "token_balance": None
                }
                for api_key, key_data in self.server.api_keys.items():
                    if key_data.get("session_id") == session_id:
                        instance_info["api_key"] = api_key
                        instance_info["is_free"] = key_data.get("is_free", False)
                        instance_info["token_balance"] = key_data.get("tokens", 0)
                        break
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"instance": instance_info}, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Instance not found"}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/personality":
            api_key = self.headers.get("Authorization", "default").replace("Bearer ", "")
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                model = list(self.server.sessions.values())[0]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"personality": model.get_personality()}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/preferences":
            api_key = self.headers.get("Authorization", "default").replace("Bearer ", "")
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                model = list(self.server.sessions.values())[0]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"preferences": model.get_preferences()}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/stats":
            api_key = self.headers.get("Authorization", "default").replace("Bearer ", "")
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                model = list(self.server.sessions.values())[0]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            stats = model.get_learning_stats()
            if api_key in self.server.api_keys:
                stats["token_balance"] = self.server.api_keys[api_key]["tokens"]
                stats["token_usage"] = self.server.token_usage.get(api_key, 0)
            self.wfile.write(json.dumps({"stats": stats}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/api_info":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            api_info = {
                "server_name": "千因 - MTG AI V-Causal API",
                "version": "1.0",
                "total_instances": len(self.server.sessions),
                "total_api_keys": len(self.server.api_keys),
                "queue_size": self.server.request_queue.qsize() if hasattr(self.server, 'request_queue') else 0,
                "endpoints": {
                    "chat": {"method": "POST", "path": "/chat", "description": "对话接口"},
                    "train": {"method": "POST", "path": "/train", "description": "训练接口"},
                    "feedback": {"method": "POST", "path": "/feedback", "description": "人类反馈训练接口"},
                    "create_instance": {"method": "POST", "path": "/create_instance", "description": "创建新实例"},
                    "delete_instance": {"method": "POST", "path": "/delete_instance", "description": "删除实例"},
                    "features": {"method": "POST", "path": "/features", "description": "功能开关管理"},
                    "update_tokens": {"method": "POST", "path": "/update_tokens", "description": "更新Token余额"},
                    "set_personality": {"method": "POST", "path": "/set_personality", "description": "设置性格"},
                    "add_preference": {"method": "POST", "path": "/add_preference", "description": "添加偏好"},
                    "rename_session": {"method": "POST", "path": "/rename_session", "description": "重命名会话"},
                    "export_chat": {"method": "GET", "path": "/export_chat", "description": "导出对话"},
                    "import_chat": {"method": "POST", "path": "/import_chat", "description": "导入对话"},
                    "save_model": {"method": "POST", "path": "/save_model", "description": "保存模型"},
                    "load_model": {"method": "POST", "path": "/load_model", "description": "加载模型"},
                    "sessions": {"method": "GET", "path": "/sessions", "description": "获取会话列表"},
                    "instances": {"method": "GET", "path": "/instances", "description": "获取所有实例详细信息"},
                    "instance_detail": {"method": "GET", "path": "/instance/{session_id}", "description": "获取单个实例详细信息"},
                    "personality": {"method": "GET", "path": "/personality", "description": "获取性格设置"},
                    "preferences": {"method": "GET", "path": "/preferences", "description": "获取偏好设置"},
                    "stats": {"method": "GET", "path": "/stats", "description": "获取统计信息"},
                    "api_info": {"method": "GET", "path": "/api_info", "description": "获取API信息"},
                    "health": {"method": "GET", "path": "/health", "description": "健康检查"}
                }
            }
            self.wfile.write(json.dumps({"api_info": api_info}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}, ensure_ascii=False).encode("utf-8"))
        elif self.path.startswith("/export_chat"):
            api_key = self.headers.get("Authorization", "default").replace("Bearer ", "")
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                model = list(self.server.sessions.values())[0]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"history": model.context_chain[-200:]}, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self._openai_route():
            return
        if self.path == "/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            user_input = data.get("input", "")
            # 二.2: 超长输入拦截
            model = self.server.get_session_by_api_key(api_key)
            if model and len(user_input) > model.max_input_len:
                self.send_response(400)
                self.end_headers()
                error_msg = json.dumps({"error": f"输入长度超过限制 (max_input_len={model.max_input_len})"}, ensure_ascii=False).encode("utf-8")
                self.wfile.write(error_msg)
                return
            if not self.server.check_token_balance(api_key):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"insufficient tokens"}')
                return
            if not self.server.check_rate_limit(api_key):
                self.send_response(429)
                self.end_headers()
                self.wfile.write(b'{"error":"rate limit exceeded"}')
                return
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return

            # 四.1: 将请求放入排队限流队列
            max_output_tokens = data.get("max_output_tokens", 200)
            enable_training = data.get("enable_training", False)
            result_future = queue.Queue()
            self.server.request_queue.put(("chat", api_key, user_input, max_output_tokens, enable_training, result_future))
            try:
                result = result_future.get(timeout=30)
            except queue.Empty:
                self.send_response(504)
                self.end_headers()
                self.wfile.write(b'{"error":"request timeout"}')
                return

            if isinstance(result, dict) and "error" in result:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
                return

            self.server.current_session = self.server.api_keys[api_key]["session_id"]
            self.server.deduct_tokens(api_key, result["input_tokens"] + result["output_tokens"])
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"result": result, "api_key": api_key}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/set_personality":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            trait = data.get("trait", "")
            value = data.get("value", 0.5)
            model.set_personality_trait(trait, value)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/add_preference":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            category = data.get("category", "")
            item = data.get("item", "")
            model.add_preference(category, item)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/create_instance":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            session_id = data.get("session_id", None)
            api_key, session_id = self.server.add_instance(session_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"api_key": api_key, "session_id": session_id}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/delete_instance":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "")
            success = self.server.delete_instance(api_key)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/features":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            action = data.get("action", "get")  # get / set
            feature_name = data.get("feature", "")
            enabled = data.get("enabled", None)
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            if action == "get":
                result = model.get_features()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"result": result}, ensure_ascii=False).encode("utf-8"))
            elif action == "set":
                if not feature_name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"error":"missing feature name"}')
                    return
                if enabled is None:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"error":"missing enabled value"}')
                    return
                result = model.set_feature(feature_name, enabled)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"result": result}, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid action, use get or set"}')
        elif self.path == "/update_tokens":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "")
            amount = data.get("amount", 0)
            new_balance = self.server.update_tokens(api_key, amount)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"new_balance": new_balance}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/train":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            user_input = data.get("input", "")
            response = data.get("response", "")
            mode = data.get("mode", "refine")
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            # 二.2: 超长输入拦截（训练接口）
            if len(user_input) > model.max_input_len or len(response) > model.max_input_len:
                self.send_response(400)
                self.end_headers()
                error_msg = json.dumps({"error": f"输入长度超过限制 (max_input_len={model.max_input_len})"}, ensure_ascii=False).encode("utf-8")
                self.wfile.write(error_msg)
                return

            # 四.1: 训练也通过排队队列
            result_future = queue.Queue()
            self.server.request_queue.put(("train", api_key, user_input, response, mode, result_future))
            try:
                result = result_future.get(timeout=60)
            except queue.Empty:
                self.send_response(504)
                self.end_headers()
                self.wfile.write(b'{"error":"request timeout"}')
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"result": result}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/feedback":
            # 人类反馈训练接口
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            user_input = data.get("input", "")
            ai_response = data.get("response", "")
            rating = data.get("rating", "neutral")
            corrected_response = data.get("corrected_response", None)
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            # 二.2: 超长输入拦截
            if len(user_input) > model.max_input_len or len(ai_response) > model.max_input_len:
                self.send_response(400)
                self.end_headers()
                error_msg = json.dumps({"error": f"输入长度超过限制 (max_input_len={model.max_input_len})"}, ensure_ascii=False).encode("utf-8")
                self.wfile.write(error_msg)
                return

            # 四.1: 反馈训练也通过排队队列
            result_future = queue.Queue()
            self.server.request_queue.put(("feedback", api_key, user_input, ai_response, rating, corrected_response, result_future))
            try:
                result = result_future.get(timeout=60)
            except queue.Empty:
                self.send_response(504)
                self.end_headers()
                self.wfile.write(b'{"error":"request timeout"}')
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"result": result}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/rename_session":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "")
            new_name = data.get("new_name", "")
            success = self.server.rename_instance(api_key, new_name)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/import_chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            chat_history = data.get("chat_history", [])
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            model.context_chain.extend(chat_history)
            if len(model.context_chain) > model.max_context_len:
                model.context_chain = model.context_chain[-model.max_context_len:]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/save_model":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            session_id = self.server.api_keys.get(api_key, {}).get("session_id", "mtgchatgf") if api_key in self.server.api_keys else "mtgchatgf"
            raw_path = data.get("path", os.path.join(SCRIPT_DIR, session_id + ".model.json"))
            path = _validate_path(raw_path)
            if path is None:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "invalid path"}, ensure_ascii=False).encode("utf-8"))
                return
            use_gzip = data.get("use_gzip", False)
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            try:
                model.save_model(path, use_gzip=use_gzip)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "path": path}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/load_model":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            api_key = data.get("api_key", "mtgchatgf")
            session_id = self.server.api_keys.get(api_key, {}).get("session_id", "mtgchatgf") if api_key in self.server.api_keys else "mtgchatgf"
            raw_path = data.get("path", os.path.join(SCRIPT_DIR, session_id + ".model.json"))
            path = _validate_path(raw_path)
            if path is None:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "invalid path"}, ensure_ascii=False).encode("utf-8"))
                return
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            try:
                model.load_model(path)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "path": path}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


    # ========== OpenAI 兼容 API 端点 ==========
    def do_v1_chat(self):
        """OpenAI 兼容对话接口 POST /v1/chat/completions"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid json"}, ensure_ascii=False).encode("utf-8"))
            return
        auth = self.headers.get("Authorization", "")
        api_key = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else data.get("api_key", "mtgchatgf")
        model = self.server.get_session_by_api_key(api_key)
        if not model:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid api key"}, ensure_ascii=False).encode("utf-8"))
            return
        if "temperature" in data: model.dynamic_params["temperature"] = data["temperature"]
        if "top_k" in data: model.dynamic_params["top_k"] = data["top_k"]
        if "top_p" in data: model.dynamic_params["top_p"] = data["top_p"]
        messages = data.get("messages", [])
        user_input = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_input = msg.get("content", "")
                break
        if not user_input:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "no user message found"}, ensure_ascii=False).encode("utf-8"))
            return
        max_tokens = data.get("max_tokens", data.get("max_output_tokens", model.dynamic_params.get("max_output_tokens", 200)))
        if "max_output_tokens" in model.dynamic_params and max_tokens > model.dynamic_params["max_output_tokens"]:
            max_tokens = model.dynamic_params["max_output_tokens"]
        result = model.chat(user_input, max_output_tokens=max_tokens)
        response_data = {
            "id": f"chatcmpl-{secrets.token_hex(8)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": data.get("model", "qianyin"),
            "choices": [{"index": 0, "message": {"role": "assistant", "content": result.get("response", "")}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": result.get("input_tokens", 0), "completion_tokens": result.get("output_tokens", 0), "total_tokens": result.get("input_tokens", 0) + result.get("output_tokens", 0)}
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

    def do_v1_completions(self):
        """OpenAI 兼容补全接口 POST /v1/completions"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid json"}, ensure_ascii=False).encode("utf-8"))
            return
        auth = self.headers.get("Authorization", "")
        api_key = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else data.get("api_key", "mtgchatgf")
        model = self.server.get_session_by_api_key(api_key)
        if not model:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid api key"}, ensure_ascii=False).encode("utf-8"))
            return
        prompt = data.get("prompt", "")
        if not prompt:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "prompt required"}, ensure_ascii=False).encode("utf-8"))
            return
        max_tokens = data.get("max_tokens", 200)
        if "max_output_tokens" in model.dynamic_params and max_tokens > model.dynamic_params["max_output_tokens"]:
            max_tokens = model.dynamic_params["max_output_tokens"]
        if "temperature" in data: model.dynamic_params["temperature"] = data["temperature"]
        result = model.chat(prompt, max_output_tokens=max_tokens)
        response_data = {
            "id": f"cmpl-{secrets.token_hex(8)}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": data.get("model", "qianyin"),
            "choices": [{"text": result.get("response", ""), "index": 0, "logprobs": None, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": result.get("input_tokens", 0), "completion_tokens": result.get("output_tokens", 0), "total_tokens": result.get("input_tokens", 0) + result.get("output_tokens", 0)}
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

    def _openai_route(self):
        """OpenAI 路由分发"""
        path = self.path
        if path.startswith("/v1/chat/completions") and self.command == "POST":
            self.do_v1_chat()
            return True
        elif path.startswith("/v1/completions") and self.command == "POST":
            self.do_v1_completions()
            return True
        return False

    def log_message(self, format, *args):
        """抑制默认的HTTP日志输出"""
        pass


class LLMServer(IPv6HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.sessions = {}
        self.api_keys = load_api_keys()
        self.token_usage = defaultdict(int)
        self.rate_limit = defaultdict(int)
        self.rate_limit_window = 60
        self.rate_limit_max = 100
        self.current_session = None
        # 四.1: 多并发请求排队限流队列
        self.request_queue = queue.Queue(maxsize=50)
        self._worker_running = True
        self._worker_thread = None
        # 四.4: 定时快照定时器
        self._snapshot_timer = None
        self._init_sessions()
        self._start_worker()
        self._start_snapshot_timer()

    def _start_worker(self):
        """启动worker线程处理排队请求"""
        def worker_loop():
            while self._worker_running:
                try:
                    item = self.request_queue.get(timeout=1.0)
                    if item is None:
                        continue
                    try:
                        self._process_request(item)
                    except Exception as e:
                        log_error(f"Worker处理请求异常: {str(e)}")
                except queue.Empty:
                    continue
                except Exception as e:
                    log_error(f"Worker循环异常: {str(e)}")
        self._worker_thread = threading.Thread(target=worker_loop, daemon=True)
        self._worker_thread.start()
        log_performance("LLMServer请求处理Worker线程已启动")

    def _process_request(self, item):
        """处理单个排队请求"""
        if item[0] == "chat":
            _, api_key, user_input, max_output_tokens, enable_training, result_future = item
            model = self.get_session_by_api_key(api_key)
            if model:
                result = model.chat(user_input, max_output_tokens=max_output_tokens, enable_training=enable_training)
                result_future.put(result)
            else:
                result_future.put({"error": "invalid api key"})
        elif item[0] == "train":
            _, api_key, user_input, response, mode, result_future = item
            model = self.get_session_by_api_key(api_key)
            if model:
                result = model.train(user_input, response, mode)
                result_future.put(result)
            else:
                result_future.put({"error": "invalid api key"})
        elif item[0] == "feedback":
            _, api_key, user_input, ai_response, rating, corrected_response, result_future = item
            model = self.get_session_by_api_key(api_key)
            if model:
                result = model.human_feedback(user_input, ai_response, rating, corrected_response)
                result_future.put(result)
            else:
                result_future.put({"error": "invalid api key"})

    def _start_snapshot_timer(self):
        """启动定时快照定时器"""
        def snapshot_loop():
            while self._worker_running:
                try:
                    time.sleep(60)
                    for session_id, model in self.sessions.items():
                        model.auto_snapshot_check()
                except Exception as e:
                    log_error(f"定时快照检查异常: {str(e)}")
        timer_thread = threading.Thread(target=snapshot_loop, daemon=True)
        timer_thread.start()
        log_performance("LLMServer定时快照定时器已启动")

    def shutdown(self):
        """关闭服务器时停止worker"""
        self._worker_running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        super().shutdown()

    def _init_sessions(self):
        config = load_config()
        weights_dir = config.get("weights_path", SCRIPT_DIR)
        if not os.path.exists(weights_dir):
            os.makedirs(weights_dir, exist_ok=True)
        for api_key, key_data in self.api_keys.items():
            session_id = key_data.get("session_id", f"session_{len(self.sessions)}")
            if session_id not in self.sessions:
                weights_file = os.path.join(weights_dir, f"{session_id}.json")
                model = LightweightMultiLayerLLM()
                # 先尝试加载快照（更快）
                snapshot_file = os.path.join(weights_dir, f"{session_id}.snapshot.json.gz")
                if os.path.exists(snapshot_file):
                    try:
                        model.load_snapshot(snapshot_file)
                        log_performance(f"从快照快速加载了{session_id}的缓存数据")
                    except Exception as e:
                        log_error(f"加载快照失败，回退到全量模型: {str(e)}")
                if os.path.exists(weights_file):
                    try:
                        model.load_model(weights_file)
                    except Exception as e:
                        log_error(f"Failed to load model for {session_id}: {str(e)}")
                self.sessions[session_id] = model
        if "mtgchatgf" not in self.api_keys:
            self.add_instance("mtgchatgf")
        if len(self.sessions) == 0:
            self.add_instance("default")

    def get_session_by_api_key(self, api_key):
        if api_key in self.api_keys:
            session_id = self.api_keys[api_key].get("session_id", None)
            if session_id and session_id in self.sessions:
                return self.sessions[session_id]
        return None

    def check_token_balance(self, api_key):
        if api_key not in self.api_keys:
            return False
        tokens = self.api_keys[api_key].get("tokens", 0)
        if tokens == -1:
            return True
        return tokens > 0

    def check_rate_limit(self, api_key):
        now = int(time.time())
        window_key = f"{api_key}_{now // self.rate_limit_window}"
        self.rate_limit[window_key] = self.rate_limit.get(window_key, 0) + 1
        return self.rate_limit[window_key] <= self.rate_limit_max

    def deduct_tokens(self, api_key, tokens):
        if api_key not in self.api_keys:
            return
        if self.api_keys[api_key].get("tokens") == -1:
            return
        self.api_keys[api_key]["tokens"] = max(0, self.api_keys[api_key].get("tokens", 0) - tokens)
        self.token_usage[api_key] += tokens
        save_api_keys(self.api_keys)

    def add_instance(self, session_id=None):
        if not session_id:
            session_id = f"session_{len(self.sessions) + 1}"
            while session_id in self.sessions:
                session_id = f"session_{len(self.sessions) + 1}"
        if session_id in self.sessions:
            existing_key = None
            for k, v in self.api_keys.items():
                if v.get("session_id") == session_id:
                    existing_key = k
                    break
            if existing_key:
                return existing_key, session_id
        model = LightweightMultiLayerLLM()
        self.sessions[session_id] = model
        if session_id == "mtgchatgf":
            api_key = "mtgchatgf"
        else:
            api_key = secrets.token_urlsafe(32)
        self.api_keys[api_key] = {
            "session_id": session_id,
            "tokens": -1 if session_id == "mtgchatgf" else 1000,
            "is_free": session_id == "mtgchatgf",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_api_keys(self.api_keys)
        return api_key, session_id

    def delete_instance(self, api_key):
        if api_key not in self.api_keys:
            return False
        session_id = self.api_keys[api_key].get("session_id")
        if session_id == "mtgchatgf" or not session_id:
            return False
        if session_id in self.sessions:
            del self.sessions[session_id]
        del self.api_keys[api_key]
        save_api_keys(self.api_keys)
        return True

    def update_tokens(self, api_key, amount):
        if api_key not in self.api_keys:
            return -1
        if self.api_keys[api_key].get("is_free", False):
            return -1
        self.api_keys[api_key]["tokens"] = max(0, self.api_keys[api_key].get("tokens", 0) + amount)
        save_api_keys(self.api_keys)
        return self.api_keys[api_key]["tokens"]

    def rename_instance(self, api_key, new_name):
        if api_key not in self.api_keys:
            return False
        old_name = self.api_keys[api_key].get("session_id")
        if old_name == new_name or old_name == "mtgchatgf":
            return False
        if new_name in self.sessions or not new_name:
            return False
        model = self.sessions[old_name]
        del self.sessions[old_name]
        self.sessions[new_name] = model
        self.api_keys[api_key]["session_id"] = new_name
        save_api_keys(self.api_keys)
        return True


class CISLAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            user_input = data.get("input", "")
            enable_training = data.get("enable_training", False)
            max_output_tokens = data.get("max_output_tokens", 200)
            if "mtgchatgf" in self.server.llm_server.sessions:
                model = self.server.llm_server.sessions["mtgchatgf"]
                result = model.chat(user_input, max_output_tokens=max_output_tokens, enable_training=enable_training)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"result": result}, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b'{"error":"server not available"}')
        elif self.path == "/feedback":
            # CISL无鉴权人类反馈训练接口
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return
            user_input = data.get("input", "")
            ai_response = data.get("response", "")
            rating = data.get("rating", "neutral")
            corrected_response = data.get("corrected_response", None)
            if "mtgchatgf" in self.server.llm_server.sessions:
                model = self.server.llm_server.sessions["mtgchatgf"]
                result = model.human_feedback(user_input, ai_response, rating, corrected_response)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"result": result}, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b'{"error":"server not available"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """抑制默认的HTTP日志输出"""
        pass



class WebAdminHandler(BaseHTTPRequestHandler):
    """Web 管理界面处理器 - 端口 8080"""

    def do_GET(self):
        if self.path == "/" or self.path == "/admin":
            self._serve_admin_page()
        elif self.path.startswith("/admin/api/"):
            self._handle_api()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.startswith("/admin/api/"):
            self._handle_api()
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith("/admin/api/"):
            self._handle_api()
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_admin_page(self):
        html = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>千因 - 管理后台</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif; background: #1e1e1e; color: #d4d4d4; font-size: 14px; }
.container { display: flex; height: 100vh; }
.sidebar { width: 260px; background: #252526; padding: 15px; overflow-y: auto; flex-shrink: 0; border-right: 1px solid #3c3c3c; }
.main { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; }
h1 { font-size: 16px; margin-bottom: 15px; color: #007acc; }
h2 { font-size: 13px; margin: 12px 0 8px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
.btn { background: #007acc; color: white; border: none; padding: 7px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; transition: background 0.2s; }
.btn:hover { background: #005a9e; }
.btn-sm { padding: 4px 10px; font-size: 12px; }
.btn-danger { background: #c42b1c; }
.btn-danger:hover { background: #a02010; }
.btn-success { background: #2d7d2d; }
.btn-success:hover { background: #1f5e1f; }
.btn-warn { background: #cc8800; }
.btn-warn:hover { background: #aa6f00; }
input, select, textarea { width: 100%; padding: 7px; background: #3c3c3c; border: 1px solid #555; color: #d4d4d4; border-radius: 4px; font-size: 13px; }
input:focus, select:focus, textarea:focus { outline: none; border-color: #007acc; }
textarea { resize: vertical; min-height: 60px; font-family: inherit; }
.session-item { padding: 8px 12px; margin: 3px 0; background: #3c3c3c; border-radius: 4px; cursor: pointer; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
.session-item:hover { background: #454545; }
.session-item.active { background: #007acc; }
.session-badge { font-size: 10px; padding: 2px 6px; border-radius: 8px; background: rgba(255,255,255,0.15); }
.chat-box { height: 350px; overflow-y: auto; background: #1a1a1a; padding: 12px; border-radius: 6px; margin: 10px 0; border: 1px solid #333; }
.message { margin: 8px 0; padding: 10px 14px; border-radius: 10px; max-width: 85%; word-wrap: break-word; line-height: 1.5; }
.message.user { background: #0e639c; margin-left: auto; }
.message.ai { background: #3c3c3c; }
.message .role { font-size: 11px; color: #aaa; margin-bottom: 3px; }
.tabs { display: flex; gap: 2px; margin-bottom: 15px; border-bottom: 2px solid #3c3c3c; flex-wrap: wrap; }
.tab { padding: 8px 16px; cursor: pointer; border-radius: 4px 4px 0 0; color: #888; font-size: 13px; transition: all 0.2s; }
.tab:hover { color: #d4d4d4; background: #2a2d2e; }
.tab.active { color: #007acc; border-bottom: 2px solid #007acc; margin-bottom: -2px; }
.tab-content { display: none; flex: 1; }
.tab-content.active { display: block; }
.panel { background: #252526; border-radius: 6px; padding: 15px; margin-bottom: 15px; border: 1px solid #333; }
.param-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
.param-label { min-width: 140px; color: #aaa; font-size: 13px; }
.param-input { flex: 1; max-width: 200px; }
.trait-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #333; }
.trait-row:last-child { border-bottom: none; }
.trait-name { min-width: 70px; font-size: 13px; }
.trait-slider { flex: 1; max-width: 250px; }
.trait-value { min-width: 40px; text-align: center; font-size: 13px; color: #007acc; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.info-item { background: #3c3c3c; padding: 10px; border-radius: 4px; }
.info-label { font-size: 11px; color: #888; margin-bottom: 3px; }
.info-value { font-size: 14px; color: #d4d4d4; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.status-dot.running { background: #4ec9b0; }
.status-dot.stopped { background: #c42b1c; }
.chat-input-row { display: flex; gap: 8px; }
.chat-input-row textarea { flex: 1; }
.pref-item { display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: #3c3c3c; margin: 4px 0; border-radius: 4px; }
.pref-remove { color: #c42b1c; cursor: pointer; font-size: 16px; }
.empty-hint { color: #666; font-size: 13px; text-align: center; padding: 20px; }
.form-group { margin-bottom: 10px; }
.form-group label { display: block; font-size: 12px; color: #888; margin-bottom: 4px; }
.inline-form { display: flex; gap: 8px; align-items: end; }
.inline-form .form-group { flex: 1; margin-bottom: 0; }
.feature-toggle { display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #3c3c3c; margin: 5px 0; border-radius: 4px; }
.switch { position: relative; width: 44px; height: 24px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider-sw { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #555; border-radius: 24px; transition: 0.3s; }
.slider-sw:before { position: absolute; content: ''; height: 18px; width: 18px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.3s; }
.switch input:checked + .slider-sw { background: #007acc; }
.switch input:checked + .slider-sw:before { transform: translateX(20px); }
.scroll-area { max-height: 400px; overflow-y: auto; }
</style></head>
<body><div class="container">
<div class="sidebar">
<h1>千因 - 管理后台</h1>
<h2>会话管理</h2>
<div id="sessionList" class="scroll-area"><div class="empty-hint">加载中...</div></div>
<div style="display:flex;gap:5px;margin-top:8px;">
<button class="btn btn-sm" id="btnNewSession">新建</button>
<button class="btn btn-sm btn-warn" id="btnRenameSession">重命名</button>
<button class="btn btn-sm btn-danger" id="btnDelSession">删除</button>
</div>
<h2>服务器状态</h2>
<div id="statusInfo" class="panel" style="padding:10px;">加载中...</div>
</div>
<div class="main">
<div class="tabs">
<div class="tab active" data-tab="chat">对话</div>
<div class="tab" data-tab="train">训练</div>
<div class="tab" data-tab="personality">性格</div>
<div class="tab" data-tab="preferences">偏好</div>
<div class="tab" data-tab="info">模型信息</div>
<div class="tab" data-tab="weights">权重管理</div>
<div class="tab" data-tab="tokens">Token管理</div>
<div class="tab" data-tab="features">功能开关</div>
</div>

<div class="tab-content active" id="tab-chat">
<div class="chat-box" id="chatBox"></div>
<div class="chat-input-row">
<textarea id="chatInput" placeholder="输入消息... (Enter发送, Shift+Enter换行)" rows="2"></textarea>
<button class="btn" id="btnSend">发送</button>
</div>
<div style="margin-top:8px;">
<button class="btn btn-sm btn-danger" id="btnClearChat">清空对话</button>
</div>
</div>

<div class="tab-content" id="tab-train">
<div class="panel">
<h2>训练模型</h2>
<div class="form-group"><label>输入文本</label><textarea id="trainInput" rows="2" placeholder="用户输入"></textarea></div>
<div class="form-group"><label>期望回复</label><textarea id="trainResponse" rows="2" placeholder="AI应回复的内容"></textarea></div>
<div class="form-group"><label>训练模式</label>
<select id="trainMode">
<option value="refine">精炼训练 (对话式)</option>
<option value="full">完整训练 (逐字)</option>
<option value="intensive">强化训练 (重点)</option>
<option value="interactive">交互式训练 (对齐)</option>
</select></div>
<button class="btn btn-success" id="btnTrain">开始训练</button>
<div id="trainResult" style="margin-top:10px;"></div>
</div>
<div class="panel">
<h2>人类反馈训练</h2>
<div class="form-group"><label>原始输入</label><textarea id="fbInput" rows="1" placeholder="用户输入"></textarea></div>
<div class="form-group"><label>AI原始回复</label><textarea id="fbResponse" rows="1" placeholder="AI之前的回复"></textarea></div>
<div class="form-group"><label>评分</label>
<select id="fbRating"><option value="good">好</option><option value="neutral">中</option><option value="bad">差</option></select></div>
<div class="form-group"><label>修正后的回复 (可选)</label><textarea id="fbCorrected" rows="2" placeholder="正确的回复内容"></textarea></div>
<button class="btn btn-warn" id="btnFeedback">提交反馈</button>
<div id="fbResult" style="margin-top:10px;"></div>
</div>
</div>

<div class="tab-content" id="tab-personality">
<div class="panel">
<h2>性格设置</h2>
<div id="personalityList"></div>
</div>
</div>

<div class="tab-content" id="tab-preferences">
<div class="panel">
<h2>偏好设置</h2>
<div id="prefList"></div>
</div>
<div class="panel">
<h2>添加偏好</h2>
<div class="inline-form">
<div class="form-group"><label>类别</label>
<select id="prefCategory">
<option value="喜欢的话题">喜欢的话题</option>
<option value="偏好的回应风格">偏好的回应风格</option>
<option value="喜欢的词汇">喜欢的词汇</option>
<option value="厌恶的话题">厌恶的话题</option>
</select></div>
<div class="form-group"><label>内容</label><input id="prefItem" placeholder="偏好内容"></div>
</div>
<button class="btn" id="btnAddPref" style="margin-top:8px;">添加偏好</button>
</div>
</div>

<div class="tab-content" id="tab-info">
<div class="panel">
<h2>模型信息</h2>
<div class="info-grid" id="modelInfoGrid"></div>
</div>
<div class="panel">
<h2>学习统计</h2>
<div class="info-grid" id="statsGrid"></div>
</div>
</div>

<div class="tab-content" id="tab-weights">
<div class="panel">
<h2>模型保存与加载</h2>
<div class="form-group"><label>模型文件路径 (留空使用默认路径)</label><input id="modelPath" placeholder="例如: my_model.json"></div>
<div style="display:flex;gap:8px;">
<button class="btn btn-success" id="btnSaveModel">保存模型</button>
<button class="btn" id="btnLoadModel">加载模型</button>
</div>
<div id="modelSaveResult" style="margin-top:10px;"></div>
</div>
<div class="panel">
<h2>对话导出与导入</h2>
<button class="btn btn-sm" id="btnExportChat">导出对话</button>
<div style="margin-top:10px;">
<div class="form-group"><label>导入对话JSON</label><textarea id="importChatData" rows="3" placeholder='[{"input":"...","response":"..."}]'></textarea></div>
<button class="btn btn-sm" id="btnImportChat">导入对话</button>
</div>
<div id="chatExportResult" style="margin-top:10px;"></div>
</div>
</div>

<div class="tab-content" id="tab-tokens">
<div class="panel">
<h2>Token管理</h2>
<div class="info-grid" id="tokenGrid"></div>
</div>
<div class="panel">
<h2>充值/扣除Token</h2>
<div class="inline-form">
<div class="form-group"><label>数量 (正数充值, 负数扣除)</label><input id="tokenAmount" type="number" value="100"></div>
</div>
<button class="btn btn-success" id="btnUpdateTokens" style="margin-top:8px;">更新Token</button>
<div id="tokenUpdateResult" style="margin-top:10px;"></div>
</div>
</div>

<div class="tab-content" id="tab-features">
<div class="panel">
<h2>功能开关</h2>
<div id="featuresList"></div>
</div>
</div>

</div>
</div>
<script>
let sessions = [], currentSession = null, currentTab = 'chat';
const API = '/admin/api';

function api(path, opts) {
    return fetch(API + path, opts).then(r => r.json()).catch(e => ({error: e.message}));
}

async function loadSessions() {
    const data = await api('/sessions');
    sessions = data.sessions || [];
    if (!currentSession && sessions.length > 0) {
        currentSession = sessions[0];
    }
    renderSessions();
    if (currentSession) {
        await loadChat();
        await loadParams();
    }
}

function renderSessions() {
    const list = document.getElementById('sessionList');
    if (sessions.length === 0) {
        list.innerHTML = '<div class="empty-hint">暂无会话</div>';
        return;
    }
    list.innerHTML = '';
    sessions.forEach(s => {
        const div = document.createElement('div');
        div.className = 'session-item' + (s === currentSession ? ' active' : '');
        const span = document.createElement('span');
        span.textContent = s;
        div.appendChild(span);
        if (s === 'mtgchatgf') {
            const badge = document.createElement('span');
            badge.className = 'session-badge';
            badge.textContent = '默认';
            div.appendChild(badge);
        }
        div.onclick = () => switchSession(s);
        list.appendChild(div);
    });
}

async function switchSession(s) {
    currentSession = s;
    renderSessions();
    await loadChat();
    await loadParams();
    await loadTabData();
}

async function createSession() {
    const name = prompt('输入会话名称:');
    if (!name) return;
    const data = await api('/sessions', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({session_id:name})});
    if (data.error) { alert('错误: ' + data.error); return; }
    currentSession = name;
    await loadSessions();
}

async function renameSession() {
    if (!currentSession) { alert('请先选择会话'); return; }
    if (currentSession === 'mtgchatgf') { alert('无法重命名默认会话'); return; }
    const newName = prompt('输入新名称:', currentSession);
    if (!newName || newName === currentSession) return;
    const data = await api('/sessions/rename', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({old_name:currentSession, new_name:newName})});
    if (data.error) { alert('错误: ' + data.error); return; }
    currentSession = newName;
    await loadSessions();
}

async function deleteSession() {
    if (!currentSession) { alert('请先选择会话'); return; }
    if (currentSession === 'mtgchatgf') { alert('无法删除默认会话'); return; }
    if (!confirm('确定删除会话 ' + currentSession + '?')) return;
    const data = await api('/sessions/' + encodeURIComponent(currentSession), {method:'DELETE'});
    if (data.error) { alert('错误: ' + data.error); return; }
    currentSession = null;
    await loadSessions();
    if (sessions.length > 0) { currentSession = sessions[0]; await switchSession(currentSession); }
}

async function loadChat() {
    if (!currentSession) return;
    const data = await api('/chat/' + encodeURIComponent(currentSession));
    const box = document.getElementById('chatBox');
    box.innerHTML = '';
    const history = data.history || [];
    if (history.length === 0) {
        box.innerHTML = '<div class="empty-hint">暂无对话记录</div>';
        return;
    }
    history.forEach(msg => {
        if (msg.input) {
            const d = document.createElement('div');
            d.className = 'message user';
            d.innerHTML = '<div class="role">你</div>' + escapeHtml(msg.input);
            box.appendChild(d);
        }
        if (msg.response) {
            const d = document.createElement('div');
            d.className = 'message ai';
            d.innerHTML = '<div class="role">千因</div>' + escapeHtml(msg.response);
            box.appendChild(d);
        }
    });
    box.scrollTop = box.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage() {
    if (!currentSession) { alert('请先选择或创建会话'); return; }
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    const box = document.getElementById('chatBox');
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.innerHTML = '<div class="role">你</div>' + escapeHtml(text);
    box.appendChild(userMsg);
    box.scrollTop = box.scrollHeight;
    const data = await api('/chat/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({input:text})});
    const aiMsg = document.createElement('div');
    aiMsg.className = 'message ai';
    aiMsg.innerHTML = '<div class="role">千因</div>' + escapeHtml(data.response || data.error || '(无回复)');
    box.appendChild(aiMsg);
    box.scrollTop = box.scrollHeight;
}

async function clearChat() {
    if (!currentSession) return;
    if (!confirm('确定清空对话历史?')) return;
    await api('/clear/' + encodeURIComponent(currentSession), {method:'POST'});
    await loadChat();
}

async function loadParams() {
    if (!currentSession) return;
    const data = await api('/params/' + encodeURIComponent(currentSession));
    const sec = document.getElementById('tab-chat');
    let paramDiv = document.getElementById('paramSection');
    if (!paramDiv) {
        paramDiv = document.createElement('div');
        paramDiv.id = 'paramSection';
        paramDiv.className = 'panel';
        paramDiv.innerHTML = '<h2>动态参数配置</h2>';
        sec.appendChild(paramDiv);
    }
    let html = '<h2>动态参数配置</h2>';
    const paramNames = ['max_input_len','max_output_tokens','num_layers','dim','learning_rate','temperature','top_k','top_p'];
    paramNames.forEach(name => {
        if (data[name] !== undefined) {
            html += '<div class="param-row"><span class="param-label">' + name + ':</span>';
            html += '<input class="param-input" type="number" step="any" id="p_' + name + '" value="' + data[name] + '">';
            html += '<button class="btn btn-sm" onclick="updateParam(\\'' + name + '\\')">设置</button></div>';
        }
    });
    paramDiv.innerHTML = html;
}

async function updateParam(name) {
    const val = document.getElementById('p_' + name).value;
    const data = await api('/params/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({param:name, value:parseFloat(val)})});
    if (data.error) { alert('错误: ' + data.error); return; }
    alert('已更新: ' + name + ' = ' + val);
}

async function doTrain() {
    if (!currentSession) { alert('请先选择会话'); return; }
    const inp = document.getElementById('trainInput').value.trim();
    const resp = document.getElementById('trainResponse').value.trim();
    const mode = document.getElementById('trainMode').value;
    if (!inp || !resp) { alert('请填写输入和期望回复'); return; }
    const data = await api('/train/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({input:inp, response:resp, mode:mode})});
    const el = document.getElementById('trainResult');
    if (data.error) { el.innerHTML = '<span style="color:#c42b1c;">错误: ' + escapeHtml(data.error) + '</span>'; return; }
    el.innerHTML = '<span style="color:#4ec9b0;">训练成功! 输入Token: ' + (data.result ? data.result.input_tokens : '?') + ', 输出Token: ' + (data.result ? data.result.output_tokens : '?') + '</span>';
    document.getElementById('trainInput').value = '';
    document.getElementById('trainResponse').value = '';
}

async function doFeedback() {
    if (!currentSession) { alert('请先选择会话'); return; }
    const inp = document.getElementById('fbInput').value.trim();
    const resp = document.getElementById('fbResponse').value.trim();
    const rating = document.getElementById('fbRating').value;
    const corrected = document.getElementById('fbCorrected').value.trim() || null;
    if (!inp || !resp) { alert('请填写输入和AI回复'); return; }
    const data = await api('/feedback/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({input:inp, response:resp, rating:rating, corrected_response:corrected})});
    const el = document.getElementById('fbResult');
    if (data.error) { el.innerHTML = '<span style="color:#c42b1c;">错误: ' + escapeHtml(data.error) + '</span>'; return; }
    el.innerHTML = '<span style="color:#4ec9b0;">反馈已提交!</span>';
}

async function loadPersonality() {
    if (!currentSession) return;
    const data = await api('/personality/' + encodeURIComponent(currentSession));
    const list = document.getElementById('personalityList');
    const p = data.personality || {};
    list.innerHTML = '';
    Object.keys(p).forEach(trait => {
        const row = document.createElement('div');
        row.className = 'trait-row';
        row.innerHTML = '<span class="trait-name">' + trait + '</span>' +
            '<input type="range" class="trait-slider" min="0" max="1" step="0.05" value="' + p[trait] + '" ' +
            'oninput="this.nextElementSibling.textContent=this.value" ' +
            'onchange="setPersonality(\\'' + trait + '\\', this.value)">' +
            '<span class="trait-value">' + p[trait] + '</span>';
        list.appendChild(row);
    });
}

async function setPersonality(trait, value) {
    if (!currentSession) return;
    await api('/personality/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({trait:trait, value:parseFloat(value)})});
}

async function loadPreferences() {
    if (!currentSession) return;
    const data = await api('/preferences/' + encodeURIComponent(currentSession));
    const list = document.getElementById('prefList');
    const prefs = data.preferences || {};
    list.innerHTML = '';
    let hasItems = false;
    Object.keys(prefs).forEach(cat => {
        if (Array.isArray(prefs[cat])) {
            prefs[cat].forEach((item, i) => {
                hasItems = true;
                const div = document.createElement('div');
                div.className = 'pref-item';
                div.innerHTML = '<span><span class="session-badge">' + cat + '</span> ' + escapeHtml(item) + '</span>' +
                    '<span class="pref-remove" onclick="removePreference(\\'' + cat + '\\', ' + i + ')">&#x2715;</span>';
                list.appendChild(div);
            });
        } else {
            hasItems = true;
            const div = document.createElement('div');
            div.className = 'pref-item';
            div.innerHTML = '<span><span class="session-badge">' + cat + '</span> ' + escapeHtml(String(prefs[cat])) + '</span>';
            list.appendChild(div);
        }
    });
    if (!hasItems) list.innerHTML = '<div class="empty-hint">暂无偏好设置</div>';
}

async function addPreference() {
    if (!currentSession) { alert('请先选择会话'); return; }
    const cat = document.getElementById('prefCategory').value;
    const item = document.getElementById('prefItem').value.trim();
    if (!item) { alert('请输入偏好内容'); return; }
    const data = await api('/preferences/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({category:cat, item:item})});
    if (data.error) { alert('错误: ' + data.error); return; }
    document.getElementById('prefItem').value = '';
    await loadPreferences();
}

async function removePreference(cat, idx) {
    if (!currentSession) return;
    await api('/preferences/' + encodeURIComponent(currentSession) + '/remove', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({category:cat, index:idx})});
    await loadPreferences();
}

async function loadModelInfo() {
    if (!currentSession) return;
    const data = await api('/info/' + encodeURIComponent(currentSession));
    const grid = document.getElementById('modelInfoGrid');
    const statsGrid = document.getElementById('statsGrid');
    const info = data.info || {};
    const stats = info.learning_stats || {};
    grid.innerHTML = '';
    const infoItems = [
        ['模型名称', info.model_name], ['模型版本', info.model_version],
        ['网络层数', info.layers], ['维度', info.dim],
        ['Token量', info.token_count], ['当前对话数', info.conversation_count],
        ['总对话次数', info.total_conversations], ['总处理Token数', info.total_tokens_processed],
        ['因果位置', info.causal_position], ['最大输入长度', info.max_input_len]
    ];
    infoItems.forEach(([label, val]) => {
        const d = document.createElement('div');
        d.className = 'info-item';
        d.innerHTML = '<div class="info-label">' + label + '</div><div class="info-value">' + (val !== undefined && val !== null ? val : '-') + '</div>';
        grid.appendChild(d);
    });
    statsGrid.innerHTML = '';
    const statItems = [
        ['平均响应分数', stats['平均响应分数']], ['学习连续性', stats['学习连续性']],
        ['学会短语数', stats['学会短语数']], ['学会词汇数', stats['学会词汇数']]
    ];
    statItems.forEach(([label, val]) => {
        const d = document.createElement('div');
        d.className = 'info-item';
        d.innerHTML = '<div class="info-label">' + label + '</div><div class="info-value">' + (val !== undefined && val !== null ? val : '-') + '</div>';
        statsGrid.appendChild(d);
    });
}

async function saveModel() {
    if (!currentSession) { alert('请先选择会话'); return; }
    const path = document.getElementById('modelPath').value.trim();
    const body = path ? {path:path} : {};
    const data = await api('/save/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    const el = document.getElementById('modelSaveResult');
    if (data.error) { el.innerHTML = '<span style="color:#c42b1c;">错误: ' + escapeHtml(data.error) + '</span>'; return; }
    el.innerHTML = '<span style="color:#4ec9b0;">模型已保存: ' + escapeHtml(data.path || '') + '</span>';
}

async function loadModel() {
    if (!currentSession) { alert('请先选择会话'); return; }
    const path = document.getElementById('modelPath').value.trim();
    const body = path ? {path:path} : {};
    const data = await api('/load/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    const el = document.getElementById('modelSaveResult');
    if (data.error) { el.innerHTML = '<span style="color:#c42b1c;">错误: ' + escapeHtml(data.error) + '</span>'; return; }
    el.innerHTML = '<span style="color:#4ec9b0;">模型已加载: ' + escapeHtml(data.path || '') + '</span>';
    await loadTabData();
}

async function exportChat() {
    if (!currentSession) { alert('请先选择会话'); return; }
    const data = await api('/export/' + encodeURIComponent(currentSession));
    const el = document.getElementById('chatExportResult');
    if (data.error) { el.innerHTML = '<span style="color:#c42b1c;">错误: ' + escapeHtml(data.error) + '</span>'; return; }
    const json = JSON.stringify(data.history || [], null, 2);
    el.innerHTML = '<span style="color:#4ec9b0;">已导出 ' + (data.history || []).length + ' 条对话</span><pre style="margin-top:8px;background:#1a1a1a;padding:10px;border-radius:4px;max-height:200px;overflow:auto;font-size:12px;">' + escapeHtml(json) + '</pre>';
}

async function importChat() {
    if (!currentSession) { alert('请先选择会话'); return; }
    const rawData = document.getElementById('importChatData').value.trim();
    if (!rawData) { alert('请输入对话JSON数据'); return; }
    let chatHistory;
    try { chatHistory = JSON.parse(rawData); } catch(e) { alert('JSON格式错误: ' + e.message); return; }
    const data = await api('/import/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({chat_history:chatHistory})});
    const el = document.getElementById('chatExportResult');
    if (data.error) { el.innerHTML = '<span style="color:#c42b1c;">错误: ' + escapeHtml(data.error) + '</span>'; return; }
    el.innerHTML = '<span style="color:#4ec9b0;">对话已导入</span>';
    await loadChat();
}

async function loadTokens() {
    if (!currentSession) return;
    const data = await api('/tokens/' + encodeURIComponent(currentSession));
    const grid = document.getElementById('tokenGrid');
    const t = data.tokens || {};
    grid.innerHTML = '';
    const items = [
        ['API密钥', t.api_key || '未分配'], ['Token余额', t.is_free ? '无限制' : (t.tokens !== undefined ? t.tokens : '-')],
        ['是否免费', t.is_free ? '是' : '否'], ['Token使用量', t.usage || 0],
        ['创建时间', t.created_at || '-'], ['会话ID', currentSession]
    ];
    items.forEach(([label, val]) => {
        const d = document.createElement('div');
        d.className = 'info-item';
        d.innerHTML = '<div class="info-label">' + label + '</div><div class="info-value" style="word-break:break-all;">' + escapeHtml(String(val)) + '</div>';
        grid.appendChild(d);
    });
}

async function updateTokens() {
    if (!currentSession) { alert('请先选择会话'); return; }
    const amount = parseInt(document.getElementById('tokenAmount').value) || 0;
    const data = await api('/tokens/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({amount:amount})});
    const el = document.getElementById('tokenUpdateResult');
    if (data.error) { el.innerHTML = '<span style="color:#c42b1c;">错误: ' + escapeHtml(data.error) + '</span>'; return; }
    el.innerHTML = '<span style="color:#4ec9b0;">已更新! 新余额: ' + (data.new_balance !== undefined ? data.new_balance : '?') + '</span>';
    await loadTokens();
}

async function loadFeatures() {
    if (!currentSession) return;
    const data = await api('/features/' + encodeURIComponent(currentSession));
    const list = document.getElementById('featuresList');
    const f = data.features || {};
    list.innerHTML = '';
    const featureNames = {'auto_full_save':'自动全量保存', 'auto_compress':'自动压缩(LZ4)'};
    Object.keys(f).forEach(name => {
        const div = document.createElement('div');
        div.className = 'feature-toggle';
        div.innerHTML = '<span>' + (featureNames[name] || name) + '</span>' +
            '<label class="switch"><input type="checkbox" ' + (f[name] ? 'checked' : '') + ' ' +
            'onchange="setFeature(\\'' + name + '\\', this.checked)"><span class="slider-sw"></span></label>';
        list.appendChild(div);
    });
}

async function setFeature(name, enabled) {
    if (!currentSession) return;
    await api('/features/' + encodeURIComponent(currentSession), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({feature:name, enabled:enabled})});
}

async function loadStatus() {
    const data = await api('/status');
    const el = document.getElementById('statusInfo');
    const apiRunning = data.api_running;
    const cjslRunning = data.cjsl_running;
    el.innerHTML = '<div style="margin-bottom:5px;"><span class="status-dot ' + (apiRunning ? 'running' : 'stopped') + '"></span>API (' + data.api_port + ')</div>' +
        '<div style="margin-bottom:5px;"><span class="status-dot ' + (cjslRunning ? 'running' : 'stopped') + '"></span>CISL (' + data.cjsl_port + ')</div>' +
        '<div style="margin-bottom:5px;"><span class="status-dot running"></span>管理后台 (' + data.admin_port + ')</div>' +
        '<div style="margin-top:8px;font-size:12px;color:#888;">实例数: ' + data.instances + '</div>' +
        '<div style="font-size:12px;color:#888;">当前会话: ' + (currentSession || '无') + '</div>';
}

function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === 'tab-' + tab));
    loadTabData();
}

async function loadTabData() {
    if (!currentSession) return;
    if (currentTab === 'personality') await loadPersonality();
    else if (currentTab === 'preferences') await loadPreferences();
    else if (currentTab === 'info') await loadModelInfo();
    else if (currentTab === 'tokens') await loadTokens();
    else if (currentTab === 'features') await loadFeatures();
}

window.sendMessage = sendMessage;
window.updateParam = updateParam;
window.setPersonality = setPersonality;
window.removePreference = removePreference;
window.setFeature = setFeature;
window.switchTab = switchTab;

document.querySelectorAll('.tab').forEach(t => t.onclick = () => switchTab(t.dataset.tab));
document.getElementById('btnNewSession').onclick = createSession;
document.getElementById('btnRenameSession').onclick = renameSession;
document.getElementById('btnDelSession').onclick = deleteSession;
document.getElementById('btnSend').onclick = sendMessage;
document.getElementById('btnClearChat').onclick = clearChat;
document.getElementById('btnTrain').onclick = doTrain;
document.getElementById('btnFeedback').onclick = doFeedback;
document.getElementById('btnAddPref').onclick = addPreference;
document.getElementById('btnSaveModel').onclick = saveModel;
document.getElementById('btnLoadModel').onclick = loadModel;
document.getElementById('btnExportChat').onclick = exportChat;
document.getElementById('btnImportChat').onclick = importChat;
document.getElementById('btnUpdateTokens').onclick = updateTokens;

document.getElementById('chatInput').addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

loadSessions();
setInterval(loadStatus, 5000);
</script></body></html>'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _handle_api(self):
        path = self.path.replace('/admin/api/', '')
        parts = [unquote(p) for p in path.split('/')]
        action = parts[0]
        if action == 'sessions':
            self._api_sessions(parts[1:] if len(parts) > 1 else [])
        elif action == 'chat':
            self._api_chat(parts[1] if len(parts) > 1 else None)
        elif action == 'params':
            self._api_params(parts[1] if len(parts) > 1 else None)
        elif action == 'personality':
            self._api_personality(parts[1] if len(parts) > 1 else None)
        elif action == 'preferences':
            self._api_preferences(parts[1:] if len(parts) > 1 else [])
        elif action == 'train':
            self._api_train(parts[1] if len(parts) > 1 else None)
        elif action == 'feedback':
            self._api_feedback(parts[1] if len(parts) > 1 else None)
        elif action == 'info':
            self._api_info(parts[1] if len(parts) > 1 else None)
        elif action == 'save':
            self._api_save(parts[1] if len(parts) > 1 else None)
        elif action == 'load':
            self._api_load(parts[1] if len(parts) > 1 else None)
        elif action == 'clear':
            self._api_clear(parts[1] if len(parts) > 1 else None)
        elif action == 'export':
            self._api_export(parts[1] if len(parts) > 1 else None)
        elif action == 'import':
            self._api_import(parts[1] if len(parts) > 1 else None)
        elif action == 'features':
            self._api_features(parts[1] if len(parts) > 1 else None)
        elif action == 'tokens':
            self._api_tokens(parts[1] if len(parts) > 1 else None)
        elif action == 'status':
            self._api_status()
        else:
            self._json({"error": "unknown endpoint"}, 404)

    def _get_model(self, sid):
        """根据会话ID获取模型"""
        if not sid:
            return None
        return self.server.admin_sessions.get(sid)

    def _get_api_key_for_session(self, sid):
        """根据会话ID获取关联的API Key"""
        for api_key, key_data in self.server.api_server.api_keys.items():
            if key_data.get("session_id") == sid:
                return api_key
        return None

    def _api_sessions(self, parts):
        if self.command == 'GET':
            sessions = list(self.server.admin_sessions.keys())
            self._json({"sessions": sessions})
        elif self.command == 'POST':
            if parts and parts[0] == 'rename':
                self._api_rename()
                return
            body = self._read_body()
            if body is None:
                return
            sid = body.get('session_id', f'session_{len(self.server.admin_sessions) + 1}')
            if sid in self.server.admin_sessions:
                self._json({"error": "session already exists"}, 400)
                return
            api_key, session_id = self.server.api_server.add_instance(sid)
            self._json({"status": "created", "session_id": session_id, "api_key": api_key})
        elif self.command == 'DELETE' and len(parts) >= 1:
            sid = parts[0]
            if sid == 'mtgchatgf':
                self._json({"error": "cannot delete default session"}, 400)
                return
            api_key = self._get_api_key_for_session(sid)
            if api_key:
                success = self.server.api_server.delete_instance(api_key)
                if success:
                    self._json({"status": "deleted"})
                else:
                    self._json({"error": "delete failed"}, 400)
            else:
                self._json({"error": "session not found"}, 404)

    def _api_rename(self):
        body = self._read_body()
        if body is None:
            return
        old_name = body.get('old_name', '')
        new_name = body.get('new_name', '')
        if not old_name or not new_name:
            self._json({"error": "missing old_name or new_name"}, 400)
            return
        if old_name == 'mtgchatgf':
            self._json({"error": "cannot rename default session"}, 400)
            return
        api_key = self._get_api_key_for_session(old_name)
        if not api_key:
            self._json({"error": "session not found"}, 404)
            return
        success = self.server.api_server.rename_instance(api_key, new_name)
        if success:
            self._json({"status": "renamed", "new_name": new_name})
        else:
            self._json({"error": "rename failed (name may already exist)"}, 400)

    def _api_chat(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'GET':
            self._json({"history": model.context_chain[-50:]})
        elif self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            inp = body.get('input', '')
            out = body.get('max_output_tokens', model.dynamic_params.get('max_output_tokens', 200))
            try:
                result = model.chat(inp, max_output_tokens=out)
                self._json(result)
            except Exception as e:
                self._json({"error": str(e)}, 500)

    def _api_params(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'GET':
            self._json(model.dynamic_params)
        elif self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            p, v = body.get('param'), body.get('value')
            if p in model.dynamic_params:
                model.dynamic_params[p] = float(v)
                if p == 'max_input_len':
                    model.max_input_len = int(v)
                self._json({"status": "updated", p: v})
            else:
                self._json({"error": f"unknown param: {p}"}, 400)

    def _api_personality(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'GET':
            self._json({"personality": model.get_personality()})
        elif self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            trait = body.get('trait', '')
            value = body.get('value', 0.5)
            model.set_personality_trait(trait, value)
            self._json({"status": "success"})

    def _api_preferences(self, parts):
        if not parts:
            self._json({"error": "missing session id"}, 400)
            return
        sid = parts[0]
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'GET':
            self._json({"preferences": model.get_preferences()})
        elif self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            if len(parts) > 1 and parts[1] == 'remove':
                category = body.get('category', '')
                index = body.get('index', -1)
                prefs = model.get_preferences()
                if category in prefs and isinstance(prefs[category], list):
                    if 0 <= index < len(prefs[category]):
                        prefs[category].pop(index)
                        self._json({"status": "removed"})
                    else:
                        self._json({"error": "index out of range"}, 400)
                else:
                    self._json({"error": "category not found or not a list"}, 400)
            else:
                category = body.get('category', '')
                item = body.get('item', '')
                model.add_preference(category, item)
                self._json({"status": "success"})

    def _api_train(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            user_input = body.get('input', '')
            response = body.get('response', '')
            mode = body.get('mode', 'refine')
            try:
                result = model.train(user_input, response, mode)
                self._json({"result": result})
            except Exception as e:
                self._json({"error": str(e)}, 500)

    def _api_feedback(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            user_input = body.get('input', '')
            ai_response = body.get('response', '')
            rating = body.get('rating', 'neutral')
            corrected = body.get('corrected_response', None)
            try:
                result = model.human_feedback(user_input, ai_response, rating, corrected)
                self._json({"result": result})
            except Exception as e:
                self._json({"error": str(e)}, 500)

    def _api_info(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'GET':
            token_count = len(model.tokenizer.char_to_token) + len(model.tokenizer.subword_to_token)
            info = {
                "model_name": model.model_name,
                "model_version": model.model_version,
                "layers": model.num_layers,
                "dim": model.semantic.dim if hasattr(model.semantic, 'dim') else 4096,
                "token_count": token_count,
                "conversation_count": len(model.context_chain),
                "total_conversations": model.total_conversations,
                "total_tokens_processed": model.total_tokens_processed,
                "causal_position": model.causal_position,
                "max_input_len": model.max_input_len,
                "learning_stats": model.get_learning_stats(),
                "personality": model.get_personality(),
                "preferences": model.get_preferences(),
                "features": model.get_features()
            }
            self._json({"info": info})

    def _api_save(self, sid):
        if not sid:
            self._json({"error": "missing session id"}, 400)
            return
        model = self._get_model(sid)
        if not model:
            self._json({"error": "session not found"}, 404)
            return
        body = self._read_body() if self.command == 'POST' else {}
        if body is None:
            return
        path = body.get('path', os.path.join(SCRIPT_DIR, f"{sid}.model.json"))
        validated = _validate_path(path)
        if validated is None:
            self._json({"error": "invalid path"}, 400)
            return
        try:
            model.save_model(validated)
            self._json({"status": "saved", "path": validated})
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _api_load(self, sid):
        if not sid:
            self._json({"error": "missing session id"}, 400)
            return
        model = self._get_model(sid)
        if not model:
            self._json({"error": "session not found"}, 404)
            return
        body = self._read_body() if self.command == 'POST' else {}
        if body is None:
            return
        path = body.get('path', os.path.join(SCRIPT_DIR, f"{sid}.model.json"))
        validated = _validate_path(path)
        if validated is None:
            self._json({"error": "invalid path"}, 400)
            return
        try:
            model.load_model(validated)
            self._json({"status": "loaded", "path": validated})
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _api_clear(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'POST':
            model.context_chain = []
            self._json({"status": "cleared"})

    def _api_export(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'GET':
            self._json({"history": model.context_chain[-200:]})

    def _api_import(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            chat_history = body.get('chat_history', [])
            model.context_chain.extend(chat_history)
            if len(model.context_chain) > model.max_context_len:
                model.context_chain = model.context_chain[-model.max_context_len:]
            self._json({"status": "success", "total": len(model.context_chain)})

    def _api_features(self, sid):
        model = self._get_model(sid)
        if not model:
            self._json({"error": "invalid session"}, 400)
            return
        if self.command == 'GET':
            self._json({"features": model.get_features()})
        elif self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            feature = body.get('feature', '')
            enabled = body.get('enabled', None)
            result = model.set_feature(feature, enabled)
            self._json({"result": result})

    def _api_tokens(self, sid):
        if not sid:
            self._json({"error": "missing session id"}, 400)
            return
        api_key = self._get_api_key_for_session(sid)
        if not api_key:
            self._json({"error": "no api key for session"}, 404)
            return
        key_data = self.server.api_server.api_keys.get(api_key, {})
        if self.command == 'GET':
            self._json({"tokens": {
                "api_key": api_key,
                "tokens": key_data.get("tokens", 0),
                "is_free": key_data.get("is_free", False),
                "usage": self.server.api_server.token_usage.get(api_key, 0),
                "created_at": key_data.get("created_at", "")
            }})
        elif self.command == 'POST':
            body = self._read_body()
            if body is None:
                return
            amount = body.get('amount', 0)
            new_balance = self.server.api_server.update_tokens(api_key, amount)
            self._json({"new_balance": new_balance})

    def _api_status(self):
        self._json({
            "instances": len(self.server.admin_sessions),
            "sessions": list(self.server.admin_sessions.keys()),
            "api_running": True,
            "cjsl_running": True,
            "api_port": getattr(self.server.api_server, 'server_address', [None, 4000])[1],
            "cjsl_port": getattr(self.server.cjsl_server, 'server_address', [None, 9000])[1] if self.server.cjsl_server else 9000,
            "admin_port": self.server.server_address[1]
        })

    def _read_body(self, max_size=MAX_BODY_SIZE):
        """读取请求体，带大小限制"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > max_size:
                self._json({"error": "request body too large"}, 413)
                return None
            if content_length > 0:
                body = self.rfile.read(content_length).decode("utf-8")
                return json.loads(body)
            return {}
        except json.JSONDecodeError:
            self._json({"error": "invalid JSON"}, 400)
            return None
        except Exception as e:
            self._json({"error": str(e)}, 500)
            return None

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        pass



class CJSLServer(IPv6HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, llm_server):
        super().__init__(server_address, RequestHandlerClass)
        self.llm_server = llm_server




def main():
    config = load_config()
    if not os.path.exists(config.get("weights_path", SCRIPT_DIR)):
        try:
            os.makedirs(config.get("weights_path", SCRIPT_DIR))
        except:
            pass
    lang = config.get("language", "zh")
    load_language(lang)

    default_model = LightweightMultiLayerLLM()
    save_path_lz4 = os.path.join(SCRIPT_DIR, "mtgchatgf.model.json.lz4")
    save_path_gz = os.path.join(SCRIPT_DIR, "mtgchatgf.model.json.gz")
    save_path_json = os.path.join(SCRIPT_DIR, "mtgchatgf.model.json")
    if os.path.exists(save_path_lz4):
        default_model.load_model(save_path_lz4)
    elif os.path.exists(save_path_gz):
        default_model.load_model(save_path_gz)
    elif os.path.exists(save_path_json):
        default_model.load_model(save_path_json)
    snapshot_path = os.path.join(SCRIPT_DIR, "model.snapshot.json.gz")
    if os.path.exists(snapshot_path):
        try:
            default_model.load_snapshot(snapshot_path)
        except:
            pass

    default_model.train("你好", "你好！有什么可以帮您？", "standard")

    api_port = config.get("port", config.get("api_port", 4000))
    cjsl_port = config.get("cjsl_port", 9000)
    admin_port = config.get("admin_port", 8080)

    llm_server = LLMServer(("::", api_port), LLMAPIHandler)
    # 直接使用已加载权重的 default_model 作为 mtgchatgf 实例
    llm_server.sessions["mtgchatgf"] = default_model
    llm_server.api_keys["mtgchatgf"] = {
        "session_id": "mtgchatgf",
        "tokens": -1,
        "is_free": True,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    llm_server.api_server = llm_server

    cjsl_server = CJSLServer(("::", cjsl_port), CISLAPIHandler, llm_server)

    threading.Thread(target=llm_server.serve_forever, daemon=True).start()
    threading.Thread(target=cjsl_server.serve_forever, daemon=True).start()
    print(f"[MTG AI V-Causal 2.26] API Server: [::]:{api_port}")
    print(f"[MTG AI V-Causal 2.26] CISL Server: [::]:{cjsl_port} (免费, 无鉴权)")
    print("[MTG AI V-Causal 2.26] 默认实例: mtgchatgf")

    try:
        admin_server = IPv6HTTPServer(("::", admin_port), WebAdminHandler)
        admin_server.admin_sessions = llm_server.sessions
        admin_server.api_server = llm_server
        admin_server.cjsl_server = cjsl_server
        threading.Thread(target=admin_server.serve_forever, daemon=True).start()
        print(f"[MTG AI V-Causal 2.26] Web管理界面: http://[::]:{admin_port}/admin")
    except Exception as e:
        print(f"[MTG AI V-Causal 2.26] Web管理界面启动失败: {e}")
    print("[MTG AI V-Causal 2.26] 按 Ctrl+C 退出")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MTG AI V-Causal 2.26] 正在关闭...")
        llm_server.shutdown()
        cjsl_server.shutdown()
        try:
            admin_server.shutdown()
        except:
            pass


if __name__ == "__main__":
    main()