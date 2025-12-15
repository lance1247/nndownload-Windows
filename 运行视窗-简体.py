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
    'BORDER': 1, 'SLIDER_DEPTH': 0, # 对象边框 # 对象3D
    'PROGRESS_DEPTH': 0, # 进度条3D
}
sg.theme('MyCreatedTheme')

sg.set_options(font=('微软雅黑', 12))

# 创建窗口布局，使用 config 文件中加载的默认值
program_col = [
    [sg.Text('使用方式:\n输入路径、网址、账号与密码\n点击确认\n检查邮箱中的验证码后再开始下载', font=('微软雅黑', 16))],
    [sg.Frame('输入栏', [
        [sg.Text('视频URL'), sg.Input(config.get('video_url',''), key='video_url', size=(42,1))],
        [sg.Text('账号'), sg.Input(config.get('username',''), key='username')],
        [sg.Text('密码'), sg.Input(password_char='*', default_text=config.get('password',''), key='password')],
        [sg.Text('输入验证码'), sg.Input(key='captcha', size=(40,1))]
    ], font=('微软雅黑',16))],

    # 添加选项
    [sg.Frame('可选项目', [
        [sg.Checkbox('高清质量(有时限流可能不可用)', key='high_quality'),
         sg.Checkbox('下载缩略图', key='download_thumbnail'),
         sg.Checkbox('下载视频评论', key='download_comments')],
        [sg.Checkbox('列出视频和音频质量', key='list_quality'),
         sg.Checkbox('仅下载视频', key='video_only'),
         sg.Checkbox('仅下载音频', key='audio_only')]
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

# 窗口整体布局
layout = [
    [sg.Push(),sg.Text('niconico会员视频下载窗口', font=('微软雅黑', 24)),sg.Push()],
    [program, sg.VSeperator(), introduce],
    [sg.Output(size=(80, 15), key='output')],  # 用于显示 cmd 输出内容
    [sg.Button('确认以获取验证码', font=('微软雅黑', 12,'bold')), sg.Button('开始下载', disabled=True, font=('微软雅黑', 12,'bold')), sg.Push(), sg.Button('退出窗口', font=('微软雅黑', 12,'bold'))]
]

window = sg.Window('nndownload-Windows', layout)

process = None

def display_message(message):
    """在 Output 框中显示消息"""
    window['output'].update(message + '\n', append=True)

def run_command(command):
    """运行命令并在窗口输出"""
    global process
    # 在命令中添加引号以处理路径中的空格
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

    # 读取输出并在窗口显示
    for line in iter(process.stdout.readline, ''):
        display_message(line.strip())  # 使用 display_message 显示输出

    for error_line in iter(process.stderr.readline, ''):
        display_message(f"错误: {error_line.strip()}")  # 显示错误信息

    process.wait()  # 等待进程结束

    # 根据返回码显示相应提示
    if process.returncode != 0:
        display_message('登录失败，请重新检查路径与账号密码')

def confirm(values): #取消nndownload_path
    username = values['username']
    password = values['password']

    # 更新配置
    config['username'] = username
    config['password'] = password

    # 保存配置
    save_config('config.txt', config)

    video_url = values['video_url']

    # 添加选项参数
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

    # 构建完整命令
    command = f'python -m nndownload "{video_url}" -u "{username}" -p "{password}" ' + ' '.join(options) #修改为不必再下载nndownload.py
    
    # 显示提示信息
    display_message('请到邮箱获取验证码，确认后请回到本窗口输入验证码')
    
    # 启动下载命令
    threading.Thread(target=run_command, args=(command,), daemon=True).start()

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == '退出窗口':
        break

    if event == '确认以获取验证码':
    # --- v2.0.1版本更新前置检查 ---
        video_url = values['video_url'].strip()
        username = values['username'].strip()
        password = values['password'].strip()

        if not video_url:
           sg.popup_error('请输入视频 URL')
           continue
        if not username or not password:
           sg.popup_error('请输入账号与密码')
           continue
        
        confirm(values)
        window['开始下载'].update(disabled=False) #开启按钮(防呆)

    if event == '开始下载':
        if process is None:
           sg.popup_error('请先点击「确认以获取验证码」，并到邮箱获取验证码')
           continue

        captcha = values['captcha'].strip()
        
        if not captcha:
           sg.popup_error('请先输入邮箱中的验证码')
           continue
        
        # 验证码通过 stdin 发送给命令序
        process.stdin.write(captcha + '\n')
        process.stdin.flush()
        
        window['开始下载'].update(disabled=True) #关闭按钮(防呆)

    # 处理链接点击事件
    if event == '-GITHUB-LINK-':
        webbrowser.open('https://github.com/lance1247')  # GitHub链接

    if event == '-BAHA-LINK-':
        webbrowser.open('https://home.gamer.com.tw/homeindex.php')  # 巴哈姆特链接

    if event == '-BILIBILI-LINK-':
        webbrowser.open('https://space.bilibili.com/171022667?spm_id_from=333.1007.0.0')  # Bilibili链接

window.close()
