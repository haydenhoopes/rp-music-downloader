import subprocess, os
from wasabi import msg


class USB:
    def __init__(self, mount_point="/mnt/usb"):
        self.mount_point = mount_point
        self.device_path = None

    def exists(self):
        result = subprocess.run(["lsblk", "-o", "NAME,MOUNTPOINT"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "sd" in line and not "/boot" in line and not "/" in line:
                self.device_path = "/dev/" + line.split()[0]
                return True
        return False

    def mount(self):
        if not os.path.ismount(self.mount_point):
            if self.device_path:
                os.makedirs(self.mount_point, exist_ok=True)
                subprocess.run(["sudo", "mount", self.device_path, self.mount_point])
                print(f"Mounted {self.device_path} to {self.mount_point}")
            else:
                msg.fail("No USB device found.")
        else:
            print("USB is already mounted.")

    def eject(self):
        if os.path.ismount(self.mount_point):
            subprocess.run(["sudo", "umount", self.mount_point])
            print("Unmounted {self.device_path} from {self.mount_point}")
        else:
            msg.fail("USB is not mounted.")
        
    def get_serial_number(self):
        if self.device_path:
            # Use udevadm to get device details
            result = subprocess.run(["udevadm", "info", "--query=all", "--name=" + self.device_path], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "ID_SERIAL=" in line:
                    return line.split("=")[-1]
            msg.fail("Serial number not found.")
        else:
            print("No USB device found.")

    def get_path(self):
        if os.path.ismount(self.mount_point):
            return self.mount_point
        else:
            msg.fail("USB is not mounted.")