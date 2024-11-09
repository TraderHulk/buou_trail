# buou_trail
分档移动止盈

本工具极大提高了胜率，特别是管住你的双手，纪律性拉满。


注意CCXT版本不一致大概率会导致bug，建议requirements.txt安装

bn交易所需设置**单向持仓**
OKx交易所**单向持仓双向都支持**
bitget交易所需设置**双向持仓**

相关视频：
- [视频1](https://www.youtube.com/watch?v=1ujgGsMQbqA)
- [视频2](https://www.youtube.com/watch?v=f4T0tKZTVrM)
- [视频3](https://www.youtube.com/watch?v=S8ICwu9u-dk)

### 安装环境
推荐使用 `python3.9`。

> 注意：很多朋友报错基本是由于 Windows 系统时间问题或代理问题。请确保电脑时间同步，若有代理问题，将 `proxy = {}` 改为你的代理端口。

服务器推荐使用阿里云轻量级服务器，我个人使用的是每月 34 人民币的那台。

如果了解 Python 基础知识，大多数情况下都能解决环境问题。如需帮助，建议找身边朋友协助，或联系我有偿代劳。

> 注意 ：配置文件改好参数之后重命名：config.template.json 改成 config.json

### 更新日志
- **20241028**: 修复已平仓品种再次下单会秒平仓的 bug。
- **20241028**: 修复全仓模式平仓会反向开单的 bug。
- **20241029**: 新增黑名单功能。
- **20241029**: 重新整理变量参数。
- **20241105**: 新增bitget版本。
- **20241105**: 改为按日切割日志。
- **20241105**: 修复bitget因为ccxt版本过高导致的bug。
- **20241105**: 更新后支持okx的策略信号监控了 (https://youtu.be/ugyQDrIw8-I)
- **20241106**: okx不再区分单向持仓还是双向，都支持了
- **20241108**: okx bitget 支持浮盈加仓了(https://youtu.be/GOYzgskAjvs) 

### 配置说明


#### Binance 配置

- **apiKey**: 你的 Binance API 密钥，用于身份验证。
- **secret**: 你的 Binance API 密钥的秘密，用于签名请求。
- **leverage**: 杠杆倍数，默认为 1.0。
- **stop_loss_pct**: 止损百分比，表示当亏损达到该百分比时平仓，例如 2 表示亏损 2% 时平仓。
- **low_trail_stop_loss_pct**: 低档保护止盈回撤百分比，表示在低档保护止盈时允许的最大回撤位置，例如 0.3 表示 0.3% 固定平仓。
- **trail_stop_loss_pct**: 第一档移动止盈回撤百分比，表示在第一档移动止盈时允许的最大回撤百分比，例如 0.2 表示 20% 回撤固定平仓。
- **higher_trail_stop_loss_pct**: 第二档移动止盈回撤百分比，表示在第二档移动止盈时允许的最大回撤百分比，例如 0.25 表示 25% 回撤固定平仓。
- **low_trail_profit_threshold**: 低档保护止盈触发阈值，表示达到该盈利百分比时进入低档保护止盈，例如 0.4 表示开仓价 0.4% 时触发。
- **first_trail_profit_threshold**: 第一档移动止盈触发阈值，表示达到该盈利百分比时进入第一档移动止盈，例如 1.0 表示开仓价 1% 时触发。
- **second_trail_profit_threshold**: 第二档移动止盈触发阈值，表示达到该盈利百分比时进入第二档移动止盈，例如 3.0 表示开仓价 1% 时触发。
- **blacklist**: 黑名单列表，包含不需要监控的交易对，例如 ["ETH/USDT:USDT"]。

#### OKX 配置

- **apiKey**: 你的 OKX API 密钥，用于身份验证。
- **secret**: 你的 OKX API 密钥的秘密，用于签名请求。
- **password**: 你的 OKX API 密码，用于身份验证。
- **leverage**: 杠杆倍数，默认为 1.0。（暂时没用，反正都是全平，布欧习惯保留这个参数而已）
- **stop_loss_pct**: 止损百分比，表示当亏损达到该百分比时平仓，例如 2 表示亏损 2% 时平仓。
- **low_trail_stop_loss_pct**: 低档保护止盈回撤百分比，表示在低档保护止盈时允许的最大回撤位置，例如 0.3 表示 0.3% 固定平仓。
- **trail_stop_loss_pct**: 第一档移动止盈回撤百分比，表示在第一档移动止盈时允许的最大回撤百分比，例如 0.2 表示 20% 回撤固定平仓。
- **higher_trail_stop_loss_pct**: 第二档移动止盈回撤百分比，表示在第二档移动止盈时允许的最大回撤百分比，例如 0.25 表示 25% 回撤固定平仓。
- **low_trail_profit_threshold**: 低档保护止盈触发阈值，表示达到该盈利百分比时进入低档保护止盈，例如 0.4 表示开仓价 0.4% 时触发。
- **first_trail_profit_threshold**: 第一档移动止盈触发阈值，表示达到该盈利百分比时进入第一档移动止盈，例如 1.0 表示开仓价 1% 时触发。
- **second_trail_profit_threshold**: 第二档移动止盈触发阈值，表示达到该盈利百分比时进入第二档移动止盈，例如 3.0 表示开仓价 1% 时触发。
- **blacklist**: 黑名单列表，包含不需要监控的交易对，例如 ["ETH-USDT-SWAP"]。

#### BITGET 配置

- **apiKey**: 你的 OKX API 密钥，用于身份验证。
- **secret**: 你的 OKX API 密钥的秘密，用于签名请求。
- **password**: 你的 OKX API 密码，用于身份验证。
- **leverage**: 杠杆倍数，默认为 1.0。（暂时没用，反正都是全平，布欧习惯保留这个参数而已）
- **stop_loss_pct**: 止损百分比，表示当亏损达到该百分比时平仓，例如 2 表示亏损 2% 时平仓。
- **low_trail_stop_loss_pct**: 低档保护止盈回撤百分比，表示在低档保护止盈时允许的最大回撤位置，例如 0.3 表示 0.3% 固定平仓。
- **trail_stop_loss_pct**: 第一档移动止盈回撤百分比，表示在第一档移动止盈时允许的最大回撤百分比，例如 0.2 表示 20% 回撤固定平仓。
- **higher_trail_stop_loss_pct**: 第二档移动止盈回撤百分比，表示在第二档移动止盈时允许的最大回撤百分比，例如 0.25 表示 25% 回撤固定平仓。
- **low_trail_profit_threshold**: 低档保护止盈触发阈值，表示达到该盈利百分比时进入低档保护止盈，例如 0.4 表示开仓价 0.4% 时触发。
- **first_trail_profit_threshold**: 第一档移动止盈触发阈值，表示达到该盈利百分比时进入第一档移动止盈，例如 1.0 表示开仓价 1% 时触发。
- **second_trail_profit_threshold**: 第二档移动止盈触发阈值，表示达到该盈利百分比时进入第二档移动止盈，例如 3.0 表示开仓价 1% 时触发。
- **blacklist**: 黑名单列表，包含不需要监控的交易对，例如 ["ETH-USDT-SWAP"]。

##### 飞书 Webhook

- **feishu_webhook**: 飞书 Webhook URL，用于接收通知。例如 `https://open.feishu.cn/open-apis/bot/v2/hook/655821a2-8`。

##### 监控间隔

- **monitor_interval**: 监控循环的时间间隔（以秒为单位），默认为 4 秒。



##### 免责声明

​		本工具不保证策略收益，一切盈亏损失自行承担！禁止商用，仅供学习使用！如果违反，出了一切法律后果自负。

##### 学习与交流

​	Telegram群：https://t.me/+bRIWTkW0RjAzYjc9

​    多人多端稳定收费vpn邀请链接：http://yunti.run/S9cx83

​	币圈二哥量化的口号是：免费开源、暴富向前！！！