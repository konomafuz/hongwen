# -*- coding: utf-8 -*-
import os

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOVEL_PY_PATH = os.path.join(WORKSPACE_DIR, "novel.py")

with open(NOVEL_PY_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the line endings to LF internally to do standard replacement, then write back as-is (Python open with 'w' handles platform-specific endings or writes correctly).
# Standardize newlines internally
content = content.replace("\r\n", "\n")

# 1. Patch cmd_status
old_status = """def cmd_status(state):
    print_section_header("项目全貌", STEP_ICONS['status'])

    # 构建进度条可视化
    total_steps = 4  # 设定 / 大纲 / 章节 / 导出
    done = sum([
        state['settings_created'],
        state['outline_created'],
        len(state['chapters']) > 0,
        os.path.exists(os.path.join(WORKSPACE_DIR, f"{state['novel_title']}.docx"))
    ])
    pct = int(done / total_steps * 100)
    bar_len = 30
    filled = int(bar_len * done / total_steps)
    bar = f"[#C77A8E]{'█' * filled}[/#C77A8E][#3D3D3D]{'░' * (bar_len - filled)}[/#3D3D3D]"

    settings_badge = f"[{C_SUCCESS}]✔ 已建立[/{C_SUCCESS}]" if state['settings_created'] else f"[{C_ERROR}]✘ 未建立[/{C_ERROR}]"
    outline_badge  = f"[{C_SUCCESS}]✔ 已生成[/{C_SUCCESS}]" if state['outline_created']  else f"[{C_ERROR}]✘ 未生成[/{C_ERROR}]"

    # 统计总字数
    total_words = 0
    for k, ch in state["chapters"].items():
        fpath = os.path.join(WORKSPACE_DIR, ch["file"])
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    total_words += len(f.read())
            except Exception:
                pass

    status_content = (
        f"[bold #C77A8E]📕 书  名[/bold #C77A8E]   [bold white]《{state['novel_title']}》[/bold white]\n"
        f"[bold #C77A8E]📝 简  介[/bold #C77A8E]   [white]{state['synopsis'][:60]}{'...' if len(state['synopsis']) > 60 else ''}[/white]\n"
        f"\n"
        f"[bold #FFB703]⚙  核心设定[/bold #FFB703]  {settings_badge}\n"
        f"[bold #FFB703]📐 大纲状态[/bold #FFB703]  {outline_badge}\n"
        f"[bold #FFB703]📖 已写章节[/bold #FFB703]  [{C_GOLD}]{len(state['chapters'])} 章[/{C_GOLD}]\n"
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
    
    if state["chapters"]:
        table = Table(
            box=ROUNDED,
            border_style="#A8687A",
            header_style="bold #FFB703 on #1A1A2E",
            show_lines=True,
            padding=(0, 1),
        )
        table.add_column("章  节", style="bold #FFB703", justify="center", width=10)
        table.add_column("章 节 标 题", style="white", min_width=24)
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
                f"第 {k} 章",
                ch["title"],
                ch["file"],
                wc,
                "✔ 定稿"
            )
        console.print(Align.center(table))
    else:
        console.print(Align.center(
            Text("尚无章节，输入 write 开始创作你的故事吧 ✨", style=f"italic {C_PINK}")
        ))"""

new_status = """def cmd_status(state):
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
        ))"""

content = content.replace(old_status, new_status)

# 2. Patch cmd_init
old_init = """def cmd_init(state):
    if state["settings_created"] and state["outline_created"]:
        overwrite = Confirm.ask(f"  [{C_WARN}]检测到当前小说已完成初始化。重新初始化会清空章节进度，是否确认？[/{C_WARN}]")
        if not overwrite:
            return

    print_section_header("初始化小说创作项目", STEP_ICONS['init'])
    
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
            
    # 从零开始生成
    console.print(f"  [{C_PINK}]请输入新作品的基本信息：[/{C_PINK}]\n")
    title = Prompt.ask(f"  [{C_GOLD}]📕 新小说书名[/{C_GOLD}]", default="绑定吃瓜系统，我靠剧透爆红了")
    synopsis = Prompt.ask(f"  [{C_GOLD}]📝 核心选题概念[/{C_GOLD}]", default="女主绑定舆情预警系统，能在心里吐槽吃瓜，而且心声会在方圆5米内被男主 and 身边人听到，在职场直播节目中反杀爆红的故事。")
    
    state["novel_title"] = title
    state["synopsis"] = synopsis
    state["settings_created"] = False
    state["outline_created"] = False
    state["chapters"] = {}
    save_state(state)
    
    # 开始生成核心设定 (步骤2)
    step2_prompt_file = os.path.join(REFERENCES_DIR, "step02-core-settings.md")
    if not os.path.exists(step2_prompt_file):
        print_err("找不到步骤2核心设定模板文件 references/step02-core-settings.md")
        return
        
    with open(step2_prompt_file, "r", encoding="utf-8") as f:
        step2_tmpl = f.read()
        
    prompt = f"请根据以下输入，执行步骤2的任务，生成小说的核心设定文档。\n【书名】：{title}\n【简介】：{synopsis}\n\n大纲模板指导内容：\n{step2_tmpl}"
    
    print_step(1, 2, "构建《核心设定》文档 (DeepSeek)")
    with console.status(f"[bold #C77A8E]  🪶 执笔织梦中，世界观正在成型...", spinner="dots12", spinner_style="#FFB703"):
        try:
            settings_content = call_deepseek(prompt, "你是一位资深女频网文世界观架构师。")
            with open(SETTINGS_FILE, "w", encoding="utf-8") as sf:
                sf.write(settings_content)
            state["settings_created"] = True
            save_state(state)
            print_ok("核心设定已生成 → novel_core_settings.md")
        except Exception as e:
            print_err(f"生成核心设定失败: {e}")
            return

    # 生成简介与推荐语 (步骤3)
    step3_prompt_file = os.path.join(REFERENCES_DIR, "step03-tags-synopsis.md")
    if os.path.exists(step3_prompt_file):
        with open(step3_prompt_file, "r", encoding="utf-8") as f:
            step3_tmpl = f.read()
        prompt = f"基于小说书名《{title}》 and 已经生成的【核心设定】内容，执行步骤3生成小说的标签和三版简介。\n\n【核心设定】内容：\n{settings_content}\n\n模板要求：\n{step3_tmpl}"
        print_step(2, 2, "构建《标签与简介》文档 (DeepSeek)")
        with console.status(f"[bold #C77A8E]  🪶 锦绣文案凝练中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                synopsis_content = call_deepseek(prompt, "你是一位精通番茄女频爆款简介的文案策划专家。")
                with open(SYNOPSIS_FILE, "w", encoding="utf-8") as syf:
                    syf.write(synopsis_content)
                state["outline_created"] = True
                save_state(state)
                print_ok("标签与三版简介已生成 → novel_tags_synopsis.md")
            except Exception as e:
                print_err(f"生成标签简介失败: {e}")
                return
                
    print_ok("小说项目初始化完成！现在可以输入 write N 自动生成章节正文。")"""

# Note the slight typo 'and' in the original code for step 3 is matched correctly.
new_init = """def cmd_init(state):
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
    console.print(f"  1. 女频长篇 (1800-2200字，注重甜宠/情感拉扯/吃瓜打脸)")
    console.print(f"  2. 男频长篇 (2000-3000字，注重金手指/升级流/热血打脸)")
    console.print(f"  3. 精品短篇 (5000-10000字单章，分段叙事/高概念/高反转)")
    console.print(f"  4. 短剧剧本 (300-500字单集，标准剧本格式/极快节奏/集尾钩子)")
    
    type_choice = Prompt.ask(f"  [{C_GOLD}]请选择数字 (1-4)[/{C_GOLD}]", default="1", choices=["1", "2", "3", "4"])
    type_mapping = {
        "1": "female_novel",
        "2": "male_novel",
        "3": "short_story",
        "4": "short_drama"
    }
    book_type = type_mapping[type_choice]
    book_cfg = load_book_type_config(book_type)
    
    console.print(f"\n  [{C_PINK}]请输入新作品的基本信息：[/{C_PINK}]\n")
    default_title = "绑定吃瓜系统，我靠剧透爆红了" if book_type == "female_novel" else ("我有万物升级系统" if book_type == "male_novel" else "红雨衣的秘密")
    title = Prompt.ask(f"  [{C_GOLD}]📕 新书名/剧名[/{C_GOLD}]", default=default_title)
    default_synopsis = "女主绑定心声剧透系统..." if book_type == "female_novel" else ("主角觉醒升级万物挂，一路扮猪吃老虎..." if book_type == "male_novel" else "关于一件诡异红色雨衣的故事...")
    synopsis = Prompt.ask(f"  [{C_GOLD}]📝 核心选题概念/故事大纲简介[/{C_GOLD}]", default=default_synopsis)
    
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
                
    print_ok("项目初始化完成！现在可以输入 write 开始创作。")"""

content = content.replace(old_init, new_init)

# 3. Patch run_rag_retrieve genre
old_rag_genre = """        # 根据当前风格自动追加题材参数
        # 如果是“古言雅致”，强行指定 --genre 古言，从而在 rag_retrieve 中激活题材冲突硬拦截
        if active_style == "古言雅致":
            cmd.extend(["--genre", "古言"])"""

new_rag_genre = """        # 自动根据项目题材追加题材过滤参数
        book_type = state.get("book_type", "female_novel")
        cmd.extend(["--genre", book_type])"""

content = content.replace(old_rag_genre, new_rag_genre)

# 4. Patch cmd_write
old_write = """def cmd_write(state, chapter_count=1):
    if not state["settings_created"]:
        print_err("项目尚未初始化设定，请先运行 init 命令。")
        return
        
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            core_settings = f.read()
    except Exception as e:
        print_err(f"读取核心设定失败: {e}")
        return
        
    start_chap = len(state["chapters"]) + 1
    end_chap = start_chap + chapter_count - 1
    
    print_section_header(
        f"全自动章节创作管线 · 第 {start_chap}–{end_chap} 章",
        STEP_ICONS['draft']
    )
    print_atmosphere_quote()
    console.print()
    
    for c_num in range(start_chap, end_chap + 1):
        console.print(Panel(
            f"[bold #FFB703]{STEP_ICONS['chapter']} 正在创作第 {c_num} 章[/bold #FFB703]",
            border_style="#C77A8E",
            box=HEAVY,
            padding=(0, 2),
        ))
        
        # 1. 获取前情提要
        prev_context = "无（这是小说的开篇第一章）"
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
        step6_prompt_file = os.path.join(REFERENCES_DIR, "step06-chapter-outline.md")
        if not os.path.exists(step6_prompt_file):
            print_err("找不到步骤6章节大纲模板。")
            return
            
        with open(step6_prompt_file, "r", encoding="utf-8") as f:
            step6_tmpl = f.read()
            
        outline_prompt = (
            f"根据小说的【核心设定】和【前情提要】，为小说的「第{c_num}章」策划详细的章节细纲。\n"
            f"注意：如果 c_num 是 1、2、3，必须在细纲和写作注意中强制落实模板里规定的「黄金三章」对应章节要求！\n\n"
            f"【小说核心设定】：\n{core_settings}\n\n"
            f"【前情提要】：\n{prev_context}\n\n"
            f"章节细纲规范要求：\n{step6_tmpl}"
        )
        
        print_step(1, 5, f"策划第 {c_num} 章详细细纲")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['outline']} 谋篇布局，章节骨架搭建中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                chapter_outline = call_deepseek(outline_prompt, "你是一位精通女频网文架构的大纲策划专家。")
                print_ok(f"第 {c_num} 章大纲策划完成")
            except Exception as e:
                print_err(f"策划大纲失败: {e}")
                return

        # 3. RAG 小抄与文风加载
        print_step(2, 5, f"匹配第 {c_num} 章文风与语感素材")
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
        step8_prompt_file = first_existing_path(
            os.path.join(DRAFT_REFERENCES_DIR, "step08-write-content.md"),
            os.path.join(REFERENCES_DIR, "step08-write-content.md"),
        )
        if not os.path.exists(step8_prompt_file):
            print_err("找不到步骤8正文创作模板。")
            return
            
        with open(step8_prompt_file, "r", encoding="utf-8") as f:
            step8_tmpl = f.read()
            
        write_prompt = (
            f"根据【核心设定】、【前情提要】和已策划好的【章节细纲】，撰写第 {c_num} 章的正文初稿。\n"
            f"请严格遵守创作原则，严防AI腔调和禁用词，段落要短，多用生活化有颗粒感细节。\n"
            f"【硬性字数要求】：{CHAPTER_LENGTH_RULE}\n"
            f"【短句段落限制】：{SHORT_PARAGRAPH_RULE}\n\n"
            f"【小说核心设定】：\n{core_settings}\n\n"
            f"【前情提要】：\n{prev_context}\n\n"
            f"【本章章节大纲】：\n{chapter_outline}\n\n"
            f"【当前激活文风】：{active_style}\n"
            f"【当前小说文风与模仿要求】：\n{active_style_desc}\n\n"
            f"【文风Reference】：\n{style_prompt}\n\n"
            f"{rag_prompt}"
            f"正文写作指南与禁区：\n{step8_tmpl}"
        )
        
        print_step(3, 5, f"撰写第 {c_num} 章正文初稿")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['draft']} 落笔生花，初稿挥就中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                draft_content = call_deepseek(write_prompt, "你是一位番茄小说女频热门作者，文风生活化、有颗粒感。")
                print_ok(f"第 {c_num} 章初稿完成（约 {len(draft_content):,} 字）")
            except Exception as e:
                print_err(f"撰写初稿失败: {e}")
                return

        # 5. 自动审查
        step9_prompt_file = os.path.join(REFERENCES_DIR, "step09-check-content.md")
        if not os.path.exists(step9_prompt_file):
            print_err("找不到步骤9正文审查模板。")
            return
            
        with open(step9_prompt_file, "r", encoding="utf-8") as f:
            step9_tmpl = f.read()
            
        review_prompt = (
            f"请作为质检编辑，严格对照小说的【核心设定】（特别是男女主和出场配角的外貌、动作、言行及感情线阶段），以及【本章章节细纲】，对刚写出的【正文初稿】运行人设一致性、逻辑一致性及去AI味的深度自审，并输出审查报告。\n\n"
            f"【硬性字数审查】：{CHAPTER_LENGTH_RULE} 若偏离该区间，必须列为 🔴 必须修改。\n"
            f"【短句段落审查】：{SHORT_PARAGRAPH_RULE} 若超限或出现车轱辘短句排比，必须列为 🔴 必须修改。\n\n"
            f"【核心设定】：\n{core_settings}\n\n"
            f"【本章章节大纲】：\n{chapter_outline}\n\n"
            f"【前情提要】：\n{prev_context}\n\n"
            f"【当前小说文风与模仿要求】：\n{active_style_desc}\n\n"
            f"{rag_prompt}"
            f"【需审查的正文初稿】：\n{draft_content}\n\n"
            f"审查标准规范：\n{step9_tmpl}"
        )
        
        print_step(4, 5, f"运行人设与逻辑纠偏审查")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['review']} 毒舌编辑上线，逐字审稿中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                review_report = call_deepseek(review_prompt, "你是一位毒舌但专业的女频网文质检编辑，专砍废话、注水和AI味。")
                print_ok(f"第 {c_num} 章质检报告输出完成")
            except Exception as e:
                print_err(f"自审失败: {e}")
                return

        # 6. 自审纠偏与精修重写
        rewrite_prompt = (
            f"请结合【编辑审查报告】中的修改建议、冗余精简意见和人设偏差纠正意见，对【初稿】进行全面重写。\n"
            f"要求：\n"
            f"1. 严格纠正所有人设偏离（特别是性格、动作、称呼等）、逻辑硬伤和AI味词汇。\n"
            f"2. {CHAPTER_LENGTH_RULE}\n"
            f"3. 必须彻底保留初稿中写得好的地方。\n"
            f"4. {SHORT_PARAGRAPH_RULE}\n"
            f"5. 只输出重写后的最终章节正文，以「# 第{c_num}章：章节名」形式的一级标题开头，不要输出任何其他前言、后记、回复或多余的Markdown区块，直接给出正文。\n\n"
            f"【当前小说文风与模仿要求】：\n{active_style_desc}\n\n"
            f"{rag_prompt}"
            f"【当前章节大纲】：\n{chapter_outline}\n\n"
            f"【初稿正文】：\n{draft_content}\n\n"
            f"【编辑审查报告】：\n{review_report}"
        )
        
        print_step(5, 5, f"应用质检纠偏 · 精修定稿")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['rewrite']} 千锤百炼，精修定稿中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                final_content = call_deepseek(rewrite_prompt, "你是一位番茄小说女频热门作者，擅长吸纳编辑的意见进行精细化修改和重写。")
                
                if not final_content.strip().startswith("#"):
                    title_match = re.search(r"第\d+章：(.*)", chapter_outline)
                    c_title = title_match.group(1).strip() if title_match else "未命名章节"
                    final_content = f"# 第{c_num}章：{c_title}\n\n" + final_content.strip()
                
                filename = f"chapter_{c_num:02d}.md"
                filepath = os.path.join(WORKSPACE_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as cf:
                    cf.write(final_content)
                
                first_line = final_content.strip().split("\n")[0]
                t_match = re.match(r"^#\s*第\s*(\d+)\s*[章回]\s*[:：\s]*\s*(.*)$", first_line)
                resolved_title = t_match.group(2).strip() if t_match else first_line.lstrip("#").strip()
                
                state["chapters"][str(c_num)] = {
                    "title": resolved_title,
                    "file": filename,
                    "status": "completed"
                }
                save_state(state)
                
                console.print()
                console.print(Panel(
                    f"[{C_SUCCESS}]{STEP_ICONS['success']} 第 {c_num} 章定稿完成[/{C_SUCCESS}]\n"
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
        Text(f"✨ 本批次 {chapter_count} 章自动写作全部完成！正在触发编译打包... ✨", style=f"bold {C_SUCCESS}")
    ))
    print_divider("#06D6A0", "═")
    cmd_export(state)"""

new_write = """def cmd_write(state, chapter_count=1):
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
        prev_context = f"无（这是开篇第一{unit_name}）"
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
    cmd_export(state)"""

content = content.replace(old_write, new_write)

# 5. Patch cmd_review
old_review = """def cmd_review(chapter_num):
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
            print_err(f"自审失败: {e}")"""

# Wait, the cmd_review in the file was already modified slightly or was old? Let's check lines 1316-1365 from our previous cascade replace.
# The previous cascade replaced cmd_review but it failed because it matched wrong. Let's make sure it's matched exactly in its original form first.
old_review_original = """def cmd_review(chapter_num):
    print_section_header(f"深度审查 · 第 {chapter_num} 章", STEP_ICONS['review'])

    filename = f"chapter_{chapter_num:02d}.md"
    filepath = os.path.join(WORKSPACE_DIR, filename)
    if not os.path.exists(filepath):
        filename = f"chapter_{chapter_num}.md"
        filepath = os.path.join(WORKSPACE_DIR, filename)
        
    if not os.path.exists(filepath):
        print_err(f"找不到第 {chapter_num} 章的正文文件 chapter_{chapter_num:02d}.md")
        return
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            chapter_content = f.read()
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            core_settings = f.read()
    except Exception as e:
        print_err(f"读取文件失败: {e}")
        return
        
    step9_prompt_file = os.path.join(REFERENCES_DIR, "step09-check-content.md")
    if not os.path.exists(step9_prompt_file):
        print_err("找不到步骤9正文审查模板。")
        return
        
    with open(step9_prompt_file, "r", encoding="utf-8") as f:
        step9_tmpl = f.read()
        
    review_prompt = (
        f"请作为质检编辑，严格对照小说的【核心设定】（特别是男女主和出场配角的外貌、动作、言行及感情线阶段），对该章节正文进行深度人设一致性、逻辑一致性及去AI味的深度质检，并输出审查报告。\n\n"
        f"【核心设定】：\n{core_settings}\n\n"
        f"【需审查的正文内容】：\n{chapter_content}\n\n"
        f"审查标准规范：\n{step9_tmpl}"
    )
    
    with console.status(f"[bold #C77A8E]  {STEP_ICONS['review']} 毒舌编辑正在逐字比对质检...", spinner="dots12", spinner_style="#FFB703"):
        try:
            report = call_deepseek(review_prompt, "你是一位毒舌但专业的女频网文质检编辑，专砍废话、注水和AI味。")
            print_section_header(f"第 {chapter_num} 章 · 审查报告", "📋")
            console.print(Panel(
                Markdown(report),
                border_style="#C77A8E",
                box=ROUNDED,
                padding=(1, 2),
            ))
        except Exception as e:
            print_err(f"自审失败: {e}")"""

# Replace the original form of cmd_review
content = content.replace(old_review_original, old_review)

# 6. Patch Shell Banner
old_banner = """    console.print(BANNER)
    console.print(Align.center(
        Text("红 文 织 梦", style="bold #C77A8E")
    ))
    console.print(Align.center(
        Text("番茄小说女频 · 全自动网文创作管线", style=f"bold {C_PINK}")
    ))"""

new_banner = """    console.print(BANNER)
    console.print(Align.center(
        Text("红 文 织 梦", style="bold #C77A8E")
    ))
    console.print(Align.center(
        Text("多体裁全自动小说/剧本创作管线", style=f"bold {C_PINK}")
    ))"""

content = content.replace(old_banner, new_banner)

# Write back
with open(NOVEL_PY_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS")
