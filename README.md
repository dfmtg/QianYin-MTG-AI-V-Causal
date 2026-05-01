# 千因 - MTG AI V-Causal

## 新型串行因果推理AI系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Architecture-Serial%20Causal-orange.svg" alt="Architecture">
</p>

---

## 📖 项目简介

**千因（QianYin）** 是一款基于**新型串行因果推理架构**的AI系统，完全脱离传统Transformer的并行架构，采用纯串行推理引擎，在CPU上高效运行。

### 核心特性

- 🧠 **串行因果推理**: 不同于Transformer的并行自注意力，采用多层串行因果推理
- ⚡ **CPU高效运行**: 无需GPU，完全在CPU上执行推理
- 🔄 **实时学习**: 支持对话中增量学习，更新模型权重
- 🌐 **双栈网络**: 支持IPv4/IPv6双协议栈
- 🖥️ **跨平台支持**: Windows/Mac OS/Linux全平台兼容

---

## 🏗️ 技术架构

### 串行因果推理 vs Transformer

| 特性 | 千因（串行因果） | Transformer |
|------|----------------|-------------|
| 推理方式 | 串行逐步推理 | 并行自注意力 |
| 依赖GPU | 否 | 是 |
| 内存占用 | 低 | 高 |
| 因果追踪 | 原生支持 | 需额外位置编码 |
| 推理速度 | 中等 | 快 |
| 可解释性 | 高 | 中 |

### 核心技术

- **语义编码器**: 4096维度向量空间
- **QKV串行注意力**: 每层独立QKV计算
- **状态转换机制**: 基于状态的因果推理
- **短语学习器**: 从对话中学习短语模式
- **人格奖励系统**: 自适应性格调整

---

## 🚀 安装与运行

### 环境要求

- Python 3.8 或更高版本
- tkinter (通常随Python一起安装)
- psutil (可选，用于CPU/内存监控)

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/dfmtg/QianYin-MTG-AI-V-Causal.git
cd QianYin-MTG-AI-V-Causal

# 2. (可选) 安装psutil以启用硬件监控
pip install psutil

# 3. 运行程序
python "MTG AI V-Causal.py"
```

---

## 📋 功能列表

### 核心功能

#### 1. 多会话管理
- 创建、重命名、删除会话
- 会话间隔离，独立记忆
- 自动保存与加载

#### 2. 对话接口
- 实时对话交互
- 多轮上下文记忆
- 情感识别与响应

#### 3. 训练系统
支持四种训练模式：

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **精炼训练 (refine)** | 轻量化增量学习 | 日常对话优化 |
| **完整训练 (full)** | 逐字全量训练 | 深度学习 |
| **强化训练 (intensive)** | 重点语义强化 | 特定主题加强 |
| **交互式训练 (interactive)** | 输入输出关联对齐 | 逻辑一致性优化 |

#### 4. API服务器
- **主端口 (4000)**: 需要API密钥的完整API接口
- **CISL端口 (9000)**: 无鉴权免费接口

#### 5. 模型权重管理
- 自动保存权重文件
- 一键备份与恢复
- 自定义存储路径

#### 6. 硬件监控
- CPU使用率实时显示
- 内存占用监控
- API服务器状态监控

---

## 🔌 API接口文档

### 主API接口 (端口 4000)

#### 对话接口
```http
POST /chat
Content-Type: application/json

{
  "api_key": "你的API密钥",
  "input": "你好，请介绍一下自己"
}
```

**响应示例：**
```json
{
  "result": {
    "user_input": "你好，请介绍一下自己",
    "response": "你好！我是千因，一个基于串行因果推理的AI助手。",
    "input_tokens": 15,
    "output_tokens": 25,
    "sentiment": "positive"
  },
  "api_key": "你的API密钥"
}
```

#### 训练接口
```http
POST /train
Content-Type: application/json

