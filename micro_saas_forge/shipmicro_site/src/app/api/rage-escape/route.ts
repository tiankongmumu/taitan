import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const apiKey = process.env.DEEPSEEK_API_KEY;
    if (!apiKey || apiKey.trim() === '') {
      return NextResponse.json(
        { error: 'API configuration error: DEEPSEEK_API_KEY is not properly configured' },
        { status: 500 }
      );
    }

    const body = await request.json();
    const { mbti, recent_bad_luck, current_role } = body;

    if (!mbti || !recent_bad_luck) {
      return NextResponse.json(
        { error: 'Missing required fields: mbti and recent_bad_luck are required' },
        { status: 400 }
      );
    }

    const proposal = {
      id: "rage-escape",
      name: "发疯文学职场逃生舱",
      description: "通过分析你的MBTI和近期压力，生成专属的“发疯文学”辞职信和体制内/外逃生路线图。",
      target_audience: "精神内耗严重、渴望逃离“打工人”或“体制内”困境的年轻白领",
      hook_question: "你的精神状态，离“发疯”辞职还差几步？",
      paywall_trigger: "在生成最解压的“发疯文学”辞职信全文和最佳“搞钱”副业推荐前",
      theme_color: "fuchsia"
    };

    const prompt = `你是一个"${proposal.name}"的AI助手。用户信息如下：
- MBTI类型: ${mbti}
- 近期压力/倒霉事: ${recent_bad_luck}
- 当前角色: ${current_role || '未指定'}

请根据以上信息，围绕这个核心问题生成一段"发疯文学"风格的职场逃生脚本：
"${proposal.hook_question}"

要求：
1. 结合用户的MBTI性格特点分析其职场困境
2. 融入"发疯文学"的夸张、情绪化、黑色幽默风格
3. 提供体制内/外的逃生路线图建议
4. 保持解压、治愈的基调，同时带有实用建议
5. 以第二人称"你"进行叙述，增强代入感
6. 重要：当你的生成内容到达"${proposal.paywall_trigger}"这个短语时，必须立即停止生成，不要生成这个短语之后的内容。这个短语就是付费墙触发点。

请生成500-800字左右的完整脚本，并在到达付费墙触发短语时准确停止。`;

    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          {
            role: 'system',
            content: '你是一个擅长创作"发疯文学"和职场心理分析的助手，风格幽默、夸张但富有洞察力。严格按照用户要求，在指定付费墙触发短语处停止生成。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.8,
        max_tokens: 1500
      })
    });

    if (!response.ok) {
      throw new Error(`DeepSeek API error: ${response.status}`);
    }

    const data = await response.json();
    let script = data.choices[0]?.message?.content || '';

    // Ensure the script stops at the paywall trigger
    const triggerIndex = script.indexOf(proposal.paywall_trigger);
    if (triggerIndex !== -1) {
      script = script.substring(0, triggerIndex);
    }

    return NextResponse.json({ script });

  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}