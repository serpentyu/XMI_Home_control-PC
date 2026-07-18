#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from mijiaAPI import mijiaAPI

api = mijiaAPI()
homes = api.get_homes_list()

print("家庭列表结构：")
print(json.dumps(homes, ensure_ascii=False, indent=2))
print()

if homes:
    home_id = homes[0].get('home_id') or homes[0].get('id')
    print(f"使用home_id: {home_id}")
    devices = api.get_devices_list(home_id)
    print("\n设备数量:", len(devices))
    if devices:
        print("\n第一个设备完整结构：")
        print(json.dumps(devices[0], ensure_ascii=False, indent=2))
