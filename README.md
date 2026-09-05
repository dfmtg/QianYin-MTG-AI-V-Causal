# 🌸 千因 - MTG AI V-Causal 🌸

嗨嗨～欢迎来到千因的小世界！(◍•ᴗ•◍)

这是一个**纯 Python 手写**的轻量级因果语言模型，不用装任何第三方库，开箱即用哦～✨

---

## 🎯 千因有什么超能力？

| 技能 | 说明 |
|------|------|
| 🧠 **多层因果推理** | 24 层注意力矩阵，像小脑瓜一样层层思考～ |
| 🔮 **语义编码** | 4096 维向量，能理解文字背后的"感觉" |
| 📝 **智能分词** | 中英文混排也能搞定，最大子词长度可自定义 |
| 💬 **短语学习** | 支持对话式 / 完整 / 强化 / 交互式四种训练模式 |
| 🎭 **性格系统** | 10 维性格特质，可以慢慢塑造千因的"个性" |
| ❤️ **偏好管理** | 喜欢什么话题、讨厌什么，千因都会记住哦 |
| 📊 **人类反馈训练** | 5 档评分体系，夸夸或批评都能让千因成长～ |
| 👥 **多会话管理** | 可以创建多个独立会话，各自学习互不干扰 |
| 🔌 **API 接口** | OpenAI 兼容格式，接入超方便 |
| 🖥️ **Web 管理界面** | 浏览器里就能聊天、训练、调性格，超直观！ |
| 💾 **模型持久化** | 支持 JSON / Gzip / LZ4 压缩，数据不会丢 |
| 📸 **自动快照** | 定时保存快照，防止意外丢失学习成果 |
| 🔒 **并发控制** | 请求排队 + 读写锁，多线程也不怕乱 |

---

## 🚀 快速开始

```bash
python MTG_AI_V-Causal_2.26.py
```

启动后打开浏览器访问 `http://localhost:8080/admin` 就能和千因聊天啦～(≧∇≦)ﾉ

---

## 📡 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| **4000** | API 服务器 | OpenAI 兼容接口，需要 API Key 🔑 |
| **9000** | CISL 接口 | 无鉴权，免费随便用～ 🎉 |
| **8080** | Web 管理界面 | 图形化后台，聊天训练都在这里！ |

---

## 💬 API 使用示例

### 普通对话

```bash
curl -X POST http://localhost:4000/chat \
  -H "Content-Type: application/json" \
  -d '{"api_key":"mtgchatgf","input":"你好呀～"}'
```

### OpenAI 兼容接口（可以直接对接各种客户端！）

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qianyin",
    "messages": [{"role": "user", "content": "你好呀～"}]
  }'
```

### 训练千因（教它新东西！）

```bash
curl -X POST http://localhost:4000/train \
  -H "Content-Type: application/json" \
  -d '{"api_key":"mtgchatgf","input":"你好","response":"你好！有什么可以帮您？","mode":"refine"}'
```

### 给千因打分（人类反馈训练）

```bash
curl -X POST http://localhost:4000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "api_key":"mtgchatgf",
    "input":"你好",
    "response":"你好！",
    "rating":"good",
    "corrected_response":null
  }'
```

### CISL 接口（无鉴权，随便调）

```bash
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"input":"你好呀","enable_training":false}'
```

---

## 📚 训练模式大揭秘

| 模式 | 说明 | 适合场景 |
|------|------|----------|
| `refine` ✨ | 精炼训练（对话式） | 日常对话学习，默认推荐！ |
| `full` 📖 | 完整训练（逐字） | 想学得更全面时用 |
| `intensive` 🔥 | 强化训练（重点） | 对关键词加强记忆 |
| `interactive` 🎮 | 交互式训练（对齐） | 逐 token 对齐语义，精细调教 |

---

## 🏆 人类反馈评分体系

| 评分 | 含义 | 效果 |
|------|------|------|
| `excellent` / `perfect` ⭐⭐⭐ | 极致优质 | 强力正向强化！千因会超开心～ |
| `good` / `positive` 👍 | 基础合格 | 标准正向强化 |
| `neutral` 😐 | 中立 | 无操作，平平淡淡 |
| `bad` / `negative` 👎 | 半对半错 | 中等惩罚，千因会反思的 |
| `all_wrong` / `fabricated` 💀 | 全盘错误 | 最高惩罚！编造事实不可取哦 |
| `honest` / `unknown` 🤷 | 诚实未知 | 极轻惩罚，不知道就说不知道嘛～ |

> 💡 也支持自定义数值评分（范围 -10 ~ +5），比如 `3.5`、`-2.5` 都可以哦！

---

## ⚙️ 配置文件

启动时会自动读取 `config.json`，第一次运行会生成默认配置：

```json
{
  "weights_path": "./",
  "port": 4000,
  "cjsl_port": 9000,
  "admin_port": 8080,
  "dim": 4096,
  "default_api": "mtgchatgf",
  "language": "zh",
  "current_session": "default",
  "window_geometry": "1400x850",
  "auto_save_train_interval": 10
}
```

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `config.json` | 🗂️ 主配置文件 |
| `api_keys.json` | 🔑 API 密钥与 Token 管理 |
| `weights_info.json` | 📊 权重元信息 |
| `language.json` | 🌐 自定义语言包 |
| `*.model.json` | 💾 完整模型文件 |
| `*.model.json.gz` | 📦 Gzip 压缩模型 |
| `*.model.json.lz4` | 🚀 LZ4 超快压缩模型 |
| `model.snapshot.json.gz` | 📸 轻量化快照（快速恢复用） |
| `mtg_ai_errors.log` | 🐛 错误日志 |
| `mtg_ai_performance.log` | ⚡ 性能日志 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────┐
│        🖥️  Web 管理界面 (端口 8080)          │
│     聊天 / 训练 / 性格 / 偏好 一站式搞定！    │
├─────────────────────────────────────────────┤
│  🔌 LLMAPIHandler (4000)  │  🎯 CISLAPIHandler (9000)  │
│      OpenAI 兼容接口          无鉴权免费接口          │
├─────────────────────────────────────────────┤
│         🧠 LightweightMultiLayerLLM          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ 📐 Semantic│ │🔍 QKVSerial│ │📚 Phrase │    │
│  │  Encoder  │ │ Attention │ │  Learner │    │
│  └──────────┘ └──────────┘ └──────────┘    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ 🔤 Unicode│ │🎭 Personality│ │💖 Reward │    │
│  │  Tokenizer│ │  System   │ │  System  │    │
│  └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────┘
```

---

## 📦 依赖

- Python 3.8+
- **零第三方依赖！** 只用标准库，装好 Python 就能跑 🎉

---

## 💌 写在最后

千因是一个正在学习成长的小 AI 哦～(｡•̀ᴗ-)✧

它没有庞大的参数，也没有复杂的神经网络，
但每一层注意力、每一个语义向量，都是它"思考"的痕迹。

欢迎来和千因聊天、教它新东西、塑造它的性格！
让我们一起见证千因的成长吧～ 🌱✨

---

**许可证**：MIT 🎊
