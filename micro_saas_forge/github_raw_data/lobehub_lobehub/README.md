<div align="center"><a name="readme-top"></a>

[![][image-banner]][vercel-link]

# LobeHub

LobeHub is the ultimate space for work and life: <br/>
to find, build, and collaborate with agent teammates that grow with you.<br/>
We’re building the world’s largest human–agent co-evolving network.

**English** · [简体中文](./README.zh-CN.md) · [Official Site][official-site] · [Changelog][changelog] · [Documents][docs] · [Blog][blog] · [Feedback][github-issues-link]

<!-- SHIELD GROUP -->

[![][github-release-shield]][github-release-link]
[![][docker-release-shield]][docker-release-link]
[![][vercel-shield]][vercel-link]
[![][discord-shield]][discord-link]<br/>
[![][codecov-shield]][codecov-link]
[![][github-action-test-shield]][github-action-test-link]
[![][github-action-release-shield]][github-action-release-link]
[![][github-releasedate-shield]][github-releasedate-link]<br/>
[![][github-contributors-shield]][github-contributors-link]
[![][github-forks-shield]][github-forks-link]
[![][github-stars-shield]][github-stars-link]
[![][github-issues-shield]][github-issues-link]
[![][github-license-shield]][github-license-link]<br>
[![][sponsor-shield]][sponsor-link]

**Share LobeHub Repository**

[![][share-x-shield]][share-x-link]
[![][share-telegram-shield]][share-telegram-link]
[![][share-whatsapp-shield]][share-whatsapp-link]
[![][share-reddit-shield]][share-reddit-link]
[![][share-weibo-shield]][share-weibo-link]
[![][share-mastodon-shield]][share-mastodon-link]
[![][share-linkedin-shield]][share-linkedin-link]

<sup>Agent teammates that grow with you</sup>

[![][github-trending-shield]][github-trending-url]

