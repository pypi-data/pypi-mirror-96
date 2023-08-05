'''Initialises TensorFlow, monkey-patching if necessary.'''

__all__ = ['init']

def init():
    '''Initialises tensorflow, monkey-patching if necessary.'''

    import tensorflow

    if tensorflow.__version__.startswith('2.') and tensorflow.__version__ < '2.4':
        import sys
        
        # monkey-patch mobilenet_v3
        from .keras_applications import mobilenet_v3
        setattr(tensorflow.python.keras.applications, 'mobilenet_v3', mobilenet_v3)
        setattr(tensorflow.keras.applications, 'mobilenet_v3', mobilenet_v3)
        sys.modules['tensorflow.python.keras.applications.mobilenet_v3'] = mobilenet_v3
 
        import h5py as _h5
        if _h5.__version__.startswith('3.'): # hack because h5py>=3.0.0 behaves differently from h5py<3.0.0
            from .keras_engine import hdf5_format
            tensorflow.python.keras.saving.hdf5_format = hdf5_format
            tensorflow.python.keras.engine.training.hdf5_format = hdf5_format
            sys.modules['tensorflow.python.keras.saving.hdf5_format'] = hdf5_format
    
    return tensorflow

init()
