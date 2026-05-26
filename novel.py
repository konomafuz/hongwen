# -*- coding: utf-8 -*-
"""
红文织梦 CLI — 番茄小说女频全自动网文创作管线
沉浸式终端交互程序，基于 DeepSeek 大模型驱动创作。
"""

import os
import re
import sys
import glob
import json
import subprocess
import time
import random

# ----------------- 依赖检测与安装 -----------------
def check_dependencies():
    # 检查 rich 库
    try:
        import rich
    except ImportError:
        print("未找到终端排版库 'rich'，正在自动安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
            print("rich 库安装成功！\n")
        except Exception as e:
            print(f"安装 rich 失败，请手动运行 'pip install rich' 后重试。错误: {e}")
            sys.exit(1)

    # 检查 python-docx 库
    try:
        import docx
    except ImportError:
        print("未找到 word 文档处理库 'python-docx'，正在自动安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
            print("python-docx 库安装成功！\n")
        except Exception as e:
            print(f"安装 python-docx 失败，请手动运行 'pip install python-docx' 后重试。错误: {e}")
            sys.exit(1)

    # 检查 requests 库
    try:
        import requests
    except ImportError:
        print("未找到网络请求库 'requests'，正在自动安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            print("requests 库安装成功！\n")
        except Exception as e:
            print(f"安装 requests 失败，请手动运行 'pip install requests' 后重试。错误: {e}")
            sys.exit(1)

check_dependencies()

# ----------------- 导入 Rich 组件 -----------------
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.markdown import Markdown
from rich.text import Text
from rich.box import ROUNDED, HEAVY, DOUBLE, SIMPLE_HEAVY
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
import requests

# Windows 终端 UTF-8 兼容：强制标准输出使用 UTF-8 编码
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

console = Console(force_terminal=True)

# ═══════════════════════════════════════════════════════════════
#  红文织梦 — 主题色彩系统
# ═══════════════════════════════════════════════════════════════
# 主色调：绛红 / 琥珀金 / 烟粉 / 墨青
C_BRAND       = "bold #C77A8E"       # 品牌绛红
C_BRAND_DIM   = "#A8687A"            # 暗绛
C_GOLD        = "bold #FFB703"       # 琥珀金
C_GOLD_DIM    = "#FB8500"            # 暗金
C_PINK        = "#F4A3B5"            # 烟粉
C_JADE        = "#2A9D8F"            # 翠玉
C_INK         = "#264653"            # 墨青
C_CREAM       = "#FAF3E0"            # 素绢
C_SILVER      = "dim #A8A8A8"        # 月银
C_SUCCESS     = "bold #06D6A0"       # 翡翠绿
C_ERROR       = "bold #D4728C"       # 胭脂红
C_WARN        = "bold #FFD166"       # 鹅黄
C_STEP        = "bold #8338EC"       # 紫烟

# ═══════════════════════════════════════════════════════════════
#  氛围装饰元素
# ═══════════════════════════════════════════════════════════════
BANNER = r"""
[#C77A8E]
    ██╗  ██╗ ██████╗ ███╗   ██╗ ██████╗ ██╗    ██╗███████╗███╗   ██╗
    ██║  ██║██╔═══██╗████╗  ██║██╔════╝ ██║    ██║██╔════╝████╗  ██║
    ███████║██║   ██║██╔██╗ ██║██║  ███╗██║ █╗ ██║█████╗  ██╔██╗ ██║
    ██╔══██║██║   ██║██║╚██╗██║██║   ██║██║███╗██║██╔══╝  ██║╚██╗██║
    ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝╚███╔███╔╝███████╗██║ ╚████║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═══╝
[/#C77A8E]"""

DIVIDER_CHARS = "─═━╌┈"

ATMOSPHERE_QUOTES = [
    "笔落惊风雨，诗成泣鬼神。",
    "文章本天成，妙手偶得之。",
    "纸上得来终觉浅，绝知此事要躬行。",
    "删繁就简三秋树，领异标新二月花。",
    "吟安一个字，捻断数茎须。",
    "一字之褒，荣于华衮；一字之贬，严于斧钺。",
    "为人性僻耽佳句，语不惊人死不休。",
    "两句三年得，一吟双泪流。",
    "世事洞明皆学问，人情练达即文章。",
    "好风凭借力，送我上青云。",
    "落霞与孤鹜齐飞，秋水共长天一色。",
    "千淘万漉虽辛苦，吹尽狂沙始到金。",
]

STEP_ICONS = {
    "outline":  "📜",
    "draft":    "✍️",
    "review":   "🔍",
    "rewrite":  "💎",
    "export":   "📦",
    "init":     "🏗️",
    "trend":    "📊",
    "status":   "📋",
    "success":  "✨",
    "error":    "💔",
    "warn":     "⚠️",
    "chapter":  "📖",
    "quill":    "🪶",
}

def print_divider(style="red", char="━"):
    """打印全宽装饰分隔线"""
    width = min(console.width, 80)
    console.print(f"[{style}]{char * width}[/{style}]")

def print_section_header(title, icon="", style=C_BRAND):
    """打印带装饰的段落标题"""
    console.print()
    console.print(Rule(
        f" {icon} {title} ",
        style="#C77A8E",
        characters="═"
    ))
    console.print()

def print_atmosphere_quote():
    """输出一句随机的古风创作名言，增加氛围感"""
    quote = random.choice(ATMOSPHERE_QUOTES)
    console.print(Align.center(
        Text(f"『 {quote} 』", style=f"italic {C_PINK}")
    ))

def print_ok(msg):
    console.print(f"  {STEP_ICONS['success']} [{C_SUCCESS}]{msg}[/{C_SUCCESS}]")

def print_err(msg):
    console.print(f"  {STEP_ICONS['error']} [{C_ERROR}]{msg}[/{C_ERROR}]")

def print_warn(msg):
    console.print(f"  {STEP_ICONS['warn']} [{C_WARN}]{msg}[/{C_WARN}]")

def print_step(step_num, total, msg):
    bar_filled = "█" * step_num
    bar_empty  = "░" * (total - step_num)
    console.print(
        f"  [{C_STEP}][ {bar_filled}{bar_empty} {step_num}/{total} ][/{C_STEP}] "
        f"[white]{msg}[/white]"
    )

# ═══════════════════════════════════════════════════════════════
#  全局路径与状态
# ═══════════════════════════════════════════════════════════════
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.getcwd()

# ----------------- 自动读取 .env 配置文件 -----------------
def load_dotenv():
    env_path = os.path.join(WORKSPACE_DIR, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k == "DEEPSEEK_API_KEY" and v:
                            os.environ["DEEPSEEK_API_KEY"] = v
        except Exception:
            pass

load_dotenv()

STATE_FILE = os.path.join(WORKSPACE_DIR, "novel_project.json")
STYLE_CONFIG_FILE = os.path.join(WORKSPACE_DIR, "styles_config.json")
KB_PATH = os.path.join(SRC_DIR, "knowledge_base", "hot_books_kb.md")
STATS_PATH = os.path.join(SRC_DIR, "scratch", "statistics_output.txt")
SETTINGS_FILE = os.path.join(WORKSPACE_DIR, "novel_core_settings.md")
SYNOPSIS_FILE = os.path.join(WORKSPACE_DIR, "novel_tags_synopsis.md")
REFERENCES_DIR = os.path.join(SRC_DIR, ".claude", "skills", "tomato-novel-female", "references")

# ----------------- 品类/题材模板配置 -----------------
def load_book_type_config(book_type):
    config_path = os.path.join(SRC_DIR, ".agents", "skills", "book_types_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return cfg.get(book_type, cfg.get("female_novel"))
        except Exception:
            pass
    return {
        "genre_name": "女频长篇",
        "format": "novel",
        "chapter_word_limit": { "min": 1800, "max": 2200, "target": 2000 },
        "rules": {
            "short_paragraph": "非对话的十个字以内单独成段短句，整章累计不超过 15 处；严禁机械化、套路化堆砌“没有...没有...他只是...”这类车轱辘短句排比并单独成段。",
            "system_prompt_story": "你是一位精通番茄女频爆款的核心设定架构师。",
            "system_prompt_synopsis": "你是一位精通番茄女频爆款简介与文案策划专家。",
            "system_prompt_outline": "你是一位精通女频网文架构的大纲策划专家。",
            "system_prompt_draft": "你是一位番茄小说女频热门作者，文风生活化、有颗粒感。",
            "system_prompt_review": "你是一位毒舌但专业的女频网文质检编辑，专砍废话、注水和AI味。"
        }
    }

def get_template_path(skill_name, book_type, file_name):
    path = os.path.join(SRC_DIR, ".agents", "skills", skill_name, "references", book_type, file_name)
    if os.path.exists(path):
        return path
    # 兼容性备用路径
    return os.path.join(REFERENCES_DIR, file_name)
TOOLS_DIR = os.path.join(SRC_DIR, ".claude", "skills", "tomato-novel-female", "tools")
DRAFT_REFERENCES_DIR = os.path.join(SRC_DIR, ".agents", "skills", "novel-draft-writer", "references")
RAG_REFERENCES_DIR = os.path.join(SRC_DIR, ".agents", "skills", "novel-rag-voice", "references")
STYLE_REFERENCES_DIR = os.path.join(DRAFT_REFERENCES_DIR, "styles")
STYLE_REFERENCE_FILES = {
    "古言雅致": "guyan-yazhi.md",
    "现言甜宠": "xianyan-tiange.md",
    "幽默吐槽": "youmo-tucao.md",
    "悬疑冷峻": "xuanyi-lengjun.md",
    "热血爽文": "rexue-shuangwen.md",
}
STYLE_SHORTCUTS = {
    "style1": "古言雅致",
    "style2": "现言甜宠",
    "style3": "幽默吐槽",
    "style4": "悬疑冷峻",
    "style5": "热血爽文",
}
CHAPTER_LENGTH_RULE = "字数必须严格在 1800-2200 字之间，目标约 2000 字，绝对不能超过 2200 字，也不能少于 1800 字。"
SHORT_PARAGRAPH_RULE = "非对话的十个字以内单独成段短句，整章累计不超过 15 处；严禁机械化、套路化堆砌“没有...没有...他只是...”这类车轱辘短句排比并单独成段。"

STYLE_ANALYSIS_SYSTEM_PROMPT = """你是一位资深的网文风格金牌分析师。你的任务是分析用户提供的参考小说文本片段，并用极其精炼、具象且颗粒感强的语言，提炼出它的文风特征描述。
请严格从以下几个维度提炼：
1. 句式与语言节奏（如：短句为主、叙事紧凑、白描多于修饰等）
2. 词汇与感情色彩（如：市井口语、带冷色调、华丽浓郁等）
3. 氛围与颗粒感细节（如：强调动作微表情、重心理吐槽、强网感幽默等）

注意：
1. 不要输出任何分析过程，只需给出一个 100-200 字以内的纯特征描述段落。
2. 描述必须直指核心，方便写作大模型直接作为 Prompt 融入使用。
3. 必须使用中文输出，直接给出提炼内容即可。"""

def load_style_config():
    default_config = {
        "current_style": "",
        "presets": {
            "古言雅致": "半文半白、用词典雅、意境优美、注重礼仪与环境描写，偏向传统且有文化底蕴的古代言情风格。",
            "现言甜宠": "轻松活泼、日常颗粒感强、甜度超标、注重肢体语言与微表情描写的现代豪门/甜宠风格。",
            "幽默吐槽": "网感极佳、玩梗密集、心理活动活跃、节奏明快爆笑的系统吐槽沙雕爽文风格。",
            "悬疑冷峻": "言简意赅、细节冷峻、侧重心理侧写与氛围营造的女强/悬疑/复仇大女主风格。",
            "热血爽文": "节奏极快、爽点密集、强调情绪张力与即时反馈、反击打脸痛快淋漓的快节奏爽文风格。"
        },
        "custom": {}
    }
    if os.path.exists(STYLE_CONFIG_FILE):
        try:
            with open(STYLE_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print_err(f"加载文风配置文件失败，正在使用默认配置。错误: {e}")
    
    # 自动创建默认配置
    try:
        with open(STYLE_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print_err(f"创建默认文风配置文件失败: {e}")
    return default_config

def save_style_config(config):
    try:
        with open(STYLE_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print_err(f"保存文风配置文件失败: {e}")

def get_active_style_desc(config):
    active_style = config.get("current_style", "现言甜宠")
    if not active_style:
        return "默认", "通用番茄女频文风：生活化、有颗粒感，优先保证人物声音清晰、节奏流畅、适配当前章节内容。"
    if active_style in config.get("presets", {}):
        return active_style, config["presets"][active_style]
    elif active_style in config.get("custom", {}):
        return active_style, config["custom"][active_style]
    return "现言甜宠", config.get("presets", {}).get("现言甜宠", "")

def read_text_if_exists(path):
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def first_existing_path(*paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return paths[0] if paths else ""

def resolve_style_name(name):
    if not name:
        return ""
    key = name.lower()
    return STYLE_SHORTCUTS.get(key, name)

def build_style_prompt():
    config = load_style_config()
    active_style, active_desc = get_active_style_desc(config)
    index_text = read_text_if_exists(os.path.join(STYLE_REFERENCES_DIR, "style-index.md"))
    style_file = STYLE_REFERENCE_FILES.get(active_style)
    style_ref = read_text_if_exists(os.path.join(STYLE_REFERENCES_DIR, style_file)) if style_file else ""
    
    if not style_ref:
        if active_style in config.get("custom", {}):
            template = read_text_if_exists(os.path.join(STYLE_REFERENCES_DIR, "custom-style-template.md"))
            style_ref = f"# {active_style}\n\n{active_desc}\n\n{template}".strip()
        else:
            style_ref = read_text_if_exists(os.path.join(STYLE_REFERENCES_DIR, "default.md"))
            
    style_prompt = "\n\n".join(part for part in [index_text, style_ref] if part).strip()
    return active_style, active_desc, style_prompt

# ═══════════════════════════════════════════════════════════════
#  DeepSeek API 客户端
# ═══════════════════════════════════════════════════════════════
def call_deepseek(prompt, system_prompt=""):
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print_err("未检测到 DEEPSEEK_API_KEY 环境变量！")
        console.print(f"  [{C_WARN}]请在终端设置环境变量，例如:[/{C_WARN}]")
        console.print(f"  [{C_JADE}]Windows Powershell:  $env:DEEPSEEK_API_KEY='your_key_here'[/{C_JADE}]")
        console.print(f"  [{C_JADE}]Windows CMD:         set DEEPSEEK_API_KEY=your_key_here[/{C_JADE}]")
        raise ValueError("DEEPSEEK_API_KEY is not set.")
        
    if not api_key.isascii() or len(api_key) > 128:
        print_err("检测到当前载入的 DEEPSEEK_API_KEY 格式非法！")
        console.print(f"  [{C_WARN}]密钥长度必须小于 128 位，且只能包含 ASCII 字符（通常以 sk- 开头）。[/{C_WARN}]")
        console.print(f"  [{C_WARN}]请检查您的环境变量设置或本地 .env 文件，确保没有复制多余的汉字或空格。[/{C_WARN}]")
        raise ValueError("Invalid DEEPSEEK_API_KEY format (contains non-ASCII characters or length is too long).")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=120)
    if response.status_code != 200:
        raise Exception(f"DeepSeek API 错误 ({response.status_code}): {response.text}")
    
    res_json = response.json()
    return res_json["choices"][0]["message"]["content"]

# ═══════════════════════════════════════════════════════════════
#  项目状态管理
# ═══════════════════════════════════════════════════════════════
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print_err(f"加载状态文件失败: {e}")
    
    existing = try_recover_state()
    if existing:
        save_state(existing)
        return existing
        
    return {
        "novel_title": "未命名小说",
        "synopsis": "暂无简介",
        "current_step": 0,
        "settings_created": False,
        "outline_created": False,
        "chapters": {}
    }

def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print_err(f"保存状态文件失败: {e}")

def try_recover_state():
    """从根目录下已存在的文件中恢复项目状态"""
    if os.path.exists(SETTINGS_FILE):
        title = "绑定吃瓜系统，我靠剧透爆红了"
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                match = re.search(r"《([^》]+)》", first_line)
                if match:
                    title = match.group(1)
        except Exception:
            pass
        
        chapters = {}
        chapter_files = glob.glob(os.path.join(WORKSPACE_DIR, "chapter_*.md"))
        
        def get_chap_num(filepath):
            basename = os.path.basename(filepath)
            match = re.search(r"chapter_(\d+)", basename)
            return int(match.group(1)) if match else 0
            
        chapter_files.sort(key=get_chap_num)
        for f in chapter_files:
            num = get_chap_num(f)
            if num > 0:
                chap_title = f"第{num}章"
                try:
                    with open(f, "r", encoding="utf-8") as cf:
                        first_l = cf.readline().strip()
                        t_match = re.match(r"^#\s*第\s*(\d+)\s*[章回]\s*[:：\s]*\s*(.*)$", first_l)
                        if t_match:
                            chap_title = t_match.group(2).strip()
                        else:
                            chap_title = first_l.lstrip("#").strip()
                except Exception:
                    pass
                chapters[str(num)] = {
                    "title": chap_title,
                    "file": os.path.basename(f),
                    "status": "completed"
                }
        
        return {
            "novel_title": title,
            "synopsis": "基于已有文件自动还原",
            "current_step": 8,
            "settings_created": True,
            "outline_created": True,
            "chapters": chapters
        }
    return None

# ═══════════════════════════════════════════════════════════════
#  爆款库 Markdown 解析
# ═══════════════════════════════════════════════════════════════
def parse_markdown_kb():
    if not os.path.exists(KB_PATH):
        return []
    
    try:
        with open(KB_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print_err(f"读取知识库失败: {e}")
        return []
        
    books = []
    parts = re.split(r'###\s+《', content)
    for part in parts[1:]:
        lines = part.strip().split('\n')
        title_match = re.match(r'([^》]+)》', lines[0])
        if not title_match:
            continue
        title = title_match.group(1)
        
        book = {"title": title, "abstract": ""}
        in_abstract = False
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- **作者**：'):
                book['author'] = line.replace('- **作者**：', '').strip()
            elif line.startswith('- **分类**：'):
                book['category'] = line.replace('- **分类**：', '').strip()
            elif line.startswith('- **标签**：'):
                book['tags'] = line.replace('- **标签**：', '').strip()
            elif line.startswith('- **字数**：'):
                wc = line.replace('- **字数**：', '').replace('字', '').strip()
                book['word_count'] = wc
            elif line.startswith('- **阅读热度**：'):
                book['read_count'] = line.replace('- **阅读热度**：', '').strip()
            elif line.startswith('- **榜单分类**：'):
                book['rank_type'] = line.replace('- **榜单分类**：', '').strip()
            elif line.startswith('- **书籍ID**：'):
                book['book_id'] = line.replace('- **书籍ID**：', '').strip()
            elif line.startswith('- **入库时间**：'):
                book['insert_time'] = line.replace('- **入库时间**：', '').strip()
            elif line.startswith('- **简介**：'):
                in_abstract = True
            elif in_abstract:
                if line.startswith('>') or line.startswith('  >'):
                    abstract_line = re.sub(r'^\s*>\s*', '', line)
                    book['abstract'] += abstract_line + "\n"
                elif line.strip() == '' or line.startswith('---'):
                    in_abstract = False
                else:
                    book['abstract'] += line + "\n"
        book['abstract'] = book['abstract'].strip()
        books.append(book)
    return books

def cmd_help():
    print_section_header("命令速查手册", STEP_ICONS['quill'])

    table = Table(
        box=HEAVY,
        border_style="#C77A8E",
        header_style="bold #FFB703 on #1A1A2E",
        title="[bold #C77A8E]红文织梦[/bold #C77A8E] [#F4A3B5]· 全部可用命令[/#F4A3B5]",
        title_style="bold",
        padding=(0, 2),
        show_lines=True,
    )
    table.add_column("命  令", style="bold #FFB703", width=16, justify="center")
    table.add_column("参  数", style="#F4A3B5", width=12, justify="center")
    table.add_column("功 能 描 述", style="white", min_width=36)
    
    table.add_row(
        "status", "—",
        "📋 显示当前小说的进度状态、字数统计及完成度面板"
    )
    table.add_row(
        "init", "—",
        "🏗️  在工作区初始化小说项目（从零开始或继承现有设定）"
    )
    table.add_row(
        "write", "[N]",
        "✍️  自动写接下来的 N 章（含细纲→初稿→自审→定稿全流程）"
    )
    table.add_row(
        "review", "<章节号>",
        "🔍 单独对某一章运行人设/逻辑自审并显示审查报告"
    )
    table.add_row(
        "trend fetch", "—",
        "🌐 抓取最新番茄爆款书籍数据并分析生成趋势报告"
    )
    table.add_row(
        "trend kb", "—",
        "📚 列出知识库中已存在的所有爆款女频小说"
    )
    table.add_row(
        "trend stats", "—",
        "📊 展示爆款库题材、标签及高频词的统计可视化面板"
    )
    table.add_row(
        "export", "—",
        "📦 按正确顺序合并所有章节并编译导出为排版好的 Word 文档"
    )
    table.add_row(
        "style", "[show/set/learn]",
        "🎨 文风管理（支持 show 列表、set 切换、learn <文件> 仿写）"
    )
    table.add_row(
        "style1-style5", "—",
        "⚡ 文风快捷切换：style1 古言 / style2 现言 / style3 吐槽 / style4 悬疑 / style5 热血"
    )
    table.add_row(
        "rag", "—",
        "🔍 手动运行 RAG 检索语感小抄进行测试"
    )
    table.add_row(
        "update", "—",
        "🌐 联网更新 RAG 热梗与语感知识库权重"
    )
    table.add_row(
        "help", "—",
        "❓ 显示此帮助信息"
    )
    table.add_row(
        "exit / quit", "—",
        "🚪 安全退出交互式控制台"
    )
    
    console.print(Align.center(table))

def cmd_status(state):
    print_section_header("项目全貌", STEP_ICONS['status'])

    # 构建进度条可视化
    total_steps = 4  # 设定 / 大纲 / 章节 / 导出
    done = sum([
        state.get('settings_created', False),
        state.get('outline_created', False),
        len(state.get('chapters', {})) > 0,
        os.path.exists(os.path.join(WORKSPACE_DIR, f"{state['novel_title']}.docx"))
    ])
    pct = int(done / total_steps * 100)
    bar_len = 30
    filled = int(bar_len * done / total_steps)
    bar = f"[#C77A8E]{'█' * filled}[/#C77A8E][#3D3D3D]{'░' * (bar_len - filled)}[/#3D3D3D]"

    settings_badge = f"[{C_SUCCESS}]✔ 已建立[/{C_SUCCESS}]" if state.get('settings_created') else f"[{C_ERROR}]✘ 未建立[/{C_ERROR}]"
    outline_badge  = f"[{C_SUCCESS}]✔ 已生成[/{C_SUCCESS}]" if state.get('outline_created')  else f"[{C_ERROR}]✘ 未生成[/{C_ERROR}]"

    # 统计总字数
    total_words = 0
    for k, ch in state.get("chapters", {}).items():
        fpath = os.path.join(WORKSPACE_DIR, ch["file"])
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    total_words += len(f.read())
            except Exception:
                pass

    book_type = state.get("book_type", "female_novel")
    book_cfg = load_book_type_config(book_type)
    genre_display = book_cfg.get("genre_name", "女频长篇")
    unit_name = "集" if book_cfg.get("format") == "script" else "章"

    status_content = (
        f"[bold #C77A8E]📕 书  名[/bold #C77A8E]   [bold white]《{state['novel_title']}》[/bold white]\n"
        f"[bold #C77A8E]🎨 题材类型[/bold #C77A8E]   [bold white]{genre_display}[/bold white]\n"
        f"[bold #C77A8E]📝 简  介[/bold #C77A8E]   [white]{state['synopsis'][:60]}{'...' if len(state['synopsis']) > 60 else ''}[/white]\n"
        f"\n"
        f"[bold #FFB703]⚙  核心设定[/bold #FFB703]  {settings_badge}\n"
        f"[bold #FFB703]📐 大纲状态[/bold #FFB703]  {outline_badge}\n"
        f"[bold #FFB703]📖 已写内容[/bold #FFB703]  [{C_GOLD}]{len(state['chapters'])} {unit_name}[/{C_GOLD}]\n"
        f"[bold #FFB703]📊 累计字数[/bold #FFB703]  [{C_GOLD}]{total_words:,} 字[/{C_GOLD}]\n"
        f"\n"
        f"[bold #F4A3B5]完成进度[/bold #F4A3B5]  {bar}  [{C_GOLD}]{pct}%[/{C_GOLD}]"
    )

    console.print(Panel(
        status_content,
        title=f"[bold #FFB703]🪶 红文织梦 · 项目仪表盘[/bold #FFB703]",
        subtitle=f"[{C_SILVER}]Powered by DeepSeek[/{C_SILVER}]",
        border_style="#C77A8E",
        box=DOUBLE,
        padding=(1, 3),
    ))
    
    if state.get("chapters"):
        table = Table(
            box=ROUNDED,
            border_style="#A8687A",
            header_style="bold #FFB703 on #1A1A2E",
            show_lines=True,
            padding=(0, 1),
        )
        table.add_column(f"内  容", style="bold #FFB703", justify="center", width=10)
        table.add_column(f"标  题", style="white", min_width=24)
        table.add_column("文 件 名", style=C_SILVER, min_width=18)
        table.add_column("字  数", style="#2A9D8F", justify="right", width=10)
        table.add_column("状  态", style=C_SUCCESS, justify="center", width=10)
        
        sorted_keys = sorted(state["chapters"].keys(), key=int)
        for k in sorted_keys:
            ch = state["chapters"][k]
            # 读取字数
            wc = "—"
            fpath = os.path.join(WORKSPACE_DIR, ch["file"])
            if os.path.exists(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        wc = f"{len(f.read()):,}"
                except Exception:
                    pass
            table.add_row(
                f"第 {k} {unit_name}",
                ch["title"],
                ch["file"],
                wc,
                "✔ 定稿"
            )
        console.print(Align.center(table))
    else:
        console.print(Align.center(
            Text(f"尚无内容，输入 write 开始创作你的故事吧 ✨", style=f"italic {C_PINK}")
        ))

def cmd_trend_kb():
    books = parse_markdown_kb()
    if not books:
        print_err("未在知识库中找到爆款书籍数据。")
        return

    print_section_header("爆款知识库", "📚")
        
    table = Table(
        title="[bold #C77A8E]番茄女频爆款小说知识库[/bold #C77A8E]",
        box=ROUNDED,
        border_style="#A8687A",
        header_style="bold #FFB703 on #1A1A2E",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("ID", style=C_SILVER, justify="center", width=8)
    table.add_column("书名", style="bold #C77A8E", min_width=20)
    table.add_column("作者", style="white", width=12)
    table.add_column("分类", style="#F4A3B5", width=10)
    table.add_column("阅读热度", style="bold #FFB703", justify="right", width=12)
    table.add_column("标签", style="#2A9D8F", min_width=16)
    table.add_column("入库日期", style=C_SILVER, justify="center", width=12)
    
    for b in books:
        table.add_row(
            b.get("book_id", "N/A"),
            f"《{b['title']}》",
            b.get("author", "未知"),
            b.get("category", "未分类"),
            b.get("read_count", "0"),
            b.get("tags", "无"),
            b.get("insert_time", "N/A")
        )
    console.print(Align.center(table))

def cmd_trend_stats():
    if not os.path.exists(STATS_PATH):
        print_warn("未找到统计缓存，正在运行分析脚本...")
        script_path = os.path.join(SRC_DIR, "scratch", "analyze_kb.py")
        if os.path.exists(script_path):
            subprocess.run([sys.executable, script_path], stdout=subprocess.DEVNULL)
        else:
            print_err("未找到分析脚本 analyze_kb.py，无法分析。")
            return
            
    try:
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")
    except Exception as e:
        print_err(f"读取统计数据失败: {e}")
        return

    print_section_header("大数据统计看板", "📊")
    console.print(Panel(
        "[bold #FFB703]知识库大数据统计看板[/bold #FFB703]\n[#F4A3B5]基于番茄女频高分榜单深度分析[/#F4A3B5]",
        border_style="#C77A8E",
        box=DOUBLE,
        padding=(0, 2),
    ))
    
    section = ""
    table = None
    for line in lines:
        if "CATEGORY DISTRIBUTION" in line:
            section = "cat"
            console.print(f"\n  [bold #F4A3B5]🏷️  爆款分类及核心题材分布[/bold #F4A3B5]")
            table = Table(box=ROUNDED, border_style="#A8687A", header_style="bold #FFB703")
            table.add_column("分类/题材", style="bold #C77A8E")
            table.add_column("数量", justify="center")
            table.add_column("占比", justify="right", style="#2A9D8F")
            table.add_column("爆款代表作", style=C_SILVER)
            continue
        elif "TAG FREQUENCY TOP 20" in line:
            section = "tag"
            console.print(f"\n  [bold #2A9D8F]🔖 Top 20 爆款核心元素/标签频次[/bold #2A9D8F]")
            table = Table(box=ROUNDED, border_style="#A8687A", header_style="bold #FFB703")
            table.add_column("排名", justify="center", width=6)
            table.add_column("元素/爽点", style="bold #C77A8E")
            table.add_column("出现频次", justify="center")
            table.add_column("占比", justify="right", style="#2A9D8F")
            table.add_column("最常搭配元素", style=C_SILVER)
            continue
        elif "TAG COMBINATIONS TOP 10" in line:
            section = "combo"
            console.print(f"\n  [bold #FFB703]💎 黄金CP/爽点组合 Top 10[/bold #FFB703]")
            table = Table(box=ROUNDED, border_style="#A8687A", header_style="bold #FFB703")
            table.add_column("排名", justify="center", width=6)
            table.add_column("黄金组合", style="bold #C77A8E")
            table.add_column("作品数", justify="center")
            table.add_column("代表作", style=C_SILVER)
            continue
        elif "KEYWORDS TOP 30" in line:
            section = "keyword"
            console.print(f"\n  [bold #C77A8E]🔥 爆款书名与简介核心高频词[/bold #C77A8E]")
            table = Table(box=ROUNDED, border_style="#A8687A", header_style="bold #FFB703")
            table.add_column("排名", justify="center", width=6)
            table.add_column("高频词汇", style="bold #C77A8E")
            table.add_column("词频数", justify="center", style="#FFB703")
            continue
        elif line.startswith("Total books"):
            console.print(f"\n  [{C_SUCCESS}]{line}[/{C_SUCCESS}]")
            continue
            
        if line.strip().startswith("|") and table:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            table.add_row(*parts)
            
        if line.strip() == "" and table:
            console.print(table)
            table = None
            
    if table:
        console.print(table)

def cmd_trend_fetch():
    print_section_header("抓取爆款数据", "🌐")
    scraper = os.path.join(TOOLS_DIR, "fanqie_scraper.py")
    report = os.path.join(TOOLS_DIR, "fanqie_report.py")
    
    if not os.path.exists(scraper):
        print_err("未找到爬虫脚本，无法抓取。")
        return
        
    try:
        with console.status(f"[bold #C77A8E]🌐 抓取每日高分排行榜数据中...", spinner="dots12", spinner_style="#FFB703"):
            subprocess.run([sys.executable, scraper], stdout=subprocess.DEVNULL)
            
        with console.status(f"[bold #C77A8E]📊 分析题材趋势并生成报告...", spinner="dots12", spinner_style="#FFB703"):
            subprocess.run([sys.executable, report], stdout=subprocess.DEVNULL)
            
        print_ok("抓取与分析成功！趋势报告已保存至 references/step00-trend-analysis.md")
    except Exception as e:
        print_err(f"运行抓取失败: {e}")

def cmd_init(state):
    # 检测 API Key 是否设置，若缺失或格式非法则提示输入并导入会话
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    is_valid = api_key and api_key.isascii() and len(api_key) < 128
    
    if is_valid:
        print_section_header("API 密钥检测", "🔑")
        masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "..."
        print_ok(f"已检测到 DEEPSEEK_API_KEY 密钥: [bold white]{masked_key}[/bold white] (已自动载入会话)")
        console.print()
    else:
        print_section_header("导入 API 密钥", "🔑")
        if api_key:
            console.print(f"  [{C_ERROR}]检测到当前环境变量或 .env 中的 DEEPSEEK_API_KEY 格式不正确！[/{C_ERROR}]")
            console.print(f"  [{C_WARN}]错误原因：密钥包含非 ASCII 字符（如汉字）或长度异常（当前长度 {len(api_key)}，正常密钥通常小于 64 位且以 sk- 开头）。[/{C_WARN}]")
        else:
            console.print(f"  [{C_WARN}]未检测到 DEEPSEEK_API_KEY 环境变量或 .env 配置文件！[/{C_WARN}]")
            
        console.print(f"  [{C_SILVER}]如果您已经有密钥，可在此直接粘贴。或者，您也可以先在终端执行以下口令设置全局环境变量（直接复制即可）：[/{C_SILVER}]")
        console.print(f"  • Windows Powershell: [bold #C77A8E]$env:DEEPSEEK_API_KEY='your_key_here'[/bold #C77A8E]")
        console.print(f"  • Windows CMD:        [bold #C77A8E]set DEEPSEEK_API_KEY=your_key_here[/bold #C77A8E]")
        console.print(f"  • Linux / macOS:      [bold #C77A8E]export DEEPSEEK_API_KEY='your_key_here'[/bold #C77A8E]\n")
        
        while True:
            key = Prompt.ask(f"  [{C_GOLD}]🔑 请输入/粘贴您的 DeepSeek API Key（回车留空则终止初始化）[/{C_GOLD}]").strip()
            if not key:
                print_err("API Key 不能为空，项目初始化终止。")
                return
            if not key.isascii() or len(key) >= 128:
                print_err("输入的 API Key 格式不正确！密钥不能包含汉字等非 ASCII 字符，且长度不能超过 128 位。请重新输入。")
                continue
            break
            
        os.environ["DEEPSEEK_API_KEY"] = key
        
        # 保存到本地 .env 文件中
        env_path = os.path.join(WORKSPACE_DIR, ".env")
        try:
            lines = []
            has_key = False
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            
            new_lines = []
            for line in lines:
                if line.strip().startswith("DEEPSEEK_API_KEY="):
                    new_lines.append(f"DEEPSEEK_API_KEY={key}\n")
                    has_key = True
                else:
                    new_lines.append(line)
            if not has_key:
                if new_lines and not new_lines[-1].endswith("\n"):
                    new_lines[-1] += "\n"
                new_lines.append(f"DEEPSEEK_API_KEY={key}\n")
                
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            print_ok("API Key 已成功导入，并已保存至本地 .env 文件中，下次无需重新输入。")
        except Exception as e:
            print_ok("API Key 已成功导入当前运行会话！")
            print_warn(f"无法将 API Key 保存至 .env 文件: {e}")
            
        # 确保 .env 在 .gitignore 中
        gitignore_path = os.path.join(WORKSPACE_DIR, ".gitignore")
        try:
            needs_append = True
            if os.path.exists(gitignore_path):
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if ".env" in content.split():
                        needs_append = False
            if needs_append:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write("\n# Environment variables\n.env\n")
        except Exception:
            pass
        console.print()

    if state.get("settings_created") and state.get("outline_created"):
        overwrite = Confirm.ask(f"  [{C_WARN}]检测到当前项目已完成初始化。重新初始化会清空章节进度，是否确认？[/{C_WARN}]")
        if not overwrite:
            return

    print_section_header("初始化创作项目", STEP_ICONS['init'])
    
    use_existing = False
    if os.path.exists(SETTINGS_FILE):
        use_existing = Confirm.ask(f"  [{C_WARN}]检测到工作区已存在核心设定文件，是否基于该文件初始化？[/{C_WARN}]")
        
    if use_existing:
        recovered = try_recover_state()
        if recovered:
            state.update(recovered)
            save_state(state)
            print_ok("项目已成功基于现有核心设定和章节还原！")
            cmd_status(state)
            return
            
    # 从零开始选择题材并生成
    console.print(f"  [{C_PINK}]请选择新作品的题材/体裁类型：[/{C_PINK}]")
    console.print(f"  1. 女频长篇")
    console.print(f"  2. 男频长篇")
    console.print(f"  3. 精品短篇")
    console.print(f"  4. 短剧剧本")
    
    type_choice = Prompt.ask(f"  [{C_GOLD}]请选择数字 (1-4)[/{C_GOLD}]", default="1", choices=["1", "2", "3", "4"])
    type_mapping = {
        "1": "female_novel",
        "2": "male_novel",
        "3": "short_story",
        "4": "short_drama"
    }
    book_type = type_mapping[type_choice]
    book_cfg = load_book_type_config(book_type)
    genre_display = book_cfg.get("genre_name", "女频长篇")
    
    # 询问选题信息
    console.print(f"\n  [{C_PINK}]请输入新作品的基本信息：[/{C_PINK}]")
    console.print(f"  [{C_SILVER}]提示：如果您没有创作灵感，可以输入 'r' 让我为您推荐3个爆款选题。[/{C_SILVER}]")
    
    while True:
        title_input = Prompt.ask(f"  [{C_GOLD}]📕 新书名/剧名 (输入 'r' 推荐选题)[/{C_GOLD}]").strip()
        if title_input:
            break
        print_err("书名/剧名不能为空，请重新输入。")
        
    title = ""
    synopsis = ""
    
    if title_input.lower() == 'r':
        # 调用大模型获取 3 个选题建议
        kb_references = ""
        if book_type in ["female_novel", "short_story"]:
            books = parse_markdown_kb()
            if books:
                samples = random.sample(books, min(len(books), 5))
                kb_references = "参考爆款样例：\n" + "\n".join([f"- 《{b['title']}》: {b.get('abstract', '')[:100]}" for b in samples])
                
        recommend_prompt = (
            f"你是一个爆款网络小说/剧本策划师。用户想写一本 【{genre_display}】 类型的作品，但他目前没有任何灵感，不知道写什么。\n"
            f"请从市场爆款逻辑出发，为他量身定制 3 个极具新意、极具冲突和卖点的选题创意选择。\n\n"
            f"{kb_references}\n"
            f"请严格按以下 JSON 格式输出，不要输出任何其他的解释、前言、后记或 Markdown 标记：\n"
            f"[\n"
            f"  {{\n"
            f"    \"title\": \"书名/剧名\",\n"
            f"    \"synopsis\": \"核心选题概念与爽点简介\"\n"
            f"  }},\n"
            f"  {{\n"
            f"    \"title\": \"书名/剧名\",\n"
            f"    \"synopsis\": \"核心选题概念与爽点简介\"\n"
            f"  }},\n"
            f"  {{\n"
            f"    \"title\": \"书名/剧名\",\n"
            f"    \"synopsis\": \"核心选题概念与爽点简介\"\n"
            f"  }}\n"
            f"]"
        )
        
        with console.status(f"[bold #C77A8E]  ✨ 正在为您检索爆款库并生成3个定制选题建议...", spinner="dots12", spinner_style="#FFB703"):
            try:
                res_raw = call_deepseek(recommend_prompt, "你是一个小说选题专家。你必须直接返回干净的JSON数组。")
                json_clean = re.sub(r"```(?:json)?", "", res_raw).strip()
                options = json.loads(json_clean)
            except Exception as e:
                print_err(f"选题推荐生成失败 ({e})，将切换回手动输入。")
                options = []
                
        if options and len(options) >= 3:
            console.print(f"\n  [bold #06D6A0]✨ 为您推荐的 3 个爆款选题：[/bold #06D6A0]")
            for idx, opt in enumerate(options[:3]):
                console.print(f"  [bold #FFB703]{idx+1}. 《{opt['title']}》[/bold #FFB703]")
                console.print(f"     [white]{opt['synopsis']}[/white]\n")
            console.print(f"  [bold #FFB703]4. 手动输入自定义书名和简介[/bold #FFB703]\n")
            
            choice = Prompt.ask(f"  [{C_GOLD}]请选择 (1-4)[/{C_GOLD}]", choices=["1", "2", "3", "4"], default="1")
            if choice in ["1", "2", "3"]:
                selected = options[int(choice) - 1]
                title = selected["title"]
                synopsis = selected["synopsis"]
                console.print(f"  [{C_SUCCESS}]✔ 已采纳选题：《{title}》[/{C_SUCCESS}]")
            else:
                while True:
                    title = Prompt.ask(f"  [{C_GOLD}]📕 新书名/剧名[/{C_GOLD}]").strip()
                    if title:
                        break
                    print_err("书名/剧名不能为空。")
                while True:
                    synopsis = Prompt.ask(f"  [{C_GOLD}]📝 核心选题概念/故事大纲简介[/{C_GOLD}]").strip()
                    if synopsis:
                        break
                    print_err("简介不能为空。")
        else:
            while True:
                title = Prompt.ask(f"  [{C_GOLD}]📕 新书名/剧名[/{C_GOLD}]").strip()
                if title:
                    break
                print_err("书名/剧名不能为空。")
            while True:
                synopsis = Prompt.ask(f"  [{C_GOLD}]📝 核心选题概念/故事大纲简介[/{C_GOLD}]").strip()
                if synopsis:
                    break
                print_err("简介不能为空。")
    else:
        title = title_input
        while True:
            synopsis = Prompt.ask(f"  [{C_GOLD}]📝 核心选题概念/故事大纲简介[/{C_GOLD}]").strip()
            if synopsis:
                break
            print_err("简介不能为空。")
        
    state["novel_title"] = title
    state["synopsis"] = synopsis
    state["book_type"] = book_type
    state["settings_created"] = False
    state["outline_created"] = False
    state["chapters"] = {}
    save_state(state)
    
    # 开始生成核心设定 (步骤2)
    step2_prompt_file = get_template_path("novel-story-foundation", book_type, "step02-core-settings.md")
    if not os.path.exists(step2_prompt_file):
        print_err(f"找不到核心设定模板文件 {step2_prompt_file}")
        return
        
    with open(step2_prompt_file, "r", encoding="utf-8") as f:
        step2_tmpl = f.read()
        
    prompt = f"请根据以下输入，生成作品的核心设定文档。\n【书名】：{title}\n【简介】：{synopsis}\n\n模板指导内容：\n{step2_tmpl}"
    
    system_role = book_cfg.get("rules", {}).get("system_prompt_story", "你是一位资深世界观架构师。")
    print_step(1, 2, f"构建《核心设定》文档 ({book_cfg['genre_name']}) (DeepSeek)")
    with console.status(f"[bold #C77A8E]  🪶 执笔织梦中，世界观正在成型...", spinner="dots12", spinner_style="#FFB703"):
        try:
            settings_content = call_deepseek(prompt, system_role)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as sf:
                sf.write(settings_content)
            state["settings_created"] = True
            save_state(state)
            print_ok("核心设定已生成 → novel_core_settings.md")
        except Exception as e:
            print_err(f"生成核心设定失败: {e}")
            return

    # 生成简介与推荐语 (步骤3)
    step3_prompt_file = get_template_path("novel-story-foundation", book_type, "step03-tags-synopsis.md")
    if os.path.exists(step3_prompt_file):
        with open(step3_prompt_file, "r", encoding="utf-8") as f:
            step3_tmpl = f.read()
        prompt = f"基于书名《{title}》和已经生成的【核心设定】内容，生成作品的标签和简介。\n\n【核心设定】内容：\n{settings_content}\n\n模板要求：\n{step3_tmpl}"
        system_role_synopsis = book_cfg.get("rules", {}).get("system_prompt_synopsis", "你是一位精通简介文案写作的运营编辑。")
        print_step(2, 2, f"构建《标签与简介》文档 ({book_cfg['genre_name']}) (DeepSeek)")
        with console.status(f"[bold #C77A8E]  🪶 锦绣文案凝练中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                synopsis_content = call_deepseek(prompt, system_role_synopsis)
                with open(SYNOPSIS_FILE, "w", encoding="utf-8") as syf:
                    syf.write(synopsis_content)
                state["outline_created"] = True
                save_state(state)
                print_ok("标签与三版简介已生成 → novel_tags_synopsis.md")
            except Exception as e:
                print_err(f"生成标签简介失败: {e}")
                return
                
    print_ok("项目初始化完成！现在可以输入 write 开始创作。")

def cmd_style(state, args):
    config = load_style_config()
    if not args or args[0].lower() in ["show", "list"]:
        print_section_header("小说文风状态", STEP_ICONS['status'])
        
        # 展示当前激活风格
        active_name, active_desc = get_active_style_desc(config)
        display_name = active_name if active_name != "默认" else "未设置（默认通用风格）"
        console.print(Panel(
            f"[bold #FFB703]当前激活文风[/bold #FFB703]: [bold #C77A8E]{display_name}[/bold #C77A8E]\n"
            f"[white]文风描述[/white]: {active_desc}",
            border_style="#C77A8E",
            box=ROUNDED,
            padding=(1, 2)
        ))
        
        # 渲染预设与自定义列表的 Table
        table = Table(
            title="[bold #C77A8E]可用预设与自定义文风列表[/bold #C77A8E]",
            box=ROUNDED,
            border_style="#A8687A",
            header_style="bold #FFB703",
            show_lines=True,
            padding=(0, 1),
        )
        table.add_column("文风名称", style="bold #FFB703", justify="center", width=15)
        table.add_column("类型", style="#F4A3B5", justify="center", width=8)
        table.add_column("文风特征与模仿要求描述", style="white", min_width=30)
        table.add_column("快捷切换", style="#2A9D8F", justify="center", width=12)
        
        for name, desc in config.get("presets", {}).items():
            active_marker = f"[bold #06D6A0]✔ {name}[/bold #06D6A0]" if name == active_name else name
            shortcut = next((k for k, v in STYLE_SHORTCUTS.items() if v == name), "")
            table.add_row(active_marker, "预设", desc, shortcut)
            
        for name, desc in config.get("custom", {}).items():
            active_marker = f"[bold #06D6A0]✔ {name}[/bold #06D6A0]" if name == active_name else name
            table.add_row(active_marker, "自定义", desc, "style learn")
            
        console.print(Align.center(table))
        console.print(f"  [{C_SILVER}]提示: 可直接输入 style1-style5 快捷切换，也可用 'style set <名称>' 切换文风，或 'style learn <路径>' 学习外部文风。[/{C_SILVER}]")
        
    elif args[0].lower() == "set":
        if len(args) < 2:
            print_err("请指定要切换的文风名称。例如: style set 古言雅致")
            return
        target_style = resolve_style_name(args[1])
        if target_style not in config.get("presets", {}) and target_style not in config.get("custom", {}):
            print_err(f"找不到文风: {target_style}。请输入 'style show' 查看所有可用文风。")
            return
        config["current_style"] = target_style
        save_style_config(config)
        print_ok(f"文风已成功切换为: 【{target_style}】！")
        
    elif args[0].lower() == "learn":
        if len(args) < 2:
            print_err("请指定参考小说文本文件的路径。例如: style learn scratch/style_sample.txt")
            return
        filepath = args[1]
        if not os.path.exists(filepath):
            print_err(f"找不到参考文件: {filepath}")
            return
        
        # 自动获取文件名作为风格命名
        filename = os.path.basename(filepath)
        style_name = "模仿_" + os.path.splitext(filename)[0]
        
        print_step(1, 2, f"正在读取并提取文风特征: {filename}")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read(5000) # 提取前5000字
        except Exception as e:
            print_err(f"读取参考文件失败: {e}")
            return
            
        if len(content.strip()) < 100:
            print_err("参考文本内容过少，请至少提供100字以上的段落以提取风格。")
            return
            
        prompt = f"请提取以下文本的文风特点，给出100-200字的文风特征描述。具体文本如下：\n\n{content}"
        
        print_step(2, 2, "大模型提炼文风中 (DeepSeek)")
        with console.status(f"[bold #C77A8E]  🪶 正在透视句式、分析笔力特征...", spinner="dots12", spinner_style="#FFB703"):
            try:
                style_desc = call_deepseek(prompt, STYLE_ANALYSIS_SYSTEM_PROMPT)
                style_desc = style_desc.strip().replace("\n", " ")
                config["custom"][style_name] = style_desc
                config["current_style"] = style_name
                save_style_config(config)
                
                console.print()
                console.print(Panel(
                    f"[{C_SUCCESS}]✨ 成功提取并生成自定义模仿文风！[/{C_SUCCESS}]\n"
                    f"[white]文风命名[/white]: [bold #FFB703]{style_name}[/bold #FFB703]\n"
                    f"[white]特征提取[/white]: {style_desc}",
                    border_style="#06D6A0",
                    box=ROUNDED,
                    padding=(1, 2)
                ))
                print_ok(f"已自动将当前小说文风切换为: 【{style_name}】")
            except Exception as e:
                print_err(f"文风提取失败: {e}")
    else:
        print_err(f"未知 style 子命令: {args[0]}。可用子命令: show, set, learn")

def run_rag_retrieve(state, chapter_num, chapter_outline, previous_context, quiet=True):
    """自动运行 RAG 检索器获取本章的语感小抄"""
    retriever_script = os.path.join(TOOLS_DIR, "rag_retrieve.py")
    if not os.path.exists(retriever_script):
        if not quiet:
            print_warn("RAG 检索器脚本未找到，将跳过本章小抄匹配。")
        return ""
        
    config = load_style_config()
    active_style, _ = get_active_style_desc(config)
    
    # 构造核心设定、章节细纲和前情提要的临时文件，方便命令行传递
    import tempfile
    
    core_file = os.path.join(WORKSPACE_DIR, "novel_core_settings.md")
    
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as outline_tmp, \
         tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as prev_tmp:
        
        outline_tmp.write(chapter_outline)
        prev_tmp.write(previous_context)
        
        outline_tmp_path = outline_tmp.name
        prev_tmp_path = prev_tmp.name
        
    try:
        cmd = [
            sys.executable, retriever_script,
            "--outline-file", outline_tmp_path,
            "--previous-file", prev_tmp_path,
            "--top-k", "12",
            "--min-k", "5",
            "--format", "markdown"
        ]
        if os.path.exists(core_file):
            cmd.extend(["--core-setting-file", core_file])
            
        # 自动根据项目题材追加题材过滤参数
        book_type = state.get("book_type", "female_novel")
        cmd.extend(["--genre", book_type])
            
        # 设置 NOVEL_RAG_KB 路径
        env = os.environ.copy()
        default_root = os.path.join(os.path.expanduser("~"), "novel-rag-kb")
        env["NOVEL_RAG_KB"] = default_root
        
        res = subprocess.run(cmd, capture_output=True, env=env)
        
        # 兼容 Windows CMD/Powershell 下的 GBK 编码输出，防止 _readerthread 编码崩溃
        stdout = ""
        stderr = ""
        if res.stdout:
            try:
                stdout = res.stdout.decode("utf-8")
            except UnicodeDecodeError:
                stdout = res.stdout.decode("gbk", errors="replace")
                
        if res.stderr:
            try:
                stderr = res.stderr.decode("utf-8")
            except UnicodeDecodeError:
                stderr = res.stderr.decode("gbk", errors="replace")
                
        if res.returncode == 0:
            return stdout
        else:
            if not quiet:
                print_err(f"RAG 检索器返回异常 ({res.returncode}): {stderr}")
            return ""
    except Exception as e:
        if not quiet:
            print_err(f"运行 RAG 检索器失败: {e}")
        return ""
    finally:
        # 清理临时文件
        for path in (outline_tmp_path, prev_tmp_path):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

def cmd_rag(state):
    print_section_header("手动触发 RAG 检索", STEP_ICONS['quill'])
    c_num = len(state["chapters"]) + 1
    
    # 寻找前情提要
    prev_context = "无"
    if c_num > 1:
        prev_file = os.path.join(WORKSPACE_DIR, f"chapter_{c_num-1:02d}.md")
        if not os.path.exists(prev_file):
            prev_file = os.path.join(WORKSPACE_DIR, f"chapter_{c_num-1}.md")
        if os.path.exists(prev_file):
            try:
                with open(prev_file, "r", encoding="utf-8") as pf:
                    content = pf.read()
                    prev_context = content[-1500:] if len(content) > 1500 else content
            except Exception:
                pass
                
    outline_file = os.path.join(WORKSPACE_DIR, "novel_core_settings.md") # 临时占位，只在手动测试时用
    
    with console.status(f"[bold #C77A8E]  🔍 检索匹配语感小抄...", spinner="dots12", spinner_style="#FFB703"):
        try:
            sheet = run_rag_retrieve(state, c_num, "手动测试 RAG 检索", prev_context, quiet=False)
            console.print(Panel(
                Markdown(sheet),
                title="[bold #FFB703]当前 RAG 语感小抄[/bold #FFB703]",
                border_style="#C77A8E",
                box=ROUNDED,
                padding=(1, 2)
            ))
        except Exception as e:
            print_err(f"RAG 检索失败: {e}")

def cmd_update():
    print_section_header("更新 RAG 知识库", "🌐")
    script = os.path.join(TOOLS_DIR, "rag_update_trends.py")
    if not os.path.exists(script):
        print_err("找不到知识库更新脚本 rag_update_trends.py。")
        return
        
    with console.status(f"[bold #C77A8E]  📚 正在联网同步并重新计算权重，请稍候...", spinner="dots12", spinner_style="#FFB703"):
        try:
            # 设置环境变量以配合 ~/novel-rag-kb 默认位置，或者使用工作区
            env = os.environ.copy()
            default_root = os.path.join(os.path.expanduser("~"), "novel-rag-kb")
            env["NOVEL_RAG_KB"] = default_root
            
            res = subprocess.run([sys.executable, script], capture_output=True, env=env)
            
            stdout = ""
            stderr = ""
            if res.stdout:
                try:
                    stdout = res.stdout.decode("utf-8")
                except UnicodeDecodeError:
                    stdout = res.stdout.decode("gbk", errors="replace")
                    
            if res.stderr:
                try:
                    stderr = res.stderr.decode("utf-8")
                except UnicodeDecodeError:
                    stderr = res.stderr.decode("gbk", errors="replace")
                    
            if res.returncode == 0:
                print_ok("RAG 语感与热梗知识库联网更新完成！")
            else:
                print_err(f"更新失败：{stderr}")
        except Exception as e:
            print_err(f"执行更新脚本出错: {e}")

def cmd_write(state, chapter_count=1):
    if not state.get("settings_created"):
        print_err("项目尚未初始化设定，请先运行 init 命令。")
        return
        
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            core_settings = f.read()
    except Exception as e:
        print_err(f"读取核心设定失败: {e}")
        return
        
    book_type = state.get("book_type", "female_novel")
    book_cfg = load_book_type_config(book_type)
    genre_display = book_cfg.get("genre_name", "女频长篇")
    unit_name = "集" if book_cfg.get("format") == "script" else "章"

    # ----------------- 精品短篇分段拼接生成分支 -----------------
    if book_cfg.get("format") == "novel_segmented":
        if len(state["chapters"]) > 0:
            print_warn("精品短篇属于单章完结故事，已经生成完毕！若要重新生成，请先运行 init。")
            return
            
        print_section_header(f"精品短篇全自动分段创作管线 (5000-10000字)", STEP_ICONS['draft'])
        print_atmosphere_quote()
        console.print()
        
        # 1. 策划短篇大纲
        step6_prompt_file = get_template_path("novel-outline-builder", book_type, "step06-chapter-outline.md")
        if not os.path.exists(step6_prompt_file):
            print_err("找不到短篇大纲模板。")
            return
        with open(step6_prompt_file, "r", encoding="utf-8") as f:
            step6_tmpl = f.read()
            
        outline_prompt = (
            f"根据小说的【核心设定】，策划包含起、承、转、合四个部分的精品短篇大纲。\n\n"
            f"【故事核心设定】：\n{core_settings}\n\n"
            f"大纲规范要求：\n{step6_tmpl}"
        )
        
        system_role_outline = book_cfg.get("rules", {}).get("system_prompt_outline", "你是一位大纲策划专家。")
        print_step(1, 5, "策划全篇起承转合结构大纲")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['outline']} 架构设计中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                story_outline = call_deepseek(outline_prompt, system_role_outline)
                print_ok("短篇故事全篇结构大纲设计完成")
            except Exception as e:
                print_err(f"大纲设计失败: {e}")
                return

        # 2. 依次生成并审查各部分内容
        segments = book_cfg.get("rules", {}).get("segments", ["起_Crisis", "承_Develop", "转_Twist", "合_End"])
        segment_limits = book_cfg.get("rules", {}).get("segment_limits", {})
        
        story_content_parts = []
        previous_parts_text = ""
        
        step8_prompt_file = get_template_path("novel-draft-writer", book_type, "step08-write-content.md")
        step9_prompt_file = get_template_path("novel-quality-review", book_type, "step09-check-content.md")
        
        with open(step8_prompt_file, "r", encoding="utf-8") as f:
            step8_tmpl = f.read()
        with open(step9_prompt_file, "r", encoding="utf-8") as f:
            step9_tmpl = f.read()
            
        system_role_draft = book_cfg.get("rules", {}).get("system_prompt_draft", "你是一位精品短篇签约作者。")
        system_role_review = book_cfg.get("rules", {}).get("system_prompt_review", "你是一位质检编辑。")
            
        for i, seg in enumerate(segments):
            limit = segment_limits.get(seg, { "min": 1500, "max": 2000, "target": 1800 })
            seg_num = i + 1
            print_step(2, 5, f"正在创作第 {seg_num}/{len(segments)} 部分: {seg}")
            
            write_prompt = (
                f"你正在写一篇 5000-10000 字的短篇故事，现在需要撰写第 {seg_num} 部分: 【{seg}】 的正文初稿。\n"
                f"【硬性字数限制】：字数必须在 {limit['min']}-{limit['max']} 字之间，目标约 {limit['target']} 字。\n"
                f"【注意】：你必须承接已经写好的前文部分，并为下一部分的发展或反转留下合理的伏笔或铺垫。\n\n"
                f"【核心设定】：\n{core_settings}\n\n"
                f"【全篇起承转合结构大纲】：\n{story_outline}\n\n"
                f"【已写好的前文】：\n{previous_parts_text if previous_parts_text else '（无，这是开篇第一段）'}\n\n"
                f"正文写作指南：\n{step8_tmpl}"
            )
            
            # 2.1 撰写初稿
            with console.status(f"[bold #C77A8E]  ✍️ 执笔润色中，正在码字 {seg} 部分...", spinner="dots12", spinner_style="#FFB703"):
                try:
                    draft_content = call_deepseek(write_prompt, system_role_draft)
                    print_ok(f"{seg} 部分初稿完成（约 {len(draft_content):,} 字）")
                except Exception as e:
                    print_err(f"生成 {seg} 部分初稿失败: {e}")
                    return
                    
            # 2.2 自动审查
            review_prompt = (
                f"请对这篇短篇小说的第 {seg_num} 部分 【{seg}】 的初稿内容运行人设一致性、逻辑一致性及冗余、字数的深度审查，并输出审查报告。\n\n"
                f"【硬性字数审查】：本段字数区间应在 {limit['min']}-{limit['max']} 字之间。如果不符合，请作为 🔴 必须修改提出。\n\n"
                f"【核心大纲】：\n{story_outline}\n\n"
                f"【已写好的前文】：\n{previous_parts_text if previous_parts_text else '（无）'}\n\n"
                f"【需审查的本段正文】：\n{draft_content}\n\n"
                f"审查标准：\n{step9_tmpl}"
            )
            
            print_step(3, 5, f"对 {seg} 部分进行人设与逻辑纠偏审查")
            with console.status(f"[bold #C77A8E]  🔍 编辑上线，审查 {seg} 部分...", spinner="dots12", spinner_style="#FFB703"):
                try:
                    review_report = call_deepseek(review_prompt, system_role_review)
                    print_ok(f"{seg} 部分质检报告输出完成")
                except Exception as e:
                    print_err(f"审查 {seg} 部分失败: {e}")
                    return
                    
            # 2.3 自审纠偏与精修重写
            rewrite_prompt = (
                f"请结合【编辑审查报告】中的修改建议，对【初稿】进行全面精修重写，加深反转，严控字数。\n"
                f"要求：\n"
                f"1. 严格遵守字数：{limit['min']}-{limit['max']} 字之间。\n"
                f"2. 只输出重写后的最终正文，不要输出任何Markdown格式以外的碎话前言，直接给出正文。\n\n"
                f"【全篇结构大纲】：\n{story_outline}\n\n"
                f"【已写好的前文】：\n{previous_parts_text if previous_parts_text else '（无）'}\n\n"
                f"【初稿正文】：\n{draft_content}\n\n"
                f"【编辑审查报告】：\n{review_report}"
            )
            
            print_step(4, 5, f"应用质检纠偏 · 重写定稿 {seg}")
            with console.status(f"[bold #C77A8E]  💎 磨砺字句，精修 {seg} 部分中...", spinner="dots12", spinner_style="#FFB703"):
                try:
                    final_part_content = call_deepseek(rewrite_prompt, system_role_draft)
                    story_content_parts.append(final_part_content.strip())
                    previous_parts_text += f"\n\n### 分段{seg_num}：{seg}\n{final_part_content.strip()}"
                    print_ok(f"{seg} 部分定稿（约 {len(final_part_content):,} 字）")
                except Exception as e:
                    print_err(f"重写 {seg} 部分失败: {e}")
                    return
                    
        # 3. 合并全篇并写入文件
        print_step(5, 5, "正在进行全篇大融合与排版保存...")
        full_novel_text = f"# {state['novel_title']}\n\n## 故事简介\n{state['synopsis']}\n\n## 故事大纲\n{story_outline}\n\n"
        for idx, part in enumerate(story_content_parts):
            full_novel_text += f"\n\n{part}\n"
            
        filename = "chapter_01.md"
        filepath = os.path.join(WORKSPACE_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_novel_text)
            
        state["chapters"]["1"] = {
            "title": state['novel_title'],
            "file": filename,
            "status": "completed"
        }
        save_state(state)
        
        console.print()
        print_divider("#06D6A0", "═")
        console.print(Align.center(
            Text(f"✨ 精品短篇 《{state['novel_title']}》 全文创作定稿完成！累计字数：{len(full_novel_text):,} 字 ✨", style=f"bold {C_SUCCESS}")
        ))
        print_divider("#06D6A0", "═")
        cmd_export(state)
        return

    # ----------------- 长篇小说/短剧剧本 循环生成分支 -----------------
    start_chap = len(state["chapters"]) + 1
    end_chap = start_chap + chapter_count - 1
    
    print_section_header(
        f"全自动创作管线 · 第 {start_chap}–{end_chap} {unit_name}",
        STEP_ICONS['draft']
    )
    print_atmosphere_quote()
    console.print()
    
    for c_num in range(start_chap, end_chap + 1):
        console.print(Panel(
            f"[bold #FFB703]{STEP_ICONS['chapter']} 正在创作第 {c_num} {unit_name}[/bold #FFB703]",
            border_style="#C77A8E",
            box=HEAVY,
            padding=(0, 2),
        ))
        
        # 1. 获取前情提要
        prev_context = f"无（这是小说的开篇第一{unit_name}）"
        if c_num > 1:
            prev_file = os.path.join(WORKSPACE_DIR, f"chapter_{c_num-1:02d}.md")
            if not os.path.exists(prev_file):
                prev_file = os.path.join(WORKSPACE_DIR, f"chapter_{c_num-1}.md")
            if os.path.exists(prev_file):
                try:
                    with open(prev_file, "r", encoding="utf-8") as pf:
                        content = pf.read()
                        prev_context = content[-1500:] if len(content) > 1500 else content
                except Exception as e:
                    print_warn(f"获取前情提要失败: {e}，将使用空白。")
                    
        # 2. 自动生成章节细纲
        step6_prompt_file = get_template_path("novel-outline-builder", book_type, "step06-chapter-outline.md")
        if not os.path.exists(step6_prompt_file):
            print_err("找不到章节大纲模板。")
            return
            
        with open(step6_prompt_file, "r", encoding="utf-8") as f:
            step6_tmpl = f.read()
            
        outline_prompt = (
            f"根据作品的【核心设定】和【前情提要】，为小说的「第{c_num}{unit_name}」策划详细大纲。\n"
            f"注意：如果 c_num 是 1、2、3，必须在细纲中落实对应的「黄金三章」要求！\n\n"
            f"【核心设定】：\n{core_settings}\n\n"
            f"【前情提要】：\n{prev_context}\n\n"
            f"大纲规范要求：\n{step6_tmpl}"
        )
        
        system_role_outline = book_cfg.get("rules", {}).get("system_prompt_outline", "你是一位大纲策划专家。")
        print_step(1, 5, f"策划第 {c_num} {unit_name} 详细细纲")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['outline']} 谋篇布局，细纲搭建中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                chapter_outline = call_deepseek(outline_prompt, system_role_outline)
                print_ok(f"第 {c_num} {unit_name} 大纲策划完成")
            except Exception as e:
                print_err(f"策划大纲失败: {e}")
                return

        # 3. RAG 小抄与文风加载
        print_step(2, 5, f"匹配第 {c_num} {unit_name} 文风与语感素材")
        active_style, active_style_desc, style_prompt = build_style_prompt()
        rag_sheet = run_rag_retrieve(state, c_num, chapter_outline, prev_context, quiet=True)
        rag_usage_rules = read_text_if_exists(os.path.join(RAG_REFERENCES_DIR, "rag-usage-rules.md")) if rag_sheet else ""
        rag_prompt = ""
        if rag_sheet:
            rag_prompt = (
                f"【RAG小抄】：\n{rag_sheet}\n\n"
                f"【RAG小抄进入正文的使用规则】：\n{rag_usage_rules}\n\n"
            )
            print_ok("RAG 语感小抄匹配完成")
        else:
            print_warn("未匹配到 RAG 小抄，本章将只使用正文基础规则与当前文风。")
        
        # 4. 初稿撰写
        step8_prompt_file = get_template_path("novel-draft-writer", book_type, "step08-write-content.md")
        if not os.path.exists(step8_prompt_file):
            print_err("找不到正文写作模板。")
            return
            
        with open(step8_prompt_file, "r", encoding="utf-8") as f:
            step8_tmpl = f.read()
            
        word_limit = book_cfg.get("chapter_word_limit", {"min": 1800, "max": 2200, "target": 2000})
        word_rule = f"字数必须严格在 {word_limit['min']}-{word_limit['max']} 字之间，目标约 {word_limit['target']} 字。"
        paragraph_rule = book_cfg.get("rules", {}).get("short_paragraph", "")
        
        write_prompt = (
            f"根据【核心设定】、【前情提要】和已策划好的【章节细纲】，撰写第 {c_num} {unit_name} 的正文初稿。\n"
            f"请严格遵守创作原则，严防AI腔调和禁用词，段落要短，多用生活化有颗粒感细节。\n"
            f"【硬性字数要求】：{word_rule}\n"
            f"【短句段落限制】：{paragraph_rule}\n\n"
            f"【小说核心设定】：\n{core_settings}\n\n"
            f"【前情提要】：\n{prev_context}\n\n"
            f"【本章章节大纲】：\n{chapter_outline}\n\n"
            f"【当前激活文风】：{active_style}\n"
            f"【当前小说文风与模仿要求】：\n{active_style_desc}\n\n"
            f"【文风Reference】：\n{style_prompt}\n\n"
            f"{rag_prompt}"
            f"正文写作指南与禁区：\n{step8_tmpl}"
        )
        
        system_role_draft = book_cfg.get("rules", {}).get("system_prompt_draft", "你是一位热门网文作者。")
        print_step(3, 5, f"撰写第 {c_num} {unit_name} 正文初稿")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['draft']} 落笔生花，初稿挥就中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                draft_content = call_deepseek(write_prompt, system_role_draft)
                print_ok(f"第 {c_num} {unit_name} 初稿完成（约 {len(draft_content):,} 字）")
            except Exception as e:
                print_err(f"撰写初稿失败: {e}")
                return

        # 5. 自动审查
        step9_prompt_file = get_template_path("novel-quality-review", book_type, "step09-check-content.md")
        if not os.path.exists(step9_prompt_file):
            print_err("找不到正文审查模板。")
            return
            
        with open(step9_prompt_file, "r", encoding="utf-8") as f:
            step9_tmpl = f.read()
            
        review_prompt = (
            f"请作为质检编辑，对【正文初稿】运行人设一致性、逻辑一致性及去AI味的深度自审，并输出审查报告。\n\n"
            f"【硬性字数审查】：{word_rule} 若偏离该区间，必须列为 🔴 必须修改。\n"
            f"【短句段落审查】：{paragraph_rule} 若超限，必须列为 🔴 必须修改。\n\n"
            f"【核心设定】：\n{core_settings}\n\n"
            f"【章节大纲】：\n{chapter_outline}\n\n"
            f"【前情提要】：\n{prev_context}\n\n"
            f"【当前小说文风与模仿要求】：\n{active_style_desc}\n\n"
            f"{rag_prompt}"
            f"【需审查的正文初稿】：\n{draft_content}\n\n"
            f"审查标准规范：\n{step9_tmpl}"
        )
        
        system_role_review = book_cfg.get("rules", {}).get("system_prompt_review", "你是一位质检编辑。")
        print_step(4, 5, f"运行人设与逻辑纠偏审查")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['review']} 毒舌编辑上线，逐字审稿中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                review_report = call_deepseek(review_prompt, system_role_review)
                print_ok(f"第 {c_num} {unit_name} 质检报告输出完成")
            except Exception as e:
                print_err(f"自审失败: {e}")
                return

        # 6. 自审纠偏与精修重写
        rewrite_prompt = (
            f"请结合【编辑审查报告】中的修改建议，对【初稿】进行全面重写并最终定稿。\n"
            f"要求：\n"
            f"1. 严格纠正人设偏离、逻辑伤与AI味。\n"
            f"2. {word_rule}\n"
            f"3. {paragraph_rule}\n"
            f"4. 只输出重写后的最终正文，以「# 第{c_num}{unit_name}：标题」形式的一级标题开头，不要输出任何其他Markdown以外的碎话前言，直接给出定稿。\n\n"
            f"【当前小说文风与模仿要求】：\n{active_style_desc}\n\n"
            f"{rag_prompt}"
            f"【当前章节大纲】：\n{chapter_outline}\n\n"
            f"【初稿正文】：\n{draft_content}\n\n"
            f"【编辑审查报告】：\n{review_report}"
        )
        
        print_step(5, 5, f"应用质检纠偏 · 精修定稿")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['rewrite']} 千锤百炼，精修定稿中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                final_content = call_deepseek(rewrite_prompt, system_role_draft)
                
                if not final_content.strip().startswith("#"):
                    title_match = re.search(rf"第\d+{unit_name}：(.*)", chapter_outline)
                    c_title = title_match.group(1).strip() if title_match else "未命名章节"
                    final_content = f"# 第{c_num}{unit_name}：{c_title}\n\n" + final_content.strip()
                
                filename = f"chapter_{c_num:02d}.md"
                filepath = os.path.join(WORKSPACE_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as cf:
                    cf.write(final_content)
                
                first_line = final_content.strip().split("\n")[0]
                t_match = re.match(rf"^#\s*第\s*(\d+)\s*[{unit_name}回]\s*[:：\s]*\s*(.*)$", first_line)
                resolved_title = t_match.group(2).strip() if t_match else first_line.lstrip("#").strip()
                
                state["chapters"][str(c_num)] = {
                    "title": resolved_title,
                    "file": filename,
                    "status": "completed"
                }
                save_state(state)
                
                console.print()
                console.print(Panel(
                    f"[{C_SUCCESS}]{STEP_ICONS['success']} 第 {c_num} {unit_name} 定稿完成[/{C_SUCCESS}]\n"
                    f"[white]📄 文件：{filename}[/white]\n"
                    f"[white]📖 标题：《{resolved_title}》[/white]\n"
                    f"[white]📊 字数：{len(final_content):,} 字[/white]",
                    border_style="#06D6A0",
                    box=ROUNDED,
                    padding=(0, 2),
                ))
            except Exception as e:
                print_err(f"精修重写失败: {e}")
                return

    # 全自动生成结束
    console.print()
    print_divider("#06D6A0", "═")
    console.print(Align.center(
        Text(f"✨ 本批次 {chapter_count} {unit_name} 自动写作全部完成！正在触发编译打包... ✨", style=f"bold {C_SUCCESS}")
    ))
    print_divider("#06D6A0", "═")
    cmd_export(state)

def cmd_review(chapter_num):
    print_section_header(f"深度审查 · 第 {chapter_num} 章/集", STEP_ICONS['review'])

    filename = f"chapter_{chapter_num:02d}.md"
    filepath = os.path.join(WORKSPACE_DIR, filename)
    if not os.path.exists(filepath):
        filename = f"chapter_{chapter_num}.md"
        filepath = os.path.join(WORKSPACE_DIR, filename)
        
    if not os.path.exists(filepath):
        print_err(f"找不到正文文件: {filename}")
        return
        
    state = load_state()
    book_type = state.get("book_type", "female_novel")
    book_cfg = load_book_type_config(book_type)
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            chapter_content = f.read()
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            core_settings = f.read()
    except Exception as e:
        print_err(f"读取文件失败: {e}")
        return
        
    step9_prompt_file = get_template_path("novel-quality-review", book_type, "step09-check-content.md")
    if not os.path.exists(step9_prompt_file):
        print_err(f"找不到质检审查模板: {step9_prompt_file}")
        return
        
    with open(step9_prompt_file, "r", encoding="utf-8") as f:
        step9_tmpl = f.read()
        
    review_prompt = (
        f"请作为质检编辑，对该正文进行深度人设一致性、逻辑一致性及去AI味的深度质检，并输出审查报告。\n\n"
        f"【核心设定】：\n{core_settings}\n\n"
        f"【需审查的正文内容】：\n{chapter_content}\n\n"
        f"审查标准规范：\n{step9_tmpl}"
    )
    
    system_role_review = book_cfg.get("rules", {}).get("system_prompt_review", "你是一位质检编辑。")
    with console.status(f"[bold #C77A8E]  {STEP_ICONS['review']} 毒舌编辑正在逐字比对质检...", spinner="dots12", spinner_style="#FFB703"):
        try:
            report = call_deepseek(review_prompt, system_role_review)
            print_section_header(f"质检审查报告", "📋")
            console.print(Panel(
                Markdown(report),
                border_style="#C77A8E",
                box=ROUNDED,
                padding=(1, 2),
            ))
        except Exception as e:
            print_err(f"自审失败: {e}")

def cmd_export(state):
    print_section_header("编译导出 Word 文档", STEP_ICONS['export'])
    
    sys.path.append(TOOLS_DIR)
    try:
        import merge_to_word
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['export']} 章节合并 & Word 排版编译中...", spinner="dots12", spinner_style="#FFB703"):
            merge_to_word.main()
        print_ok(f"Word 文档编译完成！文件已保存至工作区。")
    except ImportError:
        print_err("未能在指定目录找到合并打包脚本 merge_to_word.py")
    except Exception as e:
        print_err(f"运行 Word 打包合并失败: {e}")

# ═══════════════════════════════════════════════════════════════
#  交互式 Shell 循环
# ═══════════════════════════════════════════════════════════════
FAREWELL_QUOTES = [
    "锦绣文章，明日再续。",
    "搁笔歇墨，好梦入怀。",
    "愿你笔下生花，日日爆更。",
    "且去且珍重，江湖再见。",
    "酒入豪肠，七分酿成了月光。余下的三分啸成剑气，绣口一吐就半个盛唐。",
    "此去经年，愿你的作品万人追读。",
]

def print_onboarding_guide():
    """以极具氛围感且轻量极简的方式展示新手起航指引"""
    guide_content = (
        f"[italic #F4A3B5]“笔落惊风雨，诗成泣鬼神。”[/italic #F4A3B5]\n"
        f"[dim #FAF3E0]在这里，每一个题材都是一个待醒之梦，只待你落笔生花。[/dim #FAF3E0]\n\n"
        f"[bold #FFB703]💡 快速落笔三部曲：[/bold #FFB703]\n"
        f"  • 输入 [bold #C77A8E]init[/bold #C77A8E]   ➜  构筑核心设定，开启选题灵感\n"
        f"  • 输入 [bold #C77A8E]write[/bold #C77A8E]  ➜  大纲、初稿、自审、精修一气呵成\n"
        f"  • 输入 [bold #C77A8E]export[/bold #C77A8E] ➜  章节自动拼装，导出排版好的 Word 文档\n\n"
        f"[dim #A8687A]提示：随时输入 [bold white]help[/bold white] 查看指令秘籍，输入 [bold white]status[/bold white] 观览项目全貌。[/dim #A8687A]"
    )
    panel = Panel(
        guide_content,
        title="[bold #06D6A0]🪶  红 文 织 梦  ·  启 航[/bold #06D6A0]",
        border_style="#06D6A0",
        box=ROUNDED,
        padding=(1, 4),
    )
    console.print(panel)

def start_interactive_shell():
    # 清屏效果 (可选)
    console.print()
    print_divider("#C77A8E", "═")
    console.print(BANNER)
    console.print(Align.center(
        Text("红 文 织 梦", style="bold #C77A8E")
    ))
    console.print(Align.center(
        Text("多体裁全自动小说/剧本创作管线", style=f"bold {C_PINK}")
    ))
    console.print(Align.center(
        Text("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", style="#3D3D3D")
    ))
    console.print(Align.center(
        Text("沉浸式终端创作系统  ·  Powered by DeepSeek", style=C_SILVER)
    ))
    print_divider("#C77A8E", "═")
    console.print()
    print_atmosphere_quote()
    console.print()
    
    state = load_state()
    
    # 检查是否为首次在此目录下运行或尚未初始化设定
    is_first_time = not state.get("settings_created")
    if is_first_time:
        print_onboarding_guide()
    else:
        console.print(Align.center(Text("👉 输入 help 即可呼出全部可用指令", style=f"italic {C_SILVER}")))
        console.print()
    
    # 构建提示符
    prompt_text = Text()
    prompt_text.append("  ❯ ", style="bold #C77A8E")
    prompt_text.append("红文织梦", style="bold #FFB703")
    prompt_text.append(" ▸ ", style="#C77A8E")

    while True:
        try:
            cmd_input = Prompt.ask(f"\n  [bold #C77A8E]❯[/bold #C77A8E] [bold #FFB703]红文织梦[/bold #FFB703] [#C77A8E]▸[/#C77A8E]").strip()
            if not cmd_input:
                continue
                
            parts = cmd_input.split()
            cmd = parts[0].lower()
            args = parts[1:]
            if cmd in STYLE_SHORTCUTS:
                cmd_style(state, ["set", cmd])
                continue
            
            if cmd in ["exit", "quit"]:
                farewell = random.choice(FAREWELL_QUOTES)
                console.print()
                print_divider("#C77A8E", "━")
                console.print(Align.center(
                    Text(f"🪶  {farewell}", style=f"italic #F4A3B5")
                ))
                console.print(Align.center(
                    Text("愿您的作品早日爆红番茄！再见 👋", style=f"bold {C_GOLD}")
                ))
                print_divider("#C77A8E", "━")
                break
            elif cmd == "help":
                cmd_help()
            elif cmd == "status":
                cmd_status(state)
            elif cmd == "init":
                cmd_init(state)
            elif cmd == "trend":
                if not args:
                    print_err("trend 命令需要子命令 (fetch, kb, stats)。输入 help 查看。")
                    continue
                sub = args[0].lower()
                if sub == "fetch":
                    cmd_trend_fetch()
                elif sub == "kb":
                    cmd_trend_kb()
                elif sub == "stats":
                    cmd_trend_stats()
                else:
                    print_err(f"未知 trend 子命令: {sub}")
            elif cmd == "write":
                count = 1
                if args:
                    try:
                        count = int(args[0])
                    except ValueError:
                        print_err("参数错误: 章节数量必须为整数。例如: write 3")
                        continue
                cmd_write(state, count)
            elif cmd == "review":
                if not args:
                    print_err("review 命令需要指定章节数。例如: review 2")
                    continue
                try:
                    c_num = int(args[0])
                except ValueError:
                    print_err("参数错误: 章节号必须为整数。例如: review 2")
                    continue
                cmd_review(c_num)
            elif cmd == "export":
                cmd_export(state)
            elif cmd == "style":
                cmd_style(state, args)
            elif cmd == "rag":
                cmd_rag(state)
            elif cmd == "update":
                cmd_update()
            else:
                print_err(f"未知命令: {cmd}。输入 help 显示帮助列表。")
        except KeyboardInterrupt:
            console.print(f"\n  [{C_WARN}]已捕获 Ctrl+C，如需退出请输入 exit。[/{C_WARN}]")
        except EOFError:
            console.print(f"\n  [{C_WARN}]输入流已结束，正在退出...[/{C_WARN}]")
            break
        except Exception as e:
            print_err(f"执行出错: {e}")

# ═══════════════════════════════════════════════════════════════
#  CLI 入口
# ═══════════════════════════════════════════════════════════════
def main():
    state = load_state()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "status":
            cmd_status(state)
        elif cmd == "init":
            cmd_init(state)
        elif cmd == "export":
            cmd_export(state)
        elif cmd == "review" and len(sys.argv) > 2:
            try:
                c_num = int(sys.argv[2])
                cmd_review(c_num)
            except ValueError:
                print_err("章节号必须为整数！")
        elif cmd == "write":
            count = 1
            if len(sys.argv) > 2:
                try:
                    count = int(sys.argv[2])
                except ValueError:
                    if sys.argv[2] == "--chapters" and len(sys.argv) > 3:
                        count = int(sys.argv[3])
            cmd_write(state, count)
        elif cmd == "trend" and len(sys.argv) > 2:
            sub = sys.argv[2].lower()
            if sub == "fetch":
                cmd_trend_fetch()
            elif sub == "kb":
                cmd_trend_kb()
            elif sub == "stats":
                cmd_trend_stats()
        elif cmd == "style":
            cmd_style(state, sys.argv[2:])
        elif cmd in STYLE_SHORTCUTS:
            cmd_style(state, ["set", cmd])
        elif cmd == "rag":
            cmd_rag(state)
        elif cmd == "update":
            cmd_update()
        elif cmd == "help":
            cmd_help()
        else:
            print_err("参数错误或未知命令！请输入 'python novel.py' 进入交互式界面。")
    else:
        start_interactive_shell()

if __name__ == "__main__":
    main()
