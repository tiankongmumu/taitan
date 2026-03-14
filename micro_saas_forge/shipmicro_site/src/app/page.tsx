import { loadTools, loadNews } from "@/lib/data";
import { FadeIn } from "@/components/ui/FadeIn";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "ShipMicro — AI效率工具平台 | 证件照·关税查询·开发者工具",
  description: "AI证件照制作、HS关税秒查、15+开发者工具、小游戏、科技资讯。好用的效率工具合集，打开就能用。",
};

const GAME_CATS = ["Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic", "Game", "Arcade"];

/* ── 自有产品（收费） ── */
const OWN_PRODUCTS = [
  {
    emoji: "📷", title: "AI证件照制作", titleEn: "AI ID Photo",
    desc: "一寸二寸护照驾照，5种背景色一键换，隐私100%安全",
    price: "¥9.9", priceLabel: "永久使用",
    href: "/tools/idphoto",
    gradient: "from-purple-500 to-pink-500",
    glow: "shadow-purple-500/20",
    tags: ["🔥 热门", "本地处理"],
    features: ["6种标准尺寸", "5种背景色", "照片不上传服务器"],
  },
  {
    emoji: "🌐", title: "HS关税秒查", titleEn: "HS Tariff Lookup",
    desc: "外贸神器！输入产品名秒出HS编码+关税，免翻墙直连美国ITC",
    price: "¥9.9", priceLabel: "永久使用",
    href: "/tools/hs-tariff",
    gradient: "from-blue-500 to-cyan-500",
    glow: "shadow-blue-500/20",
    tags: ["外贸必备", "官方数据"],
    features: ["免翻墙直连", "实时USITC数据", "导出Excel"],
  },
];

/* ── 推荐工具（联盟） ── */
const PARTNER_PRODUCTS = [
  { emoji: "☁️", name: "阿里云", desc: "云服务器·网站托管·AI API", tag: "最高30%返佣", href: "https://www.aliyun.com/daily-act/ecs/activity_selection?userCode=shipmicro" },
  { emoji: "☁️", name: "腾讯云", desc: "云服务器·小程序·AI接口", tag: "最高25%返佣", href: "https://cloud.tencent.com/act/cps/redirect?redirect=1&from=shipmicro" },
  { emoji: "🤖", name: "AI API中转", desc: "国内稳定使用GPT/Claude API", tag: "充值返佣", href: "https://api2d.com/" },
  { emoji: "📝", name: "飞书", desc: "团队协作·项目管理·文档", tag: "注册返佣", href: "https://www.feishu.cn/" },
  { emoji: "📚", name: "语雀", desc: "团队知识库·技术文档管理", tag: "升级返佣", href: "https://www.yuque.com/" },
  { emoji: "💰", name: "小报童", desc: "付费专栏·知识变现·订阅制", tag: "90%归作者", href: "https://xiaobot.net/" },
];

/* ── 功能区 ── */
const SECTIONS = [
  { emoji: "⚡", title: "开发者工具", desc: "JSON·正则·JWT·Base64 等15+工具", href: "/tools", gradient: "from-cyan-500 to-blue-600" },
  { emoji: "🎮", title: "休闲小游戏", desc: "打地鼠·水果忍者·数学闪电战", href: "/arcade", gradient: "from-fuchsia-500 to-pink-600" },
  { emoji: "📰", title: "科技资讯", desc: "AI精选每日开发者新闻", href: "/news", gradient: "from-amber-500 to-orange-600" },
  { emoji: "💡", title: "赚钱灵感", desc: "AI生成每日创业点子+可行性评分", href: "/ideas", gradient: "from-emerald-500 to-teal-600" },
];

