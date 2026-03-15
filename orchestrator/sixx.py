import runtime.state_controller as state_controller
import workers.forge as forge_worker
import workers.atlas as atlas_worker
import workers.aegis as aegis_worker
import workers.sentinel as sentinel_worker
import time

class SixxOrchestrator:
    def __init__(self):
        self.state_ctrl = state_controller.StateController()
        self.worker_modules = {
            'owner:backend': forge_worker,
            'owner:mobile': atlas_worker,
            'owner:architecture': aegis_worker,
            'owner:qa': sentinel_worker
        }

    def plan(self):
        for task_id, task_info in self.state_ctrl.tasks.items():
            if task_info['state'] == 'backlog':
                print(f"Activating task: {task_id}")
                self.state_ctrl.activate_task(task_id)
                return task_id
        return None

    def dispatch(self, task_id):
        task_info = self.state_ctrl.tasks[task_id]
        owner_label = task_info['details'].get('owner_label')
        worker_module = self.worker_modules.get(owner_label)
        if not worker_module:
            raise ValueError(f"No worker module for task with owner {owner_label}")
        worker_id = f"{owner_label}-worker-{task_id}"
        self.state_ctrl.link_worker(task_id, worker_id)
        self.state_ctrl.start_worker_execution(worker_id)
        print(f"Dispatched worker {worker_id} for task {task_id}")
        return worker_id, worker_module

    def resolve(self, worker_id, worker_module):
        task_id = self.state_ctrl.workers[worker_id]['task_id']
        time.sleep(1)  # Simulate waiting
        result = worker_module.execute(task_id)
        if result == 'success':
            self.state_ctrl.record_worker_done(worker_id)
            self.state_ctrl.record_task_delivered(task_id)
            self.state_ctrl.verify_task(task_id)
            if self.state_ctrl.tasks[task_id]['state'] == 'delivered':
                self.state_ctrl.accept_task(task_id)
        elif result == 'failure':
            self.state_ctrl.record_worker_failure(worker_id)
            self.state_ctrl.block_task(task_id)
        elif result == 'blocked':
            self.state_ctrl.record_worker_blocked(worker_id, 'blocked by worker')
        else:
            raise ValueError(f"Unexpected worker result: {result}")
        self.state_ctrl.terminate_worker(worker_id)
        print(f"Resolved task {task_id} and terminated worker {worker_id} with result {result}")

    def run(self):
        while True:
            task_id = self.plan()
            if not task_id:
                print("No backlog tasks to activate. Orchestration loop sleeping.")
                time.sleep(5)
                continue
            worker_id, worker_module = self.dispatch(task_id)
            self.resolve(worker_id, worker_module)

if __name__ == '__main__':
    sixx = SixxOrchestrator()
    sixx.run()
