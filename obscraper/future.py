import time
import concurrent.futures

def map_with_delay(func, arg_dict, delay, max_workers=32, *args, **kwargs):
    """Map with a time delay between each function evaluation.
    
    If exception handling is needed, it should be performed in 
    func. 

    Args:
        func: callable. Function to be evaluated.
        arg_dict: dictionary. Dictionary whose keys identify
        each element and whose values are passed to func.
        delay: number. The time delay (in seconds) between
        function evaluations.
        max_workers: int. The maximum number of threads used
        to execute the function evaluations.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        arg_futures = {}
        for id, value in arg_dict.items():
            arg_futures[id] = executor.submit(func, value, *args, **kwargs)
            time.sleep(delay)
        result = {id: future.result() for id, future in arg_futures.items()}
    return result