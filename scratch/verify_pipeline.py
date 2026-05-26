# -*- coding: utf-8 -*-
import os
import sys
import shutil
import unittest
import re
from unittest.mock import patch, MagicMock

# Add project root to sys.path
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(WORKSPACE_DIR)

import novel

def mock_call_deepseek(prompt, system_prompt=""):
    print(f"--- [Mock API Call] system: {system_prompt[:50]}... prompt len: {len(prompt)}")
    
    # 1. Polished rewriting (cmd_write rewrite step)
    if "重写" in prompt or "精修" in prompt or "应用质检" in prompt:
        if "short_drama" in prompt or "短剧" in prompt or "第1集" in prompt:
            return (
                "# 第1集：隐秘的少爷\n\n"
                "**第1幕：【场景】写字楼大厅 【时间】日 【人物】沈安然、顾总、苏绿茶**\n"
                "（苏绿茶故意将手里的拿铁朝沈安然身上泼去，顺势倒在地上，红了眼眶）\n"
                "苏绿茶：（哭腔）安然姐姐，我真的不是故意碰瓷你的……\n"
                "（顾总从电梯口走来，看到这一幕，脸色冰冷）\n"
                "顾总:沈安然，你在干什么！\n"
                "（沈安然面无表情，反手直接抽了苏绿茶一记响亮的耳光）\n"
                "沈安然:我教她做人。"
            )
        elif "short_story" in prompt or "短篇" in prompt:
            # Determine segment based on completed segments in "【已写好的前文】"
            if "分段3：" in prompt:
                return "这是短篇小说合的内容。最终一切归于平静，但在阴雨连绵的下午，柜门再次自己缓缓拉开了。"
            elif "分段2：" in prompt:
                return "这是短篇小说转的内容。真相大白，那雨衣根本不是妻子的，而是当年失踪妹妹的遗物！"
            elif "分段1：" in prompt:
                return "这是短篇小说承的内容。主角试探着询问妻子，妻子的眼神闪烁，试图用拙劣的借口掩盖真相。"
            else:
                return "这是短篇小说起的内容。红雨衣的秘密被揭示，在深夜的柜子里，主角颤抖着手碰到了那一角冰冷的水渍。"
        elif "male_novel" in prompt or "男频" in prompt:
            return "# 第1章：逆天万物升级系统\n\n秦飞觉醒了系统，只要消耗升级点就能对世间万物进行无上限的升级！退婚的未婚妻此时正高傲地看着他，却不知他的手掌已经按在了一枚废弃丹药上。"
        else:
            return "# 第1章：心声暴露被全家宠上天\n\n顾安安绑定了吃瓜系统，吃瓜吃到自家大哥身上。她在心里狂呼：【天哪！大哥居然要在今天下午被苏绿茶陷害碰瓷了！】殊不知旁边的大哥将心声听得清楚楚。"

    # 2. Quality Review Report (step09)
    elif "审查" in prompt or "质检" in prompt:
        return "### 编辑审查报告\n\n🔴 必须修改：无\n🟡 建议修改：段落可以更简短\n🟢 优点：人设没有偏离，爽点节奏适中。"

    # 3. First draft creation (cmd_write draft step)
    elif "初稿" in prompt or "正文初稿" in prompt:
        return "这是自动生成的正文初稿内容。用于测试自审与重写逻辑。"

    # 4. Core Settings (step02)
    elif "核心设定" in prompt or "world" in prompt.lower():
        # extract title if possible
        match = re.search(r"【书名】：(.*)\n", prompt)
        title = match.group(1).strip() if match else "未命名作品"
        return f"# 《{title}》 核心设定\n\n这是自动生成的作品核心设定文案，包含人物、主线、背景等细节。"
        
    # 5. Segmented / Chapter Outline (step06)
    elif "大纲" in prompt or "起承转合" in prompt:
        return "# 章节大纲 / 结构大纲\n\n第1集/章：测试大纲标题\n- 起：危机发生\n- 承：情节展开\n- 转：发生反转\n- 合：尘埃落定"
        
    return "这是默认的 Mock API 返回内容。"

