"use client";

import { useState, useEffect, useRef, ChangeEvent, DragEvent } from "react";

const WORKER_URL = "https://codemint-idphoto.lllhhh1130.workers.dev";

interface Size {
  w: number;
  h: number;
  name: string;
}

interface Color {
  hex: string;
  name: string;
}

const colorMap: Record<string, string> = {
  "#FFFFFF": "白色",
  "#438EDB": "蓝色",
  "#D93A3A": "红色",
  "#E8E8E8": "浅灰",
  "#67C23A": "绿色",
};

const sizes: Size[] = [
  { w: 295, h: 413, name: "一寸 (25×35mm)" },
  { w: 413, h: 579, name: "二寸 (35×49mm)" },
  { w: 390, h: 567, name: "小二寸 (33×48mm)" },
  { w: 472, h: 649, name: "护照 (40×55mm)" },
  { w: 600, h: 600, name: "社交头像 (正方形)" },
  { w: 358, h: 441, name: "驾照 (22×32mm)" },
];

const colors: Color[] = [
  { hex: "#FFFFFF", name: "白色" },
  { hex: "#438EDB", name: "蓝色" },
  { hex: "#D93A3A", name: "红色" },
  { hex: "#E8E8E8", name: "浅灰" },
  { hex: "#67C23A", name: "绿色" },
];

