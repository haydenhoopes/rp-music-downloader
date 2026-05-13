import subprocess
import json
import os


class USBDevice:
    def __init__(self, drive_letter, volume_name=None, size=None):
        self.drive_letter = drive_letter  # e.g., "E:"
        self.volume_name = volume_name
        self.size = size  # in bytes
        self.mounted = True  # On Windows, if the drive exists, it's mounted

    def __repr__(self):
        return (
            f"<USBDevice drive_letter={self.drive_letter}, volume_name={self.volume_name}, "
            f"size={self.size}>"
        )


class USB:
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db
        self.devices = []  # List of USBDevice instances

    def scan(self):
        """Scan for removable drives and populate USBDevice info"""
        self.devices.clear()

        # PowerShell: get removable volumes with drive letter, label, size
        ps_cmd = [
            "powershell",
            "-Command",
            (
                "Get-Volume | Where-Object {$_.DriveType -eq 'Removable'} | "
                "Select-Object DriveLetter, FileSystemLabel, Size | ConvertTo-Json"
            )
        ]

        result = subprocess.run(ps_cmd, capture_output=True, text=True)
        try:
            volumes = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse volumes: {result.stdout}")
            self.logger.info("are you sure a usb device is plugged in?")
            volumes = []

        # Normalize single volume into a list
        if isinstance(volumes, dict):
            volumes = [volumes]

        for vol in volumes:
            drive_letter = vol.get("DriveLetter")
            if drive_letter:
                drive_letter = drive_letter + ":"
            volume_name = vol.get("FileSystemLabel")
            size = int(vol.get("Size", 0)) if vol.get("Size") else None

            device = USBDevice(
                drive_letter=drive_letter,
                volume_name=volume_name,
                size=size
            )
            self.devices.append(device)

        self.__insert_usb_table(self.devices)

        return self.devices


    def __insert_usb_table(self, devices):
        for device in devices:
            sql = f"""
                INSERT OR IGNORE INTO USB (
                    volume_name, size
                ) VALUES (?, ?);
            """
            self.db.execute(sql, [device.volume_name, device.size])
        self.logger.info('added usb devices to `USB` table')


    def mount(self, device):
        """Windows automatically mounts removable drives"""
        if os.path.exists(device.drive_letter + "\\"):
            self.logger.info(f"{device.drive_letter} is already mounted.")
            device.mounted = True
        else:
            self.logger.warning(f"{device.drive_letter} is not accessible.")


    def eject(self, device):
        """Eject a USB drive using PowerShell"""
        if device and device.mounted:
            ps_cmd = [
                "powershell",
                "-Command",
                f"(New-Object -ComObject Shell.Application).Namespace(17)"
                f".ParseName('{device.drive_letter}').InvokeVerb('Eject')"
            ]
            result = subprocess.run(ps_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"Ejected {device.drive_letter}")
                device.mounted = False
            else:
                self.logger.error(f"Failed to eject {device.drive_letter}: {result.stderr}")


    def eject_all(self):
        for device in self.devices:
            self.eject(device)
