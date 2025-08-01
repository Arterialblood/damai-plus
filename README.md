# 大麦网自动抢票工具

一个基于Python的大麦网自动抢票工具，支持多线程抢票和反爬虫绕过。

## ✨ 功能特点

- 🔐 **自动登录**：支持账号密码和扫码登录
- 🚀 **多线程抢票**：支持3-10个线程并发抢票
- 🛡️ **反爬虫绕过**：基于Selenium完全绕过反爬虫限制
- ⚡ **实时监控**：实时检测开售状态
- 💾 **Cookies保存**：自动保存登录状态
- 🎯 **智能重试**：自动重试和错误处理

## 📋 系统要求

- Python 3.7+
- Chrome浏览器
- ChromeDriver

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载ChromeDriver

根据您的Chrome版本下载对应的ChromeDriver：

```bash
# macOS用户
brew install chromedriver

# 或者手动下载
curl -O https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# 根据版本号下载对应文件
```

### 3. 配置参数

编辑 `Automatic_ticket_purchase.py` 中的配置：

```python
def __init__(self):
    # 登录信息
    self.login_id: str = 'your_account'      # 您的账号
    self.login_password: str = 'your_password' # 您的密码
    
    # 购票参数
    self.item_id: int = 954702452           # 商品ID
    self.viewer: list = ['王博弘']          # 观影人
    self.buy_nums: int = 1                  # 购买数量
    self.ticket_price: int = 180            # 票价
```

### 4. 运行程序

#### 标准模式（单线程）
```bash
# 账号密码登录
python Automatic_ticket_purchase.py

# 扫码登录
python Automatic_ticket_purchase.py --mode qr
```

#### 增强模式（多线程，推荐）
```bash
# 3个线程（默认）
python Automatic_ticket_purchase.py --enhanced

# 5个线程
python Automatic_ticket_purchase.py --enhanced --threads 5

# 扫码登录 + 多线程
python Automatic_ticket_purchase.py --mode qr --enhanced --threads 5
```

#### Selenium版本（完全绕过反爬虫）
```bash
# 使用Selenium版本
python selenium_version.py
```

## 📖 详细使用说明

### 获取商品ID

1. 访问大麦网商品页面
2. 从URL中获取商品ID：`https://detail.damai.cn/item.htm?id=954702452`
3. 将ID填入配置中

### 设置观影人

1. 在大麦网账户中添加观影人信息
2. 将观影人姓名填入配置中
3. 确保观影人数量与购买数量一致

### 选择票价

1. 查看演出详情页面的票价信息
2. 将目标票价填入配置中
3. 确保票价与实际票价一致

## 🔧 高级配置

### 多线程配置

```bash
# 低并发（适合普通票）
python Automatic_ticket_purchase.py --enhanced --threads 3

# 高并发（适合秒空票）
python Automatic_ticket_purchase.py --enhanced --threads 8
```

### 登录方式

```bash
# 账号密码登录
python Automatic_ticket_purchase.py --mode account

# 扫码登录（推荐）
python Automatic_ticket_purchase.py --mode qr
```

## 🛡️ 反爬虫策略

### 已实施的措施

1. **Selenium模拟浏览器**
   - 完全绕过API限制
   - 模拟真实用户操作
   - 支持可视化监控

2. **API优化**
   - 更新Chrome 138请求头
   - 添加随机延迟（1-3秒）
   - 检测反爬虫页面
   - 智能重试机制

3. **多线程支持**
   - 并发请求提高成功率
   - 容错处理
   - 实时状态监控

## 📊 使用建议

### 对于秒空票
```bash
# 推荐使用Selenium版本
python selenium_version.py
```

### 对于普通票
```bash
# 可以使用API版本
python Automatic_ticket_purchase.py --enhanced --threads 3
```

### 最佳实践

1. **提前准备**：在开售前30分钟启动程序
2. **网络稳定**：确保网络连接稳定
3. **多线程**：使用5-10个线程提高成功率
4. **监控状态**：关注程序输出的状态信息

## ⚠️ 注意事项

1. **合法使用**：仅用于个人学习研究，请遵守相关法律法规
2. **账号安全**：请妥善保管账号信息
3. **网络环境**：确保网络稳定，避免频繁请求
4. **版本更新**：定期更新ChromeDriver版本

## 🐛 常见问题

### Q: 程序报错"ChromeDriver版本不匹配"
A: 请更新ChromeDriver到与Chrome浏览器相同的版本

### Q: 登录失败
A: 删除cookies.pkl文件重新登录

### Q: API返回错误
A: 使用Selenium版本可以完全绕过API限制

### Q: 多线程不工作
A: 确保使用 `--enhanced` 参数启动增强模式

## 📝 更新日志

### v2.1.0
- 添加多线程支持
- 优化反爬虫策略
- 增加Selenium版本
- 改进错误处理

### v2.0.0
- 重构为API版本
- 提高抢票效率
- 添加自动登录

## 📄 许可证

本项目仅供学习研究使用，请遵守相关法律法规。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

**免责声明**：本项目仅用于技术学习和研究，使用者需自行承担使用风险，开发者不承担任何法律责任。