export default function ToolPage() {
  const [bgRemovalReady, setBgRemovalReady] = useState(false);
  const [removeBackground, setRemoveBackground] = useState<any>(null);
  const [savedCode, setSavedCode] = useState<string>("");
  const [originalImage, setOriginalImage] = useState<HTMLImageElement | null>(null);
  const [processedImage, setProcessedImage] = useState<HTMLImageElement | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentSize, setCurrentSize] = useState<Size>(sizes[0]);
  const [currentColor, setCurrentColor] = useState<string>("#FFFFFF");
  const [dropZoneHover, setDropZoneHover] = useState(false);
  const [dropZoneContent, setDropZoneContent] = useState<{
    emoji: string;
    text: string;
    subtext: string;
  }>({
    emoji: "📸",
    text: "点击上传或拖拽照片到这里",
    subtext: "支持 JPG、PNG 格式，建议正面免冠照",
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const previewCanvasRef = useRef<HTMLCanvasElement>(null);
  const vipBadgeRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const loadBgRemoval = async () => {
      try {
        // @ts-ignore
        const module = await import("https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.5.5/+esm");
        setRemoveBackground(module.default || module.removeBackground);
        setBgRemovalReady(true);
        console.log("✅ AI抠图引擎加载完成");
      } catch (e) {
        console.warn("AI抠图引擎加载失败, 将使用普通模式:", e);
      }
    };
    loadBgRemoval();
  }, []);

  const handleFile = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      alert("请上传图片文件 (JPG/PNG)");
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      const img = new Image();
      img.onload = async () => {
        setOriginalImage(img);
        setProcessedImage(null);

        setDropZoneContent({
          emoji: "⚙️",
          text: "AI 正在抠图中...",
          subtext: "首次加载模型可能需要30秒",
        });

        if (bgRemovalReady && removeBackground) {
          try {
            setIsProcessing(true);
            const blob = await (await fetch(e.target?.result as string)).blob();
            const result = await removeBackground(blob, {
              output: { format: "image/png" },
            });
            const url = URL.createObjectURL(result);
            const transparentImg = new Image();
            transparentImg.onload = () => {
              setProcessedImage(transparentImg);
              setIsProcessing(false);
              renderPreview();
              setDropZoneContent({
                emoji: "",
                text: "✅ AI抠图完成！背景已移除",
                subtext: "点击可重新选择照片",
              });
            };
            transparentImg.src = url;
            return;
          } catch (err) {
            console.warn("AI抠图失败, 使用普通模式:", err);
            setIsProcessing(false);
          }
        }

        renderPreview();
        setDropZoneContent({
          emoji: "",
          text: "✅ 照片已上传",
          subtext: "⚠️ AI抠图未就绪，建议上传透明背景照片",
        });
      };
      img.src = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  };

  const renderPreview = () => {
    if (!originalImage || !previewCanvasRef.current) return;

    const canvas = previewCanvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const targetW = currentSize.w;
    const targetH = currentSize.h;
    const ratio = targetW / targetH;

    canvas.width = targetW;
    canvas.height = targetH;

    ctx.fillStyle = currentColor;
    ctx.fillRect(0, 0, targetW, targetH);

    const imgRatio = originalImage.width / originalImage.height;
    let sx, sy, sw, sh;

    if (imgRatio > ratio) {
      sh = originalImage.height;
      sw = sh * ratio;
      sx = (originalImage.width - sw) / 2;
      sy = 0;
    } else {
      sw = originalImage.width;
      sh = sw / ratio;
      sx = 0;
      sy = originalImage.height * 0.05;
    }

    const drawImg = processedImage || originalImage;
    ctx.drawImage(drawImg, sx, sy, sw, sh, 0, 0, targetW, targetH);

    if (!savedCode) {
      ctx.save();
      ctx.globalAlpha = 0.15;
      ctx.fillStyle = "#000";
      ctx.font = "bold 16px sans-serif";
      ctx.textAlign = "center";
      ctx.translate(targetW / 2, targetH / 2);
      ctx.rotate(-Math.PI / 6);
      ctx.fillText("CodeMint 证件照", 0, 0);
      ctx.fillText("激活后去水印", 0, 24);
      ctx.restore();
    }
  };

  useEffect(() => {
    renderPreview();
  }, [originalImage, processedImage, currentSize, currentColor, savedCode]);

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDropZoneHover(false);
    if (e.dataTransfer.files.length) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDropZoneHover(true);
  };

  const handleDragLeave = () => {
    setDropZoneHover(false);
  };

  const handleDownload = () => {
    if (!originalImage) {
      alert("请先上传照片");
      return;
    }

    const hiResCanvas = document.createElement("canvas");
    const scale = 3;
    hiResCanvas.width = currentSize.w * scale;
    hiResCanvas.height = currentSize.h * scale;
    const hiCtx = hiResCanvas.getContext("2d");
    if (!hiCtx) return;

    hiCtx.fillStyle = currentColor;
    hiCtx.fillRect(0, 0, hiResCanvas.width, hiResCanvas.height);

    const targetW = currentSize.w * scale;
    const targetH = currentSize.h * scale;
    const ratio = targetW / targetH;
    const imgRatio = originalImage.width / originalImage.height;
    let sx, sy, sw, sh;
    if (imgRatio > ratio) {
      sh = originalImage.height;
      sw = sh * ratio;
      sx = (originalImage.width - sw) / 2;
      sy = 0;
    } else {
      sw = originalImage.width;
      sh = sw / ratio;
      sx = 0;
      sy = originalImage.height * 0.05;
    }
    const drawImg = processedImage || originalImage;
    hiCtx.drawImage(drawImg, sx, sy, sw, sh, 0, 0, targetW, targetH);

    const link = document.createElement("a");
    link.download = `CodeMint_证件照_${currentSize.name.replace(/\s/g, "")}.png`;
    link.href = hiResCanvas.toDataURL("image/png");
    link.click();
  };

  const handleReset = () => {
    setOriginalImage(null);
    setProcessedImage(null);
    setDropZoneContent({
      emoji: "📸",
      text: "点击上传或拖拽照片到这里",
      subtext: "支持 JPG、PNG 格式，建议正面免冠照",
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="bg-slate-950 text-white min-h-screen">
      <style dangerouslySetInnerHTML={{
        __html: `
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .fade-in {
          animation: fadeIn 0.5s ease-out;
        }
        @keyframes pulse-glow {
          0%, 100% {
            box-shadow: 0 0 5px rgba(168, 85, 247, 0.5);
          }
          50% {
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.8);
          }
        }
        .glow {
          animation: pulse-glow 2s infinite;
        }
        .size-btn.active {
          background: linear-gradient(135deg, #7c3aed, #a855f7);
          color: white;
        }
        .color-btn.active {
          --tw-ring-color: white;
          --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
          --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(3px + var(--tw-ring-offset-width)) var(--tw-ring-color);
          box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
          transform: scale(1.1);
        }
        .blur-paywall {
          filter: blur(8px);
          pointer-events: none;
          user-select: none;
        }
      `}} />

      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-400 rounded-xl flex items-center justify-center text-xl">
              📷
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 to-pink-300 bg-clip-text text-transparent">
                AI证件照制作
              </h1>
              <p className="text-xs text-slate-500">照片不上传服务器 · 隐私100%安全</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800 mb-6">
          <h2 className="text-xl font-bold mb-4">第一步：上传你的照片</h2>
          <div
            id="dropZone"
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${dropZoneHover ? "border-purple-500" : "border-slate-700"
              }`}
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            {dropZoneContent.emoji && <div className="text-4xl mb-3">{dropZoneContent.emoji}</div>}
            <p className="text-slate-400 mb-2">{dropZoneContent.text}</p>
            <p className="text-slate-600 text-sm">{dropZoneContent.subtext}</p>
            <input
              id="fileInput"
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileInputChange}
            />
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800">
            <h3 className="font-bold mb-3">第二步：选择证件照尺寸</h3>
            <div className="grid grid-cols-2 gap-2" id="sizeSelector">
              {sizes.map((size, idx) => (
                <button
                  key={idx}
                  className={`size-btn rounded-lg px-3 py-2 text-sm hover:bg-slate-700 transition-all ${currentSize.w === size.w && currentSize.h === size.h
                    ? "active"
                    : "bg-slate-800"
                    }`}
                  onClick={() => setCurrentSize(size)}
                  data-w={size.w}
                  data-h={size.h}
                  data-name={size.name}
                >
                  {size.name.split(" ")[0]}
                  <br />
                  <span className="text-xs text-slate-400">{size.name.split(" ")[1]}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800">
            <h3 className="font-bold mb-3">第三步：选择背景颜色</h3>
            <div className="flex gap-3 mb-4" id="colorSelector">
              {colors.map((color, idx) => (
                <button
                  key={idx}
                  className={`color-btn w-12 h-12 rounded-full border-4 hover:scale-110 transition-all ${currentColor === color.hex ? "active border-white" : "border-white/30"
                    }`}
                  onClick={() => setCurrentColor(color.hex)}
                  data-color={color.hex}
                  title={color.name}
                  style={{ background: color.hex }}
                />
              ))}
            </div>
            <p id="colorName" className="text-slate-400 text-sm">
              当前：{colorMap[currentColor] || currentColor}背景
            </p>
            <div className="mt-4 p-3 bg-slate-800/50 rounded-lg">
              <p className="text-xs text-slate-500">💡 小贴士：</p>
              <p className="text-xs text-slate-500">· 简历/求职 → 白色或蓝色</p>
              <p className="text-xs text-slate-500">· 护照/签证 → 白色</p>
              <p className="text-xs text-slate-500">· 身份证/结婚证 → 白色</p>
              <p className="text-xs text-slate-500">· 驾照/社保 → 白色或红色</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold">预览效果</h3>
            <div className="flex gap-2">
              <button
                id="resetBtn"
                onClick={handleReset}
                className={`bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm transition-all ${!originalImage ? "hidden" : ""
                  }`}
              >
                重新调整
              </button>
              <button
                id="downloadBtn"
                onClick={handleDownload}
                disabled={!originalImage}
                className="bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-500 hover:to-pink-400 text-white font-bold px-6 py-2 rounded-lg text-sm transition-all glow disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下载高清证件照
              </button>
            </div>
          </div>
          <div
            id="previewArea"
            className="flex items-center justify-center min-h-[300px] relative"
          >
            {!originalImage && (
              <div id="emptyState" className="text-center">
                <div className="text-6xl mb-4 opacity-30">🖼️</div>
                <p className="text-slate-600">上传照片后，这里会显示预览效果</p>
              </div>
            )}
            <canvas
              id="previewCanvas"
              ref={previewCanvasRef}
              className={`max-h-[400px] rounded-lg shadow-2xl ${!originalImage ? "hidden" : ""
                }`}
            ></canvas>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-4 mt-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 fade-in">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-rose-500 rounded-full flex items-center justify-center text-sm font-bold">
                陈
              </div>
              <div>
                <p className="font-bold text-sm">陈同学</p>
                <p className="text-slate-500 text-xs">大四应届生 · 武汉</p>
              </div>
            </div>
            <p className="text-slate-400 text-sm">
              "投简历要证件照，去照相馆一张要40块还得排队。这个工具9.9无限次用，自己在家拍完直接出片，背景颜色随便换！"
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 fade-in">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-sm font-bold">
                李
              </div>
              <div>
                <p className="font-bold text-sm">李姐</p>
                <p className="text-slate-500 text-xs">HR · 北京</p>
              </div>
            </div>
            <p className="text-slate-400 text-sm">
              "给新员工做工牌，以前还得让他们专门去拍。现在随便拿张照片往里一扔，一寸二寸随便切，省了不少事。"
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 fade-in">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-full flex items-center justify-center text-sm font-bold">
                王
              </div>
              <div>
                <p className="font-bold text-sm">王先生</p>
                <p className="text-slate-500 text-xs">办签证 · 上海</p>
              </div>
            </div>
            <p className="text-slate-400 text-sm">
              "办签证要白底照片，之前拍的是蓝底。用这个工具直接换了个背景色，5秒搞定，不用重新去拍了。"
            </p>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-4 mt-8">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-2xl mb-2">🔒</div>
            <h4 className="font-bold text-sm mb-1">隐私安全</h4>
            <p className="text-slate-500 text-xs">
              照片不上传服务器
              <br />
              全部本地处理
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-2xl mb-2">⚡</div>
            <h4 className="font-bold text-sm mb-1">秒速出片</h4>
            <p className="text-slate-500 text-xs">
              上传即预览
              <br />
              无需等待
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-2xl mb-2">🎨</div>
            <h4 className="font-bold text-sm mb-1">5种背景色</h4>
            <p className="text-slate-500 text-xs">
              白/蓝/红/灰/绿
              <br />
              一键切换
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-2xl mb-2">📐</div>
            <h4 className="font-bold text-sm mb-1">6种标准尺寸</h4>
            <p className="text-slate-500 text-xs">
              一寸/二寸/护照
              <br />
              驾照/社交头像
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-800 py-6 mt-12 text-center text-slate-600 text-sm">
        <p>CodeMint Tools © 2026 | 你的照片不会上传到任何服务器，请放心使用</p>
      </footer>
    </div>
  );
}