"use client";

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

export default function NiumaOracle() {
    const [name, setName] = useState('');
    const [industry, setIndustry] = useState('');
    const [zodiac, setZodiac] = useState('');

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState('');
    const [displayedText, setDisplayedText] = useState('');
    const [showPaywall, setShowPaywall] = useState(false);

    const typingTimerRef = useRef<NodeJS.Timeout | null>(null);

    const industries = [
        "互联网/互联网大厂", "程序猿/IT研发", "新媒体/内容运营", "电商/直播带货",
        "外包/乙方", "教培/教育", "金融/审计", "设计/画图狗", "建筑/土木老哥", "传统制造/实体"
    ];

    const zodiacs = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"];

    const handleGenerate = async () => {
        if (!name || !industry || !zodiac) {
            alert("判官需要知道你的全部前世线索！");
            return;
        }

        setLoading(true);
        setResult('');
        setDisplayedText('');
        setShowPaywall(false);

        try {
            const res = await fetch('/api/oracle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, industry, zodiac })
            });

            if (!res.ok) throw new Error("生死簿服务器崩溃了");

            const data = await res.json();
            setResult(data.script || "你这辈子太苦了，系统算不出来。");

        } catch (err) {
            console.error(err);
            setResult("阎王殿大模型宕机，请稍后再试...");
        } finally {
            setLoading(false);
        }
    };

    // Typewriter effect
    useEffect(() => {
        if (result && !loading) {
            let index = 0;
            setDisplayedText('');

            typingTimerRef.current = setInterval(() => {
                if (index < result.length) {
                    setDisplayedText((prev) => prev + result.charAt(index));
                    index++;

                    // Trigger paywall at ~40% of the text or roughly 60 characters
                    if (index === Math.floor(result.length * 0.45) || index === 80) {
                        if (typingTimerRef.current) clearInterval(typingTimerRef.current);
                        setShowPaywall(true);
                    }
                } else {
                    if (typingTimerRef.current) clearInterval(typingTimerRef.current);
                }
            }, 50); // typing speed
        }

        return () => {
            if (typingTimerRef.current) clearInterval(typingTimerRef.current);
        };
    }, [result, loading]);

    const handlePay = () => {
        alert("测试版：支付接口尚未开通。但想象一下这里收了 9.9 元。");
        setShowPaywall(false);

        // Resume typing
        let index = displayedText.length;
        typingTimerRef.current = setInterval(() => {
            if (index < result.length) {
                setDisplayedText((prev) => prev + result.charAt(index));
                index++;
            } else {
                if (typingTimerRef.current) clearInterval(typingTimerRef.current);
            }
        }, 50);
    };

    return (
        <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col font-sans selection:bg-purple-500/30">

            {/* Header */}
            <header className="fixed top-0 w-full z-40 bg-gray-900/80 backdrop-blur-md border-b border-gray-800">
                <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2 group">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-500 to-indigo-500 p-[2px] shadow-lg shadow-purple-500/20 group-hover:shadow-purple-500/40 transition-all">
                            <div className="w-full h-full bg-gray-900 rounded-md flex items-center justify-center">
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400 font-bold text-lg">S</span>
                            </div>
                        </div>
                        <span className="font-bold text-xl tracking-tight text-white group-hover:text-purple-400 transition-colors">ShipMicro</span>
                    </Link>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 max-w-2xl mx-auto w-full px-4 pt-28 pb-12">
                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center px-3 py-1 mb-4 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-medium tracking-wide">
                        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse mr-2"></span>
                        2026年爆款玄学引擎
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black mb-4 tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white via-gray-200 to-gray-500">
                        牛马转世模拟器
                    </h1>
                    <p className="text-gray-400 text-lg">
                        想知道你上辈子造了什么孽，这辈子才会在职场受苦吗？让 AI 判官为你揭秘前世今生。
                    </p>
                </div>

                <div className="bg-gray-800/50 backdrop-blur-xl rounded-3xl border border-gray-700/50 p-6 md:p-8 shadow-2xl relative overflow-hidden">
                    {/* Decorative background glow */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-xs bg-purple-500/10 blur-[100px] pointer-events-none"></div>

                    <div className="space-y-6 relative z-10">
                        {/* Input Form */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">你的姓名 / 昵称</label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="例如：打工狗小李"
                                className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">所属生肖</label>
                                <select
                                    value={zodiac}
                                    onChange={(e) => setZodiac(e.target.value)}
                                    className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all appearance-none"
                                >
                                    <option value="" disabled>选择生肖</option>
                                    {zodiacs.map(z => <option key={z} value={z}>{z}</option>)}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">被困行业</label>
                                <select
                                    value={industry}
                                    onChange={(e) => setIndustry(e.target.value)}
                                    className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all appearance-none"
                                >
                                    <option value="" disabled>选择当牛马的地方</option>
                                    {industries.map(i => <option key={i} value={i}>{i}</option>)}
                                </select>
                            </div>
                        </div>

                        <button
                            onClick={handleGenerate}
                            disabled={loading}
                            className={`w-full mt-4 py-4 rounded-xl font-bold text-lg text-white shadow-lg transition-all
                ${loading
                                    ? 'bg-gray-700 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-purple-600 to-red-600 hover:from-purple-500 hover:to-red-500 hover:shadow-purple-500/25 hover:-translate-y-0.5 active:translate-y-0'
                                }
              `}
                        >
                            {loading ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    阎王殿大模型正在查阅生死簿...
                                </span>
                            ) : "查看我的前生今世"}
                        </button>
                    </div>
                </div>

                {/* Result Area */}
                {displayedText && (
                    <div className="mt-8 relative hidden" id="result-container" style={{ display: 'block' }}>
                        <div className={`bg-gray-800 border border-gray-700 rounded-2xl p-6 md:p-8 relative transition-all duration-700 ${showPaywall ? 'overflow-hidden max-h-[250px]' : ''}`}>

                            <div className="flex items-center justify-between mb-4 border-b border-gray-700 pb-4">
                                <span className="text-sm font-bold tracking-widest text-red-400 uppercase">【绝密：轮回命盘】</span>
                                <span className="text-xs text-gray-500 font-mono">ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}</span>
                            </div>

                            <div className="prose prose-invert max-w-none font-serif leading-loose text-gray-200 whitespace-pre-wrap">
                                {displayedText}
                                {!showPaywall && typingTimerRef.current && (
                                    <span className="inline-block w-2 h-5 bg-purple-500 ml-1 animate-pulse align-middle"></span>
                                )}
                            </div>

                            {/* Faux Paywall Overlay */}
                            {showPaywall && (
                                <div className="absolute inset-0 z-20 flex flex-col items-center justify-end pb-10 bg-gradient-to-t from-gray-900 via-gray-900/95 to-transparent backdrop-blur-[2px]">
                                    <div className="bg-gray-800/80 border border-red-500/30 p-6 rounded-2xl w-[90%] max-w-sm text-center shadow-2xl backdrop-blur-md transform translate-y-4">
                                        <div className="w-12 h-12 bg-red-500/20 text-red-500 rounded-full flex items-center justify-center mx-auto mb-3">
                                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                                        </div>
                                        <h3 className="text-xl font-bold text-white mb-2">天机不可泄露</h3>
                                        <p className="text-sm text-gray-400 mb-6">
                                            命盘已算至关键破局之法。解锁完整剧本及【逆天改命】专属转运海报，需结善缘。
                                        </p>
                                        <button
                                            onClick={handlePay}
                                            className="w-full bg-[#07C160] hover:bg-[#06ad56] text-white font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors"
                                        >
                                            <svg className="w-5 h-5" viewBox="0 0 1024 1024" fill="currentColor"><path d="M512 0c282.784 0 512 229.216 512 512s-229.216 512-512 512S0 794.784 0 512 229.216 0 512 0zm197.664 366.528c-14.784-14.816-37.184-17.76-55.904-7.392L446.72 473.6l-117.824-88.352c-15.04-11.232-36.288-9.056-48.896 5.024-12.608 14.112-11.2 35.424 3.232 47.936l135.584 117.376c11.072 9.6 27.52 10.208 39.296 1.472l235.424-131.84c17.568-9.824 23.808-31.872 14.112-50.688z"></path></svg>
                                            微信支付 9.9 元解锁
                                        </button>
                                        <div className="mt-4 text-xs text-gray-500">已有 8,492 位牛马成功觉醒</div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