export default async function HomePage() {
  const allTools = loadTools();
  const tools = allTools.filter(t => !GAME_CATS.includes(t.cat) && t.success);
  const games = allTools.filter(t => GAME_CATS.includes(t.cat) && t.success);
  const news = loadNews();

  return (
    <div className="relative z-10 font-sans">

      {/* ═══════════════════════════════════════════
          HERO — 中文优先
         ═══════════════════════════════════════════ */}
      <section className="relative min-h-[60vh] md:min-h-[80vh] flex flex-col items-center justify-center text-center px-4 py-12 sm:py-0 overflow-hidden">
        <div className="absolute top-20 left-1/4 w-[150px] sm:w-[250px] md:w-[500px] h-[150px] sm:h-[250px] md:h-[500px] bg-violet-600/10 rounded-full blur-[50px] sm:blur-[80px] md:blur-[120px] animate-blob pointer-events-none" />
        <div className="absolute bottom-20 right-1/4 w-[120px] sm:w-[200px] md:w-[400px] h-[120px] sm:h-[200px] md:h-[400px] bg-cyan-600/10 rounded-full blur-[40px] sm:blur-[60px] md:blur-[100px] animate-blob animation-delay-2000 pointer-events-none" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[180px] sm:w-[300px] md:w-[600px] h-[180px] sm:h-[300px] md:h-[600px] bg-fuchsia-600/5 rounded-full blur-[60px] sm:blur-[100px] md:blur-[150px] animate-pulse-glow pointer-events-none" />

        <FadeIn delay={0}>
          <div className="badge badge-purple mb-6 sm:mb-8 shadow-lg shadow-violet-500/10 text-[10px] sm:text-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-2" />
            TITAN Engine · {tools.length + games.length + OWN_PRODUCTS.length} 款工具在线
          </div>
        </FadeIn>

        <FadeIn delay={100}>
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-black tracking-[-0.03em] leading-[1.1] mb-6 font-[family-name:var(--font-outfit)] max-w-5xl">
            <span className="text-white">你的</span>
            <span className="text-shimmer">AI 效率工具箱</span>
          </h1>
        </FadeIn>

        <FadeIn delay={200}>
          <p className="text-base sm:text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-8 sm:mb-10 font-light leading-relaxed px-2">
            证件照制作 · 关税查询 · 开发者工具 · 小游戏 · 科技资讯
            <br className="hidden sm:block" />
            <span className="text-white font-medium">打开就能用，好用不贵</span>
          </p>
        </FadeIn>

        <FadeIn delay={300}>
          <div className="flex gap-3 sm:gap-4 flex-wrap justify-center px-2">
            <a href="#products" className="group relative px-5 sm:px-7 py-3 sm:py-3.5 rounded-full font-bold text-xs sm:text-sm text-white overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-violet-500/25">
              <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-cyan-600 rounded-full" />
              <div className="absolute inset-0 bg-gradient-to-r from-violet-500 to-cyan-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
              <span className="relative z-10 flex items-center gap-2">
                🔥 查看热门产品
                <span className="group-hover:translate-x-0.5 transition-transform">↓</span>
              </span>
            </a>
            <a href="/tools" className="px-5 sm:px-7 py-3 sm:py-3.5 rounded-full font-bold text-xs sm:text-sm border border-white/10 text-white bg-white/[0.03] hover:bg-white/[0.08] hover:border-white/20 transition-all duration-300 hover:scale-105">
              ⚡ 免费工具
            </a>
          </div>
        </FadeIn>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-gray-600 animate-pulse">
          <span className="text-[10px] uppercase tracking-widest">往下滑</span>
          <div className="w-px h-6 bg-gradient-to-b from-gray-600 to-transparent" />
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          🔥 自有产品 — 核心推广区
         ═══════════════════════════════════════════ */}
      <section id="products" className="max-w-7xl mx-auto px-4 sm:px-6 pb-16 scroll-mt-20">
        <div className="text-center mb-10">
          <FadeIn delay={0}>
            <h2 className="text-2xl sm:text-3xl font-black text-white font-[family-name:var(--font-outfit)] mb-2">
              🔥 热门工具
            </h2>
            <p className="text-sm text-gray-500">实用好用，解决真问题</p>
          </FadeIn>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {OWN_PRODUCTS.map((product, i) => (
            <FadeIn key={product.title} delay={i * 100}>
              <a href={product.href}
                className={`group relative block rounded-3xl border border-white/[0.08] bg-white/[0.02] overflow-hidden transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl ${product.glow}`}>
                {/* Top gradient */}
                <div className={`h-1 bg-gradient-to-r ${product.gradient}`} />

                <div className="p-5 sm:p-8">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl sm:text-4xl">{product.emoji}</span>
                      <div>
                        <h3 className="text-base sm:text-xl font-black text-white group-hover:translate-x-0.5 transition-transform">{product.title}</h3>
                        <span className="text-xs text-gray-600">{product.titleEn}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-xl sm:text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r ${product.gradient}`}>
                        {product.price}
                      </div>
                      <div className="text-[10px] text-gray-500">{product.priceLabel}</div>
                    </div>
                  </div>

                  <p className="text-gray-400 text-sm mb-4">{product.desc}</p>

                  {/* Tags */}
                  <div className="flex gap-2 mb-4">
                    {product.tags.map(tag => (
                      <span key={tag} className="badge badge-purple text-[10px]">{tag}</span>
                    ))}
                  </div>

                  {/* Features */}
                  <div className="flex flex-wrap gap-3">
                    {product.features.map(feat => (
                      <span key={feat} className="text-[11px] text-gray-500 flex items-center gap-1">
                        <span className="text-emerald-400">✓</span> {feat}
                      </span>
                    ))}
                  </div>

                  {/* CTA */}
                  <div className={`mt-6 inline-flex items-center gap-2 text-sm font-bold text-transparent bg-clip-text bg-gradient-to-r ${product.gradient}`}>
                    立即使用 <span className="text-white group-hover:translate-x-1 transition-transform">→</span>
                  </div>
                </div>
              </a>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          功能区 4 cards
         ═══════════════════════════════════════════ */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {SECTIONS.map((s, i) => (
            <FadeIn key={s.title} delay={i * 60}>
              <a href={s.href}
                className="card card-glow group block p-4 sm:p-6 rounded-2xl text-center transition-all duration-500">
                <span className="text-2xl sm:text-3xl block mb-2 sm:mb-3">{s.emoji}</span>
                <h3 className="text-xs sm:text-sm font-bold text-white mb-1 group-hover:translate-x-0.5 transition-transform">{s.title}</h3>
                <p className="text-[11px] text-gray-500">{s.desc}</p>
              </a>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          统计栏
         ═══════════════════════════════════════════ */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "工具总数", value: tools.length + 2, icon: "⚡", color: "text-cyan-400", border: "border-cyan-500/10" },
            { label: "小游戏", value: games.length, icon: "🎮", color: "text-fuchsia-400", border: "border-fuchsia-500/10" },
            { label: "合作品牌", value: PARTNER_PRODUCTS.length, icon: "🤝", color: "text-amber-400", border: "border-amber-500/10" },
            { label: "工具价格", value: "免费", icon: "💎", color: "text-emerald-400", border: "border-emerald-500/10" },
          ].map((s, i) => (
            <FadeIn key={i} delay={i * 60}>
              <div className={`text-center p-5 rounded-2xl border ${s.border} bg-white/[0.01]`}>
                <div className="text-xl mb-1">{s.icon}</div>
                <div className={`text-2xl sm:text-3xl font-black ${s.color} font-[family-name:var(--font-outfit)]`}>{s.value}</div>
                <div className="text-[10px] text-gray-600 mt-1 uppercase tracking-widest">{s.label}</div>
              </div>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          开发者工具（分类预览）
         ═══════════════════════════════════════════ */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl sm:text-2xl font-black text-white font-[family-name:var(--font-outfit)]">⚡ 免费开发者工具</h2>
            <p className="text-sm text-gray-500 mt-1">无需注册，打开即用</p>
          </div>
          <a href="/tools" className="badge badge-cyan hover:bg-cyan-500/20 transition-colors">查看全部 →</a>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {tools.slice(0, 6).map((tool, i) => (
            <FadeIn key={tool.slug} delay={i * 50}>
              <a href={`/tools/${tool.slug}`}
                className="card card-glow group p-5 rounded-xl flex items-start gap-4">
                <span className="text-2xl mt-0.5 shrink-0">{tool.icon}</span>
                <div className="min-w-0">
                  <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors truncate">
                    {tool.nameCn || tool.name}
                  </h3>
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{tool.descCn || tool.desc}</p>
                </div>
              </a>
            </FadeIn>
          ))}
        </div>
        {tools.length > 6 && (
          <div className="text-center mt-4">
            <a href="/tools" className="text-xs text-gray-500 hover:text-cyan-400 transition-colors">
              + {tools.length - 6} 个更多工具 →
            </a>
          </div>
        )}
      </section>

      {/* ═══════════════════════════════════════════
          🤝 合作伙伴推荐
         ═══════════════════════════════════════════ */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl sm:text-2xl font-black text-white font-[family-name:var(--font-outfit)]">🤝 精选推荐</h2>
            <p className="text-sm text-gray-500 mt-1">我们在用的好工具</p>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {PARTNER_PRODUCTS.map((p, i) => (
            <FadeIn key={p.name} delay={i * 50}>
              <a href={p.href} target="_blank" rel="noopener noreferrer"
                className="card card-glow group p-4 rounded-xl text-center">
                <span className="text-2xl block mb-2">{p.emoji}</span>
                <h3 className="text-xs font-bold text-white mb-0.5 group-hover:text-cyan-300 transition-colors">{p.name}</h3>
                <p className="text-[10px] text-gray-600 line-clamp-1">{p.desc}</p>
                <span className="badge badge-emerald text-[9px] mt-2">{p.tag}</span>
              </a>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          资讯 + 游戏
         ═══════════════════════════════════════════ */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* News */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-black text-white">📰 今日资讯</h2>
              <a href="/news" className="badge badge-amber text-[10px]">更多 →</a>
            </div>
            <div className="space-y-2">
              {news.slice(0, 4).map((article, i) => (
                <FadeIn key={i} delay={i * 50}>
                  <a href={article.url} target="_blank" rel="noopener noreferrer"
                    className="card card-glow group p-4 rounded-xl flex items-center gap-3">
                    <span className="badge badge-amber text-[9px] shrink-0">{article.source}</span>
                    <h3 className="text-xs font-semibold text-white group-hover:text-amber-300 transition-colors line-clamp-1 flex-1">{article.title}</h3>
                    <span className="text-[10px] text-gray-600 shrink-0">{article.score}</span>
                  </a>
                </FadeIn>
              ))}
            </div>
          </div>

          {/* Games */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-black text-white">🎮 休闲一刻</h2>
              <a href="/arcade" className="badge badge-purple text-[10px]">全部游戏 →</a>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {games.slice(0, 6).map((game, i) => (
                <FadeIn key={game.slug} delay={i * 50}>
                  <a href={`/arcade/${game.slug}`}
                    className="card card-glow group p-4 rounded-xl text-center">
                    <span className="text-2xl block mb-1 group-hover:scale-110 transition-transform">{game.icon}</span>
                    <h3 className="text-[10px] font-bold text-white group-hover:text-fuchsia-300 transition-colors">{game.name}</h3>
                  </a>
                </FadeIn>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          CTA — 关注 & 小报童
         ═══════════════════════════════════════════ */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        <div className="relative overflow-hidden rounded-2xl sm:rounded-3xl border border-violet-500/20 p-6 sm:p-10 md:p-14 text-center">
          <div className="absolute inset-0 bg-gradient-to-br from-violet-600/5 via-transparent to-cyan-600/5" />
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent" />
          <div className="relative z-10">
            <h2 className="text-xl sm:text-2xl md:text-3xl font-black text-white mb-3 font-[family-name:var(--font-outfit)]">
              📱 关注「木木效率工坊」
            </h2>
            <p className="text-gray-400 text-sm max-w-md mx-auto mb-6">
              小红书搜索「木木效率工坊」· 第一时间获取新工具上线通知 · AI创业干货
            </p>
            <div className="flex gap-2 sm:gap-3 justify-center flex-wrap">
              <a href="https://xiaobot.net/" target="_blank" rel="noopener noreferrer"
                className="px-4 sm:px-6 py-2.5 rounded-full bg-gradient-to-r from-violet-600 to-cyan-600 text-white font-bold text-xs sm:text-sm hover:scale-105 transition-transform shadow-lg shadow-violet-500/20">
                📖 小报童付费专栏
              </a>
              <a href="https://afdian.com/a/tiankongmumu" target="_blank" rel="noopener noreferrer"
                className="px-4 sm:px-6 py-2.5 rounded-full border border-white/10 bg-white/[0.03] text-white font-bold text-xs sm:text-sm hover:bg-white/[0.08] transition-all">
                ☕ 支持作者
              </a>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
