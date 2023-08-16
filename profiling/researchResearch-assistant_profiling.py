"""Profiling file."""
import time

from memory_profiler import profile
from profiling.confprofiling import monitor_model, plot_monitor

from researchResearch-assistant.model import Model


def profiling_researchresearch-assistant_model(source=None):
    """Profiling for model."""
    time.sleep(1) # Do not delete
    
    Model()


if __name__ == "__main__":
    
    cpu_data, mem_data = monitor_model(target=profiling_researchresearch-assistant_model)
    plot_monitor(cpu_data, mem_data)
    dec = profile(target=profiling_researchresearch-assistant_model)
    dec()
