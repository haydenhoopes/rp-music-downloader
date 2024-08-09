import subprocess


class USB:
    def __init__(self):
        pass

    def exists(self):
        return len(self.get_devices) > 0

    def get_devices(self):
        try:
            # Run the 'lsblk' command and get its output
            output = subprocess.check_output(["lsblk", "-o", "NAME,MOUNTPOINT,TRAN"]).decode()
            
            # Split the output into lines
            lines = output.strip().splitlines()
            
            # The first line is the header, skip it
            headers = lines[0].split()
            devices = []
            
            for line in lines[1:]:
                # Split each line into its columns
                columns = line.split()
                
                # Only consider devices with TRAN type 'usb'
                if len(columns) >= 3 and columns[2].lower() == 'usb':
                    device_name = columns[0]
                    mount_point = columns[1] if len(columns) > 1 else None
                    devices.append((f"/dev/{device_name}", mount_point))
            
            return devices

        except Exception as e:
            print(f"Error listing USB drives: {e}")
            return []

    def get_usb(self):
        return self.get_devices()[0]

    def mount(self):
        usb = self.get_usb()
        device = usb[0]
        mount_point = usb[1]
        
        self.eject()
        subprocess.run(["sudo", "mount", device, mount_point], check=True)

    def eject(self):
        usb = self.get_usb()
        device = usb[0]
        subprocess.run(["sudo", "umount", device], check=False)

    def validate_usb_items(self):
        pass