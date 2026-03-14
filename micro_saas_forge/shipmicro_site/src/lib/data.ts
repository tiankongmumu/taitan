import fs from "fs";
import path from "path";

interface NewsArticle {
    title: string;
    source: string;
    score: number;
    slug: string;
    url: string;
    category: string;
    generated_at: string;
}

export interface ToolInfo {
    name: string;
    slug: string;
    desc: string;
    cat: string;
    icon: string;
    url?: string;
    success?: boolean;
    score?: number;
    isPremium?: boolean;
    affiliateUrl?: string;
    nameCn?: string;
    descCn?: string;
}

/* ─────────────────────────────────────────────
   Curated Tool: [name, desc, cat, icon, nameCn, descCn]
   ───────────────────────────────────────────── */
type ToolEntry = [string, string, string, string, string, string];
const CURATED_TOOLS: Record<string, ToolEntry> = {
    // 🔥 Premium Products
    "niuma-oracle": ["AI 前生今世判官", "AI-powered divination to generate your corporate slave reincarnation script", "Utility", "🔮", "AI 牛马判官", "测算你的前世牛马剧本，AI定制发疯转运密码"],
    "idphoto": ["AI ID Photo", "AI-powered ID photo maker with 6 sizes, 5 background colors, 100% privacy", "Utility", "📷", "AI证件照制作", "一寸二寸护照驾照，5种背景色一键换，隐私100%安全"],
    "hs-tariff": ["HS Tariff Lookup", "Instant HS code and tariff lookup connected to USITC", "Utility", "🌐", "HS关税秒查", "输入产品名秒出HS编码+关税，免翻墙直连美国ITC"],
    // Code Tools
    "json-formatter": ["JSON Formatter", "Format, validate, and beautify JSON with auto-fix", "Code", "⚡", "JSON 格式化", "一键格式化、验证和美化 JSON 数据"],
    "regex-tester": ["Regex Tester", "Test regex with live matching, captures, and cheatsheet", "Code", "🔍", "正则测试器", "实时匹配、捕获组、速查表一应俱全"],
    "jwt-decoder": ["JWT Decoder", "Decode JWT tokens with expiry warnings and timestamps", "Code", "🔑", "JWT 解码器", "解码令牌、过期提醒、时间戳转换"],
    "base64-codec": ["Base64 Codec", "Encode and decode Base64 with file drag-and-drop", "Code", "🔐", "Base64 编解码", "编码解码、拖拽文件即可"],
    "diff-checker": ["Diff Checker", "Compare two texts side-by-side with line-level highlights", "Code", "📊", "文本对比器", "并排对比两段文本，高亮差异"],
    "sql-formatter": ["SQL Formatter", "Format and prettify SQL queries with dialect support", "Code", "🗄️", "SQL 格式化", "格式化 SQL 查询，支持多种方言"],
    // Security
    "password-gen": ["Password Generator", "Generate secure passwords with strength analysis", "Security", "🔒", "密码生成器", "生成高强度密码，含安全评分"],
    "hash-generator": ["Hash Generator", "Generate MD5, SHA-1, SHA-256 hashes instantly", "Security", "🛡️", "哈希生成器", "MD5/SHA-1/SHA-256 一键生成"],
    "uuid-generator": ["UUID Generator", "Generate UUID v4 with bulk mode and format options", "Security", "🆔", "UUID 生成器", "批量生成 UUID v4，多种格式"],
    // Converter
    "color-converter": ["Color Converter", "Convert between HEX, RGB, HSL with visual picker", "Converter", "🎨", "颜色转换器", "HEX/RGB/HSL 互转，可视化选色"],
    "unit-converter": ["Unit Converter", "Convert units: length, weight, temp, data size, and more", "Converter", "📏", "单位转换器", "长度/重量/温度/数据大小 一键换算"],
    "timestamp-conv": ["Timestamp Converter", "Convert Unix timestamps to human-readable dates and back", "Converter", "⏱️", "时间戳转换", "Unix 时间戳与日期互转"],
    // Productivity
    "markdown-editor": ["Markdown Editor", "Write and preview Markdown with export to HTML/PDF", "Editor", "📝", "Markdown 编辑器", "实时预览，导出 HTML/PDF"],
    "qr-generator": ["QR Code Generator", "Generate QR codes with custom colors and logo embedding", "Utility", "📱", "二维码生成器", "自定义颜色/LOGO 的二维码"],
    "lorem-generator": ["Lorem Ipsum Generator", "Generate placeholder text in paragraphs, sentences, or words", "Utility", "📄", "占位文本生成", "按段落/句子/单词生成占位符"],
    // 🚀 Vercel-Deployed Premium Apps (TITAN Engine Wave 1)
    "jwt-debugger-pro": ["JWT Debugger Pro", "Inspect, validate, and generate JSON Web Tokens with advanced debugging", "Code", "🔑", "JWT 调试器 Pro", "解码、生成、验证 JWT Token，支持多种算法"],
    "json-path-finder-pro": ["JSON Path Finder", "Find and test JSON paths with real-time preview", "Code", "🔍", "JSON路径查找器", "实时测试 JSON 路径表达式"],
    "sql-formatter-pro": ["SQL Query Formatter", "Format, beautify and optimize SQL queries instantly", "Code", "🗃️", "SQL格式化器 Pro", "一键美化和格式化 SQL 查询"],
    "curl-to-code": ["cURL to Code", "Convert cURL commands to Python, JavaScript, Go and more", "Code", "🔄", "cURL转代码", "把 cURL 命令转成 Python/JS/Go 代码"],
    "pg-schema-designer": ["PostgreSQL Schema Designer", "Visual PostgreSQL schema designer with SQL export", "Code", "🐘", "PostgreSQL设计器", "可视化数据库设计,导出 SQL"],
    "qr-generator-pro": ["Smart QR Generator", "Generate customizable QR codes with logos and colors", "Utility", "📱", "智能二维码 Pro", "支持 Logo 和自定义颜色的二维码"],
    "image-compress-pro": ["Image Compress Pro", "Compress images without losing quality — JPG, PNG, WebP", "Design", "🖼️", "图片压缩 Pro", "无损压缩，支持 JPG/PNG/WebP"],
    "svg-to-png-pro": ["SVG to PNG Converter", "Convert SVG to high-quality PNG with custom resolution", "Design", "🎨", "SVG转PNG", "高质量 SVG 到 PNG 格式转换"],
    "typing-speed-pro": ["Typing Speed Test", "Test your typing speed and accuracy with real-time WPM", "Utility", "⌨️", "打字速度测试", "实时 WPM 追踪，测试打字速度"],
    "favicon-forge-pro": ["Favicon Forge Pro", "Create professional favicons from text, emoji or images", "Design", "⭐", "Favicon生成器", "从文字/Emoji 创建网站图标"],
};

