# 文风索引

正文创作时先读取本文件，再根据默认配置、用户指定或临时模仿选择一个文风 reference。

## 默认选择

- 默认读取工作区根目录 `styles_config.json` 的 `current_style`。
- 当前配置中的默认激活文风是：`古言雅致`。
- 如果无法读取 `styles_config.json`，读取 `default.md`。

## 可选文风

| 文风名 | 别名/触发词 | Reference |
|---|---|---|
| 古言雅致 | 古言、古代言情、雅致、半文半白 | `guyan-yazhi.md` |
| 现言甜宠 | 现言、甜宠、现代豪门、轻松甜 | `xianyan-tiange.md` |
| 幽默吐槽 | 吐槽、沙雕、系统文、网感强 | `youmo-tucao.md` |
| 悬疑冷峻 | 悬疑、复仇、女强、冷峻 | `xuanyi-lengjun.md` |
| 热血爽文 | 爽文、打脸、反击、快节奏 | `rexue-shuangwen.md` |

## 用户指定

- 如果用户明确说“用某某文风写”，优先读取对应文风 reference，覆盖本次默认配置。
- 如果用户指定的文风名存在于 `styles_config.json.custom`，使用其中的描述作为本次文风要求。

## 临时模仿

- 如果用户粘贴文章或提供参考文本要求模仿，读取 `custom-style-template.md`。
- 先从参考文本中提炼临时文风，再将临时文风作为【当前小说文风与模仿要求】注入正文创作。
- 只有用户明确要求保存时，才把临时文风写入 `styles_config.json` 或新增对应 reference。
