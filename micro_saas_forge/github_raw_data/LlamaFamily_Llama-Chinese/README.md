<p align="left">
    <a href="README_EN.md">English</a> ｜ 中文
</p>

<h1 align="center">
  Llama中文社区
</h1>
<p align="center" width="100%">
  <img src="assets/llama.jpg" alt="Llama" style="width: 20%; display: block; margin: auto;"></a>
</p>
<p align="center">
  <font face="黑体" color=orange size="6"> 最好的Llama大模型开源社区 </font>
</p>

<p align="center">
🤗 <a href="https://huggingface.co/FlagAlpha" target="_blank">Hugging Face</a> • 🤖 <a href="https://www.modelscope.cn/organization/FlagAlpha/" target="_blank">ModelScope</a> • ✡️ <a href="https://wisemodel.cn/models/FlagAlpha/Atom-7B-Chat" target="_blank">WiseModel</a>
</p> 

<p align="center">
  <a href="https://llama.com">Llama4原生多模态MoE模型发布！</a>
</p>
<p align="center">
  <a href="https://huggingface.co/FlagAlpha/Atom-7B-Chat">基于Llama的开源中文预训练大模型Atom</a>
</p>

</br></br>


## 🗂️ 目录
- [🗂️ 目录](#️-目录)
- [📌 Llama中文社区](#-llama中文社区)
  - [🔥 社区介绍](#-社区介绍)
    - [为什么选择Llama中文社区？](#为什么选择llama中文社区)
    - [社区活动](#社区活动)
    - [立即加入我们！](#立即加入我们)
  - [🪵 社区资源](#-社区资源)
    - [💻 算力](#-算力)
    - [📊 数据](#-数据)
    - [💬 论坛](#-论坛)
    - [📱 应用](#-应用)
  - [📢 最新动态](#-最新动态)
  - [🤗 模型发布](#-模型发布)
    - [中文预训练模型Atom](#中文预训练模型atom)
    - [Llama4官方模型](#llama4官方模型)
    - [Llama3官方模型](#llama3官方模型)
    - [Llama3中文微调模型](#llama3中文微调模型)
    - [Llama2官方模型](#llama2官方模型)
    - [Llama2中文微调模型](#llama2中文微调模型)
- [📌 如何使用Llama模型](#-如何使用llama模型)
  - [快速上手-使用Anaconda](#快速上手-使用anaconda)
  - [快速上手-使用Docker](#快速上手-使用docker)
  - [快速上手-使用llama.cpp](#快速上手-使用llamacpp)
  - [快速上手-使用gradio](#快速上手-使用gradio)
  - [快速上手-构建API服务](#快速上手-构建api服务)
  - [快速上手-使用ollama运行](#快速上手-使用ollama运行)
- [🤖 模型预训练](#-模型预训练)
- [💡 模型微调](#-模型微调)
  - [Step1: 环境准备](#step1-环境准备)
  - [Step2: 数据准备](#step2-数据准备)
  - [Step3: 微调脚本](#step3-微调脚本)
    - [LoRA微调](#lora微调)
    - [全量参数微调](#全量参数微调)
  - [Step4: 加载微调模型](#step4-加载微调模型)
    - [LoRA微调](#lora微调-1)
    - [全量参数微调](#全量参数微调-1)
- [🍄 模型量化](#-模型量化)
- [🚀 部署加速](#-部署加速)
  - [TensorRT-LLM](#tensorrt-llm)
  - [vLLM](#vllm)
  - [JittorLLMs](#jittorllms)
  - [lmdeploy](#lmdeploy)
- [💪 外延能力](#-外延能力)
  - [LangChain](#langchain)
- [🥇 模型评测](#-模型评测)
  - [Llama4模型评测](#llama4模型评测)
  - [Llama2和Llama3对比评测](#llama2和llama3对比评测)
  - [Llama3模型评测](#llama3模型评测)
  - [Llama2模型评测](#llama2模型评测)
- [📖 学习中心](#-学习中心)
  - [官方文档](#官方文档)
  - [社区文档](#社区文档)
  - [Llama相关论文](#llama相关论文)
- [📌 其它](#-其它)
  - [🎉 致谢](#-致谢)
  - [🤔 问题反馈](#-问题反馈)


## 📌 Llama中文社区

### 🔥 社区介绍

欢迎来到Llama中文社区！Llama模型的开源无疑极大促进了大模型技术的发展，我们致力于构建一个开放平台，能够让所有的开发者与技术爱好者一起共创Llama开源生态。从大模型到小模型，从文本到多模态，从软件到硬件算法优化，我们期望开源能够带给全人类以AI普惠。在一个科技爆发的时代，加入Llama Family，与技术一同进步，与社区一同前行，一起迈向AGI！

<details>

#### 为什么选择Llama中文社区？
🚀 **高级工程师团队支持**：社区有一批专注为大家服务的NLP高级工程师，我们有着强大的技术支持和丰富的经验，为您提供专业的指导和帮助。

🎯 **中文优化**：我们致力于在Llama模型的中文处理方面进行优化，探索适用于中文的最佳实践，以提升其性能和适应性【支持Llama2、Llama3、Llama4】。

💡 **创新交流**：我们拥有一支富有创造力和经验的社区成员团队，定期组织线上活动、技术研讨和经验分享，促进成员间的创新交流。

🌐 **全球联结**：我们欢迎来自世界各地的开发者加入社区，构建一个开放、多元化的学习和交流平台。

🤝 **开放共享**：我们鼓励社区成员开源分享代码和模型，推动合作共赢，共同促进中文NLP技术的发展。

#### 社区活动
🗓️ **线上讲座**：邀请行业内专家进行线上讲座，分享Llama在中文NLP领域的最新技术和应用，探讨前沿研究成果。

💻 **项目展示**：成员可展示自己在Llama中文优化方面的项目成果，获得反馈和建议，促进项目协作。

📚 **学习资源**：社区维护丰富的学习资料库，包括教程、文档和论文解读，为成员提供全面的学习支持。

📝 **论文解读**：社区成员共同解读与Llama相关的最新研究论文，深入理解前沿算法和方法。

🎉 **主题活动**：定期举办各类主题活动，包括挑战赛、黑客马拉松和技术沙龙，让社区成员在轻松愉快的氛围中交流和学习。

🌟 **奖励计划**：我们设立奖励计划，对社区中积极参与、贡献优秀的成员给予荣誉和奖励，激励更多优秀人才的加入。

📈 **技术咨询**：我们提供技术咨询服务，解答您在Llama开发和优化过程中遇到的问题，助您快速攻克难关。

🚀 **项目合作**：鼓励成员间的项目合作，共同探索Llama在实际应用中的潜力，打造创新解决方案。


#### 立即加入我们！
📚 **愿景**：无论您是对Llama已有研究和应用经验的专业开发者，还是对Llama中文优化感兴趣并希望深入探索的新手，我们都热切期待您的加入。在Llama中文社区，您将有机会与行业内顶尖人才共同交流，携手推动中文NLP技术的进步，开创更加美好的技术未来！

🔗 **温馨提示**：本社区为专业技术交流平台，我们热切期望志同道合的开发者和研究者加入。请遵守社区准则，共同维护积极向上的学习氛围。感谢您的理解和支持！

</details>


### 🪵 社区资源
社区资源的丰富性是社区发展的重要保障，它涵盖了各种方面，其中包括但不限于以下四个方面：算力、数据、论坛和应用。在这些方面的积极发展与充分利用，将为社区成员提供更多的机会和支持，推动整个社区向着更加繁荣的方向发展。更多的内容请看[llama.family](https://llama.family/)

<details>

#### 💻 算力
- 提供低于市场价格的算力资源，可用于各类计算任务，如深度学习模型的训练、推理等。
- 为社区成员提供专属的在线推理服务，让用户可以快速有效地对模型进行推理操作。
- 提供一键在线微调服务，使用户可以方便地对模型进行微调，以适应不同的任务和数据。

#### 📊 数据
- 开放丰富的训练数据资源，覆盖多个领域和行业，为模型训练提供充足的数据支持。
- 提供高质量、多样化的数据集，以满足不同用户的需求，并支持数据共享和交流，促进数据资源的充分利用。

#### 💬 论坛
- 社区论坛为社区成员提供了一个在线交流和讨论技术问题的平台。
- 在论坛上，用户可以分享经验、提出问题、解答疑惑，促进技术交流和合作。
- 论坛还可以定期举办线上活动、研讨会等，增进社区成员之间的联系和了解。

#### 📱 应用
- 免费提供应用推广展示位，让开发者可以将他们的应用充分展示给社区成员。
- 提供推广的帮助，包括但不限于宣传推广、用户引导等服务，帮助应用获得更多的曝光和用户。
- 通过社区平台，为优秀的应用提供合作机会，促进应用开发者之间的合作和交流，共同推动应用的发展和壮大。

</details>


### 📢 最新动态

【最新】2025年04月05日：原生多模态MoE架构的[Llama 4](https://ai.meta.com/blog/llama-4-multimodal-intelligence/?utm_source=llama-home-latest-updates&utm_medium=llama-referral&utm_campaign=llama-utm&utm_offering=llama-aiblog&utm_product=llama)开源！最高达2T参数的Behemoth模型，以及Maverick、Scout。

【最新】2024年12月06日：[Llama 3.3](https://llama.meta.com/docs/overview)模型发布，更新70B Instruct模型。

【最新】2024年09月25日：[Llama 3.2](https://llama.meta.com/docs/overview)模型发布，核心主打1B、3B端侧小模型，以及11B、90B多模态输入模型！

【最新】2024年07月24日：开源最强[Llama 3.1](https://llama.meta.com/docs/overview)模型发布，包含8B、70B和405B！

【最新】2024年07月16日：[社区论坛](https://forum.llamafamily.cn/)上线，有大模型问题，就找Llama中文社区！

【最新】2024年05月15日：支持ollama运行Llama3-Chinese-8B-Instruct、Atom-7B-Chat，[详细使用方法](https://github.com/LlamaFamily/Llama-Chinese?tab=readme-ov-file#%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B-%E4%BD%BF%E7%94%A8ollama%E8%BF%90%E8%A1%8C)。

【最新】2024年04月23日：社区增加了llama3 8B中文微调模型[Llama3-Chinese-8B-Instruct](https://github.com/LlamaFamily/Llama-Chinese?tab=readme-ov-file#llama3%E4%B8%AD%E6%96%87%E5%BE%AE%E8%B0%83%E6%A8%A1%E5%9E%8B)以及对应的[免费API调用](https://llama.family/docs/chat-completion-v1)。
 
【最新】2024年04月19日：社区增加了llama3 8B、llama3 70B[在线体验链接](https://llama.family/chat/#/)。

【最新】2024年04月14日：社区更新了四个专家角色：心理咨询师、羊驼夸夸 、律师、医生。链接：[角色role](https://llama.family/tools/#/agent)。

【最新】2024年04月10日：Atom-7B-Chat 模型回答内容相较之前更为丰富、增强了模型的指令遵循能力和回答稳定性、优化了ppo的奖励模型。下载链接[modelscope](https://modelscope.cn/models/FlagAlpha/Atom-7B-Chat)、[Huggingface](https://huggingface.co/FlagAlpha/Atom-7B-Chat)。

【最新】2024年04月01日：社区上线了Llama中文[应用平台](https://llama.family/store)；同时如果你有优秀的的应用需要推广可以填写[申请表](https://atomecho.feishu.cn/share/base/form/shrcnFqpN71OmBoXDCT6y0TQgIc)。

【最新】2024年03月08日：开放了免费API供大家使用，包含（Atom-1B,7B,13B 3种中文大模型）[API使用链接](https://llama.family/docs/chat-completion-v1)

【最新】2024年04月14日：社区更新了四个专家角色：心理咨询师、羊驼夸夸 、律师、医生。链接：[角色role](https://llama.family/tools/#/agent)。

【最新】2024年04月10日：Atom-7B-Chat 模型回答内容相较之前更为丰富、增强了模型的指令遵循能力和回答稳定性、优化了ppo的奖励模型。下载链接[modelscope](https://modelscope.cn/models/FlagAlpha/Atom-7B-Chat)、[Huggingface](https://huggingface.co/FlagAlpha/Atom-7B-Chat)。

【最新】2024年04月01日：社区上线了Llama中文[应用平台](https://llama.family/store)；同时如果你有优秀的的应用需要推广可以填写[申请表](https://atomecho.feishu.cn/share/base/form/shrcnFqpN71OmBoXDCT6y0TQgIc)。

【最新】2024年03月28日：[社区免费公开课](https://mp.weixin.qq.com/s/CsturoU1pOX11CqVnZgu2A)。

【最新】2024年03月08日：开放了免费API供大家使用，包含（Atom-1B,7B,13B 3种中文大模型）[API使用链接](https://llama.family/docs/chat-completion-v1)

【最新】2023年10月8日：新增清华大学JittorLLMs的推理加速功能[JittorLLMs](#jittorllms)！

<details>

- 2023年9月12日：更新预训练版本[Atom-7B](https://huggingface.co/FlagAlpha/Atom-7B)和对话版本[Atom-7B-Chat](https://huggingface.co/FlagAlpha/Atom-7B-Chat)模型参数，最新的中文预训练数据量为2.7TB token，训练进程见[llama.family](https://llama.family/)！

- 2023年9月2日：新增模型[预训练代码](#-模型预训练)和[全量参数微调代码](#-模型微调)！
  
- 2023年8月28日：发布基于Llama2进行中文预训练的开源大模型[Atom-7B](https://huggingface.co/FlagAlpha/Atom-7B)，并将持续更新，详情参考[社区公众号文章](https://mp.weixin.qq.com/s/Bdx0JTVh1kgPn5ydYxIkEw)！

- 2023年8月26日：提供[FastAPI](#fastapi接口搭建)接口搭建脚本！

- 2023年8月26日：提供将Meta原始模型参数转换为兼容Hugging Face的[格式转化脚本](https://github.com/LlamaFamily/Llama-Chinese/blob/main/scripts/convert2hf/README.md)！

- 2023年8月26日：新增[Code Llama](#-代码模型)模型！

- 2023年8月15日：新增[PEFT加载微调模型参数](#加载微调模型)的代码示例！

- 2023年8月14日：[大模型数据共享训练平台](https://llama.family)上线，没有算力也能参与大模型训练，社区每位成员贡献的数据都将决定模型能力的未来走向！

- 2023年8月3日：新增FasterTransformer和vLLM的GPU[推理加速](#-推理加速)支持！

- 2023年7月31日：【重磅】国内首个真正意义上的Llama2中文大模型发布！详情参见[社区公众号文章](https://mp.weixin.qq.com/s/lExUU7z_MvgJ7tzQPF8tUQ)

- 2023年7月28日：通过[Docker部署](#docker部署问答接口)问答接口！

- 2023年7月27日：新增[LangChain](#langchain)支持！

- 2023年7月26日：新增Llama2-13B中文微调参数的[4bit量化压缩版本](#-模型量化)！

- 2023年7月25日：社区微信公众号“Llama中文社区”欢迎大家关注，获取最新分享和动态！

- 2023年7月24日：[FlagAlpha](https://huggingface.co/FlagAlpha)新增Llama2-13B中文微调参数！

- 2023年7月24日：[llama.family](https://llama.family/)新增Llama2-70B在线体验！

- 2023年7月23日：Llama2中文微调参数发布至Hugging Face仓库[FlagAlpha](https://huggingface.co/FlagAlpha)！

- 2023年7月22日：Llama2在线体验链接[llama.family](https://llama.family/)上线，同时包含Meta原版和中文微调版本！

- 2023年7月21日：评测了Meta原始版Llama2 Chat模型的[中文问答能力](#-模型评测)！

- 2023年7月21日：新增Llama2模型的Hugging Face版本国内下载地址！

- 2023年7月20日：新增[飞书知识库文档](https://chinesellama.feishu.cn/wiki/space/7257824476874768388?ccm_open_type=lark_wiki_spaceLink)，欢迎大家一起共建！

- 2023年7月20日：国内Llama2最新下载地址上线！

- 2023年7月19日：正式启动Llama2模型的中文预训练，关注我们获取实时动态！

- 2023年7月19日：Llama2国内下载地址正在启动，敬请期待！

- 2023年7月19日：开启Llama2中文社区，欢迎大家加入！

</details>


### 🤗 模型发布

#### 中文预训练模型Atom

**原子大模型Atom**由Llama中文社区和原子回声联合打造。

|  类别  | 模型名称        | 🤗模型加载名称                  | 下载地址                                                     |
| --------------- | --------------- | ------------------------------ | ------------------------------------------------------------ |
|  预训练  | Atom-7B  | FlagAlpha/Atom-7B  | [HuggingFace](https://huggingface.co/FlagAlpha/Atom-7B) \| [ModelScope](https://modelscope.cn/models/FlagAlpha/Atom-7B) \| [WiseModel](https://wisemodel.cn/models/FlagAlpha/Atom-7B) |
|  Chat  | Atom-7B-Chat  | FlagAlpha/Atom-7B-Chat  | [HuggingFace](https://huggingface.co/FlagAlpha/Atom-7B-Chat) \| [ModelScope](https://modelscope.cn/models/FlagAlpha/Atom-7B-Chat) \| [WiseModel](https://wisemodel.cn/models/FlagAlpha/Atom-7B-Chat)|

Atom系列模型包含Atom-13B、Atom-7B和Atom-1B，基于Llama2做了中文能力的持续优化。Atom-7B和Atom-7B-Chat目前已完全开源，支持商用，可在[Hugging Face](https://huggingface.co/FlagAlpha)仓库获取模型，详情见[Atom-7B下载](#基于llama2的中文预训练模型atom)。Atom大模型针对中文做了以下优化：

- 大规模的中文数据预训练

    原子大模型Atom在Llama2的基础上，采用大规模的中文数据进行持续预训练，包含百科、书籍、博客、新闻、公告、小说、金融数据、法律数据、医疗数据、代码数据、专业论文数据、中文自然语言处理竞赛数据集等。同时对庞大的数据进行了过滤、打分、去重，筛选出超过1T token的高质量中文数据，持续不断加入训练迭代中。

- 更高效的中文词表

    为了提高中文文本处理的效率，我们针对Llama2模型的词表进行了深度优化。首先，我们基于数百G的中文文本，在该模型词表的基础上扩展词库至65,000个单词。经过测试，我们的改进使得中文编码/解码速度提高了约350％。此外，我们还扩大了中文字符集的覆盖范围，包括所有emoji符号😊。这使得生成带有表情符号的文章更加高效。

- 自适应上下文扩展

    Atom大模型默认支持4K上下文，利用位置插值PI和Neural Tangent Kernel （NTK）方法，经过微调可以将上下文长度扩增到32K。

📝 中文数据详情如下：

| 类型                                                       | 描述                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------ |
| 网络数据                                                   | 互联网上公开的网络数据，挑选出去重后的高质量中文数据，涉及到百科、书籍、博客、新闻、公告、小说等高质量长文本数据。 |
| [Wikipedia](https://github.com/goldsmith/Wikipedia)        | 中文Wikipedia的数据                                          |
| [悟道](https://github.com/BAAI-WuDao/Model)                | 中文悟道开源的200G数据                                       |
| [Clue](https://github.com/CLUEbenchmark/CLUEDatasetSearch) | Clue开放的中文预训练数据，进行清洗后的高质量中文长文本数据   |
| 竞赛数据集                                                 | 近年来中文自然语言处理多任务竞赛数据集，约150个              |
| [MNBVC](https://github.com/esbatmop/MNBVC)                 | MNBVC 中清洗出来的部分数据集  |

社区提供预训练版本Atom-7B和基于Atom-7B进行对话微调的模型参数供开放下载，关于模型的进展详见社区官网[llama.family](https://llama.family)。


#### Llama4官方模型

|  类别  | 模型名称   | 🤗模型加载名称             | 下载地址                                                     |
|  ----------  | ---------- | ------------------------- | --------------------- |
|  预训练  | Llama-4-Scout-17B-16E  | meta-llama/Llama-4-Scout-17B-16E  | [HuggingFace](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E) |
|  对话模型  | Llama-4-Scout-17B-16E-Instruct | meta-llama/Llama-4-Scout-17B-16E-Instruct | [HuggingFace](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct) |
|  预训练  | Llama-4-Maverick-17B-128E  | meta-llama/Llama-4-Maverick-17B-128E  | [HuggingFace](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E) |
|  对话模型  | Llama-4-Maverick-17B-128E-Instruct  | meta-llama/Llama-4-Maverick-17B-128E-Instruct  | [HuggingFace](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct) |


#### Llama3官方模型
注意：仅保留同等参数量级模型的最新版本。

|  类别  | 模型名称   | 🤗模型加载名称             | 下载地址                                                     |
|  ----------  | ---------- | ------------------------- | --------------------- |
|  预训练  | Llama-3.2-1B  | meta-llama/Llama-3.2-1B  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-1B) |
|  对话模型  | Llama-3.2-1B-Instruct | meta-llama/Llama-3.2-1B-Instruct | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct) |
|  预训练  | Llama-3.2-3B  | meta-llama/Llama-3.2-3B  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-3B) |
|  对话模型  | Llama-3.2-3B-Instruct | meta-llama/Llama-3.2-3B-Instruct | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct) |
|  预训练  | Llama-3.1-8B  | meta-llama/Llama-3.1-8B  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.1-8B) |
|  对话模型  | Llama-3.1-8B-Instruct | meta-llama/Llama-3.1-8B-Instruct | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) |
|  预训练  | Llama-3.1-70B  | meta-llama/Llama-3.1-70B  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.1-70B)|
|  对话模型  | Llama-3.3-70B-Instruct  | meta-llama/Llama-3.3-70B-Instruct  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) |
|  预训练  | Llama-3.1-405B  | meta-llama/Llama-3.1-405B  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.1-405B)|
|  对话模型  | Llama-3.1-405B-Instruct  | meta-llama/Llama-3.1-405B-Instruct  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct)|
|  多模态预训练  | Llama-3.2-11B-Vision  | meta-llama/Llama-3.2-11B-Vision  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision)|
|  多模态对话模型  | Llama-3.2-11B-Vision-Instruct  | meta-llama/Llama-3.2-11B-Vision-Instruct  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct)|
|  多模态预训练  | Llama-3.2-90B-Vision  | meta-llama/Llama-3.2-90B-Vision  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-90B-Vision)|
|  多模态对话模型  | Llama-3.2-90B-Vision-Instruct  | meta-llama/Llama-3.2-90B-Vision-Instruct  | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-90B-Vision-Instruct)|


#### Llama3中文微调模型

|  类别  | 模型名称   | 🤗模型加载名称             | 下载地址                                                     |
|  ----------  | ---------- | ------------------------- | --------------------- |
|  对话模型  | Llama3-Chinese-8B-Instruct  | FlagAlpha/Llama3-Chinese-8B-Instruct  | [HuggingFace](https://huggingface.co/FlagAlpha/Llama3-Chinese-8B-Instruct) \| [modelscope](https://modelscope.cn/models/FlagAlpha/Llama3-Chinese-8B-Instruct/summary) \| [wisemodel](https://wisemodel.cn/models/FlagAlpha/Llama3-Chinese-8B-Instruct/file) |


#### Llama2官方模型

<!-- <details> -->

|  类别  | 模型名称   | 🤗模型加载名称             | 下载地址                                                     |
|  ----------  | ---------- | ------------------------- | --------------------- |
|  预训练  | Llama2-7B  | meta-llama/Llama-2-7b-hf  | [HuggingFace](https://huggingface.co/meta-llama/Llama-2-7b-hf) \| [迅雷网盘](https://pan.xunlei.com/s/VN_t0dUikZqOwt-5DZWHuMvqA1?pwd=66ep) |
|  预训练  | Llama2-13B | meta-llama/Llama-2-13b-hf | [HuggingFace](https://huggingface.co/meta-llama/Llama-2-13b-hf) \| [迅雷网盘](https://pan.xunlei.com/s/VN_yT_9G8xNOz0SDWQ7Mb_GZA1?pwd=yvgf) |
|  预训练  | Llama2-70B | meta-llama/Llama-2-70b-hf | [HuggingFace](https://huggingface.co/meta-llama/Llama-2-70b-hf) |
|  Chat  | Llama2-7B-Chat  | meta-llama/Llama-2-7b-chat-hf  | [HuggingFace](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf) \| [迅雷网盘](https://pan.xunlei.com/s/VN_oaV4BpKFgKLto4KgOhBcaA1?pwd=ufir) |
|  Chat  | Llama2-13B-Chat | meta-llama/Llama-2-13b-chat-hf | [HuggingFace](https://huggingface.co/meta-llama/Llama-2-13b-chat-hf) \| [迅雷网盘](https://pan.xunlei.com/s/VN_yA-9G34NGL9B79b3OQZZGA1?pwd=xqrg) |
|  Chat  | Llama2-70B-Chat | meta-llama/Llama-2-70b-chat-hf | [HuggingFace](https://huggingface.co/meta-llama/Llama-2-70b-chat-hf) \| [迅雷网盘](https://pan.xunlei.com/s/VNa_vCGzCy3h3N7oeFXs2W1hA1?pwd=uhxh#) |
| Code  | CodeLlama-7b    |   meta-llama/Llama-2-70b-chat-hf              | [迅雷网盘](https://pan.baidu.com/s/1cIPzdNywWLvQI7_2QanOEQ?pwd=zfwi) |
| Code  | CodeLlama-7b-Python    |   meta-llama/Llama-2-70b-chat-hf              | [迅雷网盘](https://pan.baidu.com/s/1liY8klGoDagYbpw-g-oFag?pwd=i952) |
| Code  | CodeLlama-7b-Instruct    |   meta-llama/Llama-2-70b-chat-hf              | [迅雷网盘](https://pan.baidu.com/s/108o9_DT2E_vfSGtOnDCQVw?pwd=zkt9) |
| Code  | CodeLlama-13b    |   meta-llama/Llama-2-70b-chat-hf              | [迅雷网盘](https://pan.baidu.com/s/1lLaeHv0XEBv0iiZzI1dpnw?pwd=qn99) |
| Code  | CodeLlama-13b-Python    |   meta-llama/Llama-2-70b-chat-hf              | [迅雷网盘](https://pan.baidu.com/s/1OLVfvZS_oqL3oqMKwsI87w?pwd=a78k) |
| Code  | CodeLlama-13b-Instruct    |   meta-llama/Llama-2-70b-chat-hf              | [迅雷网盘](https://pan.baidu.com/s/1HyxJl4w8wElgkZRh2ATrXQ?pwd=seg6) |
| Code  | CodeLlama-34b    |   meta-llama/Llama-2-70b-chat-hf              | [迅雷网盘](https://pan.baidu.com/s/1vEw0pFgIkctPUN4_5_6pIQ?pwd=q8eu) |

Meta官方在2023年8月24日发布了Code Llama，基于代码数据对Llama2进行了微调，提供三个不同功能的版本：基础模型（Code Llama）、Python专用模型（Code Llama - Python）和指令跟随模型（Code Llama - Instruct），包含7B、13B、34B三种不同参数规模。不同模型能力区别如下表所示：

|  模型类别          |        模型名称         | 代码续写 | 代码填充 | 指令编程 |
|-----------------------|------------------------|------|------|------|
| Code Llama            | CodeLlama-7b           | ✅    | ✅    | ❌    |
|                       | CodeLlama-13b          | ✅    | ✅    | ❌    |
|                       | CodeLlama-34b          | ✅    | ❌    | ❌    |
| Code Llama - Python   | CodeLlama-7b-Python    | ✅    | ❌    | ❌    |
|                       | CodeLlama-13b-Python   | ✅    | ❌    | ❌    |
|                       | CodeLlama-34b-Python   | ✅    | ❌    | ❌    |
| Code Llama - Instruct | CodeLlama-7b-Instruct  | ❌    | ✅    | ✅    |
|                       | CodeLlama-13b-Instruct | ❌    | ✅    | ✅    |
|                       | CodeLlama-34b-Instruct | ❌    | ❌    | ✅    |

关于Code Llama的详细信息可以参考官方Github仓库[codellama](https://github.com/facebookresearch/codellama)。

<!-- </details> -->


#### Llama2中文微调模型

我们基于中文指令数据集对Llama2-Chat模型进行了微调，使得Llama2模型有着更强的中文对话能力。LoRA参数以及与基础模型合并的参数均已上传至[Hugging Face](https://huggingface.co/FlagAlpha)，目前包含7B和13B的模型。

|  类别  | 模型名称   | 🤗模型加载名称             | 基础模型版本 |    下载地址                                                     |
|  ----------  | ---------- | ------------- |  ----------------- | ------------------- |
|  合并参数 | Llama2-Chinese-7b-Chat | FlagAlpha/Llama2-Chinese-7b-Chat  |    meta-llama/Llama-2-7b-chat-hf       |[HuggingFace](https://huggingface.co/FlagAlpha/Llama2-Chinese-7b-Chat)  |
|  合并参数 | Llama2-Chinese-13b-Chat | FlagAlpha/Llama2-Chinese-13b-Chat|     meta-llama/Llama-2-13b-chat-hf     |[HuggingFace](https://huggingface.co/FlagAlpha/Llama2-Chinese-13b-Chat) |
|  LoRA参数 | Llama2-Chinese-7b-Chat-LoRA  | FlagAlpha/Llama2-Chinese-7b-Chat-LoRA  |     meta-llama/Llama-2-7b-chat-hf      |[HuggingFace](https://huggingface.co/FlagAlpha/Llama2-Chinese-7b-Chat-LoRA) |
|  LoRA参数 | Llama2-Chinese-13b-Chat-LoRA | FlagAlpha/Llama2-Chinese-13b-Chat-LoRA |     meta-llama/Llama-2-13b-chat-hf     |[HuggingFace](https://huggingface.co/FlagAlpha/Llama2-Chinese-13b-Chat-LoRA) |


## 📌 如何使用Llama模型


你可以选择下面的快速上手的任一种方式，开始使用 Llama 系列模型。推荐使用[中文预训练对话模型](#llama2中文预训练模型atom-7b)进行使用，对中文的效果支持更好。


### 快速上手-使用Anaconda

第 0 步：前提条件
- 确保安装了 Python 3.10 以上版本。

第 1 步：准备环境

如需设置环境，安装所需要的软件包，运行下面的命令。
```bash
git clone https://github.com/LlamaFamily/Llama-Chinese.git
cd Llama-Chinese
pip install -r requirements.txt
```

第 2 步：下载模型

你可以从以下来源下载Atom-7B-Chat模型。
- [HuggingFace](https://huggingface.co/FlagAlpha)
- [ModelScope](https://modelscope.cn/organization/FlagAlpha)
- [WiseModel](https://wisemodel.cn/models/FlagAlpha/Atom-7B-Chat)

第 3 步：进行推理

使用Atom-7B-Chat模型进行推理
创建一个名为 quick_start.py 的文件，并将以下内容复制到该文件中。
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
device_map = "cuda:0" if torch.cuda.is_available() else "auto"
model = AutoModelForCausalLM.from_pretrained('FlagAlpha/Atom-7B-Chat',device_map=device_map,torch_dtype=torch.float16,load_in_8bit=True,trust_remote_code=True,use_flash_attention_2=True)
model =model.eval()
tokenizer = AutoTokenizer.from_pretrained('FlagAlpha/Atom-7B-Chat',use_fast=False)
tokenizer.pad_token = tokenizer.eos_token
input_ids = tokenizer(['<s>Human: 介绍一下中国\n</s><s>Assistant: '], return_tensors="pt",add_special_tokens=False).input_ids
if torch.cuda.is_available():
  input_ids = input_ids.to('cuda')
generate_input = {
    "input_ids":input_ids,
    "max_new_tokens":512,
    "do_sample":True,
    "top_k":50,
    "top_p":0.95,
    "temperature":0.3,
    "repetition_penalty":1.3,
    "eos_token_id":tokenizer.eos_token_id,
    "bos_token_id":tokenizer.bos_token_id,
    "pad_token_id":tokenizer.pad_token_id
}
generate_ids  = model.generate(**generate_input)
text = tokenizer.decode(generate_ids[0])
print(text)
```

运行 quick_start.py 代码。
```bash
python quick_start.py
```

### 快速上手-使用Docker

详情参见：[Docker部署](https://github.com/LlamaFamily/Llama-Chinese/blob/main/docs/chat_gradio_guide.md)

第 1 步：准备docker镜像，通过docker容器启动[chat_gradio.py](../examples/chat_gradio.py)
```bash
git clone https://github.com/LlamaFamily/Llama-Chinese.git

cd Llama-Chinese

docker build -f docker/Dockerfile -t flagalpha/llama2-chinese:gradio .
```

第 2 步：通过docker-compose启动chat_gradio
```bash
cd Llama-Chinese/docker
docker-compose up -d --build
```

### 快速上手-使用llama.cpp
详情参见：[使用llama.cpp](https://github.com/LlamaFamily/Llama-Chinese/blob/main/inference-speed/CPU/ggml/README.md)

### 快速上手-使用gradio
基于gradio搭建的问答界面，实现了流式的输出，将下面代码复制到控制台运行，以下代码以Atom-7B-Chat模型为例，不同模型只需修改一下面的model_name_or_path对应的模型名称就好了😊
```
python examples/chat_gradio.py --model_name_or_path FlagAlpha/Atom-7B-Chat
```

### 快速上手-构建API服务
使用FastChat构建和OpenAI一致的推理服务接口。

<!-- <details> -->
第 0 步：前提条件

安装fastchat
```bash
pip3 install "fschat[model_worker,webui]"
```
第 1 步：启动Restful API

开启三个控制台分别执行下面的三个命令
- 首先启动controler
```bash
python3 -m fastchat.serve.controller \
--host localhost \
--port 21001
```

- 启动模型
```bash
CUDA_VISIBLE_DEVICES="0" python3 -m fastchat.serve.model_worker --model-path /path/Atom-7B-Chat \
--host localhost \
--port 21002 \
--worker-address "http://localhost:21002" \
--limit-worker-concurrency 5 \
--stream-interval 2 \