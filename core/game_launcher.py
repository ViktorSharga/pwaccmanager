"""Game launching and process management module"""

import os
import subprocess
import time
import psutil
from typing import Optional, List, Set


class GameLauncher:
    def __init__(self, game_folder: str):
        self.game_folder = game_folder
        self.process_map = {}  # Maps login to PID
    
    def _get_running_processes(self) -> Set[int]:
        """Get all running Perfect World processes"""
        pids = set()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Look for processes with "Asgrad pw" in name or elementclient.exe
                name = proc.info['name'].lower()
                if 'elementclient' in name or 'asgrad' in name:
                    pids.add(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return pids
    
    def launch_account(self, login: str, batch_file: str) -> Optional[int]:
        """Launch game client for an account"""
        if not os.path.exists(batch_file):
            return None
        
        # Get current running processes
        before_pids = self._get_running_processes()
        
        try:
            # Launch the batch file
            process = subprocess.Popen(
                batch_file,
                cwd=self.game_folder,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            # Wait a bit for the game to start
            time.sleep(3)
            
            # Find new processes
            after_pids = self._get_running_processes()
            new_pids = after_pids - before_pids
            
            if new_pids:
                # Take the first new PID
                pid = next(iter(new_pids))
                self.process_map[login] = pid
                return pid
            
            return None
            
        except Exception as e:
            print(f"Error launching game: {e}")
            return None
    
    def terminate_account(self, login: str) -> bool:
        """Terminate game client for an account"""
        pid = self.process_map.get(login)
        if not pid:
            return False
        
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for process to terminate
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                process.kill()
            
            # Remove from map
            del self.process_map[login]
            return True
            
        except psutil.NoSuchProcess:
            # Process already terminated
            if login in self.process_map:
                del self.process_map[login]
            return True
        except Exception as e:
            print(f"Error terminating process: {e}")
            return False
    
    def is_account_running(self, login: str) -> bool:
        """Check if account is currently running"""
        pid = self.process_map.get(login)
        if not pid:
            return False
        
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            # Clean up the map
            del self.process_map[login]
            return False
    
    def terminate_all(self) -> int:
        """Terminate all tracked processes"""
        count = 0
        logins = list(self.process_map.keys())
        
        for login in logins:
            if self.terminate_account(login):
                count += 1
        
        return count
    
    def cleanup_dead_processes(self):
        """Remove dead processes from tracking"""
        dead_logins = []
        
        for login, pid in self.process_map.items():
            try:
                process = psutil.Process(pid)
                if not process.is_running():
                    dead_logins.append(login)
            except psutil.NoSuchProcess:
                dead_logins.append(login)
        
        for login in dead_logins:
            del self.process_map[login]