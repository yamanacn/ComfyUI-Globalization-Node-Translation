## 免责说明

- 本项目全程由cursor制作，本人只提供程序实现的思路，项目中可能存在废弃的代码与本人无关，纯粹cursor没删掉。
- 特别鸣谢：[@AIGODLIKE](https://github.com/AIGODLIKE) 只剩一瓶辣椒酱老师和维护翻译工作的所有老师，感谢他们为英文不好的我在摸索comfyui中提供的帮助。
- 如果程序对你有帮助，请点个star，代码全部开源，任何人都可以优化
# ComfyUI节点翻译工具

一个用于翻译ComfyUI节点定义的工具，支持多语言翻译功能。

## 功能特点

- 支持拖拽文件夹进行批量处理
- 支持中文翻译和全球化翻译（包括俄语、日语、韩语、法语）
- 使用火山引擎API进行专业翻译
- 友好的图形用户界面
- 实时翻译进度显示
- 火山引擎注册地址：https://www.volcengine.com/experience/ark?utm_term=202502dsinvite&ac=DSASUQY5&rc=R697K17V
-火山引擎教程：https://www.bilibili.com/video/BV1LCN2eZEAX/?spm_id_from=333.1387.homepage.video_card.click&vd_source=ae85ec1de21e4084d40c5d4eec667b8f

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