class TestNovelPipeline(unittest.TestCase):
    def setUp(self):
        # Backup existing state & settings
        self.backups = {}
        for f in ["novel_project.json", "novel_core_settings.md"]:
            path = os.path.join(WORKSPACE_DIR, f)
            if os.path.exists(path):
                self.backups[f] = path + ".verify_backup"
                shutil.copy2(path, self.backups[f])
                os.remove(path)
                
        # Clean existing chapters
        for f in os.listdir(WORKSPACE_DIR):
            if f.startswith("chapter_") and (f.endswith(".md") or f.endswith(".docx")):
                os.remove(os.path.join(WORKSPACE_DIR, f))
            if f.endswith(".docx") and f != "novel_project.json":
                # delete Word exports created during verification
                try:
                    os.remove(os.path.join(WORKSPACE_DIR, f))
                except Exception:
                    pass

    def tearDown(self):
        # Restore backups
        for f, backup_path in self.backups.items():
            orig_path = os.path.join(WORKSPACE_DIR, f)
            if os.path.exists(orig_path):
                os.remove(orig_path)
            shutil.copy2(backup_path, orig_path)
            os.remove(backup_path)
            
        # Clean generated files from verification
        for f in os.listdir(WORKSPACE_DIR):
            if f.startswith("chapter_") and (f.endswith(".md") or f.endswith(".docx")):
                try:
                    os.remove(os.path.join(WORKSPACE_DIR, f))
                except Exception:
                    pass

    @patch("novel.call_deepseek", side_effect=mock_call_deepseek)
    @patch("rich.prompt.Confirm.ask", return_value=True)
    def test_female_novel_pipeline(self, mock_confirm, mock_ds):
        print("\n================ 测试 1: 女频长篇写作管线 ================")
        state = {}
        
        # Mock init prompt inputs
        inputs = ["1", "绑定吃瓜系统，我靠剧透爆红了", "女主绑定心声剧透系统，心声大暴光，吃瓜大打脸"]
        with patch("rich.prompt.Prompt.ask", side_effect=inputs):
            novel.cmd_init(state)
            
        self.assertTrue(state.get("settings_created"))
        self.assertEqual(state.get("book_type"), "female_novel")
        self.assertTrue(os.path.exists(os.path.join(WORKSPACE_DIR, "novel_core_settings.md")))
        
        # Test writing 1 chapter
        novel.cmd_write(state, 1)
        self.assertIn("1", state.get("chapters"))
        self.assertTrue(os.path.exists(os.path.join(WORKSPACE_DIR, "chapter_01.md")))
        
        # Test Word export
        novel.cmd_export(state)
        export_path = os.path.join(WORKSPACE_DIR, "绑定吃瓜系统，我靠剧透爆红了.docx")
        self.assertTrue(os.path.exists(export_path))
        print("女频长篇测试通过！")

    @patch("novel.call_deepseek", side_effect=mock_call_deepseek)
    @patch("rich.prompt.Confirm.ask", return_value=True)
    def test_male_novel_pipeline(self, mock_confirm, mock_ds):
        print("\n================ 测试 2: 男频长篇写作管线 ================")
        state = {}
        
        # Mock init prompt inputs
        inputs = ["2", "我有万物升级系统", "主角觉醒升级系统，退婚打脸，一步步踏天而上"]
        with patch("rich.prompt.Prompt.ask", side_effect=inputs):
            novel.cmd_init(state)
            
        self.assertTrue(state.get("settings_created"))
        self.assertEqual(state.get("book_type"), "male_novel")
        
        # Test writing 1 chapter
        novel.cmd_write(state, 1)
        self.assertIn("1", state.get("chapters"))
        self.assertTrue(os.path.exists(os.path.join(WORKSPACE_DIR, "chapter_01.md")))
        
        # Test Word export
        novel.cmd_export(state)
        export_path = os.path.join(WORKSPACE_DIR, "我有万物升级系统.docx")
        self.assertTrue(os.path.exists(export_path))
        print("男频长篇测试通过！")

    @patch("novel.call_deepseek", side_effect=mock_call_deepseek)
    @patch("rich.prompt.Confirm.ask", return_value=True)
    def test_short_story_pipeline(self, mock_confirm, mock_ds):
        print("\n================ 测试 3: 精品短篇写作管线 ================")
        state = {}
        
        # Mock init prompt inputs
        inputs = ["3", "红雨衣的秘密", "一件凭空多出来的红色雨衣揭开了一段被掩埋的尘网往事"]
        with patch("rich.prompt.Prompt.ask", side_effect=inputs):
            novel.cmd_init(state)
            
        self.assertTrue(state.get("settings_created"))
        self.assertEqual(state.get("book_type"), "short_story")
        
        # Test writing (it will automatically trigger 起、承、转、合 segmented write)
        novel.cmd_write(state, 1)
        self.assertIn("1", state.get("chapters"))
        self.assertTrue(os.path.exists(os.path.join(WORKSPACE_DIR, "chapter_01.md")))
        
        # Read the content to check if all parts are present
        with open(os.path.join(WORKSPACE_DIR, "chapter_01.md"), "r", encoding="utf-8") as f:
            full_story = f.read()
        self.assertIn("这是短篇小说起的内容", full_story)
        self.assertIn("这是短篇小说承的内容", full_story)
        self.assertIn("这是短篇小说转的内容", full_story)
        self.assertIn("这是短篇小说合的内容", full_story)
        
        # Test Word export
        novel.cmd_export(state)
        export_path = os.path.join(WORKSPACE_DIR, "红雨衣的秘密.docx")
        self.assertTrue(os.path.exists(export_path))
        print("精品短篇测试通过！")

    @patch("novel.call_deepseek", side_effect=mock_call_deepseek)
    @patch("rich.prompt.Confirm.ask", return_value=True)
    def test_short_drama_pipeline(self, mock_confirm, mock_ds):
        print("\n================ 测试 4: 短剧剧本写作管线与排版 ================")
        state = {}
        
        # Mock init prompt inputs
        inputs = ["4", "真少爷当助理", "豪门继承人隐瞒身份做助理，被恶毒上司排挤刁难，最后疯狂打脸"]
        with patch("rich.prompt.Prompt.ask", side_effect=inputs):
            novel.cmd_init(state)
            
        self.assertTrue(state.get("settings_created"))
        self.assertEqual(state.get("book_type"), "short_drama")
        
        # Test writing 1 act/episode
        novel.cmd_write(state, 1)
        self.assertIn("1", state.get("chapters"))
        self.assertTrue(os.path.exists(os.path.join(WORKSPACE_DIR, "chapter_01.md")))
        
        # Test Word export with custom script format parsing
        novel.cmd_export(state)
        export_path = os.path.join(WORKSPACE_DIR, "真少爷当助理.docx")
        self.assertTrue(os.path.exists(export_path))
        print("短剧剧本测试通过！")

if __name__ == "__main__":
    unittest.main()
