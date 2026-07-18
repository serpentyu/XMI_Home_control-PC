import json
import os
import io
import sys
import base64
import threading
import time
from flask import Flask, render_template, request, jsonify, session

# 修复Windows终端GBK编码无法打印二维码的问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)
app.secret_key = 'mijia-smart-home-secret-key'

# 凭证缓存文件
CRED_FILE = os.path.join(os.path.dirname(__file__), 'credential.json')

# 登录状态缓存
login_state = {
    'qr_image': None,
    'status': 'idle',  # idle, waiting, success, error
    'login_data': None,
    'error': None
}


def load_credential():
    """加载本地保存的登录凭证"""
    if os.path.exists(CRED_FILE):
        try:
            with open(CRED_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_credential(data):
    """保存登录凭证到本地"""
    with open(CRED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_api():
    """获取已登录的API实例"""
    try:
        from mijiaAPI import mijiaAPI
        api = mijiaAPI()
        # 尝试获取家庭列表验证登录状态
        api.get_homes_list()
        return api
    except Exception:
        return None


# ========== 登录相关 ==========

@app.route('/api/login-status')
def login_status():
    """检查登录状态"""
    api = get_api()
    if api:
        try:
            homes = api.get_homes_list()
            return jsonify({
                'logged': True,
                'homes': homes
            })
        except Exception as e:
            return jsonify({'logged': False, 'message': str(e)})
    return jsonify({'logged': False})


@app.route('/api/logout', methods=['POST'])
def logout():
    """退出登录"""
    if os.path.exists(CRED_FILE):
        os.remove(CRED_FILE)
    return jsonify({'status': 'success'})


# ========== 设备相关 ==========

def get_device_icon(model, dev_type):
    """根据设备型号判断图标类型"""
    model_lower = str(model).lower()
    if 'light' in model_lower or 'lamp' in model_lower or dev_type == 'light':
        return 'light'
    elif 'curtain' in model_lower or dev_type == 'curtain':
        return 'curtain'
    elif 'ac' in model_lower or 'aircondition' in model_lower or dev_type == 'ac':
        return 'ac'
    elif 'sensor' in model_lower or dev_type == 'sensor':
        return 'sensor'
    elif 'plug' in model_lower or 'outlet' in model_lower or dev_type == 'plug':
        return 'plug'
    elif 'switch' in model_lower or dev_type == 'switch':
        return 'switch'
    elif 'fan' in model_lower:
        return 'fan'
    elif 'humidifier' in model_lower:
        return 'humidifier'
    elif 'purifier' in model_lower:
        return 'purifier'
    else:
        return 'device'


@app.route('/api/devices')
def get_devices():
    """获取所有设备列表，按房间分组"""
    api = get_api()
    if not api:
        return jsonify({'error': '未登录'}), 401

    try:
        homes = api.get_homes_list()
        result = []

        for home in homes:
            home_id = home.get('home_id') or home.get('id')
            home_name = home.get('name', '我的家')

            try:
                devices = api.get_devices_list(home_id)
            except Exception:
                devices = []

            # 按房间分组
            rooms = {}
            for dev in devices:
                room_name = dev.get('room_name', '未分组')
                if room_name not in rooms:
                    rooms[room_name] = []
                rooms[room_name].append({
                    'did': dev.get('did'),
                    'name': dev.get('name', dev.get('model', '未知设备')),
                    'model': dev.get('model'),
                    'type': dev.get('type', 'unknown'),
                    'online': dev.get('isOnline', dev.get('online', True)),
                    'icon': get_device_icon(dev.get('model', ''), dev.get('type', '')),
                })

            result.append({
                'home_id': home_id,
                'home_name': home_name,
                'rooms': rooms
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/device/status', methods=['POST'])
def get_device_status():
    """获取设备状态（批量读取属性）"""
    api = get_api()
    if not api:
        return jsonify({'error': '未登录'}), 401

    data = request.json
    did = data.get('did')
    props = data.get('props', [{'siid': 2, 'piid': 1}])

    try:
        params = [{'did': did, 'siid': p['siid'], 'piid': p['piid']} for p in props]
        result = api.get_devices_prop(params)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/device/control', methods=['POST'])
def control_device():
    """控制设备属性"""
    api = get_api()
    if not api:
        return jsonify({'error': '未登录'}), 401

    data = request.json
    did = data.get('did')
    siid = data.get('siid', 2)
    piid = data.get('piid', 1)
    value = data.get('value')

    try:
        result = api.set_devices_prop([{
            'did': did,
            'siid': siid,
            'piid': piid,
            'value': value
        }])
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ========== 场景相关 ==========

@app.route('/api/scenes')
def get_scenes():
    """获取场景列表"""
    api = get_api()
    if not api:
        return jsonify({'error': '未登录'}), 401

    try:
        homes = api.get_homes_list()
        all_scenes = []
        for home in homes:
            home_id = home.get('home_id') or home.get('id')
            try:
                scenes = api.get_scenes_list(home_id)
                for s in scenes:
                    s['home_id'] = home_id
                all_scenes.extend(scenes)
            except Exception:
                pass
        return jsonify(all_scenes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scene/run', methods=['POST'])
def run_scene():
    """执行场景"""
    api = get_api()
    if not api:
        return jsonify({'error': '未登录'}), 401

    data = request.json
    scene_id = data.get('scene_id')

    try:
        result = api.run_scene(scene_id)
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ========== 页面路由 ==========

@app.route('/')
def index():
    return render_template('index.html')


def start_login_thread():
    """在后台线程启动二维码登录"""
    global login_state
    login_state['status'] = 'waiting'
    login_state['qr_url'] = None
    try:
        from mijiaAPI import mijiaAPI
        import re

        # 捕获stdout以获取二维码图片URL
        class OutputCapture:
            def __init__(self):
                self.lines = []
                self.original = sys.stdout
            def write(self, text):
                self.lines.append(text)
                self.original.write(text)
            def flush(self):
                self.original.flush()

        capture = OutputCapture()
        sys.stdout = capture

        print("\n" + "=" * 60)
        print("  请使用米家APP扫描下方二维码登录")
        print("=" * 60 + "\n")

        api = mijiaAPI()
        result = api.QRlogin()

        # 恢复stdout
        sys.stdout = capture.original

        # 从输出中提取二维码图片URL
        output_text = ''.join(capture.lines)
        url_match = re.search(r'(https?://account\.xiaomi\.com/pass/qr/login\?[^\s]+)', output_text)
        if url_match:
            login_state['qr_url'] = url_match.group(1)
            print(f"二维码URL: {login_state['qr_url']}")

        login_state['status'] = 'success'
        login_state['login_data'] = result
        print("\n" + "=" * 60)
        print("  登录成功！浏览器刷新页面即可使用")
        print("=" * 60 + "\n")
    except Exception as e:
        sys.stdout = sys.__stdout__
        login_state['status'] = 'error'
        login_state['error'] = str(e)
        print(f"登录失败: {e}")


@app.route('/api/qr-start', methods=['POST'])
def qr_start():
    """开始二维码登录（在终端显示二维码）"""
    global login_state
    if login_state['status'] in ('waiting', 'success'):
        return jsonify({'status': login_state['status']})

    # 在新线程启动登录
    t = threading.Thread(target=start_login_thread, daemon=True)
    t.start()
    return jsonify({'status': 'waiting'})


@app.route('/api/qr-status')
def qr_status():
    """查询登录状态"""
    return jsonify({
        'status': login_state['status'],
        'error': login_state.get('error'),
        'qr_url': login_state.get('qr_url')
    })


if __name__ == '__main__':
    cred = load_credential()
    if not cred:
        print("=" * 60)
        print("  米家全屋智能控制中心")
        print("=" * 60)
        print("  浏览器访问: http://localhost:5678")
        print("  首次使用请在网页点击「生成二维码」按钮")
        print("  然后在本终端用米家APP扫描二维码")
        print("=" * 60 + "\n")
    else:
        print("=" * 60)
        print("  米家全屋智能控制中心 - 已登录")
        print("=" * 60)
        print("  浏览器访问: http://localhost:5678")
        print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5678, debug=False)
