import flet as ft
import requests
from datetime import datetime
from typing import Dict

area_cache: Dict[str, Dict] = {}

def main(page: ft.Page):
    page.title = "地域ごとの天気予報"
    page.theme_mode = "light"

    # プログレスバーにアニメーションを追加
    progress_bar = ft.ProgressBar(
        value=0, 
        visible=False
    )

    def show_error(message: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="閉じる",
            bgcolor=ft.colors.ERROR,
        )
        page.snack_bar.open = True
        page.update()

    # ヘッダーの追加
    header = ft.Container(
        content=ft.Text("日本全土の天気予報", size=30, weight="bold", color=ft.colors.WHITE),
        alignment=ft.alignment.center,  # 修正: .CENTER → .center
        bgcolor=ft.colors.PRIMARY,
        padding=15,
        border_radius=15,
    )

    # 地域リストのデザイン変更
    region_list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=10,
    )

    region_list_container = ft.Container(
        content=region_list_view,
        bgcolor=ft.colors.LIGHT_BLUE_50,  # 背景色を設定
        padding=10,
        border_radius=10,
    )

    # forecast_view を Container でラップ
    forecast_view = ft.Container(
        content=ft.Column(
            expand=True,
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=ft.colors.LIGHT_GREEN_50,  # 背景色
        padding=15,
        border_radius=10,
    )

    def fetch_data(url: str) -> Dict:
        try:
            response = requests.get(url)
            response.raise_for_status()  
            return response.json()
        except requests.RequestException as e:
            show_error(f"データ取得エラー: {str(e)}")
            return {}

    def load_region_list():
        try:
            progress_bar.visible = True
            page.update()

            data = fetch_data("http://www.jma.go.jp/bosai/common/const/area.json")
            if "offices" in data:
                area_cache.update(data["offices"])
                update_region_menu()
            else:
                show_error("地域データの形式が予期したものと異なります。")
        except Exception as e:
            show_error(f"地域データの読み込みに失敗しました: {str(e)}")
        finally:
            progress_bar.visible = False
            page.update()

    def update_region_menu():
        region_list_view.controls.clear()
        region_list_view.controls.append(ft.Text("地域を選んでください", size=20, weight="bold"))
        for code, area in area_cache.items():
            region_list_view.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.LOCATION_ON),
                    title=ft.Text(area["name"], size=18),
                    subtitle=ft.Text(f"地域コード: {code}", size=14),
                    on_click=lambda e, code=code: load_forecast(code),
                )
            )
        page.update()

    def load_forecast(region_code: str):
        try:
            progress_bar.visible = True
            page.update()

            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{region_code}.json"
            data = fetch_data(url)

            if data:
                display_forecast(data)
            else:
                show_error("天気予報データが見つかりません。")
        except Exception as e:
            show_error(f"天気予報の取得に失敗しました: {str(e)}")
        finally:
            progress_bar.visible = False
            page.update()

    def display_forecast(data: Dict):
        forecast_view.content.controls.clear()
        try:
            weekly_data = data[1]  # 週間予報データ
            weather_forecasts = weekly_data["timeSeries"][0]
            temp_forecasts = weekly_data["timeSeries"][1]
            
            # グリッドビューの作成
            grid = ft.GridView(
                expand=True,
                runs_count=4,
                max_extent=200,
                child_aspect_ratio=0.8,
                spacing=10,
                run_spacing=10,
                padding=20,
            )
            # 1週間分の予報を表示する
            for i in range(len(weather_forecasts["timeDefines"])):
                date = weather_forecasts["timeDefines"][i]
                weather_code = weather_forecasts["areas"][0]["weatherCodes"][i]
                
                try:
                    min_temp = temp_forecasts["areas"][0]["tempsMin"][i]
                    max_temp = temp_forecasts["areas"][0]["tempsMax"][i]
                except (IndexError, KeyError):
                    min_temp = max_temp = "--"

                # 予報を表示する部分を作る
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(format_date(date), size=16, weight="bold"),
                                ft.Text(get_weather_icon(weather_code), size=30),  # アイコンサイズ変更
                                ft.Text(get_weather_text(weather_code), size=16),
                                ft.Text(
                                    f"最低 {min_temp if min_temp != '--' else '不明'}°C",
                                    size=16,
                                    color=ft.colors.BLUE,
                                    weight="bold",
                                ),
                                ft.Text(
                                    f"最高 {max_temp if max_temp != '--' else '不明'}°C",
                                    size=16,
                                    color=ft.colors.RED,
                                    weight="bold",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        padding=20,
                        bgcolor=ft.colors.SURFACE_VARIANT,  # 背景色
                        border_radius=15,  # 丸みをつける
                        elevation=5,  # 影を追加
                    )
                )
                grid.controls.append(card)
            
            forecast_view.content.controls.append(grid)
            
        except (KeyError, IndexError) as e:
            show_error("週間予報データの取得に失敗しました。")
        
        page.update()

    # 天気予報サイトのデザインを強化
    page.add(
        ft.Column(
            [
                header,  # ヘッダーを追加
                ft.Row(
                    [
                        region_list_container,  # 修正: Containerでラップ
                        forecast_view,  # 修正: Containerでラップ
                    ],
                    expand=True,
                ),
            ],
            expand=True,
            spacing=15,
        ),
        progress_bar,
    )

    # データの読み込み
    load_region_list()

# 日付をフォーマットする
def format_date(date_str: str) -> str:
    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekdays[date.weekday()]
    return f"{date.month}/{date.day}\n({weekday})"

def get_weather_text(code: str) -> str:
    weather_codes = {
        "100": "晴れ",
        "101": "晴れ時々曇り",
        "102": "晴れ時々雨",
        "200": "曇り",
        "300": "雨",
        "400": "雪",
        "500": "雷雨",
        "413": "雪のち雨",
        "314": "雨のち雪",
    }
    return weather_codes.get(code, f"不明な天気 (コード: {code})")

def get_weather_icon(code: str) -> str:
    weather_icons = {
        "100": "☀️",
        "101": "🌤️",
        "102": "🌦️",
        "200": "☁️",
        "300": "🌧️",
        "400": "❄️",
        "500": "⛈️",
        "413": "❄️→🌧️",
        "314": "🌧️→❄️",
    }
    return weather_icons.get(code, "❓")

if __name__ == "__main__":
    ft.app(target=main)