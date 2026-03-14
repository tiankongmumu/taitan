```tsx
"use client";

import { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import Link from 'next/link';

// Fixed Typewriter component with proper ref forwarding
interface TypewriterMethods {
  pause: () => void;
  resume: () => void;
}

interface TypewriterProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
  onProgress?: (progress: number, displayedText: string) => void;
  className?: string;
}

const Typewriter = forwardRef<TypewriterMethods, TypewriterProps>(({
  text,
  speed = 50,
  onComplete,
  onProgress,
  className = ""
}, ref) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const pauseTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Reset when text changes
  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
    setIsPaused(false);
    if (pauseTimerRef.current) {
      clearTimeout(pauseTimerRef.current);
    }
  }, [text]);

  // Typewriter effect
  useEffect(() => {
    if (currentIndex >= text.length || isPaused) {
      if (currentIndex >= text.length && onComplete) {
        onComplete();
      }
      return;
    }

    pauseTimerRef.current = setTimeout(() => {
      const nextIndex = currentIndex + 1;
      const newText = text.substring(0, nextIndex);
      setDisplayedText(newText);
      setCurrentIndex(nextIndex);
      
      if (onProgress) {
        const progress = nextIndex / text.length;
        onProgress(progress, newText);
      }
    }, speed);

    return () => {
      if (pauseTimerRef.current) {
        clearTimeout(pauseTimerRef.current);
      }
    };
  }, [currentIndex, text, speed, isPaused, onComplete, onProgress]);

  // Expose methods via ref
  useImperativeHandle(ref, () => ({
    pause: () => {
      setIsPaused(true);
      if (pauseTimerRef.current) {
        clearTimeout(pauseTimerRef.current);
      }
    },
    resume: () => {
      setIsPaused(false);
    }
  }));

  return <div className={className}>{displayedText}</div>;
});

Typewriter.displayName = 'Typewriter';

export default function OraclePage() {
  // Form state
  const [mbti, setMbti] = useState('');
  const [recentBadLuck, setRecentBadLuck] = useState('');
  const [currentRole, setCurrentRole] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Result and typewriter state
  const [result, setResult] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [hasTriggeredPaywall, setHasTriggeredPaywall] = useState(false);
  const typewriterRef = useRef<TypewriterMethods>(null);
  
  // Proposal data
  const proposal = {
    id: "rage-escape",
    name: "发疯文学职场逃生舱",
    description: "通过分析你的MBTI和近期压力，生成专属的“发疯文学”辞职信和体制内/外逃生路线图。",
    target_audience: "精神内耗严重、渴望逃离“打工人”或“体制内”困境的年轻白领",
    hook_question: "你的精神状态，离“发疯”辞职还差几步？",
    paywall_trigger: "在生成最解压的“发疯文学”辞职信全文和最佳“搞钱”副业推荐前",
    theme_color: "fuchsia"
  };

  // MBTI options
  const mbtiOptions = [
    'INTJ', 'INTP', 'ENTJ', 'ENTP',
    'INFJ', 'INFP', 'ENFJ', 'ENFP',
    'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
    'ISTP', 'ISFP', 'ESTP', 'ESFP'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mbti || !recentBadLuck) return;
    
    setIsLoading(true);
    setResult('');
    setHasTriggeredPaywall(false);
    setShowPaywall(false);
    
    try {
      const response = await fetch('/api/rage-escape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mbti,
          recent_bad_luck: recentBadLuck,
          current_role: currentRole || undefined,
        }),
      });
      
      const data = await response.json();
      
      if (data.error) {
        alert(`错误: ${data.error}`);
        return;
      }
      
      setResult(data.script);
      setIsTyping(true);
    } catch (error) {
      console.error('提交失败:', error);
      alert('生成失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePay = () => {
    alert('测试版：模拟支付成功');
    setShowPaywall(false);
    typewriterRef.current?.resume();
  };

  const handleTypewriterProgress = (progress: number, displayedText: string) => {
    // Check if the displayed text contains the exact paywall trigger phrase
    if (!hasTriggeredPaywall && displayedText.includes(proposal.paywall_trigger)) {
      setHasTriggeredPaywall(true);
      typewriterRef.current?.pause();
      setShowPaywall(true);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-4 md:p-8">
      {/* Header */}
      <header className="max-w-4xl mx-auto mb-8 md:mb-12">
        <Link 
          href="/" 
          className="inline-flex items-center gap-2 text-fuchsia-400 hover:text-fuchsia-300 transition-colors mb-6"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回首页
        </Link>
        
        <h1 className="text-3xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-fuchsia-500 to-purple-600 bg-clip-text text-transparent">
          {proposal.name}
        </h1>
        <p className="text-gray-300 text-lg md:text-xl">
          {proposal.hook_question}
        </p>
      </header>

      <main className="max-w-4xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Form */}
          <div className="space-y-6">
            <div className="bg-gray-900/50 backdrop-blur-sm border border-fuchsia-500/20 rounded-2xl p-6 md:p-8">
              <h2 className="text-2xl font-bold mb-6 text-fuchsia-300">输入你的信息</h2>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* MBTI Select */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    MBTI 类型 <span className="text-fuchsia-400">*</span>
                  </label>
                  <select
                    value={mbti}
                    onChange={(e) => setMbti(e.target.value)}
                    className="w-full bg-gray-800 border border-fuchsia-500/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent transition-all"
                    required
                  >
                    <option value="">选择你的MBTI类型</option>
                    {mbtiOptions.map((type) => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                {/* Recent Bad Luck */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    近期压力/倒霉事 <span className="text-fuchsia-400">*</span>
                  </label>
                  <textarea
                    value={recentBadLuck}
                    onChange={(e) => setRecentBadLuck(e.target.value)}
                    placeholder="最近工作上遇到了什么糟心事？比如：老板PUA、同事甩锅、项目延期..."
                    className="w-full h-32 bg-gray-800 border border-fuchsia-500/30 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent transition-all resize-none"
                    required
                  />
                </div>

                {/* Current Role */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    当前角色（可选）
                  </label>
                  <input
                    type="text"
                    value={currentRole}
                    onChange={(e) => setCurrentRole(e.target.value)}
                    placeholder="例如：互联网大厂程序员、体制内公务员、外企打工人..."
                    className="w-full bg-gray-800 border border-fuchsia-500/30 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent transition-all"
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isLoading || !mbti || !recentBadLuck}
                  className="w-full bg-gradient-to-r from-fuchsia-600 to-purple-700 hover:from-fuchsia-700 hover:to-purple-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-fuchsia-500/20"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      生成中...
                    </span>
                  ) : (
                    '生成我的发疯文学逃生路线'
                  )}
                </button>
              </form>
            </div>

            {/* Info Box */}
            <div className="bg-gray-900/30 border border-fuchsia-500/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-3 text-fuchsia-300">✨ 这是什么？</h3>
              <p className="text-gray-300 text-sm leading-relaxed">
                {proposal.description}
                专为{proposal.target_audience}设计。
              </p>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            <div className="bg-gray-900/50 backdrop-blur-sm border border-fuchsia-500/20 rounded-2xl p-6 md:p-8 h-full">
              <h2 className="text-2xl font-bold mb-6 text-fuchsia-300">你的专属逃生脚本</h2>
              
              <div className="min-h-[400px]">
                {result ? (
                  <div className="relative">
                    <div className="bg-gray-800/50 border border-fuchsia-500/20 rounded-xl p-6 min-h-[400px]">
                      <Typewriter
                        ref={typewriterRef}
                        text={result}
                        speed={50}
                        onComplete={() => setIsTyping(false)}
                        onProgress={handleTypewriterProgress}
                        className="text-gray-200 leading-relaxed whitespace-pre-wrap font-mono text-sm md:text-base"
                      />
                      
                      {isTyping && (
                        <div className="flex items-center gap-2 mt-4 text-fuchsia-400 text-sm">
                          <div className="flex gap-1">
                            <div className="w-2 h-2 bg-fuchsia-400 rounded-full animate-pulse"></div>
                            <div className="w-2 h-2 bg-fuchsia-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                            <div className="w-2 h-2 bg-fuchsia-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                          </div>
                          <span>AI正在创作中...</span>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-[400px] text-gray-500 border-2 border-dashed border-fuchsia-500/20 rounded-xl p-8">
                    <div className="w-16 h-16 mb-4 text-fuchsia-500/30">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <p className="text-center mb-2">填写左侧信息</p>
                    <p className="text-center text-sm">生成你的专属发疯文学逃生路线</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Paywall Overlay */}
      {showPaywall && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gradient-to-br from-gray-900 to-black border-2 border-fuchsia-500 rounded-2xl max-w-md w-full p-8 relative overflow-hidden">
            {/* Glow effect */}
            <div className="absolute -top-20 -right-20 w-40 h-40 bg-fuchsia-500/10 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl"></div>
            
            <div className="relative z-10">
              <div className="text-center mb-8">
                <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-fuchsia-500 to-purple-600 rounded-2xl flex items-center justify-center">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">解锁完整内容</h3>
                <p className="text-gray-300">
                  {proposal.paywall_trigger}
                </p>
              </div>
              
              <div className="space-y-6">
                <div className="bg-gray-800/50 rounded-xl p-6 text-center">
                  <div className="text-4xl font-bold text-fuchsia-300 mb-2">9.9 元</div>
                  <div className="text-gray-400 text-sm">解锁完整逃生路线图</div>
                </div>
                
                <button
                  onClick={handlePay}
                  className="w-full bg-gradient-to-r from-fuchsia-600 to-purple-700 hover:from-fuchsia-700 hover:to-purple-800 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-fuchsia-500/30 flex items-center justify-center gap-3"
                >
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2