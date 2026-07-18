from mijiaAPI import mijiaLogin
import inspect

# 查看mijiaLogin类的所有方法
print("=== mijiaLogin 方法 ===")
for name, method in inspect.getmembers(mijiaLogin, predicate=inspect.isfunction):
    if not name.startswith('_'):
        print(f"  - {name}")

# 查看QRlogin的源码
print("\n=== QRlogin 源码 ===")
try:
    print(inspect.getsource(mijiaLogin.QRlogin))
except Exception as e:
    print(f"无法获取源码: {e}")
