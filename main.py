"""
Main Entry Point for Python Operating System with GUI
"""

from kernel import OperatingSystem
from gui import OSGUI

def main():
    """Start the operating system with GUI"""
    print("Booting Python Operating System with GUI...")
    print("Loading kernel...")
    print("Initializing components...")
    print("Starting GUI...")
    
    # Create OS kernel
    os_system = OperatingSystem()
    
    # Create and run GUI
    gui = OSGUI(os_system)
    gui.run()

if __name__ == "__main__":
    main()