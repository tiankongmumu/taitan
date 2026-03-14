from playwright._impl._driver import compute_driver_executable, get_driver_env
import subprocess

def install_chromium():
    driver_executable, driver_cli = compute_driver_executable()
    env = get_driver_env()
    print("Executable:", driver_executable)
    print("CLI:", driver_cli)
    subprocess.run([driver_executable, *driver_cli, 'install', 'chromium'], env=env)
    print("Installed!")

install_chromium()
