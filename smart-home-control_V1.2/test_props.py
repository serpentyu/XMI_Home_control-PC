#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from mijiaAPI import mijiaAPI

api = mijiaAPI()
homes = api.get_homes_list()
home_id = homes[0]['id']
devices = api.get_devices_list(home_id)

print("=" * 80)
print("所有设备型号列表：")
print("=" * 80)
for d in devices:
    print(f"DID: {d['did']}")
    print(f"  Model: {d.get('model', 'N/A')}")
    print(f"  Online: {d.get('isOnline', False)}")
    print(f"  Spec: {d.get('spec_type', 'N/A')}")
    print()

# 针对几个关键设备测试属性读取
print("\n" + "=" * 80)
print("测试设备属性读取：")
print("=" * 80)

test_props = [
    # 通用开关
    {'siid': 2, 'piid': 1, 'name': '开关'},
    # 灯 - 亮度
    {'siid': 2, 'piid': 2, 'name': '亮度'},
    # 灯 - 色温
    {'siid': 2, 'piid': 3, 'name': '色温'},
    # 空调 - 温度
    {'siid': 2, 'piid': 2, 'name': '温度'},
    # 空调 - 模式
    {'siid': 2, 'piid': 3, 'name': '模式'},
    # 传感器 - 温度
    {'siid': 3, 'piid': 1, 'name': '传感器温度'},
    # 传感器 - 湿度
    {'siid': 3, 'piid': 2, 'name': '传感器湿度'},
    # 传感器 - 温度 (siid=2)
    {'siid': 2, 'piid': 1, 'name': 'siid2温度'},
]

# 找几个典型设备测试
target_keywords = ['monitorlight', 'sensor_ht', 'speaker', 'airc', 'miwifi']

for d in devices:
    model = d.get('model', '').lower()
    did = d['did']
    is_target = any(k in model for k in target_keywords)
    
    if is_target:
        print(f"\n--- {d.get('model', '未知')} (did: {did}) ---")
        params = [{'did': did, 'siid': p['siid'], 'piid': p['piid']} for p in test_props]
        try:
            result = api.get_devices_prop(params)
            for i, r in enumerate(result):
                prop_name = test_props[i]['name']
                code = r.get('code', '?')
                value = r.get('value', 'N/A')
                status = "OK" if code == 0 else f"ERR({code})"
                print(f"  {prop_name:12s}: {status:10s} = {value}")
        except Exception as e:
            print(f"  读取失败: {e}")
