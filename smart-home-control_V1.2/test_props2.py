#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mijiaAPI import mijiaAPI

api = mijiaAPI()
homes = api.get_homes_list()
home_id = homes[0]['id']
devices = api.get_devices_list(home_id)

# 1. 测试屏幕挂灯
print("=" * 60)
print("1. 屏幕挂灯 (yeelink.light.lamp22) 属性测试")
print("=" * 60)
lamp_did = None
for d in devices:
    if 'lamp22' in d.get('model', ''):
        lamp_did = d['did']
        break

if lamp_did:
    print(f"DID: {lamp_did}")
    # 灯的标准属性 + 扩展测试
    props = []
    for siid in [2, 3, 4]:
        for piid in range(1, 8):
            props.append({'did': lamp_did, 'siid': siid, 'piid': piid})
    try:
        result = api.get_devices_prop(props)
        for i, r in enumerate(result):
            if r.get('code') == 0:
                print(f"  siid={props[i]['siid']}, piid={props[i]['piid']}: value = {r.get('value')}")
    except Exception as e:
        print(f"  错误: {e}")

# 2. 测试路由器
print("\n" + "=" * 60)
print("2. 路由器 (xiaomi.router.rc06) 属性测试")
print("=" * 60)
router_did = None
for d in devices:
    if 'router' in d.get('model', ''):
        router_did = d['did']
        break

if router_did:
    print(f"DID: {router_did}")
    props = []
    for siid in range(1, 10):
        for piid in range(1, 6):
            props.append({'did': router_did, 'siid': siid, 'piid': piid})
    try:
        result = api.get_devices_prop(props)
        for i, r in enumerate(result):
            if r.get('code') == 0:
                print(f"  siid={props[i]['siid']}, piid={props[i]['piid']}: value = {r.get('value')}")
    except Exception as e:
        print(f"  错误: {e}")

# 3. 测试温湿度传感器更多siid
print("\n" + "=" * 60)
print("3. 温湿度传感器 更多siid测试")
print("=" * 60)
sensor_did = None
for d in devices:
    if 'sensor_ht' in d.get('model', ''):
        sensor_did = d['did']
        break

if sensor_did:
    print(f"DID: {sensor_did}")
    props = []
    for siid in range(1, 8):
        for piid in range(1, 5):
            props.append({'did': sensor_did, 'siid': siid, 'piid': piid})
    try:
        result = api.get_devices_prop(props)
        for i, r in enumerate(result):
            if r.get('code') == 0:
                print(f"  siid={props[i]['siid']}, piid={props[i]['piid']}: value = {r.get('value')}")
    except Exception as e:
        print(f"  错误: {e}")

# 4. 测试音箱播放状态
print("\n" + "=" * 60)
print("4. 音箱 (oh2p) 播放状态测试")
print("=" * 60)
speaker_did = None
for d in devices:
    if 'oh2p' in d.get('model', ''):
        speaker_did = d['did']
        break

if speaker_did:
    print(f"DID: {speaker_did}")
    props = []
    for siid in range(3, 10):
        for piid in range(1, 8):
            props.append({'did': speaker_did, 'siid': siid, 'piid': piid})
    try:
        result = api.get_devices_prop(props)
        for i, r in enumerate(result):
            if r.get('code') == 0:
                print(f"  siid={props[i]['siid']}, piid={props[i]['piid']}: value = {r.get('value')}")
    except Exception as e:
        print(f"  错误: {e}")
