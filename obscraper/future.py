"""Multithreading implementation for sending requests."""
import time
import concurrent.futures


def map_with_delay(func, arg_dict, delay, max_workers=32, **kwargs):
    """Map with a time delay between each function evaluation.

    Parameters
    ----------
    func : callable
        Function to be evaluated.
    arg_dict : Dict[str, object]
        Dictionary whose keys label each element and whose values are
        passed to func.
    delay : float
        The time delay (in seconds) between function evaluations.
    max_workers : int
        The maximum number of threads used to execute the function
        evaluations.
    **kwargs : dict, optional
        Extra arguments to be passed to `func`.

    Returns
    -------
    result : Dict[str, object]
        Dictionary whose keys are the inputted labels and whose values
        are the outputs of `func`, evaluated at each argument value.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)\
            as executor:
        arg_futures = {}
        for label, value in arg_dict.items():
            arg_futures[label] = executor.submit(func, value, **kwargs)
            time.sleep(delay)
        result = {label: future.result()
                  for label, future in arg_futures.items()}
    return result