import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11_Adapter
from nonebot.adapters.onebot.v12 import Adapter as ONEBOT_V12_Adapter


def run_bot():
    nonebot.init(_env_file=".env.prod")

    driver = nonebot.get_driver()

    driver.register_adapter(ONEBOT_V11_Adapter)
    driver.register_adapter(ONEBOT_V12_Adapter)
    try:
        print("正在加载基础插件...")
        nonebot.load_plugin("nonebot_plugin_localstore")
        nonebot.load_plugin("nonebot_plugin_orm")
        nonebot.load_plugin("nonebot_plugin_apscheduler")
        print("基础插件加载成功")
    except Exception:
        import traceback
        traceback.print_exc()

    nonebot.load_builtin_plugin("echo")

    try:
        print("正在加载业务插件 news...")
        nonebot.load_plugins("plugins")
        print("业务插件加载成功")
    except Exception:
        import traceback
        print("!!! 业务插件加载崩溃，详细错误如下: !!!")
        traceback.print_exc()
    nonebot.run()

if __name__ == "__main__":
    run_bot()