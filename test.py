import gspread

# Google Sheetsにアクセスするための認証
from google.oauth2.service_account import Credentials
from selenium import webdriver  # seleniumモジュールの読み込み
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from time import sleep


# 認証情報の読み込み
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_file(
    "future-snowfall-408404-14c3825a59f9.json", scopes=scope
)

# 認証情報を使ってクライアントを作成
client = gspread.authorize(creds)

# スプレッドシートを開く
spreadsheet = client.open("ポケスリ回答")  # 'YourSpreadsheetName' を開きたいスプレッドシートの名前に置き換えます

# シートを取得
sheet = spreadsheet.worksheet("フォームの回答 1")

daifukuCell = 18

daifukuCol = sheet.col_values(daifukuCell)
dataraw = sheet.col_values(1)
last_row = len(dataraw)

url = "https://www.pokemonsleepdaifuku.com/checker/"  # アクセス先のurlを指定

driver = webdriver.Chrome()  # driverの読み込み
driver.get(url)  # サイトにアクセス

for rows in range(len(dataraw)):
    # print(rows)
    # print(daifukuCol[rows])
    # for num in range(last_row):

    #     print(num + 2)

    #     rows = num + 210
    if rows < len(daifukuCol):
        if daifukuCol[rows] != "":
            continue

    # セルの値を取得
    rowData = sheet.row_values(rows + 1)

    PokemoName = rowData[3] + rowData[4] + rowData[5]
    Sub10 = rowData[6]
    Sub25 = rowData[7]
    Sub50 = rowData[8]
    Personality = rowData[9]

    NameFlag = rowData[1]
    DaifukuFlag = len(rowData)
    print(DaifukuFlag)
    if PokemoName == "ピカチュウ（ハロウィン）":
        PokemoName = "ハロウィンピカチュウ"
    if PokemoName == "ピカチュウ（ホリデー）":
        PokemoName = "ホリデーピカチュウ"

    Sub10 = Sub10.replace("げんき", "元気")
    Sub25 = Sub25.replace("げんき", "元気")
    Sub50 = Sub50.replace("げんき", "元気")

    if NameFlag != "やご":
        sleep(2)
        iDbtn = driver.find_element(
            By.XPATH, "//label[text()='50']"
        )
        iDbtn.click()

        PokeDropdown = driver.find_element(By.ID, "pokemonNameSelect")
        # search_area.send_keys("dailyhackon python")

        PokeSelect = Select(PokeDropdown)
        PokeSelect.select_by_value(PokemoName)

        Sub10Dropdown = driver.find_element(By.NAME, "pokemon_subskill1")
        # search_area.send_keys("dailyhackon python")
        sleep(1)
        Sub10Select = Select(Sub10Dropdown)
        Sub10Select.select_by_visible_text(Sub10)

        Sub25Dropdown = driver.find_element(By.NAME, "pokemon_subskill2")
        # search_area.send_keys("dailyhackon python")
        sleep(1)
        Sub25Select = Select(Sub25Dropdown)
        Sub25Select.select_by_visible_text(Sub25)

        Sub50Dropdown = driver.find_element(By.NAME, "pokemon_subskill3")
        # search_area.send_keys("dailyhackon python")
        sleep(1)
        Sub50Select = Select(Sub50Dropdown)
        Sub50Select.select_by_visible_text(Sub50)

        PersonalityDropdown = driver.find_element(By.NAME, "pokemon_personality")
        # search_area.send_keys("dailyhackon python")
        sleep(1)
        PersonalitySelect = Select(PersonalityDropdown)
        all_PersonalityOptions = PersonalitySelect.options  # 全ての選択肢を取得(list)
        for option in all_PersonalityOptions:
            if Personality in option.text:
                PersonalitySelect.select_by_visible_text(option.text)

        checkBtn = driver.find_element(By.CLASS_NAME, "submitButton")
        checkBtn.click()
        sleep(3)

        table = driver.find_element(By.CLASS_NAME, "resultTable")
        trs = table.find_elements(By.TAG_NAME, "tr")
        ths = trs[0].find_elements(By.TAG_NAME, "td")
        tds = trs[1].find_elements(By.TAG_NAME, "td")
        line = "{"
        for j in range(0, len(tds)):
            if j < len(tds) - 1:
                line += '"' + ths[j].text + '":"' + tds[j].text + '",'
            else:
                line += '"' + ths[j].text + '":"' + tds[j].text + '"'

        line += "}"
        print(line.replace("\n", "").replace("\r", ""))
        # daifuku = sheet.row_values(2)[16]
        sheet.update_cell(rows + 1, daifukuCell, line.replace("\n", "").replace("\r", ""))

        checkBtn = driver.find_element(By.CLASS_NAME, "resetButton")
        sleep(10)
        checkBtn.click()
