# QianYin - MTG AI V-Causal

## Next-Generation Serial Causal Inference AI System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Architecture-Serial%20Causal-orange.svg" alt="Architecture">
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

- **Semantic Encoder**: 4096-dimensional vector space
- **QKV Serial Attention**: Independent QKV computation per layer
- **State Transition Mechanism**: State-based causal inference
- **Phrase Learner**: Learns phrase patterns from conversations
- **Personality Reward System**: Adaptive personality adjustment

---

## 🚀 Installation & Usage

### Requirements

- Python 3.8 or higher
- tkinter (usually comes with Python)
- psutil (optional, for CPU/memory monitoring)

### Installation Steps

```bash
# 1. Clone the project
git clone https://github.com/dfmtg/QianYin-MTG-AI-V-Causal.git
cd QianYin-MTG-AI-V-Causal

# 2. (Optional) Install psutil for hardware monitoring
pip install psutil

# 3. Run the program
python "MTG AI V-Causal.py"
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

#### 4. API Server
- **Main Port (4000)**: Full API interface requiring API key
- **CISL Port (9000)**: Free interface without authentication

#### 5. Model Weight Management
- Auto-save weight files
- One-click backup and restore
- Custom storage path

#### 6. Hardware Monitoring
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
  "input": "Hello, please introduce yourself"
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
    "sentiment": "positive"
  },
  "api_key": "your_api_key"
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

#### Instance Management
```http
POST /create_instance    # Create new instance
POST /delete_instance    # Delete instance (requires api_key)
POST /update_tokens      # Update token balance (requires api_key, amount)
POST /rename_session     # Rename session (requires api_key, new_name)
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
POST /save_model         # Save model (requires api_key, path)
POST /load_model         # Load model (requires api_key, path)
```

### CISL Free Interface (Port 9000)

```http
POST /chat
Content-Type: application/json

{
  "input": "Hello"
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
    "sentiment": "positive/negative/neutral"
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
- `weights_info.json`: Weight version information

---

## 🌐 Cross-Platform Compatibility

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

---

## 🔧 Troubleshooting

### Issue 1: CPU/Memory shows "N/A"
**Solution**: Install psutil
```bash
pip install psutil
```

### Issue 2: tkinter import error
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

2. In GUI: Language Settings → Import Language Pack

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
- Tkinter Team
- All Open Source Contributors

---

## 📌 Project Status

![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-orange)

---

**⭐ If this project helps you, please give us a Star!**

**🚀 Let's explore the infinite possibilities of serial causal inference together!**
