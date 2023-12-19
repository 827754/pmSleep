import gspread

# Google Sheetsにアクセスするための認証
from google.oauth2.service_account import Credentials

# 認証情報の読み込み
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('future-snowfall-408404-6a89c0080a5e.json', scopes=scope)

# 認証情報を使ってクライアントを作成
client = gspread.authorize(creds)

# スプレッドシートを開く
spreadsheet = client.open('ポケスリ回答')  # 'YourSpreadsheetName' を開きたいスプレッドシートの名前に置き換えます

# シートを取得
sheet = spreadsheet.worksheet('フォームの回答 1')


# セルの値を取得
cell_value = sheet.cell(1, 1).value  # 例えば1行1列目のセルの値を取得

print(sheet.get_all_values())
