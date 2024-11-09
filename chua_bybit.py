# -*- coding: utf-8 -*-

# Author : 'hxc'

# Time: 2024/11/9 9:08 AM

# File_name: 'chua_bybit.py.py'

"""
Describe: this is a demo!
"""

import ccxt
import time
import logging
import requests
import json
from logging.handlers import TimedRotatingFileHandler

from ccxt.base.types import OrderSide


class MultiAssetTradingBot:
    def __init__(self, config, feishu_webhook=None, monitor_interval=4):
        self.leverage = float(config["leverage"])
        self.stop_loss_pct = config["stop_loss_pct"]
        self.low_trail_stop_loss_pct = config["low_trail_stop_loss_pct"]
        self.trail_stop_loss_pct = config["trail_stop_loss_pct"]
        self.higher_trail_stop_loss_pct = config["higher_trail_stop_loss_pct"]
        self.low_trail_profit_threshold = config["low_trail_profit_threshold"]
        self.first_trail_profit_threshold = config["first_trail_profit_threshold"]
        self.second_trail_profit_threshold = config["second_trail_profit_threshold"]
        self.feishu_webhook = feishu_webhook
        self.blacklist = set(config.get("blacklist", []))
        self.monitor_interval = monitor_interval  # 从配置文件读取的监控循环时间

        # 配置交易所
        self.exchange = ccxt.bybit({
            'apiKey': config["apiKey"],
            'secret': config["secret"],
            'timeout': 3000,
            'rateLimit': 50,
            'options': {'defaultType': 'swap'},
            # 'proxies': {'http': 'http://127.0.0.1:10100', 'https': 'http://127.0.0.1:10100'},
        })

        self.exchange.enable_demo_trading(True)

        # 配置日志
        log_file = "log/multi_asset_bot.log"
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # 使用 TimedRotatingFileHandler 以天为单位进行日志分割
        file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8')
        file_handler.suffix = "%Y-%m-%d"  # 设置日志文件名的后缀格式，例如 multi_asset_bot.log.2024-11-05
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        self.logger = logger

        # 用于记录每个持仓的最高盈利值和当前档位
        self.highest_profits = {}
        self.current_tiers = {}
        self.detected_positions = {}

    def send_feishu_notification(self, message):
        if self.feishu_webhook:
            try:
                headers = {'Content-Type': 'application/json'}
                payload = {"msg_type": "text", "content": {"text": message}}
                response = requests.post(self.feishu_webhook, json=payload, headers=headers)
                if response.status_code == 200:
                    self.logger.info("飞书通知发送成功")
                else:
                    self.logger.error("飞书通知发送失败，状态码: %s", response.status_code)
            except Exception as e:
                self.logger.error("发送飞书通知时出现异常: %s", str(e))

    def schedule_task(self):
        self.logger.info("启动主循环，开始执行任务调度...")
        try:
            while True:
                self.monitor_positions()
                time.sleep(self.monitor_interval)
        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.error(error_message)
            self.send_feishu_notification(error_message)

    def fetch_positions(self):
        try:
            positions = self.exchange.fetch_positions()
            return positions
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return []

    def reduce_market_order(self, symbol, amount, side):
        try:
            _side = OrderSide('buy')
            if side == 'short':
                _side = OrderSide('sell')

            # Set positionIdx based on side
            positionIdx = 1 if side == 'short' else 2  # 1 for closing long, 2 for closing short
            self.exchange.create_order(
                symbol,
                'market',
                _side,
                amount,
                None,
                {
                    'reduce_only': True,
                    'positionIdx': positionIdx
                }
            )
            self.logger.info(f"Closed position for {symbol} with size {amount}, side: {side}")
            return True
        except Exception as e:
            self.logger.error(f"Error close_position_bybit positions: {e}")
            return False

    def close_position(self, symbol, amount, side):
        try:
            # 获取当前持仓数量
            position = next((pos for pos in self.fetch_positions() if pos['symbol'] == symbol), None)
            if position is None or float(position['contracts']) == 0:
                self.logger.info(f"{symbol} 仓位已平，无需继续平仓")
                return True

            self.reduce_market_order(symbol, amount, side)
            self.logger.info(f"Closed position for {symbol} with size {amount}, side: {side}")
            self.send_feishu_notification(f"Closed position for {symbol} with size {amount}, side: {side}")
            # 清除检测过的仓位及相关数据
            self.detected_positions.pop(symbol, None)
            self.highest_profits.pop(symbol, None)  # 清除最高盈利值
            self.current_tiers.pop(symbol, None)  # 清除当前档位
            return True
        except Exception as e:
            self.logger.error(f"Error closing position for {symbol}: {e}")
            return False

    def monitor_positions(self):
        positions = self.fetch_positions()
        current_symbols = set(position['symbol'] for position in positions if float(position['contracts']) != 0)

        closed_symbols = set(self.detected_positions.keys()) - current_symbols
        for symbol in closed_symbols:
            self.logger.info(f"手动平仓检测：{symbol} 已平仓，从监控中移除")
            self.send_feishu_notification(f"手动平仓检测：{symbol} 已平仓，从监控中移除")
            self.detected_positions.pop(symbol, None)

        for position in positions:
            symbol = position['symbol']
            position_amt = float(position['contracts'])
            entry_price = float(position['entryPrice'])
            current_price = float(position['markPrice'])
            side = position['side']
            td_mode = position['marginMode']

            if position_amt == 0:
                continue

            if symbol in self.blacklist:
                if symbol not in self.detected_positions:
                    self.send_feishu_notification(f"检测到黑名单品种：{symbol}，跳过监控")
                    self.detected_positions[symbol] = position_amt  # 临时存储持仓数量
                continue

            if symbol not in self.detected_positions:
                self.detected_positions[symbol] = position_amt
                self.highest_profits[symbol] = 0
                self.current_tiers[symbol] = "无"
                self.logger.info(
                    f"首次检测到仓位：{symbol}, 仓位数量: {position_amt}, 开仓价格: {entry_price}, 方向: {side}")
                self.send_feishu_notification(
                    f"首次检测到仓位：{symbol}, 仓位数量: {position_amt}, 开仓价格: {entry_price}, 方向: {side}")

            # 检测是否有新加仓
            if position_amt > self.detected_positions[symbol]:
                self.highest_profits[symbol] = 0  # 重置最高盈利
                self.current_tiers[symbol] = "无"  # 重置档位
                self.detected_positions[symbol] = position_amt
                self.logger.info(f"{symbol} 新仓检测到，重置最高盈利和档位。")
                continue  # 跳出当前循环

            if side == 'long':
                profit_pct = (current_price - entry_price) / entry_price * 100
            elif side == 'short':
                profit_pct = (entry_price - current_price) / entry_price * 100
            else:
                continue

            highest_profit = self.highest_profits.get(symbol, 0)
            if profit_pct > highest_profit:
                highest_profit = profit_pct
                self.highest_profits[symbol] = highest_profit

            current_tier = self.current_tiers.get(symbol, "无")
            if highest_profit >= self.second_trail_profit_threshold:
                current_tier = "第二档移动止盈"
            elif highest_profit >= self.first_trail_profit_threshold:
                current_tier = "第一档移动止盈"
            elif highest_profit >= self.low_trail_profit_threshold:
                current_tier = "低档保护止盈"
            else:
                current_tier = "无"

            self.current_tiers[symbol] = current_tier

            self.logger.info(
                f"监控 {symbol}，仓位: {position_amt}，方向: {side}，开仓价格: {entry_price}，当前价格: {current_price}，浮动盈亏: {profit_pct:.2f}%，最高盈亏: {highest_profit:.2f}%，当前档位: {current_tier}")

            if current_tier == "低档保护止盈":
                self.logger.info(f"回撤到{self.low_trail_stop_loss_pct:.2f}% 止盈")
                if profit_pct <= self.low_trail_stop_loss_pct:
                    self.logger.info(f"{symbol} 触发低档保护止盈，当前盈亏回撤到: {profit_pct:.2f}%，执行平仓")
                    self.close_position(symbol, abs(position_amt), side)
                    continue

            elif current_tier == "第一档移动止盈":
                trail_stop_loss = highest_profit * (1 - self.trail_stop_loss_pct)
                self.logger.info(f"回撤到 {trail_stop_loss:.2f}% 止盈")
                if profit_pct <= trail_stop_loss:
                    self.logger.info(
                        f"{symbol} 达到利润回撤阈值，当前档位：第一档移动止盈，最高盈亏: {highest_profit:.2f}%，当前盈亏: {profit_pct:.2f}%，执行平仓")
                    self.close_position(symbol, abs(position_amt), side)
                    continue

            elif current_tier == "第二档移动止盈":
                trail_stop_loss = highest_profit * (1 - self.higher_trail_stop_loss_pct)
                self.logger.info(f"回撤到 {trail_stop_loss:.2f}% 止盈")
                if profit_pct <= trail_stop_loss:
                    self.logger.info(
                        f"{symbol} 达到利润回撤阈值，当前档位：第二档移动止盈，最高盈亏: {highest_profit:.2f}%，当前盈亏: {profit_pct:.2f}%，执行平仓")
                    self.close_position(symbol, abs(position_amt), side)
                    continue

            if profit_pct <= -self.stop_loss_pct:
                self.logger.info(f"{symbol} 触发止损，当前盈亏: {profit_pct:.2f}%，执行平仓")
                self.close_position(symbol, abs(position_amt), side)


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config_data = json.load(f)

    # 选择交易平台，假设这里选择 Bybit
    platform_config = config_data['bybit']
    feishu_webhook_url = config_data['feishu_webhook']
    monitor_interval = config_data.get("monitor_interval", 4)  # 默认值为4秒

    bot = MultiAssetTradingBot(platform_config, feishu_webhook=feishu_webhook_url, monitor_interval=monitor_interval)
    bot.schedule_task()

