import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import json

print("🚀 بوت تداول العملات - الإصدار النهائي")
print("📊 يعمل بكفاءة - إشارات حقيقية")
print("🎯 20 عملة - تحديث كل دقيقتين")
print("=" * 60)

class UltimateTradingBot:
    def __init__(self):
        self.symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
            'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
            'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'FILUSDT',
            'NEARUSDT', 'ALGOUSDT', 'VETUSDT', 'ICPUSDT', 'ETCUSDT'
        ]
        self.analysis_count = 0
        self.total_signals = 0
        
    def get_klines_data(self, symbol, interval='5m', limit=50):
        """جلب بيانات التداول"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            closes = [float(candle[4]) for candle in data]
            volumes = [float(candle[5]) for candle in data]
            
            return {
                'closes': np.array(closes),
                'volumes': np.array(volumes),
                'current_price': closes[-1]
            }
        except:
            return None

    def calculate_rsi(self, prices, period=14):
        """حساب RSI"""
        if len(prices) < period + 1:
            return 50
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.mean(gains[-period:])
        avg_losses = np.mean(losses[-period:])
        
        if avg_losses == 0:
            return 100
        
        rs = avg_gains / avg_losses
        return 100 - (100 / (1 + rs))

    def analyze_symbol(self, symbol):
        """تحليل عملة معينة"""
        try:
            data = self.get_klines_data(symbol)
            if not data:
                return None
            
            # حساب المؤشرات
            rsi = self.calculate_rsi(data['closes'])
            
            # المتوسطات
            ema_8 = pd.Series(data['closes']).ewm(span=8).mean().iloc[-1]
            ema_21 = pd.Series(data['closes']).ewm(span=21).mean().iloc[-1]
            
            # الحجم
            volume_avg = np.mean(data['volumes'][-20:])
            volume_ratio = data['volumes'][-1] / volume_avg
            
            # التغير السعري
            price_change = ((data['closes'][-1] - data['closes'][-2]) / data['closes'][-2]) * 100
            
            # نظام النقاط
            points = 0
            conditions = []
            
            # RSI
            if rsi < 25:
                points += 30
                conditions.append("RSI تشبع بيعي شديد")
            elif rsi < 35:
                points += 20
                conditions.append("RSI تشبع بيعي")
            
            # الاتجاه
            if ema_8 > ema_21:
                points += 25
                conditions.append("اتجاه صعودي")
            
            # الحجم
            if volume_ratio > 2.5:
                points += 20
                conditions.append("حجم عالي")
            elif volume_ratio > 1.5:
                points += 15
                conditions.append("حجم جيد")
            
            # الزخم
            if price_change > 0.5:
                points += 15
                conditions.append("زخم إيجابي")
            
            # تحديد الإشارة
            if points >= 60:
                if points >= 80:
                    signal_type = "🟢 شراء قوي"
                elif points >= 70:
                    signal_type = "🟡 شراء متوسط"
                else:
                    signal_type = "🔵 شراء ضعيف"
                
                return {
                    'symbol': symbol,
                    'signal': signal_type,
                    'confidence': points,
                    'price': data['current_price'],
                    'rsi': round(rsi, 1),
                    'volume_ratio': round(volume_ratio, 1),
                    'price_change': round(price_change, 2),
                    'conditions': conditions
                }
            
            return None
            
        except Exception as e:
            return None

    def run_analysis(self):
        """تشغيل دورة تحليل كاملة"""
        self.analysis_count += 1
        
        print(f"\n📊 دورة التحليل #{self.analysis_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        signals = []
        
        for symbol in self.symbols:
            signal = self.analyze_symbol(symbol)
            if signal:
                signals.append(signal)
                print(f"✅ {symbol}: {signal['signal']} ({signal['confidence']}%)")
            else:
                print(f"❌ {symbol}: لا توجد إشارة")
            
            time.sleep(0.2)  # تجنب حظر API
        
        return signals

# التشغيل الرئيسي
bot = UltimateTradingBot()

print("\n🎯 البوت يعمل بنجاح!")
print("⏰ سيتم التحليل كل دقيقتين تلقائياً")
print("=" * 50)

last_analysis = datetime.now()

try:
    while True:
        current_time = datetime.now()
        time_diff = (current_time - last_analysis).total_seconds() / 60
        
        if time_diff >= 2:  # كل دقيقتين
            signals = bot.run_analysis()
            
            if signals:
                print(f"\n🎯 تم العثور على {len(signals)} إشارة تداول!")
                print("=" * 50)
                
                # ترتيب حسب الثقة
                signals.sort(key=lambda x: x['confidence'], reverse=True)
                
                for i, signal in enumerate(signals[:5], 1):  # عرض أول 5 إشارات
                    print(f"\n{i}. {signal['symbol']} - {signal['signal']}")
                    print(f"   الثقة: {signal['confidence']}% | السعر: ${signal['price']:.4f}")
                    print(f"   RSI: {signal['rsi']} | الحجم: {signal['volume_ratio']}x")
                    print(f"   التغير: {signal['price_change']}%")
                    print(f"   الشروط: {', '.join(signal['conditions'])}")
                
                bot.total_signals += len(signals)
            
            else:
                print("\n⚠️ لا توجد إشارات قوية حالياً")
                print("💡 هذا طبيعي - انتظر دورة التحليل القادمة")
            
            last_analysis = datetime.now()
            
            # عرض الإحصائيات
            print(f"\n📈 الإحصائيات:")
            print(f"   إجمالي التحليلات: {bot.analysis_count}")
            print(f"   إجمالي الإشارات: {bot.total_signals}")
            print(f"   متوسط الإشارات: {bot.total_signals / bot.analysis_count:.1f} لكل تحليل")
        
        else:
            # عرض العد التنازلي
            remaining = 2 - time_diff
            minutes = int(remaining)
            seconds = int((remaining - minutes) * 60)
            print(f"\r⏳ التحليل القادم خلال: {minutes:02d}:{seconds:02d}", end='', flush=True)
        
        time.sleep(5)  # فحص كل 5 ثواني
        
except KeyboardInterrupt:
    print(f"\n\n🛑 تم إيقاف البوت")
    print(f"📊 الإحصائيات النهائية: {bot.analysis_count} تحليل, {bot.total_signals} إشارة")
    print("🎯 شكراً لاستخدامك البوت!")
