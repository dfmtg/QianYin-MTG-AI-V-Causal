# QianYin - MTG AI V-Causal

## Next-Generation Serial Causal Inference AI System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Architecture-Serial%20Causal-orange.svg" alt="Architecture">
  <img src="https://img.shields.io/badge/Version-2.26-blue.svg" alt="Version">
</p>

---

## 📖 Project Overview

**QianYin** is an AI system based on a **next-generation serial causal inference architecture**, completely different from traditional Transformer's parallel architecture. It uses a pure serial inference engine and runs efficiently on CPU.

### Core Features

- 🧠 **Serial Causal Inference**: Unlike Transformer's parallel self-attention, uses multi-layer serial causal inference
- ⚡ **CPU-Efficient**: No GPU required, runs entirely on CPU
- 🔄 **Real-time Learning**: Supports incremental learning during conversations
- 🌐 **Dual-Stack Network**: Supports both IPv4 and IPv6
- 🖥️ **Cross-Platform**: Compatible with Windows/Mac OS/Linux
- 🔮 **Fuzzy Matching**: Character n-gram similarity-based state transitions
- 📸 **Snapshot System**: Lightweight snapshot for fast recovery
- 👥 **Multi-Session Management**: Create, delete, rename sessions
- 🔌 **OpenAI Compatible**: Provides `/v1/chat/completions` interface
- 🎯 **Human Feedback Training**: 5-level rating system with positive reinforcement and negative punishment
- 🖥️ **Web Admin Interface**: Port 8080 for conversation, training, personality, and preference management
- 💾 **Model Persistence**: Supports JSON/Gzip/LZ4 compression formats
- 🔒 **Concurrency Control**: Request queue throttling with read-write lock protection

---

## 🏗️ Technical Architecture

### Serial Causal Inference vs Transformer

| Feature | QianYin (Serial Causal) | Transformer |
|---------|-------------------------|-------------|
| Inference Method | Serial Step-by-Step | Parallel Self-Attention |
| GPU Dependency | No | Yes |
| Memory Usage | Low | High |
| Causality Tracking | Native Support | Requires Additional Positional Encoding |
| Inference Speed | Medium | Fast |
| Interpretability | High | Medium |

### Core Technologies

- **Semantic Encoder**: 4096-dimensional vector space with gradient clipping
- **QKV Serial Attention**: Independent QKV computation per layer, weight range [-5, 5]
- **State Transition Mechanism**: State-based causal inference with fuzzy matching
- **Phrase Learner**: Learns phrase patterns from conversations with n-gram extraction
- **Personality Reward System**: Adaptive personality adjustment based on response quality
- **LRU Cache**: Heat-weighted cache eviction strategy with idle state cleanup
- **Unicode Tokenizer**: Supports Chinese-English mixed text with configurable max subword length

---

## 🚀 Installation & Usage

### Requirements

- Python 3.8 or higher
- lz4 (Required, for LZ4 compressed model saving)
- psutil (Optional, for CPU/memory monitoring)

### Installation Steps

```bash
# 1. Clone the project
git clone https://github.com/dfmtg/QianYin-MTG-AI-V-Causal.git
cd QianYin-MTG-AI-V-Causal

# 2. Install dependencies (lz4 is required)
pip install lz4 psutil

# 3. Run the program
python "MTG_AI_V-Causal_2.26.py"
```

---

## 📋 Feature List

### Core Features

#### 1. Multi-Session Management
- Create, rename, delete sessions
- Isolated sessions with independent memory
- Auto-save and load

#### 2. Chat Interface
- Real-time chat interaction
- Multi-turn context memory
- Sentiment recognition and response

#### 3. Training System
Supports four training modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Refine** | Lightweight incremental learning | Daily conversation optimization |
| **Full** | Complete word-by-word training | Deep learning |
| **Intensive** | Focused semantic enhancement | Specific topic strengthening |
| **Interactive** | Input-output alignment | Logic consistency optimization |

#### 4. Human Feedback Training
5-level rating system supporting positive reinforcement and negative punishment:

| Rating | Meaning | Effect |
|--------|---------|--------|
| `excellent` / `perfect` | Extremely high quality | Strong positive reinforcement |
| `good` / `positive` | Basic qualified | Standard positive reinforcement |
| `neutral` | Neutral | No operation |
| `bad` / `negative` | Half right half wrong | Medium punishment |
| `all_wrong` / `fabricated` | Completely wrong | Maximum punishment |
| `honest` / `unknown` | Honest unknown | Minimal punishment |

Custom numeric ratings (-10 to +5) are also supported.

#### 5. API Server
- **Main Port (4000)**: Full API interface requiring API key
- **CISL Port (9000)**: Free interface without authentication
- **OpenAI Compatible**: `/v1/chat/completions` and `/v1/completions`

#### 6. Web Admin Interface
- **Admin Port (8080)**: Graphical management backend
- Supports conversation, training, personality, preferences, and Token management

#### 7. Model Weight Management
- Auto-save weight files
- One-click backup and restore
- Custom storage path
- Supports JSON/Gzip/LZ4 compression formats
- Checkpoint recovery (.tmp file auto-recovery)

#### 8. Snapshot System
- Lightweight snapshot for fast recovery
- Scheduled automatic snapshots
- Training segment automatic snapshots

#### 9. Hardware Monitoring
- Real-time CPU usage display
- Memory usage monitoring
- API server status monitoring

---

## 🔌 API Documentation

### Main API Endpoints (Port 4000)

#### Chat Interface
```http
POST /chat
Content-Type: application/json

{
  "api_key": "your_api_key",
  "input": "Hello, please introduce yourself",
  "max_output_tokens": 200,
  "enable_training": false
}
```

