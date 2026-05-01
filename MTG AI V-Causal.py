import sys
import os
import json
import random
import re
import threading
import secrets
import math
import unicodedata
from collections import defaultdict, OrderedDict
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import time
import traceback

CONFIG_FILE = "config.json"
WEIGHTS_INFO_FILE = "weights_info.json"
LOG_FILE = "mtg_ai_errors.log"
LANG_FILE = "language.json"
API_KEYS_FILE = "api_keys.json"

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

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            return json.load(open(CONFIG_FILE, "r", encoding="utf-8"))
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    return {
        "weights_path": os.path.expanduser("~/llm_weights"),
        "port": 4000,
        "cjsl_port": 9000,
        "dim": 4096,
        "default_api": "mtgchatgf",
        "language": "zh",
        "current_session": "default",
        "window_geometry": "1400x850"
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
    def __init__(self, dim=4096):
        self.dim = dim
        self.word_vec = {}
        self.lr = 0.05
    def encode(self, word):
        if word not in self.word_vec:
            self.word_vec[word] = [random.gauss(0, 0.1) for _ in range(self.dim)]
        return self.word_vec[word]
    def update(self, word, grad):
        if word in self.word_vec:
            for i in range(self.dim):
                self.word_vec[word][i] += grad * self.lr
                self.word_vec[word][i] = max(-1.0, min(1.0, self.word_vec[word][i]))
    def similarity(self, w1, w2):
        v1 = self.encode(w1)
        v2 = self.encode(w2)
        return sum(a*b for a,b in zip(v1,v2))

class QKVSerialAttention:
    def __init__(self, dim=4096):
        self.dim = dim
        self.Wq = [random.gauss(0,0.1) for _ in range(dim)]
        self.Wk = [random.gauss(0,0.1) for _ in range(dim)]
        self.Wv = [random.gauss(0,0.1) for _ in range(dim)]
    def score(self, vec):
        q = sum(v*w for v,w in zip(vec, self.Wq))
        k = sum(v*w for v,w in zip(vec, self.Wk))
        v = sum(v*w for v,w in zip(vec, self.Wv))
        return (q * k) / math.sqrt(self.dim)

def softmax(scores):
    if not scores:
        return []
    max_s = max(scores)
    ex = [math.exp(s - max_s) for s in scores]
    sum_ex = sum(ex)
    return [e / sum_ex for e in ex] if sum_ex != 0 else [0.0]*len(scores)

class UnicodeTokenizer:
    def __init__(self):
        self.char_to_token = {}
        self.token_to_char = {}
        self.subword_to_token = {}
        self.token_to_subword = {}
        self._next_token_id = 1
        self._next_subword_id = 1
        self.max_subword_len = 4
        
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
        subword = text[start:start+length]
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
                ngram = text[i:i+n]
                key = f"input_{n}gram"
                if ngram not in self.phrase_patterns[key]:
                    self.phrase_patterns[key].append(ngram)
            for i in range(len(response) - n + 1):
                ngram = response[i:i+n]
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
    def __init__(self, num_layers=24, max_input_len=200, max_states=5000):
        self.num_layers = num_layers
        self.attention_matrices = [defaultdict(lambda: defaultdict(float)) for _ in range(num_layers)]
        self.state_to_text = {}
        self.text_to_state = {}
        self.lru_cache = OrderedDict()
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
        self.tokenizer = UnicodeTokenizer()
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

    def _lru_access(self, state_id):
        if state_id in self.lru_cache:
            self.lru_cache.move_to_end(state_id)
        else:
            if len(self.lru_cache) >= self.max_states:
                self.lru_cache.popitem(last=False)
            self.lru_cache[state_id] = True

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
        if len(text) > self.max_input_len:
            text = text[:self.max_input_len]
        tokens = self.tokenizer.tokenize(text)
        script_type = self._detect_script(text)
        core_tokens = tokens[:5]
        sem = self.semantic.encode(' '.join(core_tokens))
        state_id = f"state_{hash((''.join(core_tokens), tuple(sem), script_type))}"
        if state_id not in self.state_to_text:
            self.text_to_state[text.strip()] = state_id
            self.state_to_text[state_id] = text.strip()
            if len(self.learned_vocab) < self.max_vocab_size:
                for word in core_tokens:
                    if word.startswith('s') and word not in self.learned_vocab:
                        decoded = self.tokenizer.token_to_subword.get(int(word[1:]), word)
                        if decoded not in self.learned_vocab:
                            self.learned_vocab.append(decoded)
        self._lru_access(state_id)
        return state_id

    def multi_layer_inference(self, start_state, context_states):
        reasoning_path = []
        current_state = start_state
        reasoning_path.append(current_state)
        self.causal_position = 0
        self._lru_access(current_state)
        
        context_semantics = []
        for ctx in context_states:
            if ctx in self.state_to_text:
                text = self.state_to_text[ctx]
                vec = self.semantic.encode(text)
                context_semantics.append((ctx, text, vec))
        
        for layer_idx in range(self.num_layers):
            self.causal_position += 1
            if random.random() < self.layer_dropout:
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
                transitions = sorted(layer_matrix[current_state].items(), key=lambda x: x[1], reverse=True)[:3]
                if transitions:
                    if len(transitions) > 1 and random.random() < 0.3:
                        next_state = transitions[1][0]
                    else:
                        next_state = transitions[0][0]
                    reasoning_path.append(next_state)
                    self._lru_access(next_state)
                    current_state = next_state
                    continue
            
            if current_state not in layer_matrix or len(layer_matrix[current_state]) == 0:
                new_state = f"state_{len(self.state_to_text)}"
                if context_semantics:
                    similar_ctx = max(context_semantics, key=lambda x: self.semantic.similarity(current_text, x[1]))
                    vocab_pool = self.base_vocab + self.learned_vocab[:100]
                    if vocab_pool:
                        related_words = [w for w in vocab_pool if w in similar_ctx[1]]
                        if related_words:
                            new_text = random.choice(related_words)
                        else:
                            new_text = random.choice(vocab_pool) if vocab_pool else "响应"
                    else:
                        new_text = "响应"
                    self.state_to_text[new_state] = new_text
                else:
                    vocab_pool = self.base_vocab + self.learned_vocab[:100]
                    self.state_to_text[new_state] = random.choice(vocab_pool) if vocab_pool else "响应"
                layer_matrix[current_state][new_state] = 0.3
                reasoning_path.append(new_state)
                self._lru_access(new_state)
                current_state = new_state
            else:
                transitions = sorted(layer_matrix[current_state].items(), key=lambda x: x[1], reverse=True)[:3]
                if len(transitions) > 1 and random.random() < 0.3:
                    next_state = transitions[1][0]
                else:
                    next_state = transitions[0][0]
                reasoning_path.append(next_state)
                self._lru_access(next_state)
                current_state = next_state
        return reasoning_path

    def _detect_user_sentiment(self, user_input):
        positive_indicators = ["好", "棒", "喜欢", "谢谢", "开心", "高兴", "不错", "完美", "赞", "good", "great", "thanks", "nice", "love"]
        negative_indicators = ["不", "没", "讨厌", "差", "糟糕", "麻烦", "问题", "困难", "bad", "hate", "terrible", "awful", "wrong", "issue"]
        score = 0
        lower_input = user_input.lower()
        for word in positive_indicators:
            if word in user_input or word in lower_input:
                score += 1
        for word in negative_indicators:
            if word in user_input or word in lower_input:
                score -= 1
        if score > 0:
            return "positive"
        elif score < 0:
            return "negative"
        return "neutral"

    def decode_response(self, reasoning_path, user_input, sentiment):
        if not reasoning_path:
            return ""
        tokens = []
        for s in reasoning_path:
            if s in self.state_to_text:
                tokens.append(self.state_to_text[s])
        if not tokens:
            return ""
        
        user_words = set(user_input.split())
        filtered_tokens = [t for t in tokens if t.strip() and t not in user_words and len(t.strip()) > 0]
        if not filtered_tokens:
            filtered_tokens = [t for t in tokens if t.strip()]
        if not filtered_tokens:
            return ""
        
        learned_phrases = self.phrase_learner.get_learned_phrases(3)
        if learned_phrases and random.random() < 0.6:
            relevant_phrases = []
            for phrase in learned_phrases[:20]:
                if any(word in phrase for word in user_words):
                    relevant_phrases.append(phrase)
            if relevant_phrases:
                phrase = random.choice(relevant_phrases)
                return self.personality_reward.adjust_personality_response(phrase, sentiment)
            else:
                phrase = random.choice(learned_phrases[:10])
                return self.personality_reward.adjust_personality_response(phrase, sentiment)
        
        response = self._build_coherent_response(filtered_tokens, sentiment)
        response = self.personality_reward.adjust_personality_response(response, sentiment)
        
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
        for layer in self.attention_matrices:
            for s in layer:
                for n in layer[s]:
                    layer[s][n] *= self.weight_decay
                    layer[s][n] -= self.punishment_rate
                    if layer[s][n] < 0.01:
                        layer[s][n] = 0.01

    def update_weights(self, reasoning_path, user_input, response):
        limited_path = [s for s in reasoning_path if s in self.state_to_text]
        if len(limited_path) < 2:
            return
        sentiment = self._detect_user_sentiment(user_input)
        self.phrase_learner.learn_from_text(user_input, response)
        is_good = self.personality_reward.apply_reward(response, sentiment)
        lr_multiplier = 1.0
        if is_good:
            lr_multiplier = 1.2
            self.consecutive_correct += 1
            self.learning_streak += 1
        else:
            self.consecutive_correct = 0
            self.learning_streak = max(0, self.learning_streak - 1)
        if self.consecutive_correct > 3:
            lr_multiplier = 0.8
        if self.adaptive_lr:
            for key in self.gradient_history:
                self.gradient_history[key] *= self.learning_momentum
        for layer_idx in range(self.num_layers):
            layer_matrix = self.attention_matrices[layer_idx]
            for i in range(len(limited_path)-1):
                s_from = limited_path[i]
                s_to = limited_path[i+1]
                grad_key = f"{layer_idx}_{s_from}_{s_to}"
                if s_from not in layer_matrix:
                    layer_matrix[s_from] = defaultdict(float)
                wd = self.weight_decay
                for k in layer_matrix[s_from]:
                    layer_matrix[s_from][k] *= wd
                adjusted_lr = self.learning_rate * lr_multiplier
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
        sentiment = self._detect_user_sentiment(user_input)
        start_state = self.token_to_state(user_input)
        context_states = []
        for item in self.context_chain[-10:]:
            s = self.token_to_state(item["input"])
            if s in self.state_to_text:
                context_states.append(s)
        reasoning_path = self.multi_layer_inference(start_state, context_states)
        
        if mode == "full":
            self.phrase_learner.learn_from_text(user_input, response)
            self.update_weights(reasoning_path, user_input, response)
        elif mode == "intensive":
            self.phrase_learner.learn_from_text(user_input, response)
            self.update_weights(reasoning_path, user_input, response)
            key_phrases = self._extract_key_phrases(user_input)
            for phrase in key_phrases:
                self.phrase_learner.learn_from_text(phrase, response, weight=2.0)
            for layer_idx in range(self.num_layers):
                layer_matrix = self.attention_matrices[layer_idx]
                limited_path = [s for s in reasoning_path if s in self.state_to_text]
                for i in range(len(limited_path)-1):
                    s_from = limited_path[i]
                    s_to = limited_path[i+1]
                    if s_from in layer_matrix and s_to in layer_matrix[s_from]:
                        layer_matrix[s_from][s_to] *= 1.5
                        total = sum(layer_matrix[s_from].values()) + 1e-6
                        for k in layer_matrix[s_from]:
                            layer_matrix[s_from][k] /= total
        elif mode == "interactive":
            self.phrase_learner.learn_from_text(user_input, response)
            self.update_weights(reasoning_path, user_input, response)
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
        else:
            key_phrases = self._extract_key_phrases(user_input)
            for phrase in key_phrases:
                self.phrase_learner.learn_from_text(phrase, response)
            self.update_weights(reasoning_path, user_input, response)
        
        self.context_chain.append({"input": user_input, "state": start_state, "response": response})
        if len(self.context_chain) > self.max_context_len:
            self.context_chain.pop(0)
        
        return {"status": "success", "mode": mode, "input_tokens": len(self.tokenizer.tokenize(user_input)), "output_tokens": len(self.tokenizer.tokenize(response))}
    
    def _extract_key_phrases(self, text):
        phrases = []
        words = text.split()
        for i in range(len(words)):
            if len(words[i]) > 1:
                phrases.append(words[i])
            if i < len(words) - 1:
                two_word = f"{words[i]} {words[i+1]}"
                phrases.append(two_word)
        return phrases[:5]

    def chat(self, user_input):
        if not user_input.strip():
            return {
                "user_input": user_input,
                "response": "",
                "input_tokens": 0,
                "output_tokens": 0,
                "sentiment": "neutral"
            }
        sentiment = self._detect_user_sentiment(user_input)
        start_state = self.token_to_state(user_input)
        context_states = []
        for item in self.context_chain[-10:]:
            s = self.token_to_state(item["input"])
            if s in self.state_to_text:
                context_states.append(s)
        reasoning_path = self.multi_layer_inference(start_state, context_states)
        response = self.decode_response(reasoning_path, user_input, sentiment)
        self.punish()
        self.context_chain.append({"input": user_input, "state": start_state, "response": response})
        if len(self.context_chain) > self.max_context_len:
            self.context_chain.pop(0)
        self.update_weights(reasoning_path, user_input, response)
        self._update_user_understanding(user_input, response, sentiment)
        input_tokens = len(self.tokenizer.tokenize(user_input))
        output_tokens = len(self.tokenizer.tokenize(response))
        return {
            "user_input": user_input,
            "response": response,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "sentiment": sentiment
        }

    def _update_user_understanding(self, user_input, response, sentiment):
        if "last_sentiment" not in self.user_understanding:
            self.user_understanding["sentiment_history"] = []
        self.user_understanding["sentiment_history"].append(sentiment)
        if len(self.user_understanding["sentiment_history"]) > 10:
            self.user_understanding["sentiment_history"].pop(0)
        if sentiment == "positive" or sentiment == "negative":
            self.user_understanding["last_expressed"] = sentiment

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

    def save_model(self, path):
        data = {
            "attention_matrices": [dict(layer) for layer in self.attention_matrices],
            "state_to_text": self.state_to_text,
            "text_to_state": self.text_to_state,
            "learned_vocab": self.learned_vocab,
            "user_preferences": self.user_preferences,
            "self_understanding": self.self_understanding,
            "improvement_goals": self.improvement_goals,
            "user_understanding": self.user_understanding,
            "causal_position": self.causal_position,
            "lru_cache": list(self.lru_cache.keys()),
            "char_to_token": self.tokenizer.char_to_token,
            "token_to_char": self.tokenizer.token_to_char,
            "subword_to_token": self.tokenizer.subword_to_token,
            "token_to_subword": self.tokenizer.token_to_subword,
            "_next_token_id": self.tokenizer._next_token_id,
            "_next_subword_id": self.tokenizer._next_subword_id,
            "personality": self.personality,
            "preferences": self.preferences,
            "conversation_style": self.conversation_style,
            "phrase_patterns": dict(self.phrase_learner.phrase_patterns),
            "response_templates": self.phrase_learner.response_templates,
            "gradient_history": dict(self.gradient_history),
            "context_chain": self.context_chain,
            "learning_streak": self.learning_streak,
            "consecutive_correct": self.consecutive_correct
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"保存模型失败: {str(e)}")

    def load_model(self, path):
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise Exception(f"加载模型失败: {str(e)}")
        self.attention_matrices = [defaultdict(lambda: defaultdict(float)) for _ in range(self.num_layers)]
        for i, layer_dict in enumerate(data.get("attention_matrices", [])):
            if i < self.num_layers:
                self.attention_matrices[i] = defaultdict(lambda: defaultdict(float), layer_dict)
        self.state_to_text = data.get("state_to_text", {})
        self.text_to_state = data.get("text_to_state", {})
        self.learned_vocab = data.get("learned_vocab", [])
        self.user_preferences = data.get("user_preferences", {})
        self.self_understanding = data.get("self_understanding", {})
        self.improvement_goals = data.get("improvement_goals", [])
        self.user_understanding = data.get("user_understanding", {})
        self.causal_position = data.get("causal_position", 0)
        self.lru_cache = OrderedDict()
        lru_list = data.get("lru_cache", [])
        for state_id in lru_list:
            if state_id in self.state_to_text:
                self._lru_access(state_id)
        self.tokenizer.char_to_token = data.get("char_to_token", {})
        self.tokenizer.token_to_char = data.get("token_to_char", {})
        self.tokenizer.subword_to_token = data.get("subword_to_token", {})
        self.tokenizer.token_to_subword = data.get("token_to_subword", {})
        self.tokenizer._next_token_id = data.get("_next_token_id", 1)
        self.tokenizer._next_subword_id = data.get("_next_subword_id", 1)
        self.personality = data.get("personality", self.personality)
        self.preferences = data.get("preferences", self.preferences)
        self.conversation_style = data.get("conversation_style", "自然")
        self.phrase_learner.phrase_patterns = defaultdict(list, data.get("phrase_patterns", {}))
        self.phrase_learner.response_templates = data.get("response_templates", [])
        self.gradient_history = defaultdict(float, data.get("gradient_history", {}))
        self.context_chain = data.get("context_chain", [])
        self.learning_streak = data.get("learning_streak", 0)
        self.consecutive_correct = data.get("consecutive_correct", 0)
        self.personality_reward = PersonalityRewardSystem(self.personality)

class LLMAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
                "endpoints": {
                    "chat": {"method": "POST", "path": "/chat", "description": "对话接口"},
                    "train": {"method": "POST", "path": "/train", "description": "训练接口"},
                    "create_instance": {"method": "POST", "path": "/create_instance", "description": "创建新实例"},
                    "delete_instance": {"method": "POST", "path": "/delete_instance", "description": "删除实例"},
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
        else:
            self.send_response(404)
            self.end_headers()

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
            api_key = data.get("api_key", "mtgchatgf")
            user_input = data.get("input", "")
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
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            self.server.current_session = self.server.api_keys[api_key]["session_id"]
            result = model.chat(user_input)
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
            result = model.train(user_input, response, mode)
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
        elif self.path == "/export_chat":
            try:
                api_key = self.headers.get("Authorization", "default").replace("Bearer ", "")
                model = self.server.get_session_by_api_key(api_key)
                if not model:
                    if self.server.sessions:
                        model = list(self.server.sessions.values())[0]
                    else:
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "No sessions available"}, ensure_ascii=False).encode("utf-8"))
                        return
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"chat_history": model.context_chain if model.context_chain else []}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
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
            path = data.get("path", "model.json")
            model = self.server.get_session_by_api_key(api_key)
            if not model:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid api key"}')
                return
            try:
                model.save_model(path)
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
            path = data.get("path", "model.json")
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

class LLMServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.sessions = {}
        self.api_keys = load_api_keys()
        self.token_usage = defaultdict(int)
        self.rate_limit = defaultdict(int)
        self.rate_limit_window = 60
        self.rate_limit_max = 100
        self.current_session = None
        self._init_sessions()
    
    def _init_sessions(self):
        config = load_config()
        weights_dir = config.get("weights_path", os.path.expanduser("~/llm_weights"))
        if not os.path.exists(weights_dir):
            os.makedirs(weights_dir, exist_ok=True)
        for api_key, key_data in self.api_keys.items():
            session_id = key_data.get("session_id", f"session_{len(self.sessions)}")
            if session_id not in self.sessions:
                weights_file = os.path.join(weights_dir, f"{session_id}.json")
                model = LightweightMultiLayerLLM()
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
            if "mtgchatgf" in self.server.llm_server.sessions:
                model = self.server.llm_server.sessions["mtgchatgf"]
                result = model.chat(user_input)
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

class CJSLServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, llm_server):
        super().__init__(server_address, RequestHandlerClass)
        self.llm_server = llm_server

class LLMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(_("title"))
        config = load_config()
        geometry = config.get("window_geometry", "1400x850")
        self.root.geometry(geometry)
        self.root.minsize(800, 600)
        self.config = load_config()
        self.sessions = {}
        self.current_session = None
        self.api_server = None
        self.api_thread = None
        self.cjsl_server = None
        self.cjsl_thread = None
        self.auto_save_timer_id = None
        self._init_sessions()
        self._create_gui()
        self._load_language_config()
        self.update_model_info()
        self.update_session_list()
        self.update_server_status()
        self.root.after(1000, self.update_system_info)
        self.root.after(5000, self.update_instance_info)
        self.root.after(60000, self.auto_save_timer)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _load_language_config(self):
        lang = self.config.get("language", "zh")
        load_language(lang)
    
    def _init_sessions(self):
        api_keys = load_api_keys()
        weights_dir = self.config.get("weights_path", os.path.expanduser("~/llm_weights"))
        if not os.path.exists(weights_dir):
            os.makedirs(weights_dir, exist_ok=True)
        for api_key, key_data in api_keys.items():
            session_id = key_data.get("session_id", f"session_{len(self.sessions)}")
            if session_id not in self.sessions:
                weights_file = os.path.join(weights_dir, f"{session_id}.json")
                model = LightweightMultiLayerLLM()
                if os.path.exists(weights_file):
                    try:
                        model.load_model(weights_file)
                    except Exception as e:
                        log_error(f"Failed to load model for {session_id}: {str(e)}")
                self.sessions[session_id] = model
        if "mtgchatgf" not in self.sessions:
            self.sessions["mtgchatgf"] = LightweightMultiLayerLLM()
        if len(self.sessions) == 0:
            self.sessions["default"] = LightweightMultiLayerLLM()
        self.current_session = self.config.get("current_session", list(self.sessions.keys())[0])
        if self.current_session not in self.sessions:
            self.current_session = list(self.sessions.keys())[0]
    
    def _create_gui(self):
        bg_color = "#1e1e1e"
        surface_color = "#252526"
        text_color = "#d4d4d4"
        secondary_text = "#808080"
        accent_color = "#007acc"
        
        self.root.configure(bg=bg_color)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = tk.Frame(main_paned, bg=surface_color, width=280)
        main_paned.add(left_frame, weight=1)
        left_frame.pack_propagate(False)
        
        mid_frame = tk.Frame(main_paned, bg=bg_color)
        main_paned.add(mid_frame, weight=4)
        
        right_frame = tk.Frame(main_paned, bg=surface_color, width=300)
        main_paned.add(right_frame, weight=1)
        right_frame.pack_propagate(False)
        
        self.left_frame_label = tk.Label(left_frame, text=_("session_management"), font=("Microsoft YaHei", 12, "bold"), 
                bg=surface_color, fg=text_color)
        self.left_frame_label.pack(fill=tk.X, padx=10, pady=10)
        
        self.session_list = tk.Listbox(left_frame, bg=bg_color, fg=text_color, 
                                       selectbackground=accent_color, height=10)
        self.session_list.pack(fill=tk.X, padx=10, pady=5)
        self.session_list.bind("<<ListboxSelect>>", self.on_session_select)
        
        btn_frame = tk.Frame(left_frame, bg=surface_color)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        self.new_session_btn = ttk.Button(btn_frame, text=_("new_session"), command=self.create_new_session)
        self.new_session_btn.pack(fill=tk.X, pady=2)
        self.rename_session_btn = ttk.Button(btn_frame, text=_("rename_session"), command=self.rename_session)
        self.rename_session_btn.pack(fill=tk.X, pady=2)
        self.delete_session_btn = ttk.Button(btn_frame, text=_("delete_session"), command=self.delete_session)
        self.delete_session_btn.pack(fill=tk.X, pady=2)
        
        mid_top = tk.Frame(mid_frame, bg=surface_color)
        mid_top.pack(fill=tk.X)
        self.mid_label = tk.Label(mid_top, text=_("chat_window"), font=("Microsoft YaHei", 12, "bold"), 
                bg=surface_color, fg=text_color)
        self.mid_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.clear_btn = ttk.Button(mid_top, text=_("clear"), command=self.clear_chat)
        self.clear_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(mid_frame, bg=bg_color, fg=text_color, 
                                                      font=("Microsoft YaHei", 10), wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        input_frame = tk.Frame(mid_frame, bg=surface_color)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        self.user_input = tk.Text(input_frame, bg=bg_color, fg=text_color, 
                                 font=("Microsoft YaHei", 10), height=3, wrap=tk.WORD)
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.user_input.bind("<Control-Return>", self.send_message)
        
        self.send_btn = ttk.Button(input_frame, text=_("send"), command=self.send_message, width=10)
        self.send_btn.pack(side=tk.RIGHT, padx=5)
        
        self.right_info_label = tk.Label(right_frame, text=_("basic_info"), font=("Microsoft YaHei", 12, "bold"), 
                bg=surface_color, fg=text_color)
        self.right_info_label.pack(fill=tk.X, padx=10, pady=10)
        
        self.model_info = tk.Text(right_frame, bg=bg_color, fg=text_color, font=("Microsoft YaHei", 9), 
                                  height=8, wrap=tk.WORD)
        self.model_info.pack(fill=tk.X, padx=10, pady=5)
        self.model_info.config(state=tk.DISABLED)
        
        self.right_status_label = tk.Label(right_frame, text=_("realtime_status"), font=("Microsoft YaHei", 12, "bold"), 
                bg=surface_color, fg=text_color)
        self.right_status_label.pack(fill=tk.X, padx=10, pady=10)
        self.system_status = tk.Text(right_frame, bg=bg_color, fg=text_color, font=("Microsoft YaHei", 9), 
                                    height=6, wrap=tk.WORD)
        self.system_status.pack(fill=tk.X, padx=10, pady=5)
        self.system_status.config(state=tk.DISABLED)
        
        self.right_instance_label = tk.Label(right_frame, text=_("instance_info"), font=("Microsoft YaHei", 12, "bold"), 
                bg=surface_color, fg=text_color)
        self.right_instance_label.pack(fill=tk.X, padx=10, pady=10)
        self.instance_info = tk.Text(right_frame, bg=bg_color, fg=text_color, font=("Microsoft YaHei", 9), 
                                    height=10, wrap=tk.WORD)
        self.instance_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.instance_info.config(state=tk.DISABLED)
        
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        self.file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label=_("save_model"), command=self.save_model)
        self.file_menu.add_command(label=_("load_model"), command=self.load_model)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)
        
        self.api_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="API", menu=self.api_menu)
        self.api_menu.add_command(label=_("start_api"), command=self.start_api_server)
        self.api_menu.add_command(label=_("stop_api"), command=self.stop_api_server)
        self.api_menu.add_separator()
        self.api_menu.add_command(label=_("api_description"), command=self.show_api_help)
        
        self.language_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label=_("language_settings"), menu=self.language_menu)
        self.language_menu.add_command(label="中文", command=lambda: self.switch_lang("zh"))
        self.language_menu.add_command(label="English", command=lambda: self.switch_lang("en"))
        self.language_menu.add_separator()
        self.language_menu.add_command(label=_("import_language_pack"), command=self.import_language_pack)
        
        self._update_styles()
    
    def _update_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background="#007acc", foreground="white", padding=8)
        style.map("TButton", background=[("active", "#005a9e")])
    
    def update_session_list(self):
        current_selection = self.session_list.curselection()
        self.session_list.delete(0, tk.END)
        for session_id in self.sessions.keys():
            disp_text = session_id
            if self.api_server:
                for api_key, key_data in self.api_server.api_keys.items():
                    if key_data.get("session_id") == session_id:
                        if key_data.get("is_free", False):
                            disp_text = f"{session_id} ({_('free')})"
                        else:
                            disp_text = f"{session_id} (tokens: {key_data.get('tokens', 0)})"
                        break
            self.session_list.insert(tk.END, disp_text)
        for i, session_id in enumerate(self.sessions.keys()):
            if session_id == self.current_session:
                self.session_list.selection_set(i)
                self.session_list.see(i)
                break
    
    def update_model_info(self):
        if not self.current_session or self.current_session not in self.sessions:
            return
        model = self.sessions[self.current_session]
        token_count = len(model.tokenizer.char_to_token) + len(model.tokenizer.subword_to_token)
        stats = model.get_learning_stats()
        
        info_text = f"{_('model_name')}: {model.model_name}\n"
        info_text += f"{_('model_version')}: {model.model_version}\n"
        info_text += f"{_('network_layers')}: {model.num_layers}\n"
        info_text += f"{_('token_count')}: {token_count}\n"
        info_text += f"{_('conversation_count')}: {len(model.context_chain)}\n"
        
        self.model_info.config(state=tk.NORMAL)
        self.model_info.delete(1.0, tk.END)
        self.model_info.insert(tk.END, info_text)
        self.model_info.config(state=tk.DISABLED)
    
    def update_server_status(self):
        status_text = f"{_('api_server')}: "
        if self.api_server:
            status_text += f"● {_('running')} (Port: {self.config.get('port', 4000)})\n"
        else:
            status_text += f"● {_('stopped')}\n"
        
        status_text += f"{_('cisl_interface')}: "
        if self.cjsl_server:
            status_text += f"● {_('running')} (Port: {self.config.get('cjsl_port', 9000)})\n"
        else:
            status_text += f"● {_('stopped')}\n"
        
        self.system_status.config(state=tk.NORMAL)
        self.system_status.delete(1.0, tk.END)
        self.system_status.insert(tk.END, status_text)
        self.system_status.config(state=tk.DISABLED)
    
    def update_system_info(self):
        cpu_usage = "N/A"
        mem_usage = "N/A"
        try:
            import psutil
            cpu_usage = f"{psutil.cpu_percent()}%"
            mem = psutil.virtual_memory()
            mem_usage = f"{mem.percent}%"
        except ImportError:
            cpu_usage = "安装psutil"
            mem_usage = "安装psutil"
        except Exception as e:
            cpu_usage = f"错误: {str(e)[:10]}"
            mem_usage = f"错误: {str(e)[:10]}"
        
        status_text = f"{_('api_server')}: "
        if self.api_server:
            status_text += f"● {_('running')} (Port: {self.config.get('port', 4000)})\n"
        else:
            status_text += f"● {_('stopped')}\n"
        
        status_text += f"{_('cisl_interface')}: "
        if self.cjsl_server:
            status_text += f"● {_('running')} (Port: {self.config.get('cjsl_port', 9000)})\n"
        else:
            status_text += f"● {_('stopped')}\n"
        
        status_text += f"{_('cpu')}: {cpu_usage}\n"
        status_text += f"{_('memory')}: {mem_usage}\n"
        
        self.system_status.config(state=tk.NORMAL)
        self.system_status.delete(1.0, tk.END)
        self.system_status.insert(tk.END, status_text)
        self.system_status.config(state=tk.DISABLED)
        
        self.root.after(1000, self.update_system_info)
    
    def update_instance_info(self):
        try:
            current_pos = self.instance_info.yview()
        except:
            current_pos = None
        
        info_text = f"{_('current_instance_count')}: {len(self.sessions)}\n"
        
        for session_id, model in self.sessions.items():
            token_count = len(model.tokenizer.char_to_token) + len(model.tokenizer.subword_to_token)
            info_text += f"\n=== {session_id} ===\n"
            
            if self.api_server:
                for api_key, key_data in self.api_server.api_keys.items():
                    if key_data.get("session_id") == session_id:
                        info_text += f"{_('api_key')}: {api_key}\n"
                        if key_data.get("is_free"):
                            info_text += f"Status: {_('free')}\n"
                            info_text += f"{_('token_balance')}: {_('token_balance_unlimited')}\n"
                        else:
                            info_text += f"Status: Paid\n"
                            info_text += f"{_('token_balance')}: {key_data.get('tokens', 0)}\n"
                        break
                else:
                    info_text += f"{_('api_key')}: {_('api_key_unassigned')}\n"
                    info_text += f"Status: {_('api_not_running')}\n"
                    info_text += f"{_('token_balance')}: --\n"
            else:
                info_text += f"{_('api_key')}: {_('api_not_running')}\n"
                info_text += f"{_('token_balance')}: --\n"
            
            info_text += f"{_('model_tokens')}: {token_count}\n"
            info_text += f"{_('conversation_count')}: {len(model.context_chain)}\n"
        
        self.instance_info.config(state=tk.NORMAL)
        self.instance_info.delete(1.0, tk.END)
        self.instance_info.insert(tk.END, info_text)
        if current_pos:
            self.instance_info.yview_moveto(current_pos[0])
        self.instance_info.config(state=tk.DISABLED)
        self.root.after(5000, self.update_instance_info)
    
    def on_session_select(self, event):
        if not self.session_list.curselection():
            return
        index = self.session_list.curselection()[0]
        session_id = list(self.sessions.keys())[index]
        self.switch_session(session_id)
    
    def switch_session(self, session_id):
        if session_id not in self.sessions:
            return
        self.current_session = session_id
        self.config["current_session"] = session_id
        save_config(self.config)
        self.update_model_info()
        self.update_chat_display()
        messagebox.showinfo(_("success"), f"{_('switched_to_session')}{session_id}")
    
    def create_new_session(self):
        name = simpledialog.askstring("New Session", "Enter session name:")
        if not name:
            return
        if name in self.sessions:
            messagebox.showerror(_("error"), _("session_already_exists"))
            return
        self.sessions[name] = LightweightMultiLayerLLM()
        if self.api_server:
            api_key, temp_session = self.api_server.add_instance(name)
        self.current_session = name
        self.config["current_session"] = name
        save_config(self.config)
        self.update_session_list()
        self.update_model_info()
        messagebox.showinfo(_("success"), f"{_('session_created')}{name}")
    
    def rename_session(self):
        if not self.session_list.curselection():
            return
        index = self.session_list.curselection()[0]
        old_name = list(self.sessions.keys())[index]
        if old_name == "mtgchatgf":
            messagebox.showerror(_("error"), _("cannot_rename_default"))
            return
        new_name = simpledialog.askstring("Rename Session", "Enter new session name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        if new_name in self.sessions:
            messagebox.showerror(_("error"), _("session_already_exists"))
            return
        
        model = self.sessions[old_name]
        del self.sessions[old_name]
        self.sessions[new_name] = model
        if self.current_session == old_name:
            self.current_session = new_name
            self.config["current_session"] = new_name
            save_config(self.config)
        
        if self.api_server:
            for api_key, key_data in list(self.api_server.api_keys.items()):
                if key_data.get("session_id") == old_name:
                    self.api_server.api_keys[api_key]["session_id"] = new_name
                    save_api_keys(self.api_server.api_keys)
        
        self.update_session_list()
        self.update_model_info()
        messagebox.showinfo(_("success"), f"{_('session_renamed')}{new_name}")
    
    def delete_session(self):
        if not self.session_list.curselection():
            return
        index = self.session_list.curselection()[0]
        session_id = list(self.sessions.keys())[index]
        if session_id == "mtgchatgf":
            messagebox.showerror(_("error"), _("cannot_delete_default"))
            return
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete session '{session_id}'?"):
            return
        
        if self.api_server:
            for api_key, key_data in list(self.api_server.api_keys.items()):
                if key_data.get("session_id") == session_id:
                    del self.api_server.api_keys[api_key]
                    save_api_keys(self.api_server.api_keys)
        
        del self.sessions[session_id]
        if self.current_session == session_id:
            self.current_session = list(self.sessions.keys())[0]
            self.config["current_session"] = self.current_session
            save_config(self.config)
        
        self.update_session_list()
        self.update_model_info()
        self.update_chat_display()
        messagebox.showinfo(_("success"), f"{_('session_deleted')}{session_id}")
    
    def update_chat_display(self):
        if not self.current_session or self.current_session not in self.sessions:
            return
        model = self.sessions[self.current_session]
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        for msg in model.context_chain[-50:]:
            user_input = msg.get("input", "")
            response = msg.get("response", "")
            if user_input:
                self.chat_display.insert(tk.END, f"You: {user_input}\n\n", "user")
            if response:
                self.chat_display.insert(tk.END, f"AI: {response}\n\n", "ai")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        user_input = self.user_input.get("1.0", tk.END).strip()
        if not user_input:
            return
        if not self.current_session or self.current_session not in self.sessions:
            return
        model = self.sessions[self.current_session]
        
        if self.api_server:
            for api_key, key_data in self.api_server.api_keys.items():
                if key_data.get("session_id") == self.current_session:
                    if not key_data.get("is_free", False) and key_data.get("tokens", 0) <= 0:
                        messagebox.showerror(_("error"), _("insufficient_tokens"))
                        return
                    break
        
        result = model.chat(user_input)
        response = result.get("response", "")
        input_tokens = result.get("input_tokens", 0)
        output_tokens = result.get("output_tokens", 0)
        
        if self.api_server:
            for api_key, key_data in self.api_server.api_keys.items():
                if key_data.get("session_id") == self.current_session:
                    self.api_server.deduct_tokens(api_key, input_tokens + output_tokens)
                    break
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"You: {user_input}\n\n", "user")
        self.chat_display.insert(tk.END, f"AI: {response}\n\n", "ai")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        self.user_input.delete("1.0", tk.END)
        self.update_model_info()
        self.update_instance_info()
    
    def clear_chat(self):
        if not self.current_session or self.current_session not in self.sessions:
            return
        self.sessions[self.current_session].context_chain = []
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        messagebox.showinfo(_("success"), _("chat_cleared"))
    
    def save_model(self):
        if not self.current_session or self.current_session not in self.sessions:
            return
        weights_dir = self.config.get("weights_path", os.path.expanduser("~/llm_weights"))
        if not os.path.exists(weights_dir):
            os.makedirs(weights_dir, exist_ok=True)
        file_path = os.path.join(weights_dir, f"{self.current_session}.json")
        try:
            self.sessions[self.current_session].save_model(file_path)
            messagebox.showinfo(_("success"), f"{_('model_saved_to')}{file_path}")
        except Exception as e:
            log_error(f"Failed to save model: {str(e)}")
            messagebox.showerror(_("error"), f"Failed to save model: {str(e)}")
    
    def load_model(self):
        weights_dir = self.config.get("weights_path", os.path.expanduser("~/llm_weights"))
        file_path = filedialog.askopenfilename(initialdir=weights_dir, filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            model = LightweightMultiLayerLLM()
            model.load_model(file_path)
            filename = os.path.basename(file_path).rsplit('.', 1)[0]
            self.sessions[filename] = model
            self.current_session = filename
            self.config["current_session"] = filename
            save_config(self.config)
            self.update_session_list()
            self.update_model_info()
            self.update_chat_display()
            messagebox.showinfo(_("success"), f"{_('model_loaded_to')}{filename}")
        except Exception as e:
            log_error(f"Failed to load model: {str(e)}")
            messagebox.showerror(_("error"), f"Failed to load model: {str(e)}")
    
    def start_api_server(self):
        if self.api_server is not None:
            messagebox.showwarning(_("warning"), "API server is already running")
            return
        try:
            port = self.config.get("port", 4000)
            cjsl_port = self.config.get("cjsl_port", 9000)
            
            bind_address = "0.0.0.0"
            try:
                import socket
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                    sock.bind((bind_address, port))
                    sock.close()
                    bind_address = "::"
                except Exception:
                    sock.close()
                    bind_address = "0.0.0.0"
            except Exception:
                bind_address = "0.0.0.0"
            
            self.api_server = LLMServer((bind_address, port), LLMAPIHandler)
            self.api_server.sessions = self.sessions
            self.api_server.api_keys = load_api_keys()
            
            for session_id in self.sessions.keys():
                found = False
                for api_key, key_data in self.api_server.api_keys.items():
                    if key_data.get("session_id") == session_id:
                        found = True
                        break
                if not found:
                    if session_id == "mtgchatgf":
                        api_key = "mtgchatgf"
                    else:
                        api_key = secrets.token_urlsafe(32)
                    self.api_server.api_keys[api_key] = {
                        "session_id": session_id,
                        "tokens": -1 if session_id == "mtgchatgf" else 1000,
                        "is_free": session_id == "mtgchatgf",
                        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
            save_api_keys(self.api_server.api_keys)
            
            self.api_thread = threading.Thread(target=self.api_server.serve_forever, daemon=True)
            self.api_thread.start()
            
            self.cjsl_server = CJSLServer((bind_address, cjsl_port), CISLAPIHandler, self.api_server)
            self.cjsl_thread = threading.Thread(target=self.cjsl_server.serve_forever, daemon=True)
            self.cjsl_thread.start()
            
            self.update_server_status()
            self.update_instance_info()
            messagebox.showinfo(_("success"), f"API server started on port {port}\nCISL interface on port {cjsl_port}")
        except Exception as e:
            log_exception(e)
            messagebox.showerror(_("error"), f"Failed to start API server: {str(e)}")
    
    def stop_api_server(self):
        if self.api_server is None:
            messagebox.showwarning(_("warning"), "API server is not running")
            return
        
        try:
            self.api_server.shutdown()
            self.api_server.server_close()
            self.api_server = None
            self.api_thread = None
            
            if self.cjsl_server:
                self.cjsl_server.shutdown()
                self.cjsl_server.server_close()
                self.cjsl_server = None
                self.cjsl_thread = None
            
            self.update_server_status()
            self.update_instance_info()
            messagebox.showinfo(_("success"), "API server stopped")
        except Exception as e:
            log_exception(e)
            messagebox.showerror(_("error"), f"Failed to stop API server: {str(e)}")
    
    def auto_save_timer(self):
        try:
            self.save_all_sessions()
        except Exception as e:
            log_error(f"Auto-save failed: {str(e)}")
        self.root.after(60000, self.auto_save_timer)
    
    def save_all_sessions(self):
        weights_dir = self.config.get("weights_path", os.path.expanduser("~/llm_weights"))
        if not os.path.exists(weights_dir):
            os.makedirs(weights_dir, exist_ok=True)
        for session_id, model in self.sessions.items():
            try:
                file_path = os.path.join(weights_dir, f"{session_id}.json")
                model.save_model(file_path)
            except Exception as e:
                log_error(f"Failed to save session {session_id}: {str(e)}")
    
    def switch_lang(self, lang):
        load_language(lang)
        self.config["language"] = lang
        save_config(self.config)
        
        self.root.title(_("title"))
        
        self._update_all_texts()
        
        messagebox.showinfo(_("success"), f"{_('language_switched')}{'中文' if lang == 'zh' else 'English'}")
    
    def _update_all_texts(self):
        """更新所有GUI文本"""
        self.left_frame_label.config(text=_("session_management"))
        self.mid_label.config(text=_("chat_window"))
        self.clear_btn.config(text=_("clear"))
        self.send_btn.config(text=_("send"))
        self.right_info_label.config(text=_("basic_info"))
        self.right_status_label.config(text=_("realtime_status"))
        self.right_instance_label.config(text=_("instance_info"))
        
        self.new_session_btn.config(text=_("new_session"))
        self.rename_session_btn.config(text=_("rename_session"))
        self.delete_session_btn.config(text=_("delete_session"))
        
        self.file_menu.entryconfigure(0, label=_("save_model"))
        self.file_menu.entryconfigure(1, label=_("load_model"))
        
        self.api_menu.entryconfigure(0, label=_("start_api"))
        self.api_menu.entryconfigure(1, label=_("stop_api"))
        self.api_menu.entryconfigure(3, label=_("api_description"))
        
        self.language_menu.delete(0, 2)
        self.language_menu.add_command(label="中文", command=lambda: self.switch_lang("zh"))
        self.language_menu.add_command(label="English", command=lambda: self.switch_lang("en"))
        self.language_menu.add_separator()
        self.language_menu.add_command(label=_("import_language_pack"), command=self.import_language_pack)
    
    def import_language_pack(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                new_langs = json.load(f)
            for lang_key, lang_data in new_langs.items():
                save_custom_language(lang_key, lang_data)
            messagebox.showinfo(_("success"), _("language_pack_imported"))
        except Exception as e:
            log_exception(e)
            messagebox.showerror(_("error"), f"Failed to import language pack: {str(e)}")
    
    def show_api_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title(_("api_description"))
        help_window.geometry("700x600")
        
        help_text = tk.Text(help_window, font=("Microsoft YaHei", 10), wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if current_language == "zh":
            help_content = "=== 千因 - MTG AI V-Causal API 使用文档 ===\n\n"
            help_content += f"【API服务器】端口: {self.config.get('port', 4000)} (需要API密钥)\n\n"
            
            endpoints = [
                ("POST", "/chat", "对话接口", "api_key, input"),
                ("POST", "/train", "训练接口", "api_key, input, response, mode"),
                ("POST", "/create_instance", "创建新实例", "session_id (可选)"),
                ("POST", "/delete_instance", "删除实例", "api_key"),
                ("POST", "/update_tokens", "更新Token余额", "api_key, amount"),
                ("POST", "/set_personality", "设置性格", "api_key, trait, value"),
                ("POST", "/add_preference", "添加偏好", "api_key, category, item"),
                ("POST", "/rename_session", "重命名会话", "api_key, new_name"),
                ("POST", "/import_chat", "导入对话历史", "api_key, chat_history"),
                ("POST", "/save_model", "保存模型", "api_key, path"),
                ("POST", "/load_model", "加载模型", "api_key, path"),
                ("GET", "/sessions", "获取会话列表", ""),
                ("GET", "/instances", "获取所有实例详细信息", ""),
                ("GET", "/instance/{session_id}", "获取单个实例详情", ""),
                ("GET", "/personality", "获取性格设置", ""),
                ("GET", "/preferences", "获取偏好设置", ""),
                ("GET", "/stats", "获取学习统计", ""),
                ("GET", "/api_info", "获取API服务器信息", ""),
                ("GET", "/health", "健康检查", ""),
                ("GET", "/export_chat", "导出对话历史", ""),
            ]
            
            for method, path, desc, params in endpoints:
                help_content += f"{method} {path} - {desc}\n"
                if params:
                    help_content += f"参数: {params}\n"
                help_content += "\n"
            
            help_content += f"\n【CISL接口】端口: {self.config.get('cjsl_port', 9000)} (无鉴权，免费使用)\n"
            help_content += "POST /chat - 免费对话接口\n"
            help_content += "参数: input\n"
            help_content += "使用默认免费实例 mtgchatgf\n"
        else:
            help_content = "=== QianYin - MTG AI V-Causal API Documentation ===\n\n"
            help_content += f"[API Server] Port: {self.config.get('port', 4000)} (Requires API Key)\n\n"
            
            endpoints = [
                ("POST", "/chat", "Chat Interface", "api_key, input"),
                ("POST", "/train", "Training Interface", "api_key, input, response, mode"),
                ("POST", "/create_instance", "Create New Instance", "session_id (optional)"),
                ("POST", "/delete_instance", "Delete Instance", "api_key"),
                ("POST", "/update_tokens", "Update Token Balance", "api_key, amount"),
                ("POST", "/set_personality", "Set Personality", "api_key, trait, value"),
                ("POST", "/add_preference", "Add Preference", "api_key, category, item"),
                ("POST", "/rename_session", "Rename Session", "api_key, new_name"),
                ("POST", "/import_chat", "Import Chat History", "api_key, chat_history"),
                ("POST", "/save_model", "Save Model", "api_key, path"),
                ("POST", "/load_model", "Load Model", "api_key, path"),
                ("GET", "/sessions", "Get Session List", ""),
                ("GET", "/instances", "Get All Instance Details", ""),
                ("GET", "/instance/{session_id}", "Get Single Instance Detail", ""),
                ("GET", "/personality", "Get Personality Settings", ""),
                ("GET", "/preferences", "Get Preference Settings", ""),
                ("GET", "/stats", "Get Learning Statistics", ""),
                ("GET", "/api_info", "Get API Server Info", ""),
                ("GET", "/health", "Health Check", ""),
                ("GET", "/export_chat", "Export Chat History", ""),
            ]
            
            for method, path, desc, params in endpoints:
                help_content += f"{method} {path} - {desc}\n"
                if params:
                    help_content += f"Parameters: {params}\n"
                help_content += "\n"
            
            help_content += f"\n[CISL Interface] Port: {self.config.get('cjsl_port', 9000)} (No authentication, free)\n"
            help_content += "POST /chat - Free Chat Interface\n"
            help_content += "Parameters: input\n"
            help_content += "Uses default free instance mtgchatgf\n"
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        try:
            self.config["window_geometry"] = self.root.geometry()
            save_config(self.config)
            self.save_all_sessions()
            if self.api_server:
                self.api_server.shutdown()
                self.api_server.server_close()
            if self.cjsl_server:
                self.cjsl_server.shutdown()
                self.cjsl_server.server_close()
        except Exception as e:
            log_exception(e)
        self.root.destroy()

def main():
    config = load_config()
    if not os.path.exists(config.get("weights_path", os.path.expanduser("~/llm_weights"))):
        try:
            os.makedirs(config.get("weights_path", os.path.expanduser("~/llm_weights")))
        except:
            pass
    lang = config.get("language", "zh")
    load_language(lang)
    root = tk.Tk()
    app = LLMGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()


