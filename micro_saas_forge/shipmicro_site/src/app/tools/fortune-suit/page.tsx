"use client";

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Typewriter } from '@/components/ui/typewriter';

export default function OraclePage() {
  // Form state
  const [education, setEducation] = useState('');
  const [major, setMajor] = useState('');
  const [frustration, setFrustration] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Result state
  const [result, setResult] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  
  // Typewriter control
  const typewriterRef = useRef<{
    startTyping: (text: string) => void;
    pause: () => void;
    resume: () => void;
    reset: () => void;
  }>(null);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!education.trim() || !major.trim()) {
      alert('请填写学历和专业');
      return;
    }
    
    setIsLoading(true);
    setShowResult(false);
    setResult('');
    
    try {
      const response = await fetch('/api/fortune', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          education,
          major,
          recent_frustration: frustration,
        }),
      });
      
      if (!response.ok) {
        throw new Error('生成运势失败');
      }
      
      const data = await response.json();
      setResult(data.script);
      setShowResult(true);
      setIsLoading(false);
      
      // Start typing after a brief delay
      setTimeout(() => {
        setIsTyping(true);
        typewriterRef.current?.startTyping(data.script);
      }, 500);
      
    } catch (error) {
      console.error('Error:', error);
      alert('生成运势时出错，请重试');
      setIsLoading(false);
    }
  };
  
  const handlePay = () => {
    alert('测试版：模拟支付成功');
    setShowPaywall(false);
    typewriterRef.current?.resume();
  };
  
  const handleTypewriterProgress = (progress: number, displayedText: string) => {
    // Check if we've reached ~40% of the text or ~80 characters
    const shouldTriggerPaywall = 
      (progress >= 0.4 && displayedText.length > 80) || 
      displayedText.includes('脱下长衫');
    
    if (shouldTriggerPaywall && !showPaywall) {
      typewriterRef.current?.pause();
      setShowPaywall(true);
    }
  };
  
  const handleReset = () => {
    setShowResult(false);
    setResult('');
    setIsTyping(false);
    setShowPaywall(false);
    typewriterRef.current?.reset();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-indigo-950 to-black text-white p-4 md:p-8">
      {/* Header */}
      <header className="max-w-4xl mx-auto mb-8 md:mb-12">
        <Link 
          href="/" 
          className="inline-flex items-center text-indigo-300 hover:text-indigo-200 transition-colors mb-4"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回首页
        </Link>
        
        <h1 className="text-3xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
          孔乙己长衫运势占卜
        </h1>
        <p className="text-lg text-gray-300 max-w-2xl">
          通过玄学测试，揭示你身上无形的"孔乙己长衫"是什么，并提供"脱下长衫"后的水逆退散运势与搞钱指南。
        </p>
      </header>

      <main className="max-w-4xl mx-auto">
        {!showResult ? (
          /* Form Section */
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-indigo-500/20 p-6 md:p-8 shadow-2xl shadow-indigo-900/20">
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-2 text-indigo-300">
                困住你的，究竟是哪件"孔乙己的长衫"？
              </h2>
              <p className="text-gray-400">
                高学历但感到怀才不遇？在理想与现实间挣扎？让我们用玄学为你揭示真相。
              </p>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  学历背景 *
                </label>
                <input
                  type="text"
                  value={education}
                  onChange={(e) => setEducation(e.target.value)}
                  placeholder="例如：985本科、海外硕士、博士..."
                  className="w-full px-4 py-3 bg-gray-900/70 border border-indigo-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all placeholder-gray-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  所学专业 *
                </label>
                <input
                  type="text"
                  value={major}
                  onChange={(e) => setMajor(e.target.value)}
                  placeholder="例如：计算机科学、金融、文学、哲学..."
                  className="w-full px-4 py-3 bg-gray-900/70 border border-indigo-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all placeholder-gray-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  近期困扰（选填）
                </label>
                <textarea
                  value={frustration}
                  onChange={(e) => setFrustration(e.target.value)}
                  placeholder="最近让你感到迷茫或困扰的事情..."
                  rows={3}
                  className="w-full px-4 py-3 bg-gray-900/70 border border-indigo-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all placeholder-gray-500 resize-none"
                />
              </div>
              
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-4 px-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-indigo-900/30"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    正在召唤玄学力量...
                  </span>
                ) : (
                  '🔮 立即占卜运势'
                )}
              </button>
            </form>
            
            <p className="text-sm text-gray-500 text-center mt-6">
              你的数据仅用于生成个性化运势，不会被存储或分享
            </p>
          </div>
        ) : (
          /* Result Section */
          <div className="space-y-8">
            <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-indigo-500/20 p-6 md:p-8 shadow-2xl shadow-indigo-900/20">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold mb-2 text-indigo-300">
                    你的孔乙己长衫运势
                  </h2>
                  <p className="text-gray-400">
                    基于你的学历、专业和困扰生成的专属解读
                  </p>
                </div>
                <button
                  onClick={handleReset}
                  className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                >
                  重新测试
                </button>
              </div>
              
              <div className="min-h-[400px] bg-gray-900/50 rounded-xl p-6 border border-indigo-500/10">
                {isTyping ? (
                  <Typewriter
                    ref={typewriterRef}
                    text={result}
                    speed={50}
                    onProgress={handleTypewriterProgress}
                    className="text-lg leading-relaxed text-gray-200 font-serif"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="w-16 h-16 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-4"></div>
                      <p className="text-gray-400">正在准备你的运势解读...</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            {/* Paywall Overlay */}
            {showPaywall && (
              <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                <div className="bg-gradient-to-br from-gray-900 to-indigo-950 rounded-2xl border-2 border-indigo-500 p-8 max-w-md w-full shadow-2xl shadow-indigo-900/50">
                  <div className="text-center mb-6">
                    <div className="w-20 h-20 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-3xl">🔒</span>
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">
                      解锁完整运势
                    </h3>
                    <p className="text-gray-300">
                      在揭晓你"脱下长衫"后的具体天命职业和未来三个月财运走势图时
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    <button
                      onClick={handlePay}
                      className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 rounded-xl font-bold text-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-emerald-900/30 flex items-center justify-center"
                    >
                      <span className="mr-2">💰</span>
                      微信支付 9.9 元解锁
                    </button>
                    
                    <button
                      onClick={() => {
                        setShowPaywall(false);
                        typewriterRef.current?.resume();
                      }}
                      className="w-full py-3 bg-gray-800 hover:bg-gray-700 rounded-xl font-medium transition-colors"
                    >
                      稍后再说
                    </button>
                  </div>
                  
                  <p className="text-xs text-gray-500 text-center mt-6">
                    支付后立即解锁完整运势，支持7天无理由退款
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="max-w-4xl mx-auto mt-12 pt-8 border-t border-gray-800">
        <p className="text-center text-gray-500 text-sm">
          本测试仅供娱乐，命运掌握在自己手中。脱下长衫，勇敢前行！
        </p>
      </footer>
    </div>
  );
}