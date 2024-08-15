import subprocess, os


class USB:
    def __init__(self, mount_point="/mnt/usb"):
        self.mount_point = mount_point
        self.device_path = None

    def exists(self):
        """Check if a USB device is plugged in."""
        result = subprocess.run(["lsblk", "-o", "NAME,MOUNTPOINT"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "sd" in line and not "/boot" in line and not "/" in line:
                self.device_path = "/dev/" + line.split()[0]
                return True
        return False

    def mount(self):
        """Mount the USB device."""
        if not os.path.ismount(self.mount_point):
            if self.device_path:
                os.makedirs(self.mount_point, exist_ok=True)
                subprocess.run(["sudo", "mount", self.device_path, self.mount_point])
                return f"Mounted {self.device_path} to {self.mount_point}"
            else:
                return "No USB device found."
        else:
            return "USB is already mounted."

    def eject(self):
        """Unmount the USB device."""
        if os.path.ismount(self.mount_point):
            subprocess.run(["sudo", "umount", self.mount_point])
            return f"Unmounted {self.device_path} from {self.mount_point}"
        else:
            return "USB is not mounted."

    def get_path(self):
        """Get the path where the USB is mounted."""
        if os.path.ismount(self.mount_point):
            return self.mount_point
        else:
            return "USB is not mounted."