import FreeSimpleGUI as sg
import subprocess
import threading
import webbrowser

# 创建一个函数来读取 txt 配置文件
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

# 创建一个函数来保存配置文件
def save_config(filename, config):
    with open(filename, 'w', encoding='utf-8') as file:
        for key, value in config.items():
            file.write(f'{key}={value}\n')

# 加载配置文件
config = load_config('config.txt')

# 界面样式
sg.LOOK_AND_FEEL_TABLE['MyCreatedTheme'] = {
    'BACKGROUND': '#1ABC9C', # 背景
    'TEXT': '#000000', # 文字
    'INPUT': '#FCE7F3', # 输入框
    'TEXT_INPUT': '#000000', # 输入文字
    'SCROLL': '#EB7FD3', # 滚动条
    'BUTTON': ('#000000', '#A5B4FC'), # 按钮(文字、颜色)
    'PROGRESS': ('', ''), # 进度条(文字、颜色)
    'BORDER': 1, 'SLIDER_DEPTH': 0, # 组件边框 # 组件3D
    'PROGRESS_DEPTH': 0, # 进度条3D
}
sg.theme('MyCreatedTheme')

sg.set_options(font=('微软雅黑', 12))

# 创建窗口布局，使用 config 文件中加载的默认值
program_col = [
    [sg.Text('使用方式:\n输入路径、网址、账号与密码\n按下确认\n检查邮件中的验证码后再开始下载', font=('微软雅黑', 16))],
    [sg.Frame('输入栏', [
        [sg.Text('影片URL'), sg.Input(config.get('video_url',''), key='video_url', size=(42,1))],
        [sg.Text('账号'), sg.Input(config.get('username',''), key='username')],
        [sg.Text('密码'), sg.Input(password_char='*', default_text=config.get('password',''), key='password')],
        [sg.Text('输入验证码'), sg.Input(key='captcha', size=(40,1))]
    ], font=('微软雅黑',16))],

    # 添加选项
    [sg.Frame('可选项目', [
        [sg.Checkbox('高质量(有时限流无法使用)', key='high_quality'),
         sg.Checkbox('下载缩略图', key='download_thumbnail'),
         sg.Checkbox('下载影片评论', key='download_comments')],
        [sg.Checkbox('列出影像和音频质量', key='list_quality'),
         sg.Checkbox('只下载影片', key='video_only'),
         sg.Checkbox('只下载音频', key='audio_only')]
    ], font=('微软雅黑',16))]
]

# 个人介绍
introduce_col = [
    [sg.Image(filename='./avatar.png', key="image", size=(200, 200))],
    [sg.Text('作者: 小小甜心莫妮卡', font=('微软雅黑', 16))],
    [sg.Text('个人链接:', font=('微软雅黑', 16))],
    [sg.Text('GitHub', enable_events=True, key='-GITHUB-LINK-', text_color='blue')],
    [sg.Text('巴哈姆特', enable_events=True, key='-BAHA-LINK-', text_color='blue')],
    [sg.Text('Bilibili', enable_events=True, key='-BILIBILI-LINK-', text_color='blue')],
]

program = sg.Column(program_col)
introduce = sg.Column(introduce_col)

# 窗口整体
layout = [
    [sg.Push(),sg.Text('niconico会员影片下载窗口', font=('微软雅黑', 24)),sg.Push()],
    [program, sg.VSeperator(), introduce],
    [sg.Output(size=(80, 15), key='output')],  # 用于显示 cmd 输出的内容
    [sg.Button('确认以获取验证码', font=('微软雅黑', 12,'bold')),
     sg.Button('开始下载', font=('微软雅黑', 12,'bold')),
     sg.Push(),
     sg.Button('退出窗口', font=('微软雅黑', 12,'bold'))]
]

window = sg.Window('nndownload-Windows', layout)

process = None

def display_message(message):
    """在 Output 框中显示消息"""
    window['output'].update(message + '\n', append=True)

def run_command(command):
    """运行命令并在窗口输出"""
    global process
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

    for line in iter(process.stdout.readline, ''):
        display_message(line.strip())

    for error_line in iter(process.stderr.readline, ''):
        display_message(f"错误: {error_line.strip()}")

    process.wait()

    if process.returncode != 0:
        display_message('登录失败，请重新检查路径与账号密码')

def confirm(values):
    username = values['username']
    password = values['password']
    
    if not values['video_url']:
        sg.popup_error('请输入影片 URL')
        return

    config['username'] = username
    config['password'] = password
    save_config('config.txt', config)

    video_url = values['video_url']

    options = []
    if values['high_quality']: options.append('-f')
    if values['download_thumbnail']: options.append('-t')
    if values['download_comments']: options.append('-c')
    if values['list_quality']: options.append('-Q')
    if values['video_only']: options.append('-an')
    if values['audio_only']: options.append('-vn')

    command = f'python -m nndownload "{video_url}" -u "{username}" -p "{password}" ' + ' '.join(options)

    display_message('请前往邮箱获取验证码，确认后回到本窗口输入验证码')

    threading.Thread(target=run_command, args=(command,), daemon=True).start()

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == '退出窗口':
        break

    if event == '确认以获取验证码':
        confirm(values)

    if event == '开始下载':
        if process and process.poll() is None:
            captcha = values['captcha']
            display_message(f'开始下载: {captcha}')
            process.stdin.write(captcha + '\n')
            process.stdin.flush()

    if event == '-GITHUB-LINK-':
        webbrowser.open('https://github.com/lance1247')

    if event == '-BAHA-LINK-':
        webbrowser.open('https://home.gamer.com.tw/homeindex.php')

    if event == '-BILIBILI-LINK-':
        webbrowser.open('https://space.bilibili.com/171022667?spm_id_from=333.1007.0.0')

window.close()
