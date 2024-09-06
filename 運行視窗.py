import PySimpleGUI as sg
import subprocess
import threading
import webbrowser

# 創建一個函數來讀取 txt 配置文件
def load_config(filename):
    config = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    except FileNotFoundError:
        print(f"未找到配置文件 {filename}")
    return config

# 創建一個函數來保存配置文件
def save_config(filename, config):
    with open(filename, 'w', encoding='utf-8') as file:
        for key, value in config.items():
            file.write(f'{key}={value}\n')

# 加載配置文件
config = load_config('config.txt')

# 介面樣式
sg.LOOK_AND_FEEL_TABLE['MyCreatedTheme'] = {
    'BACKGROUND': '#1ABC9C', # 背景
    'TEXT': '#000000', # 文字
    'INPUT': '#FCE7F3', # 輸入框
    'TEXT_INPUT': '#000000', # 輸入文字
    'SCROLL': '#EB7FD3', # 滾動條
    'BUTTON': ('#000000', '#A5B4FC'), # 按鈕(文字、顏色)
    'PROGRESS': ('', ''), # 進度條(文字、顏色)
    'BORDER': 1, 'SLIDER_DEPTH': 0, # 物件邊框 # 物件3D
    'PROGRESS_DEPTH': 0, # 進度條3D
}
sg.theme('MyCreatedTheme')

sg.set_options(font=('微軟正黑體', 12))

# 創建窗口佈局，使用 config 文件中加載的默認值
program_col = [
    [sg.Frame('輸入列',
        [[
        [sg.Text('影片URL'), sg.Input(default_text=config.get('video_url', ''), key='video_url', size=(42, 1))],
        [sg.Text('帳號'), sg.Input(default_text=config.get('username', ''), key='username')],
        [sg.Text('密碼'), sg.Input(password_char='*', default_text=config.get('password', ''), key='password')],
        [sg.Text('輸入驗證碼'), sg.Input(key='captcha', size=(40, 1))],
        ]]
    ,font=('微軟正黑體', 16))],

    
    # 添加選項
    [sg.Frame('選用項目',
        [[
        [sg.Checkbox('高品質(有時限流用不了)', key='high_quality')],
        [sg.Checkbox('下載縮圖', key='download_thumbnail')],
        [sg.Checkbox('下載影片評論', key='download_comments')],
        [sg.Checkbox('列出影像和音訊品質', key='list_quality')],
        [sg.Checkbox('只下載影片', key='video_only')],
        [sg.Checkbox('只下載音訊', key='audio_only')],
        ]]
    ,font=('微軟正黑體', 16))],
]

# 個人介紹
introduce_col = [
    [sg.Image(filename='./avatar.png', key="image", size=(200, 200))],
    [sg.Text('作者: 小小甜心莫妮卡', font=('微軟正黑體', 16))],
    [sg.Text('個人連結:', font=('微軟正黑體', 16))],
    [sg.Text('GitHub', enable_events=True, key='-GITHUB-LINK-', text_color='blue')],
    [sg.Text('巴哈姆特', enable_events=True, key='-BAHA-LINK-', text_color='blue')],
    [sg.Text('Bilibili', enable_events=True, key='-BILIBILI-LINK-', text_color='blue')],
]

program = sg.Column(program_col)
introduce = sg.Column(introduce_col)

# 窗口整體
layout = [
    [sg.Text('選擇 nndownload 程式'), sg.Input(default_text=config.get('nndownload_path', ''), key='nndownload_path'), sg.FilesBrowse(button_text="選擇路徑", font=('微軟正黑體', 12,'bold'), file_types=(("Python 文件", "*.py"),))],
    [sg.Text('使用方式:', font=('微軟正黑體', 16))],
    [sg.Text('輸入路徑、網址、帳號與密碼，按下確認，檢查郵件中的驗證碼後再開始下載', font=('微軟正黑體', 16))],
    [program, sg.VSeperator(), introduce],
    [sg.Output(size=(80, 15), key='output')],  # 用於顯示 cmd 輸出的內容
    [sg.Button('確認', font=('微軟正黑體', 12,'bold')), sg.Button('開始下載', font=('微軟正黑體', 12,'bold')), sg.Push(), sg.Button('退出視窗', font=('微軟正黑體', 12,'bold'))]
]

window = sg.Window('nndownload 下載視窗', layout)

process = None

def display_message(message):
    """在 Output 框中顯示消息"""
    window['output'].update(message + '\n', append=True)

def run_command(command):
    """運行命令並在窗口輸出"""
    global process
    # 在命令中添加引號以處理路徑中的空格
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

    # 讀取輸出並在窗口顯示
    for line in iter(process.stdout.readline, ''):
        display_message(line.strip())  # 使用 display_message 顯示輸出

    for error_line in iter(process.stderr.readline, ''):
        display_message(f"錯誤: {error_line.strip()}")  # 顯示錯誤信息

    process.wait()  # 等待進程結束

    # 根據返回碼顯示相應的提示信息
    if process.returncode == 0:
        display_message('請到郵箱獲取驗證碼，確認後請回到本介面輸入驗證碼')
    else:
        display_message('登入失敗，請重新檢查路徑與帳號密碼')

def confirm(values):
    nndownload_path = f'"{values["nndownload_path"]}"'  # 路徑中包含空格時，需要加引號
    username = values['username']
    password = values['password']

    # 檢查是否輸入了影片 URL
    if not values['video_url']:
        sg.popup_error('請輸入影片 URL')  # 如果沒有輸入網址，彈出提示對話框
        return  # 阻止程序繼續執行

    # 更新配置
    config['nndownload_path'] = values['nndownload_path']
    config['username'] = username
    config['password'] = password

    # 保存配置
    save_config('config.txt', config)

    video_url = values['video_url']

    # 添加選項參數
    options = []
    if values['high_quality']:
        options.append('-f')
    if values['download_thumbnail']:
        options.append('-t')
    if values['download_comments']:
        options.append('-c')
    if values['list_quality']:
        options.append('-Q')
    if values['video_only']:
        options.append('-an')
    if values['audio_only']:
        options.append('-vn')

    # 構建完整的命令
    command = f'python {nndownload_path} {video_url} -u {username} -p {password} ' + ' '.join(options)
    
    # 顯示提示信息
    display_message('請到郵箱獲取驗證碼，確認後請回到本介面輸入驗證碼')
    
    # 啟動下載命令
    threading.Thread(target=run_command, args=(command,), daemon=True).start()

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == '退出介面':
        break

    if event == '確認':
        confirm(values)

    if event == '開始下載':
        if process and process.poll() is None:  # 確保命令序仍在運行
            captcha = values['captcha']
            display_message(f'開始下載: {captcha}')
            # 驗證碼通過 stdin 發送給命令序
            process.stdin.write(captcha + '\n')
            process.stdin.flush()

    # 處理連結點擊事件
    if event == '-GITHUB-LINK-':
        webbrowser.open('https://github.com/lance1247')  # GitHub連結

    if event == '-BAHA-LINK-':
        webbrowser.open('https://home.gamer.com.tw/homeindex.php')  # 巴哈姆特連結

    if event == '-BILIBILI-LINK-':
        webbrowser.open('https://space.bilibili.com/171022667?spm_id_from=333.1007.0.0')  # Bilibili連結

window.close()
