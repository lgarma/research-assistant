"""Profiling file."""
import time

from memory_profiler import profile
from profiling.confprofiling import monitor_model, plot_monitor

from {{cookiecutter.package.lower()}}{{cookiecutter.module_name.capitalize()}}.model import Model


def profiling_{{cookiecutter.package.lower()}}{{cookiecutter.module_name.lower()}}_model(source=None):
    """Profiling for model."""
    time.sleep(1) # Do not delete
    
    Model()


if __name__ == "__main__":
    
    cpu_data, mem_data = monitor_model(target=profiling_{{cookiecutter.package.lower()}}{{cookiecutter.module_name.lower()}}_model)
    plot_monitor(cpu_data, mem_data)
    dec = profile(target=profiling_{{cookiecutter.package.lower()}}{{cookiecutter.module_name.lower()}}_model)
    dec()
