import subprocess


class USB:
    def __init__(self):
        pass

    def exists(self):
        return len(self.get_usb()) > 0

    def get_usb(self):
        try:
            # Run the 'lsblk' command and get its output
            output = subprocess.check_output(["lsblk", "-o", "NAME,MOUNTPOINT,TRAN"]).decode()
            
            # Split the output into lines
            lines = output.strip().splitlines()
            
            for line in lines[1:]:
                # Split each line into its columns
                columns = line.split()
                
                # Only consider devices with TRAN type 'usb'
                if 'usb' in columns:
                    device_name = columns[0]
                    mount_point = columns[1] if len(columns) > 1 else None
                    return (f"/dev/{device_name}", mount_point)
            return []

        except Exception as e:
            print(f"Error listing USB drives: {e}")
            return []

    def mount(self):
        try:
            subprocess.run(['sudo', 'mkdir' '/mnt/usb'])
        except:
            pass

        usb = self.get_usb()
        if usb[1]:
            self.eject()

        device = usb[0]
        mount_point = '/mnt/usb'
        
        subprocess.run(["sudo", "mount", device, mount_point], check=True)

    def eject(self):
        subprocess.run(["sudo", "umount", '/mnt/usb'], check=False)

    def validate_usb_items(self):
        pass