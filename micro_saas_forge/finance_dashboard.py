import sqlite3
import json
import webbrowser
import os
from datetime import datetime

DB_PATH = "titan_orders.db"
OUTPUT_HTML = "titan_dashboard.html"

def fetch_data():
    if not os.path.exists(DB_PATH):
        return None
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有订单
    cursor.execute("SELECT id, original_price, cost_price, proxy_price, status, profit, create_time FROM orders ORDER BY create_time DESC")
    rows = cursor.fetchall()
    
    orders = []
    total_revenue = 0.0
    total_profit = 0.0
    completed_orders = 0
    
    for row in rows:
        status = row[4]
        profit = row[5] or 0.0
        
        orders.append({
            "id": row[0],
            "original_price": row[1],
            "cost_price": row[2],
            "proxy_price": row[3],
            "status": status,
            "profit": profit,
            "create_time": datetime.fromtimestamp(row[6]).strftime('%Y-%m-%d %H:%M:%S')
        })
        
        if status == "COMPLETED":
            completed_orders += 1
            total_revenue += row[3] # 营业额 = proxy_price
            total_profit += profit
            
    conn.close()
    
    return {
        "orders": orders,
        "metrics": {
            "total_orders": len(orders),
            "completed_orders": completed_orders,
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "profit_margin": round((total_profit / total_revenue * 100) if total_revenue > 0 else 0, 1)
        }
    }

def generate_html(data):
    metrics = data["metrics"]
    orders_json = json.dumps(data["orders"])
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Titan 商业化数据看板 (v2.0)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }}
        .glass-panel {{
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
        }}
        .metric-card {{
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.2);
        }}
        /* 自定义滚动条 */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0f172a; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    </style>
