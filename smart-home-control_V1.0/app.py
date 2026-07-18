import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = 'mijia-smart-home-secret-key'

# 凭证缓存文件
CRED_FILE = os.path.join(os.path.dirname(__file__), 'credential.json')


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
    cred = load_credential()
    if not cred:
        return None
    try:
        from mijiaAPI import mijiaAPI
        return mijiaAPI(cred)
    except Exception:
        return None


# ========== 登录相关 ==========

@app.route('/api/login-status')
def login_status():
    """检查登录状态"""
    api = get_api()
    if api:
        try:
            homes = api.getHomesList()
            return jsonify({
                'logged': True,
                'homes': homes
            })
        except Exception as e:
            return jsonify({'logged': False, 'message': str(e)})
    return jsonify({'logged': False})


@app.route('/api/do-login', methods=['POST'])
def do_login():
    """执行扫码登录（会在终端显示二维码）"""
    try:
        from mijiaAPI import mijiaLogin
        print('\n' + '=' * 50)
        print('请使用米家APP扫描下方二维码登录')
        print('=' * 50 + '\n')
        login_data = mijiaLogin.QRlogin()
        save_credential(login_data)
        print('\n登录成功！\n')
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


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
        homes = api.getHomesList()
        result = []

        for home in homes:
            home_id = home.get('home_id') or home.get('id')
            home_name = home.get('name', '我的家')

            try:
                devices = api.getDevicesList(home_id)
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
        result = api.getDevicesProp(params)
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
        result = api.setDevicesProp([{
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
        homes = api.getHomesList()
        all_scenes = []
        for home in homes:
            home_id = home.get('home_id') or home.get('id')
            try:
                scenes = api.getSceneList(home_id)
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
        result = api.runScene(scene_id)
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ========== 页面路由 ==========

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    cred = load_credential()
    if not cred:
        print("=" * 60)
        print("  米家全屋智能控制中心")
        print("=" * 60)
        print("  启动后请在浏览器打开: http://localhost:5678")
        print("  首次使用请在页面点击登录，然后扫描终端二维码")
        print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5678, debug=False)