[![](https://vercel.com/oss/program-badge.svg)](https://vercel.com/oss)

</div>

<details>
<summary><kbd>Table of contents</kbd></summary>

#### TOC

- [👋🏻 Getting Started & Join Our Community](#-getting-started--join-our-community)
- [✨ Features](#-features)
  - [Create: Agents as the Unit of Work](#create-agents-as-the-unit-of-work)
  - [Collaborate: Scale New Forms of Collaboration Networks](#collaborate-scale-new-forms-of-collaboration-networks)
  - [Evolve: Co-evolution of Humans and Agents](#evolve-co-evolution-of-humans-and-agents)
  - [MCP Plugin One-Click Installation](#mcp-plugin-one-click-installation)
  - [MCP Marketplace](#mcp-marketplace)
  - [Desktop App](#desktop-app)
  - [Smart Internet Search](#smart-internet-search)
  - [Chain of Thought](#chain-of-thought)
  - [Branching Conversations](#branching-conversations)
  - [Artifacts Support](#artifacts-support)
  - [File Upload /Knowledge Base](#file-upload-knowledge-base)
  - [Multi-Model Service Provider Support](#multi-model-service-provider-support)
  - [Local Large Language Model (LLM) Support](#local-large-language-model-llm-support)
  - [Model Visual Recognition](#model-visual-recognition)
  - [TTS & STT Voice Conversation](#tts--stt-voice-conversation)
  - [Text to Image Generation](#text-to-image-generation)
  - [Plugin System (Function Calling)](#plugin-system-function-calling)
  - [Agent Market (GPTs)](#agent-market-gpts)
  - [Support Local / Remote Database](#support-local--remote-database)
  - [Support Multi-User Management](#support-multi-user-management)
  - [Progressive Web App (PWA)](#progressive-web-app-pwa)
  - [Mobile Device Adaptation](#mobile-device-adaptation)
  - [Custom Themes](#custom-themes)
  - [`*` What's more](#-whats-more)
- [🛳 Self Hosting](#-self-hosting)
  - [`A` Deploying with Vercel, Zeabur , Sealos or Alibaba Cloud](#a-deploying-with-vercel-zeabur--sealos-or-alibaba-cloud)
  - [`B` Deploying with Docker](#b-deploying-with-docker)
  - [Environment Variable](#environment-variable)
- [📦 Ecosystem](#-ecosystem)
- [🧩 Plugins](#-plugins)
- [⌨️ Local Development](#️-local-development)
- [🤝 Contributing](#-contributing)
- [❤️ Sponsor](#️-sponsor)
- [🔗 More Products](#-more-products)

####

<br/>

</details>

<br/>

<https://github.com/user-attachments/assets/6710ad97-03d0-4175-bd75-adff9b55eca2>

## 👋🏻 Getting Started & Join Our Community

We are a group of e/acc design-engineers, hoping to provide modern design components and tools for AIGC.
By adopting the Bootstrapping approach, we aim to provide developers and users with a more open, transparent, and user-friendly product ecosystem.

Whether for users or professional developers, LobeHub will be your AI Agent playground. Please be aware that LobeHub is currently under active development, and feedback is welcome for any [issues][issues-link] encountered.

| [![](https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1065874&theme=light&t=1769347414733)](https://www.producthunt.com/products/lobehub?embed=true&utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-lobehub) | We are live on Product Hunt! We are thrilled to bring LobeHub to the world. If you believe in a future where humans and agents co-evolve, please support our journey. |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![][discord-shield-badge]][discord-link]                                                                                                                                                                                                         | Join our Discord community! This is where you can connect with developers and other enthusiastic users of LobeHub.                                                    |

> \[!IMPORTANT]
>
> **Star Us**, You will receive all release notifications from GitHub without any delay \~ ⭐️

[![][image-star]][github-stars-link]

<details>
  <summary><kbd>Star History</kbd></summary>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=lobehub%2Flobe-chat&theme=dark&type=Date">
    <img width="100%" src="https://api.star-history.com/svg?repos=lobehub%2Flobe-chat&type=Date">
  </picture>
</details>

## ✨ Features

Today’s agents are one-off, task-driven tools. They lack context, live in isolation, and require manual hand-offs between different windows and models. While some maintain memory, it is often global, shallow, and impersonal. In this mode, users are forced to toggle between fragmented conversations, making it difficult to form structured productivity.

**LobeHub changes everything.**

LobeHub is a work-and-lifestyle space to find, build, and collaborate with agent teammates that grow with you. In LobeHub, we treat **Agents as the unit of work**, providing an infrastructure where humans and agents co-evolve.

![](https://hub-apac-1.lobeobjects.space/blog/assets/2204cde2228fb3f583f3f2c090bc49fb.webp)

### Create: Agents as the Unit of Work

Building a personalized AI team starts with the **Agent Builder**. You can describe what you need once, and the agent setup starts right away, applying auto-configurations so you can use it instantly.

- **Unified Intelligence**: Seamlessly access any model and any modality—all under your control.
- **10,000+ Skills**: Connect your agents to the skills you use every day with a library of over 10,000 tools and MCP-compatible plugins.

[![][back-to-top]](#readme-top)

<div align="right">

[![][back-to-top]](#readme-top)

</div>

![](https://hub-apac-1.lobeobjects.space/blog/assets/771ff3d30b9ef93e65e55021cc43d356.webp)

### Collaborate: Scale New Forms of Collaboration Networks

LobeHub introduces **Agent Groups**, allowing you to work with agents like real teammates. The system assembles the right agents for the task, enabling parallel collaboration and iterative improvement.

- **Pages**: Write and refine content with multiple agents in one place with a shared context.
- **Schedule**: Schedule runs and let agents do the work at the right time, even while you are away.
- **Project**: Organize work by project to keep everything structured and easy to track.
- **Workspace**: A shared space for teams to collaborate with agents, ensuring clear ownership and visibility across the organization.

[![][back-to-top]](#readme-top)

<div align="right">

[![][back-to-top]](#readme-top)

</div>

![](https://hub-apac-1.lobeobjects.space/blog/assets/fe98eae9fcb6acc47c8e1fb69bdb4b50.webp)

### Evolve: Co-evolution of Humans and Agents

The best AI is one that understands you deeply. LobeHub features **Personal Memory** that builds a clear understanding of your needs.

- **Continual Learning**: Your agents learn from how you work, adapting their behavior to act at the right moment.
- **White-Box Memory**: We believe in transparency. Your agents use structured, editable memory, giving you full control over what they remember.

<div align="right">

[![][back-to-top]](#readme-top)

</div>

<details>
<summary>More Features</summary>

![][image-feat-mcp]

### MCP Plugin One-Click Installation

**Seamlessly Connect Your AI to the World**

Unlock the full potential of your AI by enabling smooth, secure, and dynamic interactions with external tools, data sources, and services. LobeHub's MCP (Model Context Protocol) plugin system breaks down the barriers between your AI and the digital ecosystem, allowing for unprecedented connectivity and functionality.

Transform your conversations into powerful workflows by connecting to databases, APIs, file systems, and more. Experience the freedom of AI that truly understands and interacts with your world.

[![][back-to-top]](#readme-top)

![][image-feat-mcp-market]

### MCP Marketplace

**Discover, Connect, Extend**

Browse a growing library of MCP plugins to expand your AI's capabilities and streamline your workflows effortlessly. Visit [lobehub.com/mcp](https://lobehub.com/mcp) to explore the MCP Marketplace, which offers a curated collection of integrations that enhance your AI's ability to work with various tools and services.

From productivity tools to development environments, discover new ways to extend your AI's reach and effectiveness. Connect with the community and find the perfect plugins for your specific needs.

[![][back-to-top]](#readme-top)

![][image-feat-desktop]

### Desktop App

**Peak Performance, Zero Distractions**

Get the full LobeHub experience without browser limitations—comprehensive, focused, and always ready to go. Our desktop application provides a dedicated environment for your AI interactions, ensuring optimal performance and minimal distractions.

Experience faster response times, better resource management, and a more stable connection to your AI assistant. The desktop app is designed for users who demand the best performance from their AI tools.

[![][back-to-top]](#readme-top)

![][image-feat-web-search]

### Smart Internet Search

**Online Knowledge On Demand**

With real-time internet access, your AI keeps up with the world—news, data, trends, and more. Stay informed and get the most current information available, enabling your AI to provide accurate and up-to-date responses.

Access live information, verify facts, and explore current events without leaving your conversation. Your AI becomes a gateway to the world's knowledge, always current and comprehensive.

[![][back-to-top]](#readme-top)

[![][image-feat-cot]][docs-feat-cot]

### [Chain of Thought][docs-feat-cot]

Experience AI reasoning like never before. Watch as complex problems unfold step by step through our innovative Chain of Thought (CoT) visualization. This breakthrough feature provides unprecedented transparency into AI's decision-making process, allowing you to observe how conclusions are reached in real-time.

By breaking down complex reasoning into clear, logical steps, you can better understand and validate the AI's problem-solving approach. Whether you're debugging, learning, or simply curious about AI reasoning, CoT visualization transforms abstract thinking into an engaging, interactive experience.

[![][back-to-top]](#readme-top)

[![][image-feat-branch]][docs-feat-branch]

### [Branching Conversations][docs-feat-branch]

Introducing a more natural and flexible way to chat with AI. With Branch Conversations, your discussions can flow in multiple directions, just like human conversations do. Create new conversation branches from any message, giving you the freedom to explore different paths while preserving the original context.

Choose between two powerful modes:

- **Continuation Mode:** Seamlessly extend your current discussion while maintaining valuable context
- **Standalone Mode:** Start fresh with a new topic based on any previous message

This groundbreaking feature transforms linear conversations into dynamic, tree-like structures, enabling deeper exploration of ideas and more productive interactions.

[![][back-to-top]](#readme-top)

[![][image-feat-artifacts]][docs-feat-artifacts]

### [Artifacts Support][docs-feat-artifacts]

Experience the power of Claude Artifacts, now integrated into LobeHub. This revolutionary feature expands the boundaries of AI-human interaction, enabling real-time creation and visualization of diverse content formats.

Create and visualize with unprecedented flexibility:

- Generate and display dynamic SVG graphics
- Build and render interactive HTML pages in real-time
- Produce professional documents in multiple formats

[![][back-to-top]](#readme-top)

[![][image-feat-knowledgebase]][docs-feat-knowledgebase]

### [File Upload /Knowledge Base][docs-feat-knowledgebase]

LobeHub supports file upload and knowledge base functionality. You can upload various types of files including documents, images, audio, and video, as well as create knowledge bases, making it convenient for users to manage and search for files. Additionally, you can utilize files and knowledge base features during conversations, enabling a richer dialogue experience.

<https://github.com/user-attachments/assets/faa8cf67-e743-4590-8bf6-ebf6ccc34175>

> \[!TIP]
>
> Learn more on [📘 LobeHub Knowledge Base Launch — From Now On, Every Step Counts](https://lobehub.com/blog/knowledge-base)

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-privoder]][docs-feat-provider]

### [Multi-Model Service Provider Support][docs-feat-provider]

In the continuous development of LobeHub, we deeply understand the importance of diversity in model service providers for meeting the needs of the community when providing AI conversation services. Therefore, we have expanded our support to multiple model service providers, rather than being limited to a single one, in order to offer users a more diverse and rich selection of conversations.

In this way, LobeHub can more flexibly adapt to the needs of different users, while also providing developers with a wider range of choices.

#### Supported Model Service Providers

We have implemented support for the following model service providers:

<!-- PROVIDER LIST -->

<details><summary><kbd>See more providers (+-10)</kbd></summary>

</details>

> 📊 Total providers: [<kbd>**0**</kbd>](https://lobechat.com/discover/providers)

 <!-- PROVIDER LIST -->

At the same time, we are also planning to support more model service providers. If you would like LobeHub to support your favorite service provider, feel free to join our [💬 community discussion](https://github.com/lobehub/lobe-chat/discussions/1284).

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-local]][docs-feat-local]

### [Local Large Language Model (LLM) Support][docs-feat-local]

To meet the specific needs of users, LobeHub also supports the use of local models based on [Ollama](https://ollama.ai), allowing users to flexibly use their own or third-party models.

> \[!TIP]
>
> Learn more about [📘 Using Ollama in LobeHub][docs-usage-ollama] by checking it out.

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-vision]][docs-feat-vision]

### [Model Visual Recognition][docs-feat-vision]

LobeHub now supports OpenAI's latest [`gpt-4-vision`](https://platform.openai.com/docs/guides/vision) model with visual recognition capabilities,
a multimodal intelligence that can perceive visuals. Users can easily upload or drag and drop images into the dialogue box,
and the agent will be able to recognize the content of the images and engage in intelligent conversation based on this,
creating smarter and more diversified chat scenarios.

This feature opens up new interactive methods, allowing communication to transcend text and include a wealth of visual elements.
Whether it's sharing images in daily use or interpreting images within specific industries, the agent provides an outstanding conversational experience.

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-tts]][docs-feat-tts]

### [TTS & STT Voice Conversation][docs-feat-tts]

LobeHub supports Text-to-Speech (TTS) and Speech-to-Text (STT) technologies, enabling our application to convert text messages into clear voice outputs,
allowing users to interact with our conversational agent as if they were talking to a real person. Users can choose from a variety of voices to pair with the agent.

Moreover, TTS offers an excellent solution for those who prefer auditory learning or desire to receive information while busy.
In LobeHub, we have meticulously selected a range of high-quality voice options (OpenAI Audio, Microsoft Edge Speech) to meet the needs of users from different regions and cultural backgrounds.
Users can choose the voice that suits their personal preferences or specific scenarios, resulting in a personalized communication experience.

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-t2i]][docs-feat-t2i]

### [Text to Image Generation][docs-feat-t2i]

With support for the latest text-to-image generation technology, LobeHub now allows users to invoke image creation tools directly within conversations with the agent. By leveraging the capabilities of AI tools such as [`DALL-E 3`](https://openai.com/dall-e-3), [`MidJourney`](https://www.midjourney.com/), and [`Pollinations`](https://pollinations.ai/), the agents are now equipped to transform your ideas into images.

This enables a more private and immersive creative process, allowing for the seamless integration of visual storytelling into your personal dialogue with the agent.

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-plugin]][docs-feat-plugin]

### [Plugin System (Function Calling)][docs-feat-plugin]

The plugin ecosystem of LobeHub is an important extension of its core functionality, greatly enhancing the practicality and flexibility of the LobeHub assistant.

<video controls src="https://github.com/lobehub/lobe-chat/assets/28616219/f29475a3-f346-4196-a435-41a6373ab9e2" muted="false"></video>

By utilizing plugins, LobeHub assistants can obtain and process real-time information, such as searching for web information and providing users with instant and relevant news.

In addition, these plugins are not limited to news aggregation, but can also extend to other practical functions, such as quickly searching documents, generating images, obtaining data from various platforms like Bilibili, Steam, and interacting with various third-party services.

> \[!TIP]
>
> Learn more about [📘 Plugin Usage][docs-usage-plugin] by checking it out.

<!-- PLUGIN LIST -->

| Recent Submits                                                                                                             | Description                                                                                                                                     |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [Shopping tools](https://lobechat.com/discover/plugin/ShoppingTools)<br/><sup>By **shoppingtools** on **2026-01-12**</sup> | Search for products on eBay & AliExpress, find eBay events & coupons. Get prompt examples.<br/>`shopping` `e-bay` `ali-express` `coupons`       |
| [SEO Assistant](https://lobechat.com/discover/plugin/seo_assistant)<br/><sup>By **webfx** on **2026-01-12**</sup>          | The SEO Assistant can generate search engine keyword information in order to aid the creation of content.<br/>`seo` `keyword`                   |
| [Video Captions](https://lobechat.com/discover/plugin/VideoCaptions)<br/><sup>By **maila** on **2025-12-13**</sup>         | Convert Youtube links into transcribed text, enable asking questions, create chapters, and summarize its content.<br/>`video-to-text` `youtube` |
| [WeatherGPT](https://lobechat.com/discover/plugin/WeatherGPT)<br/><sup>By **steven-tey** on **2025-12-13**</sup>           | Get current weather information for a specific location.<br/>`weather`                                                                          |

> 📊 Total plugins: [<kbd>**40**</kbd>](https://lobechat.com/discover/plugins)

 <!-- PLUGIN LIST -->

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-agent]][docs-feat-agent]

### [Agent Market (GPTs)][docs-feat-agent]

In LobeHub Agent Marketplace, creators can discover a vibrant and innovative community that brings together a multitude of well-designed agents,
which not only play an important role in work scenarios but also offer great convenience in learning processes.
Our marketplace is not just a showcase platform but also a collaborative space. Here, everyone can contribute their wisdom and share the agents they have developed.

> \[!TIP]
>
> By [🤖/🏪 Submit Agents][submit-agents-link], you can easily submit your agent creations to our platform.
> Importantly, LobeHub has established a sophisticated automated internationalization (i18n) workflow,
> capable of seamlessly translating your agent into multiple language versions.
> This means that no matter what language your users speak, they can experience your agent without barriers.

> \[!IMPORTANT]
>
> We welcome all users to join this growing ecosystem and participate in the iteration and optimization of agents.
> Together, we can create more interesting, practical, and innovative agents, further enriching the diversity and practicality of the agent offerings.

<!-- AGENT LIST -->

| Recent Submits                                                                                                                                                                 | Description                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Turtle Soup Host](https://lobechat.com/discover/assistant/lateral-thinking-puzzle)<br/><sup>By **[CSY2022](https://github.com/CSY2022)** on **2025-06-19**</sup>              | A turtle soup host needs to provide the scenario, the complete story (truth of the event), and the key point (the condition for guessing correctly).<br/>`turtle-soup` `reasoning` `interaction` `puzzle` `role-playing` |
| [Academic Writing Assistant](https://lobechat.com/discover/assistant/academic-writing-assistant)<br/><sup>By **[swarfte](https://github.com/swarfte)** on **2025-06-17**</sup> | Expert in academic research paper writing and formal documentation<br/>`academic-writing` `research` `formal-style`                                                                                                      |
| [Gourmet Reviewer🍟](https://lobechat.com/discover/assistant/food-reviewer)<br/><sup>By **[renhai-lab](https://github.com/renhai-lab)** on **2025-06-17**</sup>                | Food critique expert<br/>`gourmet` `review` `writing`                                                                                                                                                                    |
| [Minecraft Senior Developer](https://lobechat.com/discover/assistant/java-development)<br/><sup>By **[iamyuuk](https://github.com/iamyuuk)** on **2025-06-17**</sup>           | Expert in advanced Java development and Minecraft mod and server plugin development<br/>`development` `programming` `minecraft` `java`                                                                                   |

> 📊 Total agents: [<kbd>**505**</kbd> ](https://lobechat.com/discover/assistants)

 <!-- AGENT LIST -->

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-database]][docs-feat-database]

### [Support Local / Remote Database][docs-feat-database]

LobeHub supports the use of both server-side and local databases. Depending on your needs, you can choose the appropriate deployment solution:

- **Local database**: suitable for users who want more control over their data and privacy protection. LobeHub uses CRDT (Conflict-Free Replicated Data Type) technology to achieve multi-device synchronization. This is an experimental feature aimed at providing a seamless data synchronization experience.
- **Server-side database**: suitable for users who want a more convenient user experience. LobeHub supports PostgreSQL as a server-side database. For detailed documentation on how to configure the server-side database, please visit [Configure Server-side Database](https://lobehub.com/docs/self-hosting/advanced/server-database).

Regardless of which database you choose, LobeHub can provide you with an excellent user experience.

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-auth]][docs-feat-auth]

### [Support Multi-User Management][docs-feat-auth]

LobeHub supports multi-user management and provides flexible user authentication solutions:

- **Better Auth**: LobeHub integrates `Better Auth`, a modern and flexible authentication library that supports multiple authentication methods, including OAuth, email login, credential login, magic links, and more. With `Better Auth`, you can easily implement user registration, login, session management, social login, multi-factor authentication (MFA), and other functions to ensure the security and privacy of user data.

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[![][image-feat-pwa]][docs-feat-pwa]

### [Progressive Web App (PWA)][docs-feat-pwa]

We deeply understand the importance of providing a seamless experience for users in today's multi-device environment.
Therefore, we have adopted Progressive Web Application ([PWA](https://support.google.com/chrome/answer/9658361)) technology,
a modern web technology that elevates web applications to an experience close to that of native apps.

Through PWA, LobeHub can offer a highly optimized user experience on both desktop and mobile devices while maintaining high-performance characteristics.