{
  "api_key": "你的API密钥",
  "input": "用户输入",
  "response": "模型响应",
  "mode": "refine"
}
```

#### 实例管理
```http
POST /create_instance    # 创建新实例
POST /delete_instance    # 删除实例 (需要api_key)
POST /update_tokens      # 更新Token余额 (需要api_key, amount)
POST /rename_session     # 重命名会话 (需要api_key, new_name)
```

#### 信息查询
```http
GET /instances           # 获取所有实例信息
GET /instance/{id}       # 获取单个实例详情
GET /sessions            # 获取会话列表
GET /personality          # 获取性格设置
GET /preferences          # 获取偏好设置
GET /stats               # 获取学习统计
GET /api_info            # 获取API服务器信息
GET /health              # 健康检查
```

#### 聊天记录
```http
GET /export_chat         # 导出对话历史
POST /import_chat         # 导入对话历史 (需要api_key, chat_history)
```

#### 模型操作
```http
POST /save_model         # 保存模型 (需要api_key, path)
POST /load_model         # 加载模型 (需要api_key, path)
```

### CISL免费接口 (端口 9000)

```http
POST /chat
Content-Type: application/json

{
  "input": "你好"
}
```

**特点：**
- 无需API密钥
- 使用默认免费实例 (mtgchatgf)
- 完全免费使用

---

## 📊 返回数据结构

所有接口返回统一格式：

```json
{
  "result": {
    "user_input": "原始用户输入",
    "response": "模型最终输出",
    "input_tokens": 15,
    "output_tokens": 25,
    "sentiment": "positive/negative/neutral"
  },
  "api_key": "使用的API密钥"
}
```

---

## 💰 Token系统

### Token额度

- **免费实例 (mtgchatgf)**: 无限制使用
- **付费实例**: 初始1000 tokens，可通过接口充值

### Token扣除规则

每次对话自动扣除：`input_tokens + output_tokens`

---

## ⚙️ 配置文件

程序首次运行自动生成以下配置文件：

- `config.json`: 权重路径、端口、语言设置等
- `api_keys.json`: API密钥与实例映射
- `language.json`: 自定义语言包
- `weights_info.json`: 权重版本信息

---

## 🌐 跨平台兼容性

### Windows
- ✅ 完整支持
- ✅ tkinter自带支持
- ✅ IPv4/IPv6双栈

### macOS
- ✅ 完整支持
- ✅ tkinter需手动安装 (`brew install python-tk`)
- ✅ IPv4/IPv6双栈

### Linux
- ✅ 完整支持
- ✅ tkinter需手动安装 (`sudo apt-get install python3-tk`)
- ✅ IPv4/IPv6双栈

---

## 🔧 故障排除

### 问题1: CPU/内存显示"N/A"
**解决方案**: 安装psutil
```bash
pip install psutil
```

### 问题2: tkinter导入错误
**Windows**: 重新安装Python，勾选"tcl/tk"选项
**macOS**: `brew install python-tk`
**Linux**: `sudo apt-get install python3-tk`

### 问题3: 端口被占用
修改`config.json`中的端口号：
```json
{
  "port": 4001,
  "cjsl_port": 9001
}
```

---

## 📝 开发指南

### 添加自定义语言包

1. 创建JSON文件：
```json
{
  "title": "你的标题",
  "send": "发送",
  "new_session": "新会话"
}
```

2. 在GUI中: 语言设置 → 导入语言包

### 扩展API接口

在`LLMAPIHandler`类的`do_POST`或`do_GET`方法中添加新接口。

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

---

## 📄 许可证

本项目采用 GNU 通用公共许可证 v3.0 (GPLv3) - 详见 [LICENSE](LICENSE) 文件

---

## 👨‍💻 作者

**千因 MTG AI V-Causal**

- GitHub: https://github.com/dfmtg
- 邮箱: mtgwimtg@163.com

---

## 🙏 致谢

- Python社区
- Tkinter团队
- 所有开源贡献者

---

## 📌 项目状态

![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-orange)

---

**⭐ 如果这个项目对你有帮助，请给我们一个Star！**

**🚀 让我们一起探索串行因果推理的无限可能！**
