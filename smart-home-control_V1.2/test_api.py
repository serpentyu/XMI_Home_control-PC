#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试mijiaAPI库是否能正常导入和使用"""

print("=" * 50)
print("测试1: 导入mijiaAPI模块")
print("=" * 50)
try:
    from mijiaAPI import mijiaAPI
    print("✅ 导入成功: from mijiaAPI import mijiaAPI")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    exit(1)

print("\n" + "=" * 50)
print("测试2: 创建mijiaAPI实例")
print("=" * 50)
try:
    api = mijiaAPI()
    print(f"✅ 创建成功: {type(api)}")
except Exception as e:
    print(f"❌ 创建失败: {e}")
    exit(1)

print("\n" + "=" * 50)
print("测试3: 检查QRlogin方法是否存在")
print("=" * 50)
if hasattr(api, 'QRlogin'):
    print("✅ QRlogin 方法存在")
else:
    print("❌ QRlogin 方法不存在")
    print(f"可用方法: {[m for m in dir(api) if not m.startswith('_')]}")

print("\n" + "=" * 50)
print("测试4: 检查其他常用方法")
print("=" * 50)
methods = ['getHomesList', 'getDevicesList', 'getDevicesProp', 'setDevicesProp', 'getSceneList', 'runScene']
for m in methods:
    if hasattr(api, m):
        print(f"  ✅ {m}")
    else:
        print(f"  ❌ {m} - 不存在")

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
