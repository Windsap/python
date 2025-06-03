import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import random
import numpy as np
import platform

# 配置matplotlib中文字体
def setup_chinese_font():
    """设置matplotlib中文字体"""
    system = platform.system()

    if system == "Darwin":  # macOS
        # 尝试常见的macOS中文字体
        chinese_fonts = [
            'PingFang SC',
            'Hiragino Sans GB',
            'STHeiti',
            'SimHei',
            'Arial Unicode MS'
        ]
    elif system == "Windows":
        # Windows中文字体
        chinese_fonts = [
            'SimHei',
            'Microsoft YaHei',
            'SimSun',
            'KaiTi'
        ]
    else:  # Linux
        chinese_fonts = [
            'WenQuanYi Micro Hei',
            'WenQuanYi Zen Hei',
            'Noto Sans CJK SC',
            'Source Han Sans CN'
        ]

    # 查找可用的中文字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    for font in chinese_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font]
            plt.rcParams['axes.unicode_minus'] = False
            print(f"使用字体: {font}")
            return

    # 如果没有找到中文字体，使用默认设置并警告
    print("警告: 未找到合适的中文字体，图表中文可能显示为方块")
    plt.rcParams['axes.unicode_minus'] = False

# 初始化中文字体
setup_chinese_font()

class EconomicSimulationGame:
    def __init__(self, root):
        self.root = root
        root.title("经济学模拟游戏")
        
        # 初始化游戏参数
        self.days = 0
        self.balance = 1000
        self.inventory = 0
        self.base_cost = 5
        self.current_price = 10
        self.tax_rate = 0.2
        self.interest_rate = 0.05
        self.money_supply = 1000
        self.gdp = 500
        self.unemployment = 0.05
        self.event_cooldown = 0

        # 历史数据追踪
        self.history = {
            'days': [],
            'gdp': [],
            'unemployment': [],
            'balance': [],
            'inflation': []
        }
        
        # 初始化历史数据
        self.record_history()

        # 创建UI
        self.create_ui()
        self.update_display()
        
    def create_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制面板
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # 图表区域
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, main_frame)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建标签页
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 市场供需平衡页
        market_frame = ttk.Frame(notebook, padding=10)
        notebook.add(market_frame, text="市场供需")
        
        ttk.Label(market_frame, text="设定价格:").pack()
        self.price_entry = ttk.Entry(market_frame)
        self.price_entry.pack(pady=5)
        self.price_entry.insert(0, "10")
        ttk.Button(market_frame, text="调整价格", command=self.set_price).pack(pady=5)
        
        # 货币政策页
        monetary_frame = ttk.Frame(notebook, padding=10)
        notebook.add(monetary_frame, text="货币政策")
        
        ttk.Label(monetary_frame, text="设定利率(%):").pack()
        self.interest_entry = ttk.Entry(monetary_frame)
        self.interest_entry.pack(pady=5)
        self.interest_entry.insert(0, "5")
        
        ttk.Label(monetary_frame, text="调整货币供应量:").pack()
        self.money_supply_entry = ttk.Entry(monetary_frame)
        self.money_supply_entry.pack(pady=5)
        self.money_supply_entry.insert(0, "1000")
        
        ttk.Button(monetary_frame, text="应用货币政策", 
                  command=self.apply_monetary_policy).pack(pady=5)
        
        # 税收与公共支出页
        fiscal_frame = ttk.Frame(notebook, padding=10)
        notebook.add(fiscal_frame, text="财政政策")
        
        ttk.Label(fiscal_frame, text="设定税率(%):").pack()
        self.tax_entry = ttk.Entry(fiscal_frame)
        self.tax_entry.pack(pady=5)
        self.tax_entry.insert(0, "20")
        
        ttk.Label(fiscal_frame, text="公共支出:").pack()
        self.spending_entry = ttk.Entry(fiscal_frame)
        self.spending_entry.pack(pady=5)
        self.spending_entry.insert(0, "200")
        
        ttk.Button(fiscal_frame, text="应用财政政策", 
                  command=self.apply_fiscal_policy).pack(pady=5)
        
        # 贸易政策页
        trade_frame = ttk.Frame(notebook, padding=10)
        notebook.add(trade_frame, text="贸易政策")
        
        ttk.Label(trade_frame, text="设定关税率(%):").pack()
        self.tariff_entry = ttk.Entry(trade_frame)
        self.tariff_entry.pack(pady=5)
        self.tariff_entry.insert(0, "10")
        
        self.trade_policy = tk.StringVar(value="balanced")
        ttk.Radiobutton(trade_frame, text="平衡贸易", value="balanced", 
                       variable=self.trade_policy).pack(anchor=tk.W)
        ttk.Radiobutton(trade_frame, text="促进出口", value="export", 
                       variable=self.trade_policy).pack(anchor=tk.W)
        ttk.Radiobutton(trade_frame, text="限制进口", value="import", 
                       variable=self.trade_policy).pack(anchor=tk.W)
        
        ttk.Button(trade_frame, text="应用贸易政策", 
                  command=self.apply_trade_policy).pack(pady=5)
        
        # 状态显示
        status_frame = ttk.LabelFrame(control_frame, text="经济状态", padding=10)
        status_frame.pack(pady=10, fill=tk.X)
        
        self.status_labels = {
            'day': ttk.Label(status_frame, text="天数: 0"),
            'balance': ttk.Label(status_frame, text="资金: $1000"),
            'gdp': ttk.Label(status_frame, text="GDP: $500"),
            'unemployment': ttk.Label(status_frame, text="失业率: 5%"),
            'inflation': ttk.Label(status_frame, text="通货膨胀率: 2%"),
            'interest': ttk.Label(status_frame, text="利率: 5%"),
            'tax': ttk.Label(status_frame, text="税率: 20%")
        }
        
        for label in self.status_labels.values():
            label.pack(anchor=tk.W)
        
        # 操作按钮
        ttk.Button(control_frame, text="进入下一天", command=self.next_day).pack(pady=10)
        ttk.Button(control_frame, text="显示帮助", command=self.show_help).pack(pady=5)
    
    def update_display(self):
        # 更新状态标签
        self.status_labels['day'].config(text=f"天数: {self.days}")
        self.status_labels['balance'].config(text=f"资金: ${self.balance:.2f}")
        self.status_labels['gdp'].config(text=f"GDP: ${self.gdp:.2f}")
        self.status_labels['unemployment'].config(text=f"失业率: {self.unemployment*100:.1f}%")
        
        # 计算通货膨胀率 (简化模型)
        inflation = 0.02 + (self.money_supply / 1000 - 1) * 0.05
        self.status_labels['inflation'].config(text=f"通货膨胀率: {inflation*100:.1f}%")
        
        self.status_labels['interest'].config(text=f"利率: {self.interest_rate*100:.1f}%")
        self.status_labels['tax'].config(text=f"税率: {self.tax_rate*100:.1f}%")
        
        # 更新图表
        self.update_chart()

    def update_chart(self):
        """更新经济指标图表"""
        self.ax.clear()

        if len(self.history['days']) > 0:
            # 绘制GDP趋势
            self.ax.plot(self.history['days'], self.history['gdp'],
                        label='GDP', color='green', marker='o', linewidth=2)

            # 绘制失业率趋势 (乘以100显示为百分比)
            unemployment_percent = [u * 100 for u in self.history['unemployment']]
            self.ax.plot(self.history['days'], unemployment_percent,
                        label='失业率(%)', color='red', marker='s', linewidth=2)

            # 绘制通胀率趋势
            self.ax.plot(self.history['days'], self.history['inflation'],
                        label='通胀率(%)', color='orange', marker='^', linewidth=2)

        self.ax.set_title("经济指标趋势图", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("天数")
        self.ax.set_ylabel("数值")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        # 设置图表样式
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.canvas.draw()

    def next_day(self):
        """进入下一天，更新经济状态"""
        self.days += 1

        # 计算经济指标变化
        self.calculate_economic_changes()

        # 处理随机事件
        self.handle_events()

        # 记录历史数据
        self.record_history()

        # 更新显示
        self.update_display()

        # 显示每日报告
        self.show_daily_report()

        # 检查游戏结束条件
        if self.balance < -1000:
            messagebox.showwarning("警告", "政府债务过高！请注意财政状况。")
        elif self.unemployment > 0.3:
            messagebox.showwarning("警告", "失业率过高！经济面临严重问题。")
        elif self.gdp < 100:
            messagebox.showerror("游戏结束", "经济完全崩溃！游戏结束。")
            self.root.quit()

    def record_history(self):
        """记录当前经济数据到历史记录"""
        self.history['days'].append(self.days)
        self.history['gdp'].append(self.gdp)
        self.history['unemployment'].append(self.unemployment)
        self.history['balance'].append(self.balance)

        # 计算通胀率
        inflation = 0.02 + (self.money_supply / 1000 - 1) * 0.05
        self.history['inflation'].append(inflation * 100)

        # 只保留最近30天的数据
        if len(self.history['days']) > 30:
            for key in self.history:
                self.history[key] = self.history[key][-30:]

    def set_price(self):
        try:
            new_price = float(self.price_entry.get())
            if new_price <= 0:
                messagebox.showerror("错误", "价格必须大于0")
                return
                
            old_price = self.current_price
            self.current_price = new_price
            
            # 价格变化对经济的影响
            price_change_ratio = new_price / old_price
            
            # 价格上涨导致需求下降，GDP下降，失业率上升
            if price_change_ratio > 1:
                self.gdp *= (1 - (price_change_ratio - 1) * 0.2)
                self.unemployment += (price_change_ratio - 1) * 0.01
            # 价格下降导致需求上升，GDP上升，失业率下降
            else:
                self.gdp *= (1 + (1 - price_change_ratio) * 0.1)
                self.unemployment = max(0.01, self.unemployment - (1 - price_change_ratio) * 0.005)
            
            messagebox.showinfo("价格调整", f"价格已从 ${old_price:.2f} 调整为 ${new_price:.2f}")
            self.update_display()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def apply_monetary_policy(self):
        try:
            new_interest_rate = float(self.interest_entry.get()) / 100
            new_money_supply = float(self.money_supply_entry.get())
            
            if new_interest_rate < 0:
                messagebox.showerror("错误", "利率不能为负")
                return
                
            if new_money_supply <= 0:
                messagebox.showerror("错误", "货币供应量必须大于0")
                return
            
            old_interest = self.interest_rate
            old_money_supply = self.money_supply
            
            self.interest_rate = new_interest_rate
            self.money_supply = new_money_supply
            
            # 利率上升导致投资减少，GDP下降，失业率上升
            interest_change = new_interest_rate - old_interest
            if interest_change > 0:
                self.gdp *= (1 - interest_change * 2)
                self.unemployment += interest_change * 0.1
            # 利率下降导致投资增加，GDP上升，失业率下降
            else:
                self.gdp *= (1 - interest_change)
                self.unemployment = max(0.01, self.unemployment + interest_change * 0.05)
            
            # 货币供应量变化影响通货膨胀
            money_supply_change = new_money_supply / old_money_supply
            if money_supply_change > 1:
                # 货币供应增加会短期刺激GDP
                self.gdp *= (1 + (money_supply_change - 1) * 0.1)
            
            messagebox.showinfo("货币政策", 
                              f"利率已从 {old_interest*100:.1f}% 调整为 {new_interest_rate*100:.1f}%\n"
                              f"货币供应量已从 ${old_money_supply:.2f} 调整为 ${new_money_supply:.2f}")
            
            self.update_display()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def apply_fiscal_policy(self):
        try:
            new_tax_rate = float(self.tax_entry.get()) / 100
            public_spending = float(self.spending_entry.get())
            
            if new_tax_rate < 0 or new_tax_rate > 1:
                messagebox.showerror("错误", "税率必须在0%到100%之间")
                return
                
            if public_spending < 0:
                messagebox.showerror("错误", "公共支出不能为负")
                return
            
            old_tax_rate = self.tax_rate
            self.tax_rate = new_tax_rate
            
            # 税率变化对经济的影响
            tax_change = new_tax_rate - old_tax_rate
            
            # 税率上升减少消费和投资，降低GDP，增加失业率
            if tax_change > 0:
                self.gdp *= (1 - tax_change * 0.5)
                self.unemployment += tax_change * 0.1
                self.balance += self.gdp * tax_change  # 增加政府收入
            # 税率下降增加消费和投资，提高GDP，减少失业率
            else:
                self.gdp *= (1 - tax_change * 0.3)
                self.unemployment = max(0.01, self.unemployment + tax_change * 0.05)
                self.balance += self.gdp * tax_change  # 减少政府收入
            
            # 公共支出对经济的影响
            self.balance -= public_spending  # 减少政府资金
            self.gdp += public_spending * 0.7  # 公共支出刺激GDP
            self.unemployment = max(0.01, self.unemployment - public_spending / self.gdp * 0.05)  # 减少失业率
            
            messagebox.showinfo("财政政策", 
                              f"税率已从 {old_tax_rate*100:.1f}% 调整为 {new_tax_rate*100:.1f}%\n"
                              f"公共支出: ${public_spending:.2f}")
            
            self.update_display()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def apply_trade_policy(self):
        try:
            tariff_rate = float(self.tariff_entry.get()) / 100
            trade_policy = self.trade_policy.get()
            
            if tariff_rate < 0 or tariff_rate > 1:
                messagebox.showerror("错误", "关税率必须在0%到100%之间")
                return
            
            # 关税对经济的影响
            # 高关税增加政府收入但可能损害贸易和GDP
            trade_impact = 0
            revenue_impact = 0
            
            if trade_policy == "balanced":
                # 平衡贸易政策
                trade_impact = -tariff_rate * 0.1
                revenue_impact = tariff_rate * 0.05 * self.gdp
            elif trade_policy == "export":
                # 促进出口政策
                trade_impact = 0.05 - tariff_rate * 0.15
                revenue_impact = tariff_rate * 0.03 * self.gdp
            elif trade_policy == "import":
                # 限制进口政策
                trade_impact = -tariff_rate * 0.2
                revenue_impact = tariff_rate * 0.08 * self.gdp
            
            # 应用影响
            self.gdp *= (1 + trade_impact)
            self.balance += revenue_impact
            
            # 贸易政策对失业率的影响
            if trade_impact > 0:
                self.unemployment = max(0.01, self.unemployment - 0.01)
            else:
                self.unemployment += 0.005
            
            messagebox.showinfo("贸易政策", 
                              f"关税率: {tariff_rate*100:.1f}%\n"
                              f"贸易政策: {trade_policy}")
            
            self.update_display()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def calculate_economic_changes(self):
        # 每天的自然经济变化
        
        # GDP自然增长 (受多种因素影响)
        gdp_growth = 0.01  # 基础增长率
        gdp_growth += (0.5 - self.unemployment) * 0.02  # 失业率影响
        gdp_growth -= self.interest_rate * 0.1  # 利率影响
        gdp_growth -= self.tax_rate * 0.05  # 税率影响
        gdp_growth += random.uniform(-0.01, 0.01)  # 随机波动
        
        self.gdp *= (1 + gdp_growth)
        
        # 失业率变化
        unemployment_change = random.uniform(-0.002, 0.002)  # 随机波动
        unemployment_change += (self.interest_rate - 0.05) * 0.01  # 利率影响
        unemployment_change += (self.tax_rate - 0.2) * 0.005  # 税率影响
        
        self.unemployment = max(0.01, min(0.5, self.unemployment + unemployment_change))
        
        # 政府资金变化 (税收收入)
        tax_revenue = self.gdp * self.tax_rate
        self.balance += tax_revenue
        
        # 利息支出 (简化模型)
        interest_expense = self.balance * -0.01 if self.balance < 0 else 0
        self.balance += interest_expense
    
    def handle_events(self):
        # 随机事件系统
        if self.event_cooldown > 0:
            self.event_cooldown -= 1
            return
            
        # 20%的概率触发随机事件
        if random.random() < 0.2:
            events = [
                {"name": "经济繁荣", "description": "经济突然繁荣，GDP增长！", 
                 "effects": {"gdp": 1.1, "unemployment": 0.9}},
                {"name": "经济衰退", "description": "经济陷入衰退，GDP下降！", 
                 "effects": {"gdp": 0.9, "unemployment": 1.1}},
                {"name": "国际贸易协定", "description": "签署了有利的国际贸易协定，出口增加！", 
                 "effects": {"gdp": 1.05}},
                {"name": "自然灾害", "description": "自然灾害破坏了基础设施！", 
                 "effects": {"gdp": 0.95, "balance": 0.9}},
                {"name": "技术突破", "description": "重大技术突破提高了生产效率！", 
                 "effects": {"gdp": 1.08, "unemployment": 0.95}}
            ]
            
            event = random.choice(events)
            
            # 应用事件效果
            if "gdp" in event["effects"]:
                self.gdp *= event["effects"]["gdp"]
            if "unemployment" in event["effects"]:
                self.unemployment *= event["effects"]["unemployment"]
                self.unemployment = max(0.01, min(0.5, self.unemployment))
            if "balance" in event["effects"]:
                self.balance *= event["effects"]["balance"]
            
            messagebox.showinfo("随机事件", f"{event['name']}\n{event['description']}")
            
            # 设置冷却时间，避免事件过于频繁
            self.event_cooldown = 3
    
    def show_daily_report(self):
        # 显示每日经济报告
        report = f"第 {self.days} 天经济报告:\n\n"
        report += f"GDP: ${self.gdp:.2f}\n"
        report += f"失业率: {self.unemployment*100:.1f}%\n"
        report += f"政府资金: ${self.balance:.2f}\n"
        report += f"利率: {self.interest_rate*100:.1f}%\n"
        report += f"税率: {self.tax_rate*100:.1f}%\n"
        
        # 计算通货膨胀率 (简化模型)
        inflation = 0.02 + (self.money_supply / 1000 - 1) * 0.05
        report += f"通货膨胀率: {inflation*100:.1f}%\n"
        
        messagebox.showinfo("每日报告", report)
    
    def show_help(self):
        help_text = """
经济学模拟游戏帮助:

1. 市场供需平衡:
   调整价格以平衡供需。价格过高会减少需求，价格过低会增加需求。

2. 货币政策:
   作为中央银行行长，您可以调整利率和货币供应量。
   - 提高利率会减少投资，降低GDP，但可以控制通货膨胀
   - 增加货币供应量会刺激经济，但可能导致通货膨胀

3. 财政政策:
   管理税收和公共支出。
   - 提高税率会增加政府收入，但可能抑制经济活动
   - 增加公共支出会刺激经济，但会减少政府资金

4. 贸易政策:
   管理国际贸易。
   - 关税会增加政府收入，但可能损害贸易关系
   - 不同的贸易政策会对GDP和就业产生不同影响

目标: 保持经济稳定增长，控制失业率和通货膨胀。
        """
        messagebox.showinfo("游戏帮助", help_text)

# 启动游戏
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    game = EconomicSimulationGame(root)
    root.mainloop()