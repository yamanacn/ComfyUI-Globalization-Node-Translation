## 免责说明

- 本项目全程由cursor制作，本人只提供程序实现的思路，项目中可能存在废弃的代码与本人无关，纯粹cursor没删掉。
- 特别鸣谢：[@AIGODLIKE](https://github.com/AIGODLIKE) 只剩一瓶辣椒酱老师和维护翻译工作的所有老师，感谢他们为英文不好的我在摸索comfyui中提供的帮助。
- 使用官方的翻译，请先禁用AIGODLIKE插件
- 如果程序对你有帮助，请点个star，代码全部开源，任何人都可以优化
## 目前已知的一些有意思的Bug
- 如果使用第三方的侧边栏插件ComfyUI-N-Sidebar，用中文搜索时能正确搜到节点，但是拖出来后，节点的标题名会显示英文，除了标题名其他正确显示中文，所以建议用官方的侧边栏和搜索框
- 请将释放链接设置为搜索框，旧版的上下文菜单不能正确的显示中文（官方没维护，无论什么语言都会显示英文，与翻译无关，希望官方维护一下）

## ComfyUI节点翻译工具
#注意：如果批量拖拽插件文件夹时，一次性请不要拖拽太多，建议10个文件夹左右
#原因：部分老旧的插件，节点编写可能不规范，检测节点时会报错，导致程序停止

## 功能特点

- 支持拖拽文件夹进行批量处理
- 支持中文翻译和全球化翻译（包括俄语、日语、韩语、法语）
- 使用火山引擎API进行专业翻译
- 友好的图形用户界面
- 实时翻译进度显示
- 火山引擎注册地址：https://www.volcengine.com/
- 火山引擎教程：https://www.bilibili.com/video/BV1LCN2eZEAX/

## 系统要求

- Windows 10及以上系统
- Python 3.8 - 3.11
- 稳定的网络连接

## 安装步骤

1. 安装Python（3.8-3.11版本）需要正确的配置到系统环境变量中
2. 下载本项目代码
3. 运行`run.bat`脚本，它会自动：
   - 创建虚拟环境
   - 安装所需依赖
   - 启动程序
4. 首次运行时，在程序界面的API设置区域填入：
   - API Key：你的火山引擎API密钥
   - Model ID：你的模型ID
   然后点击"保存配置"按钮。配置文件会被安全地保存在用户主目录下的`.comfyui_translator`文件夹中。

## 使用方法

1. 启动程序后，在API设置区域填入：
   - API Key
   - Model ID
2. 将ComfyUI插件文件夹拖入程序窗口
3. 选择翻译模式：
   - 仅中文翻译
   - 全球化翻译
4. 点击"开始解析"按钮
5. 点击"开始翻译"按钮
6. 等待翻译完成

## 注意事项

- 首次使用前请确保配置正确的API信息
- 建议在翻译前备份原始文件
- 翻译过程中请保持网络连接
- 可以随时使用"终止翻译"按钮停止操作

## 作者

OLDX

## 许可证

MIT License

