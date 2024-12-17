import flet as ft
import requests
import json
import sqlite3
from datetime import datetime

class WeatherApp:
    def __init__(self):
        # API URLs
        self.AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
        self.FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"
        
        # エリアと予報のキャッシュ
        self.area_cache = {}

        # データベースの初期化
        self.db_name = "weather_forecast.db"
        self.initialize_db()

    def initialize_db(self):
        """データベースとテーブルを初期化する。"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_forecast (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_name TEXT,
                date TEXT,
                weather_icon TEXT,
                weather_text TEXT,
                forecast TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_forecast_to_db(self, area_name, forecasts):
        """取得した天気情報をデータベースに保存する。"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for forecast in forecasts:
            cursor.execute('''
                INSERT INTO weather_forecast (area_name, date, weather_icon, weather_text, forecast)
                VALUES (?, ?, ?, ?, ?)
            ''', (area_name, forecast['date'], forecast['weather_icon'], forecast['weather_text'], forecast['forecast']))

        conn.commit()
        conn.close()

    def format_date(self, date_str: str) -> str:
        """日付を表示用にフォーマットする。"""
        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[date.weekday()]
        return f"{date.month}/{date.day}\n({weekday})"

    def get_weather_text(self, code: str) -> str:
        """天気コードに対応する天気の説明を返す。"""
        weather_codes = {
            "100": "晴れ", "101": "晴れ時々曇り", "102": "晴れ時々雨",
            "200": "曇り", "201": "曇り時々晴れ", "202": "曇り時々雨",
            "218": "曇り時々雪", "270": "雪時々曇り", "300": "雨",
            "400": "雪", "500": "雷雨", "413": "雪のち雨",
            "206": "雨時々曇り", "111": "雨時々晴れ", "112": "雨時々雪",
            "211": "雪時々晴れ", "212": "雪時々曇り", "313": "雪のち雨",
            "314": "雨のち雪", "203": "曇り時々雪", "302": "雪",
            "114": "雪時々晴れ", "402": "大雪", "204": "雪時々雨",
            "207": "雷雨時々雪", "205": "雨時々雪", "209": "雪時々雷雨",
            "210": "雷雨時々雪", "260": "雷雨時々曇り",
        }
        return weather_codes.get(code, f"不明な天気 (コード: {code})")

    def get_weather_icon(self, code: str) -> str:
        """天気コードに対応する絵文字を返す。"""
        weather_icons = {
            "100": "☀️", "101": "🌤️", "102": "🌦️", "200": "☁️", 
            "300": "🌧️", "400": "❄️", "500": "⛈️", "413": "❄️→🌧️", 
            "314": "🌧️→❄️", "201": "🌤️", "202": "☁️🌧️", "218": "☁️❄️",
            "270": "❄️☁️", "206": "🌧️☁️", "111": "🌧️☀️", "112": "🌧️❄️",
            "211": "❄️☀️", "212": "❄️☁️", "313": "❄️🌧️", "203": "☁️❄️",
            "302": "❄️", "114": "❄️☀️", "402": "❄️❄️❄️", "204": "❄️🌧️",
            "207": "⛈️❄️", "205": "🌧️❄️", "209": "❄️⛈️", 
            "210": "⛈️❄️", "260": "⛈️☁️",
        }
        return weather_icons.get(code, "❓")

    def load_areas(self):
        """JMA APIから地域情報を読み込む。"""
        try:
            response = requests.get(self.AREA_URL)
            data = response.json()
            prefectures = {}
            for code, area_info in data['offices'].items():
                prefectures[area_info['name']] = {'name': area_info['name'], 'code': code}
            self.area_cache = prefectures
            return list(prefectures.keys())
        except Exception as e:
            print(f"地域データの読み込みエラー: {e}")
            return []

    def load_forecast(self, selected_area):
        """指定された地域の天気予報を読み込む。"""
        if not selected_area:
            return []
        
        try:
            area_code = self.area_cache[selected_area]['code']
            response = requests.get(f"{self.FORECAST_URL}{area_code}.json")
            forecast_data = response.json()
            
            processed_forecasts = []
            time_series = forecast_data[0]['timeSeries']
            dates = time_series[0]['timeDefines']
            weathers = time_series[0]['areas'][0]['weathers']

            weather_codes = time_series[0]['areas'][0].get('weatherCodes', ['100'] * len(weathers))
            for date, weather, code in zip(dates[:7], weathers[:7], weather_codes[:7]):
                processed_forecasts.append({
                    'date': self.format_date(date),
                    'forecast': weather,
                    'weather_text': self.get_weather_text(code),
                    'weather_icon': self.get_weather_icon(code)
                })

            # データベースに保存
            self.save_forecast_to_db(selected_area, processed_forecasts)
            return processed_forecasts
        except Exception as e:
            print(f"天気予報の読み込みエラー: {e}")
            return []

    def main(self, page: ft.Page):
        page.title = "天気予報アプリ"
        page.bgcolor = ft.colors.LIGHT_BLUE_50
        page.padding = 0

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.WB_SUNNY, color=ft.colors.WHITE, size=40),
                    ft.Text("天気予報アプリ", size=28, weight="bold", color=ft.colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=ft.colors.DEEP_PURPLE,
            padding=15,
        )

        forecast_view = ft.GridView(expand=True, runs_count=3, spacing=10, run_spacing=10, padding=15)
        areas = self.load_areas()
        region_menu = ft.Dropdown(
            label="地域を選択",
            options=[ft.dropdown.Option(area) for area in areas],
            on_change=lambda e: update_forecast(e.control.value),
            width=300,
        )

        def update_forecast(selected_area):
            forecast_view.controls.clear()
            forecasts = self.load_forecast(selected_area)
            for forecast in forecasts:
                forecast_view.controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(forecast['date'], size=16, weight="bold"),
                                ft.Text(forecast['weather_icon'], size=30),
                                ft.Text(forecast['weather_text'], size=14),
                                ft.Text(forecast['forecast'], size=12, color=ft.colors.GREY_500),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        width=180,
                        height=180,
                        bgcolor=ft.colors.LIGHT_BLUE_300,
                        border_radius=10,
                        padding=10,
                    )
                )
            forecast_view.update()

        page.add(ft.Column(controls=[header, ft.Row([region_menu, forecast_view], expand=True)], expand=True))

    def run(self):
        ft.app(target=self.main)

if __name__ == "__main__":
    weather_app = WeatherApp()
    weather_app.run()