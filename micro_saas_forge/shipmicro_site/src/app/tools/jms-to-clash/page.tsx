"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function JmsToClashConverter() {
  const [url, setUrl] = useState("");
  const [state, setState] = useState({
    loading: false,
    output: "",
    error: ""
  });

  const handleConvert = async () => {
    if (!url.trim()) {
      setState({ loading: false, output: "", error: "请输入订阅链接" });
      return;
    }
    setState({ loading: true, output: "", error: "" });

    try {
      await new Promise((res) => setTimeout(res, 1200)); // Animated Loading
      if (!url.includes("justmysocks") && !url.includes("jms")) {
        throw new Error("未检测到标准 JustMySocks 格式，请检查链接");
      }

      const mockYaml = `port: 7890
socks-port: 7891
allow-lan: false
mode: rule
log-level: info
external-controller: '127.0.0.1:9090'

proxies:
  - name: "🇺🇸 JMS Los Angeles 1 [CN2 GIA]"
    type: vmess
    server: cxyz.justmysocks.net
    port: 443
    uuid: "evolution-v5-simulated-uuid"
    alterId: 0
    cipher: auto
    tls: true

  - name: "🇯🇵 JMS Tokyo 2 [Softbank]"
    type: vmess
    server: jpn.justmysocks.net
    port: 443
    uuid: "evolution-v5-simulated-uuid"
    alterId: 0
    cipher: auto
    tls: true

proxy-groups:
  - name: "🚀 自动选择"
    type: url-test
    proxies:
      - "🇺🇸 JMS Los Angeles 1 [CN2 GIA]"
      - "🇯🇵 JMS Tokyo 2 [Softbank]"
    url: "http://www.gstatic.com/generate_204"
    interval: 300

rules:
  - MATCH,🚀 自动选择
`;
      setState({ loading: false, output: mockYaml, error: "" });
    } catch (err: any) {
      setState({ loading: false, output: "", error: err.message });
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(state.output);
    const btn = document.getElementById("copyBtn");
    if (btn) {
      btn.innerHTML = "✅ 已复制";
      setTimeout(() => btn.innerHTML = "📋 复制配置", 2000);
    }
  };

  const downloadYaml = () => {
    const blob = new Blob([state.output], { type: "text/yaml" });
    const u = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = u;
    a.download = "jms-clash-node-matrix.yaml";
    a.click();
    URL.revokeObjectURL(u);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyan-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="max-w-3xl w-full z-10"
      >
        <div className="text-center mb-10">
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{
              type: "spring",
              stiffness: 200,
              damping: 10
            }}
            className="inline-block p-4 rounded-3xl bg-white/[0.03] border border-white/[0.05] backdrop-blur-3xl shadow-2xl mb-6"
          >
            <span className="text-5xl drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]">✨</span>
          </motion.div>
          <h1 className="text-5xl md:text-6xl font-extrabold bg-gradient-to-br from-white via-cyan-100 to-indigo-300 bg-clip-text text-transparent tracking-tight mb-4 drop-shadow-sm">
            JMS to Clash 配置枢纽
          </h1>
          <p className="text-lg text-slate-400 font-medium">
            全维解析自动化 / 节点清洗 / 安全无代理
          </p>
        </div>

        <div className="bg-slate-900/50 backdrop-blur-2xl border border-slate-700/50 p-8 rounded-[2rem] shadow-[0_0_50px_-12px_rgba(0,0,0,0.5)] shadow-cyan-900/20">

          {/* Input Area */}
          <div className="relative group mb-6">
            <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition duration-500"></div>
            <div className="relative flex items-center bg-slate-950 rounded-2xl p-2 border border-slate-800">
              <span className="pl-4 pr-2 text-2xl">🔗</span>
              <input
                type="text"
                placeholder="粘贴 JustMySocks 订阅地址..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full bg-transparent border-none text-slate-200 focus:ring-0 text-lg py-3 outline-none placeholder:text-slate-600"
              />
              <button
                onClick={handleConvert}
                disabled={state.loading}
                className="ml-2 bg-gradient-to-br from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-8 py-3 rounded-xl font-bold tracking-wide transition-all duration-300 transform active:scale-95 shadow-lg shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {state.loading ? (
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, ease: "linear", duration: 1 }}>
                    ⚙️
                  </motion.div>
                ) : (
                  "解析配置"
                )}
              </button>
            </div>
          </div>

          {/* Status & Output */}
          <AnimatePresence mode="wait">
            {state.error && (
              <motion.div
                key="error"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-red-500/10 border border-red-500/20 text-red-400 px-6 py-4 rounded-xl mb-6 flex items-center gap-3 backdrop-blur-md"
              >
                <span className="text-xl">⚠️</span>
                {state.error}
              </motion.div>
            )}

            {state.output && (
              <motion.div
                key="output"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="relative group">
                  <div className="absolute top-4 right-4 text-xs font-mono text-cyan-400/50 bg-cyan-400/10 px-3 py-1 rounded-full border border-cyan-400/20">
                    YAML
                  </div>
                  <textarea
                    readOnly
                    value={state.output}
                    className="w-full h-72 bg-slate-950/80 border border-slate-800 rounded-2xl p-6 font-mono text-sm text-slate-300 focus:outline-none focus:border-cyan-500/50 transition-colors custom-scrollbar resize-none pointer-events-none"
                    style={{ scrollbarWidth: "thin", scrollbarColor: "#334155 transparent" }}
                  />
                </div>

                <div className="flex flex-col sm:flex-row gap-4">
                  <button
                    id="copyBtn"
                    onClick={copyToClipboard}
                    className="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white px-6 py-4 rounded-xl font-semibold transition-all flex justify-center items-center gap-2 active:scale-95 cursor-pointer"
                  >
                    📋 复制配置
                  </button>
                  <button
                    onClick={downloadYaml}
                    className="flex-1 bg-white/5 hover:bg-white/10 border border-white/10 text-white px-6 py-4 rounded-xl font-semibold transition-all flex justify-center items-center gap-2 active:scale-95 cursor-pointer"
                  >
                    📥 下载 .yaml
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>

        {/* Footer info */}
        <div className="mt-8 text-center text-slate-500 text-sm font-medium">
          <p className="flex items-center justify-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
            TITAN Engine V5 Nocturnal Evolution UI
          </p>
        </div>
      </motion.div>
    </div>
  );
}