</head>
<body class="min-h-screen p-4 md:p-8">

    <!-- Header -->
    <header class="flex justify-between items-center mb-8">
        <div class="flex items-center gap-3">
            <div class="h-10 w-10 rounded-full bg-gradient-to-tr from-cyan-400 to-blue-500 flex items-center justify-center shadow-[0_0_15px_rgba(56,189,248,0.5)]">
                <i class="fas fa-rocket text-white"></i>
            </div>
            <h1 class="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-400">
                Titan Commercial Dashboard
            </h1>
        </div>
        <div class="text-sm text-slate-400">
            <i class="fas fa-clock mr-1"></i> Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </header>

    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Metric 1 -->
        <div class="glass-panel p-6 metric-card">
            <div class="flex justify-between items-start mb-4">
                <div class="text-slate-400 text-sm font-medium">总流水 (Revenue)</div>
                <div class="p-2 bg-blue-500/10 rounded-lg"><i class="fas fa-wallet text-blue-400"></i></div>
            </div>
            <div class="text-3xl font-bold">¥{metrics['total_revenue']}</div>
            <div class="mt-2 text-sm text-emerald-400 flex items-center gap-1">
                <i class="fas fa-arrow-trend-up"></i> Real-time
            </div>
        </div>
        
        <!-- Metric 2 -->
        <div class="glass-panel p-6 metric-card">
            <div class="flex justify-between items-start mb-4">
                <div class="text-slate-400 text-sm font-medium">净利润 (Net Profit)</div>
                <div class="p-2 bg-emerald-500/10 rounded-lg"><i class="fas fa-chart-line text-emerald-400"></i></div>
            </div>
            <div class="text-3xl font-bold text-emerald-400">¥{metrics['total_profit']}</div>
            <div class="mt-2 text-sm text-slate-400">Profit Margin: <span class="text-emerald-400 font-semibold">{metrics['profit_margin']}%</span></div>
        </div>

        <!-- Metric 3 -->
        <div class="glass-panel p-6 metric-card">
            <div class="flex justify-between items-start mb-4">
                <div class="text-slate-400 text-sm font-medium">成单数 (Completed)</div>
                <div class="p-2 bg-purple-500/10 rounded-lg"><i class="fas fa-check-circle text-purple-400"></i></div>
            </div>
            <div class="text-3xl font-bold">{metrics['completed_orders']}</div>
            <div class="mt-2 text-sm text-slate-400">Out of {metrics['total_orders']} total queries</div>
        </div>

        <!-- Metric 4 -->
        <div class="glass-panel p-6 metric-card">
            <div class="flex justify-between items-start mb-4">
                <div class="text-slate-400 text-sm font-medium">转化率 (Conversion)</div>
                <div class="p-2 bg-amber-500/10 rounded-lg"><i class="fas fa-bolt text-amber-400"></i></div>
            </div>
            <div class="text-3xl font-bold">{round((metrics['completed_orders'] / metrics['total_orders'] * 100) if metrics['total_orders'] > 0 else 0, 1)}%</div>
            <div class="mt-2 text-sm text-slate-400">Inquiry to payment</div>
        </div>
    </div>

    <!-- Main Content Area -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Order Table -->
        <div class="glass-panel col-span-1 lg:col-span-2 p-6 flex flex-col h-[500px]">
            <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
                <i class="fas fa-list text-cyan-400"></i> 最新交易流水 (Ledger)
            </h2>
            <div class="overflow-auto flex-1">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="text-slate-400 text-sm border-b border-white/10 sticky top-0 bg-[#1e293bf2] backdrop-blur z-10">
                            <th class="pb-3 px-4 font-medium">订单ID</th>
                            <th class="pb-3 px-4 font-medium">时间</th>
                            <th class="pb-3 px-4 font-medium">原价/成本/代下价</th>
                            <th class="pb-3 px-4 font-medium">利润</th>
                            <th class="pb-3 px-4 font-medium text-right">状态</th>
                        </tr>
                    </thead>
                    <tbody id="table-body" class="text-sm">
                        <!-- JS renders here -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Profit Chart -->
        <div class="glass-panel col-span-1 p-6 flex flex-col h-[500px]">
             <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
                <i class="fas fa-chart-pie text-cyan-400"></i> 订单转化漏斗
            </h2>
            <div class="flex-1 relative flex items-center justify-center">
                <canvas id="profitChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        const ordersData = {orders_json};
        
        // Render Table
        const tbody = document.getElementById('table-body');
        let rowsHtml = '';
        
        const statusColors = {{
            'COMPLETED': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
            'PENDING_PAY': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
            'PROCESSING': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
            'CANCELLED': 'bg-slate-500/20 text-slate-400 border-slate-500/30',
            'FAILED': 'bg-red-500/20 text-red-400 border-red-500/30'
        }};

        ordersData.forEach(o => {{
            const badgeClass = statusColors[o.status] || statusColors['CANCELLED'];
            const profitHtml = o.profit > 0 ? `<span class="text-emerald-400 font-medium">+¥${{o.profit}}</span>` : `<span class="text-slate-500">-</span>`;
            
            rowsHtml += `
            <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="py-3 px-4 font-mono text-xs text-slate-300">${{o.id}}</td>
                <td class="py-3 px-4 text-slate-400">${{o.create_time.split(' ')[1]}}</td>
                <td class="py-3 px-4">¥${{o.original_price}} / ¥${{o.cost_price}} / <span class="text-cyan-400">¥${{o.proxy_price}}</span></td>
                <td class="py-3 px-4">${{profitHtml}}</td>
                <td class="py-3 px-4 text-right">
                    <span class="px-2 py-1 rounded-full text-xs border ${{badgeClass}}">${{o.status}}</span>
                </td>
            </tr>
            `;
        }});
        
        tbody.innerHTML = rowsHtml || '<tr><td colspan="5" class="text-center py-8 text-slate-500">暂无数据</td></tr>';

        // Render Chart
        const statuses = {{}};
        ordersData.forEach(o => {{
            statuses[o.status] = (statuses[o.status] || 0) + 1;
        }});

        const ctx = document.getElementById('profitChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(statuses),
                datasets: [{{
                    data: Object.values(statuses),
                    backgroundColor: [
                        '#10b981', // emerald
                        '#f59e0b', // amber
                        '#3b82f6', // blue
                        '#64748b', // slate
                        '#ef4444'  // red
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', padding: 20 }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return os.path.abspath(OUTPUT_HTML)

if __name__ == "__main__":
    db_data = fetch_data()
    if not db_data:
        print("未找到数据库 titan_orders.db，无法生成看板！")
    else:
        file_path = generate_html(db_data)
        print(f"✅ 看板生成成功！路径: {file_path}")
        print("正在自动打开浏览器...")
        webbrowser.open(f"file://{file_path}")