/* ─────────────────────────────────────────────
   Top 5 Curated Games (8-point quality)
   ───────────────────────────────────────────── */
const CURATED_GAME_NAMES: Record<string, [string, string, string, string, string]> = {
    "whack-a-mole": ["Whack-a-Mole", "Tap moles with combo multipliers, Web Audio, and 10 difficulty levels", "🐹", "打地鼠", "60秒限时挑战，连击加成，金色地鼠双倍分"],
    "fruit-ninja": ["Fruit Slicer", "Swipe to slice flying fruits with particle explosions and life system", "🍉", "水果忍者", "滑动切水果，连击爆分，小心炸弹"],
    "math-blitz": ["Math Blitz", "Solve math under pressure with streak combos and time bonuses", "🧮", "数学闪电战", "限时数学挑战，连续答对获连击加成"],
    "meteor-dodge": ["Meteor Dodge", "Pilot your ship through asteroids with shields and star collectibles", "🚀", "陨石闪避", "驾驶飞船躲避陨石，收集星星"],
    "simon-neon": ["Simon Neon", "Repeat musical neon sequences that get faster each round", "🎵", "霓虹记忆", "记忆灯光顺序，越来越快的挑战"],
};

/* ─────────────────────────────────────────────
   External URL mapping for Vercel-deployed tools
   ───────────────────────────────────────────── */
const EXTERNAL_URLS: Record<string, string> = {
    "jwt-debugger-pro": "https://jwt-debugger-tiankongmumus-projects.vercel.app",
    "json-path-finder-pro": "https://json-path-finder-4s481qkm6-tiankongmumus-projects.vercel.app",
    "sql-formatter-pro": "https://sql-query-formatter-cvv37dbxd-tiankongmumus-projects.vercel.app",
    "curl-to-code": "https://curl-to-code-26zngtfol-tiankongmumus-projects.vercel.app",
    "pg-schema-designer": "https://postgresql-schema-designer-n66208e8l-tiankongmumus-projects.vercel.app",
    "qr-generator-pro": "https://smart-qr-generator-l4gdiykzp-tiankongmumus-projects.vercel.app",
    "image-compress-pro": "https://image-compress-7mtlnql94-tiankongmumus-projects.vercel.app",
    "svg-to-png-pro": "https://svg-to-png-pro-converter-grorlo1tm-tiankongmumus-projects.vercel.app",
    "typing-speed-pro": "https://typing-speed-test-72udnt23m-tiankongmumus-projects.vercel.app",
    "favicon-forge-pro": "https://favicon-forge-nwnh7z8hf-tiankongmumus-projects.vercel.app",
};

