#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mijiaAPI import mijiaAPI

api = mijiaAPI()
homes = api.get_homes_list()
home_id = homes[0]['home_id']
devices = api.get_devices_list(home_id)

print("=" * 80)
print("设备列表：")
print("=" * 80)
for d in devices:
    name = d.get('name', '未知')
    model = d.get('model', '')
    did = d.get('did', '')
    dtype = d.get('type', '')
    print(f"名称: {name}")
    print(f"  型号: {model}")
    print(f"  DID: {did}")
    print(f"  类型: {dtype}")
    print()
