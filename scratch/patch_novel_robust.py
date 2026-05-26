# -*- coding: utf-8 -*-
import os

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOVEL_PY_PATH = os.path.join(WORKSPACE_DIR, "novel.py")

with open(NOVEL_PY_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Standardize newlines internally
content = content.replace("\r\n", "\n")

def replace_by_boundaries(text, start_marker, end_marker, replacement):
    start_idx = text.find(start_marker)
    if start_idx == -1:
        raise ValueError(f"Could not find start marker: {start_marker}")
    
    end_idx = text.find(end_marker, start_idx + len(start_marker))
    if end_idx == -1:
        raise ValueError(f"Could not find end marker: {end_marker}")
    
    return text[:start_idx] + replacement + text[end_idx:]

# 1. Replace cmd_status
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
        f"[bold #C77A8E]📕 书  名[/bold #C77A8E]   [bold white]《{state['novel_title']}》[/bold white]\\n"
        f"[bold #C77A8E]🎨 题材类型[/bold #C77A8E]   [bold white]{genre_display}[/bold white]\\n"
        f"[bold #C77A8E]📝 简  介[/bold #C77A8E]   [white]{state['synopsis'][:60]}{'...' if len(state['synopsis']) > 60 else ''}[/white]\\n"
        f"\\n"
        f"[bold #FFB703]⚙  核心设定[/bold #FFB703]  {settings_badge}\\n"
        f"[bold #FFB703]📐 大纲状态[/bold #FFB703]  {outline_badge}\\n"
        f"[bold #FFB703]📖 已写内容[/bold #FFB703]  [{C_GOLD}]{len(state['chapters'])} {unit_name}[/{C_GOLD}]\\n"
        f"[bold #FFB703]📊 累计字数[/bold #FFB703]  [{C_GOLD}]{total_words:,} 字[/{C_GOLD}]\\n"
        f"\\n"
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
\n"""

# 2. Replace cmd_write
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
            f"根据小说的【核心设定】，策划包含起、承、转、合四个部分的精品短篇大纲。\\n\\n"
            f"【故事核心设定】：\\n{core_settings}\\n\\n"
            f"大纲规范要求：\\n{step6_tmpl}"
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
                f"你正在写一篇 5000-10000 字的短篇故事，现在需要撰写第 {seg_num} 部分: 【{seg}】 的正文初稿。\\n"
                f"【硬性字数限制】：字数必须在 {limit['min']}-{limit['max']} 字之间，目标约 {limit['target']} 字。\\n"
                f"【注意】：你必须承接已经写好的前文部分，并为下一部分的发展或反转留下合理的伏笔或铺垫。\\n\\n"
                f"【核心设定】：\\n{core_settings}\\n\\n"
                f"【全篇起承转合结构大纲】：\\n{story_outline}\\n\\n"
                f"【已写好的前文】：\\n{previous_parts_text if previous_parts_text else '（无，这是开篇第一段）'}\\n\\n"
                f"正文写作指南：\\n{step8_tmpl}"
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
                f"请对这篇短篇小说的第 {seg_num} 部分 【{seg}】 的初稿内容运行人设一致性、逻辑一致性及冗余、字数的深度审查，并输出审查报告。\\n\\n"
                f"【硬性字数审查】：本段字数区间应在 {limit['min']}-{limit['max']} 字之间。如果不符合，请作为 🔴 必须修改提出。\\n\\n"
                f"【核心大纲】：\\n{story_outline}\\n\\n"
                f"【已写好的前文】：\\n{previous_parts_text if previous_parts_text else '（无）'}\\n\\n"
                f"【需审查的本段正文】：\\n{draft_content}\\n\\n"
                f"审查标准：\\n{step9_tmpl}"
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
                f"请结合【编辑审查报告】中的修改建议，对【初稿】进行全面精修重写，加深反转，严控字数。\\n"
                f"要求：\\n"
                f"1. 严格遵守字数：{limit['min']}-{limit['max']} 字之间。\\n"
                f"2. 只输出重写后的最终正文，不要输出任何Markdown格式以外的碎话前言，直接给出正文。\\n\\n"
                f"【全篇结构大纲】：\\n{story_outline}\\n\\n"
                f"【已写好的前文】：\\n{previous_parts_text if previous_parts_text else '（无）'}\\n\\n"
                f"【初稿正文】：\\n{draft_content}\\n\\n"
                f"【编辑审查报告】：\\n{review_report}"
            )
            
            print_step(4, 5, f"应用质检纠偏 · 重写定稿 {seg}")
            with console.status(f"[bold #C77A8E]  💎 磨砺字句，精修 {seg} 部分中...", spinner="dots12", spinner_style="#FFB703"):
                try:
                    final_part_content = call_deepseek(rewrite_prompt, system_role_draft)
                    story_content_parts.append(final_part_content.strip())
                    previous_parts_text += f"\\n\\n### 分段{seg_num}：{seg}\\n{final_part_content.strip()}"
                    print_ok(f"{seg} 部分定稿（约 {len(final_part_content):,} 字）")
                except Exception as e:
                    print_err(f"重写 {seg} 部分失败: {e}")
                    return
                    
        # 3. 合并全篇并写入文件
        print_step(5, 5, "正在进行全篇大融合与排版保存...")
        full_novel_text = f"# {state['novel_title']}\\n\\n## 故事简介\\n{state['synopsis']}\\n\\n## 故事大纲\\n{story_outline}\\n\\n"
        for idx, part in enumerate(story_content_parts):
            full_novel_text += f"\\n\\n{part}\\n"
            
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
            f"根据作品的【核心设定】和【前情提要】，为小说的「第{c_num}{unit_name}」策划详细大纲。\\n"
            f"注意：如果 c_num 是 1、2、3，必须在细纲中落实对应的「黄金三章」要求！\\n\\n"
            f"【核心设定】：\\n{core_settings}\\n\\n"
            f"【前情提要】：\\n{prev_context}\\n\\n"
            f"大纲规范要求：\\n{step6_tmpl}"
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
                f"【RAG小抄】：\\n{rag_sheet}\\n\\n"
                f"【RAG小抄进入正文的使用规则】：\\n{rag_usage_rules}\\n\\n"
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
            f"根据【核心设定】、【前情提要】和已策划好的【章节细纲】，撰写第 {c_num} {unit_name} 的正文初稿。\\n"
            f"请严格遵守创作原则，严防AI腔调和禁用词，段落要短，多用生活化有颗粒感细节。\\n"
            f"【硬性字数要求】：{word_rule}\\n"
            f"【短句段落限制】：{paragraph_rule}\\n\\n"
            f"【小说核心设定】：\\n{core_settings}\\n\\n"
            f"【前情提要】：\\n{prev_context}\\n\\n"
            f"【本章章节大纲】：\\n{chapter_outline}\\n\\n"
            f"【当前激活文风】：{active_style}\\n"
            f"【当前小说文风与模仿要求】：\\n{active_style_desc}\\n\\n"
            f"【文风Reference】：\\n{style_prompt}\\n\\n"
            f"{rag_prompt}"
            f"正文写作指南与禁区：\\n{step8_tmpl}"
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
            f"请作为质检编辑，对【正文初稿】运行人设一致性、逻辑一致性及去AI味的深度自审，并输出审查报告。\\n\\n"
            f"【硬性字数审查】：{word_rule} 若偏离该区间，必须列为 🔴 必须修改。\\n"
            f"【短句段落审查】：{paragraph_rule} 若超限，必须列为 🔴 必须修改。\\n\\n"
            f"【核心设定】：\\n{core_settings}\\n\\n"
            f"【章节大纲】：\\n{chapter_outline}\\n\\n"
            f"【前情提要】：\\n{prev_context}\\n\\n"
            f"【当前小说文风与模仿要求】：\\n{active_style_desc}\\n\\n"
            f"{rag_prompt}"
            f"【需审查的正文初稿】：\\n{draft_content}\\n\\n"
            f"审查标准规范：\\n{step9_tmpl}"
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
            f"请结合【编辑审查报告】中的修改建议，对【初稿】进行全面重写并最终定稿。\\n"
            f"要求：\\n"
            f"1. 严格纠正人设偏离、逻辑伤与AI味。\\n"
            f"2. {word_rule}\\n"
            f"3. {paragraph_rule}\\n"
            f"4. 只输出重写后的最终正文，以「# 第{c_num}{unit_name}：标题」形式的一级标题开头，不要输出任何其他Markdown以外的碎话前言，直接给出定稿。\\n\\n"
            f"【当前小说文风与模仿要求】：\\n{active_style_desc}\\n\\n"
            f"{rag_prompt}"
            f"【当前章节大纲】：\\n{chapter_outline}\\n\\n"
            f"【初稿正文】：\\n{draft_content}\\n\\n"
            f"【编辑审查报告】：\\n{review_report}"
        )
        
        print_step(5, 5, f"应用质检纠偏 · 精修定稿")
        with console.status(f"[bold #C77A8E]  {STEP_ICONS['rewrite']} 千锤百炼，精修定稿中...", spinner="dots12", spinner_style="#FFB703"):
            try:
                final_content = call_deepseek(rewrite_prompt, system_role_draft)
                
                if not final_content.strip().startswith("#"):
                    title_match = re.search(rf"第\d+{unit_name}：(.*)", chapter_outline)
                    c_title = title_match.group(1).strip() if title_match else "未命名章节"
                    final_content = f"# 第{c_num}{unit_name}：{c_title}\\n\\n" + final_content.strip()
                
                filename = f"chapter_{c_num:02d}.md"
                filepath = os.path.join(WORKSPACE_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as cf:
                    cf.write(final_content)
                
                first_line = final_content.strip().split("\\n")[0]
                t_match = re.match(rf"^#\\s*第\\s*(\\d+)\\s*[{unit_name}回]\\s*[:：\\s]*\\s*(.*)$", first_line)
                resolved_title = t_match.group(2).strip() if t_match else first_line.lstrip("#").strip()
                
                state["chapters"][str(c_num)] = {
                    "title": resolved_title,
                    "file": filename,
                    "status": "completed"
                }
                save_state(state)
                
                console.print()
                console.print(Panel(
                    f"[{C_SUCCESS}]{STEP_ICONS['success']} 第 {c_num} {unit_name} 定稿完成[/{C_SUCCESS}]\\n"
                    f"[white]📄 文件：{filename}[/white]\\n"
                    f"[white]📖 标题：《{resolved_title}》[/white]\\n"
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
\n"""

content = replace_by_boundaries(content, "def cmd_write(state, chapter_count=1):", "def cmd_review(chapter_num):", new_write)
print("cmd_write replaced successfully")

# Write back
with open(NOVEL_PY_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS RE-PATCH 2")
