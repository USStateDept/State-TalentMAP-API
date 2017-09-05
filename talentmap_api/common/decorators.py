from functools import wraps


def respect_instance_signalling():
    '''
    Decorator which checks for the value of an instance's "_disable_signals" variable,
    and if it is true, does not broadcast a signal for that instance. Decorates signal
    listeners
    '''
    def _respect_instance_signalling(signal_func):
        @wraps(signal_func)
        def _decorator(sender, instance, **kwargs):
            if hasattr(instance, '_disable_signals'):
                if instance._disable_signals:
                    return None
            return signal_func(sender, instance, **kwargs)
        return _decorator
    return _respect_instance_signalling
