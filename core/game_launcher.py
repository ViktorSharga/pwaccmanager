"""Game launching and process management module"""

import os
import subprocess
import time
import psutil
from typing import Optional, List, Set, Tuple
from queue import Queue
from threading import Thread, Lock
import threading


class GameLauncher:
    def __init__(self, game_folder: str):
        self.game_folder = game_folder
        self.process_map = {}  # Maps login to PID
        self.launch_queue = Queue()
        self.launch_delay = 3  # Default 3 seconds between launches
        self.launch_thread = None
        self.launch_lock = Lock()
        self.stop_launcher = False
        self._start_launch_worker()
    
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
        # For single launches, use direct launch for immediate feedback
        return self._launch_account_sync(login, batch_file)
    
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
    
    def _start_launch_worker(self):
        """Start the background thread for processing launch queue"""
        if self.launch_thread is None or not self.launch_thread.is_alive():
            self.launch_thread = Thread(target=self._launch_worker, daemon=True)
            self.launch_thread.start()
    
    def _launch_worker(self):
        """Worker thread that processes the launch queue"""
        while not self.stop_launcher:
            try:
                # Wait for launch request with timeout
                launch_request = self.launch_queue.get(timeout=1)
                if launch_request is None:  # Shutdown signal
                    break
                
                login, batch_file, callback = launch_request
                
                # Perform the actual launch
                pid = self._launch_account_sync(login, batch_file)
                
                # Call the callback with the result
                if callback:
                    callback(login, pid)
                
                # Wait before next launch
                if not self.launch_queue.empty():
                    time.sleep(self.launch_delay)
                    
            except:
                # Timeout or other error, continue
                continue
    
    def _launch_account_sync(self, login: str, batch_file: str) -> Optional[int]:
        """Synchronous version of launch_account for use in worker thread"""
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
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait a bit for the game to start
            time.sleep(3)
            
            # Find new processes
            after_pids = self._get_running_processes()
            new_pids = after_pids - before_pids
            
            if new_pids:
                # Take the first new PID
                pid = next(iter(new_pids))
                with self.launch_lock:
                    self.process_map[login] = pid
                return pid
            
            return None
            
        except Exception as e:
            print(f"Error launching game: {e}")
            return None
    
    def queue_launch(self, login: str, batch_file: str, callback=None):
        """Queue an account launch request"""
        self.launch_queue.put((login, batch_file, callback))
    
    def set_launch_delay(self, delay: int):
        """Set the delay between consecutive launches"""
        self.launch_delay = max(1, min(30, delay))  # Clamp between 1-30 seconds
    
    def shutdown(self):
        """Shutdown the launch worker thread"""
        self.stop_launcher = True
        self.launch_queue.put(None)  # Signal to stop
        if self.launch_thread:
            self.launch_thread.join(timeout=5)