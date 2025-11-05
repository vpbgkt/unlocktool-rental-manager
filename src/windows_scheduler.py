"""
Windows Task Scheduler Integration Helper

This module helps create and manage Windows Task Scheduler tasks for automated password resets.
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime


class TaskSchedulerManager:
    """Manage Windows Task Scheduler tasks."""

    TASK_NAME = "UnlockToolPasswordReset"
    
    @staticmethod
    def create_task(script_path: str = None, schedule: str = "02:00", 
                   daily: bool = True) -> tuple[bool, str]:
        """
        Create a Windows Task Scheduler task.
        
        Args:
            script_path: Path to main.py (auto-detected if None)
            schedule: Time in HH:MM format
            daily: Run daily if True, weekly if False
            
        Returns:
            (success, message)
        """
        try:
            if script_path is None:
                script_path = os.path.join(os.getcwd(), "main.py")
            
            if not os.path.exists(script_path):
                return False, f"Script not found: {script_path}"
            
            # PowerShell script to create task
            ps_script = f'''
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument '"{script_path}" --mode daemon' -WorkingDirectory "{os.path.dirname(script_path)}"
$trigger = New-ScheduledTaskTrigger -Daily -At "{schedule}"
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -TaskName "{TaskSchedulerManager.TASK_NAME}" -Description "Automated password reset for unlocktool.net" -Force
'''
            
            # Run PowerShell script
            result = subprocess.run(
                ["powershell.exe", "-Command", ps_script],
                capture_output=True,
                text=True,
                shell=False
            )
            
            if result.returncode == 0:
                return True, f"Task '{TaskSchedulerManager.TASK_NAME}' created successfully"
            else:
                return False, f"Failed to create task: {result.stderr}"
        
        except Exception as e:
            return False, f"Error creating task: {str(e)}"

    @staticmethod
    def delete_task() -> tuple[bool, str]:
        """Delete the scheduled task."""
        try:
            ps_script = f'Unregister-ScheduledTask -TaskName "{TaskSchedulerManager.TASK_NAME}" -Confirm:$false'
            
            result = subprocess.run(
                ["powershell.exe", "-Command", ps_script],
                capture_output=True,
                text=True,
                shell=False
            )
            
            if result.returncode == 0:
                return True, f"Task '{TaskSchedulerManager.TASK_NAME}' deleted"
            else:
                return False, f"Failed to delete task: {result.stderr}"
        
        except Exception as e:
            return False, f"Error deleting task: {str(e)}"

    @staticmethod
    def get_task_info() -> dict:
        """Get information about the scheduled task."""
        try:
            ps_script = f'Get-ScheduledTask -TaskName "{TaskSchedulerManager.TASK_NAME}" | ConvertTo-Json'
            
            result = subprocess.run(
                ["powershell.exe", "-Command", ps_script],
                capture_output=True,
                text=True,
                shell=False
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return None
        
        except Exception as e:
            return None

    @staticmethod
    def run_task_now() -> tuple[bool, str]:
        """Run the task immediately."""
        try:
            ps_script = f'Start-ScheduledTask -TaskName "{TaskSchedulerManager.TASK_NAME}"'
            
            result = subprocess.run(
                ["powershell.exe", "-Command", ps_script],
                capture_output=True,
                text=True,
                shell=False
            )
            
            if result.returncode == 0:
                return True, f"Task '{TaskSchedulerManager.TASK_NAME}' started"
            else:
                return False, f"Failed to start task: {result.stderr}"
        
        except Exception as e:
            return False, f"Error starting task: {str(e)}"


def create_batch_scheduler(script_dir: str = None):
    """
    Create a batch file for scheduling (alternative to PowerShell).
    
    Args:
        script_dir: Directory containing main.py
    """
    if script_dir is None:
        script_dir = os.getcwd()
    
    batch_content = f'''@echo off
REM Unlock Tool Password Reset Scheduler
REM This batch file is called by Windows Task Scheduler

cd /d "{script_dir}"
python main.py --mode daemon
pause
'''
    
    batch_path = os.path.join(script_dir, "scheduler.bat")
    
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    return batch_path


if __name__ == '__main__':
    # Example usage
    success, message = TaskSchedulerManager.create_task()
    print(message)
