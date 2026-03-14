import { NextResponse } from 'next/server';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { name, zodiac, industry } = body;

        const prompt = `你是一个深谙国内职场内卷和玄学的“牛马转世判官”。语言风格：黑色幽默、极具网感（小红书/抖音风）、毒舌但精准痛点。
请根据以下用户信息，为TA生成一份极具传播爆款潜质的【前世打工狗（牛马）转世剧本】。

用户姓名：${name}
星座/生肖：${zodiac}
当前行业：${industry}

输出要求：
1. 剧本长度约 200 字。
2. 包含“前世死因”（比如在古代因为给皇上写PPT过劳死）。
3. 包含“今生宿命”（为什么这辈子还在${industry}里受苦）。
4. 结尾留一个极大的财运悬念或破局玄机（比如：“但你命盘中暗藏一道偏财符，唯有在今年XX时机……”）。
只输出剧本正文，不要输出任何多余的解释。`;

        const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.DEEPSEEK_API_KEY}`
            },
            body: JSON.stringify({
                model: 'deepseek-chat',
                messages: [{ role: 'user', content: prompt }],
                max_tokens: 500,
                temperature: 0.8
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        const script = data.choices[0].message.content;

        return NextResponse.json({ script });
    } catch (error: any) {
        console.error('Oracle API Error:', error);
        return NextResponse.json({ error: '天机不可泄露 (API Error)' }, { status: 500 });
    }
}
