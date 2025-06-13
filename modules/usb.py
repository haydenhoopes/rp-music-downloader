import subprocess
import os


class USBDevice:
    def __init__(self, path, mount_point=None):
        self.path = path
        self.mount_point = mount_point

    def __repr__(self):
        return f"<USBDevice path={self.path}, mount_point={self.mount_point}>"


class USB:
    def __init__(self, logger, mount_point_base="/mnt/usb"):
        self.logger = logger
        self.mount_point_base = mount_point_base
        self.devices = []  # List of USBDevice instances


    def scan(self):
        self.devices.clear()

        result = subprocess.run(["lsblk", "-pnlo", "NAME,MOUNTPOINT"], capture_output=True, text=True)

        for line in result.stdout.strip().splitlines():
            parts = line.strip().split(None, 1)
            if parts and parts[0].startswith("/dev/sd"):
                device_path = parts[0]
                mount_point = parts[1] if len(parts) > 1 else None
                self.devices.append(USBDevice(device_path, mount_point))

        return self.devices


    def mount(self, device):
        mount_point = f"{self.mount_point_base}_{os.path.basename(device.path)}"

        os.makedirs(mount_point, exist_ok=True)

        result = subprocess.run(["sudo", "mount", device.path, mount_point])

        if result.returncode == 0:
            device.mounted = True
            device.mount_point = mount_point
            self.logger.info(f"mounted {device.path} at {mount_point}")
        else:
            self.logger.error(f"failed to mount {device.path}")


    def mount_all(self):
        if not self.devices:
            self.scan()

        for device in self.devices:
            self.mount(device)


    def eject(self, device):
        target = device
        if target is None:
            # Pick first mounted device
            for dev in self.devices:
                if dev.mounted:
                    target = dev
                    break

        if device and device.mounted:
            result = subprocess.run(["sudo", "umount", device.mount_point])
            if result.returncode == 0:
                self.logger.info(f"Unmounted {device.path} from {device.mount_point}")
                device.mount_point = None

            else:
                self.logger.error(f"failed to unmount {device.path}")
        else:
            self.logger.warning("no mounted usb device found.")


    def eject_all(self):
        if not self.devices:
            self.scan()

        for device in self.devices:
            self.eject(device)


    def get_serial_number(self, device):
        base = os.path.basename(device.path).rstrip("0123456789")

        result = subprocess.run(
            ["udevadm", "info", "--query=all", f"/dev/{base}"],
            capture_output=True, text=True
        )

        for line in result.stdout.strip().splitlines():
            if "ID_SERIAL=" in line:
                return line.split("ID_SERIAL=")[-1]
        self.logger.warning("serial number not found.")
        return None