/* ─────────────────────────────────────────────
   Load curated items
   ───────────────────────────────────────────── */
function loadCuratedTools(): ToolInfo[] {
    const results: ToolInfo[] = [];

    for (const [slug, [name, desc, cat, icon, nameCn, descCn]] of Object.entries(CURATED_TOOLS)) {
        const isExternal = slug in EXTERNAL_URLS;
        results.push({
            name, slug, desc, cat, icon,
            nameCn, descCn,
            url: isExternal ? EXTERNAL_URLS[slug] : `/tools/${slug}.html`,
            isPremium: false,
            success: true,
        });
    }

    for (const [slug, [name, desc, icon, nameCn, descCn]] of Object.entries(CURATED_GAME_NAMES)) {
        results.push({
            name, slug, desc,
            cat: "Game",
            icon,
            nameCn, descCn,
            url: `/games/${slug}.html`,
            success: true,
        });
    }

    return results;
}

/* ─────────────────────────────────────────────
   Public API: only curated items (no AI junk)
   ───────────────────────────────────────────── */
function loadTools(): ToolInfo[] {
    return loadCuratedTools();
}

/* ─────────────────────────────────────────────
   News loader — reads from news_articles/
   ───────────────────────────────────────────── */
function loadNews(): NewsArticle[] {
    try {
        const dir = path.join(process.cwd(), "..", "news_articles");
        if (!fs.existsSync(dir)) return getDefaultNews();

        const files = fs.readdirSync(dir).filter((f: string) => f.startsWith("index_") && f.endsWith(".json"));
        if (files.length === 0) return getDefaultNews();

        const latest = files.sort().reverse()[0];
        const data = JSON.parse(fs.readFileSync(path.join(dir, latest), "utf-8"));
        return data.map((a: Record<string, string | number>) => ({
            title: a.title || "Untitled",
            source: a.source || "News",
            score: a.score || 0,
            slug: a.slug || "",
            url: a.url || "#",
            category: guessNewsCategory(String(a.title || "")),
            generated_at: a.generated_at || new Date().toISOString(),
        }));
    } catch {
        return getDefaultNews();
    }
}

function guessNewsCategory(title: string): string {
    const t = title.toLowerCase();
    if (t.includes("ai") || t.includes("llm") || t.includes("gpt") || t.includes("model") || t.includes("neural")) return "AI";
    if (t.includes("github") || t.includes("open source") || t.includes("open-source") || t.includes("repo")) return "OpenSource";
    if (t.includes("startup") || t.includes("funding") || t.includes("raised") || t.includes("valuation")) return "Startup";
    if (t.includes("web3") || t.includes("crypto") || t.includes("blockchain") || t.includes("defi")) return "Web3";
    if (t.includes("cloud") || t.includes("aws") || t.includes("vercel") || t.includes("docker")) return "Cloud";
    return "Dev";
}

function getDefaultNews(): NewsArticle[] {
    return [
        { title: "GPT-5 Expected to Launch with Real-Time Reasoning", source: "TechCrunch", score: 1247, slug: "gpt5-launch", url: "#", category: "AI", generated_at: new Date().toISOString() },
        { title: "Cloudflare Workers Now Support Full Next.js 16", source: "HackerNews", score: 892, slug: "cf-nextjs", url: "#", category: "Cloud", generated_at: new Date().toISOString() },
        { title: "Rust Takes #2 Spot in GitHub Language Rankings", source: "GitHub", score: 756, slug: "rust-ranking", url: "#", category: "OpenSource", generated_at: new Date().toISOString() },
        { title: "Y Combinator W26 Batch: 47% Are AI-Native Startups", source: "TechCrunch", score: 634, slug: "yc-w26", url: "#", category: "Startup", generated_at: new Date().toISOString() },
        { title: "Bun 2.0 Brings Native SQLite and 3x Faster Builds", source: "HackerNews", score: 578, slug: "bun-2", url: "#", category: "Dev", generated_at: new Date().toISOString() },
        { title: "DeepSeek V3 Open-Sources 685B MoE Model", source: "GitHub", score: 1089, slug: "deepseek-v3", url: "#", category: "AI", generated_at: new Date().toISOString() },
        { title: "Vercel Acquires Turbopack — Becomes Default Bundler", source: "Vercel Blog", score: 445, slug: "vercel-turbo", url: "#", category: "Dev", generated_at: new Date().toISOString() },
        { title: "Solo Developer Reaches $50K MRR with Browser Extension", source: "IndieHackers", score: 923, slug: "indie-50k", url: "#", category: "Startup", generated_at: new Date().toISOString() },
    ];
}

export { loadNews, loadTools };
export type { NewsArticle };
