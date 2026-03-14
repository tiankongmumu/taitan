import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { education, major, recent_frustration } = body;

    // Validate required inputs
    if (!education || !major) {
      return NextResponse.json(
        { error: 'Missing required fields: education and major are required' },
        { status: 400 }
      );
    }

    // Construct the prompt for DeepSeek
    const prompt = `你是一位玄学占卜大师，专门为高学历年轻人解读"孔乙己长衫"运势。
    
用户信息：
- 学历：${education}
- 专业：${major}
- 近期困扰：${recent_frustration || '未提供'}

请根据以上信息，回答这个核心问题："困住你的，究竟是哪件'孔乙己的长衫'？"

请按照以下结构生成回答：
1. 首先分析用户身上无形的"孔乙己长衫"是什么（结合学历、专业和困扰）
2. 描述这件"长衫"如何限制了用户的发展
3. 提供"脱下长衫"后的运势转变
4. 给出具体的"搞钱指南"和行动建议
5. 最后用一句鼓励的话结束

要求：
- 语言风格：神秘玄学感，但接地气，带点幽默
- 目标受众：95后、00后高学历年轻人
- 长度：300-400字左右
- 避免使用markdown格式，用纯文本`;

    // Call DeepSeek API
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.DEEPSEEK_API_KEY}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          {
            role: 'system',
            content: '你是一位精通中国传统文化和现代年轻人心理的玄学占卜师，擅长用幽默接地气的方式为高学历年轻人解读运势。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.8,
        max_tokens: 800
      })
    });

    if (!response.ok) {
      throw new Error(`DeepSeek API error: ${response.status}`);
    }

    const data = await response.json();
    const script = data.choices[0]?.message?.content || '';

    return NextResponse.json({ script });

  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Failed to generate fortune reading' },
      { status: 500 }
    );
  }
}