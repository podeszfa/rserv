def rhome_registry():
    import winreg

    aKey = r"SOFTWARE\\R-core"
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    def find_key(key):
        val = ''
        for i in range(1024):
            try:
                subkeyname = winreg.EnumKey(key, i)
                # print(subkeyname)
                subkey = winreg.OpenKey(key, subkeyname)
                val, _ = winreg.QueryValueEx(subkey, "InstallPath")
                # print('val: ' + val)
                if not val:
                    return find_key(subkey)
            except EnvironmentError:
                break
        return val
    try:
        aKey = winreg.OpenKey(aReg, aKey)
    except:
        return

    return find_key(aKey)

def rhome():
    import rpy2.situation
    return rpy2.situation.get_r_home() or rhome_registry() or ""