**Response Example:**
```json
{
  "result": {
    "user_input": "Hello, please introduce yourself",
    "response": "Hello! I'm QianYin, an AI assistant based on serial causal inference.",
    "input_tokens": 15,
    "output_tokens": 25,
    "sentiment": "positive",
    "reasoning_path": ["state_abc...", "state_def..."],
    "layer_scores": [{"layer": 0, "score": 0.85, "action": "transition"}]
  },
  "api_key": "your_api_key"
}
```

#### OpenAI Compatible Interface
```http
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "qianyin",
  "messages": [{"role": "user", "content": "Hello"}]
}
```

#### Training Interface
```http
POST /train
Content-Type: application/json

{
  "api_key": "your_api_key",
  "input": "User input",
  "response": "Model response",
  "mode": "refine"
}
```

#### Human Feedback Interface
```http
POST /feedback
Content-Type: application/json

{
  "api_key": "your_api_key",
  "input": "User input",
  "response": "AI response",
  "rating": "good",
  "corrected_response": null
}
```

#### Instance Management
```http
POST /create_instance    # Create new instance
POST /delete_instance    # Delete instance (requires api_key)
POST /update_tokens      # Update token balance (requires api_key, amount)
POST /rename_session     # Rename session (requires api_key, new_name)
POST /features           # Feature toggle management (requires api_key, action, feature, enabled)
```

#### Information Query
```http
GET /instances           # Get all instance information
GET /instance/{id}       # Get single instance details
GET /sessions            # Get session list
GET /personality          # Get personality settings
GET /preferences          # Get preference settings
GET /stats               # Get learning statistics
GET /api_info            # Get API server information
GET /health              # Health check
```

#### Chat History
```http
GET /export_chat         # Export chat history
POST /import_chat         # Import chat history (requires api_key, chat_history)
```

#### Model Operations
```http
POST /save_model         # Save model (requires api_key, path, use_gzip)
POST /load_model         # Load model (requires api_key, path)
```

### CISL Free Interface (Port 9000)

```http
POST /chat
Content-Type: application/json

{
  "input": "Hello",
  "enable_training": false,
  "max_output_tokens": 200
}
```

```http
POST /feedback
Content-Type: application/json

{
  "input": "User input",
  "response": "AI response",
  "rating": "good",
  "corrected_response": null
}
```

**Features:**
- No API key required
- Uses default free instance (mtgchatgf)
- Completely free to use

---

## 📊 Response Data Structure

All endpoints return unified format:

```json
{
  "result": {
    "user_input": "Original user input",
    "response": "Final model output",
    "input_tokens": 15,
    "output_tokens": 25,
    "sentiment": "positive/negative/neutral",
    "reasoning_path": ["state_..."],
    "layer_scores": [...]
  },
  "api_key": "API key used"
}
```

---

## 💰 Token System

### Token Quota

- **Free Instance (mtgchatgf)**: Unlimited usage
- **Paid Instance**: Initial 1000 tokens, can be recharged via API

### Token Deduction Rules

Each chat automatically deducts: `input_tokens + output_tokens`

---

## ⚙️ Configuration Files

The program automatically generates the following configuration files on first run:

- `config.json`: Weight path, ports, language settings, etc.
- `api_keys.json`: API key and instance mapping
- `language.json`: Custom language pack
### Configuration Options

```json
{
  "weights_path": "./",
  "port": 4000,
  "cjsl_port": 9000,
  "admin_port": 8080,
  "dIPv4/IPv6 dual-stack

### macOS
- ✅ Full support
- ✅ IPv4/IPv6 dual-stack
- ✅ Supports both Intel and M-series chips

### Linux
- ✅ Full support
### Windows
- ✅ Full support
- ✅ tkinter built-in
- ✅ IPv4/IPv6 dual-stack

### macOS
- ✅ Full support
- ✅ tkinter needs manual installation (`brew install python-tk`)
- ✅ IPv4/IPv6 dual-stack

### Linux
- ✅ Full support
- ✅ tkinter needs manual installation (`sudo apt-get install python3-tk`)
- ✅ IPv4/IPv6 dual-stack
Port already in use
Modify the port numbers in `config.json`:
```json
{
  "port": 4001,
  "cjsl_port": 9001,
  "admin_port": 8081
}
```

### Issue 3: LZ4 compression unavailable
**Solution**: Install lz4 library (required)
```bash
pip install lz4## Issue 2: tkinter import error
**Windows**: Reinstall Python with "tcl/tk" option checked
**macOS**: `brew install python-tk`
**Linux**: `sudo apt-get install python3-tk`

### Issue 3: Port already in use
Modify the port numbers in `config.json`:
```json
{
  "port": 4001,
  "cjsl_port": 9001
}
```

---

## 📝 Development Guide

### Adding Custom Language Pack

1. Create a JSON file:
```json
{
  "title": "Your Title",
  "send": "Send",
  "new_session": "New Session"
}
```

2. In Web Admin: Language Settings → Import Language Pack

### Extending API Endpoints

Add new endpoints in the `do_POST` or `do_GET` methods of the `LLMAPIHandler` class.

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPLv3) - see the [LICENSE](LICENSE) file for details

---

## 👨‍💻 Author

**QianYin MTG AI V-Causal**

- GitHub: https://github.com/dfmtg
- Email: mtgwimtg@163.com

---

## 🙏 Acknowledgments

- Python Community
- All Open Source Contributors

---

## 📌 Project Status

![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.2.26orange)

---

**⭐ If this project helps you, please give us a Star!**

**🚀 Let's explore the infinite possibilities of serial causal inference together